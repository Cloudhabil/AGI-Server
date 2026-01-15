"""
Hermes 25+5 Runner (enterprise-safe scaffold).

- Runs the Hermes Protein Folding Hypothesis Miner in a 25+5 cadence.
- Local-first, no network calls. Uses dense_state + VNAND when available.
- Records structured logs with request_id, cycle, phase, provenance, governance.

Usage (from repo root):
  python scripts/hermes_25_5_runner.py --payload-file payload.json --out logs/hermes_25_5_log.jsonl

Notes:
- Payload is passed through to the Hermes skill as input_data["payload"].
- Safety/retrieval hooks are stubs; wire them to your local services.
- VNAND persistence is best-effort; falls back to JSONL logging.
"""
from __future__ import annotations

import argparse
import json
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Skill context
from skills.base import SkillContext

# --- Config loading ---------------------------------------------------------


def load_dense_state_config() -> Dict[str, Any]:
    cfg_path = Path("config/dense_state.json")
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    # Minimal default
    return {
        "vnand": {"enabled": False},
    }


# --- VNAND / dense-state integration (best-effort) --------------------------
try:
    from gpia.memory.dense_state.log_schema import DenseStateLogEntry
    from gpia.memory.dense_state.storage import DenseStateStorage
except Exception:
    DenseStateLogEntry = None  # type: ignore
    DenseStateStorage = None  # type: ignore


def make_dense_entry(vector: List[float], mode: str, metrics: Dict[str, Any]) -> Optional[Any]:
    if DenseStateLogEntry is None:
        return None
    ts = time.time()
    return DenseStateLogEntry(
        vector=vector,
        mode=mode,
        shape=[len(vector)],
        dtype="float32",
        adapter_version="hermes_25_5",
        timestamp=ts,
        metrics=metrics,
    )


# --- Safety stub ------------------------------------------------------------


def run_safety_gate(output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Placeholder safety/ethics gate. Extend to call safety governor.
    """
    # Add a marker; real gate should set pass/fail and reasons.
    output["safety"] = {"status": "PENDING_REVIEW"}
    return output


# --- Runner -----------------------------------------------------------------


@dataclass
class CycleResult:
    cycle: int
    phase: str
    status: str
    insights: List[Any]
    governance: Dict[str, Any]
    safety: Dict[str, Any]
    provenance: List[Any]
    raw_output: Dict[str, Any]


def run_cycle(skill, payload: Dict[str, Any], phase: str, cycle: int) -> CycleResult:
    input_data = {"payload": payload, "mode": "analyze" if phase == "baseline" else "rank"}
    raw = skill.execute(input_data=input_data, context=SkillContext())  # type: ignore
    output = raw.output if hasattr(raw, "output") else {}
    output = run_safety_gate(output)

    return CycleResult(
        cycle=cycle,
        phase=phase,
        status=output.get("status", "UNKNOWN"),
        insights=output.get("insights", []),
        governance=output.get("governance", {}),
        safety=output.get("safety", {}),
        provenance=output.get("provenance", []),
        raw_output=output,
    )


def main():
    parser = argparse.ArgumentParser(description="Hermes 25+5 runner (local-only)")
    parser.add_argument("--payload-file", type=str, help="JSON file with payload", default=None)
    parser.add_argument("--out", type=str, default="logs/hermes_25_5_log.jsonl", help="Output log file (JSONL)")
    args = parser.parse_args()

    payload: Dict[str, Any] = {}
    if args.payload_file:
        payload = json.loads(Path(args.payload_file).read_text(encoding="utf-8"))

    # Lazy import of Hermes skill
    from skills.synthesized.hermes_trismegistos.protein_folding_hypothesis_miner.skill import (
        HermesTrismegistosSkill,
    )

    skill = HermesTrismegistosSkill()
    cfg = load_dense_state_config()

    # VNAND storage (best-effort)
    storage = None
    if DenseStateStorage is not None:
        storage = DenseStateStorage(config=cfg, vnand_root=cfg.get("vnand", {}).get("root_dir", "data/vnand"))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    request_id = f"hermes-25-5-{uuid.uuid4().hex}"

    log_file = out_path.open("a", encoding="utf-8")

    # Baseline 25
    results: List[CycleResult] = []
    for i in range(1, 26):
        res = run_cycle(skill, payload, phase="baseline", cycle=i)
        results.append(res)

    # Decision point (could be expanded to real gap analysis)
    decision_snapshot = {
        "request_id": request_id,
        "cycle": 25,
        "decision": "continue_to_targeted",
        "timestamp": time.time(),
    }
    log_file.write(json.dumps(decision_snapshot) + "\n")

    # Targeted 5
    for i in range(26, 31):
        res = run_cycle(skill, payload, phase="targeted", cycle=i)
        results.append(res)

    # Emit logs and VNAND entries
    for res in results:
        record = {
            "request_id": request_id,
            "cycle": res.cycle,
            "phase": res.phase,
            "status": res.status,
            "insights": res.insights,
            "governance": res.governance,
            "safety": res.safety,
            "provenance": res.provenance,
            "timestamp": time.time(),
        }
        log_file.write(json.dumps(record) + "\n")

        if storage and DenseStateLogEntry is not None:
            vector = [float(len(res.insights) or 1.0)]  # minimal placeholder vector
            metrics = {"cycle": res.cycle, "phase": res.phase}
            entry = make_dense_entry(vector, mode="hermes", metrics=metrics)
            if entry is not None:
                try:
                    storage.append(entry)
                except Exception:
                    pass

    log_file.flush()
    log_file.close()

    print(f"[DONE] Hermes 25+5 run complete. Log: {out_path}")


if __name__ == "__main__":
    main()
