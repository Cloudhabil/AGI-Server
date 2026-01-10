from __future__ import annotations

import importlib
from typing import Any, Dict

from core.agents.base import AgentContext
from core.runtime.capsule_engine import CapsuleEngine
from core.runtime.capsule_types import Capsule, CapsuleResult


class LegacyCapsuleEngine(CapsuleEngine):
    """
    Lazy wrapper around legacy gpia.py (or other legacy module) so modes can
    execute capsules without importing heavy dependencies at import time.
    """

    name = "legacy_gpia"

    def __init__(self, module_path: str = "gpia") -> None:
        self._module_path = module_path
        self._gpia_mod = None  # Lazy-loaded module

    def _load(self, ctx: AgentContext):
        if self._gpia_mod is not None:
            return self._gpia_mod

        ctx.telemetry.emit("capsule_engine.legacy.import.start", {"module": self._module_path})
        mod = importlib.import_module(self._module_path)
        ctx.telemetry.emit("capsule_engine.legacy.import.done", {"module": self._module_path})

        if not hasattr(mod, "execute_capsule"):
            raise RuntimeError(
                "Legacy module missing required function: execute_capsule(capsule_dict, ctx_adapter)"
            )

        self._gpia_mod = mod
        return mod

    def execute(self, capsule: Capsule, ctx: AgentContext) -> CapsuleResult:
        try:
            gpia = self._load(ctx)

            # Minimal adapter to avoid leaking kernel internals.
            ctx_adapter: Dict[str, Any] = {
                "identity": ctx.identity,
                "ledger": ctx.ledger,
                "telemetry": ctx.telemetry,
                "perception": ctx.perception,
                "kernel": ctx.kernel,
                "state": ctx.state,
            }

            ctx.telemetry.emit(
                "capsule.execute.start", {"engine": self.name, "capsule_id": capsule.id}
            )
            raw = gpia.execute_capsule(capsule.__dict__, ctx_adapter)

            res = CapsuleResult(
                ok=bool(raw.get("ok", True)),
                capsule_id=capsule.id,
                output=dict(raw.get("output", {})),
                error=raw.get("error"),
                blocked=bool(raw.get("blocked", False)),
                pass_request=raw.get("pass_request"),
                metrics=dict(raw.get("metrics", {})),
            )

            ctx.telemetry.emit(
                "capsule.execute.done",
                {"engine": self.name, "capsule_id": capsule.id, "ok": res.ok, "blocked": res.blocked},
            )
            return res

        except Exception as e:
            ctx.telemetry.emit(
                "capsule.execute.error",
                {"engine": self.name, "capsule_id": capsule.id, "error": str(e)},
            )
            return CapsuleResult(ok=False, capsule_id=capsule.id, error=str(e))
