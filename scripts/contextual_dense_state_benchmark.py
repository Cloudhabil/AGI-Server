from __future__ import annotations

import enum
import time
import json
import argparse
from dataclasses import dataclass
from typing import Any, Dict, List

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.gpia_server import GPIA_Server


class ContextProfile(enum.Enum):
    EDGE = "edge_local"
    PUBLIC_API = "public_api_stream"
    HIGH_REASONING = "high_reasoning"
    FAST_REASONING = "fast_reasoning"
    BALANCED = "balanced_speed"
    MOE_LIKE = "moe_efficient"
    AGI_PROFILE = "agi_profile"


PROFILE_SETTINGS: Dict[ContextProfile, Dict[str, Any]] = {
    ContextProfile.EDGE: {"prompt": "quick edge test", "max_tokens": 4, "temperature": 0.2},
    ContextProfile.PUBLIC_API: {"prompt": "streaming style response", "max_tokens": 6, "temperature": 0.7},
    ContextProfile.HIGH_REASONING: {"prompt": "provide a deep analysis of multi-factor systems", "max_tokens": 12, "temperature": 0.3},
    ContextProfile.FAST_REASONING: {"prompt": "rapid answer", "max_tokens": 3, "temperature": 0.8},
    ContextProfile.BALANCED: {"prompt": "balanced reasoning and recall of context", "max_tokens": 8, "temperature": 0.5},
    ContextProfile.MOE_LIKE: {"prompt": "model-of-experts style efficiency check", "max_tokens": 5, "temperature": 0.6},
    ContextProfile.AGI_PROFILE: {
        "prompt": "summarize an AGI system plan balancing safety, memory, and compute constraints",
        "max_tokens": 16,
        "temperature": 0.4,
    },
}

PROFILE_LABELS: Dict[ContextProfile, str] = {
    ContextProfile.AGI_PROFILE: "AGI Profile",
}


def run_profile(server: GPIA_Server, profile: ContextProfile, duration: float = 60.0) -> Dict[str, Any]:
    settings = PROFILE_SETTINGS[profile]
    start = time.monotonic()
    count = 0
    tokens = 0
    while time.monotonic() - start < duration:
        payload = {
            "session_id": f"{profile.value}-{count}",
            "prompt": settings["prompt"],
            "model": "default",
            "max_tokens": settings["max_tokens"],
            "temperature": settings["temperature"],
        }
        response = server.handle_completion(payload)
        tokens += len(response["tokens"])
        count += 1
    elapsed = time.monotonic() - start
    return {
        "profile": profile.value,
        "cycles": count,
        "tokens": tokens,
        "duration": elapsed,
        "tokens_per_sec": tokens / elapsed if elapsed else 0,
        "cycles_per_sec": count / elapsed if elapsed else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run contextual dense state benchmarks.")
    parser.add_argument("--duration", type=float, default=30.0, help="Seconds per profile.")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON output path.")
    args = parser.parse_args()

    server = GPIA_Server()
    results: List[Dict[str, Any]] = []
    for profile in ContextProfile:
        label = PROFILE_LABELS.get(profile, profile.value)
        print(f"Running {label} benchmark ({args.duration:.0f}s)...")
        result = run_profile(server, profile, duration=args.duration)
        result["label"] = label
        results.append(result)
        print(f"  cycles: {result['cycles']} tokens: {result['tokens']}  tps: {result['tokens_per_sec']:.1f}")
    print("\nSummary:")
    for result in results:
        print(
            f"{result['label']}: {result['tokens_per_sec']:.1f} tokens/sec across {result['cycles']} cycles ({result['cycles_per_sec']:.1f} cps)"
        )

    if args.output:
        output_path = args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "duration_seconds": args.duration,
            "results": results,
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
