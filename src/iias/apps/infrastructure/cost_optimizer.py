"""Cost Optimizer - 214-conserved budget allocation"""

SUM_CONSTANT = 214
BRAHIM_NUMBERS = [27, 42, 60, 75, 97, 117, 139, 154, 172, 187]


class CostOptimizer:
    """Allocate budget using mirror pairs that sum to 214."""

    def __init__(self, total_budget: float):
        self.total_budget = total_budget

    def allocate(self, services: list) -> dict:
        """Allocate budget to services using Brahim number weights."""
        n = len(services)
        allocations = {}

        for i, service in enumerate(services):
            if i < len(BRAHIM_NUMBERS):
                weight = BRAHIM_NUMBERS[i] / SUM_CONSTANT
            else:
                weight = 1 / n
            allocations[service] = self.total_budget * weight

        return allocations

    def mirror_allocate(self, service_a: str, service_b: str) -> dict:
        """Allocate to a mirror pair (sums to total budget)."""
        # Use B[1]=27 and its mirror B[10]=187
        weight_a = BRAHIM_NUMBERS[0] / SUM_CONSTANT  # 27/214
        weight_b = BRAHIM_NUMBERS[9] / SUM_CONSTANT  # 187/214

        return {
            service_a: self.total_budget * weight_a,
            service_b: self.total_budget * weight_b,
        }

    def verify_conservation(self, allocations: dict) -> bool:
        """Verify allocations sum to total budget."""
        return abs(sum(allocations.values()) - self.total_budget) < 0.01


if __name__ == "__main__":
    opt = CostOptimizer(10000)
    allocs = opt.allocate(["web", "api", "db", "cache", "queue"])
    print(f"Allocations: {allocs}")
    print(f"Sum: {sum(allocs.values()):.2f}")
    print(f"Conserved: {opt.verify_conservation(allocs)}")

    mirror = opt.mirror_allocate("frontend", "backend")
    print(f"Mirror pair: {mirror}")
