"""
Task Scheduler - Lucas-Priority Queuing

Implements a task scheduling system where priority levels are derived
from the Lucas sequence. Tasks are queued and processed based on
their Lucas-weighted priorities.

Constants:
- LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
- PHI = 1.618033988749895 (Lucas[n]/Lucas[n-1] approaches PHI)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any
from enum import IntEnum
from datetime import datetime, timedelta
import heapq
import time

# IIAS Constants
PHI = 1.618033988749895
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]


class LucasPriority(IntEnum):
    """
    Priority levels based on Lucas sequence values.
    Higher Lucas numbers = higher priority.
    """
    P1_MINIMAL = 0      # Lucas[0] = 1
    P2_LOW = 1          # Lucas[1] = 3
    P3_BELOW_NORMAL = 2 # Lucas[2] = 4
    P4_NORMAL = 3       # Lucas[3] = 7
    P5_ABOVE_NORMAL = 4 # Lucas[4] = 11
    P6_HIGH = 5         # Lucas[5] = 18
    P7_ELEVATED = 6     # Lucas[6] = 29
    P8_URGENT = 7       # Lucas[7] = 47
    P9_CRITICAL = 8     # Lucas[8] = 76
    P10_EMERGENCY = 9   # Lucas[9] = 123
    P11_EXTREME = 10    # Lucas[10] = 199
    P12_MAXIMUM = 11    # Lucas[11] = 322

    @property
    def lucas_value(self) -> int:
        """Get the Lucas sequence value for this priority."""
        return LUCAS[self.value]


@dataclass(order=True)
class Task:
    """
    A task with Lucas-based priority scheduling.

    Tasks are ordered by:
    1. Lucas priority value (descending - higher is more urgent)
    2. Deadline (ascending - earlier deadlines first)
    3. Creation time (ascending - FIFO for same priority)
    """
    priority_sort: int = field(init=False, repr=False)
    deadline_sort: float = field(init=False, repr=False)
    creation_sort: float = field(init=False, repr=False)

    task_id: str = field(compare=False)
    name: str = field(compare=False)
    priority: LucasPriority = field(compare=False)
    deadline: Optional[datetime] = field(default=None, compare=False)
    created_at: datetime = field(default_factory=datetime.now, compare=False)
    payload: Any = field(default=None, compare=False)
    estimated_duration: float = field(default=0.0, compare=False)  # seconds

    def __post_init__(self):
        # Negative Lucas value so higher priority sorts first
        self.priority_sort = -LUCAS[self.priority.value]
        # Deadline timestamp (or max float if no deadline)
        self.deadline_sort = (self.deadline.timestamp()
                              if self.deadline else float('inf'))
        self.creation_sort = self.created_at.timestamp()

    @property
    def lucas_weight(self) -> int:
        """Get the Lucas weight for this task's priority."""
        return LUCAS[self.priority.value]


@dataclass
class TaskResult:
    """Result of task execution."""
    task_id: str
    task_name: str
    success: bool
    execution_time: float
    result: Any = None
    error: Optional[str] = None


class TaskScheduler:
    """
    Lucas-priority task scheduler.

    Uses a priority queue where tasks are weighted by Lucas sequence
    values. Higher Lucas numbers indicate higher priority.
    """

    def __init__(self, max_queue_size: int = 1000):
        """
        Initialize the scheduler.

        Args:
            max_queue_size: Maximum number of tasks in queue
        """
        self.max_queue_size = max_queue_size
        self._queue: List[Task] = []
        self._task_counter = 0
        self._completed: List[TaskResult] = []
        self._handlers: dict = {}

    def register_handler(self, task_type: str,
                         handler: Callable[[Task], Any]) -> None:
        """Register a handler function for a task type."""
        self._handlers[task_type] = handler

    def submit(self, name: str, priority: LucasPriority,
               deadline: Optional[datetime] = None,
               payload: Any = None,
               estimated_duration: float = 0.0) -> Task:
        """
        Submit a task to the scheduler.

        Args:
            name: Task name/type
            priority: Lucas priority level
            deadline: Optional deadline
            payload: Task data
            estimated_duration: Estimated execution time in seconds

        Returns:
            The created Task object
        """
        if len(self._queue) >= self.max_queue_size:
            raise RuntimeError(f"Queue full (max {self.max_queue_size})")

        self._task_counter += 1
        task = Task(
            task_id=f"TASK-{self._task_counter:06d}",
            name=name,
            priority=priority,
            deadline=deadline,
            payload=payload,
            estimated_duration=estimated_duration
        )

        heapq.heappush(self._queue, task)
        return task

    def peek(self) -> Optional[Task]:
        """View the next task without removing it."""
        return self._queue[0] if self._queue else None

    def pop(self) -> Optional[Task]:
        """Remove and return the highest priority task."""
        if self._queue:
            return heapq.heappop(self._queue)
        return None

    def execute_next(self) -> Optional[TaskResult]:
        """Execute the next task in queue."""
        task = self.pop()
        if not task:
            return None

        start_time = time.time()
        try:
            handler = self._handlers.get(task.name)
            if handler:
                result = handler(task)
                success = True
                error = None
            else:
                result = task.payload
                success = True
                error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)

        execution_time = time.time() - start_time

        task_result = TaskResult(
            task_id=task.task_id,
            task_name=task.name,
            success=success,
            execution_time=execution_time,
            result=result,
            error=error
        )
        self._completed.append(task_result)
        return task_result

    def execute_all(self) -> List[TaskResult]:
        """Execute all tasks in priority order."""
        results = []
        while self._queue:
            result = self.execute_next()
            if result:
                results.append(result)
        return results

    def get_queue_stats(self) -> dict:
        """Get statistics about the current queue."""
        if not self._queue:
            return {
                "queue_size": 0,
                "total_lucas_weight": 0,
                "avg_lucas_weight": 0,
                "priority_distribution": {}
            }

        priority_counts = {}
        total_weight = 0

        for task in self._queue:
            priority_counts[task.priority.name] = \
                priority_counts.get(task.priority.name, 0) + 1
            total_weight += task.lucas_weight

        return {
            "queue_size": len(self._queue),
            "total_lucas_weight": total_weight,
            "avg_lucas_weight": total_weight / len(self._queue),
            "priority_distribution": priority_counts,
            "phi_ratio_check": self._check_phi_ratio()
        }

    def _check_phi_ratio(self) -> dict:
        """Verify Lucas/PHI relationship in queue weights."""
        if len(self._queue) < 2:
            return {"valid": False, "reason": "insufficient_tasks"}

        # Get top two priorities
        sorted_tasks = sorted(self._queue, key=lambda t: t.lucas_weight, reverse=True)
        if len(sorted_tasks) >= 2:
            w1 = sorted_tasks[0].lucas_weight
            w2 = sorted_tasks[1].lucas_weight
            ratio = w1 / w2 if w2 > 0 else 0
            return {
                "valid": True,
                "ratio": ratio,
                "approaches_phi": abs(ratio - PHI) < 0.5,
                "phi": PHI
            }
        return {"valid": False, "reason": "calculation_error"}

    def get_lucas_priority_table(self) -> List[dict]:
        """Get the complete Lucas priority mapping table."""
        return [
            {
                "level": p.name,
                "index": p.value,
                "lucas_value": LUCAS[p.value],
                "relative_weight": LUCAS[p.value] / LUCAS[0]
            }
            for p in LucasPriority
        ]

    @property
    def queue_size(self) -> int:
        """Current number of tasks in queue."""
        return len(self._queue)

    @property
    def completed_count(self) -> int:
        """Number of completed tasks."""
        return len(self._completed)


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Task Scheduler - Lucas-Priority Queuing")
    print("=" * 60)
    print(f"\nLucas Sequence: {LUCAS}")
    print(f"PHI (limit of Lucas[n]/Lucas[n-1]): {PHI:.6f}")

    # Create scheduler
    scheduler = TaskScheduler()

    # Show Lucas priority table
    print("\n--- Lucas Priority Levels ---")
    for level in scheduler.get_lucas_priority_table():
        print(f"  {level['level']:20} | Index: {level['index']:2} | "
              f"Lucas: {level['lucas_value']:3} | Weight: {level['relative_weight']:.1f}x")

    # Submit test tasks
    print("\n--- Submitting Tasks ---")
    tasks = [
        ("Backup Database", LucasPriority.P8_URGENT),
        ("Send Newsletter", LucasPriority.P4_NORMAL),
        ("Security Patch", LucasPriority.P10_EMERGENCY),
        ("Update Docs", LucasPriority.P2_LOW),
        ("Deploy Feature", LucasPriority.P6_HIGH),
        ("Fix Critical Bug", LucasPriority.P9_CRITICAL),
        ("Code Review", LucasPriority.P5_ABOVE_NORMAL),
        ("Clean Logs", LucasPriority.P1_MINIMAL),
    ]

    for name, priority in tasks:
        task = scheduler.submit(name, priority)
        print(f"  Submitted: {task.task_id} | {name:20} | "
              f"Priority: {priority.name} (Lucas={priority.lucas_value})")

    # Queue statistics
    print("\n--- Queue Statistics ---")
    stats = scheduler.get_queue_stats()
    print(f"  Queue Size:        {stats['queue_size']}")
    print(f"  Total Lucas Weight: {stats['total_lucas_weight']}")
    print(f"  Avg Lucas Weight:   {stats['avg_lucas_weight']:.1f}")
    print(f"\n  Priority Distribution:")
    for p, count in sorted(stats['priority_distribution'].items()):
        print(f"    {p}: {count}")

    # Check PHI ratio
    phi_check = stats['phi_ratio_check']
    if phi_check['valid']:
        print(f"\n  Top weights ratio: {phi_check['ratio']:.4f}")
        print(f"  Approaches PHI ({PHI:.4f}): {phi_check['approaches_phi']}")

    # Execute tasks in priority order
    print("\n--- Executing Tasks (Priority Order) ---")
    execution_order = []
    while scheduler.queue_size > 0:
        task = scheduler.peek()
        print(f"  Executing: {task.name:20} | "
              f"Lucas Weight: {task.lucas_weight:3}")
        result = scheduler.execute_next()
        execution_order.append((task.name, task.lucas_weight))

    # Verify Lucas ordering
    print("\n--- Lucas Priority Verification ---")
    weights = [w for _, w in execution_order]
    is_sorted = all(weights[i] >= weights[i+1] for i in range(len(weights)-1))
    print(f"  Execution order by Lucas weight: {weights}")
    print(f"  Correctly ordered (descending): {'VERIFIED' if is_sorted else 'FAILED'}")

    # Show Lucas sequence convergence to PHI
    print("\n--- Lucas Sequence PHI Convergence ---")
    for i in range(1, len(LUCAS)):
        ratio = LUCAS[i] / LUCAS[i-1]
        diff = abs(ratio - PHI)
        print(f"  L[{i}]/L[{i-1}] = {LUCAS[i]:3}/{LUCAS[i-1]:3} = {ratio:.6f} "
              f"(diff from PHI: {diff:.6f})")
