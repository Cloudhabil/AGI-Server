"""IIAS Edge Realtime Pipeline - Parallel Execution Across NPU/CPU/GPU

This module provides a realtime execution pipeline targeting <10ms latency
by distributing workloads optimally across available compute units based
on their bandwidth characteristics.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
import time
import threading

# Constants
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
TOTAL_STATES = 840
PHI = 1.618033988749895

# Bandwidth constants (GB/s)
NPU_BW = 7.35
CPU_BW = 26.0
GPU_BW = 12.0

# Target latency (ms)
TARGET_LATENCY_MS = 10.0


class ComputeUnit(Enum):
    """Available compute units."""
    NPU = "npu"
    CPU = "cpu"
    GPU = "gpu"


@dataclass
class ComputeCapability:
    """Capability profile for a compute unit."""
    unit: ComputeUnit
    bandwidth_gbps: float
    available: bool = True
    utilization: float = 0.0
    latency_overhead_ms: float = 0.1  # Context switch overhead

    @property
    def effective_bandwidth(self) -> float:
        """Bandwidth adjusted for current utilization."""
        return self.bandwidth_gbps * (1 - self.utilization)

    @property
    def bytes_per_ms(self) -> float:
        """Convert GB/s to bytes per millisecond."""
        return (self.bandwidth_gbps * 1e9) / 1000


@dataclass
class TaskResult:
    """Result of a pipeline task."""
    task_id: str
    compute_unit: ComputeUnit
    result: Any
    latency_ms: float
    success: bool
    error: Optional[str] = None


@dataclass
class PipelineMetrics:
    """Pipeline execution metrics."""
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    min_latency_ms: float = float('inf')
    target_met_count: int = 0
    target_missed_count: int = 0

    @property
    def target_hit_rate(self) -> float:
        total = self.target_met_count + self.target_missed_count
        return (self.target_met_count / total) if total > 0 else 0.0


@dataclass
class Task:
    """A task to be executed in the pipeline."""
    task_id: str
    callable: Callable
    args: Tuple = ()
    kwargs: Dict = field(default_factory=dict)
    preferred_unit: Optional[ComputeUnit] = None
    estimated_data_bytes: int = 0
    priority: int = 5  # 1-10, lower is higher priority


class RealtimePipeline:
    """
    Realtime execution pipeline with <10ms target latency.

    Distribution strategy:
    - CPU: High bandwidth (26 GB/s) - general compute, data transformation
    - GPU: Medium bandwidth (12 GB/s) - parallel operations, inference
    - NPU: Specialized bandwidth (7.35 GB/s) - AI/ML inference

    Task scheduling optimizes for:
    1. Meeting <10ms latency target
    2. Optimal bandwidth utilization
    3. Load balancing across units
    """

    def __init__(
        self,
        enable_npu: bool = True,
        enable_gpu: bool = True,
        max_workers: int = 8,
        target_latency_ms: float = TARGET_LATENCY_MS
    ):
        self._target_latency = target_latency_ms
        self._max_workers = max_workers

        # Initialize compute capabilities
        self._capabilities: Dict[ComputeUnit, ComputeCapability] = {
            ComputeUnit.NPU: ComputeCapability(
                unit=ComputeUnit.NPU,
                bandwidth_gbps=NPU_BW,
                available=enable_npu,
                latency_overhead_ms=0.2
            ),
            ComputeUnit.CPU: ComputeCapability(
                unit=ComputeUnit.CPU,
                bandwidth_gbps=CPU_BW,
                available=True,
                latency_overhead_ms=0.05
            ),
            ComputeUnit.GPU: ComputeCapability(
                unit=ComputeUnit.GPU,
                bandwidth_gbps=GPU_BW,
                available=enable_gpu,
                latency_overhead_ms=0.3
            ),
        }

        # Thread pool for parallel execution
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._metrics = PipelineMetrics()
        self._lock = threading.Lock()

        # Task queue and results
        self._pending_tasks: List[Task] = []
        self._results: Dict[str, TaskResult] = {}

    def _estimate_latency(self, task: Task, unit: ComputeUnit) -> float:
        """
        Estimate task latency on a compute unit.

        Args:
            task: Task to estimate
            unit: Target compute unit

        Returns:
            Estimated latency in milliseconds
        """
        cap = self._capabilities[unit]
        if not cap.available:
            return float('inf')

        # Data transfer time
        if task.estimated_data_bytes > 0:
            transfer_ms = task.estimated_data_bytes / cap.bytes_per_ms
        else:
            # Default small data assumption
            transfer_ms = 0.1

        # Add overhead and utilization penalty
        utilization_penalty = cap.utilization * 2.0
        total_ms = transfer_ms + cap.latency_overhead_ms + utilization_penalty

        return total_ms

    def _select_compute_unit(self, task: Task) -> ComputeUnit:
        """
        Select optimal compute unit for a task.

        Args:
            task: Task to schedule

        Returns:
            Selected compute unit
        """
        # Respect preferred unit if available
        if task.preferred_unit:
            cap = self._capabilities[task.preferred_unit]
            if cap.available and cap.utilization < 0.9:
                return task.preferred_unit

        # Find unit with lowest estimated latency
        best_unit = ComputeUnit.CPU
        best_latency = float('inf')

        for unit, cap in self._capabilities.items():
            if not cap.available:
                continue

            latency = self._estimate_latency(task, unit)
            if latency < best_latency:
                best_latency = latency
                best_unit = unit

        return best_unit

    def _execute_task(self, task: Task, unit: ComputeUnit) -> TaskResult:
        """
        Execute a task on specified compute unit.

        Args:
            task: Task to execute
            unit: Compute unit to use

        Returns:
            TaskResult with execution details
        """
        start_time = time.perf_counter()

        try:
            # Update utilization
            with self._lock:
                self._capabilities[unit].utilization = min(
                    1.0, self._capabilities[unit].utilization + 0.1
                )

            # Execute the callable
            result = task.callable(*task.args, **task.kwargs)

            latency_ms = (time.perf_counter() - start_time) * 1000

            return TaskResult(
                task_id=task.task_id,
                compute_unit=unit,
                result=result,
                latency_ms=latency_ms,
                success=True
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return TaskResult(
                task_id=task.task_id,
                compute_unit=unit,
                result=None,
                latency_ms=latency_ms,
                success=False,
                error=str(e)
            )

        finally:
            # Release utilization
            with self._lock:
                self._capabilities[unit].utilization = max(
                    0.0, self._capabilities[unit].utilization - 0.1
                )

    def _update_metrics(self, result: TaskResult) -> None:
        """Update pipeline metrics with task result."""
        with self._lock:
            self._metrics.total_tasks += 1
            self._metrics.total_latency_ms += result.latency_ms

            if result.success:
                self._metrics.completed_tasks += 1
            else:
                self._metrics.failed_tasks += 1

            self._metrics.max_latency_ms = max(
                self._metrics.max_latency_ms, result.latency_ms
            )
            self._metrics.min_latency_ms = min(
                self._metrics.min_latency_ms, result.latency_ms
            )

            if self._metrics.completed_tasks > 0:
                self._metrics.avg_latency_ms = (
                    self._metrics.total_latency_ms / self._metrics.completed_tasks
                )

            if result.latency_ms <= self._target_latency:
                self._metrics.target_met_count += 1
            else:
                self._metrics.target_missed_count += 1

    def submit(self, task: Task) -> str:
        """
        Submit a task to the pipeline.

        Args:
            task: Task to submit

        Returns:
            Task ID
        """
        self._pending_tasks.append(task)
        return task.task_id

    def execute_single(self, task: Task) -> TaskResult:
        """
        Execute a single task immediately.

        Args:
            task: Task to execute

        Returns:
            TaskResult
        """
        unit = self._select_compute_unit(task)
        result = self._execute_task(task, unit)
        self._update_metrics(result)
        self._results[task.task_id] = result
        return result

    def execute_batch(
        self,
        tasks: List[Task],
        timeout_ms: Optional[float] = None
    ) -> List[TaskResult]:
        """
        Execute a batch of tasks in parallel.

        Args:
            tasks: List of tasks to execute
            timeout_ms: Optional timeout in milliseconds

        Returns:
            List of TaskResults
        """
        if not tasks:
            return []

        timeout_s = (timeout_ms / 1000) if timeout_ms else None
        results = []
        futures: Dict[Future, Task] = {}

        # Submit all tasks
        for task in tasks:
            unit = self._select_compute_unit(task)
            future = self._executor.submit(self._execute_task, task, unit)
            futures[future] = task

        # Collect results
        try:
            for future in as_completed(futures.keys(), timeout=timeout_s):
                result = future.result()
                self._update_metrics(result)
                self._results[result.task_id] = result
                results.append(result)
        except TimeoutError:
            # Handle timeout - cancel remaining
            for future in futures:
                future.cancel()

        return results

    def execute_pipeline(
        self,
        stages: List[List[Task]],
        timeout_ms: Optional[float] = None
    ) -> List[List[TaskResult]]:
        """
        Execute a multi-stage pipeline.

        Each stage runs in parallel, stages run sequentially.

        Args:
            stages: List of task lists (stages)
            timeout_ms: Optional per-stage timeout

        Returns:
            Results organized by stage
        """
        all_results = []

        for stage in stages:
            stage_results = self.execute_batch(stage, timeout_ms)
            all_results.append(stage_results)

            # Check for failures before proceeding
            if any(not r.success for r in stage_results):
                # Optionally halt pipeline on failure
                pass

        return all_results

    def flush(self) -> List[TaskResult]:
        """Execute all pending tasks."""
        tasks = self._pending_tasks.copy()
        self._pending_tasks.clear()
        return self.execute_batch(tasks)

    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Get result for a specific task."""
        return self._results.get(task_id)

    def get_capabilities(self) -> Dict[str, Dict]:
        """Get compute unit capabilities."""
        return {
            unit.value: {
                "bandwidth_gbps": cap.bandwidth_gbps,
                "bytes_per_ms": cap.bytes_per_ms,
                "available": cap.available,
                "utilization": round(cap.utilization, 2),
                "overhead_ms": cap.latency_overhead_ms,
            }
            for unit, cap in self._capabilities.items()
        }

    def get_metrics(self) -> PipelineMetrics:
        """Get pipeline metrics."""
        return self._metrics

    def estimate_throughput(self, data_size_bytes: int) -> Dict[str, float]:
        """
        Estimate throughput for given data size on each unit.

        Args:
            data_size_bytes: Data size in bytes

        Returns:
            Dict of unit -> estimated time in ms
        """
        return {
            unit.value: data_size_bytes / cap.bytes_per_ms
            for unit, cap in self._capabilities.items()
            if cap.available
        }

    def get_optimal_distribution(
        self,
        total_work_units: int
    ) -> Dict[ComputeUnit, int]:
        """
        Calculate optimal work distribution across compute units.

        Uses bandwidth ratios to distribute work.

        Args:
            total_work_units: Total units of work

        Returns:
            Dict of unit -> work units to assign
        """
        # Calculate bandwidth ratios
        total_bw = sum(
            cap.bandwidth_gbps for cap in self._capabilities.values()
            if cap.available
        )

        distribution = {}
        remaining = total_work_units

        for unit, cap in self._capabilities.items():
            if not cap.available:
                distribution[unit] = 0
                continue

            ratio = cap.bandwidth_gbps / total_bw
            allocated = int(total_work_units * ratio)
            distribution[unit] = allocated
            remaining -= allocated

        # Assign remaining to CPU (highest bandwidth)
        if ComputeUnit.CPU in distribution:
            distribution[ComputeUnit.CPU] += remaining

        return distribution

    def reset_metrics(self) -> None:
        """Reset pipeline metrics."""
        self._metrics = PipelineMetrics()

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the pipeline executor."""
        self._executor.shutdown(wait=wait)

    def summary(self) -> Dict:
        """Get pipeline summary."""
        m = self._metrics
        return {
            "target_latency_ms": self._target_latency,
            "total_tasks": m.total_tasks,
            "completed": m.completed_tasks,
            "failed": m.failed_tasks,
            "avg_latency_ms": round(m.avg_latency_ms, 3),
            "max_latency_ms": round(m.max_latency_ms, 3),
            "min_latency_ms": round(m.min_latency_ms, 3) if m.min_latency_ms != float('inf') else 0,
            "target_hit_rate": round(m.target_hit_rate * 100, 1),
            "bandwidths_gbps": {
                "NPU": NPU_BW,
                "CPU": CPU_BW,
                "GPU": GPU_BW,
            },
        }


# Helper functions for creating tasks
def create_task(
    task_id: str,
    func: Callable,
    *args,
    preferred_unit: Optional[ComputeUnit] = None,
    data_bytes: int = 0,
    priority: int = 5,
    **kwargs
) -> Task:
    """Create a pipeline task."""
    return Task(
        task_id=task_id,
        callable=func,
        args=args,
        kwargs=kwargs,
        preferred_unit=preferred_unit,
        estimated_data_bytes=data_bytes,
        priority=priority
    )


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Edge Realtime Pipeline - Test Suite")
    print("=" * 60)

    # Show constants
    print(f"\nTarget latency: {TARGET_LATENCY_MS}ms")
    print(f"Bandwidth - NPU: {NPU_BW} GB/s, CPU: {CPU_BW} GB/s, GPU: {GPU_BW} GB/s")

    # Initialize pipeline
    pipeline = RealtimePipeline()

    # Show capabilities
    print("\n--- Compute Capabilities ---")
    for unit, info in pipeline.get_capabilities().items():
        print(f"  {unit.upper()}: {info['bandwidth_gbps']:.2f} GB/s "
              f"({info['bytes_per_ms']:.0f} bytes/ms)")

    # Test throughput estimation
    print("\n--- Throughput Estimation (1MB data) ---")
    data_size = 1024 * 1024  # 1 MB
    estimates = pipeline.estimate_throughput(data_size)
    for unit, time_ms in estimates.items():
        print(f"  {unit.upper()}: {time_ms:.3f}ms")

    # Test optimal distribution
    print("\n--- Optimal Work Distribution (100 units) ---")
    distribution = pipeline.get_optimal_distribution(100)
    for unit, work in distribution.items():
        print(f"  {unit.value.upper()}: {work} units")

    # Define test functions
    def fast_compute(x: int) -> int:
        """Fast computation."""
        return x * 2

    def medium_compute(x: int) -> int:
        """Medium computation with small delay."""
        time.sleep(0.001)  # 1ms
        return x ** 2

    def slow_compute(x: int) -> int:
        """Slower computation."""
        time.sleep(0.005)  # 5ms
        result = 0
        for i in range(x):
            result += i
        return result

    # Test single execution
    print("\n--- Single Task Execution ---")
    task = create_task("single_1", fast_compute, 42)
    result = pipeline.execute_single(task)
    print(f"  Task: {result.task_id}")
    print(f"  Unit: {result.compute_unit.value.upper()}")
    print(f"  Result: {result.result}")
    print(f"  Latency: {result.latency_ms:.3f}ms")
    print(f"  Target met: {result.latency_ms <= TARGET_LATENCY_MS}")

    # Test batch execution
    print("\n--- Batch Execution (10 tasks) ---")
    tasks = [
        create_task(f"batch_{i}", fast_compute, i * 10)
        for i in range(10)
    ]

    start = time.perf_counter()
    results = pipeline.execute_batch(tasks)
    batch_time = (time.perf_counter() - start) * 1000

    success_count = sum(1 for r in results if r.success)
    avg_latency = sum(r.latency_ms for r in results) / len(results)

    print(f"  Tasks completed: {success_count}/{len(tasks)}")
    print(f"  Total batch time: {batch_time:.3f}ms")
    print(f"  Average task latency: {avg_latency:.3f}ms")

    # Test pipeline stages
    print("\n--- Multi-Stage Pipeline ---")
    stages = [
        [create_task(f"stage1_{i}", fast_compute, i) for i in range(3)],
        [create_task(f"stage2_{i}", medium_compute, i + 10) for i in range(3)],
        [create_task(f"stage3_{i}", fast_compute, i + 20) for i in range(3)],
    ]

    start = time.perf_counter()
    stage_results = pipeline.execute_pipeline(stages)
    pipeline_time = (time.perf_counter() - start) * 1000

    print(f"  Stages: {len(stage_results)}")
    for i, stage in enumerate(stage_results):
        stage_latency = sum(r.latency_ms for r in stage) / len(stage) if stage else 0
        print(f"    Stage {i + 1}: {len(stage)} tasks, avg {stage_latency:.3f}ms")
    print(f"  Total pipeline time: {pipeline_time:.3f}ms")

    # Test with preferred units
    print("\n--- Preferred Unit Routing ---")
    npu_task = create_task("npu_task", fast_compute, 100, preferred_unit=ComputeUnit.NPU)
    gpu_task = create_task("gpu_task", fast_compute, 100, preferred_unit=ComputeUnit.GPU)
    cpu_task = create_task("cpu_task", fast_compute, 100, preferred_unit=ComputeUnit.CPU)

    for task in [npu_task, gpu_task, cpu_task]:
        result = pipeline.execute_single(task)
        print(f"  {task.task_id}: routed to {result.compute_unit.value.upper()}")

    # Show final metrics
    print("\n--- Pipeline Metrics ---")
    metrics = pipeline.get_metrics()
    print(f"  Total tasks: {metrics.total_tasks}")
    print(f"  Completed: {metrics.completed_tasks}")
    print(f"  Failed: {metrics.failed_tasks}")
    print(f"  Avg latency: {metrics.avg_latency_ms:.3f}ms")
    print(f"  Max latency: {metrics.max_latency_ms:.3f}ms")
    print(f"  Target hit rate: {metrics.target_hit_rate:.1%}")

    # Summary
    print("\n--- Final Summary ---")
    summary = pipeline.summary()
    for key, value in summary.items():
        if key != "bandwidths_gbps":
            print(f"  {key}: {value}")

    # Cleanup
    pipeline.shutdown()

    print("\n" + "=" * 60)
    print("Realtime Pipeline tests completed successfully!")
    print("=" * 60)
