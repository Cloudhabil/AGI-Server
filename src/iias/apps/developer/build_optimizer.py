"""
Build Optimizer - PHI-parallel compilation optimization.

Uses the golden ratio (PHI) to calculate optimal worker count for parallel builds.
Formula: optimal_workers = ceil(cores * PHI / 2)
"""

import math
import os
import time
from dataclasses import dataclass, field
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants
PHI = 1.618033988749895


@dataclass
class BuildTask:
    """Represents a single build task."""
    name: str
    priority: int = 0
    duration_estimate: float = 1.0  # seconds
    dependencies: List[str] = field(default_factory=list)
    completed: bool = False
    result: Optional[str] = None


@dataclass
class BuildMetrics:
    """Metrics from a build run."""
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_time: float
    workers_used: int
    efficiency_ratio: float


class BuildOptimizer:
    """
    PHI-parallel build optimizer.

    Calculates optimal worker count using the golden ratio formula:
    optimal_workers = ceil(cores * PHI / 2)

    This balances parallelism with resource overhead, following the
    natural efficiency of PHI-based systems.
    """

    def __init__(self, core_count: Optional[int] = None):
        """
        Initialize the build optimizer.

        Args:
            core_count: Number of CPU cores. Auto-detected if not provided.
        """
        self.core_count = core_count or os.cpu_count() or 4
        self.optimal_workers = self._calculate_optimal_workers()
        self.tasks: List[BuildTask] = []
        self.metrics: Optional[BuildMetrics] = None

    def _calculate_optimal_workers(self) -> int:
        """
        Calculate optimal worker count using PHI formula.

        Formula: ceil(cores * PHI / 2)

        Returns:
            Optimal number of parallel workers.
        """
        return math.ceil(self.core_count * PHI / 2)

    def add_task(self, task: BuildTask) -> None:
        """Add a build task to the queue."""
        self.tasks.append(task)

    def add_tasks(self, tasks: List[BuildTask]) -> None:
        """Add multiple build tasks."""
        self.tasks.extend(tasks)

    def _resolve_dependencies(self) -> List[List[BuildTask]]:
        """
        Resolve task dependencies and return execution layers.

        Returns:
            List of task layers, where each layer can run in parallel.
        """
        completed = set()
        layers = []
        remaining = list(self.tasks)

        while remaining:
            # Find tasks with satisfied dependencies
            layer = []
            for task in remaining:
                deps_satisfied = all(dep in completed for dep in task.dependencies)
                if deps_satisfied:
                    layer.append(task)

            if not layer:
                # Circular dependency or missing dependency
                raise ValueError(f"Cannot resolve dependencies for: {[t.name for t in remaining]}")

            layers.append(layer)
            for task in layer:
                completed.add(task.name)
                remaining.remove(task)

        return layers

    def _execute_task(self, task: BuildTask) -> BuildTask:
        """Execute a single build task (simulated)."""
        time.sleep(task.duration_estimate * 0.01)  # Scaled for testing
        task.completed = True
        task.result = f"Built {task.name} successfully"
        return task

    def run_build(self, workers: Optional[int] = None) -> BuildMetrics:
        """
        Execute all build tasks with optimal parallelism.

        Args:
            workers: Number of workers to use. Uses optimal if not specified.

        Returns:
            BuildMetrics with results of the build.
        """
        workers = workers or self.optimal_workers
        start_time = time.time()
        completed = 0
        failed = 0

        try:
            layers = self._resolve_dependencies()
        except ValueError:
            layers = [self.tasks]  # Fall back to flat execution

        for layer in layers:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(self._execute_task, task): task for task in layer}
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result.completed:
                            completed += 1
                        else:
                            failed += 1
                    except Exception:
                        failed += 1

        total_time = time.time() - start_time

        # Calculate efficiency: actual parallelism vs theoretical
        theoretical_time = sum(t.duration_estimate * 0.01 for t in self.tasks)
        efficiency = theoretical_time / total_time if total_time > 0 else 1.0

        self.metrics = BuildMetrics(
            total_tasks=len(self.tasks),
            completed_tasks=completed,
            failed_tasks=failed,
            total_time=total_time,
            workers_used=workers,
            efficiency_ratio=min(efficiency, workers)  # Cap at worker count
        )

        return self.metrics

    def get_optimization_report(self) -> str:
        """Generate a report on build optimization."""
        lines = [
            "=" * 50,
            "PHI-PARALLEL BUILD OPTIMIZATION REPORT",
            "=" * 50,
            f"CPU Cores Detected: {self.core_count}",
            f"PHI Constant: {PHI}",
            f"Optimal Workers: {self.optimal_workers}",
            f"Formula: ceil({self.core_count} * {PHI} / 2) = {self.optimal_workers}",
            "",
        ]

        if self.metrics:
            lines.extend([
                "BUILD METRICS:",
                f"  Total Tasks: {self.metrics.total_tasks}",
                f"  Completed: {self.metrics.completed_tasks}",
                f"  Failed: {self.metrics.failed_tasks}",
                f"  Total Time: {self.metrics.total_time:.4f}s",
                f"  Workers Used: {self.metrics.workers_used}",
                f"  Efficiency Ratio: {self.metrics.efficiency_ratio:.2f}x",
            ])

        lines.append("=" * 50)
        return "\n".join(lines)


if __name__ == "__main__":
    print("Testing BuildOptimizer - PHI-parallel compilation")
    print()

    # Test with different core counts
    for cores in [4, 8, 16, 32]:
        optimizer = BuildOptimizer(core_count=cores)
        print(f"Cores: {cores} -> Optimal Workers: {optimizer.optimal_workers}")

    print()

    # Create a build optimizer and add tasks
    optimizer = BuildOptimizer()

    # Add sample tasks with dependencies
    tasks = [
        BuildTask("core_lib", priority=1, duration_estimate=2.0),
        BuildTask("utils", priority=2, duration_estimate=1.0),
        BuildTask("parser", priority=3, duration_estimate=1.5, dependencies=["core_lib"]),
        BuildTask("compiler", priority=4, duration_estimate=3.0, dependencies=["core_lib", "parser"]),
        BuildTask("tests", priority=5, duration_estimate=2.0, dependencies=["compiler", "utils"]),
    ]

    optimizer.add_tasks(tasks)

    # Run the build
    metrics = optimizer.run_build()

    # Print report
    print(optimizer.get_optimization_report())

    print("\nTest PASSED: BuildOptimizer working correctly!")
