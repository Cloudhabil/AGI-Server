#!/usr/bin/env python3
"""
Compare BrahimOnionAgent vs BOAWavelengthAgent on benchmark questions.

This script runs the same benchmark questions on both agents and compares:
- Intent detection accuracy
- Value accuracy
- Overall score

Author: Elias Oulad Brahim
"""

import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from brahims_laws import BrahimOnionAgent, BrahimAgentBuilder
from brahims_laws import BOAWavelengthAgent


@dataclass
class ComparisonResult:
    """Result comparing both agents on a question."""
    question_id: str
    question: str
    expected_intent: str

    # Original agent
    orig_intent: str
    orig_correct: bool
    orig_value: Any

    # Wavelength agent
    wave_intent: str
    wave_correct: bool
    wave_value: Any
    wave_confidence: float
    wave_resonance: float


def run_comparison(benchmark_file: str = None) -> Dict[str, Any]:
    """Run comparison between both agents."""

    benchmark_file = benchmark_file or Path(__file__).parent / "boa_benchmark_questions.json"

    with open(benchmark_file, "r", encoding="utf-8") as f:
        benchmarks = json.load(f)

    # Initialize both agents
    orig_agent = BrahimAgentBuilder().with_name("benchmark-original").build()
    wave_agent = BOAWavelengthAgent()

    results: List[ComparisonResult] = []

    orig_correct_count = 0
    wave_correct_count = 0

    print("=" * 70)
    print("AGENT COMPARISON BENCHMARK")
    print("=" * 70)
    print()

    for category in benchmarks["benchmarks"]:
        cat_name = category["category"]
        print(f"\n[{cat_name.upper()}]")
        print("-" * 50)

        for q in category["questions"]:
            q_id = q["id"]
            q_text = q["question"]
            expected_intent = q.get("expected_intent", "unknown")

            if not q_text.strip():
                continue

            # Run original agent
            try:
                orig_response = orig_agent.process(q_text)
                orig_intent = orig_response.intent.value
                orig_value = None
                if orig_response.result and isinstance(orig_response.result, dict):
                    calc = orig_response.result.get("calculation", orig_response.result)
                    orig_value = calc.get("value") or calc.get("mirror") or calc.get("result")
            except Exception as e:
                orig_intent = "error"
                orig_value = str(e)

            # Run wavelength agent
            try:
                wave_response = wave_agent.process(q_text)
                wave_intent = wave_response.intent
                wave_confidence = wave_response.confidence
                wave_resonance = wave_response.resonance
                wave_value = None
                if wave_response.result and isinstance(wave_response.result, dict):
                    wave_value = wave_response.result.get("value") or wave_response.result.get("mirror") or wave_response.result.get("result")
            except Exception as e:
                wave_intent = "error"
                wave_confidence = 0
                wave_resonance = 0
                wave_value = str(e)

            # Check correctness (case-insensitive)
            orig_correct = orig_intent.lower() == expected_intent.lower()
            wave_correct = wave_intent.lower() == expected_intent.lower()

            if orig_correct:
                orig_correct_count += 1
            if wave_correct:
                wave_correct_count += 1

            # Show result
            orig_mark = "PASS" if orig_correct else "FAIL"
            wave_mark = "PASS" if wave_correct else "FAIL"

            print(f"  {q_id}: {q_text[:35]}...")
            print(f"    Original:   {orig_mark} (intent={orig_intent})")
            print(f"    Wavelength: {wave_mark} (intent={wave_intent}, conf={wave_confidence:.1%}, res={wave_resonance:.3f})")

            results.append(ComparisonResult(
                question_id=q_id,
                question=q_text,
                expected_intent=expected_intent,
                orig_intent=orig_intent,
                orig_correct=orig_correct,
                orig_value=orig_value,
                wave_intent=wave_intent,
                wave_correct=wave_correct,
                wave_value=wave_value,
                wave_confidence=wave_confidence,
                wave_resonance=wave_resonance,
            ))

    # Summary
    total = len(results)
    orig_pct = (orig_correct_count / total * 100) if total > 0 else 0
    wave_pct = (wave_correct_count / total * 100) if total > 0 else 0

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Questions: {total}")
    print()
    print(f"Original Agent (BrahimOnionAgent):")
    print(f"  Correct: {orig_correct_count}/{total} ({orig_pct:.1f}%)")
    print()
    print(f"Wavelength Agent (BOAWavelengthAgent):")
    print(f"  Correct: {wave_correct_count}/{total} ({wave_pct:.1f}%)")

    # Get wavelength agent stats
    wave_stats = wave_agent.get_stats()
    pipeline_stats = wave_stats.get('pipeline', {})
    print(f"  Interventions: {pipeline_stats.get('interventions', pipeline_stats.get('total_interventions', 'N/A'))}")
    print(f"  Vajra Status: {pipeline_stats.get('vajra_status', 'N/A')}")
    print(f"  Mean Resonance: {wave_stats.get('mean_resonance', 0):.4f}")
    print(f"  Mean Confidence: {wave_stats.get('mean_confidence', 0):.1%}")

    # Improvement
    improvement = wave_pct - orig_pct
    if improvement > 0:
        print(f"\nImprovement: +{improvement:.1f}%")
    elif improvement < 0:
        print(f"\nRegression: {improvement:.1f}%")
    else:
        print(f"\nNo change in accuracy")

    print()
    print("=" * 70)

    return {
        "total": total,
        "original": {
            "correct": orig_correct_count,
            "percentage": orig_pct,
        },
        "wavelength": {
            "correct": wave_correct_count,
            "percentage": wave_pct,
            "stats": wave_stats,
        },
        "improvement": improvement,
    }


if __name__ == "__main__":
    result = run_comparison()

    # Exit code based on whether wavelength agent is better
    sys.exit(0 if result["improvement"] >= 0 else 1)
