"""
IIAS Security: Anomaly Detector

214-deviation threshold anomaly detection.
Formula: anomaly if |value - expected| > 214 * sensitivity

The 214 constant (SUM_CONSTANT) provides the baseline deviation threshold,
which can be scaled by sensitivity for different security contexts.
"""

import math
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime
from collections import deque
from enum import Enum

# Sacred Constants
PHI = 1.618033988749895
SUM_CONSTANT = 214
D3_CAPACITY = 4


class AnomalyType(Enum):
    """Types of detected anomalies."""
    DEVIATION = "deviation"         # Value deviates from expected
    SPIKE = "spike"                 # Sudden increase
    DROP = "drop"                   # Sudden decrease
    PATTERN = "pattern"             # Pattern violation
    THRESHOLD = "threshold"         # Absolute threshold breach


@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    anomaly_id: str
    timestamp: datetime
    anomaly_type: AnomalyType
    value: float
    expected: float
    deviation: float
    threshold: float
    severity: float
    context: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "anomaly_id": self.anomaly_id,
            "timestamp": self.timestamp.isoformat(),
            "type": self.anomaly_type.value,
            "value": self.value,
            "expected": self.expected,
            "deviation": self.deviation,
            "threshold": self.threshold,
            "severity": self.severity,
            "context": self.context,
        }


class AnomalyDetector:
    """
    214-Deviation Threshold Anomaly Detector

    Detects anomalies using the formula:
    anomaly if |value - expected| > 214 * sensitivity

    The detector maintains a rolling window of values to compute
    expected values and uses the 214 constant as the baseline
    deviation threshold.

    Attributes:
        sensitivity: Threshold multiplier (lower = more sensitive)
        window_size: Number of values to maintain for statistics
        sum_constant: The 214 baseline threshold
    """

    def __init__(
        self,
        sensitivity: float = 1.0,
        window_size: int = 100,
        use_median: bool = False
    ):
        """
        Initialize the anomaly detector.

        Args:
            sensitivity: Threshold sensitivity multiplier
            window_size: Rolling window size for statistics
            use_median: Use median instead of mean for expected value
        """
        self.sensitivity = sensitivity
        self.window_size = window_size
        self.use_median = use_median
        self.sum_constant = SUM_CONSTANT

        self._values: deque = deque(maxlen=window_size)
        self._anomalies: List[Anomaly] = []
        self._anomaly_counter = 0
        self._total_checks = 0

    def calculate_threshold(self) -> float:
        """
        Calculate the 214-deviation threshold.

        Returns:
            Current anomaly threshold
        """
        return self.sum_constant * self.sensitivity

    def get_expected_value(self) -> Optional[float]:
        """
        Get the expected value from the rolling window.

        Returns:
            Expected value or None if insufficient data
        """
        if len(self._values) < 2:
            return None

        if self.use_median:
            return statistics.median(self._values)
        else:
            return statistics.mean(self._values)

    def get_standard_deviation(self) -> Optional[float]:
        """Get standard deviation of the rolling window."""
        if len(self._values) < 2:
            return None
        return statistics.stdev(self._values)

    def check(
        self,
        value: float,
        expected: Optional[float] = None,
        context: Optional[Dict] = None
    ) -> Tuple[bool, Optional[Anomaly]]:
        """
        Check if a value is anomalous.

        Args:
            value: The value to check
            expected: Optional explicit expected value (uses rolling if None)
            context: Optional context dictionary

        Returns:
            Tuple of (is_anomaly, Anomaly if detected else None)
        """
        self._total_checks += 1

        # Determine expected value
        if expected is None:
            expected = self.get_expected_value()

        # If no expected value yet, just record and return
        if expected is None:
            self._values.append(value)
            return False, None

        # Calculate deviation
        deviation = abs(value - expected)
        threshold = self.calculate_threshold()

        # Add to rolling window
        self._values.append(value)

        # Check if anomalous: |value - expected| > 214 * sensitivity
        is_anomaly = deviation > threshold

        if is_anomaly:
            # Determine anomaly type
            if value > expected:
                anomaly_type = AnomalyType.SPIKE
            else:
                anomaly_type = AnomalyType.DROP

            # Calculate severity (how many thresholds exceeded)
            severity = min(1.0, deviation / (threshold * D3_CAPACITY))

            # Create anomaly record
            self._anomaly_counter += 1
            anomaly = Anomaly(
                anomaly_id=f"ANM-{self._anomaly_counter:06d}",
                timestamp=datetime.now(),
                anomaly_type=anomaly_type,
                value=value,
                expected=expected,
                deviation=deviation,
                threshold=threshold,
                severity=severity,
                context=context or {},
            )

            self._anomalies.append(anomaly)
            return True, anomaly

        return False, None

    def check_batch(
        self,
        values: List[float],
        context: Optional[Dict] = None
    ) -> List[Anomaly]:
        """
        Check multiple values for anomalies.

        Args:
            values: List of values to check
            context: Optional context for all values

        Returns:
            List of detected anomalies
        """
        anomalies = []
        for value in values:
            is_anomaly, anomaly = self.check(value, context=context)
            if anomaly:
                anomalies.append(anomaly)
        return anomalies

    def check_with_adaptive_threshold(
        self,
        value: float,
        context: Optional[Dict] = None
    ) -> Tuple[bool, Optional[Anomaly]]:
        """
        Check with threshold adapted by rolling standard deviation.

        The threshold is: 214 * sensitivity * (1 + stdev/PHI)

        Args:
            value: The value to check
            context: Optional context dictionary

        Returns:
            Tuple of (is_anomaly, Anomaly if detected else None)
        """
        stdev = self.get_standard_deviation()

        if stdev is not None and stdev > 0:
            # Adapt sensitivity based on variance
            adaptive_sensitivity = self.sensitivity * (1 + stdev / PHI)
            original_sensitivity = self.sensitivity
            self.sensitivity = adaptive_sensitivity

            result = self.check(value, context=context)

            self.sensitivity = original_sensitivity
            return result
        else:
            return self.check(value, context=context)

    def get_anomaly_rate(self) -> float:
        """Get the anomaly detection rate."""
        if self._total_checks == 0:
            return 0.0
        return len(self._anomalies) / self._total_checks

    def get_recent_anomalies(self, count: int = 10) -> List[Anomaly]:
        """Get the most recent anomalies."""
        return self._anomalies[-count:]

    def get_anomalies_by_type(self, anomaly_type: AnomalyType) -> List[Anomaly]:
        """Get anomalies filtered by type."""
        return [a for a in self._anomalies if a.anomaly_type == anomaly_type]

    def get_statistics(self) -> Dict:
        """Get detector statistics."""
        stats = {
            "total_checks": self._total_checks,
            "total_anomalies": len(self._anomalies),
            "anomaly_rate": self.get_anomaly_rate(),
            "sensitivity": self.sensitivity,
            "threshold": self.calculate_threshold(),
            "window_size": self.window_size,
            "current_window_count": len(self._values),
            "sum_constant": self.sum_constant,
        }

        if len(self._values) >= 2:
            stats["expected_value"] = self.get_expected_value()
            stats["standard_deviation"] = self.get_standard_deviation()

        return stats

    def reset(self):
        """Reset the detector state."""
        self._values.clear()
        self._anomalies.clear()
        self._anomaly_counter = 0
        self._total_checks = 0

    def seed_baseline(self, values: List[float]):
        """
        Seed the detector with baseline values.

        Args:
            values: Baseline values to establish normal behavior
        """
        for value in values:
            self._values.append(value)


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Security: Anomaly Detector Test")
    print("=" * 60)
    print(f"\nSUM_CONSTANT (214): {SUM_CONSTANT}")
    print(f"Formula: anomaly if |value - expected| > 214 * sensitivity")

    # Create detector
    detector = AnomalyDetector(sensitivity=0.1, window_size=50)

    print(f"\nConfiguration:")
    print(f"  Sensitivity: {detector.sensitivity}")
    print(f"  Threshold: {detector.calculate_threshold()}")
    print(f"  Window size: {detector.window_size}")

    # Seed with baseline data
    print("\n--- Seeding Baseline ---")
    baseline = [100 + (i % 10) for i in range(30)]
    detector.seed_baseline(baseline)
    print(f"  Seeded with {len(baseline)} values")
    print(f"  Expected value: {detector.get_expected_value():.2f}")
    print(f"  Standard deviation: {detector.get_standard_deviation():.2f}")

    # Test normal values
    print("\n--- Testing Normal Values ---")
    normal_values = [102, 98, 105, 103, 99, 101, 104, 97]
    for value in normal_values:
        is_anomaly, anomaly = detector.check(value)
        status = "ANOMALY" if is_anomaly else "NORMAL"
        expected = detector.get_expected_value()
        print(f"  Value: {value:6.1f} | Expected: {expected:6.2f} | {status}")

    # Test anomalous values
    print("\n--- Testing Anomalous Values ---")
    anomalous_values = [150, 50, 200, 10, 180]
    for value in anomalous_values:
        is_anomaly, anomaly = detector.check(value)
        status = "ANOMALY" if is_anomaly else "NORMAL"
        if anomaly:
            print(f"  Value: {value:6.1f} | {status}")
            print(f"    Type: {anomaly.anomaly_type.value}")
            print(f"    Deviation: {anomaly.deviation:.2f}")
            print(f"    Severity: {anomaly.severity:.2%}")
        else:
            expected = detector.get_expected_value()
            print(f"  Value: {value:6.1f} | Expected: {expected:6.2f} | {status}")

    # Test adaptive threshold
    print("\n--- Testing Adaptive Threshold ---")
    detector.reset()
    detector.seed_baseline([100 + (i % 5) for i in range(30)])  # Low variance

    test_value = 130
    is_anomaly, anomaly = detector.check_with_adaptive_threshold(test_value)
    print(f"  Low variance baseline:")
    print(f"    Value {test_value}: {'ANOMALY' if is_anomaly else 'NORMAL'}")

    detector.reset()
    detector.seed_baseline([100 + (i % 50) for i in range(30)])  # High variance

    is_anomaly, anomaly = detector.check_with_adaptive_threshold(test_value)
    print(f"  High variance baseline:")
    print(f"    Value {test_value}: {'ANOMALY' if is_anomaly else 'NORMAL'}")

    # Statistics
    print("\n--- Statistics ---")
    # Reset and do full test
    detector.reset()
    detector.seed_baseline(baseline)
    for v in normal_values + anomalous_values:
        detector.check(v)

    stats = detector.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    # Anomaly summary
    print("\n--- Anomaly Summary ---")
    for atype in AnomalyType:
        count = len(detector.get_anomalies_by_type(atype))
        if count > 0:
            print(f"  {atype.value}: {count}")

    print("\n" + "=" * 60)
    print("Anomaly Detector Test Complete")
    print("=" * 60)
