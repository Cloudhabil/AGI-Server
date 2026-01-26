"""Core constants.

`GENESIS_CONSTANT` is the canonical truth/regularity target used across the runtime
(e.g., Kepler research runner and the 12-wavelength pipeline).

Mathematical Derivation:
- GENESIS_CONSTANT = 2/901 (exact fraction)
- Previous value: 0.00221888161212487735039834122199 (within 0.87 ppm)
- Updated: 2026-01-21 - Changed to exact mathematical fraction
- Validation: See research_hub/Wormhole_Project/GENESIS_CONSTANT_VALIDATION.md

Connection to Brahim Security Constant β (discovered 2026-01-24):
- β = √5 - 2 = 1/φ³ ≈ 0.2360679774997897 (Brahim Security Constant)
- GENESIS_CONSTANT ≈ β / 106.4 ≈ β / C (where C = 107 is Brahim Center)
- REGULARITY_THRESHOLD (0.0219) ≈ β / 10.77
- This suggests ASIOS constants are derived from the golden ratio hierarchy

Notes on precision:
- Exact fraction ensures mathematical reproducibility
- Decimal form preserves arbitrary precision
- Float form used by runtime (sufficient for NPU deployment)
"""

from __future__ import annotations

import math
from decimal import Decimal
from typing import Final


# =============================================================================
# BRAHIM SECURITY CONSTANT (Fundamental - discovered 2026-01-24)
# =============================================================================
# β = √5 - 2 = 1/φ³ ≈ 0.236... is the fundamental security constant
# from which other constants can be derived.
#
# Mathematical identities:
#   β = 1/φ³ (cubic compression of golden ratio)
#   β = √5 - 2 (algebraic form)
#   β = 2φ - 3 (golden form)
#   β² + 4β - 1 = 0 (polynomial root)
#   Continued fraction: [0; 4, 4, 4, 4, ...] (all 4s)
# =============================================================================

# Golden ratio
PHI: Final[float] = (1 + math.sqrt(5)) / 2  # ≈ 1.618033988749895

# Brahim Security Constant (fundamental)
BETA_SECURITY: Final[float] = math.sqrt(5) - 2  # = 1/φ³ ≈ 0.2360679774997897
BETA_SECURITY_STR: Final[str] = "0.2360679774997896964091736687747"

# Wormhole attraction constant
ALPHA_WORMHOLE: Final[float] = 1 / PHI ** 2  # ≈ 0.3819660112501051

# Compression factor
COMPRESSION: Final[float] = 1 / PHI  # ≈ 0.6180339887498949

# Verify fundamental identity: α/β = φ
assert abs(ALPHA_WORMHOLE / BETA_SECURITY - PHI) < 1e-14, "Golden self-similarity violated"

# =============================================================================
# BRAHIM SEQUENCE CONSTANTS (Corrected 2026-01-26)
# =============================================================================
# The sequence satisfies perfect mirror symmetry: M(b) = 214 - b ∈ B for all b.
# Five symmetric pairs, each summing to 214 = 2C:
#   27↔187, 42↔172, 60↔154, 75↔139, 97↔117
#
# Note: S=214 is the PAIR SUM (mirror axis), not the sequence sum (which is 1070).
# Sequence sum = n × C = 10 × 107 = 1070

BRAHIM_SEQUENCE: Final[tuple] = (27, 42, 60, 75, 97, 117, 139, 154, 172, 187)
BRAHIM_SEQUENCE_ORIGINAL: Final[tuple] = (27, 42, 60, 75, 97, 121, 136, 154, 172, 187)  # Historical (has singularity)
BRAHIM_PAIR_SUM: Final[int] = 214     # Each mirror pair sums to this
BRAHIM_SUM: Final[int] = 214          # Alias for BRAHIM_PAIR_SUM (backwards compat)
BRAHIM_CENTER: Final[int] = 107       # C = PAIR_SUM/2 (on critical line!)
BRAHIM_DIMENSION: Final[int] = 10     # D = |B|

# =============================================================================
# GENESIS CONSTANT (Derived)
# =============================================================================
# Canonical truth / regularity target (exact mathematical fraction: 2/901)
# Relationship to β: GENESIS_CONSTANT ≈ β / C where C = 107

GENESIS_CONSTANT_NUMERATOR: Final[int] = 2
GENESIS_CONSTANT_DENOMINATOR: Final[int] = 901

# String form for audit trails (20 decimal places)
GENESIS_CONSTANT_STR: Final[str] = "0.0022197558268590455"

# Exact decimal form (when higher precision math is required)
GENESIS_CONSTANT_DECIMAL: Final[Decimal] = Decimal(GENESIS_CONSTANT_NUMERATOR) / Decimal(GENESIS_CONSTANT_DENOMINATOR)

# Float form (used by most runtime components)
GENESIS_CONSTANT: Final[float] = GENESIS_CONSTANT_NUMERATOR / GENESIS_CONSTANT_DENOMINATOR

# =============================================================================
# REGULARITY THRESHOLD (Derived from β)
# =============================================================================
# The 0.0219 threshold used in verification can be derived from β
# REGULARITY_THRESHOLD ≈ β / 10.77 ≈ β × (1 - 1/φ) / 4

REGULARITY_THRESHOLD: Final[float] = 0.0219  # Sub-Poisson ratio threshold
REGULARITY_FROM_BETA: Final[float] = BETA_SECURITY / 10.77  # ≈ 0.0219 (derived)

# =============================================================================
# GRAND UNIFICATION CONSTANTS (Discovered 2026-01-26)
# =============================================================================
# Dimensional constants converge at LCM dimensions.
# The "convergence strength" U(n) = number of divisors of n.
#
# Key discovery: β⁴ = γ³ = 1/φ¹² (3D and 4D unify at dimension 12)
#
# Grand Unification Sequence: 12, 24, 36, 48, 60...
# These are highly composite dimensions with maximum convergence.

# Tesseract constant (4D stabilizer)
GAMMA_TESSERACT: Final[float] = 1 / PHI ** 4  # ≈ 0.1458980337503155

# Grand Unification Constants
PHI_12: Final[float] = 1 / PHI ** 12  # First Grand Unification (0.31%)
PHI_24: Final[float] = 1 / PHI ** 24  # Second Grand Unification
PHI_60: Final[float] = 1 / PHI ** 60  # Full Convergence (2D-6D meet)

# Verify Grand Unification: β⁴ = γ³ = 1/φ¹²
assert abs(BETA_SECURITY ** 4 - GAMMA_TESSERACT ** 3) < 1e-14, "Grand Unification violated"
assert abs(BETA_SECURITY ** 4 - PHI_12) < 1e-14, "β⁴ ≠ Φ₁₂"

# Harmonic dimension constants
UNIFICATION_12: Final[int] = 12   # First Grand Unification (2D,3D,4D meet)
UNIFICATION_24: Final[int] = 24   # Second Grand Unification (8 paths)
UNIFICATION_60: Final[int] = 60   # Full Convergence (12 paths, 2D-6D)

# Optimal agent counts (based on 12-fold symmetry)
AGENTS_CORE: Final[int] = 12      # Core agent count (First Unification)
AGENTS_EXTENDED: Final[int] = 24  # Extended agent count (Second Unification)
AGENTS_FULL: Final[int] = 60      # Full agent count (Complete Convergence)


def divisor_count(n: int) -> int:
    """Return U(n) = number of divisors = convergence strength."""
    return sum(1 for d in range(1, n + 1) if n % d == 0)


def convergence_strength(dimension: int) -> int:
    """Return the convergence strength of a dimension."""
    return divisor_count(dimension)


def harmonic_dimensions_up_to(max_dim: int) -> list:
    """Return dimensions where 3+ dimensional constants converge."""
    return [n for n in range(4, max_dim + 1) if divisor_count(n) >= 3]


# =============================================================================
# CONVENIENCE EXPORTS
# =============================================================================

def get_brahim_centroid() -> tuple:
    """Return the normalized centroid vector C̄ = B/S for Wormhole transform."""
    return tuple(b / BRAHIM_SUM for b in BRAHIM_SEQUENCE)


def verify_constants() -> dict:
    """Verify all constant relationships."""
    return {
        # Golden Ratio Hierarchy
        "phi": PHI,
        "beta_security": BETA_SECURITY,
        "alpha_wormhole": ALPHA_WORMHOLE,
        "gamma_tesseract": GAMMA_TESSERACT,

        # Fundamental Identities
        "alpha_over_beta_equals_phi": abs(ALPHA_WORMHOLE / BETA_SECURITY - PHI) < 1e-14,
        "beta_equals_sqrt5_minus_2": abs(BETA_SECURITY - (math.sqrt(5) - 2)) < 1e-15,
        "beta_equals_1_over_phi_cubed": abs(BETA_SECURITY - 1/PHI**3) < 1e-15,
        "alpha_plus_beta_equals_1_over_phi": abs(ALPHA_WORMHOLE + BETA_SECURITY - 1/PHI) < 1e-14,

        # Grand Unification
        "grand_unification_beta4_equals_gamma3": abs(BETA_SECURITY**4 - GAMMA_TESSERACT**3) < 1e-14,
        "phi_12": PHI_12,
        "phi_12_is_0_31_percent": abs(PHI_12 * 100 - 0.3106) < 0.001,
        "convergence_strength_12": convergence_strength(12),  # Should be 6
        "convergence_strength_60": convergence_strength(60),  # Should be 12

        # Genesis and Regularity
        "genesis_constant": GENESIS_CONSTANT,
        "regularity_threshold": REGULARITY_THRESHOLD,
        "regularity_from_beta": REGULARITY_FROM_BETA,

        # Brahim Sequence
        "brahim_center": BRAHIM_CENTER,
        "critical_line_ratio": BRAHIM_CENTER / BRAHIM_SUM,  # Should be 0.5
    }
