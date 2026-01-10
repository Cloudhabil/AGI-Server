"""Pydantic models for API payloads."""

from typing import Literal, Optional, Dict, Any

from pydantic import BaseModel


class SeedBody(BaseModel):
    text: str
    meta: Optional[Dict[str, Any]] = None


NodeStatus = Literal["stopped", "starting", "running", "stopping", "error"]


class NodeConfig(BaseModel):
    system: Optional[str] = None
    temperature: Optional[float] = 0.2
    max_tokens: Optional[int] = 256
