"""
SageMaker JumpStart Provider - AWS model marketplace

Amazon SageMaker JumpStart provides pre-trained models that can be
deployed to AWS infrastructure with one click.
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


class SageMakerProvider(ModelProvider):
    """Provider for AWS SageMaker JumpStart models."""

    name = "sagemaker"
    display_name = "SageMaker JumpStart"
    base_url = "https://aws.amazon.com/sagemaker/jumpstart"
    supports_pull = False  # Deployment only via AWS
    supports_search = True

    # Known SageMaker JumpStart models
    KNOWN_MODELS = {
        "meta-textgeneration-llama-3-1-405b": {
            "name": "Llama 3.1 405B",
            "params": 405,
            "caps": ["chat", "code"],
            "license": "llama-3.1",
            "instance": "ml.p4de.24xlarge",
        },
        "meta-textgeneration-llama-3-1-70b": {
            "name": "Llama 3.1 70B",
            "params": 70,
            "caps": ["chat", "code"],
            "license": "llama-3.1",
            "instance": "ml.g5.48xlarge",
        },
        "meta-textgeneration-llama-3-1-8b": {
            "name": "Llama 3.1 8B",
            "params": 8,
            "caps": ["chat", "code"],
            "license": "llama-3.1",
            "instance": "ml.g5.2xlarge",
        },
        "huggingface-llm-mistral-7b-instruct": {
            "name": "Mistral 7B Instruct",
            "params": 7,
            "caps": ["chat", "code"],
            "license": "apache-2.0",
            "instance": "ml.g5.2xlarge",
        },
        "huggingface-llm-mixtral-8x7b-instruct": {
            "name": "Mixtral 8x7B Instruct",
            "params": 47,
            "caps": ["chat", "code"],
            "license": "apache-2.0",
            "instance": "ml.g5.48xlarge",
        },
        "huggingface-text2text-flan-t5-xxl": {
            "name": "Flan T5 XXL",
            "params": 11,
            "caps": ["chat"],
            "license": "apache-2.0",
            "instance": "ml.g5.12xlarge",
        },
        "stabilityai-stable-diffusion-xl": {
            "name": "Stable Diffusion XL",
            "params": None,
            "caps": ["image"],
            "license": "openrail",
            "instance": "ml.g5.2xlarge",
        },
        "huggingface-textembedding-bge-large-en": {
            "name": "BGE Large EN",
            "params": 0.335,
            "caps": ["embed"],
            "license": "mit",
            "instance": "ml.g5.xlarge",
        },
        "amazon-titan-text-express": {
            "name": "Amazon Titan Text Express",
            "params": None,
            "caps": ["chat"],
            "license": "proprietary",
            "instance": "ml.g5.xlarge",
        },
        "amazon-titan-embed-text": {
            "name": "Amazon Titan Embed",
            "params": None,
            "caps": ["embed"],
            "license": "proprietary",
            "instance": "ml.g5.xlarge",
        },
        "anthropic-claude-3-sonnet": {
            "name": "Claude 3 Sonnet",
            "params": None,
            "caps": ["chat", "code", "reasoning"],
            "license": "proprietary",
            "instance": "ml.p4d.24xlarge",
        },
        "cohere-command-r-plus": {
            "name": "Cohere Command R+",
            "params": None,
            "caps": ["chat", "tool-use"],
            "license": "proprietary",
            "instance": "ml.p4d.24xlarge",
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
        """Search SageMaker JumpStart models."""
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
        """Get details for a specific SageMaker model."""
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
        """List SageMaker JumpStart models."""
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
        """SageMaker is always available (via AWS)."""
        return True

    def _create_model(self, model_id: str, meta: Dict[str, Any]) -> UnifiedModel:
        """Create UnifiedModel from SageMaker model info."""
        cap_map = {
            "chat": ModelCapability.CHAT,
            "code": ModelCapability.CODE_GENERATION,
            "reasoning": ModelCapability.REASONING,
            "image": ModelCapability.IMAGE_GENERATION,
            "embed": ModelCapability.EMBEDDING,
            "tool-use": ModelCapability.TOOL_USE,
        }

        capabilities = [
            cap_map[c] for c in meta.get("caps", ["chat"]) if c in cap_map
        ]

        return UnifiedModel(
            id=model_id,
            name=meta["name"],
            provider=self.name,
            provider_url=self.base_url,
            capabilities=capabilities,
            architecture="transformer",
            parameter_count=meta.get("params"),
            license=self._infer_license(meta.get("license", "")),
            commercial_use=True,  # All SageMaker models can be used commercially
            description=f"AWS SageMaker JumpStart: {meta['name']}. Deploy on {meta.get('instance', 'AWS')}",
            tags=["sagemaker", "aws", "cloud", "managed"],
            pull_command=f"# Deploy via AWS Console or SageMaker SDK\nimport sagemaker\nmodel = sagemaker.JumpStartModel(model_id='{model_id}')\npredictor = model.deploy()",
            pull_runtime="sagemaker",
        )


# Register provider
registry.register(SageMakerProvider())
