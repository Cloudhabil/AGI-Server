"""
Sensor Adapters - Cable Monitoring Data Sources
================================================

Layer 3 of the Brahim Onion Architecture for cable monitoring.

Provides adapters for various sensor systems used in submarine
cable monitoring, translating raw data to unified CableSegment format.

Supported Sensors:
- DAS (Distributed Acoustic Sensing): Fiber as 50,000+ sensors
- AIS (Automatic Identification System): Vessel tracking
- Seismic: Earthquake/seabed movement detection
- Signal Analysis: Optical signal quality monitoring
- Simulation: Testing without real sensors

Each adapter implements the same interface for seamless integration.

Author: GPIA Cognitive Ecosystem
Date: 2026-01-26
"""

from __future__ import annotations

import json
import logging
import math
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from .cable_monitor import (
    CableSegment,
    SegmentType,
    GeoCoordinate,
    ThreatType,
    BrahimCableMonitor,
)

logger = logging.getLogger("cable.sensor_adapters")


# =============================================================================
# BASE ADAPTER INTERFACE
# =============================================================================

class SensorAdapter(ABC):
    """
    Abstract base class for sensor adapters.

    All adapters must implement:
    - connect(): Establish connection to sensor system
    - disconnect(): Close connection
    - read_data(): Read current sensor data
    - update_segments(): Update segment states from sensor data
    """

    def __init__(self, monitor: Optional[BrahimCableMonitor] = None):
        """
        Initialize adapter.

        Args:
            monitor: Cable monitor to update segments in
        """
        self.monitor = monitor
        self.connected = False
        self._last_read: Optional[datetime] = None

    @property
    @abstractmethod
    def sensor_type(self) -> str:
        """Return sensor type identifier."""
        pass

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to sensor system."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close connection."""
        pass

    @abstractmethod
    def read_data(self) -> Dict[str, Any]:
        """
        Read raw sensor data.

        Returns:
            Dictionary of sensor readings
        """
        pass

    @abstractmethod
    def update_segments(self) -> int:
        """
        Read data and update segment states in monitor.

        Returns:
            Number of segments updated
        """
        pass


# =============================================================================
# DAS ADAPTER (Distributed Acoustic Sensing)
# =============================================================================

class DASAdapter(SensorAdapter):
    """
    Distributed Acoustic Sensing adapter.

    DAS uses the optical fiber itself as a sensor array, detecting
    acoustic vibrations along the entire cable length with meter-scale
    resolution.

    Capabilities:
    - Anchor drop detection (sudden high-amplitude impact)
    - Fishing activity (periodic trawl patterns)
    - Seabed movement (low-frequency rumble)
    - Marine life (whale songs, ship engines)

    Technical specs:
    - Spatial resolution: 1-10 meters
    - Frequency range: 0.01 Hz - 50 kHz
    - Update rate: 1 kHz typical
    - Range: Up to 100 km per interrogator
    """

    def __init__(
        self,
        monitor: Optional[BrahimCableMonitor] = None,
        interrogator_host: str = "localhost",
        interrogator_port: int = 5000,
        sampling_rate_hz: float = 1000.0,
        spatial_resolution_m: float = 5.0
    ):
        """
        Initialize DAS adapter.

        Args:
            monitor: Cable monitor instance
            interrogator_host: DAS interrogator hostname
            interrogator_port: DAS interrogator port
            sampling_rate_hz: Acoustic sampling rate
            spatial_resolution_m: Spatial resolution in meters
        """
        super().__init__(monitor)

        self.interrogator_host = interrogator_host
        self.interrogator_port = interrogator_port
        self.sampling_rate_hz = sampling_rate_hz
        self.spatial_resolution_m = spatial_resolution_m

        self._client = None
        self._baseline_profiles: Dict[str, np.ndarray] = {}

    @property
    def sensor_type(self) -> str:
        return "das"

    def connect(self) -> bool:
        """Connect to DAS interrogator."""
        try:
            # In production, this would connect to actual DAS hardware
            # For now, we simulate the connection
            logger.info(
                "DASAdapter connecting to %s:%d",
                self.interrogator_host, self.interrogator_port
            )

            # Simulate connection delay
            time.sleep(0.1)

            self.connected = True
            logger.info("DASAdapter connected successfully")
            return True

        except Exception as e:
            logger.error("DASAdapter connection failed: %s", e)
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from DAS interrogator."""
        if self._client:
            self._client = None
        self.connected = False
        logger.info("DASAdapter disconnected")

    def read_data(self) -> Dict[str, Any]:
        """
        Read acoustic data from DAS.

        Returns dictionary with:
        - channel_data: Acoustic amplitude per channel
        - timestamps: Sample timestamps
        - metadata: Interrogator status
        """
        if not self.connected:
            return {}

        # Simulate DAS data
        num_channels = 1000  # 1000 sensing points
        num_samples = int(self.sampling_rate_hz * 0.1)  # 100ms of data

        data = {
            "channels": num_channels,
            "samples_per_channel": num_samples,
            "sampling_rate_hz": self.sampling_rate_hz,
            "spatial_resolution_m": self.spatial_resolution_m,
            "timestamp": datetime.utcnow().isoformat(),
            "channel_rms": [
                50.0 + random.gauss(0, 5)  # dB, baseline ~50
                for _ in range(num_channels)
            ],
            "peak_amplitude": [
                55.0 + random.gauss(0, 10)
                for _ in range(num_channels)
            ],
            "dominant_frequency_hz": [
                random.choice([10, 50, 100, 500, 1000])
                for _ in range(num_channels)
            ],
        }

        return data

    def establish_baseline(self, duration_seconds: float = 60.0) -> None:
        """
        Establish acoustic baseline for anomaly detection.

        Args:
            duration_seconds: Duration to collect baseline data
        """
        if not self.connected:
            logger.warning("Cannot establish baseline: not connected")
            return

        logger.info("Establishing DAS baseline for %.0f seconds", duration_seconds)

        samples = []
        start_time = time.time()

        while time.time() - start_time < duration_seconds:
            data = self.read_data()
            if data:
                samples.append(data["channel_rms"])
            time.sleep(0.1)

        if samples:
            # Calculate mean and std for each channel
            samples_array = np.array(samples)
            self._baseline_profiles["mean"] = np.mean(samples_array, axis=0)
            self._baseline_profiles["std"] = np.std(samples_array, axis=0)

            logger.info(
                "DAS baseline established: %d channels, mean=%.1f dB",
                len(self._baseline_profiles["mean"]),
                np.mean(self._baseline_profiles["mean"])
            )

    def detect_anomalies(
        self,
        threshold_sigma: float = 3.0
    ) -> List[Tuple[int, float, str]]:
        """
        Detect acoustic anomalies relative to baseline.

        Args:
            threshold_sigma: Standard deviations for anomaly threshold

        Returns:
            List of (channel_index, anomaly_score, pattern_type)
        """
        if not self._baseline_profiles:
            logger.warning("No baseline established")
            return []

        data = self.read_data()
        if not data:
            return []

        anomalies = []
        baseline_mean = self._baseline_profiles["mean"]
        baseline_std = self._baseline_profiles["std"]

        for i, rms in enumerate(data["channel_rms"]):
            if i >= len(baseline_mean):
                break

            # Z-score
            z_score = (rms - baseline_mean[i]) / (baseline_std[i] + 1e-6)

            if abs(z_score) > threshold_sigma:
                # Classify pattern
                freq = data["dominant_frequency_hz"][i]
                peak = data["peak_amplitude"][i]

                if peak > 80 and freq > 500:
                    pattern = "impact"  # Anchor drop
                elif freq < 50:
                    pattern = "seismic"
                elif 100 < freq < 500:
                    pattern = "vessel"
                else:
                    pattern = "unknown"

                anomalies.append((i, z_score, pattern))

        return anomalies

    def update_segments(self) -> int:
        """Update monitor segments with DAS data."""
        if not self.monitor:
            return 0

        anomalies = self.detect_anomalies()
        data = self.read_data()

        if not data:
            return 0

        updated = 0
        segments = self.monitor.get_all_segments()

        # Map channels to segments (simplified)
        channels_per_segment = max(1, len(data["channel_rms"]) // max(1, len(segments)))

        for i, segment in enumerate(segments):
            start_ch = i * channels_per_segment
            end_ch = start_ch + channels_per_segment

            if start_ch < len(data["channel_rms"]):
                # Average acoustic level for this segment
                segment_channels = data["channel_rms"][start_ch:end_ch]
                avg_acoustic = np.mean(segment_channels) if segment_channels else 50.0

                # Check for anomalies in this segment's channels
                segment_anomalies = [a for a in anomalies if start_ch <= a[0] < end_ch]
                if segment_anomalies:
                    # Use maximum anomaly
                    max_anomaly = max(segment_anomalies, key=lambda x: abs(x[1]))
                    avg_acoustic = max(avg_acoustic, 50 + abs(max_anomaly[1]) * 5)

                self.monitor.update_segment(
                    segment.segment_id,
                    current_acoustic_level=avg_acoustic,
                    das_anomaly_count=len(segment_anomalies)
                )
                updated += 1

        self._last_read = datetime.utcnow()
        return updated


# =============================================================================
# AIS ADAPTER (Vessel Tracking)
# =============================================================================

class AISAdapter(SensorAdapter):
    """
    AIS (Automatic Identification System) adapter for vessel tracking.

    Monitors vessels near cable routes to detect:
    - Anchoring in cable protection zone
    - Fishing/trawling activity
    - Suspicious loitering
    - Speed/course changes indicating anchor deployment

    Data sources:
    - Coastal AIS receivers
    - Satellite AIS (S-AIS)
    - Commercial AIS feeds (MarineTraffic, VesselFinder)
    """

    def __init__(
        self,
        monitor: Optional[BrahimCableMonitor] = None,
        api_endpoint: str = "https://ais.example.com/api/v1",
        api_key: Optional[str] = None,
        proximity_threshold_nm: float = 1.0  # Nautical miles
    ):
        """
        Initialize AIS adapter.

        Args:
            monitor: Cable monitor instance
            api_endpoint: AIS API endpoint
            api_key: API authentication key
            proximity_threshold_nm: Alert threshold distance
        """
        super().__init__(monitor)

        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.proximity_threshold_nm = proximity_threshold_nm

        self._vessel_cache: Dict[str, Dict] = {}

    @property
    def sensor_type(self) -> str:
        return "ais"

    def connect(self) -> bool:
        """Connect to AIS data feed."""
        logger.info("AISAdapter connecting to %s", self.api_endpoint)
        self.connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from AIS feed."""
        self.connected = False
        logger.info("AISAdapter disconnected")

    def read_data(self) -> Dict[str, Any]:
        """Read current vessel positions near cable routes."""
        if not self.connected:
            return {}

        # Simulate AIS data
        vessels = []
        for i in range(random.randint(5, 20)):
            vessel = {
                "mmsi": f"21900000{i:02d}",
                "name": f"VESSEL_{i}",
                "type": random.choice(["cargo", "tanker", "fishing", "tug", "other"]),
                "latitude": 40.0 + random.uniform(-5, 5),
                "longitude": -30.0 + random.uniform(-10, 10),
                "speed_knots": random.uniform(0, 15),
                "course": random.uniform(0, 360),
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Simulate some vessels anchored (speed ~0)
            if random.random() < 0.1:
                vessel["speed_knots"] = random.uniform(0, 0.5)
                vessel["navigation_status"] = "anchored"
            else:
                vessel["navigation_status"] = "underway"

            vessels.append(vessel)

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "vessel_count": len(vessels),
            "vessels": vessels,
        }

    def check_proximity(
        self,
        vessel: Dict,
        segment: CableSegment
    ) -> Tuple[bool, float]:
        """
        Check if vessel is within proximity threshold of segment.

        Returns:
            (is_near, distance_nm)
        """
        vessel_coord = GeoCoordinate(
            latitude=vessel["latitude"],
            longitude=vessel["longitude"]
        )

        # Distance to segment midpoint
        segment_mid = GeoCoordinate(
            latitude=(segment.start_coord.latitude + segment.end_coord.latitude) / 2,
            longitude=(segment.start_coord.longitude + segment.end_coord.longitude) / 2
        )

        distance_km = vessel_coord.distance_to(segment_mid)
        distance_nm = distance_km / 1.852  # km to nautical miles

        return distance_nm <= self.proximity_threshold_nm, distance_nm

    def assess_vessel_threat(self, vessel: Dict) -> Tuple[float, str]:
        """
        Assess threat level of a vessel.

        Returns:
            (threat_score 0-1, reason)
        """
        score = 0.0
        reasons = []

        # Fishing vessels are higher risk
        if vessel.get("type") == "fishing":
            score += 0.3
            reasons.append("fishing_vessel")

        # Anchored/slow vessels
        if vessel.get("speed_knots", 10) < 1:
            score += 0.4
            reasons.append("stationary")

        # AIS status
        if vessel.get("navigation_status") == "anchored":
            score += 0.3
            reasons.append("anchored")

        return min(score, 1.0), "+".join(reasons) if reasons else "normal"

    def update_segments(self) -> int:
        """Update segments with vessel proximity data."""
        if not self.monitor:
            return 0

        data = self.read_data()
        if not data:
            return 0

        segments = self.monitor.get_all_segments()
        updated = 0

        for segment in segments:
            nearby_vessels = []
            max_threat = 0.0

            for vessel in data.get("vessels", []):
                is_near, distance = self.check_proximity(vessel, segment)
                if is_near:
                    threat, reason = self.assess_vessel_threat(vessel)
                    nearby_vessels.append({
                        "mmsi": vessel["mmsi"],
                        "name": vessel["name"],
                        "distance_nm": distance,
                        "threat": threat,
                        "reason": reason,
                    })
                    max_threat = max(max_threat, threat)

            # Update segment with vessel data
            self.monitor.update_segment(
                segment.segment_id,
                nearby_vessels=nearby_vessels,
                vessel_threat_score=max_threat,
            )
            updated += 1

        self._last_read = datetime.utcnow()
        return updated


# =============================================================================
# SEISMIC ADAPTER
# =============================================================================

class SeismicAdapter(SensorAdapter):
    """
    Seismic monitoring adapter for earthquake/landslide detection.

    Monitors seismic activity that could affect cable infrastructure:
    - Earthquakes (ground shaking)
    - Underwater landslides (turbidity currents)
    - Volcanic activity

    Data sources:
    - USGS Earthquake API
    - Regional seismic networks
    - Ocean bottom seismometers
    """

    def __init__(
        self,
        monitor: Optional[BrahimCableMonitor] = None,
        usgs_api: str = "https://earthquake.usgs.gov/fdsnws/event/1",
        min_magnitude: float = 4.0,
        radius_km: float = 500.0
    ):
        """
        Initialize seismic adapter.

        Args:
            monitor: Cable monitor instance
            usgs_api: USGS earthquake API endpoint
            min_magnitude: Minimum magnitude to report
            radius_km: Search radius around cables
        """
        super().__init__(monitor)

        self.usgs_api = usgs_api
        self.min_magnitude = min_magnitude
        self.radius_km = radius_km

        self._recent_events: List[Dict] = []

    @property
    def sensor_type(self) -> str:
        return "seismic"

    def connect(self) -> bool:
        """Connect to seismic data feed."""
        logger.info("SeismicAdapter initialized with min_magnitude=%.1f", self.min_magnitude)
        self.connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from seismic feed."""
        self.connected = False

    def read_data(self) -> Dict[str, Any]:
        """Read recent seismic events."""
        if not self.connected:
            return {}

        # Simulate seismic data
        # In production, would query USGS API
        events = []

        # Occasionally generate a seismic event
        if random.random() < 0.05:
            event = {
                "id": f"usgs_{int(time.time())}",
                "magnitude": random.uniform(4.0, 6.5),
                "depth_km": random.uniform(10, 100),
                "latitude": 35.0 + random.uniform(-10, 10),
                "longitude": -40.0 + random.uniform(-20, 20),
                "timestamp": datetime.utcnow().isoformat(),
                "type": random.choice(["earthquake", "landslide"]),
            }
            events.append(event)
            self._recent_events.append(event)

        # Keep only last 100 events
        self._recent_events = self._recent_events[-100:]

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "event_count": len(events),
            "events": events,
            "recent_events_24h": len(self._recent_events),
        }

    def calculate_impact(
        self,
        event: Dict,
        segment: CableSegment
    ) -> Tuple[float, float]:
        """
        Calculate seismic impact on a segment.

        Uses distance attenuation formula:
        Impact = M × exp(-β × distance / 100)

        Returns:
            (impact_score, distance_km)
        """
        event_coord = GeoCoordinate(
            latitude=event["latitude"],
            longitude=event["longitude"],
            depth_m=event.get("depth_km", 50) * 1000
        )

        segment_mid = GeoCoordinate(
            latitude=(segment.start_coord.latitude + segment.end_coord.latitude) / 2,
            longitude=(segment.start_coord.longitude + segment.end_coord.longitude) / 2,
            depth_m=segment.depth_m
        )

        distance_km = event_coord.distance_to(segment_mid)

        # Impact formula using Brahim beta
        from .cable_monitor import BETA_SECURITY
        magnitude = event.get("magnitude", 5.0)
        impact = magnitude * math.exp(-BETA_SECURITY * distance_km / 100)

        return impact, distance_km

    def update_segments(self) -> int:
        """Update segments with seismic data."""
        if not self.monitor:
            return 0

        data = self.read_data()
        segments = self.monitor.get_all_segments()
        updated = 0

        for segment in segments:
            max_impact = 0.0
            affecting_events = []

            for event in data.get("events", []) + self._recent_events[-10:]:
                impact, distance = self.calculate_impact(event, segment)
                if impact > 0.5:  # Significant impact threshold
                    affecting_events.append({
                        "event_id": event["id"],
                        "magnitude": event["magnitude"],
                        "distance_km": distance,
                        "impact": impact,
                    })
                    max_impact = max(max_impact, impact)

            self.monitor.update_segment(
                segment.segment_id,
                seismic_impact=max_impact,
                seismic_events=affecting_events,
            )
            updated += 1

        self._last_read = datetime.utcnow()
        return updated


# =============================================================================
# SIGNAL ANALYSIS ADAPTER
# =============================================================================

class SignalAnalysisAdapter(SensorAdapter):
    """
    Optical signal quality monitoring adapter.

    Monitors fiber optic signal parameters:
    - Attenuation (dB/km)
    - OSNR (Optical Signal-to-Noise Ratio)
    - BER (Bit Error Rate)
    - Chromatic dispersion
    - PMD (Polarization Mode Dispersion)

    Detects:
    - Fiber damage (sharp attenuation increase)
    - Repeater faults
    - Gradual degradation
    """

    def __init__(
        self,
        monitor: Optional[BrahimCableMonitor] = None,
        nms_host: str = "localhost",
        nms_port: int = 8080
    ):
        """
        Initialize signal analysis adapter.

        Args:
            monitor: Cable monitor instance
            nms_host: Network Management System host
            nms_port: NMS port
        """
        super().__init__(monitor)

        self.nms_host = nms_host
        self.nms_port = nms_port

        self._baseline_readings: Dict[str, Dict] = {}

    @property
    def sensor_type(self) -> str:
        return "signal_analysis"

    def connect(self) -> bool:
        """Connect to network management system."""
        logger.info("SignalAnalysisAdapter connecting to NMS at %s:%d", self.nms_host, self.nms_port)
        self.connected = True
        return True

    def disconnect(self) -> None:
        """Disconnect from NMS."""
        self.connected = False

    def read_data(self) -> Dict[str, Any]:
        """Read optical signal parameters."""
        if not self.connected:
            return {}

        # Simulate signal data for each segment
        segments = self.monitor.get_all_segments() if self.monitor else []

        readings = {}
        for segment in segments:
            # Normal values with small random variation
            attenuation = 0.2 + random.gauss(0, 0.02)  # dB/km
            osnr = 20.0 + random.gauss(0, 1.0)  # dB
            ber = 1e-12 * (1 + random.random())  # Bit error rate

            # Occasionally simulate degradation
            if random.random() < 0.02:
                attenuation *= 1.5  # 50% increase
                osnr *= 0.8  # 20% decrease

            readings[segment.segment_id] = {
                "attenuation_db_km": attenuation,
                "osnr_db": osnr,
                "ber": ber,
                "power_dbm": -10.0 + random.gauss(0, 0.5),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "segment_count": len(readings),
            "readings": readings,
        }

    def update_segments(self) -> int:
        """Update segments with signal data."""
        if not self.monitor:
            return 0

        data = self.read_data()
        updated = 0

        for segment_id, reading in data.get("readings", {}).items():
            self.monitor.update_segment(
                segment_id,
                current_attenuation_db=reading["attenuation_db_km"],
                osnr_db=reading["osnr_db"],
                ber=reading["ber"],
            )
            updated += 1

        self._last_read = datetime.utcnow()
        return updated


# =============================================================================
# SIMULATION ADAPTER (For Testing)
# =============================================================================

class SimulationSensorAdapter(SensorAdapter):
    """
    Simulation adapter for testing without real sensors.

    Generates synthetic sensor data with configurable:
    - Normal operation patterns
    - Anomaly injection
    - Threat simulation
    """

    def __init__(
        self,
        monitor: Optional[BrahimCableMonitor] = None,
        num_cables: int = 3,
        segments_per_cable: int = 10,
        anomaly_probability: float = 0.05
    ):
        """
        Initialize simulation adapter.

        Args:
            monitor: Cable monitor instance
            num_cables: Number of simulated cables
            segments_per_cable: Segments per cable
            anomaly_probability: Probability of anomaly per update
        """
        super().__init__(monitor)

        self.num_cables = num_cables
        self.segments_per_cable = segments_per_cable
        self.anomaly_probability = anomaly_probability

        self._initialized = False

    @property
    def sensor_type(self) -> str:
        return "simulation"

    def connect(self) -> bool:
        """Initialize simulation."""
        if not self._initialized and self.monitor:
            self._setup_cables()
            self._initialized = True

        self.connected = True
        logger.info(
            "SimulationSensorAdapter connected: %d cables, %d segments each",
            self.num_cables, self.segments_per_cable
        )
        return True

    def disconnect(self) -> None:
        """Disconnect simulation."""
        self.connected = False

    def _setup_cables(self) -> None:
        """Create simulated cables and segments."""
        cable_routes = [
            ("TAT-14", "USA", "UK", 40.7, -74.0, 51.5, -0.1),
            ("FLAG-Atlantic", "USA", "France", 40.7, -74.0, 48.8, -1.8),
            ("SEA-ME-WE-3", "France", "Singapore", 43.3, 5.4, 1.3, 103.8),
        ]

        for i in range(self.num_cables):
            if i < len(cable_routes):
                name, start_loc, end_loc, lat1, lon1, lat2, lon2 = cable_routes[i]
            else:
                name = f"SIM-CABLE-{i+1}"
                start_loc, end_loc = "PointA", "PointB"
                lat1, lon1 = 40 + i * 5, -60 + i * 10
                lat2, lon2 = 50 + i * 3, 0 + i * 5

            cable_id = f"CABLE_{i+1:03d}"

            # Register cable
            self.monitor.register_cable(
                cable_id=cable_id,
                name=name,
                start_location=start_loc,
                end_location=end_loc,
                length_km=1000 * (i + 1),
                capacity_tbps=100.0,
                fiber_pairs=8,
            )

            # Create segments
            for j in range(self.segments_per_cable):
                progress = j / self.segments_per_cable
                lat = lat1 + (lat2 - lat1) * progress
                lon = lon1 + (lon2 - lon1) * progress
                next_lat = lat1 + (lat2 - lat1) * (progress + 1/self.segments_per_cable)
                next_lon = lon1 + (lon2 - lon1) * (progress + 1/self.segments_per_cable)

                # Determine segment type based on position
                if j == 0 or j == self.segments_per_cable - 1:
                    seg_type = SegmentType.SHORE_END
                    depth = 50 + j * 10
                elif j < 2 or j >= self.segments_per_cable - 2:
                    seg_type = SegmentType.SHALLOW_WATER
                    depth = 200 + j * 50
                else:
                    seg_type = SegmentType.DEEP_SEA
                    depth = 3000 + random.uniform(-500, 500)

                segment = CableSegment(
                    segment_id=f"{cable_id}_SEG_{j+1:03d}",
                    cable_id=cable_id,
                    segment_type=seg_type,
                    start_coord=GeoCoordinate(lat, lon, depth),
                    end_coord=GeoCoordinate(next_lat, next_lon, depth),
                    length_km=100.0,
                    depth_m=depth,
                )

                self.monitor.register_segment(segment)

    def read_data(self) -> Dict[str, Any]:
        """Generate simulated sensor data."""
        if not self.connected:
            return {}

        segments = self.monitor.get_all_segments() if self.monitor else []
        readings = {}

        for segment in segments:
            # Base values
            attenuation = 0.2 + random.gauss(0, 0.01)
            acoustic = 50.0 + random.gauss(0, 3)
            temperature = 4.0 + random.gauss(0, 0.5)

            # Inject anomalies
            if random.random() < self.anomaly_probability:
                anomaly_type = random.choice(["attenuation", "acoustic", "thermal"])
                if anomaly_type == "attenuation":
                    attenuation *= random.uniform(1.5, 3.0)
                elif anomaly_type == "acoustic":
                    acoustic += random.uniform(20, 50)
                else:
                    temperature += random.uniform(2, 5)

            readings[segment.segment_id] = {
                "attenuation_db": attenuation,
                "acoustic_level": acoustic,
                "temperature_c": temperature,
            }

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "readings": readings,
        }

    def update_segments(self) -> int:
        """Update segments with simulated data."""
        if not self.monitor:
            return 0

        data = self.read_data()
        updated = 0

        for segment_id, reading in data.get("readings", {}).items():
            self.monitor.update_segment(
                segment_id,
                current_attenuation_db=reading["attenuation_db"],
                current_acoustic_level=reading["acoustic_level"],
                current_temperature_c=reading["temperature_c"],
            )
            updated += 1

        self._last_read = datetime.utcnow()
        return updated

    def inject_threat(
        self,
        segment_id: str,
        threat_type: str = "anchor_drop"
    ) -> None:
        """
        Inject a simulated threat for testing.

        Args:
            segment_id: Target segment
            threat_type: Type of threat to simulate
        """
        if not self.monitor:
            return

        segment = self.monitor.get_segment(segment_id)
        if not segment:
            logger.warning("Unknown segment: %s", segment_id)
            return

        if threat_type == "anchor_drop":
            self.monitor.update_segment(
                segment_id,
                current_acoustic_level=95.0,  # Very loud
                current_attenuation_db=0.5,   # Damage
            )
        elif threat_type == "fishing":
            self.monitor.update_segment(
                segment_id,
                current_acoustic_level=70.0,
            )
        elif threat_type == "seismic":
            self.monitor.update_segment(
                segment_id,
                current_acoustic_level=80.0,
                current_temperature_c=6.0,
            )

        logger.info("Injected %s threat at %s", threat_type, segment_id)


# =============================================================================
# ADAPTER FACTORY
# =============================================================================

ADAPTER_REGISTRY: Dict[str, type] = {
    "das": DASAdapter,
    "ais": AISAdapter,
    "seismic": SeismicAdapter,
    "signal": SignalAnalysisAdapter,
    "simulation": SimulationSensorAdapter,
}


def get_sensor_adapter(
    sensor_type: str,
    monitor: Optional[BrahimCableMonitor] = None,
    **kwargs
) -> SensorAdapter:
    """
    Factory function to create sensor adapters.

    Args:
        sensor_type: Sensor type (das, ais, seismic, signal, simulation)
        monitor: Cable monitor to update
        **kwargs: Sensor-specific configuration

    Returns:
        Configured SensorAdapter instance
    """
    sensor_type = sensor_type.lower()

    if sensor_type not in ADAPTER_REGISTRY:
        supported = ", ".join(ADAPTER_REGISTRY.keys())
        raise ValueError(f"Unknown sensor type: {sensor_type}. Supported: {supported}")

    adapter_class = ADAPTER_REGISTRY[sensor_type]
    return adapter_class(monitor=monitor, **kwargs)
