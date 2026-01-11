"""
GitHub Models Provider - GitHub's model hosting

GitHub Models provides curated models with integration into
GitHub ecosystem, including Codespaces and Actions.
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


class GitHubModelsProvider(ModelProvider):
    """Provider for GitHub Models."""

    name = "github"
    display_name = "GitHub Models"
    base_url = "https://github.com/marketplace/models"
    api_url = "https://api.github.com"
    supports_pull = False  # GitHub Models are API-access only
    supports_search = True

    # Known GitHub Models (API is limited, so we maintain a catalog)
    KNOWN_MODELS = {
        "gpt-4o": {
            "name": "GPT-4o",
            "provider_org": "openai",
            "caps": ["chat", "vision", "code"],
            "context": 128000,
        },
        "gpt-4o-mini": {
            "name": "GPT-4o Mini",
            "provider_org": "openai",
            "caps": ["chat", "code"],
            "context": 128000,
        },
        "o1-preview": {
            "name": "o1-preview",
            "provider_org": "openai",
            "caps": ["reasoning", "math"],
            "context": 128000,
        },
        "o1-mini": {
            "name": "o1-mini",
            "provider_org": "openai",
            "caps": ["reasoning", "math", "code"],
            "context": 128000,
        },
        "claude-3.5-sonnet": {
            "name": "Claude 3.5 Sonnet",
            "provider_org": "anthropic",
            "caps": ["chat", "code", "reasoning"],
            "context": 200000,
        },
        "llama-3.1-405b": {
            "name": "Llama 3.1 405B",
            "provider_org": "meta",
            "caps": ["chat", "code"],
            "params": 405,
            "context": 128000,
        },
        "llama-3.1-70b": {
            "name": "Llama 3.1 70B",
            "provider_org": "meta",
            "caps": ["chat", "code"],
            "params": 70,
            "context": 128000,
        },
        "llama-3.1-8b": {
            "name": "Llama 3.1 8B",
            "provider_org": "meta",
            "caps": ["chat", "code"],
            "params": 8,
            "context": 128000,
        },
        "mistral-large": {
            "name": "Mistral Large",
            "provider_org": "mistral",
            "caps": ["chat", "code"],
            "context": 128000,
        },
        "mistral-nemo": {
            "name": "Mistral Nemo",
            "provider_org": "mistral",
            "caps": ["chat", "code"],
            "params": 12,
            "context": 128000,
        },
        "phi-3.5-moe": {
            "name": "Phi-3.5 MoE",
            "provider_org": "microsoft",
            "caps": ["chat", "code", "reasoning"],
            "params": 42,
            "context": 128000,
        },
        "phi-3.5-mini": {
            "name": "Phi-3.5 Mini",
            "provider_org": "microsoft",
            "caps": ["chat", "code"],
            "params": 3.8,
            "context": 128000,
        },
        "cohere-command-r-plus": {
            "name": "Command R+",
            "provider_org": "cohere",
            "caps": ["chat", "tool-use"],
            "context": 128000,
        },
    }

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.api_key = api_key or os.getenv("GITHUB_TOKEN")

    async def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """Search GitHub Models."""
        query_lower = query.lower()
        results = []

        for model_id, meta in self.KNOWN_MODELS.items():
            # Check if matches query
            if (query_lower in model_id.lower() or
                query_lower in meta["name"].lower() or
                query_lower in meta["provider_org"].lower()):
                model = self._create_model(model_id, meta)
                results.append(model)

        # Sort by relevance
        results.sort(key=lambda m: m.match_score(query, filters), reverse=True)

        return results[offset:offset + limit]

    async def get_model(self, model_id: str) -> Optional[UnifiedModel]:
        """Get details for a specific GitHub model."""
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
        """List all GitHub Models."""
        results = []

        for model_id, meta in self.KNOWN_MODELS.items():
            model = self._create_model(model_id, meta)

            # Filter by category
            if category:
                caps = [c.value for c in model.capabilities]
                if category.lower() not in caps:
                    continue

            results.append(model)

        return results[offset:offset + limit]

    async def health_check(self) -> bool:
        """Check if GitHub API is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/zen",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False

    def _create_model(self, model_id: str, meta: Dict[str, Any]) -> UnifiedModel:
        """Create UnifiedModel from GitHub model info."""
        cap_map = {
            "chat": ModelCapability.CHAT,
            "code": ModelCapability.CODE_GENERATION,
            "vision": ModelCapability.VISION_LANGUAGE,
            "reasoning": ModelCapability.REASONING,
            "math": ModelCapability.MATH,
            "tool-use": ModelCapability.TOOL_USE,
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
            description=f"GitHub Models: {meta['name']} by {meta['provider_org']}",
            tags=[model_id, meta["provider_org"], "github", "api"],
            commercial_use=True,
            metrics=ModelMetrics(
                context_length=meta.get("context"),
            ),
            pull_command=f"# Use GitHub Models API\ncurl -X POST https://models.inference.ai.azure.com/chat/completions -H 'Authorization: Bearer $GITHUB_TOKEN'",
            pull_runtime="github-models",
        )


# Register provider
registry.register(GitHubModelsProvider())
