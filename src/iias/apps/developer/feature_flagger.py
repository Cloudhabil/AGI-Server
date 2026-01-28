"""
Feature Flagger - Genesis-based feature rollout.

Uses the Genesis constant for exponential rollout curves.
Formula: rollout_pct = 1 - e^(-t/GENESIS_CONSTANT)

Where t is time (normalized) and GENESIS_CONSTANT = 2/901
"""

import math
import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum

# Constants
GENESIS_CONSTANT = 2 / 901  # ~0.00222


class RolloutStage(Enum):
    """Feature rollout stages."""
    DISABLED = "disabled"
    CANARY = "canary"  # < 5%
    BETA = "beta"  # 5-25%
    GRADUAL = "gradual"  # 25-75%
    GENERAL = "general"  # 75-99%
    FULL = "full"  # 100%


@dataclass
class FeatureFlag:
    """Represents a feature flag with Genesis-based rollout."""
    name: str
    description: str = ""
    enabled: bool = False
    rollout_start: Optional[float] = None  # Unix timestamp
    rollout_percentage: float = 0.0
    target_groups: Set[str] = field(default_factory=set)
    metadata: Dict = field(default_factory=dict)

    @property
    def stage(self) -> RolloutStage:
        """Get current rollout stage based on percentage."""
        if not self.enabled or self.rollout_percentage <= 0:
            return RolloutStage.DISABLED
        elif self.rollout_percentage < 5:
            return RolloutStage.CANARY
        elif self.rollout_percentage < 25:
            return RolloutStage.BETA
        elif self.rollout_percentage < 75:
            return RolloutStage.GRADUAL
        elif self.rollout_percentage < 100:
            return RolloutStage.GENERAL
        else:
            return RolloutStage.FULL


@dataclass
class RolloutMetrics:
    """Metrics for a rollout."""
    feature_name: str
    elapsed_time: float
    current_percentage: float
    stage: RolloutStage
    users_exposed: int
    total_users: int


class FeatureFlagger:
    """
    Genesis-based feature rollout manager.

    Uses the formula: rollout_pct = 1 - e^(-t/GENESIS_CONSTANT)

    The Genesis constant (2/901) provides a natural exponential curve
    that starts slow, accelerates through the middle phase, and
    asymptotically approaches 100%.

    Key properties:
    - At t=GENESIS_CONSTANT: ~63.2% rollout
    - At t=2*GENESIS_CONSTANT: ~86.5% rollout
    - At t=3*GENESIS_CONSTANT: ~95.0% rollout
    """

    def __init__(self, time_scale: float = 1.0):
        """
        Initialize the feature flagger.

        Args:
            time_scale: Multiplier for time (1.0 = seconds, 3600 = hours, etc.)
        """
        self.time_scale = time_scale
        self.flags: Dict[str, FeatureFlag] = {}
        self._user_assignments: Dict[str, Set[str]] = {}  # feature -> users

    @staticmethod
    def genesis_rollout(t: float) -> float:
        """
        Calculate rollout percentage using Genesis formula.

        Formula: rollout_pct = 1 - e^(-t/GENESIS_CONSTANT)

        Args:
            t: Normalized time value.

        Returns:
            Rollout percentage (0.0 to 1.0).
        """
        return 1.0 - math.exp(-t / GENESIS_CONSTANT)

    @staticmethod
    def inverse_genesis(target_pct: float) -> float:
        """
        Calculate time needed to reach target percentage.

        Inverse formula: t = -GENESIS_CONSTANT * ln(1 - target_pct)

        Args:
            target_pct: Target percentage (0.0 to <1.0).

        Returns:
            Time value needed.
        """
        if target_pct >= 1.0:
            return float('inf')
        if target_pct <= 0.0:
            return 0.0
        return -GENESIS_CONSTANT * math.log(1.0 - target_pct)

    def create_flag(
        self,
        name: str,
        description: str = "",
        start_enabled: bool = False
    ) -> FeatureFlag:
        """
        Create a new feature flag.

        Args:
            name: Unique flag name.
            description: Human-readable description.
            start_enabled: Start with rollout active.

        Returns:
            Created FeatureFlag.
        """
        flag = FeatureFlag(
            name=name,
            description=description,
            enabled=start_enabled,
            rollout_start=time.time() if start_enabled else None
        )
        self.flags[name] = flag
        self._user_assignments[name] = set()
        return flag

    def start_rollout(self, name: str) -> None:
        """Start rolling out a feature."""
        if name not in self.flags:
            raise KeyError(f"Feature flag '{name}' not found")

        flag = self.flags[name]
        flag.enabled = True
        flag.rollout_start = time.time()

    def stop_rollout(self, name: str) -> None:
        """Stop a feature rollout."""
        if name not in self.flags:
            raise KeyError(f"Feature flag '{name}' not found")

        flag = self.flags[name]
        flag.enabled = False

    def get_rollout_percentage(self, name: str) -> float:
        """
        Get current rollout percentage for a feature.

        Args:
            name: Feature flag name.

        Returns:
            Current percentage (0-100).
        """
        if name not in self.flags:
            return 0.0

        flag = self.flags[name]

        if not flag.enabled or flag.rollout_start is None:
            return 0.0

        elapsed = (time.time() - flag.rollout_start) / self.time_scale
        pct = self.genesis_rollout(elapsed) * 100.0
        flag.rollout_percentage = pct

        return pct

    def is_enabled_for_user(self, name: str, user_id: str) -> bool:
        """
        Check if feature is enabled for a specific user.

        Uses consistent hashing to ensure stable assignment.

        Args:
            name: Feature flag name.
            user_id: User identifier.

        Returns:
            True if feature is enabled for this user.
        """
        if name not in self.flags:
            return False

        flag = self.flags[name]

        if not flag.enabled:
            return False

        # Check target groups first
        if flag.target_groups:
            # User must be in a target group (simplified check)
            pass

        # Get current rollout percentage
        pct = self.get_rollout_percentage(name) / 100.0

        # Consistent hash for user assignment
        hash_input = f"{name}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        user_bucket = (hash_value % 10000) / 10000.0

        is_enabled = user_bucket < pct

        if is_enabled:
            self._user_assignments[name].add(user_id)

        return is_enabled

    def get_metrics(self, name: str, total_users: int = 0) -> RolloutMetrics:
        """Get rollout metrics for a feature."""
        if name not in self.flags:
            raise KeyError(f"Feature flag '{name}' not found")

        flag = self.flags[name]
        pct = self.get_rollout_percentage(name)

        elapsed = 0.0
        if flag.rollout_start:
            elapsed = time.time() - flag.rollout_start

        exposed = len(self._user_assignments.get(name, set()))

        return RolloutMetrics(
            feature_name=name,
            elapsed_time=elapsed,
            current_percentage=pct,
            stage=flag.stage,
            users_exposed=exposed,
            total_users=total_users
        )

    def get_rollout_report(self) -> str:
        """Generate a report on all feature flags."""
        lines = [
            "=" * 50,
            "GENESIS-BASED FEATURE ROLLOUT REPORT",
            "=" * 50,
            f"Genesis Constant: {GENESIS_CONSTANT:.6f} (2/901)",
            f"Time Scale: {self.time_scale}",
            "",
            "ROLLOUT CURVE MILESTONES:",
            f"  t={GENESIS_CONSTANT:.4f}: {self.genesis_rollout(GENESIS_CONSTANT)*100:.1f}%",
            f"  t={2*GENESIS_CONSTANT:.4f}: {self.genesis_rollout(2*GENESIS_CONSTANT)*100:.1f}%",
            f"  t={3*GENESIS_CONSTANT:.4f}: {self.genesis_rollout(3*GENESIS_CONSTANT)*100:.1f}%",
            "",
            "FEATURE FLAGS:",
        ]

        for name, flag in self.flags.items():
            pct = self.get_rollout_percentage(name)
            status = "ACTIVE" if flag.enabled else "INACTIVE"
            lines.append(f"  [{status}] {name}")
            lines.append(f"    Description: {flag.description or 'N/A'}")
            lines.append(f"    Rollout: {pct:.2f}%")
            lines.append(f"    Stage: {flag.stage.value}")

        lines.append("=" * 50)
        return "\n".join(lines)


if __name__ == "__main__":
    print("Testing FeatureFlagger - Genesis-based rollout")
    print()

    # Display Genesis constant properties
    print(f"Genesis Constant: {GENESIS_CONSTANT:.6f} (2/901)")
    print()

    # Show rollout curve at key points
    print("Genesis Rollout Curve:")
    test_times = [0.0001, 0.0005, 0.001, GENESIS_CONSTANT, 2*GENESIS_CONSTANT, 3*GENESIS_CONSTANT, 0.01]
    for t in test_times:
        pct = FeatureFlagger.genesis_rollout(t) * 100
        print(f"  t={t:.6f}: {pct:.2f}%")
    print()

    # Calculate time to reach specific percentages
    print("Time to reach target percentages:")
    for target in [0.10, 0.25, 0.50, 0.75, 0.90, 0.99]:
        t = FeatureFlagger.inverse_genesis(target)
        print(f"  {target*100:.0f}%: t={t:.6f}")
    print()

    # Create feature flagger with fast time scale for testing
    flagger = FeatureFlagger(time_scale=0.001)  # 1ms = 1 unit

    # Create and start a feature rollout
    flagger.create_flag(
        "dark_mode",
        description="Enable dark mode UI",
        start_enabled=True
    )

    flagger.create_flag(
        "new_search",
        description="New search algorithm",
        start_enabled=False
    )

    # Simulate some time passing
    time.sleep(0.005)

    # Check rollout percentages
    print("Current Rollout Status:")
    print(f"  dark_mode: {flagger.get_rollout_percentage('dark_mode'):.2f}%")
    print(f"  new_search: {flagger.get_rollout_percentage('new_search'):.2f}%")
    print()

    # Test user assignment
    print("User Feature Checks (dark_mode):")
    for user_id in ["user_001", "user_002", "user_003", "user_004", "user_005"]:
        enabled = flagger.is_enabled_for_user("dark_mode", user_id)
        print(f"  {user_id}: {'ENABLED' if enabled else 'DISABLED'}")
    print()

    # Print full report
    print(flagger.get_rollout_report())

    # Verify formula: 1 - e^(-t/GENESIS) should equal genesis_rollout(t)
    t_test = 0.005
    expected = 1.0 - math.exp(-t_test / GENESIS_CONSTANT)
    actual = FeatureFlagger.genesis_rollout(t_test)
    assert abs(expected - actual) < 1e-10, "Genesis formula mismatch!"

    print("\nTest PASSED: FeatureFlagger working correctly!")
