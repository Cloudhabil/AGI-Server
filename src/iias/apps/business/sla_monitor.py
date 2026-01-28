"""
SLA Monitor - PHI-Threshold Alerts

Monitors Service Level Agreement metrics with thresholds derived from
mathematical constants:
- THETA_WARN = 0.632 (1 - 1/e, the "e-fold" threshold)
- THETA_CRITICAL = 0.391 (THETA_WARN / PHI)

These thresholds represent natural inflection points based on fundamental
mathematical constants.

Constants:
- PHI = 1.618033988749895
- THETA_WARN = 0.632 (63.2% - warning threshold)
- THETA_CRITICAL = 0.391 (39.1% - critical threshold, THETA_WARN/PHI)
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Callable
from enum import Enum
from datetime import datetime, timedelta
import math
import time

# IIAS Constants
PHI = 1.618033988749895
E = math.e
THETA_WARN = 0.632      # 1 - 1/e = 0.6321...
THETA_CRITICAL = 0.391  # THETA_WARN / PHI = 0.3907...


class AlertLevel(Enum):
    """SLA alert severity levels."""
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of SLA metrics."""
    UPTIME = "uptime"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    AVAILABILITY = "availability"


@dataclass
class SLAThreshold:
    """Threshold configuration for an SLA metric."""
    metric_type: MetricType
    target_value: float
    warn_threshold: float = THETA_WARN
    critical_threshold: float = THETA_CRITICAL
    is_upper_bound: bool = True  # True if exceeding target is bad


@dataclass
class MetricReading:
    """A single metric measurement."""
    timestamp: datetime
    metric_type: MetricType
    value: float
    metadata: Optional[dict] = None


@dataclass
class Alert:
    """Generated alert from SLA violation."""
    alert_id: str
    timestamp: datetime
    metric_type: MetricType
    level: AlertLevel
    current_value: float
    threshold_value: float
    target_value: float
    message: str
    phi_factor: float  # How far from PHI-equilibrium


@dataclass
class SLAStatus:
    """Current status of an SLA."""
    metric_type: MetricType
    current_value: float
    target_value: float
    compliance_ratio: float
    alert_level: AlertLevel
    time_to_breach: Optional[timedelta]
    phi_health_score: float


class SLAMonitor:
    """
    PHI-threshold SLA monitoring system.

    Uses mathematically-derived thresholds:
    - Warning at THETA_WARN (63.2%, 1-1/e)
    - Critical at THETA_CRITICAL (39.1%, THETA_WARN/PHI)
    """

    def __init__(self):
        """Initialize the SLA monitor."""
        self._thresholds: Dict[MetricType, SLAThreshold] = {}
        self._readings: Dict[MetricType, List[MetricReading]] = {}
        self._alerts: List[Alert] = []
        self._alert_counter = 0
        self._callbacks: Dict[AlertLevel, List[Callable]] = {
            AlertLevel.WARNING: [],
            AlertLevel.CRITICAL: []
        }

    def configure_sla(self, metric_type: MetricType,
                      target_value: float,
                      is_upper_bound: bool = True) -> SLAThreshold:
        """
        Configure an SLA threshold.

        Args:
            metric_type: Type of metric to monitor
            target_value: Target SLA value
            is_upper_bound: True if exceeding target is bad (e.g., latency)
                           False if falling below is bad (e.g., uptime)

        Returns:
            Configured SLAThreshold
        """
        threshold = SLAThreshold(
            metric_type=metric_type,
            target_value=target_value,
            warn_threshold=THETA_WARN,
            critical_threshold=THETA_CRITICAL,
            is_upper_bound=is_upper_bound
        )
        self._thresholds[metric_type] = threshold
        self._readings[metric_type] = []
        return threshold

    def register_callback(self, level: AlertLevel,
                          callback: Callable[[Alert], None]) -> None:
        """Register a callback for alert notifications."""
        if level in self._callbacks:
            self._callbacks[level].append(callback)

    def record_metric(self, metric_type: MetricType,
                      value: float) -> Optional[Alert]:
        """
        Record a metric reading and check for SLA violations.

        Args:
            metric_type: Type of metric
            value: Measured value

        Returns:
            Alert if threshold violated, None otherwise
        """
        reading = MetricReading(
            timestamp=datetime.now(),
            metric_type=metric_type,
            value=value
        )

        if metric_type not in self._readings:
            self._readings[metric_type] = []
        self._readings[metric_type].append(reading)

        # Check threshold
        if metric_type in self._thresholds:
            return self._check_threshold(reading)
        return None

    def _check_threshold(self, reading: MetricReading) -> Optional[Alert]:
        """Check if reading violates SLA threshold."""
        threshold = self._thresholds[reading.metric_type]
        target = threshold.target_value

        # Calculate compliance ratio
        if threshold.is_upper_bound:
            # For upper bounds (latency, error rate): lower is better
            # compliance = target / actual (higher when actual < target)
            compliance = target / reading.value if reading.value > 0 else 1.0
        else:
            # For lower bounds (uptime, throughput): higher is better
            # compliance = actual / target (higher when actual > target)
            compliance = reading.value / target if target > 0 else 0.0

        # Determine alert level
        if compliance >= 1.0:
            return None  # Within SLA

        # Calculate PHI-factor (distance from golden equilibrium)
        phi_factor = abs(compliance - (1/PHI))

        if compliance < THETA_CRITICAL:
            level = AlertLevel.CRITICAL
            threshold_value = target * THETA_CRITICAL
        elif compliance < THETA_WARN:
            level = AlertLevel.WARNING
            threshold_value = target * THETA_WARN
        else:
            return None  # Above warning threshold

        # Create alert
        self._alert_counter += 1
        alert = Alert(
            alert_id=f"SLA-{self._alert_counter:06d}",
            timestamp=reading.timestamp,
            metric_type=reading.metric_type,
            level=level,
            current_value=reading.value,
            threshold_value=threshold_value,
            target_value=target,
            message=self._format_alert_message(reading, level, compliance),
            phi_factor=phi_factor
        )

        self._alerts.append(alert)
        self._trigger_callbacks(alert)
        return alert

    def _format_alert_message(self, reading: MetricReading,
                              level: AlertLevel,
                              compliance: float) -> str:
        """Format alert message."""
        threshold = self._thresholds[reading.metric_type]
        return (f"{level.value.upper()}: {reading.metric_type.value} "
                f"at {reading.value:.2f} (target: {threshold.target_value:.2f}, "
                f"compliance: {compliance*100:.1f}%)")

    def _trigger_callbacks(self, alert: Alert) -> None:
        """Trigger registered callbacks for alert."""
        for callback in self._callbacks.get(alert.level, []):
            try:
                callback(alert)
            except Exception:
                pass  # Don't let callback errors break monitoring

    def get_status(self, metric_type: MetricType) -> Optional[SLAStatus]:
        """
        Get current SLA status for a metric.

        Args:
            metric_type: Metric to check

        Returns:
            Current SLAStatus or None if not configured
        """
        if metric_type not in self._thresholds:
            return None

        threshold = self._thresholds[metric_type]
        readings = self._readings.get(metric_type, [])

        if not readings:
            return SLAStatus(
                metric_type=metric_type,
                current_value=0.0,
                target_value=threshold.target_value,
                compliance_ratio=1.0,
                alert_level=AlertLevel.OK,
                time_to_breach=None,
                phi_health_score=1.0
            )

        # Use latest reading
        latest = readings[-1]

        # Calculate compliance
        if threshold.is_upper_bound:
            compliance = threshold.target_value / latest.value if latest.value > 0 else 1.0
        else:
            compliance = latest.value / threshold.target_value if threshold.target_value > 0 else 0.0

        # Determine level
        if compliance >= 1.0:
            level = AlertLevel.OK
        elif compliance >= THETA_WARN:
            level = AlertLevel.OK  # Close but still OK
        elif compliance >= THETA_CRITICAL:
            level = AlertLevel.WARNING
        else:
            level = AlertLevel.CRITICAL

        # Calculate PHI health score (1.0 = perfect, 0.0 = critical)
        phi_health = min(compliance * PHI, 1.0)

        # Estimate time to breach (simplified linear projection)
        time_to_breach = None
        if len(readings) >= 2 and level != AlertLevel.CRITICAL:
            # Calculate trend
            recent = readings[-5:] if len(readings) >= 5 else readings
            if len(recent) >= 2:
                values = [r.value for r in recent]
                trend = (values[-1] - values[0]) / len(values)
                if threshold.is_upper_bound and trend > 0:
                    # Degrading: estimate time to breach
                    breach_value = threshold.target_value / THETA_CRITICAL
                    if trend > 0:
                        time_to_breach_seconds = (breach_value - latest.value) / trend
                        if time_to_breach_seconds > 0:
                            time_to_breach = timedelta(seconds=time_to_breach_seconds)

        return SLAStatus(
            metric_type=metric_type,
            current_value=latest.value,
            target_value=threshold.target_value,
            compliance_ratio=min(compliance, 1.0),
            alert_level=level,
            time_to_breach=time_to_breach,
            phi_health_score=phi_health
        )

    def get_all_statuses(self) -> Dict[MetricType, SLAStatus]:
        """Get status for all configured SLAs."""
        return {
            metric_type: self.get_status(metric_type)
            for metric_type in self._thresholds
        }

    def get_alerts(self, level: Optional[AlertLevel] = None,
                   since: Optional[datetime] = None) -> List[Alert]:
        """
        Get alerts, optionally filtered.

        Args:
            level: Filter by alert level
            since: Filter alerts after this time

        Returns:
            List of matching alerts
        """
        alerts = self._alerts

        if level:
            alerts = [a for a in alerts if a.level == level]
        if since:
            alerts = [a for a in alerts if a.timestamp >= since]

        return alerts

    def get_threshold_derivation(self) -> dict:
        """Explain the mathematical derivation of thresholds."""
        return {
            "theta_warn": {
                "value": THETA_WARN,
                "exact": 1 - 1/E,
                "derivation": "1 - 1/e (63.21%)",
                "significance": "Natural decay threshold - 63.2% of events occur by time constant"
            },
            "theta_critical": {
                "value": THETA_CRITICAL,
                "exact": (1 - 1/E) / PHI,
                "derivation": "THETA_WARN / PHI (39.07%)",
                "significance": "Golden-ratio scaled critical point"
            },
            "relationship": {
                "ratio": THETA_WARN / THETA_CRITICAL,
                "equals_phi": abs(THETA_WARN / THETA_CRITICAL - PHI) < 0.01,
                "phi": PHI
            }
        }


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS SLA Monitor - PHI-Threshold Alerts")
    print("=" * 60)
    print(f"\nThreshold Constants:")
    print(f"  THETA_WARN:     {THETA_WARN} (1 - 1/e = {1-1/E:.6f})")
    print(f"  THETA_CRITICAL: {THETA_CRITICAL} (THETA_WARN/PHI = {THETA_WARN/PHI:.6f})")
    print(f"  PHI:            {PHI}")

    # Create monitor
    monitor = SLAMonitor()

    # Show threshold derivation
    print("\n--- Threshold Derivation ---")
    derivation = monitor.get_threshold_derivation()
    print(f"\n  Warning Threshold (THETA_WARN):")
    print(f"    Value:       {derivation['theta_warn']['value']}")
    print(f"    Exact:       {derivation['theta_warn']['exact']:.6f}")
    print(f"    Derivation:  {derivation['theta_warn']['derivation']}")
    print(f"    Significance: {derivation['theta_warn']['significance']}")

    print(f"\n  Critical Threshold (THETA_CRITICAL):")
    print(f"    Value:       {derivation['theta_critical']['value']}")
    print(f"    Exact:       {derivation['theta_critical']['exact']:.6f}")
    print(f"    Derivation:  {derivation['theta_critical']['derivation']}")
    print(f"    Significance: {derivation['theta_critical']['significance']}")

    print(f"\n  PHI Relationship:")
    print(f"    THETA_WARN / THETA_CRITICAL = {derivation['relationship']['ratio']:.6f}")
    print(f"    Equals PHI ({PHI:.6f}): {derivation['relationship']['equals_phi']}")

    # Configure SLAs
    print("\n--- Configuring SLAs ---")
    slas = [
        (MetricType.UPTIME, 99.9, False),      # Target 99.9%, higher is better
        (MetricType.RESPONSE_TIME, 200, True),  # Target 200ms, lower is better
        (MetricType.ERROR_RATE, 1.0, True),     # Target 1%, lower is better
        (MetricType.THROUGHPUT, 1000, False),   # Target 1000 req/s, higher is better
    ]

    for metric_type, target, is_upper in slas:
        threshold = monitor.configure_sla(metric_type, target, is_upper)
        print(f"  {metric_type.value:15} | Target: {target:>7} | "
              f"Warn at: {target * THETA_WARN:>7.1f} | "
              f"Critical at: {target * THETA_CRITICAL:>7.1f}")

    # Register alert callback
    def alert_handler(alert: Alert):
        print(f"  [CALLBACK] {alert.level.value.upper()}: {alert.message}")

    monitor.register_callback(AlertLevel.WARNING, alert_handler)
    monitor.register_callback(AlertLevel.CRITICAL, alert_handler)

    # Simulate metric readings
    print("\n--- Recording Metrics ---")
    test_readings = [
        (MetricType.UPTIME, 99.95),     # OK
        (MetricType.UPTIME, 65.0),      # Warning (65% of 99.9)
        (MetricType.UPTIME, 35.0),      # Critical

        (MetricType.RESPONSE_TIME, 180),  # OK
        (MetricType.RESPONSE_TIME, 350),  # Warning
        (MetricType.RESPONSE_TIME, 600),  # Critical

        (MetricType.ERROR_RATE, 0.5),    # OK
        (MetricType.ERROR_RATE, 1.8),    # Warning
        (MetricType.ERROR_RATE, 3.0),    # Critical
    ]

    for metric_type, value in test_readings:
        alert = monitor.record_metric(metric_type, value)
        status = "ALERT!" if alert else "OK"
        print(f"  {metric_type.value:15} = {value:>7.2f} [{status}]")

    # Show current status
    print("\n--- Current SLA Status ---")
    statuses = monitor.get_all_statuses()
    for metric_type, status in statuses.items():
        if status:
            print(f"\n  {metric_type.value}:")
            print(f"    Current:     {status.current_value:.2f}")
            print(f"    Target:      {status.target_value:.2f}")
            print(f"    Compliance:  {status.compliance_ratio*100:.1f}%")
            print(f"    Status:      {status.alert_level.value.upper()}")
            print(f"    PHI Health:  {status.phi_health_score:.3f}")

    # Alert summary
    print("\n--- Alert Summary ---")
    warnings = monitor.get_alerts(AlertLevel.WARNING)
    criticals = monitor.get_alerts(AlertLevel.CRITICAL)
    print(f"  Total Warnings:  {len(warnings)}")
    print(f"  Total Criticals: {len(criticals)}")

    for alert in criticals[-3:]:
        print(f"\n  {alert.alert_id}: {alert.message}")
        print(f"    PHI Factor: {alert.phi_factor:.4f}")

    # Verify PHI relationship
    print("\n--- PHI Threshold Verification ---")
    ratio = THETA_WARN / THETA_CRITICAL
    print(f"  THETA_WARN / THETA_CRITICAL = {ratio:.6f}")
    print(f"  PHI =                         {PHI:.6f}")
    print(f"  Difference:                   {abs(ratio - PHI):.6f}")
    print(f"  Status: {'VERIFIED' if abs(ratio - PHI) < 0.01 else 'FAILED'}")
