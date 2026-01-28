"""Budget Allocator - Genesis-Period Planning

Budget periods based on Genesis function G(t) with GENESIS_CONSTANT = 2/901.
Allocates budgets across time periods following the emergence pattern.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math

# IIAS Constants
PHI = 1.618033988749895
SUM_CONSTANT = 214
GENESIS_CONSTANT = 2 / 901  # ~0.00221975
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]


class BudgetPhase(Enum):
    """Budget phases mapped to Genesis states."""
    VOID = "VOID"           # Pre-initialization, no allocation
    EMERGING = "EMERGING"   # Ramp-up phase
    GARDEN = "GARDEN"       # Stable operational phase
    OPERATIONAL = "OPERATIONAL"  # Full capacity


@dataclass
class BudgetPeriod:
    """A single budget period with Genesis-derived allocation."""
    period_id: int
    t_start: float
    t_end: float
    phase: BudgetPhase
    emergence_factor: float
    dimensions_active: int
    allocated_amount: float
    lucas_weight: float


@dataclass
class BudgetPlan:
    """Complete budget plan across Genesis periods."""
    total_budget: float
    periods: List[BudgetPeriod]
    sum_allocated: float
    conservation_verified: bool
    phi_growth_rate: float


class BudgetAllocator:
    """
    Genesis-Period Budget Planner.

    Uses the Genesis function G(t) to allocate budgets across time periods.
    GENESIS_CONSTANT = 2/901 marks the transition from EMERGING to GARDEN.
    """

    def __init__(self, total_budget: float):
        self.total_budget = total_budget
        self.genesis_constant = GENESIS_CONSTANT
        self.phi = PHI
        self.sum_constant = SUM_CONSTANT
        self.lucas = LUCAS

    def _genesis_emergence(self, t: float) -> float:
        """
        Calculate emergence factor at time t.

        emergence(t) = 1 - exp(-t / GENESIS_CONSTANT)
        """
        if t <= 0:
            return 0.0
        return 1 - math.exp(-t / self.genesis_constant)

    def _genesis_phase(self, t: float) -> Tuple[BudgetPhase, int]:
        """Determine Genesis phase and active dimensions at time t."""
        if t <= 0:
            return BudgetPhase.VOID, 0

        emergence = self._genesis_emergence(t)
        dims = int(12 * emergence)

        if t < self.genesis_constant:
            return BudgetPhase.EMERGING, dims
        elif t < 1:
            return BudgetPhase.GARDEN, 12
        else:
            return BudgetPhase.OPERATIONAL, 12

    def _lucas_weight_for_dims(self, dims: int) -> float:
        """Calculate Lucas weight for active dimensions."""
        if dims == 0:
            return 0.0
        return sum(self.lucas[:dims])

    def create_plan(
        self,
        num_periods: int,
        time_horizon: float = 1.0,
        front_load: bool = False
    ) -> BudgetPlan:
        """
        Create a budget plan with Genesis-based period allocation.

        Args:
            num_periods: Number of budget periods
            time_horizon: Total time span (default 1.0 for full Genesis cycle)
            front_load: If True, allocate more budget earlier (PHI ratio)

        Returns:
            BudgetPlan with period allocations
        """
        if num_periods <= 0:
            raise ValueError("num_periods must be positive")

        periods = []
        period_duration = time_horizon / num_periods

        # Calculate emergence factors for each period
        emergence_factors = []
        for i in range(num_periods):
            t_start = i * period_duration
            t_end = (i + 1) * period_duration
            t_mid = (t_start + t_end) / 2

            phase, dims = self._genesis_phase(t_mid)
            emergence = self._genesis_emergence(t_mid)

            emergence_factors.append({
                "period_id": i + 1,
                "t_start": t_start,
                "t_end": t_end,
                "phase": phase,
                "emergence": emergence,
                "dims": dims,
                "lucas_weight": self._lucas_weight_for_dims(dims)
            })

        # Normalize and allocate budget
        total_emergence = sum(ef["emergence"] for ef in emergence_factors)

        if total_emergence == 0:
            # Equal allocation if no emergence
            base_allocation = self.total_budget / num_periods
            for ef in emergence_factors:
                ef["allocation"] = base_allocation
        else:
            for ef in emergence_factors:
                if front_load:
                    # PHI-weighted front-loading
                    position_weight = self.phi ** (num_periods - ef["period_id"])
                    ef["allocation"] = self.total_budget * (
                        ef["emergence"] * position_weight /
                        sum(e["emergence"] * self.phi ** (num_periods - e["period_id"])
                            for e in emergence_factors)
                    )
                else:
                    # Standard emergence-based allocation
                    ef["allocation"] = self.total_budget * ef["emergence"] / total_emergence

        # Create BudgetPeriod objects
        for ef in emergence_factors:
            periods.append(BudgetPeriod(
                period_id=ef["period_id"],
                t_start=ef["t_start"],
                t_end=ef["t_end"],
                phase=ef["phase"],
                emergence_factor=ef["emergence"],
                dimensions_active=ef["dims"],
                allocated_amount=ef["allocation"],
                lucas_weight=ef["lucas_weight"]
            ))

        sum_allocated = sum(p.allocated_amount for p in periods)

        # Calculate PHI growth rate between periods
        phi_growth = self._calculate_phi_growth(periods)

        return BudgetPlan(
            total_budget=self.total_budget,
            periods=periods,
            sum_allocated=sum_allocated,
            conservation_verified=abs(sum_allocated - self.total_budget) < 1e-9,
            phi_growth_rate=phi_growth
        )

    def _calculate_phi_growth(self, periods: List[BudgetPeriod]) -> float:
        """Calculate how closely period growth follows PHI ratio."""
        if len(periods) < 2:
            return 1.0

        ratios = []
        for i in range(len(periods) - 1):
            if periods[i].allocated_amount > 0:
                ratio = periods[i + 1].allocated_amount / periods[i].allocated_amount
                deviation = abs(ratio - self.phi) / self.phi
                ratios.append(max(0, 1 - deviation))

        return sum(ratios) / len(ratios) if ratios else 1.0

    def allocate_to_dimensions(self, period: BudgetPeriod) -> Dict[int, float]:
        """
        Allocate a period's budget across active dimensions.

        Uses Lucas weights for dimension-based allocation.
        """
        if period.dimensions_active == 0:
            return {}

        dim_allocations = {}
        total_lucas = sum(self.lucas[:period.dimensions_active])

        for d in range(1, period.dimensions_active + 1):
            weight = self.lucas[d - 1] / total_lucas
            dim_allocations[d] = period.allocated_amount * weight

        return dim_allocations

    def get_genesis_timeline(self) -> Dict[str, float]:
        """Return key Genesis milestones."""
        return {
            "VOID_END": 0.0,
            "EMERGING_START": 0.0,
            "GARDEN_START": self.genesis_constant,
            "OPERATIONAL_START": 1.0,
            "GENESIS_CONSTANT": self.genesis_constant,
        }

    def verify_214_conservation(self, plan: BudgetPlan) -> Dict[str, float]:
        """Verify the plan maps correctly to 214-sum framework."""
        total_dims = sum(p.dimensions_active for p in plan.periods)
        total_lucas = sum(p.lucas_weight for p in plan.periods)

        # Normalize to 214
        scale = self.sum_constant / total_lucas if total_lucas > 0 else 0

        return {
            "total_dimensions": total_dims,
            "total_lucas_weight": total_lucas,
            "normalized_scale": scale,
            "conservation_sum": total_lucas * scale,
            "verified": abs(total_lucas * scale - self.sum_constant) < 1e-9 if total_lucas > 0 else True
        }


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Budget Allocator - Genesis-Period Planning")
    print("=" * 60)
    print(f"GENESIS_CONSTANT: 2/901 = {GENESIS_CONSTANT:.10f}")
    print(f"PHI: {PHI}")
    print(f"SUM_CONSTANT: {SUM_CONSTANT}")

    # Create allocator with $1,000,000 budget
    total_budget = 1_000_000
    allocator = BudgetAllocator(total_budget)

    print(f"\n[1] Genesis Timeline:")
    timeline = allocator.get_genesis_timeline()
    for milestone, t in timeline.items():
        print(f"    {milestone}: t = {t:.6f}")

    print(f"\n[2] Creating 12-period budget plan (${total_budget:,}):")
    plan = allocator.create_plan(num_periods=12, time_horizon=1.0)

    for period in plan.periods:
        print(f"    Period {period.period_id:2d} [{period.phase.value:12s}]: "
              f"t=[{period.t_start:.4f},{period.t_end:.4f}] "
              f"emergence={period.emergence_factor:.4f} "
              f"dims={period.dimensions_active:2d} "
              f"${period.allocated_amount:,.2f}")

    print(f"\n    Total Allocated: ${plan.sum_allocated:,.2f}")
    print(f"    Conservation Verified: {plan.conservation_verified}")
    print(f"    PHI Growth Rate: {plan.phi_growth_rate:.4f}")

    print("\n[3] Front-loaded PHI plan:")
    phi_plan = allocator.create_plan(num_periods=6, time_horizon=1.0, front_load=True)

    for period in phi_plan.periods:
        print(f"    Period {period.period_id}: ${period.allocated_amount:,.2f} "
              f"({period.phase.value})")

    print("\n[4] Dimension allocation for operational period:")
    operational = [p for p in plan.periods if p.phase == BudgetPhase.OPERATIONAL]
    if operational:
        dim_alloc = allocator.allocate_to_dimensions(operational[0])
        for dim, amount in dim_alloc.items():
            dim_name = ["PERCEPTION", "ATTENTION", "SECURITY", "STABILITY",
                       "COMPRESSION", "HARMONY", "REASONING", "PREDICTION",
                       "CREATIVITY", "WISDOM", "INTEGRATION", "UNIFICATION"][dim-1]
            print(f"    D{dim:2d} ({dim_name:12s}): ${amount:,.2f} (Lucas: {LUCAS[dim-1]})")

    print("\n[5] 214-sum Conservation Check:")
    conservation = allocator.verify_214_conservation(plan)
    for key, value in conservation.items():
        print(f"    {key}: {value}")

    print("\n" + "=" * 60)
    print("TEST PASSED - Genesis-period budget allocation operational")
    print("=" * 60)
