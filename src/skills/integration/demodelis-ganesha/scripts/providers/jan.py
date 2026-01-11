"""
Jan.ai Provider - Open-source desktop AI assistant

Jan provides a cross-platform desktop application for running
local models with a focus on privacy and ease of use.
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


class JanProvider(ModelProvider):
    """Provider for Jan.ai models."""

    name = "jan"
    display_name = "Jan.ai"
    base_url = "https://jan.ai"
    api_url = "http://localhost:1337/v1"  # Local API
    supports_pull = True
    supports_search = True

    # Popular models supported by Jan
    KNOWN_MODELS = {
        "llama3.2-3b-instruct": {
            "name": "Llama 3.2 3B Instruct",
            "params": 3,
            "caps": ["chat"],
            "hf_id": "bartowski/Llama-3.2-3B-Instruct-GGUF",
        },
        "llama3.1-8b-instruct": {
            "name": "Llama 3.1 8B Instruct",
            "params": 8,
            "caps": ["chat", "code"],
            "hf_id": "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
        },
        "mistral-7b-instruct": {
            "name": "Mistral 7B Instruct",
            "params": 7,
            "caps": ["chat", "code"],
            "hf_id": "TheBloke/Mistral-7B-Instruct-v0.2-GGUF",
        },
        "qwen2.5-7b-instruct": {
            "name": "Qwen 2.5 7B Instruct",
            "params": 7,
            "caps": ["chat", "code"],
            "hf_id": "bartowski/Qwen2.5-7B-Instruct-GGUF",
        },
        "phi-3-mini": {
            "name": "Phi-3 Mini",
            "params": 3.8,
            "caps": ["chat", "code", "reasoning"],
            "hf_id": "microsoft/Phi-3-mini-4k-instruct-gguf",
        },
        "gemma-2-9b": {
            "name": "Gemma 2 9B",
            "params": 9,
            "caps": ["chat"],
            "hf_id": "lmstudio-community/gemma-2-9b-it-GGUF",
        },
        "deepseek-r1-distill-7b": {
            "name": "DeepSeek R1 Distill 7B",
            "params": 7,
            "caps": ["reasoning", "math"],
            "hf_id": "bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF",
        },
        "codellama-7b-instruct": {
            "name": "CodeLlama 7B Instruct",
            "params": 7,
            "caps": ["code"],
            "hf_id": "TheBloke/CodeLlama-7B-Instruct-GGUF",
        },
        "tinyllama-1.1b-chat": {
            "name": "TinyLlama 1.1B Chat",
            "params": 1.1,
            "caps": ["chat"],
            "hf_id": "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF",
        },
        "nomic-embed-text": {
            "name": "Nomic Embed Text",
            "params": 0.137,
            "caps": ["embed"],
            "hf_id": "nomic-ai/nomic-embed-text-v1.5-GGUF",
        },
    }

    def __init__(self, api_url: str = None, **kwargs):
        super().__init__(**kwargs)
        self.api_url = api_url or os.getenv("JAN_API_URL", "http://localhost:1337/v1")

    async def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """Search Jan.ai compatible models."""
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
        """List Jan.ai models."""
        # Try to get locally installed models
        local_models = await self._get_local_models()

        results = []
        for model_id, meta in self.KNOWN_MODELS.items():
            model = self._create_model(model_id, meta)

            if model_id in local_models:
                model.tags.append("installed")

            if category:
                caps = [c.value for c in model.capabilities]
                if category.lower() not in caps:
                    continue

            results.append(model)

        return results[offset:offset + limit]

    async def pull(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """Generate download instructions for Jan model."""
        meta = self.KNOWN_MODELS.get(model_id, {})
        hf_id = meta.get("hf_id", "")

        return {
            "success": True,
            "provider": self.name,
            "model_id": model_id,
            "hf_id": hf_id,
            "message": f"Download via Jan app's model hub or from HuggingFace: {hf_id}",
            "pull_command": f"# Use Jan's built-in model browser or:\nhuggingface-cli download {hf_id}",
        }

    async def health_check(self) -> bool:
        """Check if Jan local server is running."""
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
        """Get models installed in Jan."""
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
        """Create UnifiedModel from Jan model info."""
        cap_map = {
            "chat": ModelCapability.CHAT,
            "code": ModelCapability.CODE_GENERATION,
            "reasoning": ModelCapability.REASONING,
            "math": ModelCapability.MATH,
            "embed": ModelCapability.EMBEDDING,
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
            quantization=QuantizationType.GGUF_Q4_K_M,
            format="gguf",
            commercial_use=True,
            description=f"Jan.ai compatible: {meta['name']}",
            tags=["jan", "gguf", "local", "privacy"],
            pull_command=f"huggingface-cli download {hf_id}" if hf_id else None,
            pull_runtime="jan",
        )


# Register provider
registry.register(JanProvider())
