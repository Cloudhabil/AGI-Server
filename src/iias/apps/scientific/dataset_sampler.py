"""
Dataset Sampler - Lucas-Stratified Selection
=============================================

Samples datasets using Lucas sequence-based stratified selection.
Sample sizes follow the Lucas sequence: [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]

Stratification Tiers:
    Tier 1:  1 sample   - Single representative
    Tier 2:  3 samples  - Minimal diversity
    Tier 3:  4 samples  - Basic coverage
    Tier 4:  7 samples  - Standard sample
    ...
    Tier 10: 123 samples - D10 Wisdom capacity
    ...
    Tier 12: 322 samples - Full coverage

Total capacity: 840 samples (sum of Lucas sequence)
"""

import random
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, TypeVar, Generic, Callable
from enum import Enum

# Constants
PHI = 1.618033988749895
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
D10_CAPACITY = 123  # Wisdom dimension
TOTAL_STATES = 840

T = TypeVar('T')


class SamplingTier(Enum):
    """Sampling tier based on Lucas sequence."""
    L1 = 1    # 1 sample
    L2 = 2    # 3 samples
    L3 = 3    # 4 samples
    L4 = 4    # 7 samples
    L5 = 5    # 11 samples
    L6 = 6    # 18 samples
    L7 = 7    # 29 samples
    L8 = 8    # 47 samples
    L9 = 9    # 76 samples
    L10 = 10  # 123 samples (D10 Wisdom)
    L11 = 11  # 199 samples
    L12 = 12  # 322 samples

    @property
    def sample_size(self) -> int:
        """Get sample size for this tier."""
        return LUCAS[self.value - 1]


class StratificationMethod(Enum):
    """Methods for stratified sampling."""
    UNIFORM = "uniform"           # Equal probability
    PHI_WEIGHTED = "phi_weighted" # PHI-based importance
    QUARTILE = "quartile"         # Quartile-based
    PERCENTILE = "percentile"     # Percentile-based


@dataclass
class Stratum:
    """A stratum in stratified sampling."""
    name: str
    size: int
    weight: float = 1.0
    indices: List[int] = field(default_factory=list)


@dataclass
class SampleResult(Generic[T]):
    """Result of a sampling operation."""
    tier: SamplingTier
    target_size: int
    actual_size: int
    samples: List[T]
    strata_distribution: Dict[str, int]
    phi_balance: float
    coverage_ratio: float


class DatasetSampler(Generic[T]):
    """
    Samples datasets using Lucas-stratified selection.

    Features:
        - Lucas sequence sample sizes
        - PHI-weighted stratification
        - Multiple stratification methods
        - D10 capacity optimization
    """

    def __init__(self, data: Optional[List[T]] = None):
        self.phi = PHI
        self.lucas = LUCAS
        self.d10_capacity = D10_CAPACITY
        self.total_states = TOTAL_STATES

        self._data: List[T] = data or []
        self._strata: Dict[str, Stratum] = {}
        self._rng = random.Random()

    def set_data(self, data: List[T]) -> None:
        """Set the dataset to sample from."""
        self._data = list(data)
        self._strata.clear()

    def set_seed(self, seed: int) -> None:
        """Set random seed for reproducibility."""
        self._rng.seed(seed)

    def create_strata(self,
                      key_func: Callable[[T], str],
                      weight_func: Optional[Callable[[str], float]] = None) -> Dict[str, Stratum]:
        """
        Create strata from the dataset using a key function.

        Args:
            key_func: Function to extract stratum key from each item
            weight_func: Optional function to assign weights to strata

        Returns:
            Dictionary of strata
        """
        self._strata.clear()

        # Group items by stratum
        for i, item in enumerate(self._data):
            key = key_func(item)
            if key not in self._strata:
                self._strata[key] = Stratum(name=key, size=0, indices=[])
            self._strata[key].size += 1
            self._strata[key].indices.append(i)

        # Assign weights
        if weight_func:
            for key, stratum in self._strata.items():
                stratum.weight = weight_func(key)
        else:
            # Default: PHI-weighted based on stratum order
            for i, key in enumerate(sorted(self._strata.keys())):
                self._strata[key].weight = self.phi ** (i / len(self._strata))

        return self._strata

    def sample_lucas(self, tier: SamplingTier,
                     method: StratificationMethod = StratificationMethod.PHI_WEIGHTED) -> SampleResult[T]:
        """
        Sample using Lucas tier size with stratification.

        Args:
            tier: Lucas tier determining sample size
            method: Stratification method to use

        Returns:
            SampleResult with samples and metadata
        """
        target_size = tier.sample_size

        if not self._data:
            return SampleResult(
                tier=tier,
                target_size=target_size,
                actual_size=0,
                samples=[],
                strata_distribution={},
                phi_balance=0.0,
                coverage_ratio=0.0
            )

        # Calculate samples per stratum based on method
        strata_samples = self._calculate_strata_allocation(target_size, method)

        # Collect samples
        samples: List[T] = []
        distribution: Dict[str, int] = {}

        if self._strata:
            for stratum_name, count in strata_samples.items():
                stratum = self._strata[stratum_name]
                # Sample from stratum indices
                available = min(count, len(stratum.indices))
                selected_indices = self._rng.sample(stratum.indices, available)
                for idx in selected_indices:
                    samples.append(self._data[idx])
                distribution[stratum_name] = len(selected_indices)
        else:
            # No strata - uniform random sampling
            available = min(target_size, len(self._data))
            samples = self._rng.sample(self._data, available)
            distribution["uniform"] = len(samples)

        # Calculate PHI balance (how close to golden ratio distribution)
        phi_balance = self._calculate_phi_balance(distribution)

        # Coverage ratio
        coverage = len(samples) / len(self._data) if self._data else 0.0

        return SampleResult(
            tier=tier,
            target_size=target_size,
            actual_size=len(samples),
            samples=samples,
            strata_distribution=distribution,
            phi_balance=phi_balance,
            coverage_ratio=coverage
        )

    def _calculate_strata_allocation(self,
                                      target_size: int,
                                      method: StratificationMethod) -> Dict[str, int]:
        """Calculate how many samples to take from each stratum."""
        if not self._strata:
            return {}

        allocation: Dict[str, int] = {}

        if method == StratificationMethod.UNIFORM:
            # Equal allocation
            per_stratum = target_size // len(self._strata)
            remainder = target_size % len(self._strata)
            for i, name in enumerate(self._strata.keys()):
                allocation[name] = per_stratum + (1 if i < remainder else 0)

        elif method == StratificationMethod.PHI_WEIGHTED:
            # PHI-based allocation using weights
            total_weight = sum(s.weight for s in self._strata.values())
            for name, stratum in self._strata.items():
                proportion = stratum.weight / total_weight
                allocation[name] = max(1, int(target_size * proportion))

        elif method == StratificationMethod.QUARTILE:
            # Allocate based on quartile position
            sorted_strata = sorted(self._strata.keys())
            n = len(sorted_strata)
            for i, name in enumerate(sorted_strata):
                quartile = i * 4 // n  # 0, 1, 2, or 3
                # Lucas-based quartile sizes
                lucas_idx = min(3 + quartile * 2, 11)
                proportion = self.lucas[lucas_idx] / self.total_states
                allocation[name] = max(1, int(target_size * proportion * 4))

        elif method == StratificationMethod.PERCENTILE:
            # Size-proportional allocation
            total_size = sum(s.size for s in self._strata.values())
            for name, stratum in self._strata.items():
                proportion = stratum.size / total_size
                allocation[name] = max(1, int(target_size * proportion))

        return allocation

    def _calculate_phi_balance(self, distribution: Dict[str, int]) -> float:
        """Calculate how close the distribution is to PHI ratio."""
        if len(distribution) < 2:
            return 1.0

        values = sorted(distribution.values(), reverse=True)
        ratios = []

        for i in range(len(values) - 1):
            if values[i + 1] > 0:
                ratio = values[i] / values[i + 1]
                # How close to PHI?
                deviation = abs(ratio - self.phi) / self.phi
                ratios.append(1.0 - min(deviation, 1.0))

        return sum(ratios) / len(ratios) if ratios else 1.0

    def get_optimal_tier(self, desired_coverage: float) -> SamplingTier:
        """
        Get the optimal Lucas tier for desired coverage ratio.

        Args:
            desired_coverage: Target coverage (0.0 to 1.0)

        Returns:
            Optimal SamplingTier
        """
        if not self._data:
            return SamplingTier.L1

        target_samples = int(len(self._data) * desired_coverage)

        # Find smallest tier that provides enough samples
        for tier in SamplingTier:
            if tier.sample_size >= target_samples:
                return tier

        return SamplingTier.L12

    def sample_d10(self, method: StratificationMethod = StratificationMethod.PHI_WEIGHTED) -> SampleResult[T]:
        """
        Sample using D10 (Wisdom) capacity of 123.

        This is a convenience method for the Wisdom-level sampling.
        """
        return self.sample_lucas(SamplingTier.L10, method)

    def get_lucas_coverage_table(self) -> Dict[str, Any]:
        """Get coverage statistics for each Lucas tier."""
        data_size = len(self._data)
        table = {
            "data_size": data_size,
            "tiers": {}
        }

        for tier in SamplingTier:
            size = tier.sample_size
            coverage = size / data_size if data_size > 0 else 0.0
            table["tiers"][tier.name] = {
                "sample_size": size,
                "coverage": coverage,
                "coverage_percent": coverage * 100,
            }

        return table


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Dataset Sampler Test")
    print("=" * 60)

    # Display constants
    print(f"\nPHI = {PHI}")
    print(f"LUCAS = {LUCAS}")
    print(f"D10_CAPACITY = {D10_CAPACITY}")
    print(f"TOTAL_STATES = {TOTAL_STATES}")

    # Verify Lucas sum
    lucas_sum = sum(LUCAS)
    print(f"\nLucas sum: {lucas_sum} (expected {TOTAL_STATES})")
    assert lucas_sum == TOTAL_STATES, "Lucas sum mismatch!"

    # Display Lucas tiers
    print("\n--- Lucas Sampling Tiers ---")
    for tier in SamplingTier:
        print(f"  {tier.name:4s}: {tier.sample_size:3d} samples")

    # Create test dataset
    print("\n--- Creating Test Dataset ---")

    @dataclass
    class DataPoint:
        id: int
        category: str
        value: float

    # Generate 1000 data points across 5 categories
    categories = ["alpha", "beta", "gamma", "delta", "epsilon"]
    test_data = [
        DataPoint(
            id=i,
            category=categories[i % 5],
            value=random.random() * 100
        )
        for i in range(1000)
    ]
    print(f"  Created {len(test_data)} data points in {len(categories)} categories")

    # Initialize sampler
    sampler: DatasetSampler[DataPoint] = DatasetSampler(test_data)
    sampler.set_seed(42)  # Reproducibility

    # Create strata
    print("\n--- Creating Strata ---")
    strata = sampler.create_strata(
        key_func=lambda p: p.category,
        weight_func=lambda k: PHI ** categories.index(k)
    )
    for name, stratum in strata.items():
        print(f"  {name}: {stratum.size} items, weight={stratum.weight:.3f}")

    # Test different tiers
    print("\n--- Lucas-Stratified Sampling ---")
    test_tiers = [SamplingTier.L3, SamplingTier.L6, SamplingTier.L10, SamplingTier.L12]

    for tier in test_tiers:
        result = sampler.sample_lucas(tier, StratificationMethod.PHI_WEIGHTED)
        print(f"\n{tier.name} (target={result.target_size}, actual={result.actual_size}):")
        print(f"  Coverage: {result.coverage_ratio:.1%}")
        print(f"  PHI Balance: {result.phi_balance:.3f}")
        print(f"  Distribution: {result.strata_distribution}")

    # Test D10 (Wisdom) sampling
    print("\n--- D10 (Wisdom) Sampling ---")
    d10_result = sampler.sample_d10()
    print(f"  Target: {d10_result.target_size} (D10 capacity)")
    print(f"  Actual: {d10_result.actual_size}")
    print(f"  Coverage: {d10_result.coverage_ratio:.1%}")
    print(f"  PHI Balance: {d10_result.phi_balance:.3f}")

    # Test optimal tier finder
    print("\n--- Optimal Tier Selection ---")
    for coverage in [0.01, 0.05, 0.10, 0.25]:
        optimal = sampler.get_optimal_tier(coverage)
        print(f"  {coverage:.0%} coverage -> {optimal.name} ({optimal.sample_size} samples)")

    # Display coverage table
    print("\n--- Lucas Coverage Table ---")
    table = sampler.get_lucas_coverage_table()
    print(f"  Dataset size: {table['data_size']}")
    for tier_name, info in list(table["tiers"].items())[:6]:
        print(f"  {tier_name}: {info['sample_size']:3d} samples = {info['coverage_percent']:.1f}%")
    print("  ...")

    print("\n" + "=" * 60)
    print("Dataset Sampler Test Complete")
    print("=" * 60)
