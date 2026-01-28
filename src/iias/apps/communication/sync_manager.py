"""
Sync Manager - Mirror-paired State Synchronization

Implements state synchronization where local_state + remote_state = 214
(SUM_CONSTANT). This creates a mirror-pair relationship ensuring that
state changes are always balanced across the distributed system.

Key Properties:
- Any state value S has a mirror value of (214 - S)
- PHI-weighted averaging for conflict resolution
- Lucas sequence checkpoints for sync verification
- Automatic state normalization to maintain the sum invariant
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum, auto
import time
import hashlib
import json

PHI = 1.618033988749895
SUM_CONSTANT = 214
D5_CAPACITY = 11
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]


class SyncStatus(Enum):
    """Synchronization status states."""
    SYNCED = auto()        # local + remote = 214
    PENDING = auto()       # Sync in progress
    CONFLICT = auto()      # Requires resolution
    DIVERGED = auto()      # States have diverged
    ERROR = auto()         # Sync error


@dataclass
class StateVector:
    """A normalized state vector for synchronization."""
    values: Dict[str, float]
    timestamp: float = field(default_factory=time.time)
    version: int = 0
    checksum: str = field(default="")

    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._compute_checksum()

    def _compute_checksum(self) -> str:
        """Compute state checksum for verification."""
        content = json.dumps(self.values, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @property
    def total(self) -> float:
        """Sum of all state values."""
        return sum(self.values.values())

    def get(self, key: str, default: float = 0.0) -> float:
        """Get state value by key."""
        return self.values.get(key, default)

    def set(self, key: str, value: float):
        """Set state value and update checksum."""
        self.values[key] = value
        self.version += 1
        self.timestamp = time.time()
        self.checksum = self._compute_checksum()

    def normalize(self, target: float = SUM_CONSTANT) -> 'StateVector':
        """Normalize values to sum to target."""
        total = self.total
        if total == 0:
            factor = 0
        else:
            factor = target / total

        normalized = {k: v * factor for k, v in self.values.items()}
        return StateVector(
            values=normalized,
            timestamp=time.time(),
            version=self.version + 1
        )


@dataclass
class SyncEvent:
    """Record of a synchronization event."""
    event_type: str
    local_state: StateVector
    remote_state: StateVector
    result_state: Optional[StateVector]
    status: SyncStatus
    timestamp: float = field(default_factory=time.time)
    details: str = ""


class SyncManager:
    """
    Mirror-paired State Synchronization Manager.

    Ensures that local_state + remote_state = 214 (SUM_CONSTANT)
    at all times. Uses PHI-weighted conflict resolution and
    Lucas sequence checkpoints for verification.
    """

    def __init__(self):
        self.local_state = StateVector(values={})
        self.remote_state = StateVector(values={})
        self.sync_history: List[SyncEvent] = []
        self.conflict_handlers: Dict[str, Callable] = {}
        self._lucas_checkpoints = set(LUCAS)

    def _compute_mirror(self, state: StateVector) -> StateVector:
        """Compute mirror state such that state + mirror = SUM_CONSTANT."""
        mirror_values = {}
        for key, value in state.values.items():
            mirror_values[key] = SUM_CONSTANT - value

        # For keys only in one state, mirror is SUM_CONSTANT - 0 = SUM_CONSTANT
        # But we normalize the total, not individual values

        return StateVector(
            values=mirror_values,
            timestamp=time.time(),
            version=state.version
        )

    def _verify_sum_invariant(self, local: StateVector,
                               remote: StateVector) -> bool:
        """Verify that local + remote = SUM_CONSTANT for each key."""
        all_keys = set(local.values.keys()) | set(remote.values.keys())

        for key in all_keys:
            local_val = local.get(key, 0)
            remote_val = remote.get(key, 0)
            if abs((local_val + remote_val) - SUM_CONSTANT) > 0.001:
                return False

        return True

    def _phi_weighted_merge(self, local_val: float, remote_val: float,
                            local_newer: bool = True) -> Tuple[float, float]:
        """
        PHI-weighted merge for conflict resolution.

        The newer state gets PHI weight, older gets 1/PHI weight.
        Result is normalized to sum to SUM_CONSTANT.
        """
        if local_newer:
            local_weight = PHI
            remote_weight = 1 / PHI
        else:
            local_weight = 1 / PHI
            remote_weight = PHI

        total_weight = local_weight + remote_weight

        # Weighted average
        merged = (local_val * local_weight + remote_val * remote_weight) / total_weight

        # Mirror value
        mirror = SUM_CONSTANT - merged

        return merged, mirror

    def _lucas_checkpoint(self, version: int) -> bool:
        """Check if version is a Lucas checkpoint."""
        return version in self._lucas_checkpoints or version % 322 == 0

    def initialize_state(self, keys: List[str],
                         local_ratio: float = 0.5) -> SyncStatus:
        """
        Initialize local and remote states with given keys.

        For each key: local_value + remote_value = SUM_CONSTANT (214)
        The local_ratio determines what fraction of 214 goes to local.

        Args:
            keys: State keys to initialize
            local_ratio: Local state ratio of SUM_CONSTANT per key (0-1)

        Returns:
            SyncStatus after initialization
        """
        local_ratio = max(0, min(1, local_ratio))

        local_values = {}
        remote_values = {}

        # Each key independently sums to SUM_CONSTANT
        for key in keys:
            local_values[key] = SUM_CONSTANT * local_ratio
            remote_values[key] = SUM_CONSTANT * (1 - local_ratio)

        self.local_state = StateVector(values=local_values)
        self.remote_state = StateVector(values=remote_values)

        # Verify invariant
        if self._verify_sum_invariant(self.local_state, self.remote_state):
            status = SyncStatus.SYNCED
        else:
            status = SyncStatus.ERROR

        self._record_event("initialize", status)
        return status

    def update_local(self, key: str, value: float) -> SyncStatus:
        """
        Update local state and automatically adjust remote mirror.

        The remote value for this key becomes (SUM_CONSTANT - value).
        """
        # Clamp value to valid range
        value = max(0, min(SUM_CONSTANT, value))

        self.local_state.set(key, value)
        self.remote_state.set(key, SUM_CONSTANT - value)

        status = SyncStatus.SYNCED
        self._record_event("update_local", status, f"key={key}, value={value}")

        return status

    def receive_remote_update(self, key: str, remote_value: float) -> SyncStatus:
        """
        Receive a remote state update.

        If conflict exists (local was also updated), use PHI-weighted merge.
        """
        remote_value = max(0, min(SUM_CONSTANT, remote_value))

        current_local = self.local_state.get(key, SUM_CONSTANT / 2)
        expected_remote = SUM_CONSTANT - current_local

        # Check for conflict
        if abs(remote_value - expected_remote) > 0.001:
            # Conflict: remote has diverged
            # Use PHI-weighted merge (assume remote is newer)
            new_local, new_remote = self._phi_weighted_merge(
                current_local, SUM_CONSTANT - remote_value,
                local_newer=False
            )

            self.local_state.set(key, new_local)
            self.remote_state.set(key, new_remote)

            status = SyncStatus.CONFLICT
            self._record_event("receive_remote", status,
                              f"conflict resolved: {key}={new_local:.2f}")
        else:
            self.remote_state.set(key, remote_value)
            status = SyncStatus.SYNCED
            self._record_event("receive_remote", status, f"key={key}")

        return status

    def sync_full(self, remote_state: StateVector) -> SyncStatus:
        """
        Perform full synchronization with remote state.

        Merges all keys using PHI-weighted resolution.
        """
        all_keys = set(self.local_state.values.keys()) | set(remote_state.values.keys())

        new_local = {}
        new_remote = {}
        conflicts = []

        for key in all_keys:
            local_val = self.local_state.get(key, SUM_CONSTANT / 2)
            remote_val = remote_state.get(key, SUM_CONSTANT / 2)

            # Check if already balanced
            if abs((local_val + remote_val) - SUM_CONSTANT) < 0.001:
                new_local[key] = local_val
                new_remote[key] = remote_val
            else:
                conflicts.append(key)
                # PHI-weighted merge based on timestamps
                local_newer = self.local_state.timestamp > remote_state.timestamp
                merged_local, merged_remote = self._phi_weighted_merge(
                    local_val, remote_val, local_newer
                )
                new_local[key] = merged_local
                new_remote[key] = merged_remote

        self.local_state = StateVector(values=new_local)
        self.remote_state = StateVector(values=new_remote)

        if conflicts:
            status = SyncStatus.CONFLICT
            self._record_event("sync_full", status,
                              f"resolved {len(conflicts)} conflicts")
        else:
            status = SyncStatus.SYNCED
            self._record_event("sync_full", status)

        # Check Lucas checkpoint
        if self._lucas_checkpoint(self.local_state.version):
            self._record_event("lucas_checkpoint", SyncStatus.SYNCED,
                              f"version={self.local_state.version}")

        return status

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current synchronization status."""
        all_keys = set(self.local_state.values.keys()) | set(self.remote_state.values.keys())

        key_sums = {}
        for key in all_keys:
            local_val = self.local_state.get(key, 0)
            remote_val = self.remote_state.get(key, 0)
            key_sums[key] = {
                "local": local_val,
                "remote": remote_val,
                "sum": local_val + remote_val,
                "balanced": abs((local_val + remote_val) - SUM_CONSTANT) < 0.001
            }

        all_balanced = all(ks["balanced"] for ks in key_sums.values())

        return {
            "status": SyncStatus.SYNCED if all_balanced else SyncStatus.DIVERGED,
            "local_version": self.local_state.version,
            "remote_version": self.remote_state.version,
            "local_checksum": self.local_state.checksum,
            "remote_checksum": self.remote_state.checksum,
            "sum_constant": SUM_CONSTANT,
            "keys": key_sums,
            "all_balanced": all_balanced
        }

    def _record_event(self, event_type: str, status: SyncStatus,
                      details: str = ""):
        """Record a sync event in history."""
        event = SyncEvent(
            event_type=event_type,
            local_state=StateVector(
                values=dict(self.local_state.values),
                version=self.local_state.version
            ),
            remote_state=StateVector(
                values=dict(self.remote_state.values),
                version=self.remote_state.version
            ),
            result_state=None,
            status=status,
            details=details
        )
        self.sync_history.append(event)

    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent sync history."""
        events = self.sync_history[-limit:]
        return [
            {
                "type": e.event_type,
                "status": e.status.name,
                "timestamp": e.timestamp,
                "details": e.details
            }
            for e in events
        ]

    def verify_invariant(self) -> bool:
        """Verify the sum invariant holds for all keys."""
        return self._verify_sum_invariant(self.local_state, self.remote_state)


if __name__ == "__main__":
    print("=" * 60)
    print("SyncManager - Mirror-paired State Synchronization Test")
    print("=" * 60)

    manager = SyncManager()

    print(f"\n[Configuration]")
    print(f"  SUM_CONSTANT: {SUM_CONSTANT}")
    print(f"  PHI: {PHI}")
    print(f"  Lucas checkpoints: {LUCAS[:6]}...")

    # Initialize state
    print("\n[Initialize State]")
    keys = ["alpha", "beta", "gamma", "delta"]
    status = manager.initialize_state(keys, local_ratio=0.6)
    print(f"  Status: {status.name}")

    sync_status = manager.get_sync_status()
    print(f"  All balanced: {sync_status['all_balanced']}")
    for key, info in sync_status['keys'].items():
        print(f"    {key}: local={info['local']:.2f}, remote={info['remote']:.2f}, "
              f"sum={info['sum']:.2f}")

    # Update local state
    print("\n[Local Updates]")
    manager.update_local("alpha", 150.0)
    manager.update_local("beta", 50.0)

    sync_status = manager.get_sync_status()
    print(f"  After updates:")
    for key, info in sync_status['keys'].items():
        print(f"    {key}: local={info['local']:.2f} + remote={info['remote']:.2f} "
              f"= {info['sum']:.2f} {'[OK]' if info['balanced'] else '[!]'}")

    print(f"\n  Invariant verified: {manager.verify_invariant()}")

    # Simulate remote conflict
    print("\n[Remote Conflict Resolution]")
    print("  Simulating remote update with conflict...")

    # Remote thinks alpha should be 100, but we set it to 150
    status = manager.receive_remote_update("alpha", 100.0)
    print(f"  Status: {status.name}")

    sync_status = manager.get_sync_status()
    alpha_info = sync_status['keys']['alpha']
    print(f"  After PHI-weighted merge:")
    print(f"    alpha: local={alpha_info['local']:.2f}, "
          f"remote={alpha_info['remote']:.2f}, sum={alpha_info['sum']:.2f}")

    # Full sync test
    print("\n[Full Sync Test]")
    remote_state = StateVector(values={
        "alpha": 100.0,
        "beta": 120.0,
        "gamma": 80.0,
        "delta": 107.0,
        "epsilon": 50.0  # New key
    })

    print(f"  Incoming remote state: {remote_state.values}")
    status = manager.sync_full(remote_state)
    print(f"  Sync status: {status.name}")

    sync_status = manager.get_sync_status()
    print(f"  After full sync:")
    for key, info in sync_status['keys'].items():
        print(f"    {key}: {info['local']:.2f} + {info['remote']:.2f} = "
              f"{info['sum']:.2f} {'[OK]' if info['balanced'] else '[!]'}")

    print(f"\n  Invariant verified: {manager.verify_invariant()}")

    # Show history
    print("\n[Sync History]")
    history = manager.get_history(limit=5)
    for event in history:
        print(f"  [{event['type']}] {event['status']}: {event['details']}")

    # Demonstrate mirror computation
    print("\n[Mirror Computation Demo]")
    test_state = StateVector(values={"x": 50, "y": 100, "z": 64})
    mirror = manager._compute_mirror(test_state)
    print(f"  Original: {test_state.values}")
    print(f"  Mirror:   {mirror.values}")
    print(f"  Sum per key: {SUM_CONSTANT}")

    # PHI-weighted merge demo
    print("\n[PHI-weighted Merge Demo]")
    for local_val, remote_val in [(100, 50), (150, 100), (200, 50)]:
        merged_local, merged_remote = manager._phi_weighted_merge(
            local_val, remote_val, local_newer=True
        )
        print(f"  local={local_val}, remote={remote_val} (local newer)")
        print(f"    -> merged: {merged_local:.2f} + {merged_remote:.2f} = "
              f"{merged_local + merged_remote:.2f}")

    print("\n[Test Complete]")
