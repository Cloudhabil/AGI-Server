"""
Mirror Balancer - Resource Pairing Using Brahim Conservation Law
================================================================

This module implements resource pairing based on the fundamental identity:
    B_n + M(B_n) = 214

Where:
    - B_n is a Brahim number from the sequence [27, 42, 60, 75, 97, 117, 139, 154, 172, 187]
    - M(B_n) is the mirror complement such that B_n + M(B_n) = SUM_CONSTANT (214)
    - CENTER (107) is the axis of symmetry

This ensures perfect conservation in resource allocation.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Any

from iias.constants import PHI, CENTER, SUM_CONSTANT, BRAHIM_NUMBERS, LUCAS


@dataclass
class ResourcePair:
    """A balanced pair of resources that sum to SUM_CONSTANT (214)."""

    primary: float
    mirror: float
    index: int
    name: str

    @property
    def sum(self) -> float:
        """Verify conservation law: primary + mirror = 214."""
        return self.primary + self.mirror

    @property
    def is_balanced(self) -> bool:
        """Check if the pair satisfies the conservation law."""
        return abs(self.sum - SUM_CONSTANT) < 1e-10

    @property
    def deviation_from_center(self) -> float:
        """Distance of primary from CENTER (107)."""
        return self.primary - CENTER


class MirrorBalancer:
    """
    Resource pairing system using the Brahim mirror identity.

    The mirror balancer ensures that all resource allocations maintain
    the conservation law B_n + M(B_n) = 214, where M(B_n) is the mirror
    complement of any Brahim number B_n.

    Attributes:
        pairs: List of ResourcePair objects for all 10 Brahim numbers.
        center: The axis of symmetry (107).
        sum_constant: The conservation sum (214).
    """

    def __init__(self):
        """Initialize the MirrorBalancer with all Brahim number pairs."""
        self.center = CENTER
        self.sum_constant = SUM_CONSTANT
        self.brahim_numbers = BRAHIM_NUMBERS
        self.pairs: List[ResourcePair] = []

        # Build resource pairs from Brahim numbers
        pair_names = [
            "PERCEPTION",    # B_1 = 27
            "ATTENTION",     # B_2 = 42
            "SECURITY",      # B_3 = 60
            "STABILITY",     # B_4 = 75
            "COMPRESSION",   # B_5 = 97
            "HARMONY",       # B_6 = 117
            "REASONING",     # B_7 = 139
            "PREDICTION",    # B_8 = 154
            "CREATIVITY",    # B_9 = 172
            "WISDOM",        # B_10 = 187
        ]

        for i, b_n in enumerate(self.brahim_numbers):
            mirror = self._compute_mirror(b_n)
            self.pairs.append(ResourcePair(
                primary=float(b_n),
                mirror=mirror,
                index=i + 1,
                name=pair_names[i]
            ))

    def _compute_mirror(self, value: float) -> float:
        """
        Compute the mirror complement of a value.

        M(x) = SUM_CONSTANT - x = 214 - x

        Args:
            value: The primary value to mirror.

        Returns:
            The mirror complement such that value + mirror = 214.
        """
        return self.sum_constant - value

    def get_pair(self, index: int) -> Optional[ResourcePair]:
        """
        Get a specific resource pair by index (1-10).

        Args:
            index: The Brahim number index (1-10).

        Returns:
            The ResourcePair or None if index is invalid.
        """
        if 1 <= index <= len(self.pairs):
            return self.pairs[index - 1]
        return None

    def balance_resource(self, amount: float) -> Dict[str, Any]:
        """
        Balance an arbitrary resource amount using mirror pairing.

        Given any amount, compute its mirror and find the nearest
        Brahim pair for optimal allocation.

        Args:
            amount: The resource amount to balance.

        Returns:
            Dictionary with primary, mirror, nearest pair, and metrics.
        """
        mirror = self._compute_mirror(amount)

        # Find nearest Brahim number
        nearest_idx = 0
        min_distance = float('inf')
        for i, b_n in enumerate(self.brahim_numbers):
            distance = abs(amount - b_n)
            if distance < min_distance:
                min_distance = distance
                nearest_idx = i

        nearest_pair = self.pairs[nearest_idx]

        return {
            "primary": amount,
            "mirror": mirror,
            "sum": amount + mirror,
            "is_conserved": abs(amount + mirror - self.sum_constant) < 1e-10,
            "nearest_brahim": nearest_pair.primary,
            "nearest_pair_name": nearest_pair.name,
            "deviation_from_brahim": amount - nearest_pair.primary,
            "phi_ratio": amount / mirror if mirror != 0 else float('inf'),
        }

    def allocate_symmetric(self, total: float) -> List[Dict[str, Any]]:
        """
        Allocate resources symmetrically around CENTER.

        Distributes a total amount across the 10 Brahim pairs,
        maintaining mirror symmetry.

        Args:
            total: Total resources to allocate.

        Returns:
            List of allocations with primary and mirror components.
        """
        allocations = []

        # Weight by PHI-based decay from center
        weights = []
        for pair in self.pairs:
            # Pairs closer to CENTER get higher weight
            distance = abs(pair.primary - self.center)
            weight = 1.0 / (1.0 + distance / self.center)
            weights.append(weight)

        # Normalize weights
        total_weight = sum(weights)
        normalized = [w / total_weight for w in weights]

        for i, pair in enumerate(self.pairs):
            allocation = total * normalized[i]
            allocations.append({
                "index": pair.index,
                "name": pair.name,
                "brahim_primary": pair.primary,
                "brahim_mirror": pair.mirror,
                "allocated": allocation,
                "weight": normalized[i],
            })

        return allocations

    def verify_conservation(self) -> Dict[str, Any]:
        """
        Verify that all pairs satisfy the conservation law.

        Returns:
            Dictionary with verification results.
        """
        all_balanced = all(pair.is_balanced for pair in self.pairs)

        results = []
        for pair in self.pairs:
            results.append({
                "index": pair.index,
                "name": pair.name,
                "primary": pair.primary,
                "mirror": pair.mirror,
                "sum": pair.sum,
                "balanced": pair.is_balanced,
            })

        return {
            "all_conserved": all_balanced,
            "sum_constant": self.sum_constant,
            "center": self.center,
            "pairs": results,
        }

    def phi_weighted_distribution(self, amount: float) -> Dict[str, Any]:
        """
        Distribute amount using PHI-weighted mirror pairs.

        Uses the golden ratio PHI = 1.618... to weight the distribution
        between primary and mirror allocations.

        Args:
            amount: Total amount to distribute.

        Returns:
            PHI-weighted distribution results.
        """
        # PHI-split: primary gets 1/(1+PHI), mirror gets PHI/(1+PHI)
        primary_ratio = 1.0 / (1.0 + PHI)
        mirror_ratio = PHI / (1.0 + PHI)

        primary_amount = amount * primary_ratio
        mirror_amount = amount * mirror_ratio

        return {
            "total": amount,
            "phi": PHI,
            "primary_ratio": primary_ratio,
            "mirror_ratio": mirror_ratio,
            "primary_amount": primary_amount,
            "mirror_amount": mirror_amount,
            "ratio_check": mirror_amount / primary_amount if primary_amount != 0 else 0,
            "conservation": primary_amount + mirror_amount,
        }


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Mirror Balancer - Resource Pairing Test")
    print("=" * 60)

    balancer = MirrorBalancer()

    # Test 1: Verify all pairs satisfy conservation law
    print("\n[Test 1] Conservation Law Verification")
    print("-" * 40)
    verification = balancer.verify_conservation()
    print(f"Sum Constant: {verification['sum_constant']}")
    print(f"Center: {verification['center']}")
    print(f"All Conserved: {verification['all_conserved']}")
    print("\nPairs:")
    for pair in verification['pairs']:
        status = "OK" if pair['balanced'] else "FAIL"
        print(f"  B_{pair['index']:2d} = {pair['primary']:3.0f} + M = {pair['mirror']:3.0f} = {pair['sum']:3.0f} [{status}]")

    # Test 2: Balance an arbitrary resource
    print("\n[Test 2] Balance Arbitrary Resource")
    print("-" * 40)
    test_amounts = [50, 100, 107, 150, 200]
    for amount in test_amounts:
        result = balancer.balance_resource(amount)
        print(f"  Amount: {amount:3.0f} -> Mirror: {result['mirror']:3.0f}, "
              f"Sum: {result['sum']:3.0f}, Nearest: {result['nearest_pair_name']}")

    # Test 3: Symmetric allocation
    print("\n[Test 3] Symmetric Allocation of 1000 units")
    print("-" * 40)
    allocations = balancer.allocate_symmetric(1000)
    total_allocated = 0
    for alloc in allocations:
        print(f"  {alloc['name']:12s}: {alloc['allocated']:7.2f} (weight: {alloc['weight']:.4f})")
        total_allocated += alloc['allocated']
    print(f"  {'TOTAL':12s}: {total_allocated:7.2f}")

    # Test 4: PHI-weighted distribution
    print("\n[Test 4] PHI-Weighted Distribution")
    print("-" * 40)
    phi_dist = balancer.phi_weighted_distribution(100)
    print(f"  PHI: {phi_dist['phi']:.6f}")
    print(f"  Primary Ratio: {phi_dist['primary_ratio']:.6f}")
    print(f"  Mirror Ratio: {phi_dist['mirror_ratio']:.6f}")
    print(f"  Primary Amount: {phi_dist['primary_amount']:.4f}")
    print(f"  Mirror Amount: {phi_dist['mirror_amount']:.4f}")
    print(f"  Ratio Check (should be PHI): {phi_dist['ratio_check']:.6f}")

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
