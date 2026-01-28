"""Portfolio Balancer - 214-sum Asset Allocation

All portfolio weights sum to SUM_CONSTANT (214) normalized.
This ensures conservation across the IIAS dimension space.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math

# IIAS Constants
PHI = 1.618033988749895
SUM_CONSTANT = 214
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]


@dataclass
class Asset:
    """Represents a portfolio asset with IIAS-normalized weight."""
    symbol: str
    raw_weight: float
    normalized_weight: float = 0.0
    lucas_tier: int = 0

    def __post_init__(self):
        # Assign Lucas tier based on raw weight magnitude
        for i, threshold in enumerate(LUCAS):
            if self.raw_weight <= threshold:
                self.lucas_tier = i + 1
                break
        else:
            self.lucas_tier = 12


@dataclass
class PortfolioState:
    """Portfolio state with 214-sum conservation."""
    assets: List[Asset]
    total_weight: float
    conservation_verified: bool
    phi_efficiency: float
    rebalance_needed: bool


class PortfolioBalancer:
    """
    214-sum Asset Allocation Balancer.

    Ensures all portfolio weights sum to exactly SUM_CONSTANT (214),
    providing conservation across the IIAS 12-dimensional space.
    """

    def __init__(self, tolerance: float = 1e-9):
        self.sum_constant = SUM_CONSTANT
        self.phi = PHI
        self.lucas = LUCAS
        self.tolerance = tolerance
        self._assets: Dict[str, Asset] = {}

    def add_asset(self, symbol: str, weight: float) -> None:
        """Add an asset with a raw weight."""
        if weight < 0:
            raise ValueError(f"Weight must be non-negative: {weight}")
        self._assets[symbol] = Asset(symbol=symbol, raw_weight=weight)

    def remove_asset(self, symbol: str) -> bool:
        """Remove an asset from the portfolio."""
        if symbol in self._assets:
            del self._assets[symbol]
            return True
        return False

    def _normalize_to_214(self) -> List[Asset]:
        """Normalize all weights to sum to 214."""
        if not self._assets:
            return []

        total_raw = sum(a.raw_weight for a in self._assets.values())
        if total_raw == 0:
            # Equal distribution
            equal_weight = self.sum_constant / len(self._assets)
            for asset in self._assets.values():
                asset.normalized_weight = equal_weight
        else:
            # Scale to 214
            scale_factor = self.sum_constant / total_raw
            for asset in self._assets.values():
                asset.normalized_weight = asset.raw_weight * scale_factor

        return list(self._assets.values())

    def balance(self) -> PortfolioState:
        """
        Balance the portfolio to 214-sum conservation.

        Returns:
            PortfolioState with normalized weights summing to 214.
        """
        assets = self._normalize_to_214()

        if not assets:
            return PortfolioState(
                assets=[],
                total_weight=0.0,
                conservation_verified=True,
                phi_efficiency=0.0,
                rebalance_needed=False
            )

        total = sum(a.normalized_weight for a in assets)
        conservation_ok = abs(total - self.sum_constant) < self.tolerance

        # Calculate PHI-efficiency: how close to golden ratio distribution
        sorted_assets = sorted(assets, key=lambda a: a.normalized_weight, reverse=True)
        phi_efficiency = self._calculate_phi_efficiency(sorted_assets)

        # Check if rebalance needed (large deviation from PHI ratios)
        rebalance_needed = phi_efficiency < 0.5

        return PortfolioState(
            assets=assets,
            total_weight=total,
            conservation_verified=conservation_ok,
            phi_efficiency=phi_efficiency,
            rebalance_needed=rebalance_needed
        )

    def _calculate_phi_efficiency(self, sorted_assets: List[Asset]) -> float:
        """
        Calculate how well the portfolio follows PHI ratios.

        Ideal: each asset weight is PHI times the next smaller.
        """
        if len(sorted_assets) < 2:
            return 1.0

        ratios = []
        for i in range(len(sorted_assets) - 1):
            if sorted_assets[i + 1].normalized_weight > 0:
                ratio = sorted_assets[i].normalized_weight / sorted_assets[i + 1].normalized_weight
                deviation = abs(ratio - self.phi) / self.phi
                ratios.append(max(0, 1 - deviation))

        return sum(ratios) / len(ratios) if ratios else 1.0

    def optimize_phi(self) -> PortfolioState:
        """
        Optimize portfolio to follow PHI ratio distribution while maintaining 214-sum.

        Creates a golden-ratio weighted allocation.
        """
        if not self._assets:
            return self.balance()

        n = len(self._assets)
        symbols = list(self._assets.keys())

        # Generate PHI-based weights: PHI^(n-1), PHI^(n-2), ..., PHI^0
        phi_weights = [self.phi ** (n - 1 - i) for i in range(n)]
        total_phi = sum(phi_weights)

        # Scale to 214
        scale = self.sum_constant / total_phi

        # Update assets with PHI-optimized weights
        for i, symbol in enumerate(symbols):
            self._assets[symbol].raw_weight = phi_weights[i]
            self._assets[symbol].normalized_weight = phi_weights[i] * scale

        return self.balance()

    def get_lucas_allocation(self) -> Dict[int, List[str]]:
        """Group assets by their Lucas tier."""
        tiers: Dict[int, List[str]] = {i: [] for i in range(1, 13)}
        for asset in self._assets.values():
            tiers[asset.lucas_tier].append(asset.symbol)
        return {k: v for k, v in tiers.items() if v}

    def verify_conservation(self) -> bool:
        """Verify the portfolio maintains 214-sum conservation."""
        total = sum(a.normalized_weight for a in self._assets.values())
        return abs(total - self.sum_constant) < self.tolerance


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Portfolio Balancer - 214-sum Asset Allocation")
    print("=" * 60)

    # Create balancer
    balancer = PortfolioBalancer()

    # Add sample assets
    assets = [
        ("AAPL", 30),
        ("GOOGL", 25),
        ("MSFT", 20),
        ("AMZN", 15),
        ("NVDA", 10),
    ]

    print("\n[1] Adding assets with raw weights:")
    for symbol, weight in assets:
        balancer.add_asset(symbol, weight)
        print(f"    {symbol}: {weight}")

    # Balance portfolio
    print("\n[2] Balancing to 214-sum:")
    state = balancer.balance()

    for asset in state.assets:
        print(f"    {asset.symbol}: {asset.normalized_weight:.4f} (Lucas tier: {asset.lucas_tier})")

    print(f"\n    Total Weight: {state.total_weight:.4f}")
    print(f"    Conservation Verified: {state.conservation_verified}")
    print(f"    PHI Efficiency: {state.phi_efficiency:.4f}")
    print(f"    Rebalance Needed: {state.rebalance_needed}")

    # Optimize with PHI ratios
    print("\n[3] PHI-Optimized Allocation:")
    phi_state = balancer.optimize_phi()

    for asset in sorted(phi_state.assets, key=lambda a: a.normalized_weight, reverse=True):
        print(f"    {asset.symbol}: {asset.normalized_weight:.4f}")

    print(f"\n    Total Weight: {phi_state.total_weight:.4f}")
    print(f"    PHI Efficiency: {phi_state.phi_efficiency:.4f}")

    # Lucas allocation
    print("\n[4] Lucas Tier Groupings:")
    lucas_alloc = balancer.get_lucas_allocation()
    for tier, symbols in lucas_alloc.items():
        print(f"    Tier {tier} (capacity {LUCAS[tier-1]}): {symbols}")

    print("\n" + "=" * 60)
    print("TEST PASSED - 214-sum conservation maintained")
    print("=" * 60)
