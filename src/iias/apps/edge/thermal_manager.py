"""IIAS Edge Thermal Manager - PHI-based Throttling

This module manages thermal constraints using PHI (Golden Ratio) based
throttling curves. When temperature exceeds thresholds, computational
intensity is scaled down following PHI-harmonic reduction patterns.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple
import time
import math

# Constants
PHI = 1.618033988749895
PHI_INVERSE = 1 / PHI  # 0.618033988749895
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]


class ThermalZone(Enum):
    """Thermal zones with PHI-based thresholds."""
    COOL = 0       # < 45C - Full performance
    WARM = 1       # 45-55C - Light throttle
    HOT = 2        # 55-70C - Medium throttle
    CRITICAL = 3   # 70-85C - Heavy throttle
    EMERGENCY = 4  # > 85C - Emergency shutdown


@dataclass
class ThermalThresholds:
    """Temperature thresholds in Celsius."""
    cool_max: float = 45.0
    warm_max: float = 55.0
    hot_max: float = 70.0
    critical_max: float = 85.0
    emergency_shutdown: float = 95.0

    def get_zone(self, temperature: float) -> ThermalZone:
        """Determine thermal zone from temperature."""
        if temperature < self.cool_max:
            return ThermalZone.COOL
        elif temperature < self.warm_max:
            return ThermalZone.WARM
        elif temperature < self.hot_max:
            return ThermalZone.HOT
        elif temperature < self.critical_max:
            return ThermalZone.CRITICAL
        else:
            return ThermalZone.EMERGENCY


@dataclass
class ThermalState:
    """Current thermal state."""
    temperature: float = 25.0
    zone: ThermalZone = ThermalZone.COOL
    throttle_factor: float = 1.0
    timestamp: float = field(default_factory=time.time)

    @property
    def is_throttled(self) -> bool:
        return self.throttle_factor < 1.0

    @property
    def performance_percent(self) -> float:
        return self.throttle_factor * 100


@dataclass
class ThermalEvent:
    """Record of a thermal event."""
    timestamp: float
    temperature: float
    zone: ThermalZone
    throttle_factor: float
    action: str


class ThermalManager:
    """
    Manages thermal constraints with PHI-based throttling.

    PHI-based throttling provides smooth, harmonious performance scaling:
    - Each zone reduces performance by PHI_INVERSE (0.618)
    - This creates natural stepping that avoids jarring transitions
    - The throttle curve follows the golden ratio decay
    """

    def __init__(
        self,
        thresholds: Optional[ThermalThresholds] = None,
        on_throttle: Optional[Callable[[ThermalState], None]] = None,
        on_emergency: Optional[Callable[[ThermalState], None]] = None
    ):
        self._thresholds = thresholds or ThermalThresholds()
        self._state = ThermalState()
        self._history: List[ThermalEvent] = []
        self._on_throttle = on_throttle
        self._on_emergency = on_emergency
        self._emergency_active = False

        # PHI-based throttle factors for each zone
        self._throttle_factors = self._compute_phi_throttle_curve()

    def _compute_phi_throttle_curve(self) -> Dict[ThermalZone, float]:
        """
        Compute PHI-based throttle factors for each zone.

        Uses PHI_INVERSE^n for each zone level:
        - COOL: 1.0 (full performance)
        - WARM: 0.618 (PHI^-1)
        - HOT: 0.382 (PHI^-2)
        - CRITICAL: 0.236 (PHI^-3)
        - EMERGENCY: 0.0 (shutdown)
        """
        return {
            ThermalZone.COOL: 1.0,
            ThermalZone.WARM: PHI_INVERSE,  # ~0.618
            ThermalZone.HOT: PHI_INVERSE ** 2,  # ~0.382
            ThermalZone.CRITICAL: PHI_INVERSE ** 3,  # ~0.236
            ThermalZone.EMERGENCY: 0.0,  # Full shutdown
        }

    @property
    def state(self) -> ThermalState:
        """Get current thermal state."""
        return self._state

    @property
    def thresholds(self) -> ThermalThresholds:
        """Get thermal thresholds."""
        return self._thresholds

    @property
    def is_emergency(self) -> bool:
        """Check if in emergency state."""
        return self._emergency_active

    def update(self, temperature: float) -> ThermalState:
        """
        Update thermal state with new temperature reading.

        Args:
            temperature: Current temperature in Celsius

        Returns:
            Updated ThermalState
        """
        old_zone = self._state.zone
        new_zone = self._thresholds.get_zone(temperature)
        throttle = self._throttle_factors[new_zone]

        # Update state
        self._state = ThermalState(
            temperature=temperature,
            zone=new_zone,
            throttle_factor=throttle
        )

        # Record event on zone change
        if new_zone != old_zone:
            action = self._determine_action(old_zone, new_zone)
            self._record_event(temperature, new_zone, throttle, action)

            # Trigger callbacks
            if new_zone == ThermalZone.EMERGENCY:
                self._emergency_active = True
                if self._on_emergency:
                    self._on_emergency(self._state)
            elif self._state.is_throttled and self._on_throttle:
                self._on_throttle(self._state)

        # Clear emergency on cooldown
        if self._emergency_active and new_zone.value < ThermalZone.CRITICAL.value:
            self._emergency_active = False

        return self._state

    def _determine_action(self, old_zone: ThermalZone, new_zone: ThermalZone) -> str:
        """Determine action based on zone transition."""
        if new_zone.value > old_zone.value:
            if new_zone == ThermalZone.EMERGENCY:
                return "EMERGENCY_SHUTDOWN"
            return "THROTTLE_INCREASE"
        else:
            return "THROTTLE_DECREASE"

    def _record_event(
        self,
        temperature: float,
        zone: ThermalZone,
        throttle: float,
        action: str
    ) -> None:
        """Record thermal event."""
        event = ThermalEvent(
            timestamp=time.time(),
            temperature=temperature,
            zone=zone,
            throttle_factor=throttle,
            action=action
        )
        self._history.append(event)

    def get_throttle_factor(self) -> float:
        """Get current throttle factor (0.0 to 1.0)."""
        return self._state.throttle_factor

    def get_allowed_intensity(self, max_intensity: float) -> float:
        """
        Calculate allowed intensity based on thermal constraints.

        Args:
            max_intensity: Maximum desired intensity

        Returns:
            Thermally-constrained intensity
        """
        return max_intensity * self._state.throttle_factor

    def get_phi_gradient(self, base_value: float) -> List[float]:
        """
        Generate PHI-gradient values for progressive throttling.

        Args:
            base_value: Starting value

        Returns:
            List of PHI-scaled values
        """
        return [base_value * (PHI_INVERSE ** i) for i in range(5)]

    def predict_temperature(
        self,
        current: float,
        power_watts: float,
        ambient: float = 25.0,
        thermal_resistance: float = 0.5
    ) -> float:
        """
        Predict steady-state temperature using thermal model.

        Simple thermal model: T = T_ambient + (P * R_thermal)

        Args:
            current: Current temperature
            power_watts: Power dissipation in watts
            ambient: Ambient temperature
            thermal_resistance: Thermal resistance (C/W)

        Returns:
            Predicted steady-state temperature
        """
        steady_state = ambient + (power_watts * thermal_resistance)
        # Exponential approach to steady state (simplified)
        alpha = 0.1  # Time constant factor
        return current + alpha * (steady_state - current)

    def recommend_power_limit(
        self,
        target_temp: float,
        ambient: float = 25.0,
        thermal_resistance: float = 0.5
    ) -> float:
        """
        Recommend power limit to achieve target temperature.

        Args:
            target_temp: Target temperature in Celsius
            ambient: Ambient temperature
            thermal_resistance: Thermal resistance (C/W)

        Returns:
            Recommended power limit in watts
        """
        if thermal_resistance <= 0:
            return float('inf')
        return (target_temp - ambient) / thermal_resistance

    def get_lucas_power_levels(self, base_watts: float) -> List[Tuple[int, float]]:
        """
        Get power levels scaled by Lucas numbers.

        Args:
            base_watts: Base power unit

        Returns:
            List of (lucas_number, power_watts) tuples
        """
        return [(L, L * base_watts) for L in LUCAS]

    def simulate_thermal_response(
        self,
        initial_temp: float,
        power_sequence: List[float],
        ambient: float = 25.0
    ) -> List[ThermalState]:
        """
        Simulate thermal response to a power sequence.

        Args:
            initial_temp: Starting temperature
            power_sequence: List of power values over time
            ambient: Ambient temperature

        Returns:
            List of thermal states over time
        """
        states = []
        temp = initial_temp

        for power in power_sequence:
            temp = self.predict_temperature(temp, power, ambient)
            state = self.update(temp)
            states.append(ThermalState(
                temperature=state.temperature,
                zone=state.zone,
                throttle_factor=state.throttle_factor,
                timestamp=time.time()
            ))

        return states

    def get_history(self) -> List[ThermalEvent]:
        """Get thermal event history."""
        return self._history.copy()

    def reset(self) -> None:
        """Reset thermal manager state."""
        self._state = ThermalState()
        self._history.clear()
        self._emergency_active = False

    def summary(self) -> Dict:
        """Get thermal manager summary."""
        return {
            "current_temperature": self._state.temperature,
            "zone": self._state.zone.name,
            "throttle_factor": round(self._state.throttle_factor, 3),
            "performance_percent": round(self._state.performance_percent, 1),
            "is_throttled": self._state.is_throttled,
            "is_emergency": self._emergency_active,
            "event_count": len(self._history),
            "phi_throttle_curve": {
                z.name: round(f, 3) for z, f in self._throttle_factors.items()
            },
        }


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Edge Thermal Manager - Test Suite")
    print("=" * 60)

    # Initialize manager with callbacks
    def on_throttle(state: ThermalState):
        print(f"  [CALLBACK] Throttle activated: {state.performance_percent:.1f}%")

    def on_emergency(state: ThermalState):
        print(f"  [CALLBACK] EMERGENCY at {state.temperature}C!")

    manager = ThermalManager(on_throttle=on_throttle, on_emergency=on_emergency)

    print(f"\nPHI constant: {PHI}")
    print(f"PHI inverse: {PHI_INVERSE}")

    # Show PHI throttle curve
    print("\n--- PHI-based Throttle Curve ---")
    for zone, factor in manager._throttle_factors.items():
        bars = int(factor * 20)
        bar_str = "#" * bars + "-" * (20 - bars)
        print(f"  {zone.name:10} [{bar_str}] {factor:.3f} ({factor*100:.1f}%)")

    # Show thresholds
    print("\n--- Thermal Thresholds ---")
    t = manager.thresholds
    print(f"  COOL:     < {t.cool_max}C")
    print(f"  WARM:     {t.cool_max}C - {t.warm_max}C")
    print(f"  HOT:      {t.warm_max}C - {t.hot_max}C")
    print(f"  CRITICAL: {t.hot_max}C - {t.critical_max}C")
    print(f"  EMERGENCY: > {t.critical_max}C")

    # Simulate temperature ramp
    print("\n--- Temperature Ramp Simulation ---")
    temps = [30, 40, 48, 58, 72, 88, 75, 60, 45, 35]

    for temp in temps:
        state = manager.update(temp)
        print(f"  {temp:3.0f}C -> Zone: {state.zone.name:10} | "
              f"Throttle: {state.throttle_factor:.3f} | "
              f"Perf: {state.performance_percent:5.1f}%")

    # Test intensity calculation
    print("\n--- Intensity Calculation Test ---")
    max_intensity = 100.0
    for zone in ThermalZone:
        manager._state.zone = zone
        manager._state.throttle_factor = manager._throttle_factors[zone]
        allowed = manager.get_allowed_intensity(max_intensity)
        print(f"  {zone.name:10}: Max={max_intensity:.0f} -> Allowed={allowed:.1f}")

    # Test PHI gradient
    print("\n--- PHI Gradient Test ---")
    base = 100.0
    gradient = manager.get_phi_gradient(base)
    print(f"  Base value: {base}")
    print(f"  PHI gradient: {[round(g, 2) for g in gradient]}")

    # Test power recommendation
    print("\n--- Power Limit Recommendations ---")
    targets = [45, 55, 70, 85]
    for target in targets:
        limit = manager.recommend_power_limit(target)
        print(f"  Target {target}C: Max power = {limit:.1f}W")

    # Test Lucas power levels
    print("\n--- Lucas Power Levels ---")
    base_watts = 0.1
    levels = manager.get_lucas_power_levels(base_watts)
    for lucas, watts in levels[:6]:
        print(f"  L={lucas:3} -> {watts:.1f}W")

    # Show event history
    print("\n--- Event History ---")
    for event in manager.get_history()[-5:]:
        print(f"  {event.action}: {event.temperature:.0f}C -> {event.zone.name}")

    # Final summary
    print("\n--- Final Summary ---")
    summary = manager.summary()
    for key, value in summary.items():
        if key != "phi_throttle_curve":
            print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Thermal Manager tests completed successfully!")
    print("=" * 60)
