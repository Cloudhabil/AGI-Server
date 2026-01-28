"""
Telemetry Collector Module

Lucas-priority sensor collection system.
Sensors are prioritized using Lucas numbers for natural scaling.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import defaultdict
import heapq
import time

# Constants
PHI = 1.618033988749895
GENESIS_CONSTANT = 2 / 901
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
TOTAL_STATES = 840


class SensorType(Enum):
    """Sensor types with Lucas priority indices."""
    TEMPERATURE = 0      # Priority: LUCAS[0] = 1
    HUMIDITY = 1         # Priority: LUCAS[1] = 3
    PRESSURE = 2         # Priority: LUCAS[2] = 4
    MOTION = 3           # Priority: LUCAS[3] = 7
    LIGHT = 4            # Priority: LUCAS[4] = 11
    SOUND = 5            # Priority: LUCAS[5] = 18
    VIBRATION = 6        # Priority: LUCAS[6] = 29
    GAS = 7              # Priority: LUCAS[7] = 47
    POWER = 8            # Priority: LUCAS[8] = 76
    NETWORK = 9          # Priority: LUCAS[9] = 123
    SECURITY = 10        # Priority: LUCAS[10] = 199
    CRITICAL = 11        # Priority: LUCAS[11] = 322


@dataclass
class SensorReading:
    """Individual sensor reading with metadata."""
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    timestamp: datetime = field(default_factory=datetime.now)
    quality: float = 1.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Sensor:
    """Sensor configuration with Lucas priority."""
    sensor_id: str
    sensor_type: SensorType
    device_id: str
    unit: str
    min_value: float = float('-inf')
    max_value: float = float('inf')
    sample_interval_ms: int = 1000
    enabled: bool = True

    @property
    def lucas_priority(self) -> int:
        """Get Lucas priority based on sensor type."""
        return LUCAS[self.sensor_type.value]

    @property
    def normalized_priority(self) -> float:
        """Get normalized priority (0.0 to 1.0) for scheduling."""
        max_lucas = LUCAS[-1]
        return self.lucas_priority / max_lucas


@dataclass
class CollectionBatch:
    """Batch of collected telemetry readings."""
    batch_id: str
    readings: List[SensorReading]
    collected_at: datetime
    total_priority: int
    processing_order: List[str]  # Sensor IDs in processing order


class TelemetryCollector:
    """
    Lucas-priority telemetry collection system.

    Sensors are prioritized using Lucas numbers, creating natural
    scaling where higher-indexed sensors (critical, security) get
    proportionally more attention.
    """

    def __init__(self, max_batch_size: int = 100):
        """
        Initialize telemetry collector.

        Args:
            max_batch_size: Maximum readings per collection batch
        """
        self.max_batch_size = max_batch_size
        self.sensors: Dict[str, Sensor] = {}
        self.reading_buffer: List[Tuple[int, datetime, SensorReading]] = []
        self.collection_history: List[CollectionBatch] = []
        self.batch_counter = 0

        # Priority queue for scheduling (min-heap, negate priority for max behavior)
        self._priority_queue: List[Tuple[int, str]] = []

    def register_sensor(
        self,
        sensor_id: str,
        sensor_type: SensorType,
        device_id: str,
        unit: str,
        **kwargs
    ) -> Sensor:
        """
        Register a new sensor.

        Args:
            sensor_id: Unique sensor identifier
            sensor_type: Type of sensor (determines Lucas priority)
            device_id: Parent device ID
            unit: Measurement unit
            **kwargs: Additional sensor configuration

        Returns:
            Registered Sensor instance
        """
        sensor = Sensor(
            sensor_id=sensor_id,
            sensor_type=sensor_type,
            device_id=device_id,
            unit=unit,
            **kwargs
        )

        self.sensors[sensor_id] = sensor

        # Add to priority queue (negate for max-heap behavior)
        heapq.heappush(
            self._priority_queue,
            (-sensor.lucas_priority, sensor_id)
        )

        return sensor

    def submit_reading(
        self,
        sensor_id: str,
        value: float,
        quality: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[SensorReading]:
        """
        Submit a sensor reading to the collection buffer.

        Args:
            sensor_id: Sensor that produced the reading
            value: Measured value
            quality: Reading quality (0.0 to 1.0)
            metadata: Optional additional metadata

        Returns:
            SensorReading instance or None if sensor not found
        """
        sensor = self.sensors.get(sensor_id)
        if not sensor or not sensor.enabled:
            return None

        reading = SensorReading(
            sensor_id=sensor_id,
            sensor_type=sensor.sensor_type,
            value=value,
            unit=sensor.unit,
            quality=quality,
            metadata=metadata or {}
        )

        # Add to buffer with priority
        priority = sensor.lucas_priority
        self.reading_buffer.append((priority, reading.timestamp, reading))

        return reading

    def collect_batch(self) -> CollectionBatch:
        """
        Collect a batch of readings, prioritized by Lucas numbers.

        Returns:
            CollectionBatch with prioritized readings
        """
        # Sort buffer by priority (descending) and timestamp
        self.reading_buffer.sort(key=lambda x: (-x[0], x[1]))

        # Take up to max_batch_size readings
        batch_readings = []
        processing_order = []
        total_priority = 0

        for i in range(min(len(self.reading_buffer), self.max_batch_size)):
            priority, _, reading = self.reading_buffer[i]
            batch_readings.append(reading)
            processing_order.append(reading.sensor_id)
            total_priority += priority

        # Remove collected readings from buffer
        self.reading_buffer = self.reading_buffer[len(batch_readings):]

        # Create batch
        self.batch_counter += 1
        batch = CollectionBatch(
            batch_id=f"batch-{self.batch_counter:06d}",
            readings=batch_readings,
            collected_at=datetime.now(),
            total_priority=total_priority,
            processing_order=processing_order
        )

        self.collection_history.append(batch)
        return batch

    def get_priority_schedule(self) -> List[Dict]:
        """Get the priority schedule for all registered sensors."""
        schedule = []

        for sensor in sorted(
            self.sensors.values(),
            key=lambda s: -s.lucas_priority
        ):
            schedule.append({
                "sensor_id": sensor.sensor_id,
                "type": sensor.sensor_type.name,
                "device_id": sensor.device_id,
                "lucas_priority": sensor.lucas_priority,
                "normalized_priority": round(sensor.normalized_priority, 4),
                "sample_interval_ms": sensor.sample_interval_ms,
                "enabled": sensor.enabled
            })

        return schedule

    def get_type_priorities(self) -> Dict[str, int]:
        """Get Lucas priorities for all sensor types."""
        return {
            sensor_type.name: LUCAS[sensor_type.value]
            for sensor_type in SensorType
        }

    def get_buffer_stats(self) -> Dict:
        """Get statistics about the reading buffer."""
        if not self.reading_buffer:
            return {
                "buffer_size": 0,
                "total_priority": 0,
                "priority_distribution": {}
            }

        priority_dist = defaultdict(int)
        total_priority = 0

        for priority, _, reading in self.reading_buffer:
            priority_dist[reading.sensor_type.name] += 1
            total_priority += priority

        return {
            "buffer_size": len(self.reading_buffer),
            "total_priority": total_priority,
            "priority_distribution": dict(priority_dist)
        }

    def get_collection_summary(self) -> Dict:
        """Get summary of collection history."""
        if not self.collection_history:
            return {
                "total_batches": 0,
                "total_readings": 0,
                "average_priority": 0.0
            }

        total_readings = sum(len(b.readings) for b in self.collection_history)
        total_priority = sum(b.total_priority for b in self.collection_history)

        return {
            "total_batches": len(self.collection_history),
            "total_readings": total_readings,
            "average_priority": total_priority / len(self.collection_history),
            "average_batch_size": total_readings / len(self.collection_history)
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Telemetry Collector Test - Lucas Priority Sensors")
    print("=" * 60)

    collector = TelemetryCollector(max_batch_size=20)

    # Display Lucas priorities for sensor types
    print("\nLucas Priority by Sensor Type:")
    print("-" * 40)
    print(f"{'Type':<15} {'Lucas Priority':>15}")
    print("-" * 40)

    for sensor_type, priority in collector.get_type_priorities().items():
        print(f"{sensor_type:<15} {priority:>15}")

    # Register various sensors
    print("\nRegistering Sensors:")
    print("-" * 40)

    test_sensors = [
        ("temp-001", SensorType.TEMPERATURE, "device-001", "C"),
        ("humid-001", SensorType.HUMIDITY, "device-001", "%"),
        ("press-001", SensorType.PRESSURE, "device-002", "hPa"),
        ("motion-001", SensorType.MOTION, "device-002", "bool"),
        ("light-001", SensorType.LIGHT, "device-003", "lux"),
        ("power-001", SensorType.POWER, "device-003", "W"),
        ("security-001", SensorType.SECURITY, "device-004", "level"),
        ("critical-001", SensorType.CRITICAL, "device-004", "status"),
    ]

    for sensor_id, sensor_type, device_id, unit in test_sensors:
        sensor = collector.register_sensor(sensor_id, sensor_type, device_id, unit)
        print(f"  {sensor_id}: {sensor_type.name} (priority: {sensor.lucas_priority})")

    # Submit readings
    print("\nSubmitting Readings:")
    print("-" * 40)

    import random
    random.seed(42)

    reading_data = [
        ("temp-001", 22.5),
        ("humid-001", 45.0),
        ("press-001", 1013.25),
        ("motion-001", 1.0),
        ("light-001", 500.0),
        ("power-001", 125.5),
        ("security-001", 0.0),
        ("critical-001", 1.0),
        ("temp-001", 22.7),
        ("security-001", 1.0),  # Security alert
        ("critical-001", 0.0),  # Critical status change
        ("temp-001", 22.6),
    ]

    for sensor_id, value in reading_data:
        reading = collector.submit_reading(sensor_id, value)
        if reading:
            print(f"  {sensor_id}: {value} {reading.unit}")

    # Get buffer stats before collection
    print("\nBuffer Stats (before collection):")
    print("-" * 40)
    stats = collector.get_buffer_stats()
    print(f"  Buffer Size: {stats['buffer_size']}")
    print(f"  Total Priority: {stats['total_priority']}")
    print(f"  Distribution: {stats['priority_distribution']}")

    # Collect batch
    print("\nCollecting Batch:")
    print("-" * 40)
    batch = collector.collect_batch()

    print(f"  Batch ID: {batch.batch_id}")
    print(f"  Readings: {len(batch.readings)}")
    print(f"  Total Priority: {batch.total_priority}")
    print(f"  Processing Order (by priority):")

    for i, reading in enumerate(batch.readings):
        sensor = collector.sensors[reading.sensor_id]
        print(f"    {i+1}. {reading.sensor_id} ({reading.sensor_type.name}) "
              f"- Priority: {sensor.lucas_priority}")

    # Priority schedule
    print("\nPriority Schedule:")
    print("-" * 60)
    print(f"{'Sensor':<15} {'Type':<12} {'Priority':>10} {'Normalized':>12}")
    print("-" * 60)

    for entry in collector.get_priority_schedule():
        print(
            f"{entry['sensor_id']:<15} "
            f"{entry['type']:<12} "
            f"{entry['lucas_priority']:>10} "
            f"{entry['normalized_priority']:>12.4f}"
        )

    # Collection summary
    print("\n" + "=" * 60)
    print("Collection Summary")
    print("-" * 40)
    summary = collector.get_collection_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")

    print("=" * 60)
    print("\nTest completed successfully!")
