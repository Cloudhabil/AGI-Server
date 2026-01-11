"""
GPT4All Provider - Nomic's local LLM platform

GPT4All provides curated, easy-to-use local models with a
simple desktop application.
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
    ModelLicense,
    registry,
)


class GPT4AllProvider(ModelProvider):
    """Provider for GPT4All models."""

    name = "gpt4all"
    display_name = "GPT4All"
    base_url = "https://gpt4all.io"
    api_url = "https://raw.githubusercontent.com/nomic-ai/gpt4all/main/gpt4all-chat/metadata/models3.json"
    supports_pull = True
    supports_search = True

    # Known GPT4All models (from their curated list)
    KNOWN_MODELS = {
        "Llama 3.2 3B Instruct": {
            "filename": "Llama-3.2-3B-Instruct-Q4_0.gguf",
            "params": 3,
            "ram": 4,
            "caps": ["chat"],
            "license": "llama-3.1",
        },
        "Llama 3.1 8B Instruct": {
            "filename": "Meta-Llama-3.1-8B-Instruct-Q4_0.gguf",
            "params": 8,
            "ram": 8,
            "caps": ["chat", "code"],
            "license": "llama-3.1",
        },
        "Mistral Instruct": {
            "filename": "mistral-7b-instruct-v0.1.Q4_0.gguf",
            "params": 7,
            "ram": 8,
            "caps": ["chat", "code"],
            "license": "apache-2.0",
        },
        "Mistral OpenOrca": {
            "filename": "mistral-7b-openorca.gguf2.Q4_0.gguf",
            "params": 7,
            "ram": 8,
            "caps": ["chat"],
            "license": "apache-2.0",
        },
        "Nous Hermes 2 Mistral": {
            "filename": "Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf",
            "params": 7,
            "ram": 8,
            "caps": ["chat", "code"],
            "license": "apache-2.0",
        },
        "Phi-3 Mini Instruct": {
            "filename": "Phi-3-mini-4k-instruct.Q4_0.gguf",
            "params": 3.8,
            "ram": 4,
            "caps": ["chat", "code", "reasoning"],
            "license": "mit",
        },
        "GPT4All Falcon": {
            "filename": "gpt4all-falcon-q4_0.gguf",
            "params": 7,
            "ram": 8,
            "caps": ["chat"],
            "license": "apache-2.0",
        },
        "Orca 2 Medium": {
            "filename": "orca-2-7b.Q4_0.gguf",
            "params": 7,
            "ram": 8,
            "caps": ["chat", "reasoning"],
            "license": "microsoft",
        },
        "Mini Orca": {
            "filename": "orca-mini-3b-gguf2-q4_0.gguf",
            "params": 3,
            "ram": 4,
            "caps": ["chat"],
            "license": "cc-by-nc-sa",
        },
        "DeepSeek Coder Instruct": {
            "filename": "deepseek-coder-6.7b-instruct.Q4_0.gguf",
            "params": 6.7,
            "ram": 8,
            "caps": ["code"],
            "license": "deepseek",
        },
        "Qwen2.5 Instruct": {
            "filename": "Qwen2.5-7B-Instruct-Q4_0.gguf",
            "params": 7,
            "ram": 8,
            "caps": ["chat", "code"],
            "license": "apache-2.0",
        },
        "Nomic Embed": {
            "filename": "nomic-embed-text-v1.5.f16.gguf",
            "params": 0.137,
            "ram": 1,
            "caps": ["embed"],
            "license": "apache-2.0",
        },
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """Search GPT4All models."""
        query_lower = query.lower()
        results = []

        for name, meta in self.KNOWN_MODELS.items():
            if (query_lower in name.lower() or
                query_lower in meta.get("filename", "").lower()):
                model = self._create_model(name, meta)
                results.append(model)

        results.sort(key=lambda m: m.match_score(query, filters), reverse=True)
        return results[offset:offset + limit]

    async def get_model(self, model_id: str) -> Optional[UnifiedModel]:
        """Get details for a specific GPT4All model."""
        meta = self.KNOWN_MODELS.get(model_id)
        if meta:
            return self._create_model(model_id, meta)

        # Try to match by filename
        for name, m in self.KNOWN_MODELS.items():
            if m.get("filename") == model_id:
                return self._create_model(name, m)

        return None

    async def list_models(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """List all GPT4All models."""
        # Try to fetch latest from GitHub
        await self._fetch_model_list()

        results = []
        for name, meta in self.KNOWN_MODELS.items():
            model = self._create_model(name, meta)

            if category:
                caps = [c.value for c in model.capabilities]
                if category.lower() not in caps:
                    continue

            results.append(model)

        return results[offset:offset + limit]

    async def pull(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """Generate download instructions for GPT4All model."""
        meta = self.KNOWN_MODELS.get(model_id, {})
        filename = meta.get("filename", model_id)

        return {
            "success": True,
            "provider": self.name,
            "model_id": model_id,
            "filename": filename,
            "download_url": f"https://gpt4all.io/models/gguf/{filename}",
            "message": f"Download via GPT4All app or directly from: https://gpt4all.io/models/gguf/{filename}",
        }

    async def health_check(self) -> bool:
        """Check if GPT4All model list is accessible."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.api_url,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False

    async def _fetch_model_list(self) -> None:
        """Fetch latest model list from GPT4All GitHub."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.api_url,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Update known models with fresh data
                        for item in data:
                            name = item.get("name", "")
                            if name and name not in self.KNOWN_MODELS:
                                self.KNOWN_MODELS[name] = {
                                    "filename": item.get("filename", ""),
                                    "params": item.get("parameters", 0) / 1e9 if item.get("parameters") else None,
                                    "ram": item.get("ramrequired", 8),
                                    "caps": ["chat"],
                                    "license": item.get("license", "unknown"),
                                }
        except Exception:
            pass

    def _create_model(self, name: str, meta: Dict[str, Any]) -> UnifiedModel:
        """Create UnifiedModel from GPT4All model info."""
        cap_map = {
            "chat": ModelCapability.CHAT,
            "code": ModelCapability.CODE_GENERATION,
            "reasoning": ModelCapability.REASONING,
            "embed": ModelCapability.EMBEDDING,
        }

        capabilities = [
            cap_map[c] for c in meta.get("caps", ["chat"]) if c in cap_map
        ]

        filename = meta.get("filename", "")

        return UnifiedModel(
            id=filename or name,
            name=name,
            provider=self.name,
            provider_url=f"{self.base_url}/index.html",
            capabilities=capabilities,
            architecture="transformer",
            parameter_count=meta.get("params"),
            quantization=QuantizationType.GGUF_Q4_0,
            format="gguf",
            license=self._infer_license(meta.get("license", "")),
            commercial_use=meta.get("license") in ["apache-2.0", "mit"],
            description=f"GPT4All curated model: {name}",
            tags=["gpt4all", "gguf", "local", "curated"],
            metrics=ModelMetrics(
                memory_required_gb=meta.get("ram"),
            ),
            pull_url=f"https://gpt4all.io/models/gguf/{filename}" if filename else None,
            pull_runtime="gpt4all",
        )


# Register provider
registry.register(GPT4AllProvider())
