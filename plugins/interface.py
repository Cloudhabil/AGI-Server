from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AgentPlugin(ABC):
    """Base class for all agent plug-ins.

    Plug-ins must implement :meth:`init`, :meth:`process`, and :meth:`cleanup`.
    """

    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def init(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the plug-in with optional configuration."""

    @abstractmethod
    def process(self, data: Any) -> Any:
        """Execute the main plug-in logic."""

    @abstractmethod
    def cleanup(self) -> None:
        """Release any allocated resources."""


class GeneratorPlugin(AgentPlugin, ABC):
    """Plug-in that produces new output."""

    kind = "generator"


class RefinerPlugin(AgentPlugin, ABC):
    """Plug-in that refines existing output."""

    kind = "refiner"
