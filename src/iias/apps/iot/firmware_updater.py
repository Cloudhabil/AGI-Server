"""
Firmware Updater Module

Genesis-versioned rollout system using GENESIS_CONSTANT (2/901).
Implements phased firmware deployment with Genesis-based version control.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set
import hashlib
import math

# Constants
PHI = 1.618033988749895
GENESIS_CONSTANT = 2 / 901  # ~0.00221975...
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
TOTAL_STATES = 840


class RolloutPhase(Enum):
    """Firmware rollout phases based on Genesis progression."""
    GENESIS = 0      # Initial creation (0.22% of devices)
    ALPHA = 1        # Early adopters
    BETA = 2         # Expanded testing
    GAMMA = 3        # Pre-release
    DELTA = 4        # Staged release
    EPSILON = 5      # Wide release
    ZETA = 6         # Near-complete
    ETA = 7          # Full deployment
    THETA = 8        # Verification phase
    COMPLETE = 9     # 100% deployment


@dataclass
class FirmwareVersion:
    """Firmware version with Genesis-based versioning."""
    major: int
    minor: int
    patch: int
    genesis_sequence: int  # Genesis constant multiplier
    build_hash: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def version_string(self) -> str:
        """Generate version string with Genesis sequence."""
        genesis_tag = f"G{self.genesis_sequence}"
        return f"{self.major}.{self.minor}.{self.patch}-{genesis_tag}"

    @property
    def genesis_factor(self) -> float:
        """Compute Genesis factor for this version."""
        return GENESIS_CONSTANT * self.genesis_sequence


@dataclass
class RolloutState:
    """State of a firmware rollout."""
    firmware: FirmwareVersion
    phase: RolloutPhase
    target_percentage: float
    current_percentage: float
    devices_updated: Set[str] = field(default_factory=set)
    devices_pending: Set[str] = field(default_factory=set)
    devices_failed: Set[str] = field(default_factory=set)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class FirmwareUpdater:
    """
    Genesis-versioned firmware rollout manager.

    Uses GENESIS_CONSTANT (2/901) to determine rollout percentages
    and phase transitions. Each phase increases coverage by a
    Genesis-scaled factor.
    """

    def __init__(self, device_registry: Optional[Dict[str, dict]] = None):
        """
        Initialize firmware updater.

        Args:
            device_registry: Optional dict of device_id -> device_info
        """
        self.device_registry = device_registry or {}
        self.firmware_catalog: Dict[str, FirmwareVersion] = {}
        self.active_rollouts: Dict[str, RolloutState] = {}
        self.rollout_history: List[RolloutState] = []
        self.genesis_sequence_counter = 1

    def _compute_phase_percentages(self) -> Dict[RolloutPhase, float]:
        """
        Compute target percentages for each rollout phase.

        Uses Genesis constant scaled by Lucas numbers for natural progression.
        """
        percentages = {}
        cumulative = 0.0

        for i, phase in enumerate(RolloutPhase):
            if phase == RolloutPhase.COMPLETE:
                percentages[phase] = 100.0
            else:
                # Use Lucas number at index i, scaled by Genesis constant
                lucas_factor = LUCAS[i % len(LUCAS)]
                increment = GENESIS_CONSTANT * lucas_factor * 100
                cumulative = min(cumulative + increment, 100.0)
                percentages[phase] = cumulative

        return percentages

    def _generate_build_hash(self, version: FirmwareVersion) -> str:
        """Generate a unique build hash for firmware version."""
        content = f"{version.major}.{version.minor}.{version.patch}-{version.genesis_sequence}"
        content += f"-{version.created_at.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def create_firmware(
        self,
        major: int,
        minor: int,
        patch: int
    ) -> FirmwareVersion:
        """
        Create a new firmware version with Genesis sequencing.

        Args:
            major: Major version number
            minor: Minor version number
            patch: Patch version number

        Returns:
            New FirmwareVersion instance
        """
        version = FirmwareVersion(
            major=major,
            minor=minor,
            patch=patch,
            genesis_sequence=self.genesis_sequence_counter
        )
        version.build_hash = self._generate_build_hash(version)

        # Increment Genesis sequence for next version
        self.genesis_sequence_counter += 1

        # Store in catalog
        self.firmware_catalog[version.version_string] = version

        return version

    def start_rollout(
        self,
        firmware: FirmwareVersion,
        device_ids: Optional[List[str]] = None
    ) -> RolloutState:
        """
        Start a new firmware rollout.

        Args:
            firmware: Firmware version to deploy
            device_ids: List of target device IDs (or all registered if None)

        Returns:
            RolloutState tracking the deployment
        """
        if device_ids is None:
            device_ids = list(self.device_registry.keys())

        phase_percentages = self._compute_phase_percentages()

        state = RolloutState(
            firmware=firmware,
            phase=RolloutPhase.GENESIS,
            target_percentage=phase_percentages[RolloutPhase.GENESIS],
            current_percentage=0.0,
            devices_pending=set(device_ids),
            started_at=datetime.now()
        )

        self.active_rollouts[firmware.version_string] = state
        return state

    def advance_phase(self, version_string: str) -> Optional[RolloutState]:
        """
        Advance rollout to next phase.

        Args:
            version_string: Firmware version string

        Returns:
            Updated RolloutState or None if not found
        """
        state = self.active_rollouts.get(version_string)
        if not state:
            return None

        phase_percentages = self._compute_phase_percentages()

        # Move to next phase
        current_index = state.phase.value
        if current_index < len(RolloutPhase) - 1:
            next_phase = RolloutPhase(current_index + 1)
            state.phase = next_phase
            state.target_percentage = phase_percentages[next_phase]

            if next_phase == RolloutPhase.COMPLETE:
                state.completed_at = datetime.now()
                self.rollout_history.append(state)

        return state

    def update_device(
        self,
        version_string: str,
        device_id: str,
        success: bool = True
    ) -> bool:
        """
        Record a device update result.

        Args:
            version_string: Firmware version string
            device_id: Device that was updated
            success: Whether update succeeded

        Returns:
            True if recorded successfully
        """
        state = self.active_rollouts.get(version_string)
        if not state:
            return False

        if device_id in state.devices_pending:
            state.devices_pending.remove(device_id)

            if success:
                state.devices_updated.add(device_id)
            else:
                state.devices_failed.add(device_id)

            # Update percentage
            total_devices = (
                len(state.devices_updated) +
                len(state.devices_pending) +
                len(state.devices_failed)
            )
            if total_devices > 0:
                state.current_percentage = (
                    len(state.devices_updated) / total_devices * 100
                )

            return True

        return False

    def get_rollout_status(self, version_string: str) -> Optional[Dict]:
        """Get detailed status of a rollout."""
        state = self.active_rollouts.get(version_string)
        if not state:
            return None

        return {
            "version": version_string,
            "phase": state.phase.name,
            "target_percentage": state.target_percentage,
            "current_percentage": state.current_percentage,
            "devices_updated": len(state.devices_updated),
            "devices_pending": len(state.devices_pending),
            "devices_failed": len(state.devices_failed),
            "genesis_factor": state.firmware.genesis_factor,
            "started_at": state.started_at.isoformat() if state.started_at else None,
            "completed_at": state.completed_at.isoformat() if state.completed_at else None,
        }

    def get_genesis_schedule(self) -> List[Dict]:
        """Get the Genesis-based rollout schedule."""
        percentages = self._compute_phase_percentages()
        schedule = []

        for phase in RolloutPhase:
            lucas_idx = phase.value % len(LUCAS)
            schedule.append({
                "phase": phase.name,
                "target_percentage": round(percentages[phase], 4),
                "lucas_factor": LUCAS[lucas_idx],
                "genesis_increment": round(GENESIS_CONSTANT * LUCAS[lucas_idx] * 100, 4)
            })

        return schedule


if __name__ == "__main__":
    print("=" * 60)
    print("Firmware Updater Test - Genesis-Versioned Rollout")
    print("=" * 60)

    # Initialize updater with mock device registry
    devices = {f"device-{i:03d}": {"type": "sensor"} for i in range(100)}
    updater = FirmwareUpdater(device_registry=devices)

    print(f"\nGENESIS_CONSTANT: {GENESIS_CONSTANT:.10f}")
    print(f"Registered Devices: {len(devices)}")

    # Display Genesis rollout schedule
    print("\nGenesis Rollout Schedule:")
    print("-" * 60)
    print(f"{'Phase':<12} {'Target %':>12} {'Lucas':>8} {'Increment':>12}")
    print("-" * 60)

    for phase_info in updater.get_genesis_schedule():
        print(
            f"{phase_info['phase']:<12} "
            f"{phase_info['target_percentage']:>12.4f} "
            f"{phase_info['lucas_factor']:>8} "
            f"{phase_info['genesis_increment']:>12.4f}"
        )

    # Create firmware versions
    print("\nCreating Firmware Versions:")
    print("-" * 40)

    fw1 = updater.create_firmware(1, 0, 0)
    fw2 = updater.create_firmware(1, 0, 1)
    fw3 = updater.create_firmware(1, 1, 0)

    for fw in [fw1, fw2, fw3]:
        print(f"  {fw.version_string} (hash: {fw.build_hash})")
        print(f"    Genesis Factor: {fw.genesis_factor:.10f}")

    # Start and simulate rollout
    print("\nStarting Rollout for", fw1.version_string)
    print("-" * 40)

    rollout = updater.start_rollout(fw1)

    # Simulate updating devices through phases
    device_list = list(devices.keys())
    devices_per_phase = len(device_list) // 10

    for i, phase in enumerate(RolloutPhase):
        if phase == RolloutPhase.COMPLETE:
            break

        # Update some devices
        start_idx = i * devices_per_phase
        end_idx = min(start_idx + devices_per_phase, len(device_list))

        for device_id in device_list[start_idx:end_idx]:
            updater.update_device(fw1.version_string, device_id, success=True)

        status = updater.get_rollout_status(fw1.version_string)
        print(f"\nPhase {status['phase']}:")
        print(f"  Target: {status['target_percentage']:.2f}%")
        print(f"  Current: {status['current_percentage']:.2f}%")
        print(f"  Updated: {status['devices_updated']}")

        updater.advance_phase(fw1.version_string)

    # Final status
    final_status = updater.get_rollout_status(fw1.version_string)
    print("\n" + "=" * 60)
    print("Final Rollout Status")
    print("-" * 40)
    for key, value in final_status.items():
        print(f"  {key}: {value}")

    print("=" * 60)
    print("\nTest completed successfully!")
