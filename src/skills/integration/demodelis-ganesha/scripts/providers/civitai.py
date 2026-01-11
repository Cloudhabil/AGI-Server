"""
Civitai Provider - AI art model community

Civitai specializes in image generation models: Stable Diffusion checkpoints,
LoRAs, embeddings, and other diffusion model components.
"""

import os
import asyncio
import aiohttp
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import (
    ModelProvider,
    UnifiedModel,
    ModelCapability,
    ModelMetrics,
    ModelLicense,
    QuantizationType,
    registry,
)


class CivitaiProvider(ModelProvider):
    """Provider for Civitai image generation models."""

    name = "civitai"
    display_name = "Civitai"
    base_url = "https://civitai.com"
    api_url = "https://civitai.com/api/v1"
    supports_pull = True
    supports_search = True

    # Model type to capability mapping
    TYPE_MAP = {
        "Checkpoint": ModelCapability.IMAGE_GENERATION,
        "LORA": ModelCapability.IMAGE_GENERATION,
        "LoCon": ModelCapability.IMAGE_GENERATION,
        "TextualInversion": ModelCapability.IMAGE_GENERATION,
        "Hypernetwork": ModelCapability.IMAGE_GENERATION,
        "AestheticGradient": ModelCapability.IMAGE_GENERATION,
        "Controlnet": ModelCapability.IMAGE_GENERATION,
        "Poses": ModelCapability.IMAGE_GENERATION,
        "Wildcards": ModelCapability.IMAGE_GENERATION,
        "VAE": ModelCapability.IMAGE_GENERATION,
        "Upscaler": ModelCapability.IMAGE_TO_IMAGE,
    }

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.api_key = api_key or os.getenv("CIVITAI_API_KEY")

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
        """Search Civitai models."""
        params = {
            "query": query,
            "limit": min(limit, 100),
            "page": (offset // limit) + 1,
            "sort": "Highest Rated",
        }

        if filters:
            if "type" in filters:
                params["types"] = filters["type"]
            if "nsfw" in filters:
                params["nsfw"] = str(filters["nsfw"]).lower()

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
                        items = data.get("items", [])
                        return [self._normalize_model(m) for m in items]
        except Exception as e:
            print(f"[Civitai] Search error: {e}")

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
                        return self._normalize_model(data)
        except Exception as e:
            print(f"[Civitai] Get model error: {e}")

        return None

    async def list_models(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """List Civitai models by type."""
        params = {
            "limit": min(limit, 100),
            "page": (offset // limit) + 1,
            "sort": "Most Downloaded",
        }

        if category:
            params["types"] = category

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
                        items = data.get("items", [])
                        return [self._normalize_model(m) for m in items]
        except Exception as e:
            print(f"[Civitai] List error: {e}")

        return []

    async def pull(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """Get download URL for Civitai model."""
        model = await self.get_model(model_id)
        if model and model.pull_url:
            return {
                "success": True,
                "provider": self.name,
                "model_id": model_id,
                "download_url": model.pull_url,
                "message": f"Download from: {model.pull_url}",
            }
        return {
            "success": False,
            "provider": self.name,
            "model_id": model_id,
            "error": "Could not find download URL",
        }

    async def health_check(self) -> bool:
        """Check if Civitai API is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models?limit=1",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False

    def _normalize_model(self, data: Dict[str, Any]) -> UnifiedModel:
        """Convert Civitai API response to UnifiedModel."""
        model_id = str(data.get("id", ""))
        name = data.get("name", "")
        model_type = data.get("type", "Checkpoint")

        # Get capability from type
        capability = self.TYPE_MAP.get(model_type, ModelCapability.IMAGE_GENERATION)

        # Get latest version info
        versions = data.get("modelVersions", [])
        latest_version = versions[0] if versions else {}
        files = latest_version.get("files", [])
        primary_file = files[0] if files else {}

        # File size
        file_size = primary_file.get("sizeKB", 0) / 1024 / 1024  # Convert to GB

        # Download URL
        download_url = primary_file.get("downloadUrl", "")

        # Tags
        tags = [t.get("name", "") for t in data.get("tags", [])]

        # Stats
        stats = data.get("stats", {})
        downloads = stats.get("downloadCount", 0)
        likes = stats.get("thumbsUpCount", 0)

        # Base model (SD version)
        base_model = latest_version.get("baseModel", "")

        return UnifiedModel(
            id=model_id,
            name=name,
            provider=self.name,
            provider_url=f"{self.base_url}/models/{model_id}",
            capabilities=[capability],
            architecture="diffusion",
            base_model=base_model,
            file_size_gb=file_size if file_size > 0 else None,
            format=primary_file.get("format", "safetensors"),
            license=ModelLicense.CREATIVEML if model_type == "Checkpoint" else ModelLicense.OTHER,
            commercial_use=False,  # Most Civitai models have restricted commercial use
            description=data.get("description", "")[:500] if data.get("description") else None,
            tags=[model_type.lower(), "diffusion", "image"] + tags[:15],
            metrics=ModelMetrics(
                downloads=downloads,
                likes=likes,
            ),
            pull_url=download_url,
            pull_runtime="automatic1111",  # Common runtime for SD models
            raw_data=data,
        )


# Register provider
registry.register(CivitaiProvider())
