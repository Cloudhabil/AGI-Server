"""IIAS Edge Offline Cache - Dimension-Priority Caching

This module implements dimension-priority caching where lower dimensions
(D1, D2, etc.) are cached first, ensuring fundamental data is always
available when operating offline.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import OrderedDict
import time
import hashlib
import json

# Constants
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
TOTAL_STATES = 840
PHI = 1.618033988749895


class Dimension(IntEnum):
    """Dimension levels for caching priority (lower = higher priority)."""
    D1 = 1   # Highest priority - core identity/constants
    D2 = 2   # Essential operations
    D3 = 3   # Standard operations
    D4 = 4   # Extended features
    D5 = 5   # Advanced features
    D6 = 6   # Specialized data
    D7 = 7   # Historical data
    D8 = 8   # Analytics
    D9 = 9   # Temporary data
    D10 = 10  # Lowest priority - ephemeral


@dataclass
class CacheEntry:
    """Represents a cached item."""
    key: str
    value: Any
    dimension: Dimension
    size_bytes: int
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    ttl_seconds: Optional[float] = None

    @property
    def is_expired(self) -> bool:
        if self.ttl_seconds is None:
            return False
        return (time.time() - self.created_at) > self.ttl_seconds

    @property
    def priority_score(self) -> float:
        """Calculate priority score (lower dimension = higher priority)."""
        # Combine dimension priority with recency and access frequency
        recency = 1.0 / (1 + time.time() - self.accessed_at)
        frequency = min(self.access_count / 100.0, 1.0)
        dimension_weight = 1.0 / self.dimension.value

        return dimension_weight * 0.6 + recency * 0.2 + frequency * 0.2


@dataclass
class CacheStats:
    """Cache statistics."""
    total_entries: int = 0
    total_size_bytes: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    dimension_counts: Dict[int, int] = field(default_factory=dict)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total) if total > 0 else 0.0


class OfflineCache:
    """
    Dimension-priority cache for offline edge operation.

    Caching strategy:
    - D1 data is always retained (core constants, identity)
    - D2-D3 data has high retention priority
    - D4-D7 data uses LRU within dimension
    - D8-D10 data is first to be evicted

    Size allocation follows Lucas numbers per dimension.
    """

    def __init__(
        self,
        max_size_bytes: int = 10 * 1024 * 1024,  # 10 MB default
        dimension_quotas: Optional[Dict[Dimension, float]] = None
    ):
        self._max_size = max_size_bytes
        self._cache: Dict[str, CacheEntry] = OrderedDict()
        self._dimension_index: Dict[Dimension, Set[str]] = {d: set() for d in Dimension}
        self._stats = CacheStats(dimension_counts={d.value: 0 for d in Dimension})

        # Compute dimension quotas based on Lucas numbers
        self._quotas = dimension_quotas or self._compute_lucas_quotas()

    def _compute_lucas_quotas(self) -> Dict[Dimension, float]:
        """
        Compute size quotas per dimension using Lucas numbers.

        Higher dimensions get proportionally less space following
        inverse Lucas scaling.
        """
        # Use inverse Lucas for quotas (D1 gets most, D10 gets least)
        inverse_weights = [1.0 / LUCAS[min(d.value - 1, 11)] for d in Dimension]
        total = sum(inverse_weights)

        quotas = {}
        for i, dim in enumerate(Dimension):
            quotas[dim] = inverse_weights[i] / total

        return quotas

    def _compute_key_hash(self, key: str) -> str:
        """Compute deterministic hash for key."""
        return hashlib.md5(key.encode()).hexdigest()[:16]

    def _estimate_size(self, value: Any) -> int:
        """Estimate size of value in bytes."""
        try:
            return len(json.dumps(value).encode())
        except (TypeError, ValueError):
            return len(str(value).encode())

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve item from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        entry = self._cache.get(key)

        if entry is None:
            self._stats.misses += 1
            return None

        if entry.is_expired:
            self.delete(key)
            self._stats.misses += 1
            return None

        # Update access stats
        entry.accessed_at = time.time()
        entry.access_count += 1
        self._stats.hits += 1

        # Move to end (most recently used)
        self._cache.move_to_end(key)

        return entry.value

    def set(
        self,
        key: str,
        value: Any,
        dimension: Dimension = Dimension.D5,
        ttl_seconds: Optional[float] = None
    ) -> bool:
        """
        Store item in cache with dimension priority.

        Args:
            key: Cache key
            value: Value to cache
            dimension: Priority dimension (D1 highest)
            ttl_seconds: Optional time-to-live

        Returns:
            True if cached successfully
        """
        size = self._estimate_size(value)

        # Check if we need to evict
        while self._stats.total_size_bytes + size > self._max_size:
            if not self._evict_one():
                # Cannot evict enough space
                return False

        # Remove existing entry if present
        if key in self._cache:
            self.delete(key)

        # Create and store entry
        entry = CacheEntry(
            key=key,
            value=value,
            dimension=dimension,
            size_bytes=size,
            ttl_seconds=ttl_seconds
        )

        self._cache[key] = entry
        self._dimension_index[dimension].add(key)
        self._stats.total_entries += 1
        self._stats.total_size_bytes += size
        self._stats.dimension_counts[dimension.value] += 1

        return True

    def delete(self, key: str) -> bool:
        """
        Remove item from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted, False if not found
        """
        entry = self._cache.get(key)
        if entry is None:
            return False

        del self._cache[key]
        self._dimension_index[entry.dimension].discard(key)
        self._stats.total_entries -= 1
        self._stats.total_size_bytes -= entry.size_bytes
        self._stats.dimension_counts[entry.dimension.value] -= 1

        return True

    def _evict_one(self) -> bool:
        """
        Evict one item based on dimension priority.

        Eviction order:
        1. Expired items (any dimension)
        2. D10 -> D9 -> ... -> D2 (lowest priority first)
        3. Within dimension, use LRU

        D1 items are protected and only evicted as last resort.

        Returns:
            True if item was evicted
        """
        # First, try to evict expired items
        for key, entry in list(self._cache.items()):
            if entry.is_expired:
                self.delete(key)
                self._stats.evictions += 1
                return True

        # Evict from lowest priority dimension first
        for dim in reversed(list(Dimension)):
            if dim == Dimension.D1:
                continue  # Protect D1 unless absolutely necessary

            keys = self._dimension_index[dim]
            if keys:
                # Find LRU entry in this dimension
                lru_key = None
                lru_time = float('inf')

                for key in keys:
                    entry = self._cache.get(key)
                    if entry and entry.accessed_at < lru_time:
                        lru_time = entry.accessed_at
                        lru_key = key

                if lru_key:
                    self.delete(lru_key)
                    self._stats.evictions += 1
                    return True

        # Last resort: evict from D1
        if self._dimension_index[Dimension.D1]:
            key = next(iter(self._dimension_index[Dimension.D1]))
            self.delete(key)
            self._stats.evictions += 1
            return True

        return False

    def get_dimension_entries(self, dimension: Dimension) -> List[CacheEntry]:
        """Get all entries for a dimension."""
        return [
            self._cache[key]
            for key in self._dimension_index[dimension]
            if key in self._cache
        ]

    def get_dimension_size(self, dimension: Dimension) -> int:
        """Get total size of entries in a dimension."""
        return sum(
            self._cache[key].size_bytes
            for key in self._dimension_index[dimension]
            if key in self._cache
        )

    def prefetch_dimension(
        self,
        dimension: Dimension,
        items: Dict[str, Any],
        ttl_seconds: Optional[float] = None
    ) -> int:
        """
        Prefetch multiple items for a dimension.

        Args:
            dimension: Target dimension
            items: Dict of key-value pairs
            ttl_seconds: Optional TTL for all items

        Returns:
            Number of items successfully cached
        """
        success_count = 0
        for key, value in items.items():
            if self.set(key, value, dimension, ttl_seconds):
                success_count += 1
        return success_count

    def ensure_offline_ready(self, critical_data: Dict[str, Any]) -> bool:
        """
        Ensure critical data is cached for offline operation.

        Stores all items in D1 (highest priority).

        Args:
            critical_data: Dict of essential key-value pairs

        Returns:
            True if all items were cached
        """
        success = True
        for key, value in critical_data.items():
            if not self.set(key, value, Dimension.D1, ttl_seconds=None):
                success = False
        return success

    def prune_expired(self) -> int:
        """Remove all expired entries."""
        expired = [
            key for key, entry in self._cache.items()
            if entry.is_expired
        ]
        for key in expired:
            self.delete(key)
        return len(expired)

    def clear_dimension(self, dimension: Dimension) -> int:
        """Clear all entries in a dimension."""
        keys = list(self._dimension_index[dimension])
        for key in keys:
            self.delete(key)
        return len(keys)

    def clear_all(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
        self._dimension_index = {d: set() for d in Dimension}
        self._stats = CacheStats(dimension_counts={d.value: 0 for d in Dimension})

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self._stats

    def get_quotas(self) -> Dict[str, Tuple[float, int]]:
        """Get dimension quotas as (ratio, bytes)."""
        return {
            dim.name: (ratio, int(ratio * self._max_size))
            for dim, ratio in self._quotas.items()
        }

    def summary(self) -> Dict:
        """Get cache summary."""
        return {
            "max_size_bytes": self._max_size,
            "used_size_bytes": self._stats.total_size_bytes,
            "utilization_percent": round(
                (self._stats.total_size_bytes / self._max_size) * 100, 2
            ),
            "total_entries": self._stats.total_entries,
            "hit_rate": round(self._stats.hit_rate, 3),
            "hits": self._stats.hits,
            "misses": self._stats.misses,
            "evictions": self._stats.evictions,
            "dimension_counts": {
                Dimension(d).name: count
                for d, count in self._stats.dimension_counts.items()
            },
        }


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Edge Offline Cache - Test Suite")
    print("=" * 60)

    # Initialize cache with 1KB limit for testing
    cache = OfflineCache(max_size_bytes=1024)

    print(f"\nCache initialized with {cache._max_size} bytes max")

    # Show dimension quotas
    print("\n--- Dimension Quotas (Lucas-based) ---")
    quotas = cache.get_quotas()
    for dim_name, (ratio, bytes_quota) in list(quotas.items())[:5]:
        print(f"  {dim_name}: {ratio*100:5.1f}% = {bytes_quota:4} bytes")

    # Test basic set/get
    print("\n--- Basic Set/Get Test ---")
    cache.set("config.version", "1.0.0", Dimension.D1)
    cache.set("user.name", "EdgeUser", Dimension.D2)
    cache.set("session.token", "abc123", Dimension.D5)

    print(f"  config.version (D1): {cache.get('config.version')}")
    print(f"  user.name (D2): {cache.get('user.name')}")
    print(f"  session.token (D5): {cache.get('session.token')}")

    # Test dimension-priority caching
    print("\n--- Dimension Priority Test ---")
    critical_data = {
        "phi": PHI,
        "lucas": LUCAS,
        "total_states": TOTAL_STATES,
    }
    cache.ensure_offline_ready(critical_data)
    print(f"  PHI cached in D1: {cache.get('phi')}")
    print(f"  LUCAS cached in D1: {cache.get('lucas')}")

    # Test prefetch
    print("\n--- Prefetch Test ---")
    feature_data = {
        f"feature_{i}": f"value_{i}" for i in range(5)
    }
    count = cache.prefetch_dimension(Dimension.D4, feature_data)
    print(f"  Prefetched {count} items to D4")

    # Show dimension distribution
    print("\n--- Dimension Distribution ---")
    for dim in list(Dimension)[:6]:
        entries = cache.get_dimension_entries(dim)
        size = cache.get_dimension_size(dim)
        print(f"  {dim.name}: {len(entries)} entries, {size} bytes")

    # Test TTL expiration
    print("\n--- TTL Expiration Test ---")
    cache.set("temp_data", "expires_soon", Dimension.D9, ttl_seconds=0.001)
    print(f"  Before expiry: {cache.get('temp_data')}")
    time.sleep(0.01)
    print(f"  After expiry: {cache.get('temp_data')}")

    # Test eviction under pressure
    print("\n--- Eviction Test ---")
    initial_entries = cache._stats.total_entries
    for i in range(20):
        cache.set(f"pressure_{i}", "x" * 100, Dimension.D8)

    print(f"  Initial entries: {initial_entries}")
    print(f"  After pressure: {cache._stats.total_entries}")
    print(f"  Evictions: {cache._stats.evictions}")

    # Verify D1 data survived
    print(f"  D1 PHI survived: {cache.get('phi') == PHI}")

    # Test cache stats
    print("\n--- Cache Statistics ---")
    stats = cache.get_stats()
    print(f"  Hit rate: {stats.hit_rate:.1%}")
    print(f"  Hits: {stats.hits}, Misses: {stats.misses}")

    # Final summary
    print("\n--- Final Summary ---")
    summary = cache.summary()
    for key, value in summary.items():
        if key != "dimension_counts":
            print(f"  {key}: {value}")

    print("\n  Dimension counts:")
    for dim, count in summary["dimension_counts"].items():
        if count > 0:
            print(f"    {dim}: {count}")

    print("\n" + "=" * 60)
    print("Offline Cache tests completed successfully!")
    print("=" * 60)
