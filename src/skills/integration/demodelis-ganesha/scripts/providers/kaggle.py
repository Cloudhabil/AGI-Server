"""
Kaggle Models Provider - Competition and research models

Kaggle hosts models from competitions and research, with a focus on
practical ML applications and benchmarks.
"""

import os
import asyncio
import aiohttp
from typing import Any, Dict, List, Optional

from .base import (
    ModelProvider,
    UnifiedModel,
    ModelCapability,
    ModelMetrics,
    ModelLicense,
    registry,
)


class KaggleProvider(ModelProvider):
    """Provider for Kaggle Models."""

    name = "kaggle"
    display_name = "Kaggle"
    base_url = "https://www.kaggle.com"
    api_url = "https://www.kaggle.com/api/v1"
    supports_pull = True
    supports_search = True

    def __init__(self, api_key: str = None, username: str = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.api_key = api_key or os.getenv("KAGGLE_KEY")
        self.username = username or os.getenv("KAGGLE_USERNAME")

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key and self.username:
            import base64
            creds = base64.b64encode(f"{self.username}:{self.api_key}".encode()).decode()
            headers["Authorization"] = f"Basic {creds}"
        return headers

    async def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """Search Kaggle models."""
        params = {
            "search": query,
            "pageSize": min(limit, 50),
            "page": (offset // limit) + 1,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models/list",
                    params=params,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [self._normalize_model(m) for m in data]
        except Exception as e:
            print(f"[Kaggle] Search error: {e}")

        return []

    async def get_model(self, model_id: str) -> Optional[UnifiedModel]:
        """Get details for a specific Kaggle model."""
        # model_id format: owner/model-name
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models/{model_id}",
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._normalize_model(data)
        except Exception as e:
            print(f"[Kaggle] Get model error: {e}")

        return None

    async def list_models(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """List Kaggle models."""
        params = {
            "pageSize": min(limit, 50),
            "page": (offset // limit) + 1,
            "sortBy": "downloadCount",
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models/list",
                    params=params,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [self._normalize_model(m) for m in data]
        except Exception as e:
            print(f"[Kaggle] List error: {e}")

        return []

    async def pull(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """Generate pull instructions for Kaggle model."""
        return {
            "success": True,
            "provider": self.name,
            "model_id": model_id,
            "pull_command": f"kaggle models instances versions download {model_id}",
            "python_code": f'import kagglehub\nmodel = kagglehub.model_download("{model_id}")',
            "message": f"Use kaggle CLI or kagglehub to download {model_id}",
        }

    async def health_check(self) -> bool:
        """Check if Kaggle API is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models/list?pageSize=1",
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return resp.status in [200, 401]  # 401 means API is up but needs auth
        except Exception:
            return False

    def _normalize_model(self, data: Dict[str, Any]) -> UnifiedModel:
        """Convert Kaggle API response to UnifiedModel."""
        model_id = f"{data.get('ownerSlug', '')}/{data.get('slug', '')}"
        name = data.get("title", data.get("slug", ""))

        # Infer capabilities
        subtitle = data.get("subtitle", "")
        tags = data.get("tags", [])
        capabilities = self._infer_capabilities(name, tags, subtitle)

        # Framework info
        framework = data.get("framework", "")

        return UnifiedModel(
            id=model_id,
            name=name,
            provider=self.name,
            provider_url=f"{self.base_url}/models/{model_id}",
            capabilities=capabilities,
            architecture=framework.lower() if framework else "pytorch",
            description=subtitle[:500] if subtitle else None,
            tags=["kaggle"] + tags[:15],
            license=self._infer_license(data.get("licenseName", "")),
            commercial_use=True,  # Most Kaggle models are Apache/MIT
            metrics=ModelMetrics(
                downloads=data.get("downloadCount", 0),
                likes=data.get("voteCount", 0),
            ),
            pull_command=f"kaggle models instances versions download {model_id}",
            pull_runtime="kaggle",
            raw_data=data,
        )


# Register provider
registry.register(KaggleProvider())
