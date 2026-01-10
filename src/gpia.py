"""
gpia.py: General Purpose Intelligent Agent entry point (shim).

This file now delegates to the unified runtime kernel (boot.py).
The legacy GPIA behavior is preserved by running in Sovereign-Loop mode,
which can be customized to match the original GPIA semantics.
"""

from __future__ import annotations

import sys

from boot import main


def execute_capsule(capsule_dict, ctx_adapter):
    """
    Legacy capsule bridge for LegacyCapsuleEngine.

    Args:
        capsule_dict: Serialized capsule data.
        ctx_adapter: Minimal context view (identity, ledger, telemetry, perception, kernel, state).
    Returns:
        dict with keys: ok, output, error, blocked, pass_request, metrics
    """
    goal = capsule_dict.get("goal", "")
    capsule_id = capsule_dict.get("id", "unknown")

    telemetry = ctx_adapter.get("telemetry")
    if telemetry:
        try:
            telemetry.emit("gpia.legacy_capsule.start", {"capsule_id": capsule_id, "goal": goal})
        except Exception:
            pass

    try:
        # TODO: Replace this with real legacy execution pipeline.
        output = {
            "echo_goal": goal,
            "payload": capsule_dict.get("payload", {}),
        }
        metrics = {"engine": "legacy_gpia_stub"}

        if telemetry:
            try:
                telemetry.emit(
                    "gpia.legacy_capsule.done",
                    {"capsule_id": capsule_id, "ok": True, "goal": goal},
                )
            except Exception:
                pass

        return {
            "ok": True,
            "output": output,
            "error": None,
            "blocked": False,
            "pass_request": None,
            "metrics": metrics,
        }

    except Exception as e:
        if telemetry:
            try:
                telemetry.emit(
                    "gpia.legacy_capsule.error",
                    {"capsule_id": capsule_id, "error": str(e)},
                )
            except Exception:
                pass
        return {
            "ok": False,
            "output": {},
            "error": str(e),
            "blocked": False,
            "pass_request": None,
            "metrics": {},
        }


if __name__ == "__main__":
    # Preserve legacy behavior: default to Sovereign-Loop mode
    if "--mode" not in sys.argv:
        sys.argv += ["--mode", "Sovereign-Loop"]
    raise SystemExit(main())
