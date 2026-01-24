#!/usr/bin/env python3
"""
BOA Titan Explorer SDK
Brahim Onion Agent for Planetary Science & Observation Analysis

Applications:
- Exoplanet atmosphere modeling
- Methane cycle research
- Spacecraft mission planning
- Prebiotic chemistry
- Cryogenic engineering
"""

import math
import json
import hashlib
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Brahim Security Constants
PHI = (1 + math.sqrt(5)) / 2
BETA_SEC = math.sqrt(5) - 2
ALPHA_W = 1 / PHI**2


class Instrument(Enum):
    VOYAGER_ISS = "Voyager ISS"
    CASSINI_ISS = "Cassini ISS"
    CASSINI_VIMS = "Cassini VIMS"
    CASSINI_CIRS = "Cassini CIRS"
    CASSINI_UVIS = "Cassini UVIS"
    CASSINI_RADAR = "Cassini RADAR"


@dataclass
class BrahimSecurityLayer:
    """Brahim Onion encryption wrapper."""

    @staticmethod
    def encode(data: str, layers: int = 3) -> str:
        encoded = data
        for i in range(layers):
            salt = str(BETA_SEC * (i + 1))[:8]
            encoded = hashlib.sha256((salt + encoded).encode()).hexdigest()[:16] + encoded
        return encoded

    @staticmethod
    def sign_observation(obs_id: str) -> str:
        """Sign observation ID for integrity."""
        return hashlib.sha256((str(BETA_SEC) + obs_id).encode()).hexdigest()[:16]


@dataclass
class TitanObservation:
    """Single Titan observation record."""
    opus_id: str
    instrument: str
    target: str
    start_time: str
    duration: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TitanProperties:
    """Physical properties of Titan."""
    radius_km: float = 2574.7
    mass_kg: float = 1.3452e23
    orbital_period_days: float = 15.945
    surface_temp_k: float = 94
    surface_pressure_bar: float = 1.45
    atmosphere_composition: Dict[str, float] = None

    def __post_init__(self):
        if self.atmosphere_composition is None:
            self.atmosphere_composition = {
                "N2": 94.2,      # Nitrogen
                "CH4": 5.65,    # Methane
                "H2": 0.099,    # Hydrogen
                "C2H6": 0.001   # Ethane (trace)
            }

    @property
    def surface_gravity(self) -> float:
        """Surface gravity in m/s^2."""
        G = 6.674e-11
        return G * self.mass_kg / (self.radius_km * 1000)**2

    @property
    def escape_velocity(self) -> float:
        """Escape velocity in km/s."""
        G = 6.674e-11
        return math.sqrt(2 * G * self.mass_kg / (self.radius_km * 1000)) / 1000


class TitanAnalyzer:
    """
    Analyzer for Titan observations and atmospheric data.
    """

    def __init__(self):
        self.properties = TitanProperties()
        self.security = BrahimSecurityLayer()
        self.observations: List[TitanObservation] = []

    def load_observations(self, json_data: List[dict]) -> int:
        """Load observations from JSON data."""
        count = 0
        for record in json_data:
            try:
                obs = TitanObservation(
                    opus_id=record[0],
                    instrument=record[1],
                    target=record[3],
                    start_time=record[4],
                    duration=float(record[5])
                )
                self.observations.append(obs)
                count += 1
            except (IndexError, ValueError):
                continue
        return count

    def filter_by_instrument(self, instrument: str) -> List[TitanObservation]:
        """Filter observations by instrument."""
        return [o for o in self.observations if instrument.lower() in o.instrument.lower()]

    def filter_by_date_range(self, start: str, end: str) -> List[TitanObservation]:
        """Filter observations by date range (YYYY-MM-DD format)."""
        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d")

        filtered = []
        for obs in self.observations:
            try:
                obs_dt = datetime.strptime(obs.start_time[:10], "%Y-%m-%d")
                if start_dt <= obs_dt <= end_dt:
                    filtered.append(obs)
            except ValueError:
                continue
        return filtered

    def statistics(self) -> dict:
        """Compute observation statistics."""
        if not self.observations:
            return {"error": "No observations loaded"}

        # Count by instrument
        instruments: Dict[str, int] = {}
        total_duration = 0.0

        for obs in self.observations:
            inst = obs.instrument
            instruments[inst] = instruments.get(inst, 0) + 1
            total_duration += obs.duration

        # Date range
        dates = [o.start_time for o in self.observations if o.start_time]
        min_date = min(dates) if dates else "N/A"
        max_date = max(dates) if dates else "N/A"

        return {
            "total_observations": len(self.observations),
            "total_duration_hours": total_duration / 3600,
            "instruments": instruments,
            "date_range": {"start": min_date[:10], "end": max_date[:10]}
        }

    def methane_cycle_analysis(self, latitude: float) -> dict:
        """
        Analyze methane cycle at given latitude.
        Titan has methane lakes/seas in polar regions.
        """
        # Simplified model based on Cassini observations
        is_polar = abs(latitude) > 60

        if is_polar:
            lake_probability = 0.7 if latitude > 0 else 0.3  # More lakes in north
            evaporation_rate = 0.1  # mm/year (very slow)
            precipitation = "methane rain possible"
        else:
            lake_probability = 0.05
            evaporation_rate = 0.5
            precipitation = "rare"

        return {
            "latitude": latitude,
            "region": "polar" if is_polar else "equatorial",
            "lake_probability": lake_probability,
            "evaporation_rate_mm_year": evaporation_rate,
            "precipitation": precipitation,
            "surface_temp_k": self.properties.surface_temp_k,
            "methane_fraction": self.properties.atmosphere_composition["CH4"]
        }

    def mission_planning(self, target_latitude: float, target_longitude: float) -> dict:
        """
        Plan observation targeting for Titan mission.
        """
        # Orbital parameters
        orbital_period = self.properties.orbital_period_days

        # Visibility windows (simplified)
        windows_per_orbit = 2  # Can observe twice per orbit

        # Communication delay to Earth
        saturn_distance_au = 9.5  # Average
        light_delay_min = saturn_distance_au * 8.3  # 8.3 min per AU

        # Power considerations
        solar_flux = 15  # W/m^2 at Saturn (vs 1361 at Earth)

        return {
            "target": {
                "latitude": target_latitude,
                "longitude": target_longitude
            },
            "orbital_period_days": orbital_period,
            "observation_windows_per_orbit": windows_per_orbit,
            "communication_delay_minutes": round(light_delay_min, 1),
            "round_trip_delay_minutes": round(2 * light_delay_min, 1),
            "solar_flux_w_m2": solar_flux,
            "surface_gravity_m_s2": round(self.properties.surface_gravity, 3),
            "escape_velocity_km_s": round(self.properties.escape_velocity, 2)
        }

    def prebiotic_chemistry(self) -> dict:
        """
        Analyze conditions for prebiotic chemistry on Titan.
        """
        # Titan has complex organic chemistry
        conditions = {
            "temperature_k": self.properties.surface_temp_k,
            "pressure_bar": self.properties.surface_pressure_bar,
            "liquid_present": True,  # Methane/ethane lakes
            "energy_sources": [
                "Solar UV (attenuated)",
                "Cosmic rays",
                "Saturn magnetosphere"
            ],
            "organic_molecules_detected": [
                "Methane (CH4)",
                "Ethane (C2H6)",
                "Propane (C3H8)",
                "Acetylene (C2H2)",
                "Hydrogen cyanide (HCN)",
                "Tholins (complex organics)"
            ],
            "prebiotic_potential": "High - complex organics in liquid solvent",
            "comparison_to_early_earth": "Similar organic chemistry, different temperature"
        }
        return conditions

    def cryogenic_engineering(self) -> dict:
        """
        Provide cryogenic engineering data from Titan conditions.
        """
        return {
            "surface_temp_k": self.properties.surface_temp_k,
            "surface_temp_c": self.properties.surface_temp_k - 273.15,
            "methane_state": "liquid",
            "ethane_state": "liquid",
            "nitrogen_state": "gas (supercritical near surface)",
            "applications": [
                "LNG tank design validation",
                "Cryogenic pump testing",
                "Low-temp material science",
                "Superconductor environments"
            ],
            "methane_density_kg_m3": 450,  # Liquid at 94K
            "methane_viscosity_mPa_s": 0.2
        }


class TitanExplorerAPI:
    """REST API wrapper for Titan Explorer SDK."""

    def __init__(self):
        self.analyzer = TitanAnalyzer()
        self.version = "1.0.0"

    def handle_request(self, endpoint: str, params: dict) -> dict:
        """Handle API request."""

        if endpoint == "/properties":
            props = self.analyzer.properties
            return {
                "status": "ok",
                "radius_km": props.radius_km,
                "mass_kg": props.mass_kg,
                "surface_temp_k": props.surface_temp_k,
                "surface_pressure_bar": props.surface_pressure_bar,
                "surface_gravity_m_s2": props.surface_gravity,
                "escape_velocity_km_s": props.escape_velocity,
                "atmosphere": props.atmosphere_composition
            }

        elif endpoint == "/methane":
            latitude = params.get("latitude", 0)
            result = self.analyzer.methane_cycle_analysis(latitude)
            return {"status": "ok", **result}

        elif endpoint == "/mission":
            lat = params.get("latitude", 0)
            lon = params.get("longitude", 0)
            result = self.analyzer.mission_planning(lat, lon)
            return {"status": "ok", **result}

        elif endpoint == "/prebiotic":
            result = self.analyzer.prebiotic_chemistry()
            return {"status": "ok", **result}

        elif endpoint == "/cryogenic":
            result = self.analyzer.cryogenic_engineering()
            return {"status": "ok", **result}

        elif endpoint == "/statistics":
            result = self.analyzer.statistics()
            return {"status": "ok", **result}

        elif endpoint == "/health":
            return {
                "status": "ok",
                "version": self.version,
                "sdk": "BOA Titan Explorer",
                "security": "Brahim Onion Layer v1",
                "observations_loaded": len(self.analyzer.observations),
                "data_source": "NASA PDS / SETI Institute"
            }

        else:
            return {"status": "error", "message": f"Unknown endpoint: {endpoint}"}


# Main entry point
if __name__ == "__main__":
    api = TitanExplorerAPI()

    print("=" * 60)
    print("BOA TITAN EXPLORER SDK")
    print("=" * 60)

    # Test properties
    result = api.handle_request("/properties", {})
    print(f"\n/properties:")
    print(f"  Radius: {result['radius_km']} km")
    print(f"  Surface temp: {result['surface_temp_k']} K")
    print(f"  Gravity: {result['surface_gravity_m_s2']:.3f} m/s^2")

    # Test methane cycle
    result = api.handle_request("/methane", {"latitude": 75})
    print(f"\n/methane?latitude=75:")
    print(f"  Region: {result['region']}")
    print(f"  Lake probability: {result['lake_probability']}")

    # Test mission planning
    result = api.handle_request("/mission", {"latitude": 45, "longitude": 120})
    print(f"\n/mission:")
    print(f"  Comm delay: {result['communication_delay_minutes']} min")
    print(f"  Solar flux: {result['solar_flux_w_m2']} W/m^2")

    # Test prebiotic
    result = api.handle_request("/prebiotic", {})
    print(f"\n/prebiotic:")
    print(f"  Potential: {result['prebiotic_potential']}")

    result = api.handle_request("/health", {})
    print(f"\n/health:")
    print(f"  {result}")
