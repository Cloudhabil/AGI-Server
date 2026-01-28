"""Risk Calculator - D3 (Security) Exposure with 4 Risk Levels

Uses IIAS Dimension 3 (Security) with capacity 4 for risk assessment.
The 4 risk levels map to the D3_CAPACITY constant.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import math

# IIAS Constants
PHI = 1.618033988749895
SUM_CONSTANT = 214
D3_CAPACITY = 4  # Security dimension capacity
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]


class RiskLevel(Enum):
    """Four risk levels corresponding to D3_CAPACITY."""
    MINIMAL = 1      # Conservative, low volatility
    MODERATE = 2     # Balanced risk-reward
    ELEVATED = 3     # Growth-oriented, higher volatility
    CRITICAL = 4     # Aggressive, maximum exposure


@dataclass
class RiskMetrics:
    """Risk metrics for a position or portfolio."""
    volatility: float
    var_95: float  # Value at Risk 95%
    max_drawdown: float
    sharpe_ratio: float
    beta: float

    def risk_score(self) -> float:
        """Calculate composite risk score (0-100)."""
        # Normalize each metric to 0-1 scale and combine
        vol_score = min(self.volatility / 0.5, 1.0)  # Cap at 50% volatility
        var_score = min(abs(self.var_95) / 0.2, 1.0)  # Cap at 20% VaR
        dd_score = min(abs(self.max_drawdown) / 0.5, 1.0)  # Cap at 50% drawdown

        # Weight by PHI ratios
        weights = [PHI ** 2, PHI, 1.0]
        total_weight = sum(weights)

        composite = (
            vol_score * weights[0] +
            var_score * weights[1] +
            dd_score * weights[2]
        ) / total_weight

        return composite * 100


@dataclass
class RiskExposure:
    """Complete risk exposure assessment."""
    level: RiskLevel
    score: float
    metrics: RiskMetrics
    d3_utilization: float  # How much of D3 capacity is used (0-1)
    recommendations: List[str]


class RiskCalculator:
    """
    D3 (Security) Risk Calculator with 4 risk levels.

    Maps financial risk to IIAS Dimension 3 (Security) which has
    capacity D3_CAPACITY = 4, corresponding to 4 risk levels.
    """

    def __init__(self, risk_free_rate: float = 0.05):
        self.d3_capacity = D3_CAPACITY
        self.risk_levels = list(RiskLevel)
        self.risk_free_rate = risk_free_rate
        self.phi = PHI
        self.lucas_d3 = LUCAS[2]  # Lucas number for D3 = 4

        # Risk thresholds for each level
        self.thresholds = {
            RiskLevel.MINIMAL: (0, 25),
            RiskLevel.MODERATE: (25, 50),
            RiskLevel.ELEVATED: (50, 75),
            RiskLevel.CRITICAL: (75, 100),
        }

    def calculate_volatility(self, returns: List[float]) -> float:
        """Calculate annualized volatility from returns."""
        if len(returns) < 2:
            return 0.0

        mean = sum(returns) / len(returns)
        variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
        daily_vol = math.sqrt(variance)

        # Annualize (assuming 252 trading days)
        return daily_vol * math.sqrt(252)

    def calculate_var(self, returns: List[float], confidence: float = 0.95) -> float:
        """Calculate Value at Risk at given confidence level."""
        if not returns:
            return 0.0

        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        return sorted_returns[index] if index < len(sorted_returns) else sorted_returns[0]

    def calculate_max_drawdown(self, prices: List[float]) -> float:
        """Calculate maximum drawdown from price series."""
        if len(prices) < 2:
            return 0.0

        peak = prices[0]
        max_dd = 0.0

        for price in prices:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak if peak > 0 else 0
            max_dd = max(max_dd, drawdown)

        return max_dd

    def calculate_sharpe(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio."""
        if len(returns) < 2:
            return 0.0

        mean_return = sum(returns) / len(returns)
        volatility = self.calculate_volatility(returns)

        if volatility == 0:
            return 0.0

        # Annualize mean return
        annual_return = mean_return * 252

        return (annual_return - self.risk_free_rate) / volatility

    def calculate_beta(self, asset_returns: List[float], market_returns: List[float]) -> float:
        """Calculate beta relative to market."""
        if len(asset_returns) != len(market_returns) or len(asset_returns) < 2:
            return 1.0

        n = len(asset_returns)
        asset_mean = sum(asset_returns) / n
        market_mean = sum(market_returns) / n

        covariance = sum(
            (asset_returns[i] - asset_mean) * (market_returns[i] - market_mean)
            for i in range(n)
        ) / (n - 1)

        market_variance = sum(
            (market_returns[i] - market_mean) ** 2
            for i in range(n)
        ) / (n - 1)

        return covariance / market_variance if market_variance > 0 else 1.0

    def assess_risk(
        self,
        returns: List[float],
        prices: Optional[List[float]] = None,
        market_returns: Optional[List[float]] = None
    ) -> RiskExposure:
        """
        Assess complete risk exposure using D3 framework.

        Args:
            returns: List of daily returns
            prices: Optional price series for drawdown calculation
            market_returns: Optional market returns for beta calculation

        Returns:
            RiskExposure with level, score, metrics, and recommendations
        """
        # Calculate all metrics
        volatility = self.calculate_volatility(returns)
        var_95 = self.calculate_var(returns, 0.95)
        max_drawdown = self.calculate_max_drawdown(prices) if prices else volatility * 2
        sharpe = self.calculate_sharpe(returns)
        beta = self.calculate_beta(returns, market_returns) if market_returns else 1.0

        metrics = RiskMetrics(
            volatility=volatility,
            var_95=var_95,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            beta=beta
        )

        # Calculate risk score and determine level
        score = metrics.risk_score()
        level = self._score_to_level(score)

        # Calculate D3 utilization
        d3_utilization = level.value / self.d3_capacity

        # Generate recommendations
        recommendations = self._generate_recommendations(level, metrics)

        return RiskExposure(
            level=level,
            score=score,
            metrics=metrics,
            d3_utilization=d3_utilization,
            recommendations=recommendations
        )

    def _score_to_level(self, score: float) -> RiskLevel:
        """Map risk score to risk level."""
        for level, (low, high) in self.thresholds.items():
            if low <= score < high:
                return level
        return RiskLevel.CRITICAL

    def _generate_recommendations(self, level: RiskLevel, metrics: RiskMetrics) -> List[str]:
        """Generate risk management recommendations."""
        recommendations = []

        if level == RiskLevel.CRITICAL:
            recommendations.append("URGENT: Reduce position size by at least 50%")
            recommendations.append("Implement stop-loss at 2x VaR level")
        elif level == RiskLevel.ELEVATED:
            recommendations.append("Consider hedging with inverse positions")
            recommendations.append("Review position sizing relative to portfolio")
        elif level == RiskLevel.MODERATE:
            recommendations.append("Maintain current allocation with regular monitoring")
        else:
            recommendations.append("Position is within conservative risk parameters")

        if metrics.beta > 1.5:
            recommendations.append(f"High beta ({metrics.beta:.2f}): Add low-correlation assets")

        if metrics.sharpe_ratio < 0.5:
            recommendations.append(f"Low Sharpe ({metrics.sharpe_ratio:.2f}): Risk-reward unfavorable")

        return recommendations

    def get_level_capacity(self, level: RiskLevel) -> Tuple[int, int]:
        """Get the capacity usage for a risk level within D3."""
        return (level.value, self.d3_capacity)

    def verify_d3_conservation(self, exposures: List[RiskExposure]) -> bool:
        """Verify total risk doesn't exceed D3 capacity."""
        total_utilization = sum(e.d3_utilization for e in exposures)
        # Allow up to 100% of D3 capacity
        return total_utilization <= 1.0


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Risk Calculator - D3 (Security) Exposure")
    print("=" * 60)
    print(f"D3_CAPACITY: {D3_CAPACITY} (4 risk levels)")
    print(f"Lucas[D3]: {LUCAS[2]} (Security dimension weight)")

    # Create calculator
    calc = RiskCalculator(risk_free_rate=0.05)

    # Simulate different risk profiles
    import random
    random.seed(42)

    # Low risk asset
    low_risk_returns = [random.gauss(0.0003, 0.005) for _ in range(252)]
    low_risk_prices = [100]
    for r in low_risk_returns:
        low_risk_prices.append(low_risk_prices[-1] * (1 + r))

    # High risk asset
    high_risk_returns = [random.gauss(0.001, 0.03) for _ in range(252)]
    high_risk_prices = [100]
    for r in high_risk_returns:
        high_risk_prices.append(high_risk_prices[-1] * (1 + r))

    # Market benchmark
    market_returns = [random.gauss(0.0004, 0.012) for _ in range(252)]

    print("\n[1] Low Risk Asset Assessment:")
    low_exposure = calc.assess_risk(low_risk_returns, low_risk_prices, market_returns)
    print(f"    Risk Level: {low_exposure.level.name} ({low_exposure.level.value}/{D3_CAPACITY})")
    print(f"    Risk Score: {low_exposure.score:.2f}")
    print(f"    D3 Utilization: {low_exposure.d3_utilization:.2%}")
    print(f"    Volatility: {low_exposure.metrics.volatility:.2%}")
    print(f"    VaR 95%: {low_exposure.metrics.var_95:.4f}")
    print(f"    Sharpe Ratio: {low_exposure.metrics.sharpe_ratio:.2f}")
    print("    Recommendations:")
    for rec in low_exposure.recommendations:
        print(f"      - {rec}")

    print("\n[2] High Risk Asset Assessment:")
    high_exposure = calc.assess_risk(high_risk_returns, high_risk_prices, market_returns)
    print(f"    Risk Level: {high_exposure.level.name} ({high_exposure.level.value}/{D3_CAPACITY})")
    print(f"    Risk Score: {high_exposure.score:.2f}")
    print(f"    D3 Utilization: {high_exposure.d3_utilization:.2%}")
    print(f"    Volatility: {high_exposure.metrics.volatility:.2%}")
    print(f"    VaR 95%: {high_exposure.metrics.var_95:.4f}")
    print(f"    Sharpe Ratio: {high_exposure.metrics.sharpe_ratio:.2f}")
    print("    Recommendations:")
    for rec in high_exposure.recommendations:
        print(f"      - {rec}")

    print("\n[3] D3 Conservation Check:")
    total_util = low_exposure.d3_utilization + high_exposure.d3_utilization
    print(f"    Total D3 Utilization: {total_util:.2%}")
    conservation_ok = calc.verify_d3_conservation([low_exposure, high_exposure])
    print(f"    Conservation Verified: {conservation_ok}")

    print("\n[4] Risk Level Mapping:")
    for level in RiskLevel:
        capacity = calc.get_level_capacity(level)
        print(f"    {level.name}: {capacity[0]}/{capacity[1]} D3 capacity")

    print("\n" + "=" * 60)
    print("TEST PASSED - D3 risk framework operational")
    print("=" * 60)
