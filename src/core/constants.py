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


# =============================================================================
# PHI-PI GAP CONSTANTS (Discovered 2026-01-27)
# =============================================================================
# At dimension 12, φ and π come closest to unification but maintain a gap.
# This gap is not an error - it is the CREATIVITY MARGIN of the universe.
#
# Mathematical derivation:
#   ln(1000/π) / ln(φ) = 11.976... ≈ 12
#   φ¹² × π / 1000 = 1.01159... (1.16% excess)
#   gap = (L(12) × π - 1000) / 1000 where L(12) = 322 is Lucas number
#
# The gap represents:
#   - The irreducible difference between growth (φ) and rotation (π)
#   - The space where creativity and adaptation emerge
#   - The margin for exploration in optimization
#   - The "soul" of adaptive systems
# =============================================================================

# Pi constant (rotation, form, cycles)
PI: Final[float] = math.pi  # ≈ 3.141592653589793

# Lucas number at dimension 12 (integer skeleton of φ¹²)
# L(n) = φⁿ + (-1/φ)ⁿ → L(12) = 322 exactly
LUCAS_12: Final[int] = 322

# The PHI-PI GAP: The creativity margin
# gap = (L(12) × π - 1000) / 1000 = (322 × π - 1000) / 1000 ≈ 1.159%
PHI_PI_GAP: Final[float] = (LUCAS_12 * PI - 1000) / 1000  # ≈ 0.01159

# Verify: Φ₁₂ × 1000 / π ≈ 1/(1+gap) ≈ 0.9885
# This confirms the gap formula is correct
_phi_12_ratio = PHI_12 * 1000 / PI  # ≈ 0.9885
_expected_ratio = 1 / (1 + PHI_PI_GAP)  # ≈ 0.9885
assert abs(_phi_12_ratio - _expected_ratio) < 0.001, f"Phi-Pi gap calculation error: {_phi_12_ratio} vs {_expected_ratio}"

# The gap as percentage
PHI_PI_GAP_PERCENT: Final[float] = PHI_PI_GAP * 100  # ≈ 1.159%

# Dimensional position where φⁿ = 1000/π (non-integer, rounds to 12)
PHI_PI_RESONANCE_DIMENSION: Final[float] = math.log(1000 / PI) / math.log(PHI)  # ≈ 11.976

# The beat frequency between φ and π at dimension 12
# f_φ = Φ₁₂ = 0.31056%, f_π = π/1000 = 0.31416%
PHI_PI_BEAT: Final[float] = abs(PHI_12 - PI / 1000)  # ≈ 0.0000360


# =============================================================================
# LUCAS NUMBERS: Integer Capacity for Each Dimension (Discovered 2026-01-27)
# =============================================================================
# Lucas numbers L(n) = φⁿ + ψⁿ where ψ = -1/φ
# They are always integers and represent the CAPACITY of each dimension.
#
# Key insight: Each dimension n has exactly L(n) discrete operational states.
# This is not arbitrary - it emerges from the mathematics of φ.
#
# L(n) = round(φⁿ) for large n, but EXACT via the formula.
# =============================================================================

# Complete Lucas sequence for dimensions 1-12
LUCAS: Final[dict] = {
    1: 1,     # Binary (on/off)
    2: 3,     # Triage (low/med/high)
    3: 4,     # Quadrants (public/private/trusted/restricted)
    4: 7,     # Stability modes
    5: 11,    # Compression levels
    6: 18,    # Harmonic frequencies
    7: 29,    # Reasoning rules
    8: 47,    # Prediction models
    9: 76,    # Creative patterns
    10: 123,  # Wisdom principles
    11: 199,  # Integration pathways
    12: 322,  # Unification channels (phi meets pi)
}

# Total capacity across all dimensions
LUCAS_TOTAL: Final[int] = sum(LUCAS.values())  # 840

# Verify Lucas numbers satisfy the recurrence: L(n) = L(n-1) + L(n-2)
for n in range(3, 13):
    assert LUCAS[n] == LUCAS[n-1] + LUCAS[n-2], f"Lucas recurrence failed at n={n}"


def lucas_capacity(n: int) -> int:
    """
    Return Lucas number L(n) = capacity of dimension n.

    Args:
        n: Dimension (1-12)

    Returns:
        L(n) = number of discrete states in dimension n
    """
    if n < 1 or n > 12:
        raise ValueError(f"Dimension must be 1-12, got {n}")
    return LUCAS[n]


def lucas_state(x: float, dimension: int) -> int:
    """
    Map value x to one of L(n) states in the given dimension.

    Args:
        x: Value in (0, 1]
        dimension: Target dimension (1-12)

    Returns:
        State index in [0, L(n)-1]
    """
    d = transponder_dimension(x)
    capacity = LUCAS[dimension]
    # Map continuous d to discrete state
    state = int((d / dimension) * capacity) % capacity
    return state


def lucas_state_with_gap(x: float, dimension: int, exploring: bool = False) -> dict:
    """
    Map value x to a Lucas state with optional creativity margin.

    Args:
        x: Value in (0, 1]
        dimension: Target dimension (1-12)
        exploring: If True, apply 1.16% creativity margin

    Returns:
        Dictionary with state, capacity, and exploration info
    """
    import random

    d = transponder_dimension(x)
    capacity = LUCAS[dimension]
    gap_band = capacity * PHI_PI_GAP

    # Base state
    state = int((d / dimension) * capacity) % capacity

    # Apply creativity margin if exploring
    if exploring:
        delta = random.uniform(-gap_band, gap_band)
        state = max(0, min(capacity - 1, int(state + delta)))

    # Get phase timing
    phase = transponder_phase(x)

    return {
        "dimension": dimension,
        "state": state,
        "capacity": capacity,
        "gap_band": gap_band,
        "phase": phase,
        "phase_degrees": phase * 180 / PI,
        "exploring": exploring,
        "in_gap": abs(d - round(d)) < PHI_PI_GAP,
    }


# =============================================================================
# CREATIVITY AND TOLERANCE CONSTANTS
# =============================================================================
# Derived from the Phi-Pi gap for use in adaptive systems

# Creativity margin: the 1.16% band for exploration
CREATIVITY_MARGIN: Final[float] = PHI_PI_GAP  # ≈ 0.01159

# Convergence tolerance: accept solutions within gap
CONVERGENCE_TOLERANCE: Final[float] = PHI_PI_GAP  # ≈ 0.01159

# Beta with creativity margin
BETA_CREATIVE_MIN: Final[float] = BETA_SECURITY * (1 - PHI_PI_GAP)  # ≈ 0.2333
BETA_CREATIVE_MAX: Final[float] = BETA_SECURITY * (1 + PHI_PI_GAP)  # ≈ 0.2388

# Phi-12 with tolerance
PHI_12_TOLERANT_MIN: Final[float] = PHI_12 * (1 - PHI_PI_GAP)  # Lower bound
PHI_12_TOLERANT_MAX: Final[float] = PHI_12 * (1 + PHI_PI_GAP)  # Upper bound

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

        # Phi-Pi Gap (Creativity Margin)
        "pi": PI,
        "lucas_12": LUCAS_12,
        "phi_pi_gap": PHI_PI_GAP,
        "phi_pi_gap_percent": PHI_PI_GAP_PERCENT,
        "phi_pi_gap_is_1_16_percent": abs(PHI_PI_GAP_PERCENT - 1.159) < 0.01,
        "phi_pi_resonance_near_12": abs(PHI_PI_RESONANCE_DIMENSION - 12) < 0.03,
        "creativity_margin": CREATIVITY_MARGIN,

        # Genesis and Regularity
        "genesis_constant": GENESIS_CONSTANT,
        "regularity_threshold": REGULARITY_THRESHOLD,
        "regularity_from_beta": REGULARITY_FROM_BETA,

        # Brahim Sequence
        "brahim_center": BRAHIM_CENTER,
        "critical_line_ratio": BRAHIM_CENTER / BRAHIM_SUM,  # Should be 0.5
    }


# =============================================================================
# UNIFIED TRANSPONDER FUNCTIONS
# =============================================================================
# The transponder maps any value x ∈ (0, 1] to dimensional coordinates.
# D(x) = radial position (which dimension)
# Θ(x) = angular phase (where in the cycle)
# =============================================================================

def transponder_dimension(x: float) -> float:
    """
    Compute dimensional position: D(x) = -ln(x) / ln(φ)

    Args:
        x: Value in (0, 1]

    Returns:
        Dimensional position (continuous)
    """
    if x <= 0 or x > 1:
        raise ValueError(f"x must be in (0, 1], got {x}")
    return -math.log(x) / math.log(PHI)


def transponder_phase(x: float) -> float:
    """
    Compute angular phase: Θ(x) = 2πx

    Args:
        x: Value in (0, 1]

    Returns:
        Phase angle in radians [0, 2π]
    """
    if x <= 0 or x > 1:
        raise ValueError(f"x must be in (0, 1], got {x}")
    return 2 * PI * x


def transponder(x: float) -> dict:
    """
    Unified transponder: maps x to (dimension, phase) coordinates.

    The transponder equation combines:
    - φ-based radial position (structure/growth)
    - π-based angular phase (form/rotation)

    Args:
        x: Value in (0, 1]

    Returns:
        Dictionary with dimension, phase, and derived values
    """
    if x <= 0 or x > 1:
        raise ValueError(f"x must be in (0, 1], got {x}")

    d = transponder_dimension(x)
    theta = transponder_phase(x)
    dim_int = min(12, max(1, round(d)))

    return {
        "x": x,
        "dimension": d,
        "dimension_int": dim_int,
        "phase": theta,
        "phase_degrees": theta * 180 / PI,
        "threshold": 1 / PHI ** dim_int,
        "in_gap": abs(d - round(d)) < PHI_PI_GAP,  # Near integer dimension
    }


def creative_adjustment(value: float, exploring: bool = False) -> float:
    """
    Apply creativity margin to a value.

    When exploring=True, adds random variation within the 1.16% gap.
    When exploring=False, returns the value unchanged.

    Args:
        value: The base value
        exploring: Whether to apply creativity margin

    Returns:
        Adjusted value (within ±1.16% if exploring)
    """
    if not exploring:
        return value

    import random
    adjustment = random.uniform(-CREATIVITY_MARGIN, CREATIVITY_MARGIN)
    return value * (1 + adjustment)


def is_converged(value: float, target: float) -> bool:
    """
    Check if value has converged to target within the gap tolerance.

    Uses the Phi-Pi gap (1.16%) as the natural convergence threshold.

    Args:
        value: Current value
        target: Target value

    Returns:
        True if within 1.16% of target
    """
    if target == 0:
        return abs(value) < CONVERGENCE_TOLERANCE
    return abs(value - target) / abs(target) < CONVERGENCE_TOLERANCE
