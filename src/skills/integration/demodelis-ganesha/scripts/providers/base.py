"""
Base Provider Interface and Unified Model Schema

Defines the common interface for all model providers and the normalized
model representation for cross-platform comparison.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
import hashlib


class ModelCapability(str, Enum):
    """What a model can do."""
    TEXT_GENERATION = "text-generation"
    CODE_GENERATION = "code-generation"
    CHAT = "chat"
    COMPLETION = "completion"
    EMBEDDING = "embedding"
    IMAGE_GENERATION = "image-generation"
    IMAGE_TO_IMAGE = "image-to-image"
    INPAINTING = "inpainting"
    IMAGE_CLASSIFICATION = "image-classification"
    OBJECT_DETECTION = "object-detection"
    VISION_LANGUAGE = "vision-language"
    SPEECH_TO_TEXT = "speech-to-text"
    TEXT_TO_SPEECH = "text-to-speech"
    AUDIO_GENERATION = "audio-generation"
    VIDEO_GENERATION = "video-generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question-answering"
    REASONING = "reasoning"
    MATH = "math"
    TOOL_USE = "tool-use"
    AGENT = "agent"
    MULTIMODAL = "multimodal"


class ModelLicense(str, Enum):
    """Common license types."""
    APACHE_2 = "apache-2.0"
    MIT = "mit"
    LLAMA = "llama"
    LLAMA_3 = "llama-3"
    LLAMA_3_1 = "llama-3.1"
    GEMMA = "gemma"
    QWEN = "qwen"
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"
    CC_BY_NC = "cc-by-nc-4.0"
    CC_BY_SA = "cc-by-sa-4.0"
    CC_BY = "cc-by-4.0"
    OPENRAIL = "openrail"
    CREATIVEML = "creativeml-openrail-m"
    PROPRIETARY = "proprietary"
    COMMERCIAL = "commercial"
    RESEARCH_ONLY = "research-only"
    OTHER = "other"
    UNKNOWN = "unknown"


class QuantizationType(str, Enum):
    """Quantization formats."""
    NONE = "none"
    INT8 = "int8"
    INT4 = "int4"
    FP16 = "fp16"
    BF16 = "bf16"
    FP8 = "fp8"
    GGUF_Q4_0 = "q4_0"
    GGUF_Q4_1 = "q4_1"
    GGUF_Q4_K_M = "q4_k_m"
    GGUF_Q4_K_S = "q4_k_s"
    GGUF_Q5_0 = "q5_0"
    GGUF_Q5_1 = "q5_1"
    GGUF_Q5_K_M = "q5_k_m"
    GGUF_Q5_K_S = "q5_k_s"
    GGUF_Q6_K = "q6_k"
    GGUF_Q8_0 = "q8_0"
    AWQ = "awq"
    GPTQ = "gptq"
    EXLLAMA = "exllama"
    GGML = "ggml"


@dataclass
class ModelMetrics:
    """Performance and quality metrics."""
    # Benchmarks
    mmlu_score: Optional[float] = None
    hellaswag_score: Optional[float] = None
    humaneval_score: Optional[float] = None
    gsm8k_score: Optional[float] = None
    arc_score: Optional[float] = None
    truthfulqa_score: Optional[float] = None
    winogrande_score: Optional[float] = None

    # Performance
    tokens_per_second: Optional[float] = None
    context_length: Optional[int] = None
    memory_required_gb: Optional[float] = None

    # Popularity
    downloads: Optional[int] = None
    likes: Optional[int] = None
    stars: Optional[int] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class UnifiedModel:
    """
    Normalized model representation across all providers.
    This is the common schema that enables cross-platform search.
    """
    # Identity
    id: str                              # Provider-specific ID
    name: str                            # Human-readable name
    provider: str                        # Provider name (ollama, huggingface, etc.)
    provider_url: str                    # Direct link to model page

    # Classification
    capabilities: List[ModelCapability] = field(default_factory=list)
    architecture: Optional[str] = None   # transformer, diffusion, etc.
    base_model: Optional[str] = None     # What it's fine-tuned from

    # Size & Format
    parameter_count: Optional[int] = None       # In billions (e.g., 7 for 7B)
    parameter_count_raw: Optional[int] = None   # Exact count
    file_size_bytes: Optional[int] = None
    file_size_gb: Optional[float] = None
    quantization: QuantizationType = QuantizationType.NONE
    format: Optional[str] = None         # gguf, safetensors, pytorch, etc.

    # Licensing
    license: ModelLicense = ModelLicense.UNKNOWN
    license_url: Optional[str] = None
    commercial_use: bool = False

    # Content
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)

    # Metrics
    metrics: ModelMetrics = field(default_factory=ModelMetrics)

    # Pull instructions
    pull_command: Optional[str] = None   # e.g., "ollama pull llama3:8b"
    pull_url: Optional[str] = None       # Direct download URL
    pull_runtime: Optional[str] = None   # ollama, lmstudio, etc.

    # Variants (other quantizations/sizes of same model)
    variants: List[str] = field(default_factory=list)

    # Raw provider data (for debugging)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    @property
    def unique_id(self) -> str:
        """Generate a unique ID across all providers."""
        return f"{self.provider}:{self.id}"

    @property
    def size_category(self) -> str:
        """Categorize model size."""
        if self.parameter_count is None:
            return "unknown"
        if self.parameter_count < 1:
            return "tiny"      # < 1B
        if self.parameter_count < 3:
            return "small"     # 1-3B
        if self.parameter_count < 8:
            return "medium"    # 3-8B
        if self.parameter_count < 15:
            return "large"     # 8-15B
        if self.parameter_count < 40:
            return "xlarge"    # 15-40B
        return "xxlarge"       # 40B+

    @property
    def search_text(self) -> str:
        """Text blob for full-text search."""
        parts = [
            self.name,
            self.description or "",
            self.architecture or "",
            self.base_model or "",
            " ".join(self.tags),
            " ".join([c.value for c in self.capabilities]),
        ]
        return " ".join(parts).lower()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "unique_id": self.unique_id,
            "name": self.name,
            "provider": self.provider,
            "provider_url": self.provider_url,
            "capabilities": [c.value for c in self.capabilities],
            "architecture": self.architecture,
            "base_model": self.base_model,
            "parameter_count": self.parameter_count,
            "file_size_gb": self.file_size_gb,
            "quantization": self.quantization.value if self.quantization else None,
            "format": self.format,
            "license": self.license.value if self.license else None,
            "commercial_use": self.commercial_use,
            "description": self.description,
            "tags": self.tags,
            "languages": self.languages,
            "metrics": {
                "downloads": self.metrics.downloads,
                "likes": self.metrics.likes,
                "context_length": self.metrics.context_length,
                "tokens_per_second": self.metrics.tokens_per_second,
            },
            "pull_command": self.pull_command,
            "pull_runtime": self.pull_runtime,
            "size_category": self.size_category,
        }

    def match_score(self, query: str, filters: Dict[str, Any] = None) -> float:
        """
        Calculate relevance score for a search query.
        Returns 0.0-1.0 score.
        """
        score = 0.0
        query_lower = query.lower()
        query_terms = query_lower.split()

        # Exact name match (highest weight)
        if query_lower == self.name.lower():
            score += 1.0
        elif query_lower in self.name.lower():
            score += 0.7

        # Term matching in search text
        search_text = self.search_text
        matches = sum(1 for term in query_terms if term in search_text)
        score += (matches / max(len(query_terms), 1)) * 0.5

        # Capability matching
        for term in query_terms:
            for cap in self.capabilities:
                if term in cap.value:
                    score += 0.2
                    break

        # Tag matching
        for term in query_terms:
            if any(term in tag.lower() for tag in self.tags):
                score += 0.15

        # Apply filters
        if filters:
            # Size filter
            if "max_params" in filters and self.parameter_count:
                if self.parameter_count > filters["max_params"]:
                    return 0.0  # Exclude
            if "min_params" in filters and self.parameter_count:
                if self.parameter_count < filters["min_params"]:
                    return 0.0

            # Capability filter
            if "capabilities" in filters:
                required = set(filters["capabilities"])
                have = set(c.value for c in self.capabilities)
                if not required.intersection(have):
                    return 0.0

            # License filter
            if "commercial_only" in filters and filters["commercial_only"]:
                if not self.commercial_use:
                    return 0.0

            # Quantization filter
            if "quantization" in filters:
                if self.quantization.value not in filters["quantization"]:
                    return 0.0

        # Popularity boost
        if self.metrics.downloads:
            if self.metrics.downloads > 1000000:
                score += 0.2
            elif self.metrics.downloads > 100000:
                score += 0.1
            elif self.metrics.downloads > 10000:
                score += 0.05

        return min(score, 1.0)


class ModelProvider(ABC):
    """
    Abstract base class for model providers.
    Each provider implements search, list, and pull operations.
    """

    name: str = "base"
    display_name: str = "Base Provider"
    base_url: str = ""
    supports_pull: bool = False
    supports_search: bool = True
    rate_limit_rpm: int = 60

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        self._cache: Dict[str, Any] = {}

    @abstractmethod
    async def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """
        Search for models matching query.
        Returns list of UnifiedModel objects.
        """
        pass

    @abstractmethod
    async def get_model(self, model_id: str) -> Optional[UnifiedModel]:
        """Get details for a specific model."""
        pass

    @abstractmethod
    async def list_models(
        self,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[UnifiedModel]:
        """List available models, optionally filtered by category."""
        pass

    async def pull(self, model_id: str, **kwargs) -> Dict[str, Any]:
        """
        Pull/download a model.
        Returns status dict with success, path, and error fields.
        """
        return {
            "success": False,
            "error": f"Pull not supported for {self.name}",
            "provider": self.name,
            "model_id": model_id,
        }

    async def health_check(self) -> bool:
        """Check if provider is available."""
        return True

    def normalize_model(self, raw_data: Dict[str, Any]) -> UnifiedModel:
        """
        Convert provider-specific model data to UnifiedModel.
        Subclasses must implement this.
        """
        raise NotImplementedError

    def _parse_parameter_count(self, text: str) -> Optional[int]:
        """Extract parameter count from text like '7B', '70b', '7 billion'."""
        import re
        text = text.lower()

        # Match patterns like "7b", "70B", "7 billion"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*b(?:illion)?',
            r'(\d+(?:\.\d+)?)\s*m(?:illion)?',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1))
                if 'million' in text or pattern.endswith("m'):"):
                    return value / 1000  # Convert M to B
                return int(value) if value == int(value) else value

        return None

    def _parse_file_size(self, text: str) -> Optional[float]:
        """Extract file size in GB from text."""
        import re
        text = text.lower()

        patterns = [
            (r'(\d+(?:\.\d+)?)\s*gb', 1),
            (r'(\d+(?:\.\d+)?)\s*mb', 0.001),
            (r'(\d+(?:\.\d+)?)\s*tb', 1000),
        ]

        for pattern, multiplier in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1)) * multiplier

        return None

    def _infer_capabilities(
        self,
        name: str,
        tags: List[str],
        description: str = "",
    ) -> List[ModelCapability]:
        """Infer model capabilities from metadata."""
        capabilities = []
        text = f"{name} {' '.join(tags)} {description}".lower()

        # Text generation
        if any(x in text for x in ["llm", "language model", "text-generation", "completion"]):
            capabilities.append(ModelCapability.TEXT_GENERATION)

        # Code
        if any(x in text for x in ["code", "coder", "coding", "programming", "starcoder", "codellama"]):
            capabilities.append(ModelCapability.CODE_GENERATION)

        # Chat
        if any(x in text for x in ["chat", "instruct", "conversation", "assistant"]):
            capabilities.append(ModelCapability.CHAT)

        # Vision
        if any(x in text for x in ["vision", "llava", "image", "visual", "multimodal"]):
            capabilities.append(ModelCapability.VISION_LANGUAGE)

        # Image generation
        if any(x in text for x in ["diffusion", "sdxl", "stable-diffusion", "dall-e", "image generation"]):
            capabilities.append(ModelCapability.IMAGE_GENERATION)

        # Embedding
        if any(x in text for x in ["embed", "embedding", "sentence-transformer"]):
            capabilities.append(ModelCapability.EMBEDDING)

        # Reasoning
        if any(x in text for x in ["reason", "thinking", "o1", "r1", "math", "chain-of-thought"]):
            capabilities.append(ModelCapability.REASONING)

        # Math
        if any(x in text for x in ["math", "mathstral", "qwen-math", "deepseek-math"]):
            capabilities.append(ModelCapability.MATH)

        # Speech
        if any(x in text for x in ["whisper", "speech", "asr", "stt"]):
            capabilities.append(ModelCapability.SPEECH_TO_TEXT)
        if any(x in text for x in ["tts", "text-to-speech", "bark", "xtts"]):
            capabilities.append(ModelCapability.TEXT_TO_SPEECH)

        # Default to text generation for LLMs
        if not capabilities:
            capabilities.append(ModelCapability.TEXT_GENERATION)

        return capabilities

    def _infer_license(self, license_str: str) -> ModelLicense:
        """Map license string to ModelLicense enum."""
        if not license_str:
            return ModelLicense.UNKNOWN

        license_lower = license_str.lower()

        mappings = {
            "apache": ModelLicense.APACHE_2,
            "mit": ModelLicense.MIT,
            "llama3": ModelLicense.LLAMA_3,
            "llama-3": ModelLicense.LLAMA_3,
            "llama 3": ModelLicense.LLAMA_3,
            "llama2": ModelLicense.LLAMA,
            "gemma": ModelLicense.GEMMA,
            "qwen": ModelLicense.QWEN,
            "deepseek": ModelLicense.DEEPSEEK,
            "mistral": ModelLicense.MISTRAL,
            "cc-by-nc": ModelLicense.CC_BY_NC,
            "cc-by-sa": ModelLicense.CC_BY_SA,
            "cc-by": ModelLicense.CC_BY,
            "openrail": ModelLicense.OPENRAIL,
            "creativeml": ModelLicense.CREATIVEML,
        }

        for key, value in mappings.items():
            if key in license_lower:
                return value

        return ModelLicense.OTHER


class ProviderRegistry:
    """Registry of all available model providers."""

    _instance: Optional["ProviderRegistry"] = None
    _providers: Dict[str, ModelProvider] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, provider: ModelProvider) -> None:
        """Register a provider."""
        self._providers[provider.name] = provider

    def get(self, name: str) -> Optional[ModelProvider]:
        """Get a provider by name."""
        return self._providers.get(name)

    def list(self) -> List[str]:
        """List all registered provider names."""
        return list(self._providers.keys())

    def all(self) -> Dict[str, ModelProvider]:
        """Get all providers."""
        return self._providers.copy()

    async def search_all(
        self,
        query: str,
        providers: List[str] = None,
        filters: Dict[str, Any] = None,
        limit: int = 50,
    ) -> List[UnifiedModel]:
        """
        Search across all (or specified) providers.
        Returns merged, deduplicated, ranked results.
        """
        import asyncio

        target_providers = providers or self.list()
        tasks = []

        for name in target_providers:
            provider = self.get(name)
            if provider and provider.supports_search:
                tasks.append(provider.search(query, filters, limit=limit))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Flatten and deduplicate
        all_models = []
        seen = set()

        for result in results:
            if isinstance(result, Exception):
                continue
            for model in result:
                if model.unique_id not in seen:
                    seen.add(model.unique_id)
                    all_models.append(model)

        # Re-rank by match score
        all_models.sort(key=lambda m: m.match_score(query, filters), reverse=True)

        return all_models[:limit]


# Global registry instance
registry = ProviderRegistry()
