"""Load Balancer - Lucas-weighted fair queuing"""

LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]

# Tier capacities
FREE_CAPACITY = sum(LUCAS[0:4])       # 15
STANDARD_CAPACITY = sum(LUCAS[4:8])   # 105
ENTERPRISE_CAPACITY = sum(LUCAS[8:12]) # 720
TOTAL_CAPACITY = 840


class LoadBalancer:
    """Lucas-weighted fair queuing with ratios 15:105:720."""

    def __init__(self):
        self.tiers = {
            "free": FREE_CAPACITY,
            "standard": STANDARD_CAPACITY,
            "enterprise": ENTERPRISE_CAPACITY,
        }
        self.queues = {tier: [] for tier in self.tiers}

    def get_weight(self, tier: str) -> float:
        return self.tiers.get(tier, 0) / TOTAL_CAPACITY

    def enqueue(self, tier: str, request: dict):
        if tier in self.queues:
            self.queues[tier].append(request)

    def dequeue(self) -> tuple:
        """Dequeue based on weighted priority."""
        for tier in ["enterprise", "standard", "free"]:
            if self.queues[tier]:
                return tier, self.queues[tier].pop(0)
        return None, None

    def get_ratio(self) -> dict:
        return {
            "free": 1,
            "standard": STANDARD_CAPACITY // FREE_CAPACITY,  # 7
            "enterprise": ENTERPRISE_CAPACITY // FREE_CAPACITY,  # 48
        }


if __name__ == "__main__":
    lb = LoadBalancer()
    print(f"Tier capacities: {lb.tiers}")
    print(f"Ratios: {lb.get_ratio()}")
    print(f"Free weight: {lb.get_weight('free'):.4f}")
    print(f"Enterprise weight: {lb.get_weight('enterprise'):.4f}")
