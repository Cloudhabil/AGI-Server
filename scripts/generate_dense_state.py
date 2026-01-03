#!/usr/bin/env python3
"""
Generate a single dense-state snapshot and append it to logs/gpia_server_dense_state.jsonl.
Runs non-interactively to seed the log for GPIA-bridge dense-state consumption.
"""
from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.resonant_kernel.interface import TemporalFormalismContract

LOG_PATH = Path("logs") / "gpia_server_dense_state.jsonl"


def main() -> int:
    contract = TemporalFormalismContract()
    task = "seed dense state"
    tokens = contract.tokens_from_text(task, max_tokens=256)
    env_bias = contract.observe_telemetry(cpu=None, vram=None)
    result = contract.evolve_state(tokens, env_bias)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": f"seed-{uuid.uuid4().hex[:8]}",
        "model": "gpia-seed",
        "resonance_hash": (result.get("vector_hash") or "")[:16],
        "resonance_score": result.get("resonance_score"),
        "tokens": len(tokens),
        "prompt_snippet": task,
    }

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")

    print(f"Wrote dense-state snapshot to {LOG_PATH}: {entry}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
