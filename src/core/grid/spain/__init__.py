"""
Brahim Grid Optimizer - Spain Solar Configuration
==================================================

Spain-specific configuration for the Brahim Onion Grid Optimizer,
optimized for the Spanish solar-dominant electricity system.

Features:
- REE (Red Eléctrica de España) API integration
- Seasonal CO2 intensity profiles
- Regional grid zones (Peninsula, Canarias, Baleares, Ceuta, Melilla)
- Iberdrola/Endesa smart meter integration
- Solar surplus detection and load shifting

Spain Grid Facts:
- 60+ GW solar capacity (largest in EU)
- 28 million smart meters deployed
- Peak solar: 11:00-15:00 (summer), 12:00-14:00 (winter)
- Evening gap: 18:00-22:00 (highest CO2 from gas peakers)

CO2 Reduction Potential:
- EV charging shift: 315,000 tons/year
- Industrial load shift: 4.3M tons/year
- Battery optimization: 1.5M tons/year
- Residential shift: 1.6M tons/year
- TOTAL: 7.7M tons CO2/year (2.3% of Spain's emissions)

Author: GPIA Cognitive Ecosystem
Date: 2026-01-26
Version: 1.0.0
"""

from .spain_config import (
    SpainGridZone,
    SpainSeason,
    SPAIN_CO2_PROFILES,
    SPAIN_GRID_ZONES,
    SpainCO2Calculator,
    get_current_season,
    get_solar_window,
)

from .ree_adapter import (
    REEIndicator,
    REEAdapter,
    get_ree_adapter,
)

from .smart_meter_adapters import (
    IberdrolaAdapter,
    EndesaAdapter,
    SpanishSmartMeterAdapter,
    get_spanish_meter_adapter,
)

from .spain_optimizer import (
    SpainSolarOptimizer,
    SolarSurplusEvent,
    EVChargingSchedule,
    get_spain_optimizer,
)

__all__ = [
    # Config
    "SpainGridZone",
    "SpainSeason",
    "SPAIN_CO2_PROFILES",
    "SPAIN_GRID_ZONES",
    "SpainCO2Calculator",
    "get_current_season",
    "get_solar_window",
    # REE
    "REEIndicator",
    "REEAdapter",
    "get_ree_adapter",
    # Smart Meters
    "IberdrolaAdapter",
    "EndesaAdapter",
    "SpanishSmartMeterAdapter",
    "get_spanish_meter_adapter",
    # Optimizer
    "SpainSolarOptimizer",
    "SolarSurplusEvent",
    "EVChargingSchedule",
    "get_spain_optimizer",
]

__version__ = "1.0.0"
