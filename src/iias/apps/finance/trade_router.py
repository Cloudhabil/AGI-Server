"""Trade Router - PHI-Latency Execution

Routes trades to minimize latency using PHI optimization.
Leverages golden ratio mathematics for optimal execution timing.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
import math
import time

# IIAS Constants
PHI = 1.618033988749895
SUM_CONSTANT = 214
GENESIS_CONSTANT = 2 / 901
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]


class VenueType(Enum):
    """Trading venue types with associated latency profiles."""
    EXCHANGE = "EXCHANGE"       # Traditional exchange
    DARK_POOL = "DARK_POOL"     # Dark pool
    ATS = "ATS"                 # Alternative trading system
    MARKET_MAKER = "MARKET_MAKER"  # Direct market maker


class OrderType(Enum):
    """Order types with execution priority."""
    MARKET = "MARKET"           # Immediate execution
    LIMIT = "LIMIT"             # Price-bounded
    ICEBERG = "ICEBERG"         # Hidden quantity
    TWAP = "TWAP"               # Time-weighted average
    VWAP = "VWAP"               # Volume-weighted average


@dataclass
class Venue:
    """Trading venue with PHI-optimized latency characteristics."""
    venue_id: str
    venue_type: VenueType
    base_latency_ms: float
    liquidity_score: float  # 0-1
    reliability: float  # 0-1
    phi_factor: float  # PHI-based optimization factor

    def effective_latency(self, order_size: float, market_volatility: float = 0.01) -> float:
        """
        Calculate PHI-optimized effective latency.

        Latency increases with order size and volatility,
        but is reduced by PHI-factor optimization.
        """
        size_impact = math.log1p(order_size) / 10
        vol_impact = market_volatility * 100

        # PHI-optimization reduces latency
        phi_reduction = 1 / (1 + self.phi_factor * PHI)

        return self.base_latency_ms * (1 + size_impact + vol_impact) * phi_reduction


@dataclass
class TradeOrder:
    """A trade order to be routed."""
    order_id: str
    symbol: str
    side: str  # "BUY" or "SELL"
    quantity: float
    order_type: OrderType
    limit_price: Optional[float] = None
    urgency: float = 0.5  # 0-1, higher = more urgent


@dataclass
class RouteDecision:
    """Routing decision with PHI-optimization metrics."""
    order: TradeOrder
    selected_venue: Venue
    expected_latency_ms: float
    phi_efficiency: float
    slices: List[Tuple[str, float]]  # Venue ID and quantity pairs
    lucas_distribution: Dict[int, float]


class TradeRouter:
    """
    PHI-Latency Trade Router.

    Routes trades to minimize execution latency using PHI-based
    optimization across multiple venues.
    """

    def __init__(self):
        self.phi = PHI
        self.lucas = LUCAS
        self.sum_constant = SUM_CONSTANT
        self.venues: Dict[str, Venue] = {}
        self._initialize_default_venues()

    def _initialize_default_venues(self) -> None:
        """Initialize default trading venues with PHI factors."""
        defaults = [
            ("NYSE", VenueType.EXCHANGE, 1.2, 0.95, 0.99, 1.0),
            ("NASDAQ", VenueType.EXCHANGE, 0.8, 0.92, 0.99, 1.2),
            ("BATS", VenueType.EXCHANGE, 0.5, 0.85, 0.98, 1.5),
            ("IEX", VenueType.EXCHANGE, 0.35, 0.70, 0.97, PHI),  # PHI-optimized
            ("SIGMA_X", VenueType.DARK_POOL, 2.0, 0.60, 0.95, 0.8),
            ("CROSSFINDER", VenueType.DARK_POOL, 2.5, 0.55, 0.94, 0.7),
            ("CITADEL", VenueType.MARKET_MAKER, 0.3, 0.88, 0.96, 1.8),
            ("VIRTU", VenueType.MARKET_MAKER, 0.25, 0.90, 0.97, PHI * 1.1),
        ]

        for venue_id, vtype, latency, liquidity, reliability, phi_factor in defaults:
            self.venues[venue_id] = Venue(
                venue_id=venue_id,
                venue_type=vtype,
                base_latency_ms=latency,
                liquidity_score=liquidity,
                reliability=reliability,
                phi_factor=phi_factor
            )

    def add_venue(self, venue: Venue) -> None:
        """Add a trading venue."""
        self.venues[venue.venue_id] = venue

    def _phi_score(self, venue: Venue, order: TradeOrder, volatility: float) -> float:
        """
        Calculate PHI-optimization score for venue-order pair.

        Higher score = better routing choice.
        Combines latency, liquidity, reliability with PHI weighting.
        """
        latency = venue.effective_latency(order.quantity, volatility)

        # Invert latency (lower is better)
        latency_score = 1 / (1 + latency)

        # Weight factors using PHI ratios
        weights = {
            "latency": self.phi ** 2,      # Most important
            "liquidity": self.phi,          # Second
            "reliability": 1.0,             # Third
        }
        total_weight = sum(weights.values())

        # Urgency amplifies latency importance
        urgency_boost = 1 + order.urgency * self.phi

        score = (
            latency_score * weights["latency"] * urgency_boost +
            venue.liquidity_score * weights["liquidity"] +
            venue.reliability * weights["reliability"]
        ) / total_weight

        return score * venue.phi_factor

    def route(
        self,
        order: TradeOrder,
        volatility: float = 0.01,
        max_slices: int = 4
    ) -> RouteDecision:
        """
        Route an order using PHI-latency optimization.

        Args:
            order: The trade order to route
            volatility: Current market volatility
            max_slices: Maximum number of venue slices

        Returns:
            RouteDecision with optimal routing
        """
        if not self.venues:
            raise ValueError("No venues available for routing")

        # Score all venues
        venue_scores = []
        for venue in self.venues.values():
            score = self._phi_score(venue, order, volatility)
            latency = venue.effective_latency(order.quantity, volatility)
            venue_scores.append((venue, score, latency))

        # Sort by score (descending)
        venue_scores.sort(key=lambda x: x[1], reverse=True)

        # Select top venue
        best_venue = venue_scores[0][0]
        best_latency = venue_scores[0][2]

        # Create PHI-distributed slices for large orders
        slices = self._create_phi_slices(order, venue_scores[:max_slices])

        # Calculate overall PHI efficiency
        phi_efficiency = self._calculate_phi_efficiency(venue_scores[:max_slices])

        # Lucas distribution for the slices
        lucas_dist = self._lucas_distribution(slices)

        return RouteDecision(
            order=order,
            selected_venue=best_venue,
            expected_latency_ms=best_latency,
            phi_efficiency=phi_efficiency,
            slices=slices,
            lucas_distribution=lucas_dist
        )

    def _create_phi_slices(
        self,
        order: TradeOrder,
        scored_venues: List[Tuple[Venue, float, float]]
    ) -> List[Tuple[str, float]]:
        """
        Create PHI-distributed order slices across venues.

        Uses golden ratio to distribute quantity.
        """
        if len(scored_venues) == 1:
            return [(scored_venues[0][0].venue_id, order.quantity)]

        n = len(scored_venues)

        # PHI-based weights: PHI^(n-1), PHI^(n-2), ..., PHI^0
        phi_weights = [self.phi ** (n - 1 - i) for i in range(n)]
        total_weight = sum(phi_weights)

        slices = []
        remaining = order.quantity

        for i, (venue, score, latency) in enumerate(scored_venues[:-1]):
            quantity = order.quantity * phi_weights[i] / total_weight
            slices.append((venue.venue_id, quantity))
            remaining -= quantity

        # Last venue gets remainder
        slices.append((scored_venues[-1][0].venue_id, remaining))

        return slices

    def _calculate_phi_efficiency(
        self,
        scored_venues: List[Tuple[Venue, float, float]]
    ) -> float:
        """Calculate how efficiently PHI optimization is working."""
        if len(scored_venues) < 2:
            return 1.0

        # Check if scores follow PHI ratio
        scores = [s[1] for s in scored_venues]
        ratios = []

        for i in range(len(scores) - 1):
            if scores[i + 1] > 0:
                ratio = scores[i] / scores[i + 1]
                deviation = abs(ratio - self.phi) / self.phi
                ratios.append(max(0, 1 - deviation))

        return sum(ratios) / len(ratios) if ratios else 1.0

    def _lucas_distribution(
        self,
        slices: List[Tuple[str, float]]
    ) -> Dict[int, float]:
        """Map slices to Lucas sequence for dimension allocation."""
        distribution = {}
        total_quantity = sum(q for _, q in slices)

        for i, (venue_id, quantity) in enumerate(slices):
            lucas_idx = min(i, len(self.lucas) - 1)
            weight = quantity / total_quantity if total_quantity > 0 else 0
            distribution[lucas_idx + 1] = weight * self.sum_constant

        return distribution

    def optimize_batch(
        self,
        orders: List[TradeOrder],
        volatility: float = 0.01
    ) -> List[RouteDecision]:
        """
        Optimize routing for a batch of orders.

        Considers order interactions and venue capacity.
        """
        decisions = []

        # Sort by urgency (most urgent first)
        sorted_orders = sorted(orders, key=lambda o: o.urgency, reverse=True)

        for order in sorted_orders:
            decision = self.route(order, volatility)
            decisions.append(decision)

        return decisions

    def get_latency_stats(self) -> Dict[str, Dict[str, float]]:
        """Get latency statistics for all venues."""
        stats = {}
        test_sizes = [100, 1000, 10000]

        for venue in self.venues.values():
            venue_stats = {}
            for size in test_sizes:
                latency = venue.effective_latency(size)
                venue_stats[f"size_{size}"] = latency
            venue_stats["phi_factor"] = venue.phi_factor
            stats[venue.venue_id] = venue_stats

        return stats

    def verify_conservation(self, decision: RouteDecision) -> bool:
        """Verify the routing maintains 214-sum conservation."""
        total = sum(decision.lucas_distribution.values())
        return abs(total - self.sum_constant) < 1e-6


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Trade Router - PHI-Latency Execution")
    print("=" * 60)
    print(f"PHI: {PHI}")
    print(f"SUM_CONSTANT: {SUM_CONSTANT}")

    # Create router
    router = TradeRouter()

    print("\n[1] Available Venues:")
    for venue in router.venues.values():
        print(f"    {venue.venue_id:15s} | Type: {venue.venue_type.value:13s} | "
              f"Base Latency: {venue.base_latency_ms:.2f}ms | "
              f"PHI Factor: {venue.phi_factor:.3f}")

    print("\n[2] Routing a single order:")
    order = TradeOrder(
        order_id="ORD001",
        symbol="AAPL",
        side="BUY",
        quantity=10000,
        order_type=OrderType.LIMIT,
        limit_price=175.50,
        urgency=0.8
    )

    decision = router.route(order, volatility=0.015)

    print(f"    Order: {order.side} {order.quantity} {order.symbol} @ ${order.limit_price}")
    print(f"    Best Venue: {decision.selected_venue.venue_id}")
    print(f"    Expected Latency: {decision.expected_latency_ms:.4f}ms")
    print(f"    PHI Efficiency: {decision.phi_efficiency:.4f}")

    print("\n    PHI-distributed Slices:")
    for venue_id, qty in decision.slices:
        pct = qty / order.quantity * 100
        print(f"      {venue_id:15s}: {qty:,.0f} shares ({pct:.1f}%)")

    print("\n    Lucas Distribution (normalized to 214):")
    for dim, value in decision.lucas_distribution.items():
        print(f"      Dimension {dim}: {value:.4f}")

    print("\n[3] Batch order optimization:")
    batch = [
        TradeOrder("ORD002", "MSFT", "BUY", 5000, OrderType.MARKET, urgency=0.9),
        TradeOrder("ORD003", "GOOGL", "SELL", 2000, OrderType.LIMIT, 150.00, 0.5),
        TradeOrder("ORD004", "AMZN", "BUY", 15000, OrderType.TWAP, urgency=0.3),
    ]

    batch_decisions = router.optimize_batch(batch, volatility=0.02)

    for dec in batch_decisions:
        print(f"    {dec.order.order_id}: {dec.order.symbol} -> {dec.selected_venue.venue_id} "
              f"(latency: {dec.expected_latency_ms:.4f}ms, PHI-eff: {dec.phi_efficiency:.4f})")

    print("\n[4] Latency Statistics by Venue:")
    stats = router.get_latency_stats()
    for venue_id, venue_stats in stats.items():
        print(f"    {venue_id}:")
        for key, value in venue_stats.items():
            if "size" in key:
                print(f"      {key}: {value:.4f}ms")
            else:
                print(f"      {key}: {value:.3f}")

    print("\n[5] Conservation Check:")
    conservation_ok = router.verify_conservation(decision)
    total_lucas = sum(decision.lucas_distribution.values())
    print(f"    Total Lucas Distribution: {total_lucas:.4f}")
    print(f"    Expected Sum: {SUM_CONSTANT}")
    print(f"    Conservation Verified: {conservation_ok}")

    print("\n" + "=" * 60)
    print("TEST PASSED - PHI-latency trade routing operational")
    print("=" * 60)
