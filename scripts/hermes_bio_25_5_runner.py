"""
Hermes Biomedical 25+5 Runner (governed, local-only).

- Runs the Hermes Biomedical Discovery skill in a 25+5 cadence.
- Local-first, no network calls. Uses dense_state + VNAND when available.
- Records structured logs with request_id, cycle, phase, provenance, governance, promotion.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import os
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from skills.base import SkillContext

SCHEMA_VERSION = 1
ALLOWED_SAFETY = {"ALLOW", "PENDING_REVIEW", "BLOCKED"}
ALLOWED_PROMO = {"promoted", "discarded", "unverified", "blocked_by_safety"}


def _sha256_file(path: str) -> Optional[str]:
    p = Path(path)
    if not p.exists():
        return None
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _alignment_ref(path: str) -> Dict[str, Any]:
    return {"path": path, "sha256": _sha256_file(path)}


def _file_exists(path: Optional[str]) -> bool:
    return bool(path) and Path(path).exists()


def _git_info(repo_root: Optional[str] = None) -> Dict[str, Any]:
    cwd = repo_root or os.getcwd()
    try:
        sha = (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=cwd, stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )
        dirty_rc = subprocess.call(
            ["git", "diff", "--quiet"],
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        dirty = bool(dirty_rc != 0)
        return {"sha": sha, "dirty": dirty}
    except Exception:
        return {"sha": None, "dirty": None}


def _read_json_len(path: str) -> Optional[int]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
        if isinstance(obj, list):
            return len(obj)
        return None
    except Exception:
        return None

MODEL_SELECTOR_PAYLOAD = {
    "task": "biomedical_discovery",
    "preferred": ["qwen2", "tensorrt-mistral"],
    "fallback": ["small-llm"],
}


def select_model() -> Optional[str]:
    """Best-effort model selection via model_router with TRT preference."""
    try:
        from agents.model_router import ModelRouter

        router = ModelRouter()
        for mid in MODEL_SELECTOR_PAYLOAD["preferred"] + MODEL_SELECTOR_PAYLOAD["fallback"]:
            if mid in router.models:
                return mid
        return router._default_model_id if hasattr(router, "_default_model_id") else None
    except Exception:
        return None


def load_dense_state_config() -> Dict[str, Any]:
    cfg_path = Path("config/dense_state.json")
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"vnand": {"enabled": False}}


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
        adapter_version="hermes_bio_25_5",
        timestamp=ts,
        metrics=metrics,
    )


def _safe_gate_status(output: Dict[str, Any]) -> Dict[str, Any]:
    try:
        prov = output.get("provenance") or []
        if not prov:
            return {"status": "BLOCKED", "reason": "no_provenance"}
        for p in prov:
            lic = str(p.get("license", "unknown")).lower()
            if lic in ("unknown", "proprietary", "restricted"):
                return {"status": "BLOCKED", "reason": "license_disallowed"}
        return {"status": "ALLOW", "reason": "ok"}
    except Exception as e:
        return {"status": "BLOCKED", "reason": f"gate_error:{e.__class__.__name__}"}


def run_safety_gate(output: Dict[str, Any]) -> Dict[str, Any]:
    output["safety"] = _safe_gate_status(output)
    return output


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


def run_cycle(skill, payload: Dict[str, Any], phase: str, cycle: int, model_id: Optional[str]) -> CycleResult:
    input_data = {"payload": payload, "mode": "analyze" if phase == "baseline" else "rank"}
    ctx = SkillContext(agent_model=model_id)
    raw = skill.execute(input_data=input_data, context=ctx)  # type: ignore
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


def verify_log(path: Path) -> None:
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        raise SystemExit("verification failed: empty log")
    try:
        first = json.loads(lines[0])
    except Exception as e:
        raise SystemExit(f"verification failed: cannot parse first line: {e}")
    if first.get("record_type") != "run_meta":
        raise SystemExit("verification failed: first record is not run_meta")
    if first.get("schema_version") != SCHEMA_VERSION:
        raise SystemExit(
            f"verification failed: schema_version mismatch (got {first.get('schema_version')}, expected {SCHEMA_VERSION})"
        )
    run_id = first.get("run_id")
    if not run_id:
        raise SystemExit("verification failed: run_meta missing run_id")
    ingest = first.get("ingest_stats") or first.get("ingestion") or {}
    if (ingest.get("enabled")) and not all(k in ingest for k in ("accepted", "rejected", "bytes", "rejected_reasons")):
        raise SystemExit("verification failed: ingest_stats missing required fields")
    for idx, ln in enumerate(lines[1:], start=2):
        try:
            obj = json.loads(ln)
        except Exception as e:
            raise SystemExit(f"verification failed line {idx}: parse error {e}")
        if obj.get("run_id") != run_id:
            raise SystemExit(f"verification failed line {idx}: run_id mismatch")
        if obj.get("schema_version") != SCHEMA_VERSION:
            raise SystemExit(
                f"verification failed line {idx}: schema_version mismatch (got {obj.get('schema_version')}, expected {SCHEMA_VERSION})"
            )
        safety = (obj.get("safety") or {}).get("status") if "safety" in obj else None
        promo = obj.get("promotion")
        if safety and safety not in ALLOWED_SAFETY:
            raise SystemExit(f"verification failed line {idx}: invalid safety {safety}")
        if promo and promo not in ALLOWED_PROMO:
            raise SystemExit(f"verification failed line {idx}: invalid promotion {promo}")
        if safety in ("BLOCKED", "PENDING_REVIEW") and promo and promo != "blocked_by_safety":
            raise SystemExit(
                f"verification failed line {idx}: safety {safety} but promotion {promo}"
            )


def main():
    parser = argparse.ArgumentParser(description="Hermes Biomedical 25+5 runner (local-only)")
    parser.add_argument("--payload-file", type=str, help="JSON file with payload", default=None)
    parser.add_argument("--out", type=str, default=None, help="Output log file (JSONL). If omitted, a timestamped file is created.")
    parser.add_argument(
        "--append-corpus",
        type=str,
        default="data/biomedical_corpus.json",
        help="Optional: append discovered provenance to this corpus file between baseline and targeted phases",
    )
    parser.add_argument(
        "--goal",
        type=str,
        default="",
        help="High-value question/alignment goal (for logging/traceability)",
    )
    parser.add_argument(
        "--alignment-file",
        type=str,
        default="research/initial_alignment.md",
        help="Path to alignment context (hashed for traceability)",
    )
    parser.add_argument(
        "--ingest-dir",
        type=str,
        default=None,
        help="Optional: path with *.json sources to ingest into the corpus before running",
    )
    parser.add_argument(
        "--score-threshold",
        type=float,
        default=None,
        help="Optional: Professor score threshold for promotion (0-1). If not set, promotion still emitted per safety/score presence.",
    )
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="Run invariant verification after execution; exits non-zero on failure.",
    )
    parser.add_argument(
        "--phase",
        choices=["baseline", "targeted", "both"],
        default="both",
        help="Operational phase to run (baseline=1-25, targeted=26-30, both=1-30)",
    )
    parser.add_argument(
        "--latest-path",
        type=str,
        default="logs/hermes_bio_latest.jsonl",
        help="Path to copy the latest successful run log (Windows-safe copy).",
    )
    args = parser.parse_args()

    if args.score_threshold is not None and not args.self_check:
        print("ERROR: --score-threshold requires --self-check (promotion must be verified).", file=sys.stderr)
        sys.exit(2)

    payload: Dict[str, Any] = {}
    if args.payload_file:
        payload = json.loads(Path(args.payload_file).read_text(encoding="utf-8"))

    from skills.synthesized.hermes_trismegistos.biomedical_discovery.skill import (
        HermesBiomedicalDiscoverySkill,
    )

    skill = HermesBiomedicalDiscoverySkill()
    cfg = load_dense_state_config()

    # Optional ingestion step (Professor/data agent populating corpus)
    if args.ingest_dir:
        src_dir = Path(args.ingest_dir)
        corpus_path = Path(args.append_corpus or "data/biomedical_corpus.json")
        ingest_result = None
        try:
            from scripts.ingest_biomedical_corpus import ingest_corpus
        except Exception:
            # Fallback: load by path to avoid import resolution issues
            import importlib.util

            ingest_path = Path("scripts/ingest_biomedical_corpus.py").resolve()
            spec = importlib.util.spec_from_file_location("ingest_biomedical_corpus", ingest_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                ingest_corpus = getattr(module, "ingest_corpus", None)  # type: ignore
            else:
                ingest_corpus = None
        if ingest_corpus:
            ingest_result = ingest_corpus(src_dir, corpus_path)
        else:
            print("[WARN] Ingest module unavailable after fallback import.")

        if ingest_result and ingest_result.get("ingest_stats"):
            ingest_stats = ingest_result["ingest_stats"]

    # Model selection (Alpha -> Beta fallback if needed)
    model_id = select_model()

    storage = None
    if DenseStateStorage is not None:
        storage = DenseStateStorage(config=cfg, vnand_root=cfg.get("vnand", {}).get("root_dir", "data/vnand"))

    # TensorRT preflight (warn if sidecar unavailable when TRT is requested)
    if os.getenv("GPIA_USE_TENSORRT", "0") in ("1", "true", "on"):
        try:
            from integrations.trt_llm_client import TensorRTClient

            tcli = TensorRTClient()
            if not tcli.is_alive():
                print("[WARN] TensorRT sidecar not responding; TRT path will be skipped.")
        except Exception as e:
            print(f"[WARN] TensorRT client unavailable: {e}")

    if args.out:
        out_path = Path(args.out)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = Path("logs") / f"hermes_bio_{ts}.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    request_id = f"hermes-bio-25-5-{uuid.uuid4().hex}"
    alignment_ref = _alignment_ref(args.alignment_file)

    # Corpus stats before append
    corpus_before = {
        "path": args.append_corpus,
        "exists": _file_exists(args.append_corpus),
        "sha256": _sha256_file(args.append_corpus),
        "count": _read_json_len(args.append_corpus) if _file_exists(args.append_corpus) else 0,
    }
    ingest_stats = {
        "enabled": bool(args.ingest_dir),
        "accepted": 0,
        "rejected": 0,
        "bytes": 0,
        "rejected_reasons": {},
    }

    log_file = out_path.open("w", encoding="utf-8")

    # Corpus stats after ingestion (before baseline)
    corpus_after_ingest = {
        "path": args.append_corpus,
        "exists": _file_exists(args.append_corpus),
        "sha256": _sha256_file(args.append_corpus),
        "count": _read_json_len(args.append_corpus) if _file_exists(args.append_corpus) else None,
    }

    git_info = _git_info()

    run_meta = {
        "record_type": "run_meta",
        "schema_version": SCHEMA_VERSION,
        "run_id": request_id,
        "timestamp": time.time(),
        "goal": args.goal,
        "alignment_ref": alignment_ref,
        "git": git_info,
        "model": {
            "router": "ModelRouter",
            "selected": model_id,
        },
        "ingestion": ingest_stats,
        "ingest_stats": ingest_stats,
        "corpus": {
            "format": "json_array",
            "before": corpus_before,
            "after_ingest": corpus_after_ingest,
        },
        "args": {
            "score_threshold": args.score_threshold,
            "ingest_dir": args.ingest_dir,
            "payload_file": args.payload_file,
            "append_corpus": args.append_corpus,
            "use_tensorrt": bool(os.getenv("GPIA_USE_TENSORRT")),
            "phase": args.phase,
        },
    }
    log_file.write(json.dumps(run_meta) + "\n")

    results: List[CycleResult] = []
    
    # Baseline 25
    if args.phase in ("baseline", "both"):
        for i in range(1, 26):
            res = run_cycle(skill, payload, phase="baseline", cycle=i, model_id=model_id)
            results.append(res)

        decision_snapshot = {
            "record_type": "decision",
            "schema_version": SCHEMA_VERSION,
            "request_id": request_id,
            "run_id": request_id,
            "cycle": 25,
            "decision": "continue_to_targeted",
            "timestamp": time.time(),
            "goal": args.goal,
            "alignment_ref": alignment_ref,
        }
        log_file.write(json.dumps(decision_snapshot) + "\n")

        # Append baseline provenance to corpus (if requested)
        if args.append_corpus:
            corpus_path = Path(args.append_corpus)
            corpus_path.parent.mkdir(parents=True, exist_ok=True)
            existing = {}
            if corpus_path.exists():
                try:
                    for entry in json.loads(corpus_path.read_text(encoding="utf-8")):
                        if "id" in entry:
                            existing[entry["id"]] = entry
                except Exception:
                    pass
            for res in results:
                if res.phase != "baseline":
                    continue
                for prov in res.provenance or []:
                    pid = prov.get("id") or f"{request_id}_{res.cycle}_{prov.get('source','')}"
                    if pid not in existing:
                        prov_copy = dict(prov)
                        prov_copy["id"] = pid
                        existing[pid] = prov_copy
            corpus_path.write_text(json.dumps(list(existing.values()), indent=2), encoding="utf-8")
            log_file.write(
                json.dumps(
                    {
                        "record_type": "corpus_append",
                        "schema_version": SCHEMA_VERSION,
                        "request_id": request_id,
                        "run_id": request_id,
                        "cycle": 25,
                        "corpus_appended": True,
                        "corpus_path": str(corpus_path),
                        "alignment_ref": alignment_ref,
                        "timestamp": time.time(),
                    }
                )
                + "\n"
            )

    # Targeted 5
    if args.phase in ("targeted", "both"):
        for i in range(26, 31):
            res = run_cycle(skill, payload, phase="targeted", cycle=i, model_id=model_id)
            results.append(res)

    # Prepare padding length if voxel mode is enabled
    padding_len = None
    mode_cfg = cfg.get("mode", "vector")
    if mode_cfg == "voxel":
        shape = cfg.get("voxel", {}).get("shape", [])
        if shape:
            padding_len = 1
            for d in shape:
                padding_len *= int(d)

    for res in results:
        record = {
            "record_type": "cycle",
            "schema_version": SCHEMA_VERSION,
            "request_id": request_id,
            "run_id": request_id,
            "cycle": res.cycle,
            "phase": res.phase,
            "status": res.status,
            "insights": res.insights,
            "governance": res.governance,
            "safety": res.safety,
            "provenance": res.provenance,
            "timestamp": time.time(),
            "goal": args.goal,
            "alignment_ref": alignment_ref,
        }

        # Scoring/promotion logic with safety precedence
        score = res.raw_output.get("score") if isinstance(res.raw_output, dict) else None
        if score is not None:
            record["score"] = score
        safety_status = (record.get("safety") or {}).get("status")

        if safety_status in ("BLOCKED", "PENDING_REVIEW"):
            record["promotion"] = "blocked_by_safety"
        elif score is None:
            record["promotion"] = "unverified"
        elif args.score_threshold is None:
            record["promotion"] = "unverified"
        else:
            record["promotion"] = "promoted" if float(score) >= float(args.score_threshold) else "discarded"

        log_file.write(json.dumps(record) + "\n")

        if storage and DenseStateLogEntry is not None:
            supports = [i.get("support", 0.0) for i in (res.insights or [])]
            avg_support = sum(supports) / len(supports) if supports else 0.0
            vector = [float(len(res.insights) or 1.0), float(avg_support)]
            if padding_len and padding_len > len(vector):
                vector = vector + [0.0] * (padding_len - len(vector))
            metrics = {"cycle": res.cycle, "phase": res.phase}
            entry = make_dense_entry(vector, mode="hermes_bio", metrics=metrics)
            if entry is not None:
                try:
                    storage.append(entry)
                except Exception:
                    pass

    log_file.flush()
    log_file.close()
    if args.self_check:
        verify_log(out_path)
        print(f"[SELF-CHECK] Log invariants OK: {out_path}")
    if args.latest_path:
        latest_path = Path(args.latest_path)
        latest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(out_path, latest_path)
        print(f"[LATEST] Copied to {latest_path}")
    print(f"[DONE] Hermes biomedical 25+5 run complete. Log: {out_path}")


if __name__ == "__main__":
    main()
