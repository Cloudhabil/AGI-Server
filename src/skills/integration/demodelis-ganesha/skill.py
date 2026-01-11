"""
demodelis-ganesha Skill
=======================

Unified search engine for AI models across all major platforms.
Search, compare, rank, and pull models from 14+ providers.

Supported Providers:
- Ollama (local)
- HuggingFace
- ModelScope
- Civitai
- Kaggle
- Replicate
- GitHub Models
- Mistral AI
- DeepSeek
- LM Studio
- GPT4All
- Jan.ai
- SageMaker JumpStart
- Vertex AI Model Garden

Capabilities:
- search: Find models matching criteria
- compare: Side-by-side model comparison
- recommend: Get AI-powered model recommendations
- pull: Download/deploy models
- list: Browse models by category
- providers: List available providers
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
    SkillScale,
)

# Import providers
from .scripts.providers import (
    registry,
    UnifiedModel,
    ModelCapability,
    OllamaProvider,
    HuggingFaceProvider,
    ModelScopeProvider,
    CivitaiProvider,
    KaggleProvider,
    ReplicateProvider,
    GitHubModelsProvider,
    MistralProvider,
    DeepSeekProvider,
    LMStudioProvider,
    GPT4AllProvider,
    JanProvider,
    SageMakerProvider,
    VertexAIProvider,
)


class DemodelisGaneshaSkill(Skill):
    """
    demodelis-ganesha - Unified AI Model Search

    Search across 14+ model providers with unified ranking and comparison.
    """

    # Cache configuration
    CACHE_TTL_SECONDS = 300  # 5 minutes
    CACHE_FILE = Path(__file__).parent / "data" / "model_cache.json"

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._initialized = False

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="integration/demodelis-ganesha",
            name="demodelis-ganesha",
            description="Unified search engine for AI models across all major platforms",
            version="1.0.0",
            category=SkillCategory.INTEGRATION,
            level=SkillLevel.ADVANCED,
            scale=SkillScale.L2_MACRO,
            tags=[
                "models", "search", "discovery", "ollama", "huggingface",
                "llm", "diffusion", "multimodal", "pull", "compare",
            ],
            estimated_tokens=800,
            token_budget=150,
            author="GPIA Team",
            license="CSAL",
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {
                    "type": "string",
                    "enum": ["search", "compare", "recommend", "pull", "list", "providers", "health"],
                    "description": "The operation to perform",
                },
                # Search parameters
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'code generation model under 8B')",
                },
                "providers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Limit search to specific providers",
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Maximum results to return",
                },
                # Filter parameters
                "max_params": {
                    "type": "number",
                    "description": "Maximum parameter count (in billions)",
                },
                "min_params": {
                    "type": "number",
                    "description": "Minimum parameter count (in billions)",
                },
                "capabilities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Required capabilities (e.g., ['code', 'chat'])",
                },
                "commercial_only": {
                    "type": "boolean",
                    "default": False,
                    "description": "Only show commercially licensable models",
                },
                "local_only": {
                    "type": "boolean",
                    "default": False,
                    "description": "Only show models that can run locally",
                },
                # Compare parameters
                "models": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "provider": {"type": "string"},
                            "id": {"type": "string"},
                        },
                    },
                    "description": "Models to compare",
                },
                # Pull parameters
                "provider": {
                    "type": "string",
                    "description": "Provider name for pull operation",
                },
                "model_id": {
                    "type": "string",
                    "description": "Model ID to pull",
                },
                # List parameters
                "category": {
                    "type": "string",
                    "description": "Category to list (e.g., 'text-generation', 'code')",
                },
            },
            "required": ["capability"],
        }

    def output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "models": {
                    "type": "array",
                    "description": "List of matching models",
                },
                "comparison": {
                    "type": "object",
                    "description": "Model comparison results",
                },
                "recommendation": {
                    "type": "object",
                    "description": "AI-powered recommendation",
                },
                "pull_result": {
                    "type": "object",
                    "description": "Pull operation result",
                },
                "providers": {
                    "type": "array",
                    "description": "Available providers",
                },
                "health": {
                    "type": "object",
                    "description": "Provider health status",
                },
            },
        }

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the skill and register all providers."""
        if self._initialized:
            return

        # Ensure all providers are registered
        # (They auto-register on import, but we verify here)
        providers = [
            OllamaProvider,
            HuggingFaceProvider,
            ModelScopeProvider,
            CivitaiProvider,
            KaggleProvider,
            ReplicateProvider,
            GitHubModelsProvider,
            MistralProvider,
            DeepSeekProvider,
            LMStudioProvider,
            GPT4AllProvider,
            JanProvider,
            SageMakerProvider,
            VertexAIProvider,
        ]

        for provider_cls in providers:
            try:
                if provider_cls.name not in registry.list():
                    registry.register(provider_cls())
            except Exception:
                pass

        # Load cache from disk
        self._load_cache()

        self._initialized = True

    def execute(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> SkillResult:
        """Execute the skill based on capability."""
        self.initialize()

        capability = input_data.get("capability", "search")

        try:
            # Run async operation
            result = asyncio.run(self._execute_async(capability, input_data, context))
            return SkillResult(
                success=True,
                output=result,
                skill_id=self.metadata().id,
            )
        except Exception as e:
            return SkillResult(
                success=False,
                output=None,
                error=str(e),
                error_code="EXECUTION_ERROR",
                skill_id=self.metadata().id,
            )

    async def _execute_async(
        self,
        capability: str,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> Dict[str, Any]:
        """Async execution dispatcher."""
        handlers = {
            "search": self._handle_search,
            "compare": self._handle_compare,
            "recommend": self._handle_recommend,
            "pull": self._handle_pull,
            "list": self._handle_list,
            "providers": self._handle_providers,
            "health": self._handle_health,
        }

        handler = handlers.get(capability)
        if not handler:
            raise ValueError(f"Unknown capability: {capability}")

        return await handler(input_data, context)

    async def _handle_search(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> Dict[str, Any]:
        """Search for models across providers."""
        query = input_data.get("query", "")
        providers = input_data.get("providers")
        limit = input_data.get("limit", 20)

        # Build filters
        filters = {}
        if input_data.get("max_params"):
            filters["max_params"] = input_data["max_params"]
        if input_data.get("min_params"):
            filters["min_params"] = input_data["min_params"]
        if input_data.get("capabilities"):
            filters["capabilities"] = input_data["capabilities"]
        if input_data.get("commercial_only"):
            filters["commercial_only"] = True

        # Check cache
        cache_key = f"search:{query}:{json.dumps(providers or [])}:{json.dumps(filters)}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        # Determine which providers to search
        if input_data.get("local_only"):
            providers = ["ollama", "lmstudio", "gpt4all", "jan"]

        # Search across providers
        models = await registry.search_all(
            query=query,
            providers=providers,
            filters=filters,
            limit=limit,
        )

        result = {
            "query": query,
            "total": len(models),
            "models": [m.to_dict() for m in models],
            "filters_applied": filters,
            "providers_searched": providers or registry.list(),
        }

        # Cache result
        self._set_cached(cache_key, result)

        return result

    async def _handle_compare(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> Dict[str, Any]:
        """Compare multiple models side by side."""
        models_to_compare = input_data.get("models", [])

        if len(models_to_compare) < 2:
            raise ValueError("Need at least 2 models to compare")

        # Fetch model details
        fetched_models = []
        for model_spec in models_to_compare:
            provider_name = model_spec.get("provider")
            model_id = model_spec.get("id")

            provider = registry.get(provider_name)
            if provider:
                model = await provider.get_model(model_id)
                if model:
                    fetched_models.append(model)

        if len(fetched_models) < 2:
            raise ValueError("Could not fetch enough models for comparison")

        # Build comparison matrix
        comparison = {
            "models": [m.to_dict() for m in fetched_models],
            "comparison_matrix": self._build_comparison_matrix(fetched_models),
            "recommendation": self._generate_comparison_recommendation(fetched_models),
        }

        return comparison

    def _build_comparison_matrix(self, models: List[UnifiedModel]) -> Dict[str, Any]:
        """Build a comparison matrix for models."""
        matrix = {
            "parameters": {},
            "capabilities": {},
            "licenses": {},
            "size": {},
            "popularity": {},
        }

        for model in models:
            key = model.unique_id

            matrix["parameters"][key] = model.parameter_count
            matrix["capabilities"][key] = [c.value for c in model.capabilities]
            matrix["licenses"][key] = model.license.value if model.license else "unknown"
            matrix["size"][key] = model.file_size_gb
            matrix["popularity"][key] = model.metrics.downloads

        return matrix

    def _generate_comparison_recommendation(
        self,
        models: List[UnifiedModel],
    ) -> Dict[str, Any]:
        """Generate a recommendation from compared models."""
        # Score each model
        scores = {}
        for model in models:
            score = 0

            # Smaller is better for local deployment
            if model.parameter_count and model.parameter_count <= 8:
                score += 2
            elif model.parameter_count and model.parameter_count <= 13:
                score += 1

            # More capabilities is better
            score += len(model.capabilities) * 0.5

            # Commercial use is valuable
            if model.commercial_use:
                score += 1

            # Popularity boost
            if model.metrics.downloads and model.metrics.downloads > 100000:
                score += 1

            scores[model.unique_id] = score

        # Find winner
        winner = max(scores, key=scores.get)
        winner_model = next(m for m in models if m.unique_id == winner)

        return {
            "winner": winner,
            "winner_name": winner_model.name,
            "scores": scores,
            "reason": self._explain_recommendation(winner_model, models),
        }

    def _explain_recommendation(
        self,
        winner: UnifiedModel,
        all_models: List[UnifiedModel],
    ) -> str:
        """Explain why a model was recommended."""
        reasons = []

        if winner.parameter_count and winner.parameter_count <= 8:
            reasons.append("optimal size for local deployment")
        if winner.commercial_use:
            reasons.append("commercially licensable")
        if len(winner.capabilities) > 1:
            reasons.append(f"versatile ({len(winner.capabilities)} capabilities)")
        if winner.metrics.downloads and winner.metrics.downloads > 100000:
            reasons.append("popular and well-tested")

        return f"{winner.name} wins because: {', '.join(reasons) or 'best overall score'}"

    async def _handle_recommend(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> Dict[str, Any]:
        """Get AI-powered model recommendations."""
        query = input_data.get("query", "")
        use_case = input_data.get("use_case", query)

        # First, search for relevant models
        search_result = await self._handle_search(
            {"query": query, "limit": 10, **input_data},
            context,
        )

        models = search_result.get("models", [])
        if not models:
            return {
                "recommendation": None,
                "reason": "No models found matching your criteria",
            }

        # Analyze and recommend
        top_model = models[0]
        alternatives = models[1:4]

        return {
            "recommendation": top_model,
            "alternatives": alternatives,
            "use_case": use_case,
            "reason": f"Recommended {top_model['name']} based on: high relevance to '{query}', "
                     f"{top_model.get('size_category', 'medium')} size, "
                     f"available via {top_model['provider']}",
            "pull_command": top_model.get("pull_command"),
        }

    async def _handle_pull(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> Dict[str, Any]:
        """Pull/download a model."""
        provider_name = input_data.get("provider")
        model_id = input_data.get("model_id")

        if not provider_name or not model_id:
            raise ValueError("Both 'provider' and 'model_id' are required for pull")

        provider = registry.get(provider_name)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_name}")

        if not provider.supports_pull:
            return {
                "success": False,
                "error": f"Provider {provider_name} does not support direct pulls",
                "suggestion": "Use the provider's native tools or web interface",
            }

        result = await provider.pull(model_id)
        return result

    async def _handle_list(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> Dict[str, Any]:
        """List models by category."""
        category = input_data.get("category")
        providers = input_data.get("providers")
        limit = input_data.get("limit", 50)

        all_models = []

        target_providers = providers or registry.list()
        for provider_name in target_providers:
            provider = registry.get(provider_name)
            if provider:
                try:
                    models = await provider.list_models(
                        category=category,
                        limit=limit // len(target_providers),
                    )
                    all_models.extend(models)
                except Exception:
                    pass

        # Sort by popularity
        all_models.sort(
            key=lambda m: m.metrics.downloads or 0,
            reverse=True,
        )

        return {
            "category": category,
            "total": len(all_models),
            "models": [m.to_dict() for m in all_models[:limit]],
        }

    async def _handle_providers(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> Dict[str, Any]:
        """List available providers and their capabilities."""
        providers_info = []

        for name in registry.list():
            provider = registry.get(name)
            if provider:
                providers_info.append({
                    "name": provider.name,
                    "display_name": provider.display_name,
                    "base_url": provider.base_url,
                    "supports_pull": provider.supports_pull,
                    "supports_search": provider.supports_search,
                })

        return {
            "total": len(providers_info),
            "providers": providers_info,
        }

    async def _handle_health(
        self,
        input_data: Dict[str, Any],
        context: SkillContext,
    ) -> Dict[str, Any]:
        """Check health of all providers."""
        health_status = {}

        for name in registry.list():
            provider = registry.get(name)
            if provider:
                try:
                    is_healthy = await provider.health_check()
                    health_status[name] = {
                        "status": "healthy" if is_healthy else "unavailable",
                        "checked_at": datetime.now().isoformat(),
                    }
                except Exception as e:
                    health_status[name] = {
                        "status": "error",
                        "error": str(e),
                        "checked_at": datetime.now().isoformat(),
                    }

        return {
            "health": health_status,
            "healthy_count": sum(1 for h in health_status.values() if h["status"] == "healthy"),
            "total_providers": len(health_status),
        }

    # Cache helpers
    def _get_cached(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached value if not expired."""
        if key in self._cache:
            timestamp = self._cache_timestamps.get(key, 0)
            if time.time() - timestamp < self.CACHE_TTL_SECONDS:
                return self._cache[key]
        return None

    def _set_cached(self, key: str, value: Dict[str, Any]) -> None:
        """Set cached value with timestamp."""
        self._cache[key] = value
        self._cache_timestamps[key] = time.time()

        # Persist to disk periodically
        if len(self._cache) % 10 == 0:
            self._save_cache()

    def _load_cache(self) -> None:
        """Load cache from disk."""
        try:
            if self.CACHE_FILE.exists():
                with open(self.CACHE_FILE) as f:
                    data = json.load(f)
                    self._cache = data.get("cache", {})
                    self._cache_timestamps = data.get("timestamps", {})
        except Exception:
            pass

    def _save_cache(self) -> None:
        """Save cache to disk."""
        try:
            self.CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.CACHE_FILE, "w") as f:
                json.dump({
                    "cache": self._cache,
                    "timestamps": self._cache_timestamps,
                }, f)
        except Exception:
            pass


# Export skill class
__all__ = ["DemodelisGaneshaSkill"]
