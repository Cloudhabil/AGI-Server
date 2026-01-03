#!/usr/bin/env python3
"""
Compute and save dense-state normalization stats (mean/std) from JSONL logs.
Usage:
    python scripts/lock_dense_state_stats.py --logs path/to/logs.jsonl --out artifacts/dense_state/dense_state_stats.pt
"""
from __future__ import annotations

import argparse
from pathlib import Path

from train_dense_state_golden_route import compute_stats, detect_keys, iter_jsonl, save_stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs", required=True, help="Path to JSONL logs with text/state/resonance")
    ap.add_argument("--out", required=True, help="Path to save stats artifact (pt)")
    args = ap.parse_args()

    logs_path = Path(args.logs)
    out_path = Path(args.out)

    first = None
    for rec in iter_jsonl(logs_path):
        if any(isinstance(v, str) for v in rec.values()) and any(isinstance(v, list) for v in rec.values()) and any(isinstance(v, (int, float)) for v in rec.values()):
            first = rec
            break
    if first is None:
        raise RuntimeError("Cannot find a record suitable for key detection in logs.")
    _text_key, state_key, _res_key = detect_keys(first)

    stats = compute_stats(logs_path, state_key)
    save_stats(stats, out_path)
    print(f"[stats] saved to {out_path} count={stats['count']} state_dim={stats['state_dim']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
