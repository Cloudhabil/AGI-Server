"""
Vertex AI Model Garden Provider - Google Cloud's model marketplace

Vertex AI Model Garden provides access to Google's models and
curated third-party models for deployment on GCP.
"""

import os
import asyncio
from typing import Any, Dict, List, Optional

from .base import (
    ModelProvider,
    UnifiedModel,
    ModelCapability,
    ModelMetrics,
    ModelLicense,
    registry,
)


class VertexAIProvider(ModelProvider):
    """Provider for Google Cloud Vertex AI Model Garden."""

    name = "vertexai"
    display_name = "Vertex AI Model Garden"
    base_url = "https://console.cloud.google.com/vertex-ai/model-garden"
    supports_pull = False  # Deployment only via GCP
    supports_search = True

    # Known Vertex AI Model Garden models
    KNOWN_MODELS = {
        "gemini-1.5-pro": {
            "name": "Gemini 1.5 Pro",
            "params": None,
            "context": 2000000,
            "caps": ["chat", "code", "vision", "reasoning"],
            "license": "proprietary",
        },
        "gemini-1.5-flash": {
            "name": "Gemini 1.5 Flash",
            "params": None,
            "context": 1000000,
            "caps": ["chat", "code", "vision"],
            "license": "proprietary",
        },
        "gemini-2.0-flash": {
            "name": "Gemini 2.0 Flash",
            "params": None,
            "context": 1000000,
            "caps": ["chat", "code", "vision", "reasoning"],
            "license": "proprietary",
        },
        "gemma-2-27b-it": {
            "name": "Gemma 2 27B IT",
            "params": 27,
            "caps": ["chat"],
            "license": "gemma",
        },
        "gemma-2-9b-it": {
            "name": "Gemma 2 9B IT",
            "params": 9,
            "caps": ["chat"],
            "license": "gemma",
        },
        "gemma-2-2b-it": {
            "name": "Gemma 2 2B IT",
            "params": 2,
            "caps": ["chat"],
            "license": "gemma",
        },
        "codegemma-7b-it": {
            "name": "CodeGemma 7B IT",
            "params": 7,
            "caps": ["code"],
            "license": "gemma",
        },
        "palm-2-text-bison": {
            "name": "PaLM 2 Text Bison",
            "params": None,
            "caps": ["chat"],
            "license": "proprietary",
        },
        "text-embedding-005": {
            "name": "Text Embedding 005",
            "params": None,
            "caps": ["embed"],
            "license": "proprietary",
        },
        "imagen-3": {
            "name": "Imagen 3",
            "params": None,
            "caps": ["image"],
            "license": "proprietary",
        },
        "llama-3.1-405b": {
            "name": "Llama 3.1 405B",
            "params": 405,
            "caps": ["chat", "code"],
            "license": "llama-3.1",
        },
        "llama-3.1-70b": {
            "name": "Llama 3.1 70B",
            "params": 70,
            "caps": ["chat", "code"],
            "license": "llama-3.1",
        },
        "claude-3-5-sonnet": {
            "name": "Claude 3.5 Sonnet",
            "params": None,
            "caps": ["chat", "code", "reasoning"],
            "license": "proprietary",
        },
        "claude-3-opus": {
            "name": "Claude 3 Opus",
            "params": None,
            "caps": ["chat", "code", "reasoning"],
            "license": "proprietary",
        },
        "mistral-large": {
            "name": "Mistral Large",
            "params": 123,
            "caps": ["chat", "code"],
            "license": "mistral",
        },
        "codestral": {
            "name": "Codestral",
            "params": 22,
            "caps": ["code"],
            "license": "mistral",
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
        """Search Vertex AI Model Garden models."""
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
        """Get details for a specific Vertex AI model."""
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
        """List Vertex AI Model Garden models."""
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
        """Vertex AI is always available (via GCP)."""
        return True

    def _create_model(self, model_id: str, meta: Dict[str, Any]) -> UnifiedModel:
        """Create UnifiedModel from Vertex AI model info."""
        cap_map = {
            "chat": ModelCapability.CHAT,
            "code": ModelCapability.CODE_GENERATION,
            "vision": ModelCapability.VISION_LANGUAGE,
            "reasoning": ModelCapability.REASONING,
            "image": ModelCapability.IMAGE_GENERATION,
            "embed": ModelCapability.EMBEDDING,
        }

        capabilities = [
            cap_map[c] for c in meta.get("caps", ["chat"]) if c in cap_map
        ]

        return UnifiedModel(
            id=model_id,
            name=meta["name"],
            provider=self.name,
            provider_url=f"{self.base_url}/{model_id}",
            capabilities=capabilities,
            architecture="transformer",
            parameter_count=meta.get("params"),
            license=self._infer_license(meta.get("license", "")),
            commercial_use=True,  # All Vertex AI models can be used commercially
            description=f"Google Cloud Vertex AI: {meta['name']}",
            tags=["vertexai", "gcp", "google", "cloud", "managed"],
            metrics=ModelMetrics(
                context_length=meta.get("context"),
            ),
            pull_command=f"# Deploy via GCP Console or Vertex AI SDK\nfrom vertexai.generative_models import GenerativeModel\nmodel = GenerativeModel('{model_id}')",
            pull_runtime="vertexai",
        )


# Register provider
registry.register(VertexAIProvider())
