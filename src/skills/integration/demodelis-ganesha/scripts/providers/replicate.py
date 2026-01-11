"""
Replicate Provider - Cloud model inference platform

Replicate hosts models as API endpoints. While primarily for inference,
it's useful for model discovery and comparison.
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
    registry,
)


class ReplicateProvider(ModelProvider):
    """Provider for Replicate models."""

    name = "replicate"
    display_name = "Replicate"
    base_url = "https://replicate.com"
    api_url = "https://api.replicate.com/v1"
    supports_pull = False  # Replicate is inference-only
    supports_search = True

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.api_key = api_key or os.getenv("REPLICATE_API_TOKEN")

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Token {self.api_key}"
        return headers

    async def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """Search Replicate models."""
        # Replicate doesn't have a search API, so we fetch collections and filter
        try:
            async with aiohttp.ClientSession() as session:
                # Get featured/popular models
                async with session.get(
                    f"{self.api_url}/collections/featured-image-generation-models/models",
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = data.get("results", [])

                        # Filter by query
                        query_lower = query.lower()
                        filtered = [
                            m for m in models
                            if query_lower in m.get("name", "").lower()
                            or query_lower in m.get("description", "").lower()
                        ]

                        return [self._normalize_model(m) for m in filtered[:limit]]
        except Exception as e:
            print(f"[Replicate] Search error: {e}")

        return []

    async def get_model(self, model_id: str) -> Optional[UnifiedModel]:
        """Get details for a specific Replicate model."""
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
            print(f"[Replicate] Get model error: {e}")

        return None

    async def list_models(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """List Replicate models."""
        collections = [
            "featured-image-generation-models",
            "language-models",
            "audio-models",
            "video-models",
        ]

        if category:
            # Map category to collection
            category_map = {
                "image": "featured-image-generation-models",
                "text": "language-models",
                "audio": "audio-models",
                "video": "video-models",
            }
            collections = [category_map.get(category, collections[0])]

        all_models = []
        try:
            async with aiohttp.ClientSession() as session:
                for collection in collections:
                    async with session.get(
                        f"{self.api_url}/collections/{collection}/models",
                        headers=self._get_headers(),
                        timeout=aiohttp.ClientTimeout(total=30),
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            models = data.get("results", [])
                            all_models.extend([self._normalize_model(m) for m in models])

                    if len(all_models) >= limit:
                        break

        except Exception as e:
            print(f"[Replicate] List error: {e}")

        return all_models[:limit]

    async def health_check(self) -> bool:
        """Check if Replicate API is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models",
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return resp.status in [200, 401]
        except Exception:
            return False

    def _normalize_model(self, data: Dict[str, Any]) -> UnifiedModel:
        """Convert Replicate API response to UnifiedModel."""
        owner = data.get("owner", "")
        name = data.get("name", "")
        model_id = f"{owner}/{name}"

        description = data.get("description", "")

        # Infer capabilities from description
        capabilities = self._infer_capabilities(name, [], description)

        # Run count as popularity metric
        run_count = data.get("run_count", 0)

        return UnifiedModel(
            id=model_id,
            name=name,
            provider=self.name,
            provider_url=f"{self.base_url}/{model_id}",
            capabilities=capabilities,
            description=description[:500] if description else None,
            tags=["replicate", "api", "inference"],
            license=self._infer_license(data.get("license_url", "")),
            commercial_use=True,  # Replicate models are generally available via API
            metrics=ModelMetrics(
                downloads=run_count,  # Use run_count as proxy
            ),
            pull_command=f"replicate run {model_id}",
            pull_runtime="replicate",
            raw_data=data,
        )


# Register provider
registry.register(ReplicateProvider())
