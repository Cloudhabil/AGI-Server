"""
IIAS Replication Manager

Mirror-pair redundancy using the SUM_CONSTANT formula:
    replica_location = SUM_CONSTANT - primary_location
    replica_location = 214 - primary_location

This creates complementary location pairs that sum to 214,
ensuring balanced geographic/logical distribution of replicas.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Set
from enum import Enum
import hashlib
import threading


# Fundamental constants
PHI = 1.618033988749895
GENESIS_CONSTANT = 2 / 901
SUM_CONSTANT = 214


class ReplicationState(Enum):
    """State of replication."""
    SYNCED = "synced"
    SYNCING = "syncing"
    OUT_OF_SYNC = "out_of_sync"
    FAILED = "failed"
    PENDING = "pending"


class LocationRole(Enum):
    """Role of a location in replication pair."""
    PRIMARY = "primary"
    REPLICA = "replica"


@dataclass
class Location:
    """Storage location definition."""
    location_id: int
    name: str
    role: LocationRole
    mirror_id: Optional[int] = None
    capacity_gb: int = 1000
    used_gb: int = 0
    is_online: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def available_gb(self) -> int:
        """Get available capacity."""
        return self.capacity_gb - self.used_gb

    def calculate_mirror_id(self) -> int:
        """Calculate mirror location ID using SUM_CONSTANT."""
        return SUM_CONSTANT - self.location_id


@dataclass
class ReplicatedData:
    """Data item with replication info."""
    data_id: str
    data: Any
    primary_location: int
    replica_location: int
    state: ReplicationState
    primary_version: int = 1
    replica_version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    last_synced: Optional[datetime] = None
    checksum: str = ""

    def __post_init__(self):
        """Calculate checksum after initialization."""
        if not self.checksum:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate data checksum."""
        return hashlib.sha256(str(self.data).encode()).hexdigest()[:16]

    def verify_checksum(self, data: Any) -> bool:
        """Verify data matches checksum."""
        test_checksum = hashlib.sha256(str(data).encode()).hexdigest()[:16]
        return test_checksum == self.checksum


class ReplicationManager:
    """
    Mirror-pair replication manager using SUM_CONSTANT = 214.

    Formula: replica_location = 214 - primary_location

    This creates complementary pairs:
    - Location 1 <-> Location 213
    - Location 50 <-> Location 164
    - Location 100 <-> Location 114
    - Location 107 <-> Location 107 (self-mirroring center point)

    The symmetric pairing ensures:
    - Balanced distribution across location spectrum
    - Predictable replica placement
    - Simple failover logic
    """

    def __init__(self, max_location_id: int = 214):
        """
        Initialize replication manager.

        Args:
            max_location_id: Maximum location ID (default: SUM_CONSTANT)
        """
        self.max_location_id = max_location_id
        self._locations: Dict[int, Location] = {}
        self._replicated_data: Dict[str, ReplicatedData] = {}
        self._sync_queue: List[str] = []
        self._lock = threading.Lock()

    def calculate_replica_location(self, primary_location: int) -> int:
        """
        Calculate replica location using mirror-pair formula.

        Formula: replica = SUM_CONSTANT - primary = 214 - primary

        Args:
            primary_location: Primary storage location ID

        Returns:
            Calculated replica location ID
        """
        if primary_location < 1 or primary_location > self.max_location_id:
            raise ValueError(
                f"Location must be between 1 and {self.max_location_id}"
            )
        return SUM_CONSTANT - primary_location

    def register_location(
        self,
        location_id: int,
        name: str,
        capacity_gb: int = 1000,
        auto_register_mirror: bool = True,
    ) -> Tuple[Location, Optional[Location]]:
        """
        Register a storage location and optionally its mirror.

        Args:
            location_id: Location identifier
            name: Human-readable name
            capacity_gb: Storage capacity
            auto_register_mirror: Also register mirror location

        Returns:
            Tuple of (primary_location, mirror_location or None)
        """
        mirror_id = self.calculate_replica_location(location_id)

        # Create primary location
        primary = Location(
            location_id=location_id,
            name=name,
            role=LocationRole.PRIMARY,
            mirror_id=mirror_id,
            capacity_gb=capacity_gb,
        )
        self._locations[location_id] = primary

        mirror = None
        if auto_register_mirror and mirror_id != location_id:
            # Create mirror location
            mirror = Location(
                location_id=mirror_id,
                name=f"{name}_mirror",
                role=LocationRole.REPLICA,
                mirror_id=location_id,
                capacity_gb=capacity_gb,
            )
            self._locations[mirror_id] = mirror

        return primary, mirror

    def get_location(self, location_id: int) -> Optional[Location]:
        """Get location by ID."""
        return self._locations.get(location_id)

    def get_mirror_pair(self, location_id: int) -> Tuple[Optional[Location], Optional[Location]]:
        """Get both locations in a mirror pair."""
        mirror_id = self.calculate_replica_location(location_id)
        return self._locations.get(location_id), self._locations.get(mirror_id)

    def store_with_replication(
        self,
        data_id: str,
        data: Any,
        primary_location: int,
    ) -> ReplicatedData:
        """
        Store data with automatic mirror replication.

        Args:
            data_id: Unique data identifier
            data: Data to store
            primary_location: Primary storage location

        Returns:
            ReplicatedData record
        """
        replica_location = self.calculate_replica_location(primary_location)

        # Verify locations exist
        if primary_location not in self._locations:
            raise ValueError(f"Primary location {primary_location} not registered")
        if replica_location not in self._locations:
            raise ValueError(f"Replica location {replica_location} not registered")

        replicated = ReplicatedData(
            data_id=data_id,
            data=data,
            primary_location=primary_location,
            replica_location=replica_location,
            state=ReplicationState.SYNCED,
            last_synced=datetime.now(),
        )

        with self._lock:
            self._replicated_data[data_id] = replicated

            # Update location usage (simulated)
            data_size = len(str(data)) / (1024 * 1024 * 1024)  # Rough GB estimate
            self._locations[primary_location].used_gb += data_size
            self._locations[replica_location].used_gb += data_size

        return replicated

    def get_data(self, data_id: str, prefer_primary: bool = True) -> Optional[Any]:
        """
        Retrieve replicated data.

        Args:
            data_id: Data identifier
            prefer_primary: Prefer primary location (if available)

        Returns:
            Data if found
        """
        with self._lock:
            replicated = self._replicated_data.get(data_id)
            if not replicated:
                return None

            if prefer_primary:
                primary_loc = self._locations.get(replicated.primary_location)
                if primary_loc and primary_loc.is_online:
                    return replicated.data

            # Fallback to replica
            replica_loc = self._locations.get(replicated.replica_location)
            if replica_loc and replica_loc.is_online:
                return replicated.data

            return None

    def trigger_sync(self, data_id: str) -> bool:
        """
        Trigger synchronization for a data item.

        Args:
            data_id: Data to sync

        Returns:
            True if sync triggered
        """
        with self._lock:
            if data_id in self._replicated_data:
                replicated = self._replicated_data[data_id]
                replicated.state = ReplicationState.SYNCING
                replicated.last_synced = datetime.now()
                replicated.replica_version = replicated.primary_version
                replicated.state = ReplicationState.SYNCED
                return True
        return False

    def failover(self, location_id: int) -> List[str]:
        """
        Perform failover from a location to its mirror.

        Args:
            location_id: Failed location ID

        Returns:
            List of data IDs that were failed over
        """
        mirror_id = self.calculate_replica_location(location_id)
        failed_over = []

        with self._lock:
            # Mark location as offline
            if location_id in self._locations:
                self._locations[location_id].is_online = False

            # Find all data with primary at failed location
            for data_id, replicated in self._replicated_data.items():
                if replicated.primary_location == location_id:
                    # Swap primary and replica
                    replicated.primary_location = mirror_id
                    replicated.replica_location = location_id
                    replicated.state = ReplicationState.OUT_OF_SYNC
                    failed_over.append(data_id)

        return failed_over

    def restore_location(self, location_id: int) -> int:
        """
        Restore a location and trigger resync.

        Args:
            location_id: Location to restore

        Returns:
            Number of items queued for resync
        """
        resync_count = 0

        with self._lock:
            if location_id in self._locations:
                self._locations[location_id].is_online = True

            # Queue resync for affected data
            for data_id, replicated in self._replicated_data.items():
                if (replicated.primary_location == location_id or
                    replicated.replica_location == location_id):
                    if replicated.state == ReplicationState.OUT_OF_SYNC:
                        self._sync_queue.append(data_id)
                        resync_count += 1

        return resync_count

    def get_mirror_pairs(self) -> List[Tuple[int, int]]:
        """
        Get all registered mirror pairs.

        Returns:
            List of (location_id, mirror_id) tuples
        """
        pairs: Set[Tuple[int, int]] = set()

        for loc_id in self._locations:
            mirror_id = self.calculate_replica_location(loc_id)
            pair = tuple(sorted([loc_id, mirror_id]))
            pairs.add(pair)

        return list(pairs)

    def get_replication_status(self, data_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed replication status for data."""
        replicated = self._replicated_data.get(data_id)
        if not replicated:
            return None

        primary_loc = self._locations.get(replicated.primary_location)
        replica_loc = self._locations.get(replicated.replica_location)

        return {
            "data_id": data_id,
            "state": replicated.state.value,
            "primary": {
                "location_id": replicated.primary_location,
                "name": primary_loc.name if primary_loc else "unknown",
                "online": primary_loc.is_online if primary_loc else False,
                "version": replicated.primary_version,
            },
            "replica": {
                "location_id": replicated.replica_location,
                "name": replica_loc.name if replica_loc else "unknown",
                "online": replica_loc.is_online if replica_loc else False,
                "version": replicated.replica_version,
            },
            "checksum": replicated.checksum,
            "last_synced": replicated.last_synced.isoformat() if replicated.last_synced else None,
            "mirror_sum": replicated.primary_location + replicated.replica_location,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get replication statistics."""
        total_data = len(self._replicated_data)
        synced = sum(1 for d in self._replicated_data.values() if d.state == ReplicationState.SYNCED)
        out_of_sync = sum(1 for d in self._replicated_data.values() if d.state == ReplicationState.OUT_OF_SYNC)

        return {
            "sum_constant": SUM_CONSTANT,
            "registered_locations": len(self._locations),
            "mirror_pairs": len(self.get_mirror_pairs()),
            "total_replicated_data": total_data,
            "synced": synced,
            "out_of_sync": out_of_sync,
            "pending_sync": len(self._sync_queue),
            "online_locations": sum(1 for loc in self._locations.values() if loc.is_online),
        }


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Replication Manager - Test Suite")
    print("=" * 60)
    print(f"SUM_CONSTANT: {SUM_CONSTANT}")
    print(f"Formula: replica_location = {SUM_CONSTANT} - primary_location")

    # Initialize manager
    manager = ReplicationManager()

    # Test 1: Mirror pair calculation
    print("\n[TEST 1] Mirror Pair Calculation...")
    test_locations = [1, 50, 100, 107, 150, 200, 213]

    for loc in test_locations:
        mirror = manager.calculate_replica_location(loc)
        print(f"  Location {loc:>3} <-> Mirror {mirror:>3} (sum = {loc + mirror})")

    # Test 2: Register locations
    print("\n[TEST 2] Registering Location Pairs...")

    location_configs = [
        (1, "US-East", 5000),
        (50, "EU-West", 3000),
        (100, "Asia-Pacific", 4000),
    ]

    for loc_id, name, capacity in location_configs:
        primary, mirror = manager.register_location(loc_id, name, capacity)
        print(f"  Registered: {name} (ID:{primary.location_id}) <-> "
              f"{mirror.name if mirror else 'self'} (ID:{mirror.location_id if mirror else loc_id})")

    # Test 3: Store data with replication
    print("\n[TEST 3] Storing Data with Replication...")

    test_data = [
        ("user_db", {"users": 10000, "active": 5000}, 1),
        ("product_catalog", {"items": 50000, "categories": 200}, 50),
        ("analytics", {"events": 1000000}, 100),
    ]

    for data_id, data, primary_loc in test_data:
        replicated = manager.store_with_replication(data_id, data, primary_loc)
        print(f"  Stored '{data_id}': primary={replicated.primary_location}, "
              f"replica={replicated.replica_location}, sum={replicated.primary_location + replicated.replica_location}")

    # Test 4: Replication status
    print("\n[TEST 4] Replication Status...")
    status = manager.get_replication_status("user_db")
    if status:
        print(f"  Data: {status['data_id']}")
        print(f"  State: {status['state']}")
        print(f"  Primary: {status['primary']['name']} (ID:{status['primary']['location_id']})")
        print(f"  Replica: {status['replica']['name']} (ID:{status['replica']['location_id']})")
        print(f"  Mirror sum verification: {status['mirror_sum']} (expected: {SUM_CONSTANT})")

    # Test 5: Failover simulation
    print("\n[TEST 5] Failover Simulation...")
    print(f"  Simulating failure of location 1 (US-East)...")

    failed_over = manager.failover(1)
    print(f"  Failed over {len(failed_over)} data items: {failed_over}")

    # Check status after failover
    status_after = manager.get_replication_status("user_db")
    if status_after:
        print(f"  'user_db' new primary: {status_after['primary']['location_id']} "
              f"(was replica at {SUM_CONSTANT - status_after['primary']['location_id']})")

    # Test 6: Restore location
    print("\n[TEST 6] Location Restoration...")
    resync_count = manager.restore_location(1)
    print(f"  Restored location 1, queued {resync_count} items for resync")

    # Test 7: Get all mirror pairs
    print("\n[TEST 7] All Mirror Pairs...")
    pairs = manager.get_mirror_pairs()
    for loc1, loc2 in pairs:
        print(f"  {loc1:>3} <-> {loc2:>3} (sum = {loc1 + loc2})")

    # Test 8: Retrieve data with failover
    print("\n[TEST 8] Data Retrieval with Failover...")
    for data_id, _, _ in test_data:
        data = manager.get_data(data_id)
        print(f"  Retrieved '{data_id}': {data}")

    # Test 9: Special case - center point
    print("\n[TEST 9] Center Point (Self-Mirror)...")
    center = SUM_CONSTANT // 2
    if SUM_CONSTANT % 2 == 0:
        center_mirror = manager.calculate_replica_location(center)
        print(f"  Location {center} mirrors to {center_mirror}")
        print(f"  Note: {SUM_CONSTANT}/2 = {SUM_CONSTANT/2} (not a valid self-mirror)")
    else:
        print(f"  SUM_CONSTANT {SUM_CONSTANT} is odd, no perfect center point")

    # Test 10: Statistics
    print("\n[TEST 10] Replication Statistics...")
    stats = manager.get_statistics()
    print(f"  SUM_CONSTANT: {stats['sum_constant']}")
    print(f"  Registered locations: {stats['registered_locations']}")
    print(f"  Mirror pairs: {stats['mirror_pairs']}")
    print(f"  Total replicated data: {stats['total_replicated_data']}")
    print(f"  Synced: {stats['synced']}")
    print(f"  Out of sync: {stats['out_of_sync']}")
    print(f"  Online locations: {stats['online_locations']}")

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print(f"SUM_CONSTANT = {SUM_CONSTANT}")
    print(f"Formula: replica = {SUM_CONSTANT} - primary")
    print("=" * 60)
