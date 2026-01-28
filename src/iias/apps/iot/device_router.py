"""
Device Router Module

12-class device taxonomy based on dimensions using PHI golden ratio scaling.
Routes IoT devices to appropriate handlers based on dimensional classification.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math

# Constants
PHI = 1.618033988749895
GENESIS_CONSTANT = 2 / 901
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
TOTAL_STATES = 840


class DeviceClass(Enum):
    """12-class device taxonomy based on dimensional scaling."""
    NANO = 1        # Sub-millimeter sensors
    MICRO = 2       # Millimeter-scale devices
    MINI = 3        # Centimeter-scale devices
    COMPACT = 4     # Palm-sized devices
    STANDARD = 5    # Handheld devices
    MEDIUM = 6      # Portable devices
    LARGE = 7       # Desktop-scale devices
    XLARGE = 8      # Appliance-scale devices
    INDUSTRIAL = 9  # Industrial equipment
    MACHINERY = 10  # Heavy machinery
    FACILITY = 11   # Facility-level systems
    CAMPUS = 12     # Campus/site-level infrastructure


@dataclass
class DeviceProfile:
    """Profile containing device classification and routing info."""
    device_id: str
    device_class: DeviceClass
    dimensions: Tuple[float, float, float]  # width, height, depth in mm
    volume_mm3: float
    phi_dimension_index: int
    routing_priority: int
    handler_endpoint: str


class DeviceRouter:
    """
    Routes IoT devices based on 12-class dimensional taxonomy.

    Uses PHI-based scaling to determine device class boundaries.
    Each class boundary is PHI times the previous boundary.
    """

    def __init__(self, base_dimension_mm: float = 1.0):
        """
        Initialize router with base dimension for class boundaries.

        Args:
            base_dimension_mm: Base dimension in mm for class 1 (NANO)
        """
        self.base_dimension = base_dimension_mm
        self.class_boundaries = self._compute_class_boundaries()
        self.routing_table: Dict[DeviceClass, str] = self._init_routing_table()
        self.registered_devices: Dict[str, DeviceProfile] = {}

    def _compute_class_boundaries(self) -> List[float]:
        """Compute 12 class boundaries using PHI scaling."""
        boundaries = []
        for i in range(12):
            # Each boundary is PHI^i * base_dimension
            boundary = self.base_dimension * (PHI ** i)
            boundaries.append(boundary)
        return boundaries

    def _init_routing_table(self) -> Dict[DeviceClass, str]:
        """Initialize default routing endpoints for each device class."""
        return {
            DeviceClass.NANO: "/api/v1/devices/nano",
            DeviceClass.MICRO: "/api/v1/devices/micro",
            DeviceClass.MINI: "/api/v1/devices/mini",
            DeviceClass.COMPACT: "/api/v1/devices/compact",
            DeviceClass.STANDARD: "/api/v1/devices/standard",
            DeviceClass.MEDIUM: "/api/v1/devices/medium",
            DeviceClass.LARGE: "/api/v1/devices/large",
            DeviceClass.XLARGE: "/api/v1/devices/xlarge",
            DeviceClass.INDUSTRIAL: "/api/v1/devices/industrial",
            DeviceClass.MACHINERY: "/api/v1/devices/machinery",
            DeviceClass.FACILITY: "/api/v1/devices/facility",
            DeviceClass.CAMPUS: "/api/v1/devices/campus",
        }

    def classify_device(self, dimensions: Tuple[float, float, float]) -> DeviceClass:
        """
        Classify a device based on its dimensions.

        Args:
            dimensions: Tuple of (width, height, depth) in mm

        Returns:
            DeviceClass enum value
        """
        # Use the maximum dimension for classification
        max_dim = max(dimensions)

        # Find the appropriate class based on PHI-scaled boundaries
        for i, boundary in enumerate(self.class_boundaries):
            if max_dim <= boundary * PHI:
                return DeviceClass(i + 1)

        # Default to highest class if exceeds all boundaries
        return DeviceClass.CAMPUS

    def compute_phi_index(self, dimensions: Tuple[float, float, float]) -> int:
        """
        Compute PHI dimension index for fine-grained routing.

        Args:
            dimensions: Device dimensions in mm

        Returns:
            PHI-based index (0-840 range based on TOTAL_STATES)
        """
        volume = dimensions[0] * dimensions[1] * dimensions[2]
        # Map volume to state index using logarithmic PHI scaling
        if volume <= 0:
            return 0
        log_volume = math.log(volume) / math.log(PHI)
        index = int(log_volume) % TOTAL_STATES
        return index

    def register_device(
        self,
        device_id: str,
        dimensions: Tuple[float, float, float]
    ) -> DeviceProfile:
        """
        Register a new device and compute its routing profile.

        Args:
            device_id: Unique device identifier
            dimensions: Device dimensions (width, height, depth) in mm

        Returns:
            DeviceProfile with classification and routing info
        """
        device_class = self.classify_device(dimensions)
        volume = dimensions[0] * dimensions[1] * dimensions[2]
        phi_index = self.compute_phi_index(dimensions)

        # Priority based on Lucas number at class index
        lucas_index = (device_class.value - 1) % len(LUCAS)
        priority = LUCAS[lucas_index]

        profile = DeviceProfile(
            device_id=device_id,
            device_class=device_class,
            dimensions=dimensions,
            volume_mm3=volume,
            phi_dimension_index=phi_index,
            routing_priority=priority,
            handler_endpoint=self.routing_table[device_class]
        )

        self.registered_devices[device_id] = profile
        return profile

    def route_device(self, device_id: str) -> Optional[str]:
        """
        Get routing endpoint for a registered device.

        Args:
            device_id: Device identifier

        Returns:
            Routing endpoint or None if not registered
        """
        profile = self.registered_devices.get(device_id)
        if profile:
            return profile.handler_endpoint
        return None

    def get_devices_by_class(self, device_class: DeviceClass) -> List[DeviceProfile]:
        """Get all registered devices of a specific class."""
        return [
            profile for profile in self.registered_devices.values()
            if profile.device_class == device_class
        ]

    def get_class_boundaries_report(self) -> Dict[str, float]:
        """Get report of all class boundaries in mm."""
        return {
            DeviceClass(i + 1).name: boundary
            for i, boundary in enumerate(self.class_boundaries)
        }


if __name__ == "__main__":
    print("=" * 60)
    print("Device Router Test - 12-Class Dimensional Taxonomy")
    print("=" * 60)

    router = DeviceRouter(base_dimension_mm=1.0)

    # Display class boundaries
    print("\nPHI-scaled Class Boundaries (mm):")
    print("-" * 40)
    for name, boundary in router.get_class_boundaries_report().items():
        print(f"  {name:12s}: {boundary:>12.4f} mm")

    # Test device registrations across different scales
    test_devices = [
        ("sensor-001", (0.5, 0.5, 0.2)),      # NANO
        ("sensor-002", (2.0, 1.5, 1.0)),      # MICRO
        ("sensor-003", (15.0, 10.0, 5.0)),    # MINI
        ("phone-001", (70.0, 150.0, 8.0)),    # COMPACT/STANDARD
        ("tablet-001", (200.0, 280.0, 7.0)),  # MEDIUM
        ("server-001", (500.0, 800.0, 400.0)),# LARGE
        ("machine-001", (2000.0, 3000.0, 1500.0)),  # INDUSTRIAL
    ]

    print("\nDevice Registration Results:")
    print("-" * 60)
    for device_id, dims in test_devices:
        profile = router.register_device(device_id, dims)
        print(f"\nDevice: {device_id}")
        print(f"  Dimensions: {dims} mm")
        print(f"  Class: {profile.device_class.name}")
        print(f"  Volume: {profile.volume_mm3:.2f} mm^3")
        print(f"  PHI Index: {profile.phi_dimension_index}")
        print(f"  Priority (Lucas): {profile.routing_priority}")
        print(f"  Endpoint: {profile.handler_endpoint}")

    # Summary
    print("\n" + "=" * 60)
    print("Summary Statistics")
    print("-" * 40)
    print(f"Total Registered Devices: {len(router.registered_devices)}")
    print(f"PHI Constant: {PHI}")
    print(f"Total States: {TOTAL_STATES}")
    print("=" * 60)
    print("\nTest completed successfully!")
