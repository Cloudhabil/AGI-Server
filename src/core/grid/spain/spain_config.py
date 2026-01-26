"""
Spain Grid Configuration
========================

Core configuration for Spanish electricity grid optimization,
including CO2 intensity profiles, regional zones, and solar windows.

Data Sources:
- REE (Red Eléctrica de España): Real-time generation mix
- MITECO: Official emissions factors
- PVGIS: Solar irradiance data for Spain

Regional Zones:
- PENINSULA: Mainland Spain (interconnected)
- CANARIAS: Canary Islands (isolated, diesel-heavy)
- BALEARES: Balearic Islands (cable to Peninsula)
- CEUTA: North Africa exclave
- MELILLA: North Africa exclave

Author: GPIA Cognitive Ecosystem
Date: 2026-01-26
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple

# Import Brahim constants
try:
    from core.constants import GENESIS_CONSTANT, BETA_SECURITY, PHI, BRAHIM_SEQUENCE
except ImportError:
    GENESIS_CONSTANT = 2 / 901
    BETA_SECURITY = math.sqrt(5) - 2
    PHI = (1 + math.sqrt(5)) / 2
    BRAHIM_SEQUENCE = (27, 42, 60, 75, 97, 121, 136, 154, 172, 187)


# =============================================================================
# ENUMS
# =============================================================================

class SpainGridZone(Enum):
    """Spanish electricity grid zones."""
    PENINSULA = "peninsular"      # Mainland Spain
    CANARIAS = "canarias"         # Canary Islands
    BALEARES = "baleares"         # Balearic Islands
    CEUTA = "ceuta"               # Ceuta
    MELILLA = "melilla"           # Melilla


class SpainSeason(Enum):
    """Seasons for solar profile adjustment."""
    WINTER = "winter"       # Dec-Feb: Short days, lower solar
    SPRING = "spring"       # Mar-May: Increasing solar
    SUMMER = "summer"       # Jun-Aug: Peak solar, high AC demand
    AUTUMN = "autumn"       # Sep-Nov: Decreasing solar


class SpainTariffPeriod(Enum):
    """Spanish electricity tariff periods (PVPC 2.0TD)."""
    PUNTA = "punta"         # Peak: 10-14, 18-22 (weekdays)
    LLANO = "llano"         # Shoulder: 8-10, 14-18, 22-24
    VALLE = "valle"         # Off-peak: 0-8, weekends


# =============================================================================
# GRID ZONE SPECIFICATIONS
# =============================================================================

@dataclass
class GridZoneSpec:
    """Specification for a Spanish grid zone."""
    zone: SpainGridZone
    name_es: str
    name_en: str
    population: int
    peak_demand_mw: int
    solar_capacity_mw: int
    wind_capacity_mw: int
    interconnection_mw: int  # 0 for isolated
    base_co2_intensity: float  # kg/kWh average
    timezone: str


SPAIN_GRID_ZONES: Dict[SpainGridZone, GridZoneSpec] = {
    SpainGridZone.PENINSULA: GridZoneSpec(
        zone=SpainGridZone.PENINSULA,
        name_es="España Peninsular",
        name_en="Mainland Spain",
        population=43_000_000,
        peak_demand_mw=40_000,
        solar_capacity_mw=55_000,
        wind_capacity_mw=30_000,
        interconnection_mw=6_000,  # France + Portugal
        base_co2_intensity=0.15,
        timezone="Europe/Madrid",
    ),
    SpainGridZone.CANARIAS: GridZoneSpec(
        zone=SpainGridZone.CANARIAS,
        name_es="Canarias",
        name_en="Canary Islands",
        population=2_200_000,
        peak_demand_mw=1_800,
        solar_capacity_mw=800,
        wind_capacity_mw=500,
        interconnection_mw=0,  # Isolated
        base_co2_intensity=0.45,  # More diesel
        timezone="Atlantic/Canary",
    ),
    SpainGridZone.BALEARES: GridZoneSpec(
        zone=SpainGridZone.BALEARES,
        name_es="Baleares",
        name_en="Balearic Islands",
        population=1_200_000,
        peak_demand_mw=1_200,
        solar_capacity_mw=400,
        wind_capacity_mw=50,
        interconnection_mw=400,  # Cable to Peninsula
        base_co2_intensity=0.35,
        timezone="Europe/Madrid",
    ),
    SpainGridZone.CEUTA: GridZoneSpec(
        zone=SpainGridZone.CEUTA,
        name_es="Ceuta",
        name_en="Ceuta",
        population=85_000,
        peak_demand_mw=60,
        solar_capacity_mw=10,
        wind_capacity_mw=0,
        interconnection_mw=0,
        base_co2_intensity=0.50,
        timezone="Europe/Madrid",
    ),
    SpainGridZone.MELILLA: GridZoneSpec(
        zone=SpainGridZone.MELILLA,
        name_es="Melilla",
        name_en="Melilla",
        population=87_000,
        peak_demand_mw=55,
        solar_capacity_mw=8,
        wind_capacity_mw=0,
        interconnection_mw=0,
        base_co2_intensity=0.50,
        timezone="Europe/Madrid",
    ),
}


# =============================================================================
# CO2 INTENSITY PROFILES
# =============================================================================

# Hourly CO2 intensity profiles (kg CO2 per kWh)
# Based on REE generation mix data and MITECO emissions factors

SPAIN_CO2_PROFILES: Dict[SpainSeason, Dict[int, float]] = {
    SpainSeason.SUMMER: {
        # Summer: Strong solar, moderate wind
        # Solar peak 10:00-17:00, evening gas ramp
        0: 0.18, 1: 0.17, 2: 0.16, 3: 0.15, 4: 0.16, 5: 0.18,
        6: 0.20, 7: 0.18, 8: 0.12, 9: 0.08,
        10: 0.05, 11: 0.03, 12: 0.02, 13: 0.02, 14: 0.03, 15: 0.04,
        16: 0.06, 17: 0.10,
        18: 0.25, 19: 0.38, 20: 0.42, 21: 0.40, 22: 0.35, 23: 0.25,
    },
    SpainSeason.WINTER: {
        # Winter: Weaker solar, strong wind
        # Solar peak 12:00-15:00, longer evening demand
        0: 0.22, 1: 0.20, 2: 0.19, 3: 0.18, 4: 0.19, 5: 0.22,
        6: 0.28, 7: 0.32, 8: 0.30, 9: 0.25,
        10: 0.18, 11: 0.12, 12: 0.08, 13: 0.07, 14: 0.08, 15: 0.12,
        16: 0.20, 17: 0.30,
        18: 0.40, 19: 0.45, 20: 0.48, 21: 0.46, 22: 0.42, 23: 0.32,
    },
    SpainSeason.SPRING: {
        # Spring: Increasing solar, variable wind
        0: 0.20, 1: 0.18, 2: 0.17, 3: 0.16, 4: 0.17, 5: 0.20,
        6: 0.24, 7: 0.22, 8: 0.15, 9: 0.10,
        10: 0.06, 11: 0.04, 12: 0.03, 13: 0.03, 14: 0.04, 15: 0.06,
        16: 0.10, 17: 0.18,
        18: 0.32, 19: 0.40, 20: 0.44, 21: 0.42, 22: 0.38, 23: 0.28,
    },
    SpainSeason.AUTUMN: {
        # Autumn: Decreasing solar, increasing wind
        0: 0.20, 1: 0.19, 2: 0.18, 3: 0.17, 4: 0.18, 5: 0.21,
        6: 0.26, 7: 0.28, 8: 0.22, 9: 0.15,
        10: 0.10, 11: 0.07, 12: 0.05, 13: 0.05, 14: 0.06, 15: 0.09,
        16: 0.15, 17: 0.25,
        18: 0.38, 19: 0.44, 20: 0.46, 21: 0.44, 22: 0.40, 23: 0.30,
    },
}

# Canarias has higher baseline (more diesel)
CANARIAS_CO2_ADJUSTMENT = 0.25  # Add to Peninsula values

# Weekend adjustment (less industrial demand, more renewable share)
WEEKEND_CO2_REDUCTION = 0.15  # 15% lower on weekends


# =============================================================================
# SOLAR WINDOW DEFINITIONS
# =============================================================================

@dataclass
class SolarWindow:
    """Definition of a solar surplus window."""
    start_hour: int
    end_hour: int
    peak_hour: int
    typical_surplus_mw: int
    co2_intensity: float  # Average during window


# Solar windows by season (Peninsula)
SOLAR_WINDOWS: Dict[SpainSeason, SolarWindow] = {
    SpainSeason.SUMMER: SolarWindow(
        start_hour=9,
        end_hour=18,
        peak_hour=13,
        typical_surplus_mw=15000,
        co2_intensity=0.04,
    ),
    SpainSeason.WINTER: SolarWindow(
        start_hour=11,
        end_hour=15,
        peak_hour=13,
        typical_surplus_mw=5000,
        co2_intensity=0.09,
    ),
    SpainSeason.SPRING: SolarWindow(
        start_hour=10,
        end_hour=17,
        peak_hour=13,
        typical_surplus_mw=12000,
        co2_intensity=0.05,
    ),
    SpainSeason.AUTUMN: SolarWindow(
        start_hour=10,
        end_hour=16,
        peak_hour=13,
        typical_surplus_mw=8000,
        co2_intensity=0.07,
    ),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_current_season(dt: Optional[datetime] = None) -> SpainSeason:
    """
    Get the current season in Spain.

    Args:
        dt: Datetime to check (default: now)

    Returns:
        SpainSeason enum value
    """
    if dt is None:
        dt = datetime.now()

    month = dt.month

    if month in (12, 1, 2):
        return SpainSeason.WINTER
    elif month in (3, 4, 5):
        return SpainSeason.SPRING
    elif month in (6, 7, 8):
        return SpainSeason.SUMMER
    else:
        return SpainSeason.AUTUMN


def get_solar_window(
    dt: Optional[datetime] = None,
    zone: SpainGridZone = SpainGridZone.PENINSULA
) -> SolarWindow:
    """
    Get the solar surplus window for current date and zone.

    Args:
        dt: Date to check (default: now)
        zone: Grid zone

    Returns:
        SolarWindow for the season
    """
    season = get_current_season(dt)
    window = SOLAR_WINDOWS[season]

    # Adjust for Canarias (1 hour later due to timezone)
    if zone == SpainGridZone.CANARIAS:
        return SolarWindow(
            start_hour=window.start_hour,  # Same solar time
            end_hour=window.end_hour,
            peak_hour=window.peak_hour,
            typical_surplus_mw=int(window.typical_surplus_mw * 0.02),  # 2% of Peninsula
            co2_intensity=window.co2_intensity + CANARIAS_CO2_ADJUSTMENT,
        )

    return window


def get_tariff_period(dt: Optional[datetime] = None) -> SpainTariffPeriod:
    """
    Get the current Spanish electricity tariff period.

    PVPC 2.0TD tariff structure:
    - Punta (peak): 10-14, 18-22 on weekdays
    - Llano (shoulder): 8-10, 14-18, 22-24 on weekdays
    - Valle (off-peak): 0-8 on weekdays, all weekend

    Args:
        dt: Datetime to check (default: now)

    Returns:
        SpainTariffPeriod enum value
    """
    if dt is None:
        dt = datetime.now()

    hour = dt.hour
    weekday = dt.weekday()  # 0=Monday, 6=Sunday

    # Weekend is always Valle
    if weekday >= 5:
        return SpainTariffPeriod.VALLE

    # Weekday periods
    if hour < 8:
        return SpainTariffPeriod.VALLE
    elif hour < 10:
        return SpainTariffPeriod.LLANO
    elif hour < 14:
        return SpainTariffPeriod.PUNTA
    elif hour < 18:
        return SpainTariffPeriod.LLANO
    elif hour < 22:
        return SpainTariffPeriod.PUNTA
    else:
        return SpainTariffPeriod.LLANO


def is_solar_surplus_likely(
    dt: Optional[datetime] = None,
    zone: SpainGridZone = SpainGridZone.PENINSULA
) -> Tuple[bool, float]:
    """
    Check if solar surplus is likely at given time.

    Returns:
        (is_surplus_likely, confidence 0-1)
    """
    if dt is None:
        dt = datetime.now()

    window = get_solar_window(dt, zone)
    hour = dt.hour

    if window.start_hour <= hour <= window.end_hour:
        # Within solar window
        # Confidence is highest at peak hour
        distance_from_peak = abs(hour - window.peak_hour)
        max_distance = max(window.peak_hour - window.start_hour, window.end_hour - window.peak_hour)
        confidence = 1.0 - (distance_from_peak / max_distance) * 0.5

        return True, confidence

    return False, 0.0


# =============================================================================
# SPAIN CO2 CALCULATOR
# =============================================================================

class SpainCO2Calculator:
    """
    Spain-specific CO2 intensity calculator.

    Accounts for:
    - Seasonal solar/wind variation
    - Regional differences (Peninsula vs Islands)
    - Weekend/holiday effects
    - Real-time REE data integration
    """

    def __init__(
        self,
        zone: SpainGridZone = SpainGridZone.PENINSULA,
        use_realtime: bool = False
    ):
        """
        Initialize Spain CO2 calculator.

        Args:
            zone: Grid zone
            use_realtime: If True, fetch real-time data from REE
        """
        self.zone = zone
        self.use_realtime = use_realtime
        self.zone_spec = SPAIN_GRID_ZONES[zone]

        # Cache for real-time data
        self._realtime_cache: Dict[str, Tuple[datetime, float]] = {}
        self._cache_duration = timedelta(minutes=10)

    def get_intensity(
        self,
        dt: Optional[datetime] = None
    ) -> float:
        """
        Get CO2 intensity for a specific datetime.

        Args:
            dt: Datetime to check (default: now)

        Returns:
            CO2 intensity in kg/kWh
        """
        if dt is None:
            dt = datetime.now()

        # Get base profile value
        season = get_current_season(dt)
        hour = dt.hour
        base_intensity = SPAIN_CO2_PROFILES[season].get(hour, 0.25)

        # Adjust for zone
        if self.zone == SpainGridZone.CANARIAS:
            base_intensity += CANARIAS_CO2_ADJUSTMENT
        elif self.zone in (SpainGridZone.CEUTA, SpainGridZone.MELILLA):
            base_intensity += 0.30  # More diesel in exclave

        # Adjust for weekend
        if dt.weekday() >= 5:
            base_intensity *= (1 - WEEKEND_CO2_REDUCTION)

        return max(0.01, base_intensity)  # Minimum 0.01 kg/kWh

    def get_intensity_forecast(
        self,
        hours: int = 24,
        start: Optional[datetime] = None
    ) -> List[Tuple[datetime, float]]:
        """
        Get CO2 intensity forecast.

        Args:
            hours: Number of hours to forecast
            start: Start time (default: now)

        Returns:
            List of (datetime, intensity) tuples
        """
        if start is None:
            start = datetime.now()

        forecast = []
        for h in range(hours):
            dt = start + timedelta(hours=h)
            intensity = self.get_intensity(dt)
            forecast.append((dt, intensity))

        return forecast

    def calculate_savings(
        self,
        kwh: float,
        from_time: datetime,
        to_time: datetime
    ) -> Tuple[float, float, float]:
        """
        Calculate CO2 and cost savings from load shift.

        Args:
            kwh: Energy amount to shift
            from_time: Original consumption time
            to_time: New consumption time

        Returns:
            (co2_saved_kg, cost_saved_eur, percentage_improvement)
        """
        from_intensity = self.get_intensity(from_time)
        to_intensity = self.get_intensity(to_time)

        # CO2 savings
        co2_saved = kwh * (from_intensity - to_intensity)

        # Cost savings (PVPC tariff based)
        from_tariff = get_tariff_period(from_time)
        to_tariff = get_tariff_period(to_time)

        # Approximate prices (EUR/kWh)
        tariff_prices = {
            SpainTariffPeriod.PUNTA: 0.25,
            SpainTariffPeriod.LLANO: 0.15,
            SpainTariffPeriod.VALLE: 0.08,
        }

        from_price = tariff_prices[from_tariff]
        to_price = tariff_prices[to_tariff]
        cost_saved = kwh * (from_price - to_price)

        # Percentage improvement
        if from_intensity > 0:
            pct_improvement = (from_intensity - to_intensity) / from_intensity * 100
        else:
            pct_improvement = 0

        return max(0, co2_saved), max(0, cost_saved), pct_improvement

    def find_optimal_window(
        self,
        duration_hours: float = 1.0,
        start: Optional[datetime] = None,
        look_ahead_hours: int = 24
    ) -> Tuple[datetime, float, float]:
        """
        Find optimal time window for minimum CO2.

        Args:
            duration_hours: Load duration
            start: Search start time
            look_ahead_hours: How far ahead to search

        Returns:
            (optimal_start_time, avg_intensity, savings_vs_now)
        """
        if start is None:
            start = datetime.now()

        current_intensity = self.get_intensity(start)
        forecast = self.get_intensity_forecast(look_ahead_hours, start)

        best_start = start
        best_intensity = current_intensity

        # Find window with lowest average intensity
        for i in range(len(forecast) - int(duration_hours)):
            window_intensities = [
                forecast[j][1]
                for j in range(i, min(i + int(duration_hours) + 1, len(forecast)))
            ]
            avg_intensity = sum(window_intensities) / len(window_intensities)

            if avg_intensity < best_intensity:
                best_intensity = avg_intensity
                best_start = forecast[i][0]

        savings_vs_now = current_intensity - best_intensity

        return best_start, best_intensity, savings_vs_now

    def get_daily_summary(
        self,
        dt: Optional[date] = None
    ) -> Dict[str, any]:
        """
        Get daily CO2 summary.

        Returns:
            Summary with peak, valley, average intensities
        """
        if dt is None:
            dt = date.today()

        day_start = datetime.combine(dt, datetime.min.time())
        forecast = self.get_intensity_forecast(24, day_start)

        intensities = [f[1] for f in forecast]

        # Find best and worst hours
        min_intensity = min(intensities)
        max_intensity = max(intensities)
        min_hour = intensities.index(min_intensity)
        max_hour = intensities.index(max_intensity)

        return {
            "date": dt.isoformat(),
            "zone": self.zone.value,
            "season": get_current_season(day_start).value,
            "average_intensity": sum(intensities) / len(intensities),
            "min_intensity": min_intensity,
            "min_hour": min_hour,
            "max_intensity": max_intensity,
            "max_hour": max_hour,
            "solar_window": {
                "start": get_solar_window(day_start, self.zone).start_hour,
                "end": get_solar_window(day_start, self.zone).end_hour,
                "peak": get_solar_window(day_start, self.zone).peak_hour,
            },
            "best_ev_charging": f"{min_hour:02d}:00 - {(min_hour+4)%24:02d}:00",
            "avoid_consumption": f"{max_hour:02d}:00 - {(max_hour+2)%24:02d}:00",
        }
