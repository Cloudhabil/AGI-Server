#!/usr/bin/env python3
"""
CLI wrapper for the BSD Gap Closure Framework skill.

Example:
  python run_bsd_gap_closure_framework.py --a -1 --b 0 --primes 101,103 --write-report
"""
# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List

from skills.base import SkillContext
from skills.research.bsd_gap_closure_framework.skill import BSDGapClosureFrameworkSkill


def _parse_int_list(csv: str) -> List[int]:
    out: List[int] = []
    for part in csv.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(int(part))
        except Exception:
            continue
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="BSD Gap Closure Framework (evidence + needs generator)")
    parser.add_argument("--a", type=int, help="Curve coefficient a for y^2 = x^3 + a x + b")
    parser.add_argument("--b", type=int, help="Curve coefficient b for y^2 = x^3 + a x + b")
    parser.add_argument("--x-bound", type=int, default=200, help="Integral x search bound")
    parser.add_argument("--u-bound", type=int, default=200, help="u bound for x=u/v^2 search")
    parser.add_argument("--v-bound", type=int, default=30, help="v bound for x=u/v^2 search")
    parser.add_argument("--torsion-order-max", type=int, default=24, help="Max n for small torsion-order detection")
    parser.add_argument("--primes", type=str, default="", help="Comma-separated primes for reduction checks")
    parser.add_argument("--max-naive-prime", type=int, default=20000, help="Skip naive point count for p > this")
    parser.add_argument("--sha-inputs", type=str, default="", help="JSON object with sha_inputs fields")
    parser.add_argument("--write-report", action="store_true", help="Write a markdown report under data/")
    parser.add_argument("--report-path", type=str, default="", help="Override report path (relative to repo root)")

    args = parser.parse_args()

    payload: Dict[str, Any] = {"capability": "run"}
    if args.a is not None and args.b is not None:
        payload["curve"] = {"a": args.a, "b": args.b}

    payload["search"] = {
        "x_bound": args.x_bound,
        "u_bound": args.u_bound,
        "v_bound": args.v_bound,
        "torsion_order_max": args.torsion_order_max,
    }

    if args.primes:
        payload["primes"] = _parse_int_list(args.primes)
    payload["max_naive_prime"] = args.max_naive_prime

    if args.sha_inputs:
        payload["sha_inputs"] = json.loads(args.sha_inputs)

    if args.write_report:
        payload["write_report"] = True
        if args.report_path:
            payload["report_path"] = args.report_path

    skill = BSDGapClosureFrameworkSkill()
    ctx = SkillContext(user_id="cli", session_id="cli", agent_role="cli")
    result = skill.execute(payload, ctx)
    if not result.success:
        raise SystemExit(result.error or "failed")

    print(json.dumps(result.output, indent=2, ensure_ascii=False))
    if result.artifacts.get("report_path"):
        print(f"\nReport written to: {result.artifacts['report_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
