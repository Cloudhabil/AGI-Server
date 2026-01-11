"""
HuggingFace Provider - Largest model repository

HuggingFace Hub hosts hundreds of thousands of models across all modalities.
Supports search, filtering, and direct downloads.
"""

import os
import asyncio
import aiohttp
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import (
    ModelProvider,
    UnifiedModel,
    ModelCapability,
    ModelMetrics,
    ModelLicense,
    QuantizationType,
    registry,
)


class HuggingFaceProvider(ModelProvider):
    """Provider for HuggingFace Hub."""

    name = "huggingface"
    display_name = "Hugging Face"
    base_url = "https://huggingface.co"
    api_url = "https://huggingface.co/api"
    supports_pull = True
    supports_search = True
    rate_limit_rpm = 100

    # Task to capability mapping
    TASK_MAP = {
        "text-generation": ModelCapability.TEXT_GENERATION,
        "text2text-generation": ModelCapability.TEXT_GENERATION,
        "conversational": ModelCapability.CHAT,
        "feature-extraction": ModelCapability.EMBEDDING,
        "sentence-similarity": ModelCapability.EMBEDDING,
        "fill-mask": ModelCapability.TEXT_GENERATION,
        "question-answering": ModelCapability.QUESTION_ANSWERING,
        "summarization": ModelCapability.SUMMARIZATION,
        "translation": ModelCapability.TRANSLATION,
        "text-classification": ModelCapability.TEXT_GENERATION,
        "token-classification": ModelCapability.TEXT_GENERATION,
        "image-classification": ModelCapability.IMAGE_CLASSIFICATION,
        "object-detection": ModelCapability.OBJECT_DETECTION,
        "image-segmentation": ModelCapability.OBJECT_DETECTION,
        "text-to-image": ModelCapability.IMAGE_GENERATION,
        "image-to-image": ModelCapability.IMAGE_TO_IMAGE,
        "image-to-text": ModelCapability.VISION_LANGUAGE,
        "visual-question-answering": ModelCapability.VISION_LANGUAGE,
        "automatic-speech-recognition": ModelCapability.SPEECH_TO_TEXT,
        "text-to-speech": ModelCapability.TEXT_TO_SPEECH,
        "audio-classification": ModelCapability.SPEECH_TO_TEXT,
        "text-to-video": ModelCapability.VIDEO_GENERATION,
        "video-classification": ModelCapability.VIDEO_GENERATION,
        "zero-shot-classification": ModelCapability.TEXT_GENERATION,
        "zero-shot-image-classification": ModelCapability.IMAGE_CLASSIFICATION,
        "depth-estimation": ModelCapability.OBJECT_DETECTION,
        "image-feature-extraction": ModelCapability.EMBEDDING,
    }

    def __init__(self, api_key: str = None, **kwargs):
        super().__init__(api_key=api_key, **kwargs)
        self.api_key = api_key or os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")

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
        """Search HuggingFace models."""
        params = {
            "search": query,
            "limit": min(limit, 100),
            "full": "true",
            "config": "true",
        }

        # Apply filters
        if filters:
            if "task" in filters:
                params["pipeline_tag"] = filters["task"]
            if "library" in filters:
                params["library"] = filters["library"]
            if "language" in filters:
                params["language"] = filters["language"]

        # Sort by downloads for relevance
        params["sort"] = "downloads"
        params["direction"] = "-1"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models",
                    params=params,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [self._normalize_model(m) for m in data]
        except Exception as e:
            print(f"[HuggingFace] Search error: {e}")

        return []

    async def get_model(self, model_id: str) -> Optional[UnifiedModel]:
        """Get details for a specific model."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models/{model_id}",
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._normalize_model(data)
        except Exception as e:
            print(f"[HuggingFace] Get model error: {e}")

        return None

    async def list_models(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """List HuggingFace models by category."""
        params = {
            "limit": min(limit, 100),
            "full": "true",
            "sort": "downloads",
            "direction": "-1",
        }

        if category:
            # Map category to pipeline_tag
            category_map = {
                "text-generation": "text-generation",
                "chat": "conversational",
                "code": "text-generation",
                "embedding": "feature-extraction",
                "image": "text-to-image",
                "vision": "image-to-text",
                "speech": "automatic-speech-recognition",
            }
            params["pipeline_tag"] = category_map.get(category, category)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models",
                    params=params,
                    headers=self._get_headers(),
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return [self._normalize_model(m) for m in data]
        except Exception as e:
            print(f"[HuggingFace] List error: {e}")

        return []

    async def pull(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """Generate pull instructions for HuggingFace model."""
        # HF models are typically pulled via transformers or huggingface_hub
        return {
            "success": True,
            "provider": self.name,
            "model_id": model_id,
            "pull_command": f"huggingface-cli download {model_id}",
            "python_code": f'from transformers import AutoModel\nmodel = AutoModel.from_pretrained("{model_id}")',
            "message": f"Use huggingface-cli or transformers to download {model_id}",
        }

    async def health_check(self) -> bool:
        """Check if HuggingFace API is available."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/models?limit=1",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False

    def _normalize_model(self, data: Dict[str, Any]) -> UnifiedModel:
        """Convert HuggingFace API response to UnifiedModel."""
        model_id = data.get("modelId", data.get("id", ""))

        # Extract pipeline tag / task
        pipeline_tag = data.get("pipeline_tag", "")
        capabilities = []
        if pipeline_tag and pipeline_tag in self.TASK_MAP:
            capabilities.append(self.TASK_MAP[pipeline_tag])

        # Infer additional capabilities from tags
        tags = data.get("tags", [])
        for tag in tags:
            if tag in self.TASK_MAP and self.TASK_MAP[tag] not in capabilities:
                capabilities.append(self.TASK_MAP[tag])

        # Infer from model name/id
        name_lower = model_id.lower()
        if "chat" in name_lower or "instruct" in name_lower:
            if ModelCapability.CHAT not in capabilities:
                capabilities.append(ModelCapability.CHAT)
        if "code" in name_lower or "coder" in name_lower:
            if ModelCapability.CODE_GENERATION not in capabilities:
                capabilities.append(ModelCapability.CODE_GENERATION)
        if "embed" in name_lower:
            if ModelCapability.EMBEDDING not in capabilities:
                capabilities.append(ModelCapability.EMBEDDING)

        # Default to text generation
        if not capabilities:
            capabilities.append(ModelCapability.TEXT_GENERATION)

        # Parse parameters from safetensors info or model card
        safetensors = data.get("safetensors", {})
        param_count = None
        if safetensors:
            total = safetensors.get("total", 0)
            if total > 0:
                param_count = total / 1_000_000_000  # Convert to billions

        # If not in safetensors, try to parse from name
        if param_count is None:
            param_count = self._parse_parameter_count(model_id)

        # Parse license
        license_str = data.get("license", "") or ""
        license_type = self._infer_license(license_str)

        # Commercial use heuristic
        commercial = license_type in [
            ModelLicense.APACHE_2,
            ModelLicense.MIT,
            ModelLicense.CC_BY,
        ]

        # Quantization detection
        quant = QuantizationType.NONE
        for tag in tags:
            tag_lower = tag.lower()
            if "gguf" in tag_lower:
                quant = QuantizationType.GGUF_Q4_K_M
            elif "gptq" in tag_lower:
                quant = QuantizationType.GPTQ
            elif "awq" in tag_lower:
                quant = QuantizationType.AWQ
            elif "int8" in tag_lower:
                quant = QuantizationType.INT8
            elif "int4" in tag_lower:
                quant = QuantizationType.INT4

        # Format detection
        model_format = "safetensors" if safetensors else "pytorch"
        if any("gguf" in t.lower() for t in tags):
            model_format = "gguf"

        # Metrics
        downloads = data.get("downloads", 0)
        likes = data.get("likes", 0)

        # Timestamps
        created = data.get("createdAt")
        updated = data.get("lastModified")

        return UnifiedModel(
            id=model_id,
            name=model_id.split("/")[-1],
            provider=self.name,
            provider_url=f"{self.base_url}/{model_id}",
            capabilities=capabilities,
            architecture=data.get("config", {}).get("model_type", "transformer"),
            parameter_count=param_count,
            quantization=quant,
            format=model_format,
            license=license_type,
            license_url=f"{self.base_url}/{model_id}/blob/main/LICENSE",
            commercial_use=commercial,
            description=data.get("description", "")[:500] if data.get("description") else None,
            tags=tags[:20],  # Limit tags
            languages=data.get("languages", []),
            metrics=ModelMetrics(
                downloads=downloads,
                likes=likes,
                created_at=datetime.fromisoformat(created.replace("Z", "+00:00")) if created else None,
                updated_at=datetime.fromisoformat(updated.replace("Z", "+00:00")) if updated else None,
            ),
            pull_command=f"huggingface-cli download {model_id}",
            pull_runtime="transformers",
            raw_data=data,
        )


# Register provider
registry.register(HuggingFaceProvider())
