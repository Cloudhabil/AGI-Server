"""
IIAS Data Tiering Manager

Hot/warm/cold storage classification by dimension:
- D1-D4: Hot storage (frequent access, high performance)
- D5-D8: Warm storage (moderate access, balanced)
- D9-D12: Cold storage (archival, cost-optimized)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime


# Fundamental constants
PHI = 1.618033988749895
GENESIS_CONSTANT = 2 / 901
SUM_CONSTANT = 214


class StorageTier(Enum):
    """Storage tier classification."""
    HOT = "hot"
    WARM = "warm"
    COLD = "cold"


@dataclass
class TieredData:
    """Data item with tier classification."""
    key: str
    data: Any
    dimension: int
    tier: StorageTier
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0

    def access(self) -> Any:
        """Record access and return data."""
        self.last_accessed = datetime.now()
        self.access_count += 1
        return self.data


class DataTieringManager:
    """
    Manages hot/warm/cold storage tiering based on dimensional classification.

    Tier Assignment:
    - Dimensions 1-4: HOT tier (fast SSD, in-memory cache)
    - Dimensions 5-8: WARM tier (standard SSD, disk cache)
    - Dimensions 9-12: COLD tier (HDD/archive, compressed)
    """

    # Dimension ranges for each tier
    HOT_DIMENSIONS = range(1, 5)    # D1-D4
    WARM_DIMENSIONS = range(5, 9)   # D5-D8
    COLD_DIMENSIONS = range(9, 13)  # D9-D12

    def __init__(self):
        """Initialize the tiering manager."""
        self._hot_storage: Dict[str, TieredData] = {}
        self._warm_storage: Dict[str, TieredData] = {}
        self._cold_storage: Dict[str, TieredData] = {}
        self._dimension_map: Dict[str, int] = {}

    def _classify_tier(self, dimension: int) -> StorageTier:
        """Classify dimension to storage tier."""
        if dimension in self.HOT_DIMENSIONS:
            return StorageTier.HOT
        elif dimension in self.WARM_DIMENSIONS:
            return StorageTier.WARM
        elif dimension in self.COLD_DIMENSIONS:
            return StorageTier.COLD
        else:
            raise ValueError(f"Invalid dimension {dimension}. Must be 1-12.")

    def _get_storage(self, tier: StorageTier) -> Dict[str, TieredData]:
        """Get storage dict for tier."""
        return {
            StorageTier.HOT: self._hot_storage,
            StorageTier.WARM: self._warm_storage,
            StorageTier.COLD: self._cold_storage,
        }[tier]

    def store(self, key: str, data: Any, dimension: int) -> TieredData:
        """
        Store data in appropriate tier based on dimension.

        Args:
            key: Unique identifier for the data
            data: Data to store
            dimension: Dimension (1-12) determining tier placement

        Returns:
            TieredData object with tier assignment
        """
        tier = self._classify_tier(dimension)
        tiered_item = TieredData(
            key=key,
            data=data,
            dimension=dimension,
            tier=tier,
        )

        storage = self._get_storage(tier)
        storage[key] = tiered_item
        self._dimension_map[key] = dimension

        return tiered_item

    def retrieve(self, key: str) -> Optional[Any]:
        """
        Retrieve data by key, searching all tiers.

        Args:
            key: Data identifier

        Returns:
            Data if found, None otherwise
        """
        for storage in [self._hot_storage, self._warm_storage, self._cold_storage]:
            if key in storage:
                return storage[key].access()
        return None

    def get_tier(self, key: str) -> Optional[StorageTier]:
        """Get the tier for a stored item."""
        if key in self._dimension_map:
            return self._classify_tier(self._dimension_map[key])
        return None

    def migrate_tier(self, key: str, new_dimension: int) -> Optional[TieredData]:
        """
        Migrate data to a new tier based on dimension change.

        Args:
            key: Data identifier
            new_dimension: New dimension (1-12)

        Returns:
            Updated TieredData or None if not found
        """
        # Find and remove from current storage
        data = None
        for storage in [self._hot_storage, self._warm_storage, self._cold_storage]:
            if key in storage:
                data = storage.pop(key).data
                break

        if data is None:
            return None

        # Store in new tier
        return self.store(key, data, new_dimension)

    def get_tier_stats(self) -> Dict[str, int]:
        """Get count of items in each tier."""
        return {
            "hot": len(self._hot_storage),
            "warm": len(self._warm_storage),
            "cold": len(self._cold_storage),
            "total": len(self._hot_storage) + len(self._warm_storage) + len(self._cold_storage),
        }

    def list_tier(self, tier: StorageTier) -> List[str]:
        """List all keys in a specific tier."""
        return list(self._get_storage(tier).keys())

    def calculate_phi_weighted_access(self, key: str) -> float:
        """
        Calculate PHI-weighted access score for tiering decisions.

        Higher scores indicate candidates for tier promotion.
        """
        for storage in [self._hot_storage, self._warm_storage, self._cold_storage]:
            if key in storage:
                item = storage[key]
                age_hours = (datetime.now() - item.created_at).total_seconds() / 3600
                # PHI-weighted: recent high-frequency access scores higher
                if age_hours > 0:
                    return (item.access_count * PHI) / age_hours
                return item.access_count * PHI
        return 0.0


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Data Tiering Manager - Test Suite")
    print("=" * 60)

    # Initialize manager
    manager = DataTieringManager()

    # Test storing data in different dimensions
    print("\n[TEST 1] Storing data across dimensions...")

    test_data = [
        ("user_session", {"user": "alice", "token": "abc123"}, 1),    # D1 -> HOT
        ("real_time_metrics", {"cpu": 45, "mem": 62}, 3),             # D3 -> HOT
        ("daily_report", {"date": "2025-01-28", "total": 1000}, 6),   # D6 -> WARM
        ("monthly_aggregate", {"month": "Jan", "sum": 50000}, 7),     # D7 -> WARM
        ("annual_archive", {"year": 2024, "records": 1000000}, 10),   # D10 -> COLD
        ("historical_log", {"period": "2020-2024"}, 12),              # D12 -> COLD
    ]

    for key, data, dim in test_data:
        result = manager.store(key, data, dim)
        print(f"  Stored '{key}' in D{dim} -> {result.tier.value.upper()} tier")

    # Test tier statistics
    print("\n[TEST 2] Tier Statistics...")
    stats = manager.get_tier_stats()
    print(f"  HOT:  {stats['hot']} items (D1-D4)")
    print(f"  WARM: {stats['warm']} items (D5-D8)")
    print(f"  COLD: {stats['cold']} items (D9-D12)")
    print(f"  Total: {stats['total']} items")

    # Test retrieval
    print("\n[TEST 3] Data Retrieval...")
    for key, _, _ in test_data[:3]:
        retrieved = manager.retrieve(key)
        tier = manager.get_tier(key)
        print(f"  Retrieved '{key}': {retrieved} (tier: {tier.value})")

    # Test tier migration
    print("\n[TEST 4] Tier Migration (D6 -> D2)...")
    original_tier = manager.get_tier("daily_report")
    migrated = manager.migrate_tier("daily_report", 2)
    new_tier = manager.get_tier("daily_report")
    print(f"  'daily_report': {original_tier.value} -> {new_tier.value}")

    # Test PHI-weighted access scoring
    print("\n[TEST 5] PHI-Weighted Access Scores...")
    # Simulate multiple accesses
    for _ in range(5):
        manager.retrieve("user_session")
    for _ in range(2):
        manager.retrieve("annual_archive")

    for key, _, _ in test_data:
        score = manager.calculate_phi_weighted_access(key)
        print(f"  '{key}': {score:.4f}")

    # Test dimension validation
    print("\n[TEST 6] Dimension Validation...")
    try:
        manager.store("invalid", {}, 15)
        print("  ERROR: Should have raised ValueError")
    except ValueError as e:
        print(f"  Correctly raised: {e}")

    # List items by tier
    print("\n[TEST 7] Items by Tier...")
    for tier in StorageTier:
        items = manager.list_tier(tier)
        print(f"  {tier.value.upper()}: {items}")

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print(f"PHI constant used: {PHI}")
    print("=" * 60)
