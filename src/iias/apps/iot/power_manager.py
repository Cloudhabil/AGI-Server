"""
Power Manager Module

840-mW budget allocation across device components.
Uses PHI-based golden ratio partitioning for optimal power distribution.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math

# Constants
PHI = 1.618033988749895
GENESIS_CONSTANT = 2 / 901
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
TOTAL_STATES = 840  # Total power budget in mW


class PowerState(Enum):
    """Device power states."""
    OFF = 0
    SLEEP = 1
    IDLE = 2
    LOW_POWER = 3
    NORMAL = 4
    HIGH_PERFORMANCE = 5
    BURST = 6


class ComponentType(Enum):
    """Device component types with base power weights."""
    CPU = 1          # Processing unit
    MEMORY = 2       # RAM/Storage
    RADIO = 3        # Wireless communication
    SENSORS = 4      # Sensor array
    DISPLAY = 5      # Visual output
    ACTUATORS = 6    # Motors/servos
    SECURITY = 7     # Encryption/authentication


@dataclass
class PowerComponent:
    """Individual power-consuming component."""
    component_id: str
    component_type: ComponentType
    device_id: str
    base_power_mw: float
    current_power_mw: float = 0.0
    allocated_budget_mw: float = 0.0
    power_state: PowerState = PowerState.IDLE
    efficiency: float = 0.85  # 0.0 to 1.0

    @property
    def utilization(self) -> float:
        """Current power utilization percentage."""
        if self.allocated_budget_mw <= 0:
            return 0.0
        return min(self.current_power_mw / self.allocated_budget_mw, 1.0)


@dataclass
class PowerBudget:
    """Power budget allocation for a device."""
    device_id: str
    total_budget_mw: float
    allocated_mw: float = 0.0
    component_allocations: Dict[str, float] = field(default_factory=dict)
    phi_partition: List[float] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def available_mw(self) -> float:
        """Remaining available power budget."""
        return max(0.0, self.total_budget_mw - self.allocated_mw)

    @property
    def utilization_percentage(self) -> float:
        """Budget utilization percentage."""
        if self.total_budget_mw <= 0:
            return 0.0
        return (self.allocated_mw / self.total_budget_mw) * 100


class PowerManager:
    """
    840-mW power budget manager using PHI-based allocation.

    Distributes power across device components using golden ratio
    partitioning for optimal efficiency. The total budget is TOTAL_STATES (840 mW).
    """

    def __init__(self, total_budget_mw: float = TOTAL_STATES):
        """
        Initialize power manager.

        Args:
            total_budget_mw: Total power budget (default: 840 mW)
        """
        self.total_budget_mw = total_budget_mw
        self.devices: Dict[str, PowerBudget] = {}
        self.components: Dict[str, PowerComponent] = {}
        self.power_history: List[Dict] = []

        # Compute PHI-based partition for 7 component types
        self.phi_partition = self._compute_phi_partition(len(ComponentType))

    def _compute_phi_partition(self, n_partitions: int) -> List[float]:
        """
        Compute PHI-based power partition ratios.

        Uses golden ratio to create naturally balanced partitions where
        each partition is PHI times smaller than the previous.

        Args:
            n_partitions: Number of partitions needed

        Returns:
            List of partition ratios summing to 1.0
        """
        if n_partitions <= 0:
            return []

        # Generate PHI-weighted values
        weights = []
        for i in range(n_partitions):
            # Higher index = lower weight (inverse PHI scaling)
            weight = 1.0 / (PHI ** i)
            weights.append(weight)

        # Normalize to sum to 1.0
        total_weight = sum(weights)
        return [w / total_weight for w in weights]

    def _compute_lucas_weights(self) -> Dict[ComponentType, float]:
        """Compute Lucas-weighted component priorities."""
        weights = {}
        total_lucas = sum(LUCAS[:len(ComponentType)])

        for i, comp_type in enumerate(ComponentType):
            lucas_val = LUCAS[i % len(LUCAS)]
            weights[comp_type] = lucas_val / total_lucas

        return weights

    def register_device(self, device_id: str) -> PowerBudget:
        """
        Register a new device with power budget.

        Args:
            device_id: Unique device identifier

        Returns:
            PowerBudget instance for the device
        """
        budget = PowerBudget(
            device_id=device_id,
            total_budget_mw=self.total_budget_mw,
            phi_partition=self.phi_partition.copy()
        )

        self.devices[device_id] = budget
        return budget

    def register_component(
        self,
        component_id: str,
        component_type: ComponentType,
        device_id: str,
        base_power_mw: float,
        efficiency: float = 0.85
    ) -> Optional[PowerComponent]:
        """
        Register a power-consuming component.

        Args:
            component_id: Unique component identifier
            component_type: Type of component
            device_id: Parent device ID
            base_power_mw: Base power consumption in mW
            efficiency: Component efficiency (0.0 to 1.0)

        Returns:
            PowerComponent instance or None if device not found
        """
        if device_id not in self.devices:
            return None

        component = PowerComponent(
            component_id=component_id,
            component_type=component_type,
            device_id=device_id,
            base_power_mw=base_power_mw,
            efficiency=efficiency
        )

        self.components[component_id] = component
        return component

    def allocate_power(self, device_id: str) -> Optional[Dict[str, float]]:
        """
        Allocate power budget to device components using PHI partitioning.

        Args:
            device_id: Device to allocate power for

        Returns:
            Dict of component_id -> allocated_mw or None if device not found
        """
        budget = self.devices.get(device_id)
        if not budget:
            return None

        # Get components for this device
        device_components = [
            c for c in self.components.values()
            if c.device_id == device_id
        ]

        if not device_components:
            return {}

        # Sort by component type value (matches PHI partition order)
        device_components.sort(key=lambda c: c.component_type.value)

        # Allocate based on PHI partition
        allocations = {}
        total_allocated = 0.0

        for i, component in enumerate(device_components):
            # Use PHI partition ratio, falling back to equal distribution
            if i < len(self.phi_partition):
                ratio = self.phi_partition[i]
            else:
                ratio = 1.0 / len(device_components)

            # Calculate allocation considering base power needs
            allocation = budget.total_budget_mw * ratio

            # Ensure minimum for base power (with efficiency adjustment)
            min_required = component.base_power_mw / component.efficiency
            allocation = max(allocation, min_required)

            # Cap to available budget
            allocation = min(allocation, budget.total_budget_mw - total_allocated)

            component.allocated_budget_mw = allocation
            allocations[component.component_id] = allocation
            budget.component_allocations[component.component_id] = allocation
            total_allocated += allocation

        budget.allocated_mw = total_allocated
        return allocations

    def set_component_power(
        self,
        component_id: str,
        power_mw: float
    ) -> bool:
        """
        Set current power consumption for a component.

        Args:
            component_id: Component identifier
            power_mw: Current power in mW

        Returns:
            True if within budget, False if exceeds allocation
        """
        component = self.components.get(component_id)
        if not component:
            return False

        component.current_power_mw = power_mw

        # Record in history
        self.power_history.append({
            "component_id": component_id,
            "power_mw": power_mw,
            "allocated_mw": component.allocated_budget_mw,
            "timestamp": datetime.now().isoformat()
        })

        return power_mw <= component.allocated_budget_mw

    def set_power_state(
        self,
        component_id: str,
        state: PowerState
    ) -> Optional[float]:
        """
        Set component power state and adjust power accordingly.

        Args:
            component_id: Component identifier
            state: Target power state

        Returns:
            New power consumption in mW or None if component not found
        """
        component = self.components.get(component_id)
        if not component:
            return None

        component.power_state = state

        # Calculate power based on state
        state_multipliers = {
            PowerState.OFF: 0.0,
            PowerState.SLEEP: 0.05,
            PowerState.IDLE: 0.15,
            PowerState.LOW_POWER: 0.35,
            PowerState.NORMAL: 0.70,
            PowerState.HIGH_PERFORMANCE: 0.90,
            PowerState.BURST: 1.0,
        }

        multiplier = state_multipliers.get(state, 0.5)
        new_power = component.base_power_mw * multiplier
        component.current_power_mw = new_power

        return new_power

    def get_device_power_status(self, device_id: str) -> Optional[Dict]:
        """Get detailed power status for a device."""
        budget = self.devices.get(device_id)
        if not budget:
            return None

        device_components = [
            c for c in self.components.values()
            if c.device_id == device_id
        ]

        total_current = sum(c.current_power_mw for c in device_components)

        return {
            "device_id": device_id,
            "total_budget_mw": budget.total_budget_mw,
            "allocated_mw": budget.allocated_mw,
            "current_consumption_mw": total_current,
            "available_mw": budget.available_mw,
            "utilization_percentage": budget.utilization_percentage,
            "headroom_mw": budget.total_budget_mw - total_current,
            "components": [
                {
                    "component_id": c.component_id,
                    "type": c.component_type.name,
                    "allocated_mw": c.allocated_budget_mw,
                    "current_mw": c.current_power_mw,
                    "utilization": c.utilization,
                    "state": c.power_state.name
                }
                for c in device_components
            ]
        }

    def get_phi_allocation_report(self) -> Dict:
        """Get report on PHI-based power allocation."""
        return {
            "total_budget_mw": self.total_budget_mw,
            "phi_constant": PHI,
            "partition_ratios": [round(p, 6) for p in self.phi_partition],
            "partition_mw": [
                round(p * self.total_budget_mw, 2)
                for p in self.phi_partition
            ],
            "component_types": [ct.name for ct in ComponentType]
        }

    def optimize_allocation(self, device_id: str) -> Optional[Dict[str, float]]:
        """
        Optimize power allocation based on current utilization.

        Reallocates unused power from low-utilization components
        to high-utilization ones.

        Args:
            device_id: Device to optimize

        Returns:
            New allocation dict or None if device not found
        """
        budget = self.devices.get(device_id)
        if not budget:
            return None

        device_components = [
            c for c in self.components.values()
            if c.device_id == device_id
        ]

        if not device_components:
            return {}

        # Calculate unused power
        total_unused = sum(
            max(0, c.allocated_budget_mw - c.current_power_mw)
            for c in device_components
        )

        # Find components that need more power
        needs_more = [
            c for c in device_components
            if c.current_power_mw >= c.allocated_budget_mw * 0.9
        ]

        if not needs_more or total_unused <= 0:
            return budget.component_allocations

        # Redistribute based on Lucas weights
        lucas_weights = self._compute_lucas_weights()

        for component in needs_more:
            weight = lucas_weights.get(component.component_type, 0.1)
            bonus = total_unused * weight
            component.allocated_budget_mw += bonus
            budget.component_allocations[component.component_id] = component.allocated_budget_mw

        return budget.component_allocations


if __name__ == "__main__":
    print("=" * 60)
    print("Power Manager Test - 840-mW Budget Allocation")
    print("=" * 60)

    manager = PowerManager(total_budget_mw=TOTAL_STATES)

    # Display PHI allocation scheme
    print(f"\nTotal Budget: {TOTAL_STATES} mW")
    print(f"PHI Constant: {PHI}")

    print("\nPHI-Based Allocation Scheme:")
    print("-" * 50)
    report = manager.get_phi_allocation_report()

    print(f"{'Component Type':<18} {'Ratio':>10} {'Allocation (mW)':>15}")
    print("-" * 50)

    for i, comp_type in enumerate(ComponentType):
        if i < len(report['partition_ratios']):
            ratio = report['partition_ratios'][i]
            alloc = report['partition_mw'][i]
            print(f"{comp_type.name:<18} {ratio:>10.4f} {alloc:>15.2f}")

    total_ratio = sum(report['partition_ratios'])
    total_alloc = sum(report['partition_mw'])
    print("-" * 50)
    print(f"{'TOTAL':<18} {total_ratio:>10.4f} {total_alloc:>15.2f}")

    # Register device and components
    print("\nRegistering Device and Components:")
    print("-" * 40)

    device_id = "iot-device-001"
    manager.register_device(device_id)

    test_components = [
        ("cpu-001", ComponentType.CPU, 120.0),
        ("mem-001", ComponentType.MEMORY, 80.0),
        ("radio-001", ComponentType.RADIO, 150.0),
        ("sensor-001", ComponentType.SENSORS, 50.0),
        ("display-001", ComponentType.DISPLAY, 200.0),
        ("actuator-001", ComponentType.ACTUATORS, 100.0),
        ("security-001", ComponentType.SECURITY, 40.0),
    ]

    for comp_id, comp_type, base_power in test_components:
        component = manager.register_component(
            comp_id, comp_type, device_id, base_power
        )
        print(f"  {comp_id}: {comp_type.name} (base: {base_power} mW)")

    # Allocate power
    print("\nAllocating Power:")
    print("-" * 40)

    allocations = manager.allocate_power(device_id)
    for comp_id, alloc in allocations.items():
        component = manager.components[comp_id]
        print(f"  {comp_id}: {alloc:.2f} mW allocated")

    # Simulate power consumption
    print("\nSimulating Power States:")
    print("-" * 40)

    state_assignments = [
        ("cpu-001", PowerState.NORMAL),
        ("mem-001", PowerState.NORMAL),
        ("radio-001", PowerState.LOW_POWER),
        ("sensor-001", PowerState.IDLE),
        ("display-001", PowerState.HIGH_PERFORMANCE),
        ("actuator-001", PowerState.IDLE),
        ("security-001", PowerState.NORMAL),
    ]

    for comp_id, state in state_assignments:
        power = manager.set_power_state(comp_id, state)
        print(f"  {comp_id}: {state.name} -> {power:.2f} mW")

    # Get device status
    print("\nDevice Power Status:")
    print("-" * 60)
    status = manager.get_device_power_status(device_id)

    print(f"Device: {status['device_id']}")
    print(f"Total Budget: {status['total_budget_mw']} mW")
    print(f"Allocated: {status['allocated_mw']:.2f} mW")
    print(f"Current Consumption: {status['current_consumption_mw']:.2f} mW")
    print(f"Headroom: {status['headroom_mw']:.2f} mW")
    print(f"Utilization: {status['utilization_percentage']:.1f}%")

    print("\nComponent Breakdown:")
    print("-" * 70)
    print(f"{'Component':<15} {'Type':<12} {'Allocated':>10} {'Current':>10} {'Util':>8} {'State':<12}")
    print("-" * 70)

    for comp in status['components']:
        print(
            f"{comp['component_id']:<15} "
            f"{comp['type']:<12} "
            f"{comp['allocated_mw']:>10.2f} "
            f"{comp['current_mw']:>10.2f} "
            f"{comp['utilization']*100:>7.1f}% "
            f"{comp['state']:<12}"
        )

    # Optimization
    print("\n" + "=" * 60)
    print("Running Power Optimization...")
    print("-" * 40)

    optimized = manager.optimize_allocation(device_id)
    print("Optimization complete. New allocations applied.")

    print("=" * 60)
    print("\nTest completed successfully!")
