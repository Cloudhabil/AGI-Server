#!/usr/bin/env python3
"""
Test Ephemeral Onion Subnet vs Original vs Wavelength Agent.

Compares three architectures:
1. BrahimOnionAgent (keyword-based)
2. BOAWavelengthAgent (12-wavelength pipeline)
3. BOAEphemeralAgent (MoE with learned routing)

Author: Elias Oulad Brahim
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from brahims_laws import BrahimOnionAgent, BrahimAgentBuilder
from brahims_laws import BOAWavelengthAgent
from brahims_laws.ml.ephemeral_subnet import BOAEphemeralAgent, generate_training_data


def load_benchmark() -> List[Tuple[str, str]]:
    """Load benchmark questions as (text, intent) pairs."""
    benchmark_file = Path(__file__).parent / "boa_benchmark_questions.json"

    with open(benchmark_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    examples = []
    for category in data["benchmarks"]:
        for q in category["questions"]:
            if q["question"].strip():
                examples.append((q["question"], q.get("expected_intent", "unknown")))

    return examples


def test_agent(agent, name: str, examples: List[Tuple[str, str]]) -> Dict[str, Any]:
    """Test an agent on examples and return accuracy stats."""
    correct = 0
    results = []

    for text, expected in examples:
        try:
            if hasattr(agent, 'process'):
                response = agent.process(text)

                # Handle different response formats
                if hasattr(response, 'intent'):
                    # Original agent returns object with .intent.value
                    if hasattr(response.intent, 'value'):
                        actual = response.intent.value.lower()
                    else:
                        actual = str(response.intent).lower()
                elif isinstance(response, dict):
                    actual = response.get("intent", "unknown").lower()
                else:
                    actual = "unknown"
            else:
                actual = "unknown"

            is_correct = actual == expected.lower()
            if is_correct:
                correct += 1

            results.append({
                "text": text[:40],
                "expected": expected,
                "actual": actual,
                "correct": is_correct
            })

        except Exception as e:
            results.append({
                "text": text[:40],
                "expected": expected,
                "actual": "error",
                "correct": False,
                "error": str(e)
            })

    accuracy = correct / len(examples) if examples else 0

    return {
        "name": name,
        "correct": correct,
        "total": len(examples),
        "accuracy": accuracy,
        "results": results
    }


def main():
    print("=" * 70)
    print("THREE-WAY AGENT COMPARISON")
    print("=" * 70)

    # Load benchmark
    benchmark_examples = load_benchmark()
    print(f"\nLoaded {len(benchmark_examples)} benchmark questions")

    # Create agents
    print("\n[1] Creating BrahimOnionAgent (original)...")
    original_agent = BrahimAgentBuilder().with_name("original").build()

    print("[2] Creating BOAWavelengthAgent (12-wavelength)...")
    wavelength_agent = BOAWavelengthAgent()

    print("[3] Creating BOAEphemeralAgent (MoE)...")
    ephemeral_agent = BOAEphemeralAgent(top_k=2, temperature=0.5)

    # Train ephemeral agent on training data
    print("\n" + "-" * 70)
    print("Training Ephemeral MoE Agent...")
    print("-" * 70)

    training_data = generate_training_data()
    train_stats = ephemeral_agent.train(training_data, epochs=10)
    print(f"Training accuracy: {train_stats['final_accuracy']:.1%}")

    # Test all three agents
    print("\n" + "-" * 70)
    print("Running Benchmark Tests...")
    print("-" * 70)

    print("\n[1] Testing Original Agent...")
    original_results = test_agent(original_agent, "Original (keyword)", benchmark_examples)

    print("[2] Testing Wavelength Agent...")
    wavelength_results = test_agent(wavelength_agent, "Wavelength (12-wave)", benchmark_examples)

    print("[3] Testing Ephemeral MoE Agent...")
    ephemeral_results = test_agent(ephemeral_agent, "Ephemeral (MoE)", benchmark_examples)

    # Summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    print(f"\n{'Agent':<25} {'Correct':<12} {'Accuracy':<12}")
    print("-" * 50)

    for result in [original_results, wavelength_results, ephemeral_results]:
        print(f"{result['name']:<25} {result['correct']}/{result['total']:<8} {result['accuracy']:.1%}")

    # Calculate improvements
    baseline = original_results['accuracy']
    wave_improvement = (wavelength_results['accuracy'] - baseline) * 100
    moe_improvement = (ephemeral_results['accuracy'] - baseline) * 100

    print("\n" + "-" * 50)
    print(f"Wavelength vs Original: {wave_improvement:+.1f}%")
    print(f"Ephemeral MoE vs Original: {moe_improvement:+.1f}%")

    # Best agent
    best = max([original_results, wavelength_results, ephemeral_results],
               key=lambda x: x['accuracy'])
    print(f"\nBest Agent: {best['name']} ({best['accuracy']:.1%})")

    # Show failed cases for MoE agent
    print("\n" + "=" * 70)
    print("EPHEMERAL MoE - FAILED CASES")
    print("=" * 70)

    failed = [r for r in ephemeral_results['results'] if not r['correct']]
    for f in failed[:10]:  # Show first 10
        print(f"  [{f['expected']}] {f['text']}...")
        print(f"    Got: {f['actual']}")

    print(f"\n  ... {len(failed)} total failures")

    # Expert usage distribution
    print("\n" + "=" * 70)
    print("EXPERT USAGE DISTRIBUTION")
    print("=" * 70)
    stats = ephemeral_agent.get_stats()
    for expert, count in stats['subnet']['expert_usage'].items():
        bar = "#" * int(count / 5)
        print(f"  {expert:<12} {count:>4} {bar}")

    print("\n" + "=" * 70)

    return ephemeral_results['accuracy']


if __name__ == "__main__":
    accuracy = main()
    # Exit 0 if accuracy > 70%
    sys.exit(0 if accuracy > 0.70 else 1)
