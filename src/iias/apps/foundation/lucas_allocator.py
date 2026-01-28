"""
Lucas Allocator - State Budgeting Using Lucas Numbers
=====================================================

This module implements state budgeting based on the Lucas number sequence:
    L = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]

Key properties:
    - L_n = L_{n-1} + L_{n-2} (Fibonacci-like recurrence)
    - sum(L) = 840 = TOTAL_STATES
    - 12 dimensions for complete system coverage

The Lucas sequence provides natural allocation weights for the 12 IIAS dimensions.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from iias.constants import PHI, CENTER, SUM_CONSTANT, BRAHIM_NUMBERS, LUCAS


# Total states derived from Lucas sum
TOTAL_STATES = 840


class AllocationMode(Enum):
    """Resource allocation strategies."""
    PROPORTIONAL = "proportional"      # Direct Lucas proportion
    PHI_WEIGHTED = "phi_weighted"      # PHI-adjusted weights
    UNIFORM = "uniform"                # Equal distribution
    PRIORITY = "priority"              # Higher dimensions first


@dataclass
class StateAllocation:
    """Allocation result for a single dimension."""

    dimension: int
    name: str
    lucas_capacity: int
    allocated_states: float
    utilization: float

    @property
    def is_within_capacity(self) -> bool:
        """Check if allocation is within Lucas capacity."""
        return self.allocated_states <= self.lucas_capacity


class LucasAllocator:
    """
    State budgeting system using Lucas numbers.

    The Lucas allocator distributes system states across 12 dimensions
    using the Lucas sequence as capacity weights. This ensures natural
    scaling following the golden ratio PHI.

    Attributes:
        lucas: The Lucas sequence [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322].
        total_states: Sum of Lucas numbers (840).
        dimension_names: Names for each of the 12 dimensions.
    """

    # Dimension names corresponding to the 12 Lucas numbers
    DIMENSION_NAMES = [
        "PERCEPTION",    # L_1 = 1
        "ATTENTION",     # L_2 = 3
        "SECURITY",      # L_3 = 4
        "STABILITY",     # L_4 = 7
        "COMPRESSION",   # L_5 = 11
        "HARMONY",       # L_6 = 18
        "REASONING",     # L_7 = 29
        "PREDICTION",    # L_8 = 47
        "CREATIVITY",    # L_9 = 76
        "WISDOM",        # L_10 = 123
        "INTEGRATION",   # L_11 = 199
        "UNIFICATION",   # L_12 = 322
    ]

    def __init__(self):
        """Initialize the LucasAllocator with Lucas sequence."""
        self.lucas = LUCAS
        self.total_states = sum(LUCAS)  # Should be 840
        self.phi = PHI
        self.center = CENTER
        self.sum_constant = SUM_CONSTANT

        # Precompute proportional weights
        self._weights = [l / self.total_states for l in self.lucas]

    def get_capacity(self, dimension: int) -> int:
        """
        Get the Lucas capacity for a dimension (1-12).

        Args:
            dimension: The dimension index (1-12).

        Returns:
            The Lucas number capacity for that dimension.
        """
        if 1 <= dimension <= 12:
            return self.lucas[dimension - 1]
        return 0

    def get_dimension_name(self, dimension: int) -> str:
        """
        Get the name of a dimension (1-12).

        Args:
            dimension: The dimension index (1-12).

        Returns:
            The dimension name or "UNKNOWN".
        """
        if 1 <= dimension <= 12:
            return self.DIMENSION_NAMES[dimension - 1]
        return "UNKNOWN"

    def allocate(
        self,
        total_budget: float,
        mode: AllocationMode = AllocationMode.PROPORTIONAL
    ) -> List[StateAllocation]:
        """
        Allocate a budget across all 12 dimensions.

        Args:
            total_budget: Total states/resources to allocate.
            mode: The allocation strategy to use.

        Returns:
            List of StateAllocation objects for each dimension.
        """
        allocations = []

        if mode == AllocationMode.PROPORTIONAL:
            weights = self._weights
        elif mode == AllocationMode.PHI_WEIGHTED:
            # Weight by PHI^(dimension-1)
            raw = [self.phi ** (i) for i in range(12)]
            total = sum(raw)
            weights = [r / total for r in raw]
        elif mode == AllocationMode.UNIFORM:
            weights = [1.0 / 12] * 12
        elif mode == AllocationMode.PRIORITY:
            # Higher dimensions get more (reverse Lucas proportion)
            reversed_lucas = list(reversed(self.lucas))
            total = sum(reversed_lucas)
            weights = [l / total for l in reversed_lucas]
        else:
            weights = self._weights

        for i in range(12):
            dim = i + 1
            allocated = total_budget * weights[i]
            capacity = self.lucas[i]
            utilization = allocated / capacity if capacity > 0 else 0

            allocations.append(StateAllocation(
                dimension=dim,
                name=self.DIMENSION_NAMES[i],
                lucas_capacity=capacity,
                allocated_states=allocated,
                utilization=utilization
            ))

        return allocations

    def allocate_by_demand(
        self,
        demands: Dict[int, float]
    ) -> Tuple[List[StateAllocation], Dict[str, Any]]:
        """
        Allocate based on specific dimension demands.

        Respects Lucas capacity limits and redistributes overflow.

        Args:
            demands: Dictionary mapping dimension (1-12) to requested amount.

        Returns:
            Tuple of (allocations list, metrics dictionary).
        """
        allocations = []
        total_demanded = sum(demands.values())
        total_allocated = 0
        overflow = 0

        for i in range(12):
            dim = i + 1
            capacity = self.lucas[i]
            demanded = demands.get(dim, 0)

            # Cap at capacity
            if demanded > capacity:
                allocated = capacity
                overflow += demanded - capacity
            else:
                allocated = demanded

            total_allocated += allocated
            utilization = allocated / capacity if capacity > 0 else 0

            allocations.append(StateAllocation(
                dimension=dim,
                name=self.DIMENSION_NAMES[i],
                lucas_capacity=capacity,
                allocated_states=allocated,
                utilization=utilization
            ))

        metrics = {
            "total_demanded": total_demanded,
            "total_allocated": total_allocated,
            "overflow": overflow,
            "efficiency": total_allocated / total_demanded if total_demanded > 0 else 1.0,
            "capacity_used": total_allocated / self.total_states,
        }

        return allocations, metrics

    def compute_phi_cascade(self, initial: float) -> List[Dict[str, Any]]:
        """
        Compute PHI-cascade allocation from initial value.

        Each subsequent dimension gets PHI times less than the previous,
        following the golden ratio decay.

        Args:
            initial: The starting allocation for dimension 1.

        Returns:
            List of cascade allocation results.
        """
        cascade = []
        current = initial

        for i in range(12):
            dim = i + 1
            capacity = self.lucas[i]
            utilization = current / capacity if capacity > 0 else 0

            cascade.append({
                "dimension": dim,
                "name": self.DIMENSION_NAMES[i],
                "allocation": current,
                "capacity": capacity,
                "utilization": utilization,
                "within_capacity": current <= capacity,
            })

            # Decay by PHI for next dimension
            current = current / self.phi

        return cascade

    def balance_to_center(self, allocations: List[StateAllocation]) -> Dict[str, Any]:
        """
        Analyze how well allocations balance around CENTER (107).

        Args:
            allocations: List of StateAllocation objects.

        Returns:
            Balance analysis metrics.
        """
        # Weighted center of allocations
        total_alloc = sum(a.allocated_states for a in allocations)
        if total_alloc == 0:
            return {"weighted_center": 0, "deviation": self.center, "balanced": False}

        weighted_sum = sum(
            a.dimension * a.allocated_states for a in allocations
        )
        weighted_center = weighted_sum / total_alloc

        # Ideal center is around dimension 6.5 (between 6 and 7)
        ideal_center = 6.5
        deviation = abs(weighted_center - ideal_center)

        return {
            "weighted_center": weighted_center,
            "ideal_center": ideal_center,
            "deviation": deviation,
            "balanced": deviation < 1.0,
            "total_allocated": total_alloc,
        }

    def verify_lucas_properties(self) -> Dict[str, Any]:
        """
        Verify Lucas sequence properties.

        Returns:
            Dictionary with verification results.
        """
        # Check recurrence relation: L_n = L_{n-1} + L_{n-2}
        recurrence_ok = True
        for i in range(2, 12):
            if self.lucas[i] != self.lucas[i-1] + self.lucas[i-2]:
                recurrence_ok = False
                break

        # Check total
        total_ok = sum(self.lucas) == TOTAL_STATES

        # Check PHI relationship (L_n / L_{n-1} approaches PHI)
        ratios = []
        for i in range(1, 12):
            if self.lucas[i-1] > 0:
                ratios.append(self.lucas[i] / self.lucas[i-1])

        phi_convergence = abs(ratios[-1] - self.phi) if ratios else float('inf')

        return {
            "lucas_sequence": self.lucas,
            "total_states": self.total_states,
            "expected_total": TOTAL_STATES,
            "total_correct": total_ok,
            "recurrence_valid": recurrence_ok,
            "ratios": ratios,
            "phi_convergence": phi_convergence,
            "converges_to_phi": phi_convergence < 0.01,
        }

    def generate_budget_report(self, budget: float) -> str:
        """
        Generate a formatted budget allocation report.

        Args:
            budget: Total budget to allocate.

        Returns:
            Formatted report string.
        """
        allocations = self.allocate(budget, AllocationMode.PROPORTIONAL)
        balance = self.balance_to_center(allocations)

        lines = [
            "=" * 60,
            "LUCAS ALLOCATOR - BUDGET REPORT",
            "=" * 60,
            f"Total Budget: {budget:.2f}",
            f"Total States (Capacity): {self.total_states}",
            "-" * 60,
            f"{'Dim':>3} {'Name':<14} {'Capacity':>8} {'Allocated':>10} {'Util':>8}",
            "-" * 60,
        ]

        for a in allocations:
            status = "OK" if a.is_within_capacity else "OVER"
            lines.append(
                f"{a.dimension:>3} {a.name:<14} {a.lucas_capacity:>8} "
                f"{a.allocated_states:>10.2f} {a.utilization:>7.1%} {status}"
            )

        lines.extend([
            "-" * 60,
            f"Weighted Center: {balance['weighted_center']:.2f} "
            f"(ideal: {balance['ideal_center']:.1f})",
            f"Balance Status: {'BALANCED' if balance['balanced'] else 'UNBALANCED'}",
            "=" * 60,
        ])

        return "\n".join(lines)


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Lucas Allocator - State Budgeting Test")
    print("=" * 60)

    allocator = LucasAllocator()

    # Test 1: Verify Lucas sequence properties
    print("\n[Test 1] Lucas Sequence Verification")
    print("-" * 40)
    props = allocator.verify_lucas_properties()
    print(f"Sequence: {props['lucas_sequence']}")
    print(f"Total States: {props['total_states']} (expected: {props['expected_total']})")
    print(f"Total Correct: {props['total_correct']}")
    print(f"Recurrence Valid: {props['recurrence_valid']}")
    print(f"PHI Convergence: {props['phi_convergence']:.6f}")
    print(f"Converges to PHI: {props['converges_to_phi']}")

    # Test 2: Proportional allocation
    print("\n[Test 2] Proportional Allocation of 840 states")
    print("-" * 40)
    allocs = allocator.allocate(840, AllocationMode.PROPORTIONAL)
    for a in allocs:
        print(f"  D{a.dimension:2d} {a.name:14s}: {a.allocated_states:6.1f} / {a.lucas_capacity:3d} = {a.utilization:5.1%}")

    # Test 3: PHI-weighted allocation
    print("\n[Test 3] PHI-Weighted Allocation of 840 states")
    print("-" * 40)
    allocs_phi = allocator.allocate(840, AllocationMode.PHI_WEIGHTED)
    for a in allocs_phi:
        print(f"  D{a.dimension:2d} {a.name:14s}: {a.allocated_states:6.1f} / {a.lucas_capacity:3d} = {a.utilization:5.1%}")

    # Test 4: PHI cascade
    print("\n[Test 4] PHI Cascade from initial=100")
    print("-" * 40)
    cascade = allocator.compute_phi_cascade(100)
    for c in cascade:
        status = "OK" if c['within_capacity'] else "OVER"
        print(f"  D{c['dimension']:2d}: {c['allocation']:8.2f} (cap: {c['capacity']:3d}) [{status}]")

    # Test 5: Demand-based allocation
    print("\n[Test 5] Demand-Based Allocation")
    print("-" * 40)
    demands = {1: 2, 5: 15, 10: 200, 12: 400}  # Some over capacity
    allocs, metrics = allocator.allocate_by_demand(demands)
    print(f"Demanded: {demands}")
    print(f"Total Demanded: {metrics['total_demanded']}")
    print(f"Total Allocated: {metrics['total_allocated']}")
    print(f"Overflow: {metrics['overflow']}")
    print(f"Efficiency: {metrics['efficiency']:.1%}")

    # Test 6: Balance analysis
    print("\n[Test 6] Balance Analysis")
    print("-" * 40)
    balance = allocator.balance_to_center(allocs)
    print(f"Weighted Center: {balance['weighted_center']:.2f}")
    print(f"Ideal Center: {balance['ideal_center']}")
    print(f"Deviation: {balance['deviation']:.2f}")
    print(f"Balanced: {balance['balanced']}")

    # Test 7: Full budget report
    print("\n[Test 7] Budget Report (1000 units)")
    print("-" * 40)
    report = allocator.generate_budget_report(1000)
    print(report)

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
