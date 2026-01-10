from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from core.agents.base import AgentContext
from core.runtime.capsule_types import Capsule, CapsuleResult


class CapsuleEngine(ABC):
    """
    Stable façade for capsule execution. Modes should depend on this contract,
    not on legacy gpia imports.
    """

    name: str = "base"

    @abstractmethod
    def execute(self, capsule: Capsule, ctx: AgentContext) -> CapsuleResult:
        ...

    def health(self, ctx: AgentContext) -> Dict[str, Any]:
        return {"engine": self.name, "ok": True}

    def supports_pass(self) -> bool:
        return True
