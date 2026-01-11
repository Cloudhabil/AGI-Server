"""
Mistral AI Provider - Mistral's model platform

Mistral AI provides high-quality open-weight models and API access.
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


class MistralProvider(ModelProvider):
    """Provider for Mistral AI models."""

    name = "mistral"
    display_name = "Mistral AI"
    base_url = "https://mistral.ai"
    api_url = "https://api.mistral.ai/v1"
    supports_pull = False  # API access primarily
    supports_search = True

    # Known Mistral models
    KNOWN_MODELS = {
        "mistral-large-latest": {
            "name": "Mistral Large",
            "params": 123,
            "context": 128000,
            "caps": ["chat", "code", "reasoning", "tool-use"],
            "commercial": True,
        },
        "mistral-medium-latest": {
            "name": "Mistral Medium",
            "params": None,
            "context": 32000,
            "caps": ["chat", "code"],
            "commercial": True,
        },
        "mistral-small-latest": {
            "name": "Mistral Small",
            "params": 22,
            "context": 32000,
            "caps": ["chat", "code"],
            "commercial": True,
        },
        "codestral-latest": {
            "name": "Codestral",
            "params": 22,
            "context": 32000,
            "caps": ["code"],
            "commercial": False,  # Non-commercial license
        },
        "codestral-mamba-latest": {
            "name": "Codestral Mamba",
            "params": 7,
            "context": 256000,
            "caps": ["code"],
            "commercial": True,
        },
        "open-mistral-nemo": {
            "name": "Mistral Nemo",
            "params": 12,
            "context": 128000,
            "caps": ["chat", "code"],
            "commercial": True,
            "open_weight": True,
        },
        "open-mixtral-8x7b": {
            "name": "Mixtral 8x7B",
            "params": 47,
            "context": 32000,
            "caps": ["chat", "code"],
            "commercial": True,
            "open_weight": True,
        },
        "open-mixtral-8x22b": {
            "name": "Mixtral 8x22B",
            "params": 141,
            "context": 64000,
            "caps": ["chat", "code"],
            "commercial": True,
            "open_weight": True,
        },
        "open-mistral-7b": {
            "name": "Mistral 7B",
            "params": 7,
            "context": 32000,
            "caps": ["chat"],
            "commercial": True,
            "open_weight": True,
        },
        "ministral-3b-latest": {
            "name": "Ministral 3B",
            "params": 3,
            "context": 128000,
            "caps": ["chat", "code"],
            "commercial": True,
        },
        "ministral-8b-latest": {
            "name": "Ministral 8B",
            "params": 8,
            "context": 128000,
            "caps": ["chat", "code"],
            "commercial": True,
        },
        "pixtral-12b-latest": {
            "name": "Pixtral 12B",
            "params": 12,
            "context": 128000,
            "caps": ["chat", "vision"],
            "commercial": True,
            "open_weight": True,
        },
        "mistral-embed": {
            "name": "Mistral Embed",
            "params": None,
            "context": 8000,
            "caps": ["embed"],
            "commercial": True,
        },
    }

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")

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
        """Search Mistral models."""
        query_lower = query.lower()
        results = []

        for model_id, meta in self.KNOWN_MODELS.items():
            if (query_lower in model_id.lower() or
                query_lower in meta["name"].lower()):
                model = self._create_model(model_id, meta)
                results.append(model)

        results.sort(key=lambda m: m.match_score(query, filters), reverse=True)
        return results[offset:offset + limit]

    async def get_model(self, model_id: str) -> Optional[UnifiedModel]:
        """Get details for a specific Mistral model."""
        meta = self.KNOWN_MODELS.get(model_id)
        if meta:
            return self._create_model(model_id, meta)
        return None

    async def list_models(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """List all Mistral models."""
        # Try API first
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models",
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        api_models = data.get("data", [])
                        # Merge with known models
                        for m in api_models:
                            model_id = m.get("id", "")
                            if model_id not in self.KNOWN_MODELS:
                                self.KNOWN_MODELS[model_id] = {
                                    "name": model_id,
                                    "caps": ["chat"],
                                    "commercial": True,
                                }
        except Exception:
            pass  # Fall back to known models

        results = []
        for model_id, meta in self.KNOWN_MODELS.items():
            model = self._create_model(model_id, meta)
            if category:
                caps = [c.value for c in model.capabilities]
                if category.lower() not in caps:
                    continue
            results.append(model)

        return results[offset:offset + limit]

    async def health_check(self) -> bool:
        """Check if Mistral API is available."""
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

    def _create_model(self, model_id: str, meta: Dict[str, Any]) -> UnifiedModel:
        """Create UnifiedModel from Mistral model info."""
        cap_map = {
            "chat": ModelCapability.CHAT,
            "code": ModelCapability.CODE_GENERATION,
            "vision": ModelCapability.VISION_LANGUAGE,
            "reasoning": ModelCapability.REASONING,
            "embed": ModelCapability.EMBEDDING,
            "tool-use": ModelCapability.TOOL_USE,
        }

        capabilities = [
            cap_map[c] for c in meta.get("caps", ["chat"]) if c in cap_map
        ]

        tags = ["mistral"]
        if meta.get("open_weight"):
            tags.append("open-weight")

        return UnifiedModel(
            id=model_id,
            name=meta["name"],
            provider=self.name,
            provider_url=f"{self.base_url}/technology",
            capabilities=capabilities,
            architecture="transformer",
            parameter_count=meta.get("params"),
            license=ModelLicense.APACHE_2 if meta.get("open_weight") else ModelLicense.PROPRIETARY,
            commercial_use=meta.get("commercial", True),
            description=f"Mistral AI model: {meta['name']}",
            tags=tags,
            metrics=ModelMetrics(
                context_length=meta.get("context"),
            ),
            pull_command=f"# Use Mistral API or download from HuggingFace\nmistral-client chat --model {model_id}",
            pull_runtime="mistral",
        )


# Register provider
registry.register(MistralProvider())
