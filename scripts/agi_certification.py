#!/usr/bin/env python3
"""
AGI certification runner: executes benchmark suite and contextual profiles,
then collects artifacts into a certification folder.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = ROOT / "runs"


def run_command(args: list[str], log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as handle:
        proc = subprocess.run(
            args,
            cwd=ROOT,
            stdout=handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
    return proc.returncode


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_summary(
    output_dir: Path,
    suite_results: Optional[Dict[str, Any]],
    contextual_results: Optional[Dict[str, Any]],
    duration: float,
) -> None:
    lines = []
    lines.append("# AGI Certification Summary")
    lines.append("")
    lines.append(f"Generated at: {time.strftime('%Y-%m-%dT%H:%M:%S')}")
    lines.append(f"Contextual duration: {duration:.1f}s per profile")
    lines.append("")

    if suite_results:
        summary = suite_results.get("summary", {})
        lines.append("## Benchmark Suite")
        lines.append("")
        lines.append(f"- Total tests: {summary.get('total_tests')}")
        lines.append(f"- Passed: {summary.get('passed')}")
        lines.append(f"- Failed: {summary.get('failed')}")
        lines.append("")
        lines.append("| Category | Passed | Failed | Avg Time (ms) |")
        lines.append("|---|---:|---:|---:|")
        categories = summary.get("categories", {})
        for name, stats in categories.items():
            lines.append(
                f"| {name} | {stats.get('passed')} | {stats.get('failed')} | {stats.get('avg_time_ms'):.1f} |"
            )
        lines.append("")
    else:
        lines.append("## Benchmark Suite")
        lines.append("")
        lines.append("- Suite results not found.")
        lines.append("")

    if contextual_results:
        results = contextual_results.get("results", [])
        lines.append("## Contextual Dense State Benchmark")
        lines.append("")
        lines.append("| Profile | Tokens/sec | Cycles/sec | Cycles | Tokens | Duration (s) |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for entry in results:
            lines.append(
                f"| {entry.get('label')} | {entry.get('tokens_per_sec'):.1f} | "
                f"{entry.get('cycles_per_sec'):.1f} | {entry.get('cycles')} | "
                f"{entry.get('tokens')} | {entry.get('duration'):.3f} |"
            )
        lines.append("")

        if results:
            best = max(results, key=lambda item: item.get("tokens_per_sec", 0))
            worst = min(results, key=lambda item: item.get("tokens_per_sec", 0))
            lines.append(
                f"- Top throughput: {best.get('label')} at {best.get('tokens_per_sec'):.1f} tokens/sec."
            )
            lines.append(
                f"- Lowest throughput: {worst.get('label')} at {worst.get('tokens_per_sec'):.1f} tokens/sec."
            )
            lines.append("")
    else:
        lines.append("## Contextual Dense State Benchmark")
        lines.append("")
        lines.append("- Contextual benchmark results not found.")
        lines.append("")

    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AGI certification workflow.")
    parser.add_argument(
        "--output-dir",
        default="certifications/agi_certification",
        help="Folder to store certification artifacts.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=30.0,
        help="Seconds per contextual profile.",
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        help="Reuse existing results instead of re-running benchmarks.",
    )
    args = parser.parse_args()

    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.reuse:
        suite_log = output_dir / "suite_run_output.txt"
        suite_args = [
            sys.executable,
            "gpia_benchmark_suite.py",
            "--sections",
            "model,s2,memory,skill,safety,conscience,e2e",
            "--guardrails",
            "on",
        ]
        run_command(suite_args, suite_log)

        contextual_log = output_dir / "contextual_run_output.txt"
        contextual_args = [
            sys.executable,
            "scripts/contextual_dense_state_benchmark.py",
            "--duration",
            str(args.duration),
            "--output",
            str(output_dir / "contextual_results.json"),
        ]
        run_command(contextual_args, contextual_log)

    suite_src = RUNS_DIR / "gpia_benchmark_results.json"
    suite_dest = output_dir / "gpia_benchmark_results.json"
    if suite_src.exists():
        suite_dest.write_text(suite_src.read_text(encoding="utf-8"), encoding="utf-8")

    contextual_results_path = output_dir / "contextual_results.json"
    if not contextual_results_path.exists():
        fallback = ROOT / "certifications/contextual_dense_state_benchmark/results.json"
        if fallback.exists():
            contextual_results_path.write_text(fallback.read_text(encoding="utf-8"), encoding="utf-8")

    suite_results = read_json(suite_dest) if suite_dest.exists() else None
    contextual_results = read_json(contextual_results_path) if contextual_results_path.exists() else None
    write_summary(output_dir, suite_results, contextual_results, args.duration)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
