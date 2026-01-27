#!/usr/bin/env python3
"""
Validate the Unified PIO Equation using Brahim's Calculator
============================================================

THE ONE EQUATION:
    φ^D · Θ = 2π

Where:
    D(x) = -ln(x) / ln(φ)  → Dimensional position (WHERE)
    Θ(x) = 2πx             → Angular phase (WHEN)
    x = φ^(-D) = Θ/(2π)    → The bridge between structure and form

This script validates that the equation holds across:
1. All 12 Lucas dimensions
2. Brahim sequence values
3. Key mathematical constants (β, φ^-12, etc.)
4. Random samples

Author: Elias Oulad Brahim
Date: 2026-01-27
"""

import sys
import math
from pathlib import Path

# Add project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Windows encoding fix
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Import from PIO and Brahim Calculator
from src.core.pio import PHI, PI, LUCAS, LUCAS_TOTAL, PHI_PI_GAP, D, Theta, locate, PIO


def validate_unified_equation(x: float, tolerance: float = 1e-10) -> dict:
    """
    Validate: φ^D · Θ = 2π

    Args:
        x: Value in (0, 1]
        tolerance: Acceptable error

    Returns:
        Validation result dictionary
    """
    # Compute D and Θ
    d = D(x)
    theta = Theta(x)

    # The unified equation
    phi_power_d = PHI ** d
    product = phi_power_d * theta
    expected = 2 * PI

    # Error
    error = abs(product - expected)
    valid = error < tolerance

    return {
        "x": x,
        "D(x)": d,
        "Theta(x)": theta,
        "phi^D": phi_power_d,
        "phi^D * Theta": product,
        "2*pi": expected,
        "error": error,
        "valid": valid
    }


def main():
    print("=" * 70)
    print("  UNIFIED PIO EQUATION VALIDATION")
    print("  φ^D · Θ = 2π")
    print("=" * 70)
    print()

    all_valid = True
    results = []

    # =========================================================================
    # TEST 1: Lucas Dimension Thresholds (x = 1/φ^n)
    # =========================================================================
    print("[1/5] LUCAS DIMENSION THRESHOLDS (x = 1/φ^n)")
    print("-" * 50)
    print(f"{'n':>3} | {'x':>12} | {'D(x)':>8} | {'Θ(x)':>10} | {'φ^D·Θ':>12} | {'2π':>10} | {'Valid'}")
    print("-" * 70)

    for n in range(1, 13):
        x = 1 / PHI ** n
        r = validate_unified_equation(x)
        results.append(r)
        all_valid &= r["valid"]

        status = "✓" if r["valid"] else "✗"
        print(f"{n:>3} | {r['x']:>12.8f} | {r['D(x)']:>8.4f} | {r['Theta(x)']:>10.6f} | {r['phi^D * Theta']:>12.8f} | {r['2*pi']:>10.8f} | {status}")

    print()

    # =========================================================================
    # TEST 2: Brahim Constants
    # =========================================================================
    print("[2/5] BRAHIM CONSTANTS")
    print("-" * 50)

    brahim_values = {
        "β (1/φ³)": 1 / PHI**3,        # 0.236...
        "α (1/φ²)": 1 / PHI**2,        # 0.382...
        "1/φ": 1 / PHI,                 # 0.618...
        "φ^-12": 1 / PHI**12,          # 0.0031...
        "φ^-6": 1 / PHI**6,            # 0.0557...
    }

    for name, x in brahim_values.items():
        r = validate_unified_equation(x)
        results.append(r)
        all_valid &= r["valid"]
        status = "✓" if r["valid"] else "✗"
        print(f"  {name:>12}: x={r['x']:.10f} → φ^D·Θ = {r['phi^D * Theta']:.10f} [{status}]")

    print()

    # =========================================================================
    # TEST 3: Lucas Numbers as x values (normalized)
    # =========================================================================
    print("[3/5] LUCAS NUMBERS (normalized x = L(n)/840)")
    print("-" * 50)

    for n in range(12):
        x = LUCAS[n] / LUCAS_TOTAL  # Normalize to (0, 1]
        if x > 0 and x <= 1:
            r = validate_unified_equation(x)
            results.append(r)
            all_valid &= r["valid"]
            status = "✓" if r["valid"] else "✗"
            print(f"  L({n+1:>2})={LUCAS[n]:>3}: x={r['x']:.6f} → φ^D·Θ = {r['phi^D * Theta']:.10f} [{status}]")

    print()

    # =========================================================================
    # TEST 4: Phi-Pi Gap Region
    # =========================================================================
    print("[4/5] PHI-PI GAP REGION (1.16% margin)")
    print("-" * 50)

    # Test values near dimension boundaries (in the gap)
    for n in [3, 6, 9, 12]:
        base = 1 / PHI ** n
        for delta_factor in [-0.5, 0, 0.5]:
            x = base * (1 + delta_factor * PHI_PI_GAP)
            if x > 0 and x <= 1:
                r = validate_unified_equation(x)
                results.append(r)
                all_valid &= r["valid"]
                status = "✓" if r["valid"] else "✗"
                in_gap = "IN GAP" if abs(r["D(x)"] - round(r["D(x)"])) < PHI_PI_GAP else ""
                print(f"  D≈{n}, δ={delta_factor:+.1f}*gap: φ^D·Θ = {r['phi^D * Theta']:.10f} [{status}] {in_gap}")

    print()

    # =========================================================================
    # TEST 5: Random Samples
    # =========================================================================
    print("[5/5] RANDOM SAMPLES (100 values)")
    print("-" * 50)

    import random
    random.seed(42)  # Reproducible

    random_valid = 0
    for _ in range(100):
        x = random.uniform(0.001, 1.0)
        r = validate_unified_equation(x)
        results.append(r)
        if r["valid"]:
            random_valid += 1
        all_valid &= r["valid"]

    print(f"  Random samples: {random_valid}/100 valid")
    print()

    # =========================================================================
    # MATHEMATICAL PROOF
    # =========================================================================
    print("=" * 70)
    print("  MATHEMATICAL PROOF")
    print("=" * 70)
    print()
    print("  Given:")
    print("    D(x) = -ln(x) / ln(φ)")
    print("    Θ(x) = 2πx")
    print()
    print("  From D(x):")
    print("    D = -ln(x) / ln(φ)")
    print("    D · ln(φ) = -ln(x)")
    print("    ln(φ^D) = ln(1/x)")
    print("    φ^D = 1/x")
    print("    x = φ^(-D)  ... (1)")
    print()
    print("  From Θ(x):")
    print("    Θ = 2πx")
    print("    x = Θ/(2π)  ... (2)")
    print()
    print("  From (1) and (2):")
    print("    φ^(-D) = Θ/(2π)")
    print("    φ^D · Θ = 2π  ∎")
    print()

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("=" * 70)
    print("  VALIDATION SUMMARY")
    print("=" * 70)
    print()
    total = len(results)
    valid_count = sum(1 for r in results if r["valid"])
    max_error = max(r["error"] for r in results)

    print(f"  Total tests:     {total}")
    print(f"  Valid:           {valid_count}")
    print(f"  Invalid:         {total - valid_count}")
    print(f"  Max error:       {max_error:.2e}")
    print(f"  Tolerance:       1e-10")
    print()

    if all_valid:
        print("  ╔═══════════════════════════════════════════════════════╗")
        print("  ║                                                       ║")
        print("  ║   THE UNIFIED EQUATION IS MATHEMATICALLY VALID        ║")
        print("  ║                                                       ║")
        print("  ║              φ^D · Θ = 2π                             ║")
        print("  ║                                                       ║")
        print("  ║   Structure × Form = Unity                            ║")
        print("  ║                                                       ║")
        print("  ╚═══════════════════════════════════════════════════════╝")
    else:
        print("  ⚠ VALIDATION FAILED - Check results above")

    print()
    print("=" * 70)

    return all_valid


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
