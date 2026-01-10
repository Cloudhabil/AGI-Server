from __future__ import annotations

from core.agents.base import AgentContext
from core.runtime.capsule_engine import CapsuleEngine
from core.runtime.capsule_types import Capsule, CapsuleResult


class NativeCapsuleEngine(CapsuleEngine):
    """
    Placeholder for the clean, in-repo capsule executor.
    Extend this over time while keeping the legacy engine as fallback.
    """

    name = "native"

    def execute(self, capsule: Capsule, ctx: AgentContext) -> CapsuleResult:
        ctx.telemetry.emit("capsule.native.stub", {"capsule_id": capsule.id})
        return CapsuleResult(
            ok=False,
            capsule_id=capsule.id,
            error="NativeCapsuleEngine not implemented yet",
        )
