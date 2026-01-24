#!/usr/bin/env python3
"""
Test Kelimutu Subnet - Three Lakes, One Magma

Compares all four architectures:
1. Original (keyword-based)
2. Wavelength (12-wave pipeline)
3. Ephemeral (MoE separate experts)
4. Kelimutu (unified magma, connected channels)

Author: Elias Oulad Brahim
"""

import sys
from pathlib import Path
import json

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from brahims_laws import BrahimOnionAgent, BrahimAgentBuilder
from brahims_laws import BOAWavelengthAgent
from brahims_laws.ml.ephemeral_subnet import BOAEphemeralAgent, generate_training_data
from brahims_laws.ml.kelimutu_subnet import BOAKelimutuAgent, KELIMUTU_LAT, KELIMUTU_LON


def load_benchmark():
    """Load benchmark questions."""
    benchmark_file = Path(__file__).parent / "boa_benchmark_questions.json"
    with open(benchmark_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    examples = []
    for cat in data["benchmarks"]:
        for q in cat["questions"]:
            if q["question"].strip():
                examples.append((q["question"], q.get("expected_intent", "unknown")))
    return examples


def test_agent(agent, name, examples):
    """Test agent accuracy."""
    correct = 0

    for text, expected in examples:
        try:
            response = agent.process(text)

            if hasattr(response, 'intent'):
                if hasattr(response.intent, 'value'):
                    actual = response.intent.value.lower()
                else:
                    actual = str(response.intent).lower()
            elif isinstance(response, dict):
                actual = response.get("intent", "unknown").lower()
            else:
                actual = "unknown"

            if actual == expected.lower():
                correct += 1

        except Exception as e:
            pass

    return correct / len(examples) if examples else 0


def main():
    print("=" * 70)
    print("FOUR-WAY ARCHITECTURE COMPARISON")
    print("=" * 70)
    print(f"\nKelimutu coordinates: {KELIMUTU_LAT}S, {KELIMUTU_LON}E")
    print(f"121.82 ~ B6 = 121 (Brahim sequence connection)")
    print()

    # Load data
    benchmark = load_benchmark()
    training_data = generate_training_data()
    print(f"Benchmark: {len(benchmark)} questions")
    print(f"Training: {len(training_data)} examples")

    # Create all agents
    print("\n" + "-" * 70)
    print("Creating agents...")
    print("-" * 70)

    original = BrahimAgentBuilder().build()
    wavelength = BOAWavelengthAgent()
    ephemeral = BOAEphemeralAgent(top_k=2)
    kelimutu = BOAKelimutuAgent()

    # Train learnable agents
    print("\nTraining Ephemeral MoE...")
    ephemeral.train(training_data, epochs=10)

    print("\nTraining Kelimutu Subnet...")
    kelimutu.train(training_data, epochs=10)

    # Test all
    print("\n" + "-" * 70)
    print("Running benchmarks...")
    print("-" * 70)

    results = [
        ("Original (keyword)", test_agent(original, "orig", benchmark)),
        ("Wavelength (12-wave)", test_agent(wavelength, "wave", benchmark)),
        ("Ephemeral (MoE)", test_agent(ephemeral, "moe", benchmark)),
        ("Kelimutu (3 lakes)", test_agent(kelimutu, "keli", benchmark)),
    ]

    # Summary
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\n{'Architecture':<25} {'Accuracy':<12} {'Improvement':<12}")
    print("-" * 50)

    baseline = results[0][1]
    for name, acc in results:
        improvement = (acc - baseline) * 100
        imp_str = f"{improvement:+.1f}%" if name != "Original (keyword)" else "-"
        print(f"{name:<25} {acc:.1%}        {imp_str}")

    # Best
    best_name, best_acc = max(results, key=lambda x: x[1])
    print(f"\nBest: {best_name} ({best_acc:.1%})")

    # Kelimutu specific stats
    print("\n" + "=" * 70)
    print("KELIMUTU LAKE STATISTICS")
    print("=" * 70)
    stats = kelimutu.get_stats()
    for lake, data in stats["subnet"]["channel_flows"].items():
        print(f"  {lake}: {data['activations']} activations, flow={data['total_flow']:.2f}")

    print("\n" + "=" * 70)
    print("The hidden structure connects all three expressions.")
    print("=" * 70)

    return best_acc


if __name__ == "__main__":
    acc = main()
    sys.exit(0 if acc > 0.65 else 1)
