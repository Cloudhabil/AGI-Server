"""
Metric Collector - 840-point telemetry collection.

Collects up to 840 metric points for comprehensive system telemetry.
The 840 limit derives from the TOTAL_STATES constant in the IIAS architecture.
"""

import time
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from collections import deque
import threading

# Constants
TOTAL_STATES = 840


class MetricType(Enum):
    """Types of metrics that can be collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class MetricPoint:
    """A single metric data point."""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "value": self.value,
            "labels": self.labels
        }


@dataclass
class MetricDefinition:
    """Definition of a metric."""
    name: str
    metric_type: MetricType
    description: str = ""
    unit: str = ""
    labels: List[str] = field(default_factory=list)


@dataclass
class MetricSummary:
    """Statistical summary of collected metrics."""
    name: str
    count: int
    min_value: float
    max_value: float
    mean_value: float
    std_dev: float
    percentiles: Dict[int, float]
    first_timestamp: float
    last_timestamp: float


class MetricCollector:
    """
    840-point telemetry collector.

    Collects up to TOTAL_STATES (840) metric points for each defined metric.
    When the limit is reached, oldest points are discarded (ring buffer behavior).

    The 840-point limit provides:
    - Sufficient granularity for trend analysis
    - Memory-bounded collection
    - Alignment with IIAS state space
    """

    def __init__(self, max_points: int = TOTAL_STATES):
        """
        Initialize the metric collector.

        Args:
            max_points: Maximum points per metric (default: 840).
        """
        self.max_points = min(max_points, TOTAL_STATES)  # Cap at 840
        self.metrics: Dict[str, MetricDefinition] = {}
        self.data: Dict[str, deque] = {}
        self._lock = threading.Lock()
        self._collectors: Dict[str, Callable] = {}

    def define_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
        unit: str = "",
        labels: Optional[List[str]] = None
    ) -> MetricDefinition:
        """
        Define a new metric for collection.

        Args:
            name: Unique metric name.
            metric_type: Type of metric.
            description: Human-readable description.
            unit: Unit of measurement.
            labels: Optional label keys.

        Returns:
            Created MetricDefinition.
        """
        definition = MetricDefinition(
            name=name,
            metric_type=metric_type,
            description=description,
            unit=unit,
            labels=labels or []
        )

        with self._lock:
            self.metrics[name] = definition
            self.data[name] = deque(maxlen=self.max_points)

        return definition

    def record(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        timestamp: Optional[float] = None
    ) -> None:
        """
        Record a metric data point.

        Args:
            name: Metric name.
            value: Metric value.
            labels: Optional labels.
            timestamp: Optional timestamp (defaults to now).
        """
        if name not in self.metrics:
            raise KeyError(f"Metric '{name}' not defined")

        point = MetricPoint(
            timestamp=timestamp or time.time(),
            value=value,
            labels=labels or {}
        )

        with self._lock:
            self.data[name].append(point)

    def increment(self, name: str, amount: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        if name not in self.metrics:
            raise KeyError(f"Metric '{name}' not defined")

        if self.metrics[name].metric_type != MetricType.COUNTER:
            raise ValueError(f"Metric '{name}' is not a counter")

        with self._lock:
            current = self.data[name][-1].value if self.data[name] else 0.0
            self.record(name, current + amount, labels)

    def get_points(self, name: str, limit: Optional[int] = None) -> List[MetricPoint]:
        """
        Get collected data points for a metric.

        Args:
            name: Metric name.
            limit: Optional limit on returned points.

        Returns:
            List of MetricPoints.
        """
        if name not in self.data:
            return []

        with self._lock:
            points = list(self.data[name])

        if limit:
            return points[-limit:]
        return points

    def get_point_count(self, name: str) -> int:
        """Get the number of points collected for a metric."""
        if name not in self.data:
            return 0
        return len(self.data[name])

    def get_summary(self, name: str) -> Optional[MetricSummary]:
        """
        Get statistical summary for a metric.

        Args:
            name: Metric name.

        Returns:
            MetricSummary or None if no data.
        """
        points = self.get_points(name)

        if not points:
            return None

        values = [p.value for p in points]
        timestamps = [p.timestamp for p in points]

        # Calculate percentiles
        sorted_values = sorted(values)
        n = len(sorted_values)
        percentiles = {}
        for p in [50, 90, 95, 99]:
            idx = int(n * p / 100)
            percentiles[p] = sorted_values[min(idx, n - 1)]

        return MetricSummary(
            name=name,
            count=len(values),
            min_value=min(values),
            max_value=max(values),
            mean_value=statistics.mean(values),
            std_dev=statistics.stdev(values) if len(values) > 1 else 0.0,
            percentiles=percentiles,
            first_timestamp=min(timestamps),
            last_timestamp=max(timestamps)
        )

    def register_collector(self, name: str, collector_fn: Callable[[], float]) -> None:
        """
        Register an automatic collector function.

        Args:
            name: Metric name to collect for.
            collector_fn: Function that returns the metric value.
        """
        if name not in self.metrics:
            raise KeyError(f"Metric '{name}' not defined")

        self._collectors[name] = collector_fn

    def collect_all(self) -> Dict[str, float]:
        """
        Run all registered collectors and record values.

        Returns:
            Dict of metric names to collected values.
        """
        results = {}

        for name, collector_fn in self._collectors.items():
            try:
                value = collector_fn()
                self.record(name, value)
                results[name] = value
            except Exception as e:
                results[name] = float('nan')

        return results

    def clear(self, name: Optional[str] = None) -> None:
        """
        Clear collected data.

        Args:
            name: Specific metric to clear, or None for all.
        """
        with self._lock:
            if name:
                if name in self.data:
                    self.data[name].clear()
            else:
                for metric_data in self.data.values():
                    metric_data.clear()

    def get_telemetry_report(self) -> str:
        """Generate a telemetry report."""
        lines = [
            "=" * 50,
            "840-POINT TELEMETRY REPORT",
            "=" * 50,
            f"Max Points per Metric: {self.max_points}",
            f"Total Metrics Defined: {len(self.metrics)}",
            "",
            "METRICS:",
        ]

        total_points = 0

        for name, definition in self.metrics.items():
            count = self.get_point_count(name)
            total_points += count
            summary = self.get_summary(name)

            lines.append(f"\n  {name} ({definition.metric_type.value})")
            lines.append(f"    Description: {definition.description or 'N/A'}")
            lines.append(f"    Unit: {definition.unit or 'N/A'}")
            lines.append(f"    Points: {count}/{self.max_points}")

            if summary:
                lines.append(f"    Min: {summary.min_value:.4f}")
                lines.append(f"    Max: {summary.max_value:.4f}")
                lines.append(f"    Mean: {summary.mean_value:.4f}")
                lines.append(f"    StdDev: {summary.std_dev:.4f}")
                lines.append(f"    P50: {summary.percentiles[50]:.4f}")
                lines.append(f"    P99: {summary.percentiles[99]:.4f}")

        lines.extend([
            "",
            f"Total Data Points: {total_points}",
            f"Maximum Capacity: {self.max_points * len(self.metrics)}",
            "=" * 50
        ])

        return "\n".join(lines)


if __name__ == "__main__":
    print("Testing MetricCollector - 840-point telemetry")
    print()

    print(f"TOTAL_STATES constant: {TOTAL_STATES}")
    print()

    # Create collector
    collector = MetricCollector()

    # Define metrics
    collector.define_metric(
        "cpu_usage",
        MetricType.GAUGE,
        description="CPU utilization percentage",
        unit="percent"
    )

    collector.define_metric(
        "request_count",
        MetricType.COUNTER,
        description="Total HTTP requests",
        unit="requests"
    )

    collector.define_metric(
        "response_time",
        MetricType.HISTOGRAM,
        description="API response latency",
        unit="ms"
    )

    # Record some data points
    print("Recording metric points...")
    import random

    for i in range(100):
        # CPU gauge - varies randomly
        collector.record("cpu_usage", random.uniform(20, 80))

        # Response time histogram - normal distribution
        collector.record("response_time", random.gauss(50, 15))

    # Increment counter
    for i in range(50):
        collector.increment("request_count")

    print(f"  cpu_usage: {collector.get_point_count('cpu_usage')} points")
    print(f"  request_count: {collector.get_point_count('request_count')} points")
    print(f"  response_time: {collector.get_point_count('response_time')} points")
    print()

    # Test 840-point limit
    print("Testing 840-point limit...")
    collector.define_metric("test_limit", MetricType.GAUGE, description="Limit test")

    for i in range(1000):  # Record more than 840
        collector.record("test_limit", i)

    count = collector.get_point_count("test_limit")
    print(f"  Recorded 1000 points, kept: {count}")
    assert count == TOTAL_STATES, f"Expected {TOTAL_STATES}, got {count}"
    print(f"  Correctly limited to {TOTAL_STATES} points!")
    print()

    # Get summary statistics
    print("Response Time Summary:")
    summary = collector.get_summary("response_time")
    if summary:
        print(f"  Count: {summary.count}")
        print(f"  Min: {summary.min_value:.2f}ms")
        print(f"  Max: {summary.max_value:.2f}ms")
        print(f"  Mean: {summary.mean_value:.2f}ms")
        print(f"  P50: {summary.percentiles[50]:.2f}ms")
        print(f"  P99: {summary.percentiles[99]:.2f}ms")
    print()

    # Test automatic collector
    print("Testing automatic collectors...")
    collector.define_metric("memory_usage", MetricType.GAUGE, description="Memory usage", unit="MB")

    def get_memory():
        return random.uniform(500, 800)

    collector.register_collector("memory_usage", get_memory)

    for _ in range(10):
        results = collector.collect_all()
        print(f"  Collected memory_usage: {results.get('memory_usage', 'N/A'):.2f} MB")
    print()

    # Print full report
    print(collector.get_telemetry_report())

    print("\nTest PASSED: MetricCollector working correctly!")
