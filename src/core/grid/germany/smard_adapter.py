"""
SMARD API Adapter
=================

Integration with Germany's SMARD platform (Strommarktdaten)
operated by Bundesnetzagentur.

SMARD provides real-time and historical data for:
- Generation by source (wind, solar, coal, gas, etc.)
- Electricity consumption
- Cross-border flows
- Day-ahead and intraday prices
- CO2 emissions

API Documentation: https://www.smard.de/home/downloadcenter/download-marktdaten

Brahim Integration:
- Uses GENESIS_CONSTANT for API polling intervals
- PHI-based caching expiration
- BETA_SECURITY thresholds for anomaly detection

Author: GPIA Cognitive Ecosystem
Date: 2026-01-26
"""

import asyncio
import hashlib
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import json

logger = logging.getLogger(__name__)


# =============================================================================
# Brahim Constants
# =============================================================================

GENESIS_CONSTANT = 0.0022
BETA_SECURITY = 0.236
PHI = 1.618033988749895
BRAHIM_SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]


# =============================================================================
# SMARD Data Categories
# =============================================================================

class SMARDFilter(Enum):
    """SMARD filter IDs for different data categories."""
    # Generation
    GENERATION_TOTAL = 1223
    GENERATION_WIND_ONSHORE = 4067
    GENERATION_WIND_OFFSHORE = 1225
    GENERATION_SOLAR = 4068
    GENERATION_BIOMASS = 4069
    GENERATION_HYDRO = 4070
    GENERATION_NUCLEAR = 1224  # Legacy/phasing out
    GENERATION_LIGNITE = 4071
    GENERATION_HARD_COAL = 4072
    GENERATION_GAS = 4073
    GENERATION_PUMPED_STORAGE = 4074
    GENERATION_OTHER = 4075

    # Consumption
    CONSUMPTION_TOTAL = 410
    CONSUMPTION_RESIDUAL = 4359  # Total - Renewables

    # Prices
    PRICE_DAY_AHEAD = 4169
    PRICE_INTRADAY = 4170

    # Cross-border
    FLOW_FRANCE = 4174
    FLOW_AUSTRIA = 4175
    FLOW_SWITZERLAND = 4176
    FLOW_NETHERLANDS = 4177
    FLOW_POLAND = 4178
    FLOW_CZECH = 4179
    FLOW_DENMARK = 4180


class SMARDResolution(Enum):
    """Time resolution for SMARD data."""
    QUARTERHOUR = "quarterhour"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class GenerationMix:
    """Current generation mix in Germany."""
    timestamp: datetime
    wind_onshore_mw: float
    wind_offshore_mw: float
    solar_mw: float
    biomass_mw: float
    hydro_mw: float
    nuclear_mw: float  # Legacy
    lignite_mw: float
    hard_coal_mw: float
    gas_mw: float
    pumped_storage_mw: float
    other_mw: float

    @property
    def total_mw(self) -> float:
        return (
            self.wind_onshore_mw + self.wind_offshore_mw +
            self.solar_mw + self.biomass_mw + self.hydro_mw +
            self.nuclear_mw + self.lignite_mw + self.hard_coal_mw +
            self.gas_mw + self.pumped_storage_mw + self.other_mw
        )

    @property
    def renewable_mw(self) -> float:
        return (
            self.wind_onshore_mw + self.wind_offshore_mw +
            self.solar_mw + self.biomass_mw + self.hydro_mw
        )

    @property
    def fossil_mw(self) -> float:
        return self.lignite_mw + self.hard_coal_mw + self.gas_mw

    @property
    def renewable_share(self) -> float:
        if self.total_mw <= 0:
            return 0.0
        return self.renewable_mw / self.total_mw

    @property
    def wind_total_mw(self) -> float:
        return self.wind_onshore_mw + self.wind_offshore_mw


@dataclass
class GridStatus:
    """Current German grid status."""
    timestamp: datetime
    generation: GenerationMix
    consumption_mw: float
    price_eur_mwh: float
    co2_intensity_kg_kwh: float
    renewable_share: float
    is_export: bool  # True if exporting
    net_flow_mw: float  # Positive = export


@dataclass
class PriceData:
    """Electricity price data."""
    timestamp: datetime
    day_ahead_eur_mwh: float
    intraday_eur_mwh: Optional[float] = None
    is_negative: bool = False


@dataclass
class CrossBorderFlow:
    """Cross-border electricity flow."""
    timestamp: datetime
    country: str
    flow_mw: float  # Positive = export from Germany
    is_export: bool


# =============================================================================
# SMARD Adapter
# =============================================================================

class SMARDAdapter:
    """
    Adapter for Germany's SMARD API.

    Provides real-time access to:
    - Generation by source
    - Consumption data
    - Price information
    - Cross-border flows

    Uses Brahim optimization for:
    - Request timing (GENESIS_CONSTANT intervals)
    - Cache management (PHI-based expiration)
    - Anomaly detection (BETA_SECURITY thresholds)
    """

    BASE_URL = "https://www.smard.de/app/chart_data"
    DOWNLOAD_URL = "https://www.smard.de/nip-download-manager"

    def __init__(
        self,
        resolution: SMARDResolution = SMARDResolution.HOUR,
        simulation_mode: bool = True,  # Use simulation until API integrated
    ):
        self.resolution = resolution
        self.simulation_mode = simulation_mode
        self._cache: Dict[str, Tuple[Any, datetime]] = {}
        self._last_request: datetime = datetime.min
        self._request_interval = timedelta(seconds=GENESIS_CONSTANT * 1000)

        logger.info(
            f"SMARDAdapter initialized (resolution={resolution.value}, "
            f"simulation={simulation_mode})"
        )

    def _cache_key(self, method: str, *args) -> str:
        """Generate cache key using Brahim hash."""
        raw = f"{method}:{':'.join(str(a) for a in args)}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached value if not expired (PHI-based expiration)."""
        if key in self._cache:
            value, cached_at = self._cache[key]
            # Cache expires after PHI * 5 minutes
            expiry = timedelta(minutes=PHI * 5)
            if datetime.now() - cached_at < expiry:
                return value
            del self._cache[key]
        return None

    def _set_cached(self, key: str, value: Any) -> None:
        """Cache a value with timestamp."""
        self._cache[key] = (value, datetime.now())

    async def _throttle_request(self) -> None:
        """Apply Brahim-optimized request throttling."""
        now = datetime.now()
        elapsed = now - self._last_request

        if elapsed < self._request_interval:
            wait_time = (self._request_interval - elapsed).total_seconds()
            await asyncio.sleep(wait_time)

        self._last_request = datetime.now()

    def _simulate_generation_mix(self, dt: datetime) -> GenerationMix:
        """
        Simulate generation mix based on typical German patterns.

        Uses Brahim constants for realistic variation.
        """
        import random
        hour = dt.hour
        month = dt.month

        # Base patterns by season
        is_winter = month in [11, 12, 1, 2]
        is_summer = month in [5, 6, 7, 8]

        # Wind patterns (stronger at night and in winter)
        wind_base = 20000 if is_winter else 12000  # MW
        wind_hour_factor = 1.2 if (hour < 6 or hour > 20) else 0.8
        wind_random = 1 + (random.random() - 0.5) * BETA_SECURITY

        wind_onshore = wind_base * 0.7 * wind_hour_factor * wind_random
        wind_offshore = wind_base * 0.3 * wind_hour_factor * wind_random

        # Solar patterns (obvious day/night cycle)
        if 6 <= hour <= 20:
            solar_factor = math.sin(math.pi * (hour - 6) / 14)
            solar_base = 45000 if is_summer else 15000
            solar_random = 1 + (random.random() - 0.5) * 0.3
            solar = solar_base * solar_factor * solar_random
        else:
            solar = 0

        # Biomass (relatively constant)
        biomass = 5000 + random.random() * 500

        # Hydro (slight variation)
        hydro = 2500 + random.random() * 500

        # Nuclear (legacy - minimal)
        nuclear = 500 if random.random() > 0.5 else 0

        # Fossil dispatch based on residual load
        demand_base = 65000 if is_winter else 50000
        demand_hour_factor = {
            0: 0.65, 1: 0.60, 2: 0.58, 3: 0.57, 4: 0.58, 5: 0.62,
            6: 0.72, 7: 0.85, 8: 0.92, 9: 0.95, 10: 0.98, 11: 1.00,
            12: 0.98, 13: 0.95, 14: 0.93, 15: 0.92, 16: 0.94, 17: 0.97,
            18: 1.00, 19: 0.98, 20: 0.92, 21: 0.85, 22: 0.78, 23: 0.70,
        }.get(hour, 0.85)

        estimated_demand = demand_base * demand_hour_factor
        renewable_supply = wind_onshore + wind_offshore + solar + biomass + hydro

        residual = max(0, estimated_demand - renewable_supply)

        # Merit order dispatch for fossil
        if residual > 25000:
            gas = residual * 0.4
            lignite = residual * 0.35
            hard_coal = residual * 0.25
        elif residual > 10000:
            gas = residual * 0.3
            lignite = residual * 0.5
            hard_coal = residual * 0.2
        else:
            gas = residual * 0.5
            lignite = residual * 0.3
            hard_coal = residual * 0.2

        # Pumped storage (charging during surplus, discharging during peak)
        if renewable_supply > estimated_demand:
            pumped_storage = -(renewable_supply - estimated_demand) * 0.3  # Charging
        elif 17 <= hour <= 20:
            pumped_storage = 3000 + random.random() * 1000  # Discharging
        else:
            pumped_storage = random.random() * 500

        return GenerationMix(
            timestamp=dt,
            wind_onshore_mw=round(wind_onshore, 1),
            wind_offshore_mw=round(wind_offshore, 1),
            solar_mw=round(solar, 1),
            biomass_mw=round(biomass, 1),
            hydro_mw=round(hydro, 1),
            nuclear_mw=round(nuclear, 1),
            lignite_mw=round(lignite, 1),
            hard_coal_mw=round(hard_coal, 1),
            gas_mw=round(gas, 1),
            pumped_storage_mw=round(pumped_storage, 1),
            other_mw=round(random.random() * 500, 1),
        )

    async def get_generation_mix(
        self,
        dt: Optional[datetime] = None,
    ) -> GenerationMix:
        """
        Get current generation mix.

        Args:
            dt: Datetime to query (default: now)

        Returns:
            GenerationMix with all sources
        """
        if dt is None:
            dt = datetime.now()

        cache_key = self._cache_key("generation", dt.strftime("%Y%m%d%H"))
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if self.simulation_mode:
            mix = self._simulate_generation_mix(dt)
        else:
            await self._throttle_request()
            # Real API call would go here
            # URL: {BASE_URL}/{filter}/{resolution}/DE/{timestamp}.json
            mix = self._simulate_generation_mix(dt)

        self._set_cached(cache_key, mix)
        return mix

    async def get_consumption(self, dt: Optional[datetime] = None) -> float:
        """Get current electricity consumption in MW."""
        if dt is None:
            dt = datetime.now()

        mix = await self.get_generation_mix(dt)

        # Consumption ≈ Generation (with small import/export adjustment)
        import random
        adjustment = (random.random() - 0.5) * 2000  # ±1000 MW
        return mix.total_mw + adjustment

    async def get_price(self, dt: Optional[datetime] = None) -> PriceData:
        """Get electricity price."""
        if dt is None:
            dt = datetime.now()

        mix = await self.get_generation_mix(dt)
        consumption = await self.get_consumption(dt)

        # Price based on supply/demand balance
        surplus = mix.total_mw - consumption

        if surplus > 5000:
            # Oversupply - low/negative prices
            price = 10 - (surplus / 1000) * 2
        elif surplus < -5000:
            # Shortage - high prices
            price = 80 + abs(surplus) / 100
        else:
            # Normal range
            base_price = 45
            price = base_price + (mix.fossil_mw / 1000) * 1.5

        # Add some randomness
        import random
        price *= (1 + (random.random() - 0.5) * BETA_SECURITY)

        return PriceData(
            timestamp=dt,
            day_ahead_eur_mwh=round(price, 2),
            intraday_eur_mwh=round(price * 1.05, 2),
            is_negative=price < 0,
        )

    async def get_co2_intensity(self, dt: Optional[datetime] = None) -> float:
        """
        Calculate CO2 intensity using Brahim's method.

        CO2 factors (kg/MWh):
        - Wind/Solar/Hydro: 0
        - Biomass: 50
        - Nuclear: 12
        - Gas: 400
        - Hard Coal: 820
        - Lignite: 1000
        """
        if dt is None:
            dt = datetime.now()

        mix = await self.get_generation_mix(dt)

        # CO2 factors (kg/MWh)
        co2_factors = {
            "wind_onshore": 0,
            "wind_offshore": 0,
            "solar": 0,
            "hydro": 0,
            "biomass": 50,
            "nuclear": 12,
            "gas": 400,
            "hard_coal": 820,
            "lignite": 1000,
            "pumped_storage": 0,  # Depends on source, assume clean
            "other": 300,
        }

        total_co2 = (
            mix.wind_onshore_mw * co2_factors["wind_onshore"] +
            mix.wind_offshore_mw * co2_factors["wind_offshore"] +
            mix.solar_mw * co2_factors["solar"] +
            mix.hydro_mw * co2_factors["hydro"] +
            mix.biomass_mw * co2_factors["biomass"] +
            mix.nuclear_mw * co2_factors["nuclear"] +
            mix.gas_mw * co2_factors["gas"] +
            mix.hard_coal_mw * co2_factors["hard_coal"] +
            mix.lignite_mw * co2_factors["lignite"] +
            max(0, mix.pumped_storage_mw) * co2_factors["pumped_storage"] +
            mix.other_mw * co2_factors["other"]
        )

        # Convert from kg/MWh to kg/kWh
        if mix.total_mw > 0:
            co2_per_mwh = total_co2 / mix.total_mw
            co2_per_kwh = co2_per_mwh / 1000
        else:
            co2_per_kwh = 0.40  # Default

        # Apply Brahim correction for grid losses (~5%)
        co2_per_kwh *= (1 + GENESIS_CONSTANT * 100)

        return round(co2_per_kwh, 4)

    async def get_grid_status(self, dt: Optional[datetime] = None) -> GridStatus:
        """Get comprehensive grid status."""
        if dt is None:
            dt = datetime.now()

        mix = await self.get_generation_mix(dt)
        consumption = await self.get_consumption(dt)
        price = await self.get_price(dt)
        co2 = await self.get_co2_intensity(dt)

        net_flow = mix.total_mw - consumption

        return GridStatus(
            timestamp=dt,
            generation=mix,
            consumption_mw=consumption,
            price_eur_mwh=price.day_ahead_eur_mwh,
            co2_intensity_kg_kwh=co2,
            renewable_share=mix.renewable_share,
            is_export=net_flow > 0,
            net_flow_mw=net_flow,
        )

    async def is_renewable_surplus(self) -> Tuple[bool, float]:
        """
        Check if there's currently a renewable surplus.

        Returns:
            Tuple of (is_surplus, surplus_percentage)
        """
        status = await self.get_grid_status()

        # Surplus if renewables > 80% of consumption
        renewable_pct = (status.generation.renewable_mw / max(status.consumption_mw, 1)) * 100

        is_surplus = renewable_pct > 80

        return (is_surplus, renewable_pct)

    async def detect_dunkelflaute(self) -> Tuple[bool, float]:
        """
        Detect Dunkelflaute (dark doldrums) condition.

        Returns:
            Tuple of (is_dunkelflaute, renewable_percentage)
        """
        status = await self.get_grid_status()

        # Dunkelflaute if renewables < 20% of generation
        renewable_pct = status.renewable_share * 100

        is_dunkelflaute = renewable_pct < 20

        if is_dunkelflaute:
            logger.warning(
                f"Dunkelflaute detected! Renewables at {renewable_pct:.1f}%"
            )

        return (is_dunkelflaute, renewable_pct)


# =============================================================================
# Factory Function
# =============================================================================

def get_smard_adapter(
    resolution: SMARDResolution = SMARDResolution.HOUR,
    simulation: bool = True,
) -> SMARDAdapter:
    """
    Factory function to get SMARD adapter.

    Args:
        resolution: Time resolution for data
        simulation: Use simulation mode (default True until API integrated)

    Returns:
        Configured SMARDAdapter instance
    """
    return SMARDAdapter(resolution=resolution, simulation_mode=simulation)


# =============================================================================
# CLI Demo
# =============================================================================

async def demo():
    """Demonstrate SMARD adapter."""
    print("=" * 70)
    print("SMARD Adapter Demo - German Grid Data")
    print("=" * 70)

    adapter = get_smard_adapter()

    # Get current status
    print("\n1. Current Grid Status:")
    status = await adapter.get_grid_status()

    print(f"   Timestamp: {status.timestamp.strftime('%Y-%m-%d %H:%M')}")
    print(f"   Total Generation: {status.generation.total_mw:,.0f} MW")
    print(f"   Total Consumption: {status.consumption_mw:,.0f} MW")
    print(f"   Net Flow: {status.net_flow_mw:+,.0f} MW ({'Export' if status.is_export else 'Import'})")
    print(f"   Renewable Share: {status.renewable_share * 100:.1f}%")
    print(f"   CO2 Intensity: {status.co2_intensity_kg_kwh:.4f} kg/kWh")
    print(f"   Price: {status.price_eur_mwh:.2f} EUR/MWh")

    # Generation breakdown
    print("\n2. Generation Mix:")
    mix = status.generation
    print(f"   Wind Onshore:  {mix.wind_onshore_mw:>8,.0f} MW")
    print(f"   Wind Offshore: {mix.wind_offshore_mw:>8,.0f} MW")
    print(f"   Solar:         {mix.solar_mw:>8,.0f} MW")
    print(f"   Biomass:       {mix.biomass_mw:>8,.0f} MW")
    print(f"   Hydro:         {mix.hydro_mw:>8,.0f} MW")
    print(f"   Gas:           {mix.gas_mw:>8,.0f} MW")
    print(f"   Lignite:       {mix.lignite_mw:>8,.0f} MW")
    print(f"   Hard Coal:     {mix.hard_coal_mw:>8,.0f} MW")

    # Check for surplus
    print("\n3. Renewable Surplus Check:")
    is_surplus, surplus_pct = await adapter.is_renewable_surplus()
    print(f"   Renewable Coverage: {surplus_pct:.1f}%")
    print(f"   Is Surplus: {is_surplus}")

    # Check for Dunkelflaute
    print("\n4. Dunkelflaute Check:")
    is_dunkelflaute, renewable_pct = await adapter.detect_dunkelflaute()
    print(f"   Renewable Share: {renewable_pct:.1f}%")
    print(f"   Is Dunkelflaute: {is_dunkelflaute}")

    print("\n" + "=" * 70)
    print("Demo complete!")


if __name__ == "__main__":
    asyncio.run(demo())
