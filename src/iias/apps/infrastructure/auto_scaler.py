"""Auto Scaler - PHI-based scaling threshold"""

import math

PHI = 1.618033988749895
THETA_UP = 1 - 1/math.e      # 0.632
THETA_DOWN = THETA_UP / PHI  # 0.391


class AutoScaler:
    """Scale at 63.2% utilization, scale down at 39.1%."""

    def __init__(self, theta_up: float = THETA_UP, theta_down: float = THETA_DOWN):
        self.theta_up = theta_up
        self.theta_down = theta_down

    def should_scale(self, current_load: float, capacity: float) -> str:
        if capacity <= 0:
            return "STABLE"
        utilization = current_load / capacity
        if utilization > self.theta_up:
            return "SCALE_UP"
        elif utilization < self.theta_down:
            return "SCALE_DOWN"
        return "STABLE"

    def optimal_capacity(self, expected_load: float) -> float:
        """Calculate optimal capacity for expected load."""
        return expected_load / self.theta_up


if __name__ == "__main__":
    scaler = AutoScaler()
    print(f"THETA_UP: {THETA_UP:.3f}")
    print(f"THETA_DOWN: {THETA_DOWN:.3f}")
    print(f"Load 70/100: {scaler.should_scale(70, 100)}")
    print(f"Load 30/100: {scaler.should_scale(30, 100)}")
    print(f"Load 50/100: {scaler.should_scale(50, 100)}")
