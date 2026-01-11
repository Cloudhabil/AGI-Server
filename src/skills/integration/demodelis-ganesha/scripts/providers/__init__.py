"""
Universal Model Search - Provider Adapters

Each provider adapter normalizes model metadata into a unified schema
for cross-platform search and comparison.
"""

from .base import (
    ModelProvider,
    UnifiedModel,
    ModelCapability,
    ModelLicense,
    ProviderRegistry,
)
from .ollama import OllamaProvider
from .huggingface import HuggingFaceProvider
from .modelscope import ModelScopeProvider
from .civitai import CivitaiProvider
from .kaggle import KaggleProvider
from .replicate import ReplicateProvider
from .github_models import GitHubModelsProvider
from .mistral import MistralProvider
from .deepseek import DeepSeekProvider
from .lmstudio import LMStudioProvider
from .gpt4all import GPT4AllProvider
from .jan import JanProvider
from .sagemaker import SageMakerProvider
from .vertexai import VertexAIProvider

__all__ = [
    "ModelProvider",
    "UnifiedModel",
    "ModelCapability",
    "ModelLicense",
    "ProviderRegistry",
    "OllamaProvider",
    "HuggingFaceProvider",
    "ModelScopeProvider",
    "CivitaiProvider",
    "KaggleProvider",
    "ReplicateProvider",
    "GitHubModelsProvider",
    "MistralProvider",
    "DeepSeekProvider",
    "LMStudioProvider",
    "GPT4AllProvider",
    "JanProvider",
    "SageMakerProvider",
    "VertexAIProvider",
]
