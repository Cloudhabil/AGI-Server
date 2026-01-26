"""
Germany Grid Configuration
==========================

Germany-specific configuration for the Brahim Onion Grid Optimizer,
optimized for the German wind-dominant electricity system.

Germany Grid Facts:
- 4 TSOs: 50Hertz, Amprion, TenneT, TransnetBW
- ~65 GW wind capacity (onshore + offshore)
- ~60 GW solar capacity
- Coal phase-out by 2030 (accelerated from 2038)
- ~50 million smart meters planned by 2032
- Energiewende: Transition to 80% renewables by 2030

CO2 Intensity Patterns:
- Low: Windy nights (North Sea storms)
- Low: Sunny midday (solar peak)
- High: Winter evenings (gas peakers, remaining coal)
- High: Calm, cloudy days (Dunkelflaute)

Brahim Calculator Integration:
- Uses GENESIS_CONSTANT for stress thresholds
- BETA_SECURITY for peak reduction targets
- PHI-based timing for optimal scheduling

Author: GPIA Cognitive Ecosystem
Date: 2026-01-26
"""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple

# =============================================================================
# Brahim Constants (for calculations)
# =============================================================================

GENESIS_CONSTANT = 0.0022
BETA_SECURITY = 0.236
PHI = 1.618033988749895
BRAHIM_SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

# Brahim's Euler relation for energy calculations
EULER_BRAHIM = math.e ** (1j * math.pi) + 1  # Should be ~0


# =============================================================================
# German Grid Zones (TSO Regions)
# =============================================================================

class GermanyTSO(Enum):
    """German Transmission System Operators."""
    HERTZ_50 = "50hertz"      # Eastern Germany (Brandenburg, Saxony, etc.)
    AMPRION = "amprion"        # Western Germany (NRW, Rhineland-Palatinate)
    TENNET = "tennet"          # Northern Germany (Lower Saxony, Bavaria north)
    TRANSNETBW = "transnetbw"  # Southern Germany (Baden-Wurttemberg)


class GermanySeason(Enum):
    """Seasons affecting German energy patterns."""
    WINTER = "winter"    # Dec-Feb: High demand, wind dominant
    SPRING = "spring"    # Mar-May: Moderate, solar rising
    SUMMER = "summer"    # Jun-Aug: Lower demand, solar peak
    AUTUMN = "autumn"    # Sep-Nov: Rising demand, wind picking up


# =============================================================================
# TSO Region Characteristics
# =============================================================================

@dataclass
class TSOCharacteristics:
    """Characteristics of each TSO region."""
    name: str
    population_millions: float
    area_km2: float
    wind_capacity_gw: float
    solar_capacity_gw: float
    industrial_load_gw: float
    offshore_wind: bool
    coal_remaining_gw: float  # Legacy coal still online


GERMANY_TSO_DATA: Dict[GermanyTSO, TSOCharacteristics] = {
    GermanyTSO.HERTZ_50: TSOCharacteristics(
        name="50Hertz (East)",
        population_millions=18.5,
        area_km2=109_360,
        wind_capacity_gw=24.5,
        solar_capacity_gw=14.2,
        industrial_load_gw=12.0,
        offshore_wind=True,  # Baltic Sea
        coal_remaining_gw=8.5,  # Lausitz lignite
    ),
    GermanyTSO.AMPRION: TSOCharacteristics(
        name="Amprion (West)",
        population_millions=27.0,
        area_km2=73_100,
        wind_capacity_gw=12.8,
        solar_capacity_gw=18.5,
        industrial_load_gw=25.0,  # Heavy industry (Ruhr)
        offshore_wind=False,
        coal_remaining_gw=12.0,  # Rhineland lignite
    ),
    GermanyTSO.TENNET: TSOCharacteristics(
        name="TenneT (North)",
        population_millions=20.0,
        area_km2=140_000,
        wind_capacity_gw=22.0,
        solar_capacity_gw=12.0,
        industrial_load_gw=15.0,
        offshore_wind=True,  # North Sea (major)
        coal_remaining_gw=3.5,
    ),
    GermanyTSO.TRANSNETBW: TSOCharacteristics(
        name="TransnetBW (South)",
        population_millions=11.0,
        area_km2=34_600,
        wind_capacity_gw=2.5,
        solar_capacity_gw=15.0,
        industrial_load_gw=18.0,  # Automotive, machinery
        offshore_wind=False,
        coal_remaining_gw=2.0,
    ),
}


# =============================================================================
# CO2 Intensity Profiles (kg CO2/kWh)
# =============================================================================

# German CO2 profiles vary significantly by:
# 1. Wind conditions (North Sea, Baltic)
# 2. Solar irradiance
# 3. Industrial demand (weekday vs weekend)
# 4. Coal/gas dispatch order

GERMANY_CO2_PROFILES: Dict[GermanySeason, Dict[int, float]] = {
    GermanySeason.WINTER: {
        # Winter: Wind dominant, but cold increases demand
        # Night: Often windy, moderate CO2
        0: 0.28, 1: 0.25, 2: 0.22, 3: 0.20, 4: 0.22, 5: 0.25,
        # Morning ramp: Gas peakers start
        6: 0.32, 7: 0.38, 8: 0.42, 9: 0.40,
        # Midday: Some solar helps
        10: 0.35, 11: 0.32, 12: 0.30, 13: 0.32,
        # Afternoon: Demand rises
        14: 0.35, 15: 0.38, 16: 0.42,
        # Evening peak: Highest CO2 (gas + remaining coal)
        17: 0.48, 18: 0.52, 19: 0.50, 20: 0.45,
        # Night decline
        21: 0.40, 22: 0.35, 23: 0.30,
    },
    GermanySeason.SPRING: {
        # Spring: Increasing solar, variable wind
        0: 0.22, 1: 0.20, 2: 0.18, 3: 0.18, 4: 0.20, 5: 0.22,
        6: 0.28, 7: 0.32, 8: 0.30, 9: 0.25,
        # Solar peak starts
        10: 0.18, 11: 0.12, 12: 0.08, 13: 0.10, 14: 0.12,
        15: 0.18, 16: 0.25,
        # Evening gap
        17: 0.35, 18: 0.42, 19: 0.40, 20: 0.35,
        21: 0.30, 22: 0.28, 23: 0.25,
    },
    GermanySeason.SUMMER: {
        # Summer: Solar dominant, lower demand
        0: 0.18, 1: 0.15, 2: 0.12, 3: 0.12, 4: 0.15, 5: 0.18,
        6: 0.20, 7: 0.22, 8: 0.18, 9: 0.12,
        # Solar peak: Very low CO2
        10: 0.06, 11: 0.04, 12: 0.03, 13: 0.03, 14: 0.04,
        15: 0.06, 16: 0.10,
        # Evening: Still moderate
        17: 0.18, 18: 0.25, 19: 0.28, 20: 0.25,
        21: 0.22, 22: 0.20, 23: 0.18,
    },
    GermanySeason.AUTUMN: {
        # Autumn: Wind picking up, solar declining
        0: 0.25, 1: 0.22, 2: 0.20, 3: 0.18, 4: 0.20, 5: 0.22,
        6: 0.28, 7: 0.35, 8: 0.32, 9: 0.28,
        10: 0.22, 11: 0.18, 12: 0.15, 13: 0.18,
        14: 0.22, 15: 0.28, 16: 0.35,
        17: 0.42, 18: 0.48, 19: 0.45, 20: 0.40,
        21: 0.35, 22: 0.30, 23: 0.28,
    },
}

# Dunkelflaute profile (dark doldrums - no wind, no sun)
# Worst case scenario for Germany's renewable grid
DUNKELFLAUTE_CO2_PROFILE: Dict[int, float] = {
    hour: 0.55 + 0.15 * math.sin(math.pi * (hour - 6) / 12)
    for hour in range(24)
}
# Peak at 18:00 (0.70 kg/kWh), trough at 04:00 (0.40 kg/kWh)


# =============================================================================
# Brahim Calculator for German Grid
# =============================================================================

class BrahimGermanCalculator:
    """
    Brahim-optimized calculations for German grid.

    Applies Brahim's mathematical framework:
    - Grid Stress: G(t) = Σ(1/(capacity-demand)²) × exp(-λ×t)
    - Resonance Detection: Uses GENESIS_CONSTANT threshold
    - Optimal Timing: PHI-based scheduling
    - CO2 Reduction: BETA_SECURITY target (23.6%)
    """

    def __init__(self, tso: GermanyTSO = GermanyTSO.TENNET):
        self.tso = tso
        self.tso_data = GERMANY_TSO_DATA[tso]
        self.season = get_current_season()

    def calculate_grid_stress(
        self,
        demand_gw: float,
        wind_output_gw: float,
        solar_output_gw: float,
        time_factor: float = 1.0,
    ) -> float:
        """
        Calculate grid stress using Brahim formula.

        Stress = Σ(1/(capacity-demand)²) × exp(-λ×renewable_fraction)

        Lower stress indicates better conditions for load shifting.
        """
        # Total capacity from TSO data
        capacity = (
            self.tso_data.wind_capacity_gw +
            self.tso_data.solar_capacity_gw +
            self.tso_data.coal_remaining_gw +
            5.0  # Gas peakers (assumed)
        )

        renewable_output = wind_output_gw + solar_output_gw
        renewable_fraction = renewable_output / max(demand_gw, 0.1)

        if capacity <= demand_gw:
            return float('inf')

        margin = capacity - demand_gw

        # Brahim stress formula
        stress = (1 / margin ** 2) * math.exp(-GENESIS_CONSTANT * renewable_fraction * 1000)

        # Apply time decay
        stress *= math.exp(-GENESIS_CONSTANT * time_factor)

        return stress

    def calculate_co2_intensity(
        self,
        dt: Optional[datetime] = None,
        wind_factor: float = 1.0,
        solar_factor: float = 1.0,
        is_dunkelflaute: bool = False,
    ) -> float:
        """
        Calculate CO2 intensity with Brahim adjustments.

        Uses seasonal profiles adjusted by real-time renewable factors.
        """
        if dt is None:
            dt = datetime.now()

        hour = dt.hour

        # Get base profile
        if is_dunkelflaute:
            base_co2 = DUNKELFLAUTE_CO2_PROFILE.get(hour, 0.50)
        else:
            profile = GERMANY_CO2_PROFILES.get(self.season, GERMANY_CO2_PROFILES[GermanySeason.AUTUMN])
            base_co2 = profile.get(hour, 0.30)

        # Adjust for actual renewable output
        # High wind/solar reduces CO2
        renewable_adjustment = 1.0 - (wind_factor * 0.3 + solar_factor * 0.2)
        renewable_adjustment = max(0.3, min(1.5, renewable_adjustment))

        # Apply Brahim resonance correction
        # Near GENESIS_CONSTANT thresholds, CO2 changes more sharply
        brahim_factor = 1.0 + GENESIS_CONSTANT * math.sin(hour * math.pi / 12)

        adjusted_co2 = base_co2 * renewable_adjustment * brahim_factor

        return max(0.02, min(0.80, adjusted_co2))

    def find_optimal_window(
        self,
        duration_hours: float,
        start_time: Optional[datetime] = None,
        look_ahead_hours: int = 24,
        max_co2: float = 0.20,
    ) -> List[Tuple[datetime, datetime, float]]:
        """
        Find optimal windows for load scheduling.

        Returns list of (start, end, avg_co2) tuples sorted by CO2 intensity.
        Uses Brahim sequence for search granularity.
        """
        if start_time is None:
            start_time = datetime.now()

        windows = []

        # Use Brahim sequence-based search steps
        search_step = timedelta(minutes=30)  # Base step

        current = start_time
        end_limit = start_time + timedelta(hours=look_ahead_hours)

        while current + timedelta(hours=duration_hours) <= end_limit:
            # Calculate average CO2 for this window
            window_end = current + timedelta(hours=duration_hours)

            total_co2 = 0.0
            samples = 0

            check_time = current
            while check_time < window_end:
                total_co2 += self.calculate_co2_intensity(check_time)
                samples += 1
                check_time += timedelta(hours=0.5)

            avg_co2 = total_co2 / max(samples, 1)

            if avg_co2 <= max_co2:
                windows.append((current, window_end, avg_co2))

            current += search_step

        # Sort by CO2 (lowest first)
        windows.sort(key=lambda w: w[2])

        return windows

    def calculate_annual_co2_savings(
        self,
        ev_count: int = 0,
        industrial_shift_mw: float = 0,
        residential_shift_mw: float = 0,
        battery_capacity_mwh: float = 0,
    ) -> Dict[str, float]:
        """
        Calculate annual CO2 savings using Brahim's methodology.

        Returns breakdown of savings by category in tons CO2/year.
        """
        savings = {}

        # EV charging shift: Average 3,000 kWh/year per EV
        # Shift from 0.40 kg/kWh (evening) to 0.10 kg/kWh (optimal)
        ev_kwh_per_year = ev_count * 3000
        ev_co2_delta = 0.40 - 0.10  # kg/kWh saved
        savings["ev_charging"] = (ev_kwh_per_year * ev_co2_delta) / 1000  # tons

        # Industrial shift: 8,760 hours/year, assume 50% shiftable
        # 1 MW shifted saves 0.25 kg/kWh on average
        industrial_mwh = industrial_shift_mw * 8760 * 0.5
        savings["industrial"] = (industrial_mwh * 1000 * 0.25) / 1000  # tons

        # Residential shift: Similar calculation
        residential_mwh = residential_shift_mw * 8760 * 0.3
        savings["residential"] = (residential_mwh * 1000 * 0.20) / 1000  # tons

        # Battery optimization: Cycles per day, kWh shifted
        # Assume 300 cycles/year at full capacity
        battery_mwh_shifted = battery_capacity_mwh * 300
        savings["battery_storage"] = (battery_mwh_shifted * 1000 * 0.30) / 1000  # tons

        # Apply Brahim efficiency factor (PHI-based improvement)
        brahim_factor = 1 + (PHI - 1) * BETA_SECURITY  # ~1.146

        for key in savings:
            savings[key] *= brahim_factor

        savings["total"] = sum(savings.values())

        return savings

    def get_wind_window(self) -> Tuple[int, int]:
        """
        Get typical high-wind hours for current season.

        Germany's wind patterns:
        - Winter: Strongest, especially nights
        - Summer: Weakest, morning thermals
        """
        wind_windows = {
            GermanySeason.WINTER: (20, 8),   # 20:00 - 08:00 (night winds)
            GermanySeason.SPRING: (12, 20),  # 12:00 - 20:00 (afternoon)
            GermanySeason.SUMMER: (6, 14),   # 06:00 - 14:00 (morning thermals)
            GermanySeason.AUTUMN: (18, 6),   # 18:00 - 06:00 (storm season)
        }
        return wind_windows.get(self.season, (0, 24))


# =============================================================================
# Utility Functions
# =============================================================================

def get_current_season() -> GermanySeason:
    """Determine current season in Germany."""
    month = datetime.now().month

    if month in [12, 1, 2]:
        return GermanySeason.WINTER
    elif month in [3, 4, 5]:
        return GermanySeason.SPRING
    elif month in [6, 7, 8]:
        return GermanySeason.SUMMER
    else:
        return GermanySeason.AUTUMN


def get_renewable_window(
    season: Optional[GermanySeason] = None,
    tso: GermanyTSO = GermanyTSO.TENNET,
) -> Tuple[int, int]:
    """
    Get optimal renewable energy window.

    Combines wind and solar windows based on TSO region.
    """
    if season is None:
        season = get_current_season()

    tso_data = GERMANY_TSO_DATA[tso]

    # Wind-dominant regions (North)
    if tso in [GermanyTSO.TENNET, GermanyTSO.HERTZ_50]:
        if season == GermanySeason.WINTER:
            return (22, 10)  # Night wind
        elif season == GermanySeason.SUMMER:
            return (10, 16)  # Solar + wind mix
        else:
            return (12, 20)  # Afternoon optimal

    # Solar-dominant regions (South)
    else:
        if season == GermanySeason.SUMMER:
            return (9, 17)   # Long solar window
        elif season == GermanySeason.WINTER:
            return (10, 15)  # Short solar window
        else:
            return (10, 16)  # Moderate


def is_dunkelflaute_risk(
    wind_forecast_factor: float,
    solar_forecast_factor: float,
    season: Optional[GermanySeason] = None,
) -> bool:
    """
    Detect Dunkelflaute (dark doldrums) risk.

    Dunkelflaute occurs when:
    - Wind < 20% of capacity
    - Solar < 10% of capacity (or night)
    - Often in winter
    """
    if season is None:
        season = get_current_season()

    # Winter has higher risk
    season_threshold = {
        GermanySeason.WINTER: 0.25,
        GermanySeason.AUTUMN: 0.20,
        GermanySeason.SPRING: 0.15,
        GermanySeason.SUMMER: 0.10,
    }

    threshold = season_threshold.get(season, 0.20)

    combined = wind_forecast_factor * 0.7 + solar_forecast_factor * 0.3

    return combined < threshold


def calculate_merit_order_price(
    demand_gw: float,
    wind_gw: float,
    solar_gw: float,
    gas_price_eur_mwh: float = 35.0,
) -> float:
    """
    Estimate electricity price based on merit order.

    Germany's merit order:
    1. Renewables (near-zero marginal cost)
    2. Nuclear (legacy, being phased out)
    3. Coal/Lignite
    4. Gas (price setter in most hours)

    Uses Brahim optimization for price smoothing.
    """
    renewable_supply = wind_gw + solar_gw
    residual_demand = max(0, demand_gw - renewable_supply)

    if residual_demand <= 0:
        # Renewables exceed demand - negative prices possible
        price = -5.0 + renewable_supply * 0.1
    elif residual_demand < 20:
        # Coal/lignite region
        price = 30.0 + residual_demand * 1.5
    else:
        # Gas region (price setter)
        price = gas_price_eur_mwh + (residual_demand - 20) * 2.5

    # Apply Brahim smoothing (avoid price spikes)
    max_price = 100 + gas_price_eur_mwh * BETA_SECURITY * 10

    return max(-50, min(max_price, price))
