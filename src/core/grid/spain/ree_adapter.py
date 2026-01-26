"""
REE (Red Eléctrica de España) API Adapter
==========================================

Adapter for Spain's grid operator API (e·sios and ESIOS).

Provides real-time and historical data:
- Generation mix (solar, wind, nuclear, gas, etc.)
- Demand forecast and actual
- CO2 emissions
- Cross-border exchanges
- Spot market prices (OMIE)

API Endpoints:
- https://api.esios.ree.es - Main ESIOS API
- https://apidatos.ree.es - Public REE data API

Authentication:
- ESIOS: Requires API token (free registration)
- REE Public: No authentication required

Author: GPIA Cognitive Ecosystem
Date: 2026-01-26
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("grid.spain.ree")


# =============================================================================
# REE INDICATORS
# =============================================================================

class REEIndicator(Enum):
    """
    REE ESIOS Indicator IDs.

    Full list: https://api.esios.ree.es/indicators
    """
    # Generation
    GENERATION_SOLAR = 10206          # Solar PV generation
    GENERATION_WIND = 10207           # Wind generation
    GENERATION_NUCLEAR = 10208        # Nuclear generation
    GENERATION_HYDRO = 10209          # Hydro generation
    GENERATION_CCGT = 10210           # Combined cycle gas
    GENERATION_COAL = 10211           # Coal generation
    GENERATION_COGENERATION = 10212   # Cogeneration

    # Demand
    DEMAND_ACTUAL = 10001             # Actual demand
    DEMAND_FORECAST = 10002           # Demand forecast
    DEMAND_PROGRAMMED = 10003         # Programmed demand

    # Prices
    PRICE_SPOT = 600                  # OMIE spot price
    PRICE_PVPC = 1001                 # PVPC tariff price

    # Emissions
    CO2_EMISSIONS = 10300             # CO2 emissions factor
    CO2_FREE_GENERATION = 10301       # CO2-free generation %

    # Exchanges
    EXCHANGE_FRANCE = 10101           # France interconnection
    EXCHANGE_PORTUGAL = 10102         # Portugal interconnection
    EXCHANGE_MOROCCO = 10103          # Morocco interconnection

    # Renewable %
    RENEWABLE_PERCENTAGE = 10400      # Renewable share


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class GenerationMix:
    """Current generation mix snapshot."""
    timestamp: datetime
    total_mw: float
    solar_mw: float
    wind_mw: float
    nuclear_mw: float
    hydro_mw: float
    gas_ccgt_mw: float
    coal_mw: float
    cogeneration_mw: float
    other_mw: float

    @property
    def renewable_mw(self) -> float:
        """Total renewable generation."""
        return self.solar_mw + self.wind_mw + self.hydro_mw

    @property
    def renewable_percentage(self) -> float:
        """Renewable share of total."""
        if self.total_mw == 0:
            return 0.0
        return self.renewable_mw / self.total_mw * 100

    @property
    def co2_intensity_estimate(self) -> float:
        """
        Estimate CO2 intensity based on generation mix.

        Emission factors (kg CO2/MWh):
        - Solar: 0
        - Wind: 0
        - Nuclear: 0
        - Hydro: 0
        - Gas CCGT: 350
        - Coal: 900
        - Cogeneration: 400
        """
        if self.total_mw == 0:
            return 0.0

        emissions_mwh = (
            self.gas_ccgt_mw * 350 +
            self.coal_mw * 900 +
            self.cogeneration_mw * 400 +
            self.other_mw * 300
        )

        return emissions_mwh / self.total_mw / 1000  # Convert to kg/kWh


@dataclass
class DemandData:
    """Demand data snapshot."""
    timestamp: datetime
    actual_mw: float
    forecast_mw: float
    programmed_mw: float

    @property
    def forecast_error_pct(self) -> float:
        """Forecast error as percentage."""
        if self.forecast_mw == 0:
            return 0.0
        return abs(self.actual_mw - self.forecast_mw) / self.forecast_mw * 100


@dataclass
class PriceData:
    """Electricity price data."""
    timestamp: datetime
    spot_eur_mwh: float
    pvpc_eur_kwh: float

    @property
    def spot_eur_kwh(self) -> float:
        """Spot price in EUR/kWh."""
        return self.spot_eur_mwh / 1000


@dataclass
class REESnapshot:
    """Complete REE data snapshot."""
    timestamp: datetime
    generation: GenerationMix
    demand: DemandData
    price: PriceData
    co2_intensity: float
    renewable_pct: float


# =============================================================================
# REE ADAPTER
# =============================================================================

class REEAdapter:
    """
    Adapter for REE (Red Eléctrica de España) APIs.

    Provides access to:
    - Real-time generation mix
    - Demand data (actual, forecast)
    - Spot and PVPC prices
    - CO2 emissions data

    Two API modes:
    1. ESIOS API (full access, requires token)
    2. Public API (limited, no auth required)
    """

    # API endpoints
    ESIOS_BASE_URL = "https://api.esios.ree.es"
    PUBLIC_BASE_URL = "https://apidatos.ree.es/es/datos"

    def __init__(
        self,
        api_token: Optional[str] = None,
        use_public_api: bool = True,
        cache_duration_minutes: int = 5
    ):
        """
        Initialize REE adapter.

        Args:
            api_token: ESIOS API token (optional)
            use_public_api: If True, use public API (no auth)
            cache_duration_minutes: Cache duration for API calls
        """
        self.api_token = api_token
        self.use_public_api = use_public_api or api_token is None
        self.cache_duration = timedelta(minutes=cache_duration_minutes)

        # Response cache
        self._cache: Dict[str, Tuple[datetime, Any]] = {}

        self.connected = False

        logger.info(
            "REEAdapter initialized: mode=%s, cache=%d min",
            "public" if self.use_public_api else "esios",
            cache_duration_minutes
        )

    def connect(self) -> bool:
        """
        Test API connectivity.

        Returns:
            True if API is reachable
        """
        try:
            # Test with a simple request
            if self.use_public_api:
                # Public API test
                self.connected = True  # Simulated for now
            else:
                # ESIOS API test
                self.connected = self.api_token is not None

            logger.info("REEAdapter connected: %s", self.connected)
            return self.connected

        except Exception as e:
            logger.error("REEAdapter connection failed: %s", e)
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from API."""
        self.connected = False
        logger.info("REEAdapter disconnected")

    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached value if still valid."""
        if key in self._cache:
            cached_time, cached_value = self._cache[key]
            if datetime.now() - cached_time < self.cache_duration:
                return cached_value
        return None

    def _set_cache(self, key: str, value: Any) -> None:
        """Set cache value."""
        self._cache[key] = (datetime.now(), value)

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Make API request (simulated for now).

        In production, would use requests library:
        ```python
        import requests
        headers = {"Authorization": f"Token token={self.api_token}"}
        response = requests.get(url, headers=headers, params=params)
        return response.json()
        ```
        """
        # Simulated response for development
        # In production, replace with actual API calls
        logger.debug("REE API request: %s, params=%s", endpoint, params)

        # Return simulated data
        return self._generate_simulated_data(endpoint)

    def _generate_simulated_data(self, endpoint: str) -> Dict:
        """Generate simulated REE data for development."""
        now = datetime.now()
        hour = now.hour

        # Simulate daily solar/demand patterns
        solar_factor = max(0, 1 - abs(hour - 13) / 7) if 6 <= hour <= 20 else 0
        demand_factor = 0.6 + 0.4 * (1 - abs(hour - 19) / 10)

        return {
            "timestamp": now.isoformat(),
            "generation": {
                "total": 35000 * demand_factor,
                "solar": 20000 * solar_factor,
                "wind": 8000 + 2000 * (hash(str(hour)) % 100) / 100,
                "nuclear": 7000,
                "hydro": 3000 + 1000 * solar_factor,
                "gas_ccgt": max(0, 35000 * demand_factor - 20000 * solar_factor - 8000 - 7000 - 3000),
                "coal": 500 if hour >= 18 else 0,
                "cogeneration": 2500,
                "other": 500,
            },
            "demand": {
                "actual": 35000 * demand_factor,
                "forecast": 35000 * demand_factor * 1.02,
                "programmed": 35000 * demand_factor * 0.98,
            },
            "price": {
                "spot": 50 + 100 * (1 - solar_factor) + 30 * demand_factor,
                "pvpc": (50 + 100 * (1 - solar_factor) + 30 * demand_factor) / 1000 + 0.05,
            },
        }

    # =========================================================================
    # GENERATION DATA
    # =========================================================================

    def get_generation_mix(
        self,
        dt: Optional[datetime] = None
    ) -> GenerationMix:
        """
        Get current generation mix.

        Args:
            dt: Datetime to query (default: now)

        Returns:
            GenerationMix object
        """
        if dt is None:
            dt = datetime.now()

        cache_key = f"generation_{dt.strftime('%Y%m%d%H')}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        data = self._make_request("/generation")
        if not data:
            # Return default values
            return GenerationMix(
                timestamp=dt,
                total_mw=30000,
                solar_mw=10000,
                wind_mw=8000,
                nuclear_mw=7000,
                hydro_mw=3000,
                gas_ccgt_mw=2000,
                coal_mw=0,
                cogeneration_mw=0,
                other_mw=0,
            )

        gen = data.get("generation", {})
        mix = GenerationMix(
            timestamp=dt,
            total_mw=gen.get("total", 30000),
            solar_mw=gen.get("solar", 10000),
            wind_mw=gen.get("wind", 8000),
            nuclear_mw=gen.get("nuclear", 7000),
            hydro_mw=gen.get("hydro", 3000),
            gas_ccgt_mw=gen.get("gas_ccgt", 2000),
            coal_mw=gen.get("coal", 0),
            cogeneration_mw=gen.get("cogeneration", 0),
            other_mw=gen.get("other", 0),
        )

        self._set_cache(cache_key, mix)
        return mix

    def get_solar_generation(self, dt: Optional[datetime] = None) -> float:
        """Get current solar generation in MW."""
        mix = self.get_generation_mix(dt)
        return mix.solar_mw

    def get_renewable_percentage(self, dt: Optional[datetime] = None) -> float:
        """Get current renewable generation percentage."""
        mix = self.get_generation_mix(dt)
        return mix.renewable_percentage

    # =========================================================================
    # DEMAND DATA
    # =========================================================================

    def get_demand(self, dt: Optional[datetime] = None) -> DemandData:
        """
        Get current demand data.

        Args:
            dt: Datetime to query (default: now)

        Returns:
            DemandData object
        """
        if dt is None:
            dt = datetime.now()

        cache_key = f"demand_{dt.strftime('%Y%m%d%H')}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        data = self._make_request("/demand")
        if not data:
            return DemandData(
                timestamp=dt,
                actual_mw=30000,
                forecast_mw=30000,
                programmed_mw=30000,
            )

        dem = data.get("demand", {})
        demand = DemandData(
            timestamp=dt,
            actual_mw=dem.get("actual", 30000),
            forecast_mw=dem.get("forecast", 30000),
            programmed_mw=dem.get("programmed", 30000),
        )

        self._set_cache(cache_key, demand)
        return demand

    # =========================================================================
    # PRICE DATA
    # =========================================================================

    def get_prices(self, dt: Optional[datetime] = None) -> PriceData:
        """
        Get current electricity prices.

        Args:
            dt: Datetime to query (default: now)

        Returns:
            PriceData object
        """
        if dt is None:
            dt = datetime.now()

        cache_key = f"price_{dt.strftime('%Y%m%d%H')}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        data = self._make_request("/price")
        if not data:
            return PriceData(
                timestamp=dt,
                spot_eur_mwh=80.0,
                pvpc_eur_kwh=0.15,
            )

        price_data = data.get("price", {})
        price = PriceData(
            timestamp=dt,
            spot_eur_mwh=price_data.get("spot", 80.0),
            pvpc_eur_kwh=price_data.get("pvpc", 0.15),
        )

        self._set_cache(cache_key, price)
        return price

    def get_pvpc_price(self, dt: Optional[datetime] = None) -> float:
        """Get current PVPC price in EUR/kWh."""
        return self.get_prices(dt).pvpc_eur_kwh

    # =========================================================================
    # CO2 DATA
    # =========================================================================

    def get_co2_intensity(self, dt: Optional[datetime] = None) -> float:
        """
        Get current CO2 intensity.

        Calculated from generation mix emission factors.

        Args:
            dt: Datetime to query

        Returns:
            CO2 intensity in kg/kWh
        """
        mix = self.get_generation_mix(dt)
        return mix.co2_intensity_estimate

    # =========================================================================
    # COMBINED SNAPSHOT
    # =========================================================================

    def get_snapshot(self, dt: Optional[datetime] = None) -> REESnapshot:
        """
        Get complete REE data snapshot.

        Args:
            dt: Datetime to query

        Returns:
            REESnapshot with all data
        """
        if dt is None:
            dt = datetime.now()

        generation = self.get_generation_mix(dt)
        demand = self.get_demand(dt)
        price = self.get_prices(dt)

        return REESnapshot(
            timestamp=dt,
            generation=generation,
            demand=demand,
            price=price,
            co2_intensity=generation.co2_intensity_estimate,
            renewable_pct=generation.renewable_percentage,
        )

    # =========================================================================
    # SOLAR SURPLUS DETECTION
    # =========================================================================

    def is_solar_surplus(
        self,
        threshold_mw: float = 5000,
        dt: Optional[datetime] = None
    ) -> Tuple[bool, float]:
        """
        Check if there is solar surplus (curtailment risk).

        Surplus = Solar generation > Demand - Other generation

        Args:
            threshold_mw: Minimum surplus to consider
            dt: Datetime to check

        Returns:
            (is_surplus, surplus_mw)
        """
        mix = self.get_generation_mix(dt)
        demand = self.get_demand(dt)

        # Calculate effective surplus
        # If solar > demand - baseload, there's surplus
        baseload = mix.nuclear_mw + mix.hydro_mw * 0.5  # Assume 50% hydro is baseload
        available_demand = demand.actual_mw - baseload
        surplus = mix.solar_mw - available_demand

        is_surplus = surplus >= threshold_mw
        return is_surplus, max(0, surplus)

    def get_optimal_consumption_windows(
        self,
        hours_ahead: int = 24
    ) -> List[Tuple[datetime, float, str]]:
        """
        Get optimal consumption windows for next N hours.

        Returns windows ranked by CO2 intensity (lowest first).

        Returns:
            List of (datetime, co2_intensity, recommendation)
        """
        windows = []
        now = datetime.now().replace(minute=0, second=0, microsecond=0)

        for h in range(hours_ahead):
            dt = now + timedelta(hours=h)
            intensity = self.get_co2_intensity(dt)

            if intensity < 0.05:
                recommendation = "OPTIMAL - High solar"
            elif intensity < 0.15:
                recommendation = "GOOD - Renewable dominant"
            elif intensity < 0.30:
                recommendation = "MODERATE"
            else:
                recommendation = "AVOID - High carbon"

            windows.append((dt, intensity, recommendation))

        # Sort by intensity
        windows.sort(key=lambda x: x[1])

        return windows


# =============================================================================
# MODULE-LEVEL SINGLETON
# =============================================================================

_ree_adapter: Optional[REEAdapter] = None


def get_ree_adapter(api_token: Optional[str] = None) -> REEAdapter:
    """Get the global REE adapter instance."""
    global _ree_adapter

    if _ree_adapter is None:
        _ree_adapter = REEAdapter(api_token=api_token)
        _ree_adapter.connect()

    return _ree_adapter
