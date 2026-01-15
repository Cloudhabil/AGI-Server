"""
Local ingestion stub for biomedical corpus (no network).

- Reads JSON files from a specified directory (default: data/corpus_sources).
- Merges them into data/biomedical_corpus.json (append/update by id).
- Enforces basic allowlist from config/hermes_bio_sources.json (status != allowed are skipped).

Usage:
  python scripts/ingest_biomedical_corpus.py --source-dir data/corpus_sources --out data/biomedical_corpus.json
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple

MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB per file guard


def load_allowlist() -> Dict[str, Any]:
    cfg_path = Path("config/hermes_bio_sources.json")
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"sources": []}


def _reject(reason: str, stats: Dict[str, Any]) -> None:
    stats["rejected"] += 1
    stats["rejected_reasons"][reason] = stats["rejected_reasons"].get(reason, 0) + 1


def _process_entries(
    entries: List[Any], allowed_sources: set, merged: Dict[str, Any]
) -> Tuple[int, int]:
    """
    Returns (added_records, allow_hits) where allow_hits counts entries that passed allowlist.
    """
    added = 0
    allow_hits = 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        src_name = entry.get("source", "")
        if allowed_sources and src_name not in allowed_sources:
            continue
        allow_hits += 1
        if "id" in entry:
            merged[entry["id"]] = entry
            added += 1
    return added, allow_hits


def ingest_corpus(source_dir: Path, out_path: Path) -> Dict[str, Any]:
    """
    Ingest JSON/JSONL files from source_dir into out_path.
    Returns corpus list and ingest_stats.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    stats: Dict[str, Any] = {
        "enabled": True,
        "accepted": 0,
        "rejected": 0,
        "bytes": 0,
        "rejected_reasons": {},
        "accepted_records": 0,
    }

    allow = load_allowlist()
    allowed_sources = {
        s.get("name")
        for s in allow.get("sources", [])
        if s.get("status", "").startswith("allowed")
    }

    merged: Dict[str, Any] = {}
    if out_path.exists():
        try:
            for entry in json.loads(out_path.read_text(encoding="utf-8")):
                if "id" in entry:
                    merged[entry["id"]] = entry
        except Exception:
            pass

    if not source_dir.exists():
        _reject("source_dir_missing", stats)
        out_path.write_text(json.dumps(list(merged.values()), indent=2), encoding="utf-8")
        return {"corpus": list(merged.values()), "ingest_stats": stats}

    for path in source_dir.glob("*.json*"):
        if path.suffix.lower() not in (".json", ".jsonl"):
            _reject("not_json", stats)
            continue
        try:
            size = path.stat().st_size
            if size > MAX_FILE_BYTES:
                _reject("too_large", stats)
                continue
        except Exception:
            _reject("stat_error", stats)
            continue

        try:
            raw = path.read_bytes()
        except Exception:
            _reject("read_error", stats)
            continue

        try:
            added = 0
            allow_hits = 0
            if path.suffix.lower() == ".jsonl":
                lines = raw.decode("utf-8", errors="replace").splitlines()
                parsed = []
                for ln in lines:
                    ln = ln.strip()
                    if not ln:
                        continue
                    parsed.append(json.loads(ln))
                added, allow_hits = _process_entries(parsed, allowed_sources, merged)
            else:
                obj = json.loads(raw.decode("utf-8", errors="replace"))
                if isinstance(obj, list):
                    added, allow_hits = _process_entries(obj, allowed_sources, merged)
                else:
                    added, allow_hits = _process_entries([obj], allowed_sources, merged)

            if allow_hits == 0:
                _reject("not_allowlisted", stats)
                continue

            stats["accepted"] += 1
            stats["bytes"] += len(raw)
            stats["accepted_records"] += added
        except json.JSONDecodeError:
            _reject("parse_error", stats)
        except Exception:
            _reject("ingest_error", stats)

    out_path.write_text(json.dumps(list(merged.values()), indent=2), encoding="utf-8")
    return {"corpus": list(merged.values()), "ingest_stats": stats}


def main():
    parser = argparse.ArgumentParser(description="Local biomedical corpus ingestion (no network)")
    parser.add_argument("--source-dir", type=str, default="data/corpus_sources", help="Directory with *.json files")
    parser.add_argument("--out", type=str, default="data/biomedical_corpus.json", help="Output merged corpus file")
    args = parser.parse_args()

    result = ingest_corpus(Path(args.source_dir), Path(args.out))
    stats = result.get("ingest_stats", {})
    print(
        f"[OK] merged corpus entries: {len(result.get('corpus', []))} -> {args.out} "
        f"(accepted={stats.get('accepted',0)}, rejected={stats.get('rejected',0)})"
    )


if __name__ == "__main__":
    main()
