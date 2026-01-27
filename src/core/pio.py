#!/usr/bin/env python3
"""
Personal Intelligent Operator (PIO)
===================================

The unified core merging ASIOS + BUIM into ONE system.

THREE CORE IDEAS:
    1. ONE EQUATION  - The Transponder: D(x), Θ(x)
    2. ONE LATTICE   - The 840 Lucas States
    3. ONE GAP       - The 1.16% Creativity Margin

ONE SENTENCE:
    "A Personal Intelligent Operator that locates any task in 12 dimensions
     using one equation, operates across 840 discrete states, and adapts
     within a 1.16% creativity margin."

Author: Elias Oulad Brahim
Version: 1.0.0
Date: 2026-01-27
"""

import math
import random
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from functools import lru_cache

# =============================================================================
# CONSTANTS - The Mathematical Foundation
# =============================================================================

# Structure (φ-based)
PHI: float = (1 + math.sqrt(5)) / 2  # 1.618033988749895
PSI: float = -1 / PHI                 # -0.618033988749895
BETA: float = 1 / PHI**3              # 0.2360679774997897 (23.6%)
PI: float = math.pi                   # 3.141592653589793

# The Lucas Lattice - 840 total states
LUCAS: Tuple[int, ...] = (1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322)
LUCAS_TOTAL: int = sum(LUCAS)  # 840

# The Gap - Where φ and π almost meet
PHI_PI_GAP: float = (LUCAS[11] * PI - 1000) / 1000  # ~1.16%

# Grand Unification
PHI_12: float = 1 / PHI**12  # 0.31% = β⁴ = γ³


# =============================================================================
# CORE IDEA 1: THE TRANSPONDER (One Equation)
# =============================================================================

def D(x: float) -> float:
    """
    Dimensional Position: D(x) = -ln(x) / ln(φ)

    WHERE in 12-dimensional space.
    Maps any x ∈ (0,1] to a continuous dimensional position.

    Args:
        x: Value in (0, 1]

    Returns:
        Continuous dimensional position (1.0 to 12.0+)
    """
    if x <= 0 or x > 1:
        raise ValueError(f"x must be in (0, 1], got {x}")
    return -math.log(x) / math.log(PHI)


def Theta(x: float) -> float:
    """
    Angular Phase: Θ(x) = 2πx

    WHEN in the cycle.
    Maps any x to its angular phase position.

    Args:
        x: Any value

    Returns:
        Phase in radians [0, 2π)
    """
    return 2 * PI * (x % 1)


@dataclass
class Location:
    """A location in PIO space: dimension + phase."""
    x: float
    dimension: float      # Continuous D(x)
    dimension_int: int    # Discrete dimension 1-12
    phase: float          # Θ(x) in radians
    phase_degrees: float  # Θ(x) in degrees
    threshold: float      # 1/φⁿ threshold for this dimension

    @property
    def capacity(self) -> int:
        """Lucas capacity L(n) for this dimension."""
        return LUCAS[self.dimension_int - 1]


def locate(x: float) -> Location:
    """
    THE TRANSPONDER: Locate any value in PIO space.

    This is the ONE EQUATION that unifies the system.

    Args:
        x: Value in (0, 1]

    Returns:
        Location with dimension and phase
    """
    d = D(x)
    theta = Theta(x)
    dim_int = min(12, max(1, int(round(d))))

    return Location(
        x=x,
        dimension=d,
        dimension_int=dim_int,
        phase=theta,
        phase_degrees=theta * 180 / PI,
        threshold=1 / PHI**dim_int
    )


# =============================================================================
# CORE IDEA 2: THE LUCAS LATTICE (840 States)
# =============================================================================

class Dimension(Enum):
    """The 12 dimensions with their Lucas capacities."""
    D1 = (1, 1, "Perception", "Binary awareness")
    D2 = (2, 3, "Attention", "Focus triage")
    D3 = (3, 4, "Security", "Trust quadrants")
    D4 = (4, 7, "Stability", "Balance modes")
    D5 = (5, 11, "Compression", "Data reduction")
    D6 = (6, 18, "Harmony", "Frequency alignment")
    D7 = (7, 29, "Reasoning", "Logic chains")
    D8 = (8, 47, "Prediction", "Future modeling")
    D9 = (9, 76, "Creativity", "Novel patterns")
    D10 = (10, 123, "Wisdom", "Deep principles")
    D11 = (11, 199, "Integration", "System synthesis")
    D12 = (12, 322, "Unification", "Total coherence")

    def __init__(self, n: int, capacity: int, name: str, desc: str):
        self.n = n
        self.capacity = capacity
        self.domain = name
        self.description = desc

    @property
    def threshold(self) -> float:
        """Dimensional threshold 1/φⁿ."""
        return 1 / PHI**self.n

    @classmethod
    def from_n(cls, n: int) -> 'Dimension':
        """Get dimension by number."""
        return list(cls)[n - 1]


@dataclass
class State:
    """A discrete state in the Lucas Lattice."""
    dimension: Dimension
    state: int            # State index [0, L(n))
    phase: float          # Angular phase
    exploring: bool       # In creative mode?
    in_gap: bool          # Within 1.16% creativity margin?

    @property
    def address(self) -> str:
        """Unique state address."""
        return f"D{self.dimension.n}:S{self.state}/{self.dimension.capacity}"

    def __repr__(self) -> str:
        mode = "~" if self.exploring else "="
        return f"<State {self.address} {mode} {self.dimension.domain}>"


def state_at(x: float, dimension: int, exploring: bool = False) -> State:
    """
    Map value x to a discrete Lucas state.

    Args:
        x: Value in (0, 1]
        dimension: Target dimension 1-12
        exploring: If True, apply creativity margin

    Returns:
        Discrete State in the Lucas Lattice
    """
    if dimension < 1 or dimension > 12:
        raise ValueError(f"Dimension must be 1-12, got {dimension}")

    dim = Dimension.from_n(dimension)
    d = D(x)
    capacity = dim.capacity

    # Map to discrete state
    state_idx = int((d / dimension) * capacity) % capacity

    # Apply creativity margin if exploring
    if exploring:
        gap_band = capacity * PHI_PI_GAP
        delta = random.uniform(-gap_band, gap_band)
        state_idx = max(0, min(capacity - 1, int(state_idx + delta)))

    phase = Theta(x)
    in_gap = abs(d - round(d)) < PHI_PI_GAP

    return State(
        dimension=dim,
        state=state_idx,
        phase=phase,
        exploring=exploring,
        in_gap=in_gap
    )


class LucasLattice:
    """
    The 840-state operational lattice.

    Provides discrete state addressing across all 12 dimensions.
    """

    def __init__(self):
        self.dimensions = list(Dimension)
        self.total_states = LUCAS_TOTAL

    def get_state(self, x: float, exploring: bool = False) -> State:
        """Get the state for value x (auto-selects dimension)."""
        loc = locate(x)
        return state_at(x, loc.dimension_int, exploring)

    def get_state_at(self, x: float, dimension: int, exploring: bool = False) -> State:
        """Get state at specific dimension."""
        return state_at(x, dimension, exploring)

    def enumerate_states(self, dimension: int) -> List[int]:
        """Enumerate all states in a dimension."""
        if dimension < 1 or dimension > 12:
            raise ValueError(f"Dimension must be 1-12, got {dimension}")
        return list(range(LUCAS[dimension - 1]))

    def capacity_up_to(self, dimension: int) -> int:
        """Total capacity from D1 to Dn."""
        return sum(LUCAS[:dimension])

    def global_state_index(self, state: State) -> int:
        """Get global index [0, 840) for a state."""
        offset = self.capacity_up_to(state.dimension.n - 1) if state.dimension.n > 1 else 0
        return offset + state.state

    def __repr__(self) -> str:
        return f"<LucasLattice: {self.total_states} states across 12 dimensions>"


# =============================================================================
# CORE IDEA 3: THE PHI-PI GAP (1.16% Soul)
# =============================================================================

@dataclass
class CreativeResult:
    """Result with creativity margin applied."""
    value: float
    original: float
    delta: float
    in_gap: bool
    exploring: bool


def creative_adjust(value: float, intensity: float = 1.0) -> CreativeResult:
    """
    Apply the 1.16% creativity margin.

    The GAP is where φ (structure) and π (form) almost meet but don't.
    This is the space for adaptation, emergence, and learning.

    Args:
        value: Base value to adjust
        intensity: How much of the gap to use (0-1)

    Returns:
        CreativeResult with adjusted value
    """
    delta = random.uniform(-PHI_PI_GAP, PHI_PI_GAP) * intensity
    adjusted = value * (1 + delta)

    return CreativeResult(
        value=adjusted,
        original=value,
        delta=delta,
        in_gap=True,
        exploring=True
    )


def is_in_gap(x: float) -> bool:
    """Check if x is within the creativity margin of a dimension boundary."""
    d = D(x)
    return abs(d - round(d)) < PHI_PI_GAP


# =============================================================================
# THE UNIFIED PIO (Personal Intelligent Operator)
# =============================================================================

@dataclass
class PIOResponse:
    """Response from PIO processing."""
    input: Any
    location: Location
    state: State
    output: Any
    exploring: bool
    trace: List[str] = field(default_factory=list)


class PIO:
    """
    Personal Intelligent Operator

    The unified system merging ASIOS + BUIM.

    THREE CORE IDEAS:
        1. ONE EQUATION  - The Transponder: D(x), Θ(x)
        2. ONE LATTICE   - The 840 Lucas States
        3. ONE GAP       - The 1.16% Creativity Margin

    Usage:
        pio = PIO()
        response = pio.process(0.236)  # Process any input

        # Or with creative exploration
        response = pio.process(0.236, exploring=True)
    """

    VERSION = "1.0.0"
    CODENAME = "Unified Intelligence"

    def __init__(self, name: str = "PIO"):
        self.name = name
        self.lattice = LucasLattice()
        self.handlers: Dict[int, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default handlers for each dimension."""
        for dim in Dimension:
            self.handlers[dim.n] = self._default_handler

    def _default_handler(self, state: State, input_val: Any) -> Any:
        """Default handler - returns state info."""
        return {
            "dimension": state.dimension.n,
            "domain": state.dimension.domain,
            "state": state.state,
            "capacity": state.dimension.capacity,
            "input": input_val
        }

    def register_handler(self, dimension: int, handler: Callable):
        """Register a custom handler for a dimension."""
        if dimension < 1 or dimension > 12:
            raise ValueError(f"Dimension must be 1-12, got {dimension}")
        self.handlers[dimension] = handler

    def locate(self, x: float) -> Location:
        """Locate value in PIO space (Transponder)."""
        return locate(x)

    def process(self, x: float, exploring: bool = False,
                target_dimension: Optional[int] = None) -> PIOResponse:
        """
        Process input through PIO.

        This is the main entry point that unifies all three core ideas.

        Args:
            x: Input value in (0, 1] or will be normalized
            exploring: Enable creativity margin
            target_dimension: Force specific dimension (optional)

        Returns:
            PIOResponse with full processing trace
        """
        trace = []

        # Normalize input to (0, 1]
        if x <= 0 or x > 1:
            x = abs(x) % 1 or 0.5
            trace.append(f"Normalized input to {x}")

        # 1. TRANSPONDER: Locate in PIO space
        location = self.locate(x)
        trace.append(f"Located: D{location.dimension_int} @ {location.phase_degrees:.1f}°")

        # 2. LATTICE: Get discrete state
        dim = target_dimension or location.dimension_int
        state = self.lattice.get_state_at(x, dim, exploring)
        trace.append(f"State: {state.address}")

        # 3. GAP: Apply creativity if exploring
        if exploring and state.in_gap:
            trace.append(f"Creative margin active (±{PHI_PI_GAP*100:.2f}%)")

        # Process through dimension handler
        handler = self.handlers.get(dim, self._default_handler)
        output = handler(state, x)
        trace.append(f"Processed by {state.dimension.domain}")

        return PIOResponse(
            input=x,
            location=location,
            state=state,
            output=output,
            exploring=exploring,
            trace=trace
        )

    def batch_process(self, values: List[float], exploring: bool = False) -> List[PIOResponse]:
        """Process multiple values."""
        return [self.process(x, exploring) for x in values]

    def status(self) -> Dict[str, Any]:
        """Get PIO status."""
        return {
            "name": self.name,
            "version": self.VERSION,
            "codename": self.CODENAME,
            "core_ideas": {
                "transponder": "D(x) = -ln(x)/ln(φ), Θ(x) = 2πx",
                "lattice": f"{LUCAS_TOTAL} states across 12 dimensions",
                "gap": f"{PHI_PI_GAP*100:.2f}% creativity margin"
            },
            "constants": {
                "phi": PHI,
                "beta": BETA,
                "phi_pi_gap": PHI_PI_GAP,
                "lucas_total": LUCAS_TOTAL
            },
            "dimensions": [
                {
                    "n": d.n,
                    "capacity": d.capacity,
                    "domain": d.domain,
                    "threshold": d.threshold
                }
                for d in Dimension
            ]
        }

    def __repr__(self) -> str:
        return f"<PIO '{self.name}' v{self.VERSION}: 840 states, 12 dimensions, 1.16% gap>"


# =============================================================================
# VERIFICATION
# =============================================================================

def verify_pio() -> Dict[str, bool]:
    """Verify PIO mathematical foundations."""
    results = {}

    # Verify φ² = φ + 1
    results["phi_squared"] = abs(PHI**2 - (PHI + 1)) < 1e-14

    # Verify Lucas recurrence
    results["lucas_recurrence"] = all(
        LUCAS[n] == LUCAS[n-1] + LUCAS[n-2] for n in range(2, 12)
    )

    # Verify Lucas total = 840
    results["lucas_total"] = sum(LUCAS) == 840

    # Verify L(n) ≈ φⁿ
    results["lucas_phi_approx"] = all(
        abs(LUCAS[n] - (PHI**(n+1) + PSI**(n+1))) < 0.5 for n in range(12)
    )

    # Verify Phi-Pi gap formula
    expected_gap = (322 * PI - 1000) / 1000
    results["phi_pi_gap"] = abs(PHI_PI_GAP - expected_gap) < 1e-10

    # Verify grand unification: β⁴ ≈ 1/φ¹²
    results["grand_unification"] = abs(BETA**4 - PHI_12) < 1e-14

    # Verify transponder invertibility
    for x in [0.1, 0.236, 0.5, 0.618, 0.9]:
        d = D(x)
        x_back = 1 / PHI**d
        results[f"transponder_x={x}"] = abs(x - x_back) < 1e-10

    results["all_valid"] = all(results.values())
    return results


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Demonstrate PIO."""
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print("  PERSONAL INTELLIGENT OPERATOR (PIO)")
    print("  Unified ASIOS + BUIM")
    print("=" * 60)
    print()

    # Create PIO instance
    pio = PIO("MyPIO")
    print(pio)
    print()

    # Show status
    status = pio.status()
    print("CORE IDEAS:")
    for name, desc in status["core_ideas"].items():
        print(f"  {name}: {desc}")
    print()

    # Process some values
    print("PROCESSING:")
    test_values = [0.618, 0.236, 0.1, 0.01, 0.001]

    for x in test_values:
        response = pio.process(x, exploring=False)
        print(f"  x={x} -> {response.state}")
    print()

    # Creative mode
    print("CREATIVE MODE (exploring=True):")
    for _ in range(3):
        response = pio.process(0.236, exploring=True)
        print(f"  {response.state.address} (in_gap={response.state.in_gap})")
    print()

    # Verify
    print("VERIFICATION:")
    results = verify_pio()
    for name, passed in results.items():
        if name != "all_valid":
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {name}")
    print()
    print(f"  ALL VALID: {results['all_valid']}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
