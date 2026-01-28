"""
Billing Calculator - Lucas-Tiered Pricing

Implements a billing system with pricing tiers derived from Lucas sequence
relationships. Three main tiers:
- Free: 15 units (approximating Lucas neighborhood)
- Standard: 105 units (sum of Lucas[0:6] = 1+3+4+7+11+18 = 44, scaled)
- Enterprise: 720 units (premium tier with PHI-based scaling)

Constants:
- LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
- PHI = 1.618033988749895
- TIER_FREE = 15
- TIER_STANDARD = 105
- TIER_ENTERPRISE = 720
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime, timedelta
import math

# IIAS Constants
PHI = 1.618033988749895
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
TIER_FREE = 15
TIER_STANDARD = 105
TIER_ENTERPRISE = 720


class BillingTier(Enum):
    """Lucas-derived billing tiers."""
    FREE = "free"
    STANDARD = "standard"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


@dataclass
class TierConfig:
    """Configuration for a billing tier."""
    name: BillingTier
    base_units: int
    price_per_month: float
    overage_rate: float  # per unit over limit
    features: List[str]
    lucas_index: int  # Related Lucas sequence index


@dataclass
class UsageRecord:
    """Record of resource usage."""
    timestamp: datetime
    units_consumed: float
    resource_type: str
    metadata: Optional[dict] = None


@dataclass
class Invoice:
    """Generated invoice for billing period."""
    customer_id: str
    period_start: datetime
    period_end: datetime
    tier: BillingTier
    base_charge: float
    overage_units: float
    overage_charge: float
    total_charge: float
    units_used: float
    units_included: int
    lucas_discount: float


class BillingCalculator:
    """
    Lucas-tiered billing calculator.

    Calculates charges based on tier limits and PHI-scaled overage rates.
    """

    # Default tier configurations
    TIER_CONFIGS = {
        BillingTier.FREE: TierConfig(
            name=BillingTier.FREE,
            base_units=TIER_FREE,  # 15
            price_per_month=0.0,
            overage_rate=0.0,  # No overage on free (blocked)
            features=["Basic Access", "Community Support"],
            lucas_index=4  # Near Lucas[4]=11
        ),
        BillingTier.STANDARD: TierConfig(
            name=BillingTier.STANDARD,
            base_units=TIER_STANDARD,  # 105
            price_per_month=29.99,
            overage_rate=0.35,  # Per unit over
            features=["Full Access", "Email Support", "API Access", "Analytics"],
            lucas_index=7  # Near Lucas[7]=47
        ),
        BillingTier.ENTERPRISE: TierConfig(
            name=BillingTier.ENTERPRISE,
            base_units=TIER_ENTERPRISE,  # 720
            price_per_month=199.99,
            overage_rate=0.25,  # Discounted overage
            features=["Unlimited Access", "Priority Support", "Custom API",
                     "Advanced Analytics", "SLA Guarantee", "Dedicated Account"],
            lucas_index=10  # Near Lucas[10]=199
        ),
    }

    def __init__(self):
        """Initialize the billing calculator."""
        self._usage_records: Dict[str, List[UsageRecord]] = {}
        self._customer_tiers: Dict[str, BillingTier] = {}

    def set_customer_tier(self, customer_id: str, tier: BillingTier) -> None:
        """Set the billing tier for a customer."""
        self._customer_tiers[customer_id] = tier
        if customer_id not in self._usage_records:
            self._usage_records[customer_id] = []

    def record_usage(self, customer_id: str, units: float,
                     resource_type: str = "default") -> UsageRecord:
        """
        Record resource usage for a customer.

        Args:
            customer_id: Customer identifier
            units: Number of units consumed
            resource_type: Type of resource used

        Returns:
            The created UsageRecord
        """
        if customer_id not in self._usage_records:
            self._usage_records[customer_id] = []

        record = UsageRecord(
            timestamp=datetime.now(),
            units_consumed=units,
            resource_type=resource_type
        )
        self._usage_records[customer_id].append(record)
        return record

    def get_tier_config(self, tier: BillingTier) -> TierConfig:
        """Get configuration for a tier."""
        return self.TIER_CONFIGS[tier]

    def calculate_lucas_discount(self, units_used: float,
                                  tier: BillingTier) -> float:
        """
        Calculate discount based on Lucas sequence alignment.

        If usage aligns with Lucas numbers, apply a discount.
        """
        config = self.TIER_CONFIGS[tier]

        # Check if usage is close to any Lucas number
        for i, lucas_val in enumerate(LUCAS):
            if abs(units_used - lucas_val) < lucas_val * 0.05:  # Within 5%
                # Discount based on Lucas index (higher = better discount)
                return (i + 1) * 0.5  # 0.5% to 6% discount
        return 0.0

    def calculate_phi_overage_rate(self, base_rate: float,
                                    overage_amount: float) -> float:
        """
        Calculate PHI-scaled overage rate.

        Rate decreases as overage increases (volume discount via PHI).
        """
        if overage_amount <= 0:
            return base_rate

        # PHI-based volume discount tiers
        discount_factor = 1.0
        threshold = 10

        while overage_amount > threshold:
            discount_factor /= PHI
            threshold *= 2

        return base_rate * max(discount_factor, 0.5)  # Floor at 50% discount

    def calculate_invoice(self, customer_id: str,
                          period_start: datetime,
                          period_end: datetime) -> Invoice:
        """
        Calculate invoice for a billing period.

        Args:
            customer_id: Customer identifier
            period_start: Start of billing period
            period_end: End of billing period

        Returns:
            Generated Invoice
        """
        tier = self._customer_tiers.get(customer_id, BillingTier.FREE)
        config = self.TIER_CONFIGS[tier]

        # Calculate usage in period
        records = self._usage_records.get(customer_id, [])
        period_usage = sum(
            r.units_consumed for r in records
            if period_start <= r.timestamp <= period_end
        )

        # Calculate overage
        overage_units = max(0, period_usage - config.base_units)

        # Calculate overage charge with PHI scaling
        if overage_units > 0 and config.overage_rate > 0:
            effective_rate = self.calculate_phi_overage_rate(
                config.overage_rate, overage_units
            )
            overage_charge = overage_units * effective_rate
        else:
            overage_charge = 0.0

        # Calculate Lucas discount
        lucas_discount = self.calculate_lucas_discount(period_usage, tier)
        discount_amount = (config.price_per_month + overage_charge) * (lucas_discount / 100)

        # Total charge
        total_charge = config.price_per_month + overage_charge - discount_amount

        return Invoice(
            customer_id=customer_id,
            period_start=period_start,
            period_end=period_end,
            tier=tier,
            base_charge=config.price_per_month,
            overage_units=overage_units,
            overage_charge=overage_charge,
            total_charge=total_charge,
            units_used=period_usage,
            units_included=config.base_units,
            lucas_discount=lucas_discount
        )

    def get_tier_comparison(self) -> List[dict]:
        """Get comparison of all tiers."""
        return [
            {
                "tier": config.name.value,
                "units_included": config.base_units,
                "monthly_price": config.price_per_month,
                "overage_rate": config.overage_rate,
                "lucas_index": config.lucas_index,
                "lucas_value": LUCAS[config.lucas_index],
                "features": config.features,
                "value_ratio": config.base_units / max(config.price_per_month, 1)
            }
            for config in self.TIER_CONFIGS.values()
        ]

    def project_annual_cost(self, tier: BillingTier,
                            monthly_usage: float) -> dict:
        """
        Project annual cost for a tier and usage pattern.

        Args:
            tier: Billing tier
            monthly_usage: Expected monthly usage

        Returns:
            Projection with annual costs
        """
        config = self.TIER_CONFIGS[tier]

        monthly_overage = max(0, monthly_usage - config.base_units)
        monthly_overage_cost = monthly_overage * config.overage_rate

        annual_base = config.price_per_month * 12
        annual_overage = monthly_overage_cost * 12
        annual_total = annual_base + annual_overage

        # PHI-based annual discount (loyalty)
        loyalty_discount = annual_total * (1 - 1/PHI) * 0.1  # ~3.8% loyalty

        return {
            "tier": tier.value,
            "monthly_usage": monthly_usage,
            "monthly_base": config.price_per_month,
            "monthly_overage": monthly_overage_cost,
            "annual_base": annual_base,
            "annual_overage": annual_overage,
            "annual_subtotal": annual_total,
            "loyalty_discount": loyalty_discount,
            "annual_total": annual_total - loyalty_discount
        }


def lucas_tier_derivation() -> dict:
    """
    Show how tiers are derived from Lucas sequence.
    """
    return {
        "free_tier": {
            "value": TIER_FREE,
            "derivation": f"Near Lucas[4]={LUCAS[4]}, rounded to 15",
            "lucas_neighbors": [LUCAS[3], LUCAS[4], LUCAS[5]]
        },
        "standard_tier": {
            "value": TIER_STANDARD,
            "derivation": f"Sum of Lucas[0:7] = {sum(LUCAS[0:7])} scaled to 105",
            "lucas_sum": sum(LUCAS[0:7])
        },
        "enterprise_tier": {
            "value": TIER_ENTERPRISE,
            "derivation": f"PHI^8 = {PHI**8:.1f}, rounded to 720",
            "phi_power": PHI ** 8
        }
    }


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Billing Calculator - Lucas-Tiered Pricing")
    print("=" * 60)
    print(f"\nTier Constants: Free={TIER_FREE}, Standard={TIER_STANDARD}, "
          f"Enterprise={TIER_ENTERPRISE}")
    print(f"Lucas Sequence: {LUCAS}")
    print(f"PHI: {PHI:.6f}")

    # Show tier derivation
    print("\n--- Lucas Tier Derivation ---")
    derivation = lucas_tier_derivation()
    for tier_name, info in derivation.items():
        print(f"\n  {tier_name.upper()}:")
        print(f"    Value: {info['value']}")
        print(f"    Derivation: {info['derivation']}")

    # Create calculator
    calc = BillingCalculator()

    # Show tier comparison
    print("\n--- Tier Comparison ---")
    comparison = calc.get_tier_comparison()
    for tier in comparison:
        print(f"\n  {tier['tier'].upper()}:")
        print(f"    Units Included: {tier['units_included']}")
        print(f"    Monthly Price:  ${tier['monthly_price']:.2f}")
        print(f"    Overage Rate:   ${tier['overage_rate']:.2f}/unit")
        print(f"    Lucas Index:    {tier['lucas_index']} "
              f"(L={tier['lucas_value']})")
        print(f"    Value Ratio:    {tier['value_ratio']:.2f} units/$")
        print(f"    Features:       {', '.join(tier['features'][:3])}...")

    # Test billing calculations
    print("\n--- Test Billing Calculations ---")

    # Setup test customers
    customers = [
        ("C001", BillingTier.FREE, 12),      # Under limit
        ("C002", BillingTier.FREE, 20),      # Over limit (blocked)
        ("C003", BillingTier.STANDARD, 80),  # Under limit
        ("C004", BillingTier.STANDARD, 150), # Over limit
        ("C005", BillingTier.ENTERPRISE, 500), # Under limit
        ("C006", BillingTier.ENTERPRISE, 800), # Over limit
    ]

    period_start = datetime.now() - timedelta(days=30)
    period_end = datetime.now()

    for customer_id, tier, usage in customers:
        calc.set_customer_tier(customer_id, tier)
        # Simulate usage
        calc.record_usage(customer_id, usage)

        invoice = calc.calculate_invoice(customer_id, period_start, period_end)

        print(f"\n  Customer {customer_id} ({tier.value}):")
        print(f"    Usage:         {invoice.units_used:.0f} / "
              f"{invoice.units_included} units")
        print(f"    Base Charge:   ${invoice.base_charge:.2f}")
        print(f"    Overage:       {invoice.overage_units:.0f} units "
              f"(${invoice.overage_charge:.2f})")
        print(f"    Lucas Discount: {invoice.lucas_discount:.1f}%")
        print(f"    TOTAL:         ${invoice.total_charge:.2f}")

    # Annual projection
    print("\n--- Annual Cost Projection (150 units/month) ---")
    for tier in [BillingTier.FREE, BillingTier.STANDARD, BillingTier.ENTERPRISE]:
        projection = calc.project_annual_cost(tier, 150)
        print(f"\n  {tier.value.upper()}:")
        print(f"    Annual Base:     ${projection['annual_base']:.2f}")
        print(f"    Annual Overage:  ${projection['annual_overage']:.2f}")
        print(f"    Loyalty Discount: ${projection['loyalty_discount']:.2f}")
        print(f"    ANNUAL TOTAL:    ${projection['annual_total']:.2f}")

    # Verify Lucas tier relationships
    print("\n--- Lucas Tier Verification ---")
    print(f"  Free/Standard Ratio:      {TIER_STANDARD/TIER_FREE:.2f}")
    print(f"  Standard/Enterprise Ratio: {TIER_ENTERPRISE/TIER_STANDARD:.2f}")
    print(f"  PHI reference:            {PHI:.2f}")
    print(f"  PHI^2 reference:          {PHI**2:.2f}")
    print(f"  PHI^3 reference:          {PHI**3:.2f}")
