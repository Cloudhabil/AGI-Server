"""IIAS Edge Battery Manager - 840-unit Lucas-based Energy Budget

This module manages energy consumption using Lucas numbers to allocate
energy across different computational tiers. The total budget is 840 units,
distributed according to Lucas sequence proportions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import time

# Constants
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
TOTAL_STATES = 840
PHI = 1.618033988749895


class EnergyTier(Enum):
    """Energy tiers mapped to Lucas indices."""
    MICRO = 0      # L[0] = 1 unit
    TINY = 1       # L[1] = 3 units
    SMALL = 2      # L[2] = 4 units
    LIGHT = 3      # L[3] = 7 units
    MEDIUM = 4     # L[4] = 11 units
    STANDARD = 5   # L[5] = 18 units
    HEAVY = 6      # L[6] = 29 units
    INTENSE = 7    # L[7] = 47 units
    EXTREME = 8    # L[8] = 76 units
    CRITICAL = 9   # L[9] = 123 units
    MAXIMUM = 10   # L[10] = 199 units
    BURST = 11     # L[11] = 322 units


@dataclass
class EnergyAllocation:
    """Represents an energy allocation request and result."""
    tier: EnergyTier
    units_requested: int
    units_allocated: int
    timestamp: float = field(default_factory=time.time)
    task_id: Optional[str] = None

    @property
    def fulfilled(self) -> bool:
        return self.units_allocated >= self.units_requested


@dataclass
class BatteryState:
    """Current battery state."""
    total_capacity: int = TOTAL_STATES
    available: int = TOTAL_STATES
    reserved: int = 0
    consumed: int = 0

    @property
    def utilization(self) -> float:
        """Return utilization as a percentage."""
        return (self.consumed / self.total_capacity) * 100 if self.total_capacity > 0 else 0.0

    @property
    def remaining_percent(self) -> float:
        """Return remaining energy as a percentage."""
        return (self.available / self.total_capacity) * 100 if self.total_capacity > 0 else 0.0


class BatteryManager:
    """
    Manages 840-unit energy budget using Lucas number allocations.

    The Lucas sequence provides natural energy tier boundaries:
    - Sum of first 12 Lucas numbers = 840
    - Each tier represents a computational intensity level
    - PHI-based scaling ensures harmonious energy distribution
    """

    def __init__(self, initial_capacity: int = TOTAL_STATES):
        self._state = BatteryState(total_capacity=initial_capacity, available=initial_capacity)
        self._allocations: List[EnergyAllocation] = []
        self._reservations: Dict[str, int] = {}
        self._lucas = LUCAS.copy()

    @property
    def state(self) -> BatteryState:
        """Get current battery state."""
        return self._state

    @property
    def lucas_tiers(self) -> List[int]:
        """Get Lucas number tiers."""
        return self._lucas.copy()

    def get_tier_cost(self, tier: EnergyTier) -> int:
        """Get energy cost for a specific tier."""
        return self._lucas[tier.value]

    def can_allocate(self, tier: EnergyTier) -> bool:
        """Check if tier allocation is possible."""
        required = self._lucas[tier.value]
        return self._state.available >= required

    def allocate(self, tier: EnergyTier, task_id: Optional[str] = None) -> EnergyAllocation:
        """
        Allocate energy for a task based on its tier.

        Args:
            tier: The energy tier required
            task_id: Optional identifier for the task

        Returns:
            EnergyAllocation with results
        """
        required = self._lucas[tier.value]
        allocated = min(required, self._state.available)

        if allocated > 0:
            self._state.available -= allocated
            self._state.consumed += allocated

        allocation = EnergyAllocation(
            tier=tier,
            units_requested=required,
            units_allocated=allocated,
            task_id=task_id
        )
        self._allocations.append(allocation)

        return allocation

    def allocate_custom(self, units: int, task_id: Optional[str] = None) -> EnergyAllocation:
        """
        Allocate a custom number of energy units.

        Args:
            units: Number of units to allocate
            task_id: Optional task identifier

        Returns:
            EnergyAllocation with results
        """
        allocated = min(units, self._state.available)

        if allocated > 0:
            self._state.available -= allocated
            self._state.consumed += allocated

        # Find closest tier for logging
        closest_tier = EnergyTier.MICRO
        for tier in EnergyTier:
            if self._lucas[tier.value] <= units:
                closest_tier = tier

        allocation = EnergyAllocation(
            tier=closest_tier,
            units_requested=units,
            units_allocated=allocated,
            task_id=task_id
        )
        self._allocations.append(allocation)

        return allocation

    def reserve(self, task_id: str, units: int) -> bool:
        """
        Reserve energy for future use.

        Args:
            task_id: Unique task identifier
            units: Units to reserve

        Returns:
            True if reservation successful
        """
        if units > self._state.available:
            return False

        self._state.available -= units
        self._state.reserved += units
        self._reservations[task_id] = units
        return True

    def release_reservation(self, task_id: str) -> int:
        """
        Release a reservation back to available pool.

        Args:
            task_id: Task identifier to release

        Returns:
            Units released (0 if not found)
        """
        if task_id not in self._reservations:
            return 0

        units = self._reservations.pop(task_id)
        self._state.reserved -= units
        self._state.available += units
        return units

    def consume_reservation(self, task_id: str) -> int:
        """
        Consume a reserved allocation.

        Args:
            task_id: Task identifier to consume

        Returns:
            Units consumed (0 if not found)
        """
        if task_id not in self._reservations:
            return 0

        units = self._reservations.pop(task_id)
        self._state.reserved -= units
        self._state.consumed += units
        return units

    def recharge(self, units: int) -> int:
        """
        Recharge the battery.

        Args:
            units: Units to add

        Returns:
            Actual units added (capped at capacity)
        """
        max_recharge = self._state.total_capacity - self._state.available - self._state.reserved
        actual = min(units, max_recharge)

        if actual > 0:
            self._state.available += actual
            self._state.consumed = max(0, self._state.consumed - actual)

        return actual

    def reset(self) -> None:
        """Reset battery to full capacity."""
        self._state = BatteryState(
            total_capacity=self._state.total_capacity,
            available=self._state.total_capacity
        )
        self._allocations.clear()
        self._reservations.clear()

    def get_optimal_tier(self, max_units: Optional[int] = None) -> Optional[EnergyTier]:
        """
        Get the optimal tier that fits within available or specified budget.

        Args:
            max_units: Optional maximum units (uses available if None)

        Returns:
            Highest tier that fits, or None if none fit
        """
        budget = max_units if max_units is not None else self._state.available

        optimal = None
        for tier in reversed(list(EnergyTier)):
            if self._lucas[tier.value] <= budget:
                optimal = tier
                break

        return optimal

    def get_phi_scaled_budget(self, base_tier: EnergyTier) -> int:
        """
        Calculate PHI-scaled budget from a base tier.

        Args:
            base_tier: Starting tier for calculation

        Returns:
            PHI-scaled energy budget
        """
        base = self._lucas[base_tier.value]
        return int(base * PHI)

    def get_allocation_history(self) -> List[EnergyAllocation]:
        """Get allocation history."""
        return self._allocations.copy()

    def summary(self) -> Dict:
        """Get battery summary."""
        return {
            "total_capacity": self._state.total_capacity,
            "available": self._state.available,
            "reserved": self._state.reserved,
            "consumed": self._state.consumed,
            "utilization_percent": round(self._state.utilization, 2),
            "remaining_percent": round(self._state.remaining_percent, 2),
            "allocation_count": len(self._allocations),
            "active_reservations": len(self._reservations),
            "lucas_tiers": self._lucas,
        }


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Edge Battery Manager - Test Suite")
    print("=" * 60)

    # Initialize manager
    manager = BatteryManager()
    print(f"\nInitialized with {TOTAL_STATES} units (sum of Lucas[0:12])")
    print(f"Lucas sequence: {LUCAS}")
    print(f"Sum verification: {sum(LUCAS)} = {TOTAL_STATES}")

    # Test tier costs
    print("\n--- Tier Energy Costs ---")
    for tier in EnergyTier:
        cost = manager.get_tier_cost(tier)
        print(f"  {tier.name:10} = {cost:3} units")

    # Test allocations
    print("\n--- Allocation Tests ---")

    # Allocate several tiers
    test_tiers = [EnergyTier.SMALL, EnergyTier.MEDIUM, EnergyTier.HEAVY, EnergyTier.CRITICAL]
    for tier in test_tiers:
        alloc = manager.allocate(tier, task_id=f"task_{tier.name.lower()}")
        status = "OK" if alloc.fulfilled else "PARTIAL"
        print(f"  {tier.name}: requested={alloc.units_requested}, "
              f"allocated={alloc.units_allocated} [{status}]")

    print(f"\nState after allocations:")
    print(f"  Available: {manager.state.available}/{manager.state.total_capacity}")
    print(f"  Consumed: {manager.state.consumed}")
    print(f"  Utilization: {manager.state.utilization:.1f}%")

    # Test reservation
    print("\n--- Reservation Test ---")
    reserved = manager.reserve("future_task", 100)
    print(f"  Reserved 100 units: {reserved}")
    print(f"  Available after reserve: {manager.state.available}")
    print(f"  Reserved pool: {manager.state.reserved}")

    # Consume reservation
    consumed = manager.consume_reservation("future_task")
    print(f"  Consumed reservation: {consumed} units")

    # Test PHI scaling
    print("\n--- PHI Scaling Test ---")
    base = EnergyTier.STANDARD  # 18 units
    phi_budget = manager.get_phi_scaled_budget(base)
    print(f"  Base tier {base.name}: {manager.get_tier_cost(base)} units")
    print(f"  PHI-scaled ({PHI:.6f}): {phi_budget} units")

    # Test optimal tier selection
    print("\n--- Optimal Tier Selection ---")
    optimal = manager.get_optimal_tier(50)
    print(f"  Best tier for 50 units: {optimal.name if optimal else 'None'} "
          f"(cost={manager.get_tier_cost(optimal) if optimal else 0})")

    # Test recharge
    print("\n--- Recharge Test ---")
    recharged = manager.recharge(200)
    print(f"  Recharged: {recharged} units")
    print(f"  New available: {manager.state.available}")

    # Final summary
    print("\n--- Final Summary ---")
    summary = manager.summary()
    for key, value in summary.items():
        if key != "lucas_tiers":
            print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Battery Manager tests completed successfully!")
    print("=" * 60)
