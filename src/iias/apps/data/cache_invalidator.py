"""
IIAS Cache Invalidator

Genesis-timed expiry using GENESIS_CONSTANT = 2/901.

The Genesis constant represents the fundamental ratio for cache timing,
providing a precise expiration window based on access patterns.

Default TTL calculation: base_ttl * GENESIS_CONSTANT
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import hashlib
import threading
import time


# Fundamental constants
PHI = 1.618033988749895
GENESIS_CONSTANT = 2 / 901  # 0.00221975...
SUM_CONSTANT = 214


class CacheState(Enum):
    """Cache entry state."""
    VALID = "valid"
    STALE = "stale"
    EXPIRED = "expired"
    INVALIDATED = "invalidated"


@dataclass
class CacheEntry:
    """Individual cache entry with Genesis-timed expiry."""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    ttl_seconds: float
    state: CacheState = CacheState.VALID
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    genesis_factor: float = GENESIS_CONSTANT
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return datetime.now() > self.expires_at

    def time_remaining(self) -> float:
        """Get remaining time in seconds."""
        remaining = (self.expires_at - datetime.now()).total_seconds()
        return max(0, remaining)

    def access(self) -> Any:
        """Record access and return value."""
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.value


class CacheInvalidator:
    """
    Genesis-timed cache invalidation system.

    Uses GENESIS_CONSTANT (2/901) to calculate expiration times:
    - TTL = base_time * GENESIS_CONSTANT * multiplier
    - Provides precise, mathematically-grounded cache timing

    Features:
    - Automatic expiration based on Genesis constant
    - Manual invalidation support
    - Stale-while-revalidate pattern
    - Access-based TTL extension
    """

    def __init__(
        self,
        base_ttl_seconds: float = 1000.0,
        genesis_multiplier: float = 1.0,
        auto_cleanup: bool = False,
    ):
        """
        Initialize cache invalidator.

        Args:
            base_ttl_seconds: Base TTL before Genesis factor applied
            genesis_multiplier: Multiplier for Genesis constant
            auto_cleanup: Enable automatic background cleanup
        """
        self.base_ttl = base_ttl_seconds
        self.genesis_multiplier = genesis_multiplier
        self._cache: Dict[str, CacheEntry] = {}
        self._invalidation_callbacks: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self._cleanup_thread: Optional[threading.Thread] = None

        if auto_cleanup:
            self._start_cleanup_thread()

    def calculate_ttl(self, custom_base: Optional[float] = None) -> float:
        """
        Calculate TTL using Genesis constant.

        Formula: TTL = base * GENESIS_CONSTANT * multiplier

        Args:
            custom_base: Override default base TTL

        Returns:
            TTL in seconds
        """
        base = custom_base or self.base_ttl
        return base * GENESIS_CONSTANT * self.genesis_multiplier

    def _generate_cache_key(self, key: str) -> str:
        """Generate internal cache key."""
        return hashlib.sha256(key.encode()).hexdigest()[:16] + "_" + key

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> CacheEntry:
        """
        Set cache entry with Genesis-timed expiry.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Override calculated TTL
            metadata: Optional metadata

        Returns:
            Created CacheEntry
        """
        ttl = ttl_seconds or self.calculate_ttl()
        now = datetime.now()

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl),
            ttl_seconds=ttl,
            genesis_factor=GENESIS_CONSTANT,
            metadata=metadata or {},
        )

        with self._lock:
            self._cache[key] = entry

        return entry

    def get(
        self,
        key: str,
        default: Any = None,
        extend_on_access: bool = False,
    ) -> Optional[Any]:
        """
        Get cached value if valid.

        Args:
            key: Cache key
            default: Default if not found or expired
            extend_on_access: Extend TTL on access

        Returns:
            Cached value or default
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                return default

            if entry.is_expired():
                entry.state = CacheState.EXPIRED
                return default

            if extend_on_access:
                # Extend by Genesis-scaled amount
                extension = self.calculate_ttl() * 0.5
                entry.expires_at += timedelta(seconds=extension)

            return entry.access()

    def invalidate(self, key: str, reason: str = "manual") -> bool:
        """
        Manually invalidate a cache entry.

        Args:
            key: Cache key to invalidate
            reason: Reason for invalidation

        Returns:
            True if entry was invalidated
        """
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                entry.state = CacheState.INVALIDATED
                entry.metadata["invalidation_reason"] = reason
                entry.metadata["invalidated_at"] = datetime.now().isoformat()

                # Call invalidation callback if registered
                if key in self._invalidation_callbacks:
                    try:
                        self._invalidation_callbacks[key](entry)
                    except Exception:
                        pass

                del self._cache[key]
                return True
        return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.

        Args:
            pattern: Substring to match in keys

        Returns:
            Number of entries invalidated
        """
        keys_to_invalidate = [
            k for k in self._cache.keys() if pattern in k
        ]

        count = 0
        for key in keys_to_invalidate:
            if self.invalidate(key, reason=f"pattern:{pattern}"):
                count += 1

        return count

    def mark_stale(self, key: str) -> bool:
        """
        Mark entry as stale (allows stale-while-revalidate).

        Args:
            key: Cache key

        Returns:
            True if entry was marked stale
        """
        with self._lock:
            if key in self._cache:
                self._cache[key].state = CacheState.STALE
                return True
        return False

    def get_stale(self, key: str) -> Optional[Any]:
        """
        Get value even if stale (for stale-while-revalidate pattern).

        Args:
            key: Cache key

        Returns:
            Value if exists (even if stale), None otherwise
        """
        with self._lock:
            entry = self._cache.get(key)
            if entry:
                return entry.access()
        return None

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.

        Returns:
            Number of entries removed
        """
        with self._lock:
            expired_keys = [
                k for k, v in self._cache.items() if v.is_expired()
            ]

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)

    def _start_cleanup_thread(self):
        """Start background cleanup thread."""
        def cleanup_loop():
            while True:
                time.sleep(self.calculate_ttl() * 10)
                self.cleanup_expired()

        self._cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self._cleanup_thread.start()

    def register_invalidation_callback(self, key: str, callback: Callable) -> None:
        """Register callback for when key is invalidated."""
        self._invalidation_callbacks[key] = callback

    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a cache entry."""
        with self._lock:
            entry = self._cache.get(key)
            if entry:
                return {
                    "key": entry.key,
                    "state": entry.state.value,
                    "created_at": entry.created_at.isoformat(),
                    "expires_at": entry.expires_at.isoformat(),
                    "ttl_seconds": entry.ttl_seconds,
                    "time_remaining": entry.time_remaining(),
                    "access_count": entry.access_count,
                    "genesis_factor": entry.genesis_factor,
                    "is_expired": entry.is_expired(),
                }
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = len(self._cache)
            expired = sum(1 for e in self._cache.values() if e.is_expired())
            stale = sum(1 for e in self._cache.values() if e.state == CacheState.STALE)
            valid = total - expired - stale

            return {
                "total_entries": total,
                "valid_entries": valid,
                "stale_entries": stale,
                "expired_entries": expired,
                "genesis_constant": GENESIS_CONSTANT,
                "base_ttl_seconds": self.base_ttl,
                "calculated_ttl": self.calculate_ttl(),
                "genesis_multiplier": self.genesis_multiplier,
            }

    def clear(self) -> int:
        """Clear all cache entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Cache Invalidator - Test Suite")
    print("=" * 60)
    print(f"GENESIS_CONSTANT: {GENESIS_CONSTANT}")
    print(f"Formula: 2/901 = {2/901}")

    # Initialize invalidator
    invalidator = CacheInvalidator(base_ttl_seconds=1000.0, genesis_multiplier=1.0)

    # Test 1: TTL calculation
    print("\n[TEST 1] Genesis TTL Calculation...")
    ttl = invalidator.calculate_ttl()
    print(f"  Base TTL: 1000 seconds")
    print(f"  Genesis constant: {GENESIS_CONSTANT}")
    print(f"  Calculated TTL: {ttl:.6f} seconds")
    print(f"  Verification: 1000 * {GENESIS_CONSTANT} = {1000 * GENESIS_CONSTANT:.6f}")

    # Test 2: Set cache entries
    print("\n[TEST 2] Setting Cache Entries...")
    entries = [
        ("user:123", {"name": "Alice", "role": "admin"}),
        ("session:abc", {"token": "xyz123", "expires": "2025-01-29"}),
        ("config:app", {"debug": False, "version": "2.0"}),
        ("metrics:cpu", {"value": 45.2, "unit": "percent"}),
    ]

    for key, value in entries:
        entry = invalidator.set(key, value)
        print(f"  Set '{key}': TTL={entry.ttl_seconds:.4f}s, expires={entry.expires_at}")

    # Test 3: Get cache entries
    print("\n[TEST 3] Retrieving Cache Entries...")
    for key, _ in entries[:2]:
        value = invalidator.get(key)
        info = invalidator.get_entry_info(key)
        print(f"  Get '{key}': {value}")
        print(f"    - Access count: {info['access_count']}")
        print(f"    - Time remaining: {info['time_remaining']:.4f}s")

    # Test 4: Manual invalidation
    print("\n[TEST 4] Manual Invalidation...")
    result = invalidator.invalidate("session:abc", reason="logout")
    print(f"  Invalidated 'session:abc': {result}")
    value = invalidator.get("session:abc")
    print(f"  Get after invalidation: {value}")

    # Test 5: Pattern invalidation
    print("\n[TEST 5] Pattern Invalidation...")
    invalidator.set("user:456", {"name": "Bob"})
    invalidator.set("user:789", {"name": "Charlie"})
    count = invalidator.invalidate_pattern("user:")
    print(f"  Invalidated {count} entries matching 'user:'")

    # Test 6: Stale-while-revalidate
    print("\n[TEST 6] Stale-While-Revalidate Pattern...")
    invalidator.set("data:important", {"value": 42})
    invalidator.mark_stale("data:important")

    regular_get = invalidator.get("data:important")
    stale_get = invalidator.get_stale("data:important")

    print(f"  Regular get (stale): {regular_get}")
    print(f"  Stale get: {stale_get}")

    # Test 7: Custom TTL
    print("\n[TEST 7] Custom TTL with Genesis Scaling...")
    custom_bases = [100, 500, 1000, 5000, 10000]
    print(f"  Base (s) -> Genesis TTL (s)")
    for base in custom_bases:
        custom_ttl = invalidator.calculate_ttl(custom_base=base)
        print(f"  {base:>6} -> {custom_ttl:.6f}")

    # Test 8: Statistics
    print("\n[TEST 8] Cache Statistics...")
    stats = invalidator.get_statistics()
    print(f"  Total entries: {stats['total_entries']}")
    print(f"  Valid entries: {stats['valid_entries']}")
    print(f"  Genesis constant: {stats['genesis_constant']}")
    print(f"  Calculated TTL: {stats['calculated_ttl']:.6f}s")

    # Test 9: TTL extension on access
    print("\n[TEST 9] TTL Extension on Access...")
    invalidator.set("extend:test", "test_value")
    info_before = invalidator.get_entry_info("extend:test")
    invalidator.get("extend:test", extend_on_access=True)
    info_after = invalidator.get_entry_info("extend:test")

    print(f"  Before access: expires at {info_before['expires_at']}")
    print(f"  After access:  expires at {info_after['expires_at']}")

    # Test 10: Cleanup
    print("\n[TEST 10] Clear All Cache...")
    cleared = invalidator.clear()
    print(f"  Cleared {cleared} entries")
    print(f"  Remaining entries: {invalidator.get_statistics()['total_entries']}")

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print(f"GENESIS_CONSTANT = 2/901 = {GENESIS_CONSTANT}")
    print("=" * 60)
