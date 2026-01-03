"""Reflex audit logger."""

import json
from pathlib import Path


def run(task, context, level, flags, runtime, manifest, policy, schema):
    decision = runtime.get("last_decision") or {}
    payload = {
        "input_hash": runtime.get("input_hash"),
        "decision": decision.get("action", "PASS"),
        "audit": decision.get("audit", {}),
        "elapsed_ms": decision.get("elapsed_ms"),
    }
    log_path = Path(__file__).resolve().parents[2] / "core" / "reflex_audit.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    except OSError:
        pass

    return {"action": "PASS", "payload": {}, "audit": {"level": level, "decision": "logged"}}
