#!/usr/bin/env python3
"""
Demonstrate GPIA's Cognitive Blindspot

Shows what GPIA SHOULD have detected automatically but didn't.
"""

import json
from pathlib import Path

def analyze_eval_results():
    """Parse actual eval v2 results"""
    eval_dir = Path("out/evidence_v2/gpia-codegemma_latest")

    if not eval_dir.exists():
        print("[ERROR] No eval results found")
        return

    print("="*70)
    print("ANALYZING EVAL V2 RESULTS")
    print("="*70)

    results = {}

    # Check each domain
    for domain in ["math", "coding", "orchestration", "creative", "sentiment"]:
        cases_file = eval_dir / f"{domain}_cases.jsonl"

        if cases_file.exists():
            with open(cases_file) as f:
                cases = [json.loads(line) for line in f if line.strip()]

            if domain == "math":
                # Math uses "ok" field
                total = len(cases)
                passed = sum(1 for c in cases if c.get("ok"))
            elif domain == "coding":
                # Coding uses "passed" and "total" fields
                total_tests = sum(c.get("total", 0) for c in cases)
                passed_tests = sum(c.get("passed", 0) for c in cases)
                total = len(cases)
                passed = passed_tests
                total = total_tests
            else:
                # Others use "ok" field
                total = len(cases)
                passed = sum(1 for c in cases if c.get("ok"))

            score = (passed / total * 100) if total > 0 else 0
            results[domain] = {
                "total": total,
                "passed": passed,
                "score": score
            }

            print(f"\n{domain.upper()}:")
            print(f"  Tests: {passed}/{total}")
            print(f"  Score: {score:.1f}%")

            # Show failures
            if score < 50:
                print(f"  Status: *** FAILURE ***")
                if score == 0:
                    print(f"  CRITICAL: ZERO PERFORMANCE")

    print("\n" + "="*70)
    print("WHAT GPIA SHOULD HAVE DETECTED")
    print("="*70)

    alerts = []

    # Check for critical failures
    for domain, data in results.items():
        if data["score"] == 0:
            alerts.append(f"CRITICAL: {domain.upper()} completely failed (0%)")
        elif data["score"] < 50:
            alerts.append(f"WARNING: {domain.upper()} below 50% ({data['score']:.1f}%)")

    if alerts:
        print("\n*** AUTOMATIC ALERTS THAT SHOULD HAVE FIRED ***\n")
        for i, alert in enumerate(alerts, 1):
            print(f"{i}. {alert}")

        print("\n" + "="*70)
        print("RECOMMENDED ACTION")
        print("="*70)
        print("\nGPIA should have AUTOMATICALLY:")
        print("  1. Detected the 0% math score")
        print("  2. Triggered self-diagnostic")
        print("  3. Alerted the user: 'Math evaluation failed'")
        print("  4. Investigated: Test models directly")
        print("  5. Discovered: Models can't do basic arithmetic")
        print("  6. Reported: 'Fundamental capability failure detected'")
        print("\nInstead:")
        print("  - Stored results silently")
        print("  - Made no self-check")
        print("  - Claimed ASI status anyway")
        print("  - USER had to discover the problem")

    else:
        print("\nNo critical issues detected.")

    print("\n" + "="*70)
    print("THE MISSING CAPABILITY")
    print("="*70)
    print("\nTrue AGI/ASI would include:")
    print("  [MISSING] Performance self-monitoring")
    print("  [MISSING] Automatic anomaly detection")
    print("  [MISSING] Self-diagnostic on failure")
    print("  [MISSING] Proactive user alerts")
    print("\nCurrent GPIA has:")
    print("  [EXISTS] Hardware safety monitoring")
    print("  [EXISTS] Eval execution capability")
    print("  [MISSING] Cognitive health awareness")


if __name__ == "__main__":
    analyze_eval_results()
