import os
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

import requests


class BaseChatClient(ABC):
    """Minimal interface for chat model backends."""

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send chat messages and return the model response."""


class OllamaChat(BaseChatClient):
    def __init__(self, endpoint: str, model: str):
        self.endpoint = endpoint
        self.model = model

    def chat(self, messages: List[Dict[str, str]]) -> str:
        # ZERO-KEEP-ALIVE PROTOCOL (Pass the Ball)
        # 0 = Unload immediately after response
        keep_alive = os.getenv("OLLAMA_KEEP_ALIVE", "0")
        
        payload = {
            "model": self.model,
            "messages": messages,
            "keep_alive": keep_alive,
        }
        r = requests.post(self.endpoint, json=payload, timeout=300) # Increased for loading time
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict):
            return data.get("message", {}).get("content", "")
        return ""


class OpenAIChat(BaseChatClient):
    def __init__(self, endpoint: str, model: str, api_key: str | None = None):
        self.endpoint = endpoint or "https://api.openai.com/v1/chat/completions"
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

    def chat(self, messages: List[Dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "messages": messages}
        r = requests.post(self.endpoint, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")


class CustomChat(BaseChatClient):
    """Client for custom OpenAI-compatible endpoints (e.g. vLLM, LM Studio, LocalAI).
    
    Does not enforce API key presence, allowing for local servers that don't require auth.
    """
    def __init__(self, endpoint: str, model: str, api_key: str = "dummy"):
        self.endpoint = endpoint
        self.model = model
        self.api_key = api_key or "dummy"

    def chat(self, messages: List[Dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "messages": messages}
        # Increase timeout for local inference
        r = requests.post(self.endpoint, headers=headers, json=payload, timeout=300)
        r.raise_for_status()
        data = r.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")


class AnthropicChat(BaseChatClient):
    """Minimal Anthropic Messages API client.

    Uses the Messages API with non-streaming responses.
    Expects env var `ANTHROPIC_API_KEY` if api_key is not provided.
    Endpoint defaults to `https://api.anthropic.com/v1/messages`.
    """

    def __init__(
        self,
        model: str,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: str = "2023-06-01",
    ) -> None:
        self.endpoint = endpoint or "https://api.anthropic.com/v1/messages"
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.api_version = api_version
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")

    def chat(self, messages: List[Dict[str, str]]) -> str:
        # Convert OpenAI-style messages to Anthropic content blocks
        # Keep the last system as `system`, rest as user/assistant content blocks
        system_content = None
        converted = []
        for m in messages:
            role = m.get("role", "user")
            content = m.get("content", "")
            if role == "system":
                system_content = (system_content + "\n" if system_content else "") + content
                continue
            converted.append({"role": role, "content": [{"type": "text", "text": content}]}
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.api_version,
            "content-type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": converted,
            "max_tokens": 1024,
        }
        if system_content:
            payload["system"] = system_content

        r = requests.post(self.endpoint, headers=headers, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        # Non-streaming Messages API returns `content` as a list of blocks
        blocks = data.get("content", [])
        if blocks and isinstance(blocks, list):
            first = blocks[0]
            if isinstance(first, dict) and first.get("type") == "text":
                return first.get("text", "")
        return ""


def make_client(kind: str, endpoint: str, model: str):
    if kind == "ollama":
        return OllamaChat(endpoint, model)
    if kind == "openai":
        return OpenAIChat(endpoint, model)
    if kind == "custom":
        return CustomChat(endpoint, model)
    if kind == "anthropic":
        # Anthropic ignores the OpenAI-style endpoint; pass endpoint if overridden
        return AnthropicChat(model=model, endpoint=endpoint or None)
    raise ValueError(f"unknown model backend {kind}")