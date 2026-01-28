"""
IIAS Security: Rate Limiter

PHI-saturation rate control implementation.
Formula: rate(t) = max_rate * (1 - e^(-t/PHI))

This creates an organic rate limiting curve that smoothly approaches
the maximum rate using golden ratio scaling, preventing sudden capacity
changes while maintaining security guarantees.
"""

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

# Sacred Constants
PHI = 1.618033988749895
SUM_CONSTANT = 214
D3_CAPACITY = 4


@dataclass
class RateLimitState:
    """State tracking for a rate-limited entity."""
    entity_id: str
    request_count: int = 0
    window_start: float = field(default_factory=time.time)
    last_request: float = field(default_factory=time.time)
    blocked_count: int = 0

    def reset_window(self):
        """Reset the rate limit window."""
        self.request_count = 0
        self.window_start = time.time()


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    current_rate: float
    max_rate: float
    saturation: float
    remaining: int
    retry_after: Optional[float] = None
    message: str = ""


class RateLimiter:
    """
    PHI-Saturation Rate Limiter

    Implements rate limiting using the formula:
    rate(t) = max_rate * (1 - e^(-t/PHI))

    This provides an organic rate curve that:
    - Starts at 0 and asymptotically approaches max_rate
    - Uses PHI for natural scaling
    - Prevents burst attacks while allowing legitimate traffic

    Attributes:
        max_rate: Maximum requests per window
        window_seconds: Time window in seconds
        phi: Golden ratio constant
        states: Per-entity rate limit states
    """

    def __init__(
        self,
        max_rate: int = 100,
        window_seconds: float = 60.0,
        burst_multiplier: float = 1.0
    ):
        """
        Initialize the rate limiter.

        Args:
            max_rate: Maximum requests per window
            window_seconds: Time window in seconds
            burst_multiplier: Multiplier for burst allowance
        """
        self.max_rate = max_rate
        self.window_seconds = window_seconds
        self.burst_multiplier = burst_multiplier
        self.phi = PHI
        self.states: Dict[str, RateLimitState] = {}
        self._total_requests = 0
        self._total_blocked = 0

    def calculate_phi_rate(self, elapsed_time: float) -> float:
        """
        Calculate the PHI-saturation rate at time t.

        Formula: rate(t) = max_rate * (1 - e^(-t/PHI))

        Args:
            elapsed_time: Time elapsed in the current window

        Returns:
            Current allowed rate
        """
        if elapsed_time <= 0:
            return 0.0

        saturation = 1.0 - math.exp(-elapsed_time / self.phi)
        return self.max_rate * saturation * self.burst_multiplier

    def get_saturation_level(self, elapsed_time: float) -> float:
        """
        Get the current saturation level (0.0 to 1.0).

        Args:
            elapsed_time: Time elapsed in the current window

        Returns:
            Saturation level
        """
        if elapsed_time <= 0:
            return 0.0
        return 1.0 - math.exp(-elapsed_time / self.phi)

    def check_rate_limit(
        self,
        entity_id: str,
        cost: int = 1
    ) -> RateLimitResult:
        """
        Check if a request is allowed under rate limits.

        Args:
            entity_id: Unique identifier for the entity (IP, user, etc.)
            cost: Cost of this request (default 1)

        Returns:
            RateLimitResult with allow/deny decision
        """
        current_time = time.time()
        self._total_requests += 1

        # Get or create state
        if entity_id not in self.states:
            self.states[entity_id] = RateLimitState(entity_id=entity_id)

        state = self.states[entity_id]

        # Check if window has expired
        elapsed = current_time - state.window_start
        if elapsed >= self.window_seconds:
            state.reset_window()
            elapsed = 0.0

        # Calculate current allowed rate
        current_allowed = self.calculate_phi_rate(elapsed)
        saturation = self.get_saturation_level(elapsed)

        # Calculate remaining capacity
        remaining = max(0, int(current_allowed) - state.request_count)

        # Check if request is allowed
        if state.request_count + cost <= current_allowed:
            state.request_count += cost
            state.last_request = current_time

            return RateLimitResult(
                allowed=True,
                current_rate=current_allowed,
                max_rate=float(self.max_rate),
                saturation=saturation,
                remaining=remaining - cost,
                message="Request allowed"
            )
        else:
            # Calculate retry time
            # Solve for t: max_rate * (1 - e^(-t/PHI)) = request_count + cost
            target_rate = state.request_count + cost
            if target_rate < self.max_rate:
                # Solve: 1 - e^(-t/PHI) = target/max
                ratio = target_rate / self.max_rate
                retry_time = -self.phi * math.log(1 - ratio)
                retry_after = max(0, retry_time - elapsed)
            else:
                retry_after = self.window_seconds - elapsed

            state.blocked_count += 1
            self._total_blocked += 1

            return RateLimitResult(
                allowed=False,
                current_rate=current_allowed,
                max_rate=float(self.max_rate),
                saturation=saturation,
                remaining=0,
                retry_after=retry_after,
                message=f"Rate limit exceeded. Retry after {retry_after:.2f}s"
            )

    def get_rate_curve(
        self,
        num_points: int = 20
    ) -> List[Tuple[float, float]]:
        """
        Get the PHI-saturation rate curve for visualization.

        Args:
            num_points: Number of points to sample

        Returns:
            List of (time, rate) tuples
        """
        curve = []
        for i in range(num_points + 1):
            t = (i / num_points) * self.window_seconds
            rate = self.calculate_phi_rate(t)
            curve.append((t, rate))
        return curve

    def get_entity_state(self, entity_id: str) -> Optional[RateLimitState]:
        """Get the current state for an entity."""
        return self.states.get(entity_id)

    def reset_entity(self, entity_id: str) -> bool:
        """Reset rate limit state for an entity."""
        if entity_id in self.states:
            del self.states[entity_id]
            return True
        return False

    def get_statistics(self) -> Dict:
        """Get rate limiter statistics."""
        return {
            "total_requests": self._total_requests,
            "total_blocked": self._total_blocked,
            "block_rate": self._total_blocked / max(1, self._total_requests),
            "active_entities": len(self.states),
            "max_rate": self.max_rate,
            "window_seconds": self.window_seconds,
            "phi": self.phi,
        }

    def cleanup_expired(self, max_age_seconds: float = 3600.0) -> int:
        """
        Clean up expired entity states.

        Args:
            max_age_seconds: Remove entities inactive for this long

        Returns:
            Number of entities cleaned up
        """
        current_time = time.time()
        expired = []

        for entity_id, state in self.states.items():
            if current_time - state.last_request > max_age_seconds:
                expired.append(entity_id)

        for entity_id in expired:
            del self.states[entity_id]

        return len(expired)


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Security: Rate Limiter Test")
    print("=" * 60)
    print(f"\nPHI constant: {PHI}")
    print(f"Formula: rate(t) = max_rate * (1 - e^(-t/PHI))")

    # Create limiter
    limiter = RateLimiter(max_rate=100, window_seconds=10.0)

    print(f"\nConfiguration:")
    print(f"  Max rate: {limiter.max_rate}")
    print(f"  Window: {limiter.window_seconds}s")

    # Show rate curve
    print("\n--- PHI-Saturation Rate Curve ---")
    curve = limiter.get_rate_curve(10)
    for t, rate in curve:
        bar = "#" * int(rate / 2)
        print(f"  t={t:5.1f}s: rate={rate:6.2f} |{bar}")

    # Test rate limiting
    print("\n--- Rate Limit Tests ---")
    test_entity = "user_123"

    # Simulate requests over time
    print("\nSimulating rapid requests:")
    for i in range(15):
        result = limiter.check_rate_limit(test_entity)
        status = "ALLOWED" if result.allowed else "BLOCKED"
        print(f"  Request {i+1}: {status} "
              f"(saturation: {result.saturation:.2%}, "
              f"remaining: {result.remaining})")

        if not result.allowed:
            print(f"    Retry after: {result.retry_after:.2f}s")
            break

    # Test after time passage
    print("\nSimulating time passage (2s)...")
    state = limiter.get_entity_state(test_entity)
    if state:
        state.window_start -= 2.0  # Simulate 2 seconds passing

    print("\nContinuing requests after 2s:")
    for i in range(5):
        result = limiter.check_rate_limit(test_entity)
        status = "ALLOWED" if result.allowed else "BLOCKED"
        print(f"  Request: {status} "
              f"(saturation: {result.saturation:.2%}, "
              f"current_rate: {result.current_rate:.1f})")

    # Test multiple entities
    print("\n--- Multiple Entity Test ---")
    entities = ["ip_1.1.1.1", "ip_2.2.2.2", "ip_3.3.3.3"]
    for entity in entities:
        result = limiter.check_rate_limit(entity)
        print(f"  {entity}: {'ALLOWED' if result.allowed else 'BLOCKED'}")

    # Statistics
    print("\n--- Statistics ---")
    stats = limiter.get_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Rate Limiter Test Complete")
    print("=" * 60)
