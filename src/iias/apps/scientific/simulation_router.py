"""
Simulation Router - 12-Dimension Parameter Space Routing
========================================================

Routes simulations across a 12-dimensional parameter space using the IIAS
architecture. Each dimension maps to a Lucas capacity for resource allocation.

Dimension Mapping:
    D1-D4:   Low complexity (capacity 1+3+4+7 = 15)
    D5-D8:   Medium complexity (capacity 11+18+29+47 = 105)
    D9-D12:  High complexity (capacity 76+123+199+322 = 720)

The router uses PHI-based weighting for parameter importance.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# Constants
PHI = 1.618033988749895
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
D10_CAPACITY = 123  # Wisdom dimension
TOTAL_STATES = 840

# Dimension names in the 12D parameter space
DIMENSION_NAMES = [
    "Foundation",    # D1
    "Structure",     # D2
    "Dynamics",      # D3
    "Interaction",   # D4
    "Emergence",     # D5
    "Pattern",       # D6
    "Complexity",    # D7
    "Integration",   # D8
    "Insight",       # D9
    "Wisdom",        # D10
    "Transcendence", # D11
    "Unity",         # D12
]


class ComplexityTier(Enum):
    """Simulation complexity tiers."""
    LOW = "LOW"       # D1-D4
    MEDIUM = "MEDIUM" # D5-D8
    HIGH = "HIGH"     # D9-D12


@dataclass
class ParameterPoint:
    """A point in the 12-dimensional parameter space."""
    coordinates: List[float]  # 12 values, each 0.0-1.0
    name: str = ""

    def __post_init__(self):
        if len(self.coordinates) != 12:
            raise ValueError(f"Expected 12 coordinates, got {len(self.coordinates)}")
        # Normalize to [0, 1]
        self.coordinates = [max(0.0, min(1.0, c)) for c in self.coordinates]

    @property
    def dominant_dimension(self) -> int:
        """Find the dimension with highest weight."""
        return self.coordinates.index(max(self.coordinates)) + 1

    @property
    def complexity_tier(self) -> ComplexityTier:
        """Determine complexity tier from dominant dimension."""
        dim = self.dominant_dimension
        if dim <= 4:
            return ComplexityTier.LOW
        elif dim <= 8:
            return ComplexityTier.MEDIUM
        else:
            return ComplexityTier.HIGH

    def get_weighted_capacity(self) -> float:
        """Calculate total weighted capacity based on coordinates."""
        total = 0.0
        for i, coord in enumerate(self.coordinates):
            total += coord * LUCAS[i]
        return total


@dataclass
class SimulationConfig:
    """Configuration for a simulation run."""
    sim_id: str
    parameter_point: ParameterPoint
    iterations: int = 1000
    precision: float = 1e-6
    timeout_seconds: float = 3600.0


@dataclass
class RoutingDecision:
    """Result of routing a simulation."""
    config: SimulationConfig
    tier: ComplexityTier
    primary_dimension: int
    allocated_capacity: int
    phi_weight: float
    estimated_runtime_seconds: float
    success: bool
    message: str = ""


class SimulationRouter:
    """
    Routes simulations through a 12-dimensional parameter space.

    Uses Lucas capacities to allocate resources and PHI-based weighting
    to prioritize dimensions.
    """

    def __init__(self):
        self.phi = PHI
        self.lucas = LUCAS
        self.total_states = TOTAL_STATES
        self.d10_capacity = D10_CAPACITY

        # Track allocated capacity per dimension
        self._allocated: List[float] = [0.0] * 12

        # Active simulations
        self._active_simulations: Dict[str, SimulationConfig] = {}

    def route(self, config: SimulationConfig) -> RoutingDecision:
        """
        Route a simulation to the appropriate dimension tier.

        Args:
            config: Simulation configuration with parameter point

        Returns:
            RoutingDecision with allocation details
        """
        point = config.parameter_point
        tier = point.complexity_tier
        primary_dim = point.dominant_dimension

        # Get capacity for primary dimension
        dim_capacity = self.lucas[primary_dim - 1]
        current_usage = self._allocated[primary_dim - 1]

        # Calculate PHI-weighted importance
        phi_weight = self._calculate_phi_weight(point)

        # Check if we can allocate
        required = point.get_weighted_capacity() / self.total_states

        if current_usage + required > 1.0:
            return RoutingDecision(
                config=config,
                tier=tier,
                primary_dimension=primary_dim,
                allocated_capacity=0,
                phi_weight=phi_weight,
                estimated_runtime_seconds=float('inf'),
                success=False,
                message=f"D{primary_dim} ({DIMENSION_NAMES[primary_dim-1]}) at capacity"
            )

        # Allocate resources
        self._allocated[primary_dim - 1] += required
        self._active_simulations[config.sim_id] = config

        # Estimate runtime based on complexity and PHI scaling
        runtime = self._estimate_runtime(config, tier, phi_weight)

        return RoutingDecision(
            config=config,
            tier=tier,
            primary_dimension=primary_dim,
            allocated_capacity=dim_capacity,
            phi_weight=phi_weight,
            estimated_runtime_seconds=runtime,
            success=True,
            message=f"Routed to D{primary_dim} ({DIMENSION_NAMES[primary_dim-1]})"
        )

    def _calculate_phi_weight(self, point: ParameterPoint) -> float:
        """
        Calculate PHI-based weight for a parameter point.

        Higher dimensions get exponentially more weight via PHI.
        """
        total_weight = 0.0
        for i, coord in enumerate(point.coordinates):
            # PHI^(dimension/6) scaling - higher dims get more weight
            phi_factor = self.phi ** (i / 6.0)
            total_weight += coord * phi_factor
        return total_weight / 12.0

    def _estimate_runtime(self, config: SimulationConfig,
                          tier: ComplexityTier, phi_weight: float) -> float:
        """Estimate simulation runtime in seconds."""
        base_time = config.iterations * 0.001  # 1ms per iteration base

        # Tier multipliers
        tier_mult = {
            ComplexityTier.LOW: 1.0,
            ComplexityTier.MEDIUM: self.phi,
            ComplexityTier.HIGH: self.phi ** 2,
        }

        # Precision factor (tighter precision = longer runtime)
        precision_factor = -math.log10(config.precision) / 6.0

        return base_time * tier_mult[tier] * precision_factor * (1 + phi_weight)

    def get_dimension_status(self) -> Dict[int, Dict[str, Any]]:
        """Get allocation status for all 12 dimensions."""
        status = {}
        for i in range(12):
            dim = i + 1
            status[dim] = {
                "name": DIMENSION_NAMES[i],
                "lucas_capacity": self.lucas[i],
                "allocated": self._allocated[i],
                "available": 1.0 - self._allocated[i],
            }
        return status

    def get_tier_capacity(self, tier: ComplexityTier) -> Tuple[int, int]:
        """Get (used, total) capacity for a tier."""
        if tier == ComplexityTier.LOW:
            dims = range(0, 4)
        elif tier == ComplexityTier.MEDIUM:
            dims = range(4, 8)
        else:
            dims = range(8, 12)

        total = sum(self.lucas[i] for i in dims)
        used = sum(self._allocated[i] * self.lucas[i] for i in dims)
        return int(used), total

    def release(self, sim_id: str) -> bool:
        """Release resources from a completed simulation."""
        if sim_id not in self._active_simulations:
            return False

        config = self._active_simulations.pop(sim_id)
        point = config.parameter_point
        primary_dim = point.dominant_dimension
        required = point.get_weighted_capacity() / self.total_states

        self._allocated[primary_dim - 1] = max(0.0,
            self._allocated[primary_dim - 1] - required)
        return True

    def reset(self) -> None:
        """Reset all allocations."""
        self._allocated = [0.0] * 12
        self._active_simulations.clear()


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Simulation Router Test")
    print("=" * 60)

    router = SimulationRouter()

    # Display constants
    print(f"\nPHI = {PHI}")
    print(f"LUCAS = {LUCAS}")
    print(f"D10_CAPACITY = {D10_CAPACITY}")
    print(f"TOTAL_STATES = {TOTAL_STATES}")

    # Verify Lucas sum
    lucas_sum = sum(LUCAS)
    print(f"\nLucas sum: {lucas_sum} (expected {TOTAL_STATES})")
    assert lucas_sum == TOTAL_STATES, "Lucas sum mismatch!"

    print("\n--- Dimension Configuration ---")
    for i in range(12):
        print(f"  D{i+1:2d} ({DIMENSION_NAMES[i]:12s}): capacity = {LUCAS[i]:3d}")

    # Test routing with different parameter points
    print("\n--- Routing Tests ---")

    test_points = [
        # Low complexity - dominant in D1-D4
        ParameterPoint([0.9, 0.1, 0.1, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "Foundation Focus"),
        # Medium complexity - dominant in D5-D8
        ParameterPoint([0.1, 0.1, 0.1, 0.1, 0.2, 0.8, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1], "Pattern Focus"),
        # High complexity - dominant in D10 (Wisdom)
        ParameterPoint([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.9, 0.2, 0.1], "Wisdom Focus"),
    ]

    for point in test_points:
        config = SimulationConfig(
            sim_id=f"sim-{point.name.replace(' ', '-').lower()}",
            parameter_point=point,
            iterations=10000,
            precision=1e-8
        )

        result = router.route(config)
        print(f"\n{point.name}:")
        print(f"  Dominant dimension: D{result.primary_dimension} ({DIMENSION_NAMES[result.primary_dimension-1]})")
        print(f"  Complexity tier: {result.tier.value}")
        print(f"  Allocated capacity: {result.allocated_capacity}")
        print(f"  PHI weight: {result.phi_weight:.4f}")
        print(f"  Estimated runtime: {result.estimated_runtime_seconds:.2f}s")
        print(f"  Success: {result.success}")

    # Display tier capacities
    print("\n--- Tier Capacities ---")
    for tier in ComplexityTier:
        used, total = router.get_tier_capacity(tier)
        print(f"  {tier.value:6s}: {used:3d}/{total:3d} used")

    # Display dimension status
    print("\n--- Dimension Status ---")
    status = router.get_dimension_status()
    for dim, info in status.items():
        if info['allocated'] > 0:
            print(f"  D{dim} ({info['name']}): {info['allocated']:.1%} allocated")

    print("\n" + "=" * 60)
    print("Simulation Router Test Complete")
    print("=" * 60)
