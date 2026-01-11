"""
ModelScope Provider - Alibaba's model hub

ModelScope is popular in China and hosts many Chinese language models
and multimodal models. Similar API to HuggingFace.
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
    QuantizationType,
    registry,
)


class ModelScopeProvider(ModelProvider):
    """Provider for ModelScope (Alibaba)."""

    name = "modelscope"
    display_name = "ModelScope"
    base_url = "https://modelscope.cn"
    api_url = "https://modelscope.cn/api/v1"
    supports_pull = True
    supports_search = True

    # Task to capability mapping
    TASK_MAP = {
        "text-generation": ModelCapability.TEXT_GENERATION,
        "chat": ModelCapability.CHAT,
        "text-classification": ModelCapability.TEXT_GENERATION,
        "sentence-embedding": ModelCapability.EMBEDDING,
        "text-to-image": ModelCapability.IMAGE_GENERATION,
        "image-to-image": ModelCapability.IMAGE_TO_IMAGE,
        "visual-question-answering": ModelCapability.VISION_LANGUAGE,
        "automatic-speech-recognition": ModelCapability.SPEECH_TO_TEXT,
        "text-to-speech": ModelCapability.TEXT_TO_SPEECH,
        "video-generation": ModelCapability.VIDEO_GENERATION,
    }

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.api_key = api_key or os.getenv("MODELSCOPE_TOKEN")

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """Search ModelScope models."""
        params = {
            "Query": query,
            "PageSize": min(limit, 50),
            "PageNumber": (offset // limit) + 1,
            "SortBy": "downloads",
        }

        if filters:
            if "task" in filters:
                params["Tasks"] = filters["task"]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models",
                    params=params,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = data.get("Data", {}).get("Models", [])
                        return [self._normalize_model(m) for m in models]
        except Exception as e:
            print(f"[ModelScope] Search error: {e}")

        return []

    async def get_model(self, model_id: str) -> Optional[UnifiedModel]:
        """Get details for a specific model."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models/{model_id}",
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._normalize_model(data.get("Data", {}))
        except Exception as e:
            print(f"[ModelScope] Get model error: {e}")

        return None

    async def list_models(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """List ModelScope models by category."""
        params = {
            "PageSize": min(limit, 50),
            "PageNumber": (offset // limit) + 1,
            "SortBy": "downloads",
        }

        if category:
            params["Tasks"] = category

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models",
                    params=params,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = data.get("Data", {}).get("Models", [])
                        return [self._normalize_model(m) for m in models]
        except Exception as e:
            print(f"[ModelScope] List error: {e}")

        return []

    async def pull(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """Generate pull instructions for ModelScope model."""
        return {
            "success": True,
            "provider": self.name,
            "model_id": model_id,
            "pull_command": f"modelscope download --model {model_id}",
            "python_code": f'from modelscope import snapshot_download\nmodel_dir = snapshot_download("{model_id}")',
            "message": f"Use modelscope CLI or Python SDK to download {model_id}",
        }

    async def health_check(self) -> bool:
        """Check if ModelScope API is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models?PageSize=1",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False

    def _normalize_model(self, data: Dict[str, Any]) -> UnifiedModel:
        """Convert ModelScope API response to UnifiedModel."""
        model_id = data.get("Name", data.get("Id", ""))

        # Extract tasks
        tasks = data.get("Tasks", [])
        capabilities = []
        for task in tasks:
            if task in self.TASK_MAP:
                capabilities.append(self.TASK_MAP[task])

        if not capabilities:
            capabilities.append(ModelCapability.TEXT_GENERATION)

        # Metrics
        downloads = data.get("Downloads", 0)

        return UnifiedModel(
            id=model_id,
            name=model_id.split("/")[-1] if "/" in model_id else model_id,
            provider=self.name,
            provider_url=f"{self.base_url}/models/{model_id}",
            capabilities=capabilities,
            architecture="transformer",
            parameter_count=self._parse_parameter_count(model_id),
            license=self._infer_license(data.get("License", "")),
            commercial_use=False,  # Conservative default
            description=data.get("Description", "")[:500] if data.get("Description") else None,
            tags=data.get("Tags", [])[:20],
            languages=data.get("Languages", ["zh", "en"]),
            metrics=ModelMetrics(downloads=downloads),
            pull_command=f"modelscope download --model {model_id}",
            pull_runtime="modelscope",
            raw_data=data,
        )


# Register provider
registry.register(ModelScopeProvider())
