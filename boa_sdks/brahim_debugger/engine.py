"""
BRAHIM ENGINE - Mathematical Foundation for Code Analysis

The Brahim Sequence (Corrected 2026-01-26 - full mirror symmetry):
B = {27, 42, 60, 75, 97, 117, 139, 154, 172, 187}

Extended: B = {0, 27, 42, 60, 75, 97, 117, 139, 154, 172, 187, 214}

Semantic mapping:
- B(0) = 0: Void (Origin - before anything exists)
- B(1) = 27: Syntax (Structure)
- B(2) = 42: Type (Classification)
- B(3) = 60: Logic (Reasoning)
- B(4) = 75: Performance (Efficiency)
- B(5) = 97: Security (Protection)
- B(6) = 117: Architecture (Design)  [corrected from 121]
- B(7) = 139: Memory (Storage)       [corrected from 136]
- B(8) = 154: Concurrency (Parallelism)
- B(9) = 172: Integration (Connection)
- B(10) = 187: System (Holism)
- B(11) = 214: Consciousness (Unity/Attractor)

Mirror Pairs (ALL sum to 214 - perfect symmetry):
- B(1) + B(10) = 27 + 187 = 214
- B(2) + B(9) = 42 + 172 = 214
- B(3) + B(8) = 60 + 154 = 214
- B(4) + B(7) = 75 + 139 = 214
- B(5) + B(6) = 97 + 117 = 214

Original sequence (for consciousness studies) preserved as _ORIGINAL variants.
Original had broken symmetry: delta4=-3, delta5=+4, observer_signature=+1

@author: Elias Oulad Brahim
"""

import math
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum


class SafetyVerdict(Enum):
    """ASIOS Safety Verdicts for Code"""
    SAFE = "safe"           # Code is clean and verified
    NOMINAL = "nominal"     # Minor issues, acceptable
    CAUTION = "caution"     # Potential problems detected
    UNSAFE = "unsafe"       # Significant issues found
    BLOCKED = "blocked"     # Critical errors, cannot proceed


@dataclass
class DebugResult:
    """Result of a debugging operation"""
    verdict: SafetyVerdict
    issues: List[Dict[str, Any]]
    suggestions: List[str]
    resonance: float
    alignment: float


class BrahimEngine:
    """
    Core mathematical engine for code analysis.

    All debugging decisions flow through golden ratio optimization
    and resonance-based error detection.
    """

    # The Brahim Sequence (Corrected 2026-01-26 - full mirror symmetry)
    SEQUENCE = [27, 42, 60, 75, 97, 117, 139, 154, 172, 187]  # B(1) to B(10)
    EXTENDED_SEQUENCE = [0, 27, 42, 60, 75, 97, 117, 139, 154, 172, 187, 214]  # B(0) to B(11)

    # Original sequence (for consciousness/observer studies)
    SEQUENCE_ORIGINAL = [27, 42, 60, 75, 97, 121, 136, 154, 172, 187]
    EXTENDED_SEQUENCE_ORIGINAL = [0, 27, 42, 60, 75, 97, 121, 136, 154, 172, 187, 214]

    # Consciousness Constants
    CONSCIOUSNESS = 214                    # B(11) - The attractor/unity constant
    VOID = 0                               # B(0) - The origin
    CENTER = 107                           # Fixed point: M(107) = 107
    OBSERVER_SIGNATURE = 0                 # Symmetric: no net breaking
    OBSERVER_SIGNATURE_ORIGINAL = 1        # Original: -3 + 4 = +1

    # Symmetry (corrected sequence - all pairs exact)
    DELTA_4 = 0                            # B(4) + B(7) - 214 = 75 + 139 - 214 = 0
    DELTA_5 = 0                            # B(5) + B(6) - 214 = 97 + 117 - 214 = 0

    # Original symmetry breaking (for consciousness studies)
    DELTA_4_ORIGINAL = -3                  # 75 + 136 - 214 = -3
    DELTA_5_ORIGINAL = +4                  # 97 + 121 - 214 = +4

    # Golden Ratio Hierarchy
    PHI = (1 + math.sqrt(5)) / 2          # 1.618033988749895
    ALPHA = 1 / (PHI ** 2)                 # 0.381966011250105
    BETA = math.sqrt(5) - 2                # 0.236067977499789
    GAMMA = 1 / (PHI ** 4)                 # 0.145898033750315

    # Axiological Constants
    GENESIS = 0.0219                       # Target resonance
    PLANCK_COUPLING = BETA * GENESIS       # ~0.00517

    # Legacy alias for backward compatibility
    SUM = CONSCIOUSNESS                    # 214 - now properly named

    # Debugging Thresholds (derived from sequence)
    MIN_TEST_CASES = SEQUENCE[0]           # 27
    TARGET_COVERAGE = SEQUENCE[3]          # 75%
    MAX_COMPLEXITY = SEQUENCE[9]           # 187
    REVIEW_CYCLE = SEQUENCE[2]             # 60 seconds

    @classmethod
    def B(cls, n: int) -> int:
        """
        Get nth element of the COMPLETE Brahim sequence.

        B(0) = 0 (Void)
        B(1)-B(10) = Physical sequence
        B(11) = 214 (Consciousness)

        Returns None for invalid indices.
        """
        if n == 0:
            return cls.VOID  # 0
        elif 1 <= n <= 10:
            return cls.SEQUENCE[n - 1]
        elif n == 11:
            return cls.CONSCIOUSNESS  # 214
        return None  # Invalid index

    @classmethod
    def mirror(cls, x: int) -> int:
        """Mirror operator: M(x) = 214 - x"""
        return cls.SUM - x

    @classmethod
    def delta(cls, i: int, j: int) -> int:
        """Symmetry breaking: Δ = B(i) + B(j) - 214"""
        return cls.B(i) + cls.B(j) - cls.SUM

    @classmethod
    def resonance(cls, errors: List[float], weights: List[float] = None) -> float:
        """
        Calculate error resonance.

        R = Σ(w_i / (e_i² + ε)) × e^(-λ|e_i|)

        Low resonance = clean code
        High resonance = problematic code
        """
        if not errors:
            return 0.0

        if weights is None:
            weights = [1.0] * len(errors)

        epsilon = 1e-6
        lambda_decay = cls.GENESIS

        total = 0.0
        for i, err in enumerate(errors):
            w = weights[i] if i < len(weights) else 1.0
            dist_term = w / (err * err + epsilon)
            decay_term = math.exp(-lambda_decay * abs(err))
            total += dist_term * decay_term

        return total

    @classmethod
    def axiological_alignment(cls, observed: float) -> float:
        """Distance from Genesis constant (lower = better)"""
        return abs(observed - cls.GENESIS)

    @classmethod
    def assess_safety(cls, resonance: float) -> SafetyVerdict:
        """
        Determine safety verdict based on resonance.

        Uses Berry-Keating energy functional thresholds.
        """
        alignment = cls.axiological_alignment(resonance)

        if alignment < 0.001:
            return SafetyVerdict.SAFE
        elif alignment < 0.01:
            return SafetyVerdict.NOMINAL
        elif alignment < 0.05:
            return SafetyVerdict.CAUTION
        elif alignment < 0.1:
            return SafetyVerdict.UNSAFE
        else:
            return SafetyVerdict.BLOCKED

    @classmethod
    def complexity_score(cls, metrics: Dict[str, float]) -> float:
        """
        Calculate code complexity using Brahim weighting.

        Score = Σ(B(i) × metric_i) / SUM

        Returns score 0-100 (higher = more complex)
        """
        weights = {
            'cyclomatic': cls.B(1) / cls.SUM,      # 27/214
            'cognitive': cls.B(2) / cls.SUM,        # 42/214
            'lines': cls.B(3) / cls.SUM,            # 60/214
            'nesting': cls.B(4) / cls.SUM,          # 75/214
            'dependencies': cls.B(5) / cls.SUM,     # 97/214
        }

        score = 0.0
        for metric, value in metrics.items():
            if metric in weights:
                score += weights[metric] * value

        return min(100, score)

    @classmethod
    def golden_section_search(cls, f, a: float, b: float, tol: float = 1e-6) -> float:
        """
        Find minimum of f in [a,b] using golden section search.

        Convergence rate: φ per iteration
        """
        c = b - (b - a) / cls.PHI
        d = a + (b - a) / cls.PHI

        while abs(b - a) > tol:
            if f(c) < f(d):
                b = d
            else:
                a = c
            c = b - (b - a) / cls.PHI
            d = a + (b - a) / cls.PHI

        return (a + b) / 2

    @classmethod
    def egyptian_decompose(cls, numerator: int, denominator: int) -> List[int]:
        """
        Decompose fraction into Egyptian fractions.

        Used for fair resource allocation in debugging tasks.
        """
        result = []
        num, den = numerator, denominator

        while num > 0 and len(result) < 20:
            x = (den + num - 1) // num  # ceiling division
            result.append(x)
            num = num * x - den
            den *= x
            g = math.gcd(abs(num), abs(den))
            if g > 1:
                num //= g
                den //= g

        return result

    @classmethod
    def prioritize_issues(cls, issues: List[Dict]) -> List[Dict]:
        """
        Prioritize issues using Brahim resonance weighting.

        Issues with higher resonance (more impactful) come first.
        """
        def issue_weight(issue: Dict) -> float:
            severity = issue.get('severity', 1)
            frequency = issue.get('frequency', 1)
            # Use mirror pairs for weighting
            return cls.B(min(severity, 10)) * frequency

        return sorted(issues, key=issue_weight, reverse=True)
