"""Rate Limiter - PHI-saturation rate control"""

import math
import time

PHI = 1.618033988749895


class RateLimiter:
    """PHI-based rate limiting with saturation curve."""

    def __init__(self, max_rate: float, window_seconds: float = 1.0):
        self.max_rate = max_rate
        self.window = window_seconds
        self.requests = []

    def current_rate(self) -> float:
        """Get current request rate."""
        now = time.time()
        self.requests = [t for t in self.requests if now - t < self.window]
        return len(self.requests) / self.window

    def saturation_limit(self, t: float) -> float:
        """
        PHI-saturation rate limit.
        limit(t) = max_rate * (1 - e^(-t/PHI))
        """
        return self.max_rate * (1 - math.exp(-t / PHI))

    def allow(self) -> bool:
        """Check if request is allowed."""
        rate = self.current_rate()
        if rate < self.max_rate:
            self.requests.append(time.time())
            return True
        return False

    def utilization(self) -> float:
        """Current utilization as fraction of max."""
        return self.current_rate() / self.max_rate


if __name__ == "__main__":
    limiter = RateLimiter(max_rate=100)

    print("PHI-saturation limits:")
    for t in [0.5, 1.0, PHI, 2.0, 3.0]:
        limit = limiter.saturation_limit(t)
        print(f"  t={t:.2f}: {limit:.2f} req/s ({limit/100*100:.1f}%)")

    print(f"\nAllow request: {limiter.allow()}")
    print(f"Current rate: {limiter.current_rate():.2f}")
