"""
Ollama Provider - Local model runtime

Ollama provides pre-quantized models optimized for local inference.
Supports GGUF format with various quantization levels.
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


class OllamaProvider(ModelProvider):
    """Provider for Ollama local model runtime."""

    name = "ollama"
    display_name = "Ollama"
    base_url = "http://localhost:11434"
    library_url = "https://ollama.com/library"
    supports_pull = True
    supports_search = True

    # Popular models with metadata (since Ollama API is limited)
    KNOWN_MODELS = {
        "llama3.2": {"params": 3, "caps": ["chat", "code"], "license": "llama-3.1"},
        "llama3.1": {"params": 8, "caps": ["chat", "code"], "license": "llama-3.1"},
        "llama3.1:70b": {"params": 70, "caps": ["chat", "code"], "license": "llama-3.1"},
        "llama3": {"params": 8, "caps": ["chat"], "license": "llama-3"},
        "llama2": {"params": 7, "caps": ["chat"], "license": "llama"},
        "mistral": {"params": 7, "caps": ["chat", "code"], "license": "apache-2.0"},
        "mixtral": {"params": 47, "caps": ["chat", "code"], "license": "apache-2.0"},
        "codellama": {"params": 7, "caps": ["code"], "license": "llama"},
        "codegemma": {"params": 7, "caps": ["code"], "license": "gemma"},
        "gemma2": {"params": 9, "caps": ["chat"], "license": "gemma"},
        "gemma": {"params": 7, "caps": ["chat"], "license": "gemma"},
        "qwen2.5": {"params": 7, "caps": ["chat", "code"], "license": "apache-2.0"},
        "qwen2.5-coder": {"params": 7, "caps": ["code"], "license": "apache-2.0"},
        "qwen2": {"params": 7, "caps": ["chat"], "license": "apache-2.0"},
        "phi3": {"params": 3.8, "caps": ["chat", "reason"], "license": "mit"},
        "phi3.5": {"params": 3.8, "caps": ["chat", "reason"], "license": "mit"},
        "deepseek-r1": {"params": 7, "caps": ["reason", "math"], "license": "deepseek"},
        "deepseek-coder-v2": {"params": 16, "caps": ["code"], "license": "deepseek"},
        "starcoder2": {"params": 7, "caps": ["code"], "license": "bigcode"},
        "llava": {"params": 7, "caps": ["vision"], "license": "llama"},
        "llava-llama3": {"params": 8, "caps": ["vision"], "license": "llama-3"},
        "nomic-embed-text": {"params": 0.137, "caps": ["embed"], "license": "apache-2.0"},
        "mxbai-embed-large": {"params": 0.335, "caps": ["embed"], "license": "apache-2.0"},
        "all-minilm": {"params": 0.023, "caps": ["embed"], "license": "apache-2.0"},
    }

    def __init__(self, base_url: str = None, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")

    async def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """Search Ollama library."""
        # Get local models first
        local_models = await self._get_local_models()

        # Match against known models
        results = []
        query_lower = query.lower()

        for model_name, meta in self.KNOWN_MODELS.items():
            # Check if matches query
            if query_lower in model_name.lower():
                model = self._create_model(model_name, meta, model_name in local_models)
                results.append(model)

        # Also include any local models not in known list
        for local_name in local_models:
            base_name = local_name.split(":")[0]
            if base_name not in self.KNOWN_MODELS and query_lower in local_name.lower():
                model = self._create_model(local_name, {}, True)
                results.append(model)

        # Sort by relevance
        results.sort(key=lambda m: m.match_score(query, filters), reverse=True)

        return results[offset:offset + limit]

    async def get_model(self, model_id: str) -> Optional[UnifiedModel]:
        """Get details for a specific Ollama model."""
        base_name = model_id.split(":")[0]
        meta = self.KNOWN_MODELS.get(base_name, {})

        local_models = await self._get_local_models()
        is_local = model_id in local_models or base_name in local_models

        return self._create_model(model_id, meta, is_local)

    async def list_models(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """List available Ollama models."""
        local_models = await self._get_local_models()

        results = []
        for model_name, meta in self.KNOWN_MODELS.items():
            model = self._create_model(model_name, meta, model_name in local_models)

            # Filter by category if specified
            if category:
                caps = [c.value for c in model.capabilities]
                if category.lower() not in caps:
                    continue

            results.append(model)

        return results[offset:offset + limit]

    async def pull(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """Pull a model from Ollama registry."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json={"name": model_id, "stream": False},
                    timeout=aiohttp.ClientTimeout(total=3600),  # 1 hour timeout
                ) as resp:
                    if resp.status == 200:
                        return {
                            "success": True,
                            "provider": self.name,
                            "model_id": model_id,
                            "message": f"Successfully pulled {model_id}",
                        }
                    else:
                        error = await resp.text()
                        return {
                            "success": False,
                            "provider": self.name,
                            "model_id": model_id,
                            "error": error,
                        }
        except Exception as e:
            return {
                "success": False,
                "provider": self.name,
                "model_id": model_id,
                "error": str(e),
            }

    async def health_check(self) -> bool:
        """Check if Ollama is running."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def _get_local_models(self) -> set:
        """Get list of locally installed models."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = data.get("models", [])
                        return {m.get("name", "").split(":")[0] for m in models}
        except Exception:
            pass
        return set()

    def _create_model(
        self,
        model_name: str,
        meta: Dict[str, Any],
        is_local: bool,
    ) -> UnifiedModel:
        """Create UnifiedModel from Ollama model info."""
        base_name = model_name.split(":")[0]
        tag = model_name.split(":")[-1] if ":" in model_name else "latest"

        # Infer quantization from tag
        quant = QuantizationType.NONE
        if "q4_0" in tag:
            quant = QuantizationType.GGUF_Q4_0
        elif "q4_k_m" in tag or "q4" in tag:
            quant = QuantizationType.GGUF_Q4_K_M
        elif "q5_k_m" in tag or "q5" in tag:
            quant = QuantizationType.GGUF_Q5_K_M
        elif "q8" in tag:
            quant = QuantizationType.GGUF_Q8_0
        elif "fp16" in tag:
            quant = QuantizationType.FP16

        # Build capabilities
        cap_map = {
            "chat": ModelCapability.CHAT,
            "code": ModelCapability.CODE_GENERATION,
            "vision": ModelCapability.VISION_LANGUAGE,
            "embed": ModelCapability.EMBEDDING,
            "reason": ModelCapability.REASONING,
            "math": ModelCapability.MATH,
        }
        capabilities = [
            cap_map[c] for c in meta.get("caps", ["chat"]) if c in cap_map
        ]

        return UnifiedModel(
            id=model_name,
            name=base_name.replace("-", " ").title(),
            provider=self.name,
            provider_url=f"{self.library_url}/{base_name}",
            capabilities=capabilities,
            architecture="transformer",
            parameter_count=meta.get("params"),
            quantization=quant,
            format="gguf",
            license=self._infer_license(meta.get("license", "")),
            commercial_use=meta.get("license", "") in ["apache-2.0", "mit"],
            description=f"Ollama model: {model_name}",
            tags=[base_name, "ollama", "local", "gguf"] + (["installed"] if is_local else []),
            pull_command=f"ollama pull {model_name}",
            pull_runtime="ollama",
            metrics=ModelMetrics(),
        )


# Register provider
registry.register(OllamaProvider())
