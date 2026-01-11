"""
DeepSeek Provider - Chinese AI lab's models

DeepSeek is known for strong reasoning models (DeepSeek-R1) and
efficient coder models.
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


class DeepSeekProvider(ModelProvider):
    """Provider for DeepSeek models."""

    name = "deepseek"
    display_name = "DeepSeek"
    base_url = "https://www.deepseek.com"
    api_url = "https://api.deepseek.com"
    supports_pull = True  # Available on HuggingFace
    supports_search = True

    # Known DeepSeek models
    KNOWN_MODELS = {
        "deepseek-chat": {
            "name": "DeepSeek Chat",
            "params": 67,
            "context": 64000,
            "caps": ["chat", "code"],
            "hf_id": "deepseek-ai/deepseek-llm-67b-chat",
        },
        "deepseek-coder": {
            "name": "DeepSeek Coder",
            "params": 33,
            "context": 16000,
            "caps": ["code"],
            "hf_id": "deepseek-ai/deepseek-coder-33b-instruct",
        },
        "deepseek-coder-v2": {
            "name": "DeepSeek Coder V2",
            "params": 236,
            "context": 128000,
            "caps": ["code", "chat"],
            "hf_id": "deepseek-ai/DeepSeek-Coder-V2-Instruct",
        },
        "deepseek-r1": {
            "name": "DeepSeek R1",
            "params": 671,
            "context": 64000,
            "caps": ["reasoning", "math", "code"],
            "hf_id": "deepseek-ai/DeepSeek-R1",
        },
        "deepseek-r1-distill-llama-70b": {
            "name": "DeepSeek R1 Distill (70B)",
            "params": 70,
            "context": 64000,
            "caps": ["reasoning", "math"],
            "hf_id": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        },
        "deepseek-r1-distill-qwen-32b": {
            "name": "DeepSeek R1 Distill (32B)",
            "params": 32,
            "context": 64000,
            "caps": ["reasoning", "math"],
            "hf_id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        },
        "deepseek-r1-distill-qwen-14b": {
            "name": "DeepSeek R1 Distill (14B)",
            "params": 14,
            "context": 64000,
            "caps": ["reasoning", "math"],
            "hf_id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        },
        "deepseek-r1-distill-qwen-7b": {
            "name": "DeepSeek R1 Distill (7B)",
            "params": 7,
            "context": 64000,
            "caps": ["reasoning", "math"],
            "hf_id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        },
        "deepseek-r1-distill-qwen-1.5b": {
            "name": "DeepSeek R1 Distill (1.5B)",
            "params": 1.5,
            "context": 64000,
            "caps": ["reasoning"],
            "hf_id": "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        },
        "deepseek-v3": {
            "name": "DeepSeek V3",
            "params": 671,
            "context": 64000,
            "caps": ["chat", "code", "reasoning"],
            "hf_id": "deepseek-ai/DeepSeek-V3",
        },
        "deepseek-math": {
            "name": "DeepSeek Math",
            "params": 7,
            "context": 4096,
            "caps": ["math", "reasoning"],
            "hf_id": "deepseek-ai/deepseek-math-7b-instruct",
        },
        "deepseek-vl": {
            "name": "DeepSeek VL",
            "params": 7,
            "context": 4096,
            "caps": ["vision", "chat"],
            "hf_id": "deepseek-ai/deepseek-vl-7b-chat",
        },
    }

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")

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
        """Search DeepSeek models."""
        query_lower = query.lower()
        results = []

        for model_id, meta in self.KNOWN_MODELS.items():
            if (query_lower in model_id.lower() or
                query_lower in meta["name"].lower() or
                any(query_lower in cap for cap in meta.get("caps", []))):
                model = self._create_model(model_id, meta)
                results.append(model)

        results.sort(key=lambda m: m.match_score(query, filters), reverse=True)
        return results[offset:offset + limit]

    async def get_model(self, model_id: str) -> Optional[UnifiedModel]:
        """Get details for a specific DeepSeek model."""
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
        """List all DeepSeek models."""
        results = []

        for model_id, meta in self.KNOWN_MODELS.items():
            model = self._create_model(model_id, meta)
            if category:
                caps = [c.value for c in model.capabilities]
                if category.lower() not in caps:
                    continue
            results.append(model)

        return results[offset:offset + limit]

    async def pull(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """Generate pull instructions for DeepSeek model."""
        meta = self.KNOWN_MODELS.get(model_id, {})
        hf_id = meta.get("hf_id", f"deepseek-ai/{model_id}")

        return {
            "success": True,
            "provider": self.name,
            "model_id": model_id,
            "hf_id": hf_id,
            "pull_command": f"huggingface-cli download {hf_id}",
            "ollama_command": f"ollama pull deepseek-r1" if "r1" in model_id else None,
            "message": f"Download from HuggingFace: {hf_id}",
        }

    async def health_check(self) -> bool:
        """Check if DeepSeek API is available."""
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
        """Create UnifiedModel from DeepSeek model info."""
        cap_map = {
            "chat": ModelCapability.CHAT,
            "code": ModelCapability.CODE_GENERATION,
            "vision": ModelCapability.VISION_LANGUAGE,
            "reasoning": ModelCapability.REASONING,
            "math": ModelCapability.MATH,
        }

        capabilities = [
            cap_map[c] for c in meta.get("caps", ["chat"]) if c in cap_map
        ]

        hf_id = meta.get("hf_id", "")

        return UnifiedModel(
            id=model_id,
            name=meta["name"],
            provider=self.name,
            provider_url=f"https://huggingface.co/{hf_id}" if hf_id else self.base_url,
            capabilities=capabilities,
            architecture="transformer",
            parameter_count=meta.get("params"),
            license=ModelLicense.DEEPSEEK,
            commercial_use=True,  # DeepSeek license allows commercial use
            description=f"DeepSeek model: {meta['name']}",
            tags=["deepseek", "chinese"] + meta.get("caps", []),
            metrics=ModelMetrics(
                context_length=meta.get("context"),
            ),
            pull_command=f"huggingface-cli download {hf_id}" if hf_id else None,
            pull_runtime="transformers",
        )


# Register provider
registry.register(DeepSeekProvider())
