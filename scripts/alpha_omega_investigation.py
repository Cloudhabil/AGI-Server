#!/usr/bin/env python3
"""
Alpha-Omega Investigation
=========================

"Where there is alpha, there is omega"

What are we missing? Let's find the complete picture.

Author: Elias Oulad Brahim
Date: 2026-01-27
"""

import sys
import math

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Constants
PHI = (1 + math.sqrt(5)) / 2
PI = math.pi

print("=" * 70)
print("  ALPHA-OMEGA INVESTIGATION")
print("  'Where there is alpha, there is omega'")
print("=" * 70)
print()

# =============================================================================
# WHAT DO WE HAVE?
# =============================================================================
print("[INVENTORY] What we currently have:")
print("-" * 50)
print()
print("  THREE PILLARS:")
print(f"    φ (phi)     = {PHI:.10f}  → Structure")
print(f"    π (pi)      = {PI:.10f}  → Form")
print(f"    ε (epsilon) = 0.01159...        → Gap/Soul")
print()
print("  ONE EQUATION:")
print("    φ^D · Θ = 2π")
print()
print("  But where is the DUALITY? The cycle? The return?")
print()

# =============================================================================
# THE ALPHA-OMEGA OF PHI
# =============================================================================
print("[DISCOVERY 1] The Alpha-Omega of φ")
print("-" * 50)
print()

alpha = PHI
omega = 1 / PHI

print(f"  α (alpha) = φ     = {alpha:.10f}")
print(f"  ω (omega) = 1/φ   = {omega:.10f}")
print()
print("  Relationships:")
print(f"    α · ω = φ · (1/φ) = {alpha * omega:.10f} = 1 (unity)")
print(f"    α - ω = φ - 1/φ   = {alpha - omega:.10f} = 1 (unity!)")
print(f"    α / ω = φ / (1/φ) = {alpha / omega:.10f} = φ² = φ + 1")
print(f"    α + ω = φ + 1/φ   = {alpha + omega:.10f} = √5")
print()
print("  INSIGHT: α - ω = 1 exactly!")
print("           The difference between beginning and end is UNITY.")
print()

# =============================================================================
# THE MISSING PARTNER
# =============================================================================
print("[DISCOVERY 2] Every constant has a partner")
print("-" * 50)
print()

# Our constants and their conjugates
constants = [
    ("φ (phi)", PHI, 1/PHI, "1/φ"),
    ("β (beta) = 1/φ³", 1/PHI**3, PHI**3, "φ³"),
    ("φ^-12", 1/PHI**12, PHI**12, "φ^12"),
    ("2π", 2*PI, 1/(2*PI), "1/2π"),
]

print("  Constant         |  Value α      |  Partner ω    |  α · ω")
print("  " + "-" * 60)
for name, val, partner, partner_name in constants:
    product = val * partner
    print(f"  {name:16} | {val:12.6f} | {partner:12.6f} | {product:.6f}")

print()
print("  Every α has an ω. Every expansion has a contraction.")
print()

# =============================================================================
# THE MISSING EQUATION
# =============================================================================
print("[DISCOVERY 3] The missing equation")
print("-" * 50)
print()

print("  We have:    φ^D · Θ = 2π     (the forward path)")
print()
print("  What about: φ^(-D) · Θ' = ?  (the return path)")
print()
print("  Let's derive...")
print()

# Forward: φ^D · Θ = 2π
# If D increases (going deeper), Θ decreases
# At D=0: φ^0 · Θ = 2π → Θ = 2π (full phase)
# At D=12: φ^12 · Θ = 2π → Θ = 2π/φ^12 (tiny phase)

print("  FORWARD PATH (α → ω): Going deeper")
print("  " + "-" * 40)
for D in [0, 3, 6, 9, 12]:
    theta = 2 * PI / (PHI ** D)
    x = theta / (2 * PI)
    print(f"    D={D:2}: Θ = 2π/φ^{D:2} = {theta:.6f} rad = {math.degrees(theta):8.3f}°")

print()
print("  RETURN PATH (ω → α): Coming back")
print("  " + "-" * 40)

# The return: what if we go from D=12 back to D=0?
# This is the INVERSE journey
# φ^(-D) · Θ = 2π/φ^12 (starting small, growing)

for D in [12, 9, 6, 3, 0]:
    # On return, we're "unwinding"
    theta = 2 * PI * (PHI ** (12 - D)) / (PHI ** 12)
    print(f"    D={D:2}: Θ = {theta:.6f} rad = {math.degrees(theta):8.3f}°")

print()

# =============================================================================
# THE COMPLETE CYCLE
# =============================================================================
print("[DISCOVERY 4] The complete cycle: α → ω → α")
print("-" * 50)
print()

print("  The system is not LINEAR, it's CIRCULAR.")
print()
print("       α (D=0)")
print("        ↓")
print("    Creation")
print("        ↓")
print("    Descent through 12 dimensions")
print("        ↓")
print("       ω (D=12) ← Unification point")
print("        ↓")
print("    Return / Rebirth")
print("        ↓")
print("       α (D=0) ← Back to beginning")
print()
print("  This is the OUROBOROS - the snake eating its tail.")
print()

# =============================================================================
# THE DUAL EQUATION
# =============================================================================
print("[DISCOVERY 5] The DUAL equation")
print("-" * 50)
print()

print("  FORWARD (Creation → Unification):")
print("    φ^D · Θ = 2π")
print("    As D↑, Θ↓ (going deeper, phase shrinks)")
print()
print("  BACKWARD (Unification → Creation):")
print("    φ^(-D) · Θ' = 2π/φ^12")
print("    As D↓, Θ'↑ (returning, phase expands)")
print()
print("  Or more symmetrically:")
print()
print("    ALPHA EQUATION:  φ^D · Θ = 2π")
print("    OMEGA EQUATION:  φ^(12-D) · Θ' = 2π")
print()

# Verify the omega equation
print("  Verification of OMEGA equation:")
for D in [0, 6, 12]:
    D_omega = 12 - D
    theta_prime = 2 * PI / (PHI ** D_omega)
    check = (PHI ** D_omega) * theta_prime
    print(f"    D={D:2}: φ^{D_omega:2} · Θ' = {check:.6f} = 2π ✓")

print()

# =============================================================================
# THE COMPLETE FRAMEWORK
# =============================================================================
print("=" * 70)
print("  THE COMPLETE FRAMEWORK: α-β-ω")
print("=" * 70)
print()

print("  We were missing the OMEGA - the return path!")
print()
print("  COMPLETE SYSTEM:")
print()
print("    α (ALPHA) = φ = 1.618...")
print("      The beginning, expansion, creation")
print("      Equation: φ^D · Θ = 2π")
print()
print("    β (BETA) = 1/φ³ = 0.236...")
print("      The balance point, security threshold")
print("      The 'waist' of the hourglass")
print()
print("    ω (OMEGA) = 1/φ = 0.618...")
print("      The end/return, contraction, completion")
print("      Equation: φ^(12-D) · Θ' = 2π")
print()
print("    ε (EPSILON) = 1.16%")
print("      The gap that allows movement between α and ω")
print("      The 'lubricant' of the cycle")
print()

# =============================================================================
# THE FUNDAMENTAL IDENTITIES
# =============================================================================
print("[IDENTITIES] The fundamental relationships")
print("-" * 50)
print()

print(f"  α - ω = φ - 1/φ = {PHI - 1/PHI:.10f} = 1")
print(f"  α · ω = φ · 1/φ = {PHI * (1/PHI):.10f} = 1")
print(f"  α + ω = φ + 1/φ = {PHI + 1/PHI:.10f} = √5")
print(f"  α² - 1 = φ² - 1 = {PHI**2 - 1:.10f} = φ")
print(f"  ω² + ω = (1/φ)² + 1/φ = {(1/PHI)**2 + 1/PHI:.10f} = 1")
print()
print("  The dance of α and ω always resolves to UNITY or √5.")
print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 70)
print("  WHAT WAS MISSING")
print("=" * 70)
print()
print("  We had:")
print("    • φ (structure)")
print("    • π (form)")
print("    • ε (gap)")
print("    • ONE equation: φ^D · Θ = 2π")
print()
print("  We were missing:")
print("    • ω = 1/φ (the return, the omega)")
print("    • The DUAL equation: φ^(12-D) · Θ' = 2π")
print("    • The CYCLE: α → ω → α")
print()
print("  THE COMPLETE PICTURE:")
print()
print("    ┌─────────────────────────────────────┐")
print("    │                                     │")
print("    │    α ════════════════════> ω        │")
print("    │    ↑    φ^D · Θ = 2π       │        │")
print("    │    │    (creation path)    │        │")
print("    │    │                       ↓        │")
print("    │    │    ε = 1.16%          │        │")
print("    │    │    (the gap)          │        │")
print("    │    │                       │        │")
print("    │    ω <════════════════════ α        │")
print("    │         φ^(12-D) · Θ' = 2π          │")
print("    │         (return path)               │")
print("    │                                     │")
print("    └─────────────────────────────────────┘")
print()
print("    α = φ   = 1.618... (beginning)")
print("    ω = 1/φ = 0.618... (end/return)")
print("    α - ω = 1 (the journey is always unity)")
print()
print("=" * 70)
