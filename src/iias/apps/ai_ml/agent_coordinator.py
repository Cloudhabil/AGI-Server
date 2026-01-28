"""
Agent Coordinator - Coordinate up to 12 agents in parallel
==========================================================

Coordinates multiple AI agents, one per dimension, across the
IIAS 12-dimension architecture. Each agent operates on its
assigned silicon layer with its Lucas-capacity resources.

Agent Distribution:
    D1-D4 (NPU agents):  capacity 1+3+4+7 = 15
    D5-D8 (CPU agents):  capacity 11+18+29+47 = 105
    D9-D12 (GPU agents): capacity 76+123+199+322 = 720
    Total: 12 agents, 840 total capacity
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import time
import threading
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
import queue

# Constants
PHI = 1.618033988749895
TOTAL_STATES = 840
MAX_AGENTS = 12

# Lucas sequence for 12 dimensions
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]

# Dimension names and silicon mapping
DIMENSION_CONFIG = [
    ("PERCEPTION", "NPU"),
    ("ATTENTION", "NPU"),
    ("SECURITY", "NPU"),
    ("STABILITY", "NPU"),
    ("COMPRESSION", "CPU"),
    ("HARMONY", "CPU"),
    ("REASONING", "CPU"),
    ("PREDICTION", "CPU"),
    ("CREATIVITY", "GPU"),
    ("WISDOM", "GPU"),
    ("INTEGRATION", "GPU"),
    ("UNIFICATION", "GPU"),
]


class AgentState(Enum):
    """Agent operational states."""
    IDLE = "idle"
    RUNNING = "running"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentTask:
    """A task for an agent to execute."""
    task_id: str
    dimension: int
    payload: Any
    callback: Optional[Callable[[Any], None]] = None
    timeout_ms: float = 5000.0
    created_at: float = field(default_factory=time.time)


@dataclass
class AgentResult:
    """Result from an agent task execution."""
    task_id: str
    dimension: int
    success: bool
    result: Any
    duration_ms: float
    message: str = ""


class DimensionAgent:
    """
    An agent operating on a single dimension.

    Each agent has:
    - A dimension assignment (1-12)
    - Lucas capacity for that dimension
    - Silicon layer (NPU/CPU/GPU)
    """

    def __init__(self, dimension: int):
        if not 1 <= dimension <= 12:
            raise ValueError(f"Dimension must be 1-12, got {dimension}")

        self.dimension = dimension
        self.name = DIMENSION_CONFIG[dimension - 1][0]
        self.silicon = DIMENSION_CONFIG[dimension - 1][1]
        self.capacity = LUCAS[dimension - 1]

        self.state = AgentState.IDLE
        self.current_task: Optional[AgentTask] = None
        self._task_queue: queue.Queue = queue.Queue()

        # Statistics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_processing_ms = 0.0

    def submit(self, task: AgentTask) -> bool:
        """Submit a task to this agent."""
        if task.dimension != self.dimension:
            return False
        self._task_queue.put(task)
        return True

    def execute(self, task: AgentTask) -> AgentResult:
        """Execute a task synchronously."""
        start_time = time.time()
        self.state = AgentState.RUNNING
        self.current_task = task

        try:
            # Simulate dimension-specific processing
            result = self._process(task)

            duration_ms = (time.time() - start_time) * 1000
            self.tasks_completed += 1
            self.total_processing_ms += duration_ms

            return AgentResult(
                task_id=task.task_id,
                dimension=self.dimension,
                success=True,
                result=result,
                duration_ms=duration_ms,
                message=f"Agent D{self.dimension} completed"
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.tasks_failed += 1

            return AgentResult(
                task_id=task.task_id,
                dimension=self.dimension,
                success=False,
                result=None,
                duration_ms=duration_ms,
                message=f"Agent D{self.dimension} failed: {str(e)}"
            )

        finally:
            self.state = AgentState.IDLE
            self.current_task = None

    def _process(self, task: AgentTask) -> Any:
        """Process task based on dimension specialty."""
        # Simulate processing time based on capacity (larger = faster throughput)
        base_time = 0.01  # 10ms base
        process_time = base_time / (1 + math.log(self.capacity))

        time.sleep(process_time)

        # Return dimension-aware result
        return {
            "dimension": self.dimension,
            "name": self.name,
            "silicon": self.silicon,
            "capacity": self.capacity,
            "payload_processed": task.payload,
            "phi_factor": PHI ** (self.dimension / 12),
        }

    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        return {
            "dimension": self.dimension,
            "name": self.name,
            "silicon": self.silicon,
            "capacity": self.capacity,
            "state": self.state.value,
            "queue_size": self._task_queue.qsize(),
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "avg_processing_ms": (
                self.total_processing_ms / self.tasks_completed
                if self.tasks_completed > 0 else 0.0
            ),
        }


class AgentCoordinator:
    """
    Coordinates up to 12 agents operating in parallel.

    Each agent handles one dimension of the IIAS architecture,
    with agents grouped by silicon layer for efficient scheduling.
    """

    def __init__(self, max_parallel: int = MAX_AGENTS):
        self.phi = PHI
        self.total_states = TOTAL_STATES
        self.max_parallel = min(max_parallel, MAX_AGENTS)

        # Initialize agents for each dimension
        self.agents: Dict[int, DimensionAgent] = {
            d: DimensionAgent(d) for d in range(1, 13)
        }

        # Thread pool for parallel execution
        self._executor = ThreadPoolExecutor(max_workers=self.max_parallel)

        # Task tracking
        self._task_counter = 0
        self._pending_futures: Dict[str, Future] = {}

        # Coordination lock
        self._lock = threading.Lock()

    def submit_task(self, dimension: int, payload: Any,
                    callback: Optional[Callable[[AgentResult], None]] = None,
                    timeout_ms: float = 5000.0) -> str:
        """
        Submit a task to a specific dimension's agent.

        Args:
            dimension: Target dimension (1-12)
            payload: Task payload
            callback: Optional callback for result
            timeout_ms: Task timeout

        Returns:
            Task ID
        """
        if not 1 <= dimension <= 12:
            raise ValueError(f"Invalid dimension: {dimension}")

        with self._lock:
            self._task_counter += 1
            task_id = f"task-{self._task_counter:06d}"

        task = AgentTask(
            task_id=task_id,
            dimension=dimension,
            payload=payload,
            callback=callback,
            timeout_ms=timeout_ms
        )

        agent = self.agents[dimension]

        def execute_with_callback():
            result = agent.execute(task)
            if callback:
                callback(result)
            return result

        future = self._executor.submit(execute_with_callback)
        self._pending_futures[task_id] = future

        return task_id

    def submit_parallel(self, tasks: List[tuple]) -> List[str]:
        """
        Submit multiple tasks in parallel.

        Args:
            tasks: List of (dimension, payload) tuples

        Returns:
            List of task IDs
        """
        task_ids = []
        for dimension, payload in tasks:
            task_id = self.submit_task(dimension, payload)
            task_ids.append(task_id)
        return task_ids

    def broadcast(self, payload: Any) -> List[str]:
        """
        Broadcast a task to all 12 agents.

        Args:
            payload: Task payload for all agents

        Returns:
            List of task IDs
        """
        tasks = [(d, payload) for d in range(1, 13)]
        return self.submit_parallel(tasks)

    def wait_for(self, task_id: str, timeout_s: float = 10.0) -> Optional[AgentResult]:
        """Wait for a specific task to complete."""
        future = self._pending_futures.get(task_id)
        if future is None:
            return None

        try:
            result = future.result(timeout=timeout_s)
            del self._pending_futures[task_id]
            return result
        except Exception as e:
            return AgentResult(
                task_id=task_id,
                dimension=0,
                success=False,
                result=None,
                duration_ms=0,
                message=f"Wait failed: {str(e)}"
            )

    def wait_all(self, task_ids: List[str], timeout_s: float = 30.0) -> List[AgentResult]:
        """Wait for multiple tasks to complete."""
        results = []
        futures = [self._pending_futures.get(tid) for tid in task_ids if tid in self._pending_futures]

        for future in as_completed(futures, timeout=timeout_s):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append(AgentResult(
                    task_id="unknown",
                    dimension=0,
                    success=False,
                    result=None,
                    duration_ms=0,
                    message=f"Task failed: {str(e)}"
                ))

        # Clean up
        for tid in task_ids:
            self._pending_futures.pop(tid, None)

        return results

    def get_agent_status(self, dimension: int) -> Dict[str, Any]:
        """Get status of a specific agent."""
        if dimension not in self.agents:
            return {}
        return self.agents[dimension].get_status()

    def get_status(self) -> Dict[str, Any]:
        """Get coordinator status."""
        # Group agents by silicon
        silicon_groups = {
            "NPU": {"dimensions": [1, 2, 3, 4], "capacity": sum(LUCAS[0:4]), "agents": []},
            "CPU": {"dimensions": [5, 6, 7, 8], "capacity": sum(LUCAS[4:8]), "agents": []},
            "GPU": {"dimensions": [9, 10, 11, 12], "capacity": sum(LUCAS[8:12]), "agents": []},
        }

        total_completed = 0
        total_failed = 0

        for dim, agent in self.agents.items():
            status = agent.get_status()
            total_completed += status["tasks_completed"]
            total_failed += status["tasks_failed"]

            for silicon, group in silicon_groups.items():
                if dim in group["dimensions"]:
                    group["agents"].append(status)

        return {
            "max_parallel": self.max_parallel,
            "total_agents": len(self.agents),
            "total_capacity": TOTAL_STATES,
            "pending_tasks": len(self._pending_futures),
            "total_completed": total_completed,
            "total_failed": total_failed,
            "silicon_groups": silicon_groups,
        }

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the coordinator."""
        self._executor.shutdown(wait=wait)


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Agent Coordinator Test (12 Parallel Agents)")
    print("=" * 60)

    coordinator = AgentCoordinator()

    # Display configuration
    print(f"\nPHI = {PHI}")
    print(f"MAX_AGENTS = {MAX_AGENTS}")
    print(f"TOTAL_STATES = {TOTAL_STATES}")

    print("\n--- Agent Configuration ---")
    print("Silicon | Dimensions | Capacity")
    print("-" * 35)
    print(f"NPU     | D1-D4      | {sum(LUCAS[0:4]):3d} (1+3+4+7)")
    print(f"CPU     | D5-D8      | {sum(LUCAS[4:8]):3d} (11+18+29+47)")
    print(f"GPU     | D9-D12     | {sum(LUCAS[8:12]):3d} (76+123+199+322)")
    print(f"Total   | D1-D12     | {sum(LUCAS):3d}")

    # Test individual task submission
    print("\n--- Individual Task Test ---")
    task_id = coordinator.submit_task(
        dimension=7,
        payload={"query": "reasoning test"}
    )
    print(f"Submitted task: {task_id}")

    result = coordinator.wait_for(task_id)
    if result:
        print(f"Result: {result.success}, duration={result.duration_ms:.2f}ms")
        print(f"  Dimension: D{result.dimension}")

    # Test parallel broadcast
    print("\n--- Broadcast Test (All 12 Agents) ---")
    task_ids = coordinator.broadcast({"operation": "sync_check"})
    print(f"Submitted {len(task_ids)} tasks")

    results = coordinator.wait_all(task_ids)
    print(f"Completed: {len([r for r in results if r.success])}/12")

    successful = [r for r in results if r.success]
    if successful:
        avg_duration = sum(r.duration_ms for r in successful) / len(successful)
        print(f"Average duration: {avg_duration:.2f}ms")

    # Test silicon-grouped execution
    print("\n--- Silicon-Grouped Test ---")

    # Submit to NPU dimensions (1-4)
    npu_tasks = coordinator.submit_parallel([
        (1, {"type": "perception"}),
        (2, {"type": "attention"}),
        (3, {"type": "security"}),
        (4, {"type": "stability"}),
    ])
    print(f"NPU tasks submitted: {len(npu_tasks)}")

    npu_results = coordinator.wait_all(npu_tasks)
    npu_success = sum(1 for r in npu_results if r.success)
    print(f"NPU completed: {npu_success}/4")

    # Get final status
    print("\n--- Coordinator Status ---")
    status = coordinator.get_status()
    print(f"Total agents: {status['total_agents']}")
    print(f"Total capacity: {status['total_capacity']}")
    print(f"Tasks completed: {status['total_completed']}")
    print(f"Tasks failed: {status['total_failed']}")

    print("\n--- Silicon Group Summary ---")
    for silicon, group in status['silicon_groups'].items():
        completed = sum(a['tasks_completed'] for a in group['agents'])
        print(f"{silicon}: capacity={group['capacity']}, completed={completed}")

    # Show per-agent stats
    print("\n--- Per-Agent Statistics ---")
    for dim in range(1, 13):
        agent_status = coordinator.get_agent_status(dim)
        print(f"D{dim:2d} ({agent_status['name']:12s}): "
              f"{agent_status['tasks_completed']} tasks, "
              f"avg={agent_status['avg_processing_ms']:.1f}ms")

    # Cleanup
    coordinator.shutdown()

    print("\n" + "=" * 60)
    print("Agent Coordinator Test Complete")
    print("=" * 60)
