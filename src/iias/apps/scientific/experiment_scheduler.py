"""
Experiment Scheduler - Lucas-Resource Allocation for Experiments
================================================================

Schedules scientific experiments using Lucas sequence for resource allocation.
Each experiment is assigned resources proportional to Lucas numbers, ensuring
PHI-optimal distribution across the 12-dimension parameter space.

Resource Tiers (based on Lucas sequence):
    Tier 1 (L1):  1 unit   - Quick tests
    Tier 2 (L2):  3 units  - Small experiments
    Tier 3 (L3):  4 units  - Standard experiments
    Tier 4 (L4):  7 units  - Extended experiments
    ...
    Tier 10 (L10): 123 units - D10 Wisdom capacity
    ...
    Tier 12 (L12): 322 units - Maximum capacity
"""

import time
import heapq
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from datetime import datetime, timedelta

# Constants
PHI = 1.618033988749895
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
D10_CAPACITY = 123  # Wisdom dimension
TOTAL_STATES = 840


class ExperimentStatus(Enum):
    """Status of an experiment."""
    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ResourceTier(Enum):
    """Resource allocation tier based on Lucas sequence."""
    L1 = 1
    L2 = 2
    L3 = 3
    L4 = 4
    L5 = 5
    L6 = 6
    L7 = 7
    L8 = 8
    L9 = 9
    L10 = 10  # D10 Wisdom
    L11 = 11
    L12 = 12

    @property
    def capacity(self) -> int:
        """Get Lucas capacity for this tier."""
        return LUCAS[self.value - 1]


@dataclass(order=True)
class Experiment:
    """A scientific experiment with resource requirements."""
    priority: int = field(compare=True)  # Lower = higher priority
    exp_id: str = field(compare=False)
    name: str = field(compare=False)
    tier: ResourceTier = field(compare=False)
    duration_estimate_minutes: float = field(compare=False)
    status: ExperimentStatus = field(default=ExperimentStatus.PENDING, compare=False)
    created_at: datetime = field(default_factory=datetime.now, compare=False)
    started_at: Optional[datetime] = field(default=None, compare=False)
    completed_at: Optional[datetime] = field(default=None, compare=False)
    result: Optional[Any] = field(default=None, compare=False)

    @property
    def resource_units(self) -> int:
        """Get resource units required (Lucas capacity)."""
        return self.tier.capacity

    @property
    def phi_priority(self) -> float:
        """Calculate PHI-weighted priority."""
        # Higher tiers get slight priority boost via PHI
        return self.priority / (PHI ** (self.tier.value / 12.0))


@dataclass
class ScheduleSlot:
    """A scheduled time slot for an experiment."""
    experiment: Experiment
    start_time: datetime
    end_time: datetime
    allocated_resources: int


@dataclass
class SchedulerMetrics:
    """Metrics for the scheduler."""
    total_experiments: int
    completed_experiments: int
    running_experiments: int
    pending_experiments: int
    total_resources_used: int
    total_resources_available: int
    utilization_percent: float
    avg_wait_time_minutes: float


class ExperimentScheduler:
    """
    Schedules experiments using Lucas-based resource allocation.

    Features:
        - Priority queue with PHI-weighted ordering
        - Lucas-based resource tiers
        - D10 (Wisdom) capacity tracking
        - Automatic resource release on completion
    """

    def __init__(self, max_concurrent: int = 10):
        self.phi = PHI
        self.lucas = LUCAS
        self.total_states = TOTAL_STATES
        self.d10_capacity = D10_CAPACITY
        self.max_concurrent = max_concurrent

        # Priority queue for pending experiments
        self._pending: List[Experiment] = []
        heapq.heapify(self._pending)

        # Currently running experiments
        self._running: Dict[str, Experiment] = {}

        # Completed experiments
        self._completed: List[Experiment] = []

        # Resource tracking per tier
        self._tier_usage: Dict[ResourceTier, int] = {t: 0 for t in ResourceTier}

        # Total resources in use
        self._resources_in_use: int = 0

    def submit(self, experiment: Experiment) -> bool:
        """
        Submit an experiment for scheduling.

        Args:
            experiment: The experiment to schedule

        Returns:
            True if submitted successfully
        """
        if experiment.status != ExperimentStatus.PENDING:
            return False

        heapq.heappush(self._pending, experiment)
        return True

    def schedule_next(self) -> Optional[ScheduleSlot]:
        """
        Schedule the next pending experiment if resources available.

        Returns:
            ScheduleSlot if an experiment was scheduled, None otherwise
        """
        if not self._pending:
            return None

        if len(self._running) >= self.max_concurrent:
            return None

        # Peek at highest priority experiment
        experiment = self._pending[0]
        required = experiment.resource_units

        # Check if we have capacity
        tier_available = LUCAS[experiment.tier.value - 1] - self._tier_usage[experiment.tier]

        if required > tier_available:
            return None

        # Pop and schedule
        experiment = heapq.heappop(self._pending)
        experiment.status = ExperimentStatus.SCHEDULED
        experiment.started_at = datetime.now()

        # Allocate resources
        self._tier_usage[experiment.tier] += required
        self._resources_in_use += required

        # Create schedule slot
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=experiment.duration_estimate_minutes)

        slot = ScheduleSlot(
            experiment=experiment,
            start_time=start_time,
            end_time=end_time,
            allocated_resources=required
        )

        # Move to running
        experiment.status = ExperimentStatus.RUNNING
        self._running[experiment.exp_id] = experiment

        return slot

    def complete(self, exp_id: str, result: Any = None, success: bool = True) -> bool:
        """
        Mark an experiment as completed and release resources.

        Args:
            exp_id: Experiment ID
            result: Optional result data
            success: Whether the experiment succeeded

        Returns:
            True if completed successfully
        """
        if exp_id not in self._running:
            return False

        experiment = self._running.pop(exp_id)
        experiment.completed_at = datetime.now()
        experiment.result = result
        experiment.status = ExperimentStatus.COMPLETED if success else ExperimentStatus.FAILED

        # Release resources
        released = experiment.resource_units
        self._tier_usage[experiment.tier] -= released
        self._resources_in_use -= released

        self._completed.append(experiment)
        return True

    def cancel(self, exp_id: str) -> bool:
        """Cancel a pending or running experiment."""
        # Check pending
        for i, exp in enumerate(self._pending):
            if exp.exp_id == exp_id:
                exp.status = ExperimentStatus.CANCELLED
                del self._pending[i]
                heapq.heapify(self._pending)
                self._completed.append(exp)
                return True

        # Check running
        if exp_id in self._running:
            return self.complete(exp_id, result="Cancelled", success=False)

        return False

    def get_lucas_allocation(self) -> Dict[str, Any]:
        """Get current Lucas-based resource allocation."""
        allocation = {
            "tiers": {},
            "total_capacity": self.total_states,
            "total_used": self._resources_in_use,
            "utilization": self._resources_in_use / self.total_states,
        }

        for tier in ResourceTier:
            capacity = LUCAS[tier.value - 1]
            used = self._tier_usage[tier]
            allocation["tiers"][f"L{tier.value}"] = {
                "capacity": capacity,
                "used": used,
                "available": capacity - used,
                "utilization": used / capacity if capacity > 0 else 0.0
            }

        return allocation

    def get_d10_status(self) -> Dict[str, Any]:
        """Get D10 (Wisdom) dimension status specifically."""
        used = self._tier_usage[ResourceTier.L10]
        return {
            "dimension": "D10 (Wisdom)",
            "capacity": self.d10_capacity,
            "used": used,
            "available": self.d10_capacity - used,
            "utilization": used / self.d10_capacity,
        }

    def get_metrics(self) -> SchedulerMetrics:
        """Get scheduler metrics."""
        completed_times = [
            (e.completed_at - e.created_at).total_seconds() / 60.0
            for e in self._completed
            if e.completed_at and e.status == ExperimentStatus.COMPLETED
        ]

        avg_wait = sum(completed_times) / len(completed_times) if completed_times else 0.0

        return SchedulerMetrics(
            total_experiments=len(self._pending) + len(self._running) + len(self._completed),
            completed_experiments=len([e for e in self._completed if e.status == ExperimentStatus.COMPLETED]),
            running_experiments=len(self._running),
            pending_experiments=len(self._pending),
            total_resources_used=self._resources_in_use,
            total_resources_available=self.total_states,
            utilization_percent=(self._resources_in_use / self.total_states) * 100,
            avg_wait_time_minutes=avg_wait
        )

    def schedule_batch(self) -> List[ScheduleSlot]:
        """Schedule as many experiments as possible."""
        slots = []
        while True:
            slot = self.schedule_next()
            if slot is None:
                break
            slots.append(slot)
        return slots


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Experiment Scheduler Test")
    print("=" * 60)

    scheduler = ExperimentScheduler(max_concurrent=5)

    # Display constants
    print(f"\nPHI = {PHI}")
    print(f"LUCAS = {LUCAS}")
    print(f"D10_CAPACITY = {D10_CAPACITY}")
    print(f"TOTAL_STATES = {TOTAL_STATES}")

    # Display tier capacities
    print("\n--- Lucas Resource Tiers ---")
    for tier in ResourceTier:
        print(f"  {tier.name}: {tier.capacity:3d} units")

    # Submit test experiments
    print("\n--- Submitting Experiments ---")
    experiments = [
        Experiment(priority=1, exp_id="exp-001", name="Quick Validation",
                   tier=ResourceTier.L1, duration_estimate_minutes=5),
        Experiment(priority=2, exp_id="exp-002", name="Standard Analysis",
                   tier=ResourceTier.L3, duration_estimate_minutes=30),
        Experiment(priority=1, exp_id="exp-003", name="Wisdom Insight",
                   tier=ResourceTier.L10, duration_estimate_minutes=120),
        Experiment(priority=3, exp_id="exp-004", name="Pattern Discovery",
                   tier=ResourceTier.L6, duration_estimate_minutes=60),
        Experiment(priority=2, exp_id="exp-005", name="Full Synthesis",
                   tier=ResourceTier.L12, duration_estimate_minutes=240),
    ]

    for exp in experiments:
        scheduler.submit(exp)
        print(f"  Submitted: {exp.name} (L{exp.tier.value}, {exp.resource_units} units)")

    # Schedule batch
    print("\n--- Scheduling Batch ---")
    slots = scheduler.schedule_batch()
    for slot in slots:
        print(f"  Scheduled: {slot.experiment.name}")
        print(f"    Resources: {slot.allocated_resources} units")
        print(f"    Duration: {slot.experiment.duration_estimate_minutes} min")

    # Show Lucas allocation
    print("\n--- Lucas Resource Allocation ---")
    allocation = scheduler.get_lucas_allocation()
    print(f"  Total: {allocation['total_used']}/{allocation['total_capacity']} "
          f"({allocation['utilization']:.1%})")
    for tier_name, info in allocation["tiers"].items():
        if info["used"] > 0:
            print(f"  {tier_name}: {info['used']}/{info['capacity']} used")

    # Show D10 status
    print("\n--- D10 (Wisdom) Status ---")
    d10 = scheduler.get_d10_status()
    print(f"  Capacity: {d10['capacity']}")
    print(f"  Used: {d10['used']}")
    print(f"  Available: {d10['available']}")
    print(f"  Utilization: {d10['utilization']:.1%}")

    # Complete some experiments
    print("\n--- Completing Experiments ---")
    for slot in slots[:2]:
        scheduler.complete(slot.experiment.exp_id, result="Success")
        print(f"  Completed: {slot.experiment.name}")

    # Show final metrics
    print("\n--- Scheduler Metrics ---")
    metrics = scheduler.get_metrics()
    print(f"  Total experiments: {metrics.total_experiments}")
    print(f"  Completed: {metrics.completed_experiments}")
    print(f"  Running: {metrics.running_experiments}")
    print(f"  Pending: {metrics.pending_experiments}")
    print(f"  Resource utilization: {metrics.utilization_percent:.1f}%")

    print("\n" + "=" * 60)
    print("Experiment Scheduler Test Complete")
    print("=" * 60)
