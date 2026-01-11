"""
LM Studio Provider - Desktop LLM application

LM Studio provides a GUI for running local models. It supports
GGUF models and has its own model discovery system.
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


class LMStudioProvider(ModelProvider):
    """Provider for LM Studio models."""

    name = "lmstudio"
    display_name = "LM Studio"
    base_url = "https://lmstudio.ai"
    api_url = "http://localhost:1234/v1"  # Local API
    supports_pull = True  # Via HuggingFace
    supports_search = True

    # Popular models on LM Studio
    KNOWN_MODELS = {
        "TheBloke/Llama-2-7B-Chat-GGUF": {
            "name": "Llama 2 7B Chat",
            "params": 7,
            "quant": "q4_k_m",
            "caps": ["chat"],
        },
        "TheBloke/Llama-2-13B-chat-GGUF": {
            "name": "Llama 2 13B Chat",
            "params": 13,
            "quant": "q4_k_m",
            "caps": ["chat"],
        },
        "TheBloke/Mistral-7B-Instruct-v0.2-GGUF": {
            "name": "Mistral 7B Instruct",
            "params": 7,
            "quant": "q4_k_m",
            "caps": ["chat", "code"],
        },
        "TheBloke/CodeLlama-7B-Instruct-GGUF": {
            "name": "CodeLlama 7B",
            "params": 7,
            "quant": "q4_k_m",
            "caps": ["code"],
        },
        "TheBloke/Mixtral-8x7B-Instruct-v0.1-GGUF": {
            "name": "Mixtral 8x7B",
            "params": 47,
            "quant": "q4_k_m",
            "caps": ["chat", "code"],
        },
        "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF": {
            "name": "Llama 3.1 8B",
            "params": 8,
            "quant": "q4_k_m",
            "caps": ["chat", "code"],
        },
        "bartowski/Qwen2.5-7B-Instruct-GGUF": {
            "name": "Qwen 2.5 7B",
            "params": 7,
            "quant": "q4_k_m",
            "caps": ["chat", "code"],
        },
        "bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF": {
            "name": "DeepSeek R1 Distill 7B",
            "params": 7,
            "quant": "q4_k_m",
            "caps": ["reasoning", "math"],
        },
        "lmstudio-community/gemma-2-9b-it-GGUF": {
            "name": "Gemma 2 9B",
            "params": 9,
            "quant": "q4_k_m",
            "caps": ["chat"],
        },
        "lmstudio-community/Phi-3.5-mini-instruct-GGUF": {
            "name": "Phi 3.5 Mini",
            "params": 3.8,
            "quant": "q4_k_m",
            "caps": ["chat", "code"],
        },
    }

    def __init__(self, api_url: str = None, **kwargs):
        super().__init__(**kwargs)
        self.api_url = api_url or os.getenv("LMSTUDIO_API_URL", "http://localhost:1234/v1")

    async def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """Search LM Studio compatible models."""
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
        """Get details for a specific model."""
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
        """List LM Studio models."""
        # Try to get locally loaded models first
        local_models = await self._get_local_models()

        results = []
        for model_id, meta in self.KNOWN_MODELS.items():
            model = self._create_model(model_id, meta)

            # Mark as installed if found locally
            if any(model_id in lm for lm in local_models):
                model.tags.append("installed")

            if category:
                caps = [c.value for c in model.capabilities]
                if category.lower() not in caps:
                    continue

            results.append(model)

        return results[offset:offset + limit]

    async def pull(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """Generate download instructions for LM Studio."""
        return {
            "success": True,
            "provider": self.name,
            "model_id": model_id,
            "pull_command": f"# Download via LM Studio UI or HuggingFace\nhuggingface-cli download {model_id}",
            "message": f"Use LM Studio's model browser or download from HuggingFace: {model_id}",
        }

    async def health_check(self) -> bool:
        """Check if LM Studio local server is running."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def _get_local_models(self) -> List[str]:
        """Get models loaded in LM Studio."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [m.get("id", "") for m in data.get("data", [])]
        except Exception:
            pass
        return []

    def _create_model(self, model_id: str, meta: Dict[str, Any]) -> UnifiedModel:
        """Create UnifiedModel from LM Studio model info."""
        cap_map = {
            "chat": ModelCapability.CHAT,
            "code": ModelCapability.CODE_GENERATION,
            "reasoning": ModelCapability.REASONING,
            "math": ModelCapability.MATH,
        }

        capabilities = [
            cap_map[c] for c in meta.get("caps", ["chat"]) if c in cap_map
        ]

        quant_map = {
            "q4_0": QuantizationType.GGUF_Q4_0,
            "q4_k_m": QuantizationType.GGUF_Q4_K_M,
            "q5_k_m": QuantizationType.GGUF_Q5_K_M,
            "q8_0": QuantizationType.GGUF_Q8_0,
        }

        return UnifiedModel(
            id=model_id,
            name=meta["name"],
            provider=self.name,
            provider_url=f"https://huggingface.co/{model_id}",
            capabilities=capabilities,
            architecture="transformer",
            parameter_count=meta.get("params"),
            quantization=quant_map.get(meta.get("quant", ""), QuantizationType.GGUF_Q4_K_M),
            format="gguf",
            commercial_use=True,
            description=f"LM Studio compatible: {meta['name']}",
            tags=["lmstudio", "gguf", "local"],
            pull_command=f"huggingface-cli download {model_id}",
            pull_runtime="lmstudio",
        )


# Register provider
registry.register(LMStudioProvider())
