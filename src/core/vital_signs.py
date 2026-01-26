"""
System Health Metrics Collection and Analysis Module
=====================================================

Implements real-time telemetry collection for autonomous system monitoring.
Provides baseline establishment, trend analysis, and anomaly detection support.

Metrics Categories:
1. Memory Subsystem: Fragmentation, density distribution, isolation ratios
2. Network Layer: Routing efficiency, latency, connection statistics
3. Security Layer: Violation rates, detection statistics
4. Performance: Resource utilization, operation latencies

This module follows:
- IEEE 1451 Smart Transducer Interface Standards
- NIST SP 800-137 Continuous Monitoring Guidelines

Author: Elias Oulad Brahim
Institution: ASIOS Research
Date: 2026-01-26
License: Proprietary
"""

import json
import logging
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import deque
from enum import Enum

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: TYPE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

class HealthStatus(Enum):
    """System health classification."""
    OPTIMAL = "optimal"         # All metrics within normal range
    NOMINAL = "nominal"         # Minor deviations, acceptable
    DEGRADED = "degraded"       # Significant deviations, monitoring required
    CRITICAL = "critical"       # System at risk, intervention needed


@dataclass
class MetricDefinition:
    """
    Specification for a monitored metric.

    Attributes:
        name: Unique metric identifier
        unit: Measurement unit (e.g., "ratio", "ms", "count")
        lower_bound: Minimum healthy value
        upper_bound: Maximum healthy value
        description: Human-readable description
    """
    name: str
    unit: str
    lower_bound: float
    upper_bound: float
    description: str


@dataclass
class MetricReading:
    """
    Single metric observation.

    Attributes:
        metric_name: Reference to MetricDefinition.name
        value: Observed value
        timestamp: ISO 8601 observation time
        within_bounds: Whether value is in healthy range
        deviation: Normalized distance from midpoint
    """
    metric_name: str
    value: float
    timestamp: str
    within_bounds: bool
    deviation: float


@dataclass
class SystemHealthSnapshot:
    """
    Complete system health observation at a point in time.

    Attributes:
        timestamp: ISO 8601 observation time
        health_score: Aggregate health (0.0 - 1.0)
        status: Classified health status
        readings: Individual metric observations
        alerts: List of threshold violations
    """
    timestamp: str
    health_score: float
    status: HealthStatus
    readings: Dict[str, MetricReading]
    alerts: List[str]


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: METRIC SPECIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

METRIC_SPECIFICATIONS: Dict[str, MetricDefinition] = {
    "memory_fragmentation": MetricDefinition(
        name="memory_fragmentation",
        unit="ratio",
        lower_bound=0.0,
        upper_bound=0.3,
        description="Ratio of underutilized memory segments to total segments"
    ),
    "segment_density_mean": MetricDefinition(
        name="segment_density_mean",
        unit="items",
        lower_bound=5.0,
        upper_bound=50.0,
        description="Mean item count per memory segment"
    ),
    "segment_density_variance": MetricDefinition(
        name="segment_density_variance",
        unit="variance",
        lower_bound=0.0,
        upper_bound=100.0,
        description="Variance in segment item counts"
    ),
    "routing_efficiency": MetricDefinition(
        name="routing_efficiency",
        unit="ratio",
        lower_bound=0.6,
        upper_bound=1.0,
        description="Successful routes / total route attempts"
    ),
    "quantization_error": MetricDefinition(
        name="quantization_error",
        unit="MSE",
        lower_bound=0.0,
        upper_bound=0.15,
        description="Mean squared reconstruction error"
    ),
    "isolation_ratio": MetricDefinition(
        name="isolation_ratio",
        unit="ratio",
        lower_bound=0.0,
        upper_bound=0.1,
        description="Ratio of isolated segments to total segments"
    ),
    "violation_rate": MetricDefinition(
        name="violation_rate",
        unit="events/min",
        lower_bound=0.0,
        upper_bound=0.5,
        description="Security violation attempts per minute"
    ),
    "response_latency": MetricDefinition(
        name="response_latency",
        unit="ms",
        lower_bound=0.0,
        upper_bound=2000.0,
        description="Average operation response time"
    ),
    "cpu_utilization": MetricDefinition(
        name="cpu_utilization",
        unit="ratio",
        lower_bound=0.0,
        upper_bound=0.8,
        description="CPU usage ratio (0.0 - 1.0)"
    ),
    "active_operations": MetricDefinition(
        name="active_operations",
        unit="count",
        lower_bound=0.0,
        upper_bound=100.0,
        description="Concurrent operation count"
    ),
}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: METRIC COLLECTORS
# ═══════════════════════════════════════════════════════════════════════════════

class MemoryMetricsCollector:
    """
    Collects memory subsystem metrics from substrate tree.

    Metrics:
    - memory_fragmentation: Small segment ratio
    - segment_density_mean: Average items per segment
    - segment_density_variance: Distribution spread
    - isolation_ratio: Isolated segment ratio
    """

    def __init__(self, data_path: Path):
        self._tree_path = data_path / "substrate_tree.json"

    def collect(self) -> Dict[str, float]:
        """
        Sample current memory metrics.

        Returns:
            Dictionary of metric_name -> value
        """
        metrics = {
            "memory_fragmentation": 0.0,
            "segment_density_mean": 0.0,
            "segment_density_variance": 0.0,
            "isolation_ratio": 0.0,
        }

        if not self._tree_path.exists():
            return metrics

        try:
            with open(self._tree_path, 'r', encoding='utf-8') as f:
                tree = json.load(f)

            if not tree:
                return metrics

            # Calculate density statistics
            densities = [segment.get("count", 0) for segment in tree]
            metrics["segment_density_mean"] = float(np.mean(densities))
            metrics["segment_density_variance"] = float(np.var(densities))

            # Fragmentation: ratio of sparse segments
            sparse_count = sum(1 for d in densities if d < 5)
            metrics["memory_fragmentation"] = sparse_count / len(tree)

            # Isolation ratio
            isolated_count = sum(
                1 for s in tree
                if s.get("status") in ("ISOLATED", "QUARANTINED")
            )
            metrics["isolation_ratio"] = isolated_count / len(tree)

        except Exception as e:
            logger.error(f"Memory metrics collection failed: {e}")

        return metrics


class NetworkMetricsCollector:
    """
    Collects network/routing layer metrics.

    Maintains rolling window of route events for statistical analysis.
    """

    def __init__(self, window_size: int = 100):
        self._route_log: deque = deque(maxlen=window_size)

    def record_route_event(
        self,
        hop_count: int,
        latency_ms: float,
        success: bool
    ):
        """
        Record a routing operation.

        Args:
            hop_count: Number of hops in route
            latency_ms: Total operation latency
            success: Whether route completed successfully
        """
        self._route_log.append({
            "hops": hop_count,
            "latency": latency_ms,
            "success": success,
            "timestamp": time.time()
        })

    def collect(self) -> Dict[str, float]:
        """
        Calculate current network metrics.

        Returns:
            Dictionary of metric_name -> value
        """
        metrics = {
            "routing_efficiency": 1.0,
            "response_latency": 0.0,
            "active_operations": 0.0,
        }

        if not self._route_log:
            return metrics

        # Filter to recent events (last 5 minutes)
        cutoff = time.time() - 300
        recent = [r for r in self._route_log if r["timestamp"] > cutoff]

        if not recent:
            return metrics

        # Routing efficiency
        success_count = sum(1 for r in recent if r["success"])
        metrics["routing_efficiency"] = success_count / len(recent)

        # Average latency
        latencies = [r["latency"] for r in recent]
        metrics["response_latency"] = float(np.mean(latencies))

        # Operations per minute estimate
        duration_minutes = (time.time() - recent[0]["timestamp"]) / 60
        if duration_minutes > 0:
            metrics["active_operations"] = len(recent) / duration_minutes

        return metrics


class SecurityMetricsCollector:
    """
    Collects security layer metrics.

    Tracks violation attempts for rate calculation.
    """

    def __init__(self, window_size: int = 1000):
        self._violation_timestamps: deque = deque(maxlen=window_size)

    def record_violation_attempt(self):
        """Record a security violation attempt."""
        self._violation_timestamps.append(time.time())

    def collect(self) -> Dict[str, float]:
        """
        Calculate security metrics.

        Returns:
            Dictionary of metric_name -> value
        """
        # Violations in last minute
        cutoff = time.time() - 60
        recent_count = sum(
            1 for t in self._violation_timestamps
            if t > cutoff
        )

        return {
            "violation_rate": recent_count,  # per minute
        }


class PerformanceMetricsCollector:
    """
    Collects system performance metrics.

    Optional dependency on psutil for CPU metrics.
    """

    def __init__(self):
        self._operation_log: deque = deque(maxlen=100)

    def record_operation(self, operation_type: str, duration_ms: float):
        """
        Record an operation timing.

        Args:
            operation_type: Category of operation
            duration_ms: Operation duration in milliseconds
        """
        self._operation_log.append({
            "type": operation_type,
            "duration": duration_ms,
            "timestamp": time.time()
        })

    def collect(self) -> Dict[str, float]:
        """
        Calculate performance metrics.

        Returns:
            Dictionary of metric_name -> value
        """
        metrics = {
            "quantization_error": 0.05,  # Default placeholder
            "cpu_utilization": 0.0,
        }

        # CPU utilization (optional dependency)
        try:
            import psutil
            metrics["cpu_utilization"] = psutil.cpu_percent() / 100.0
        except ImportError:
            pass

        return metrics


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: HEALTH MONITOR
# ═══════════════════════════════════════════════════════════════════════════════

class SystemHealthMonitor:
    """
    Central coordinator for health telemetry.

    Responsibilities:
    - Aggregate metrics from all collectors
    - Maintain baseline for comparison
    - Generate health snapshots
    - Provide trend analysis

    Usage:
        monitor = SystemHealthMonitor(repo_root)
        monitor.establish_baseline()
        snapshot = monitor.take_snapshot()
        print(f"Health: {snapshot.health_score:.2%}")
    """

    def __init__(self, repo_root: Path):
        self._root = repo_root
        self._baseline_path = repo_root / "data" / "metrics_baseline.json"
        self._history_path = repo_root / "data" / "metrics_history.json"

        # Initialize collectors
        self._memory_collector = MemoryMetricsCollector(repo_root / "data")
        self._network_collector = NetworkMetricsCollector()
        self._security_collector = SecurityMetricsCollector()
        self._performance_collector = PerformanceMetricsCollector()

        # State
        self._baseline: Dict[str, float] = {}
        self._history: deque = deque(maxlen=1000)

        # Load persisted baseline
        self._load_baseline()

        logger.info("System health monitor initialized.")

    def _load_baseline(self):
        """Load baseline from persistent storage."""
        if not self._baseline_path.exists():
            return

        try:
            with open(self._baseline_path, 'r', encoding='utf-8') as f:
                self._baseline = json.load(f)
            logger.info(f"Loaded baseline: {len(self._baseline)} metrics")
        except Exception as e:
            logger.warning(f"Baseline load failed: {e}")

    def _save_baseline(self):
        """Persist baseline to storage."""
        self._baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._baseline_path, 'w', encoding='utf-8') as f:
            json.dump(self._baseline, f, indent=2)

    def collect_all_metrics(self) -> Dict[str, float]:
        """
        Aggregate metrics from all collectors.

        Returns:
            Complete metrics dictionary
        """
        metrics = {}
        metrics.update(self._memory_collector.collect())
        metrics.update(self._network_collector.collect())
        metrics.update(self._security_collector.collect())
        metrics.update(self._performance_collector.collect())
        return metrics

    def take_snapshot(self) -> SystemHealthSnapshot:
        """
        Generate complete health snapshot.

        Returns:
            SystemHealthSnapshot with all current metrics
        """
        timestamp = datetime.utcnow().isoformat()
        metrics = self.collect_all_metrics()

        readings: Dict[str, MetricReading] = {}
        alerts: List[str] = []
        healthy_count = 0
        total_count = 0

        for metric_name, value in metrics.items():
            spec = METRIC_SPECIFICATIONS.get(metric_name)
            if spec is None:
                continue

            within_bounds = spec.lower_bound <= value <= spec.upper_bound

            # Calculate normalized deviation from midpoint
            midpoint = (spec.lower_bound + spec.upper_bound) / 2
            range_size = spec.upper_bound - spec.lower_bound
            deviation = abs(value - midpoint) / (range_size / 2) if range_size > 0 else 0

            reading = MetricReading(
                metric_name=metric_name,
                value=value,
                timestamp=timestamp,
                within_bounds=within_bounds,
                deviation=deviation
            )
            readings[metric_name] = reading

            if within_bounds:
                healthy_count += 1
            else:
                if value < spec.lower_bound:
                    alerts.append(
                        f"{metric_name}: {value:.3f} < {spec.lower_bound} ({spec.unit})"
                    )
                else:
                    alerts.append(
                        f"{metric_name}: {value:.3f} > {spec.upper_bound} ({spec.unit})"
                    )

            total_count += 1

        # Calculate aggregate health score
        health_score = healthy_count / total_count if total_count > 0 else 1.0

        # Classify status
        if health_score >= 0.9:
            status = HealthStatus.OPTIMAL
        elif health_score >= 0.7:
            status = HealthStatus.NOMINAL
        elif health_score >= 0.5:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.CRITICAL

        snapshot = SystemHealthSnapshot(
            timestamp=timestamp,
            health_score=health_score,
            status=status,
            readings=readings,
            alerts=alerts
        )

        # Archive to history
        self._history.append({
            "timestamp": timestamp,
            "health_score": health_score,
            "status": status.value,
            "metrics": metrics,
            "alerts": alerts
        })

        return snapshot

    def establish_baseline(self, sample_count: int = 10) -> Dict[str, float]:
        """
        Establish healthy baseline by averaging multiple samples.

        Should be called during known-healthy operation.

        Args:
            sample_count: Number of samples to average

        Returns:
            Established baseline metrics
        """
        accumulated: Dict[str, List[float]] = {}

        for _ in range(sample_count):
            metrics = self.collect_all_metrics()
            for key, value in metrics.items():
                if key not in accumulated:
                    accumulated[key] = []
                accumulated[key].append(value)
            time.sleep(0.1)

        self._baseline = {
            key: float(np.mean(values))
            for key, values in accumulated.items()
        }

        self._save_baseline()
        logger.info(f"Established baseline: {len(self._baseline)} metrics")
        return self._baseline

    def get_baseline(self) -> Dict[str, float]:
        """
        Get current baseline metrics.

        Returns:
            Baseline dictionary for anomaly detection
        """
        return self._baseline.copy()

    def get_current_metrics(self) -> Dict[str, float]:
        """
        Get latest metrics.

        Returns:
            Current metrics dictionary
        """
        return self.collect_all_metrics()

    def get_summary(self) -> Dict:
        """
        Generate health summary from recent history.

        Returns:
            Summary dictionary with statistics
        """
        if not self._history:
            return {
                "status": "NO_DATA",
                "message": "Insufficient data for summary"
            }

        recent = list(self._history)[-10:]
        avg_health = float(np.mean([r["health_score"] for r in recent]))

        # Aggregate alerts
        all_alerts = []
        for record in recent:
            all_alerts.extend(record["alerts"])

        # Status classification
        if avg_health >= 0.9:
            status = "OPTIMAL"
        elif avg_health >= 0.7:
            status = "NOMINAL"
        elif avg_health >= 0.5:
            status = "DEGRADED"
        else:
            status = "CRITICAL"

        return {
            "status": status,
            "average_health_score": avg_health,
            "sample_count": len(recent),
            "total_alerts": len(all_alerts),
            "unique_alerts": list(set(all_alerts)),
            "last_observation": recent[-1]["timestamp"]
        }

    def analyze_trend(self, metric_name: str, window: int = 10) -> Dict:
        """
        Analyze trend for specific metric.

        Args:
            metric_name: Metric to analyze
            window: Number of samples for trend calculation

        Returns:
            Trend analysis dictionary
        """
        if len(self._history) < 3:
            return {"trend": "INSUFFICIENT_DATA"}

        recent = list(self._history)[-window:]
        values = [r["metrics"].get(metric_name, 0) for r in recent]

        if len(values) < 3:
            return {"trend": "INSUFFICIENT_DATA"}

        # Simple linear trend analysis
        first_half_mean = float(np.mean(values[:len(values)//2]))
        second_half_mean = float(np.mean(values[len(values)//2:]))

        if first_half_mean == 0:
            change_ratio = 0.0
        else:
            change_ratio = (second_half_mean - first_half_mean) / first_half_mean

        if change_ratio > 0.1:
            trend = "INCREASING"
        elif change_ratio < -0.1:
            trend = "DECREASING"
        else:
            trend = "STABLE"

        return {
            "trend": trend,
            "change_percent": change_ratio * 100,
            "current_value": values[-1],
            "baseline_value": self._baseline.get(metric_name)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: MODULE INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

_monitor_instance: Optional[SystemHealthMonitor] = None


def get_health_monitor(repo_root: Optional[Path] = None) -> SystemHealthMonitor:
    """
    Singleton accessor for health monitor.

    Args:
        repo_root: Repository root path (auto-detected if None)

    Returns:
        SystemHealthMonitor instance
    """
    global _monitor_instance
    if _monitor_instance is None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[2]
        _monitor_instance = SystemHealthMonitor(repo_root)
    return _monitor_instance


def take_health_snapshot() -> Dict:
    """
    Convenience function for quick health check.

    Returns:
        Snapshot as dictionary
    """
    monitor = get_health_monitor()
    snapshot = monitor.take_snapshot()

    return {
        "timestamp": snapshot.timestamp,
        "health_score": snapshot.health_score,
        "status": snapshot.status.value,
        "alerts": snapshot.alerts,
        "readings": {
            name: {
                "value": r.value,
                "unit": METRIC_SPECIFICATIONS[name].unit,
                "within_bounds": r.within_bounds
            }
            for name, r in snapshot.readings.items()
            if name in METRIC_SPECIFICATIONS
        }
    }


def get_metrics_for_anomaly_detection() -> Tuple[Dict[str, float], Dict[str, float]]:
    """
    Get baseline and current metrics for anomaly detection.

    Returns:
        Tuple of (baseline_metrics, current_metrics)
    """
    monitor = get_health_monitor()
    return monitor.get_baseline(), monitor.get_current_metrics()
