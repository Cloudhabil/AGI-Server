"""
Cable Monitor - Core Engine
===========================

Applies traffic/grid mathematics to submarine cable threat detection.
Provides real-time monitoring and anomaly detection for critical
undersea infrastructure.

Mathematical Translation:
------------------------
Grid Stress:    S(t) = Σ(1/(capacity - demand)²) × exp(-λ×t)
Cable Threat:   T(t) = Σ(1/(baseline - anomaly)²) × exp(-λ×distance)

When Threat > GENESIS_CONSTANT (0.0022): Trigger alert
Expected attenuation: β = 23.6% per 100km (Brahim Security Constant)

Threat Sources:
- Acoustic anomalies (anchor drops, dragging, cutting)
- Vessel proximity (AIS correlation)
- Signal attenuation spikes
- Seismic activity
- Environmental changes

References:
- Distributed Acoustic Sensing: Hartog (2017)
- Submarine Cable Protection: ICPC Recommendations
- Brahim Resonance: publications/Brahims_Theorem_Final_Edition.tex

Author: GPIA Cognitive Ecosystem
Date: 2026-01-26
"""

from __future__ import annotations

import logging
import math
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Callable, Any

import numpy as np

# Import Brahim constants
try:
    from core.constants import (
        GENESIS_CONSTANT,
        BETA_SECURITY,
        PHI,
        BRAHIM_SEQUENCE,
        BRAHIM_SUM,
        BRAHIM_CENTER,
        REGULARITY_THRESHOLD,
    )
except ImportError:
    GENESIS_CONSTANT = 2 / 901
    BETA_SECURITY = math.sqrt(5) - 2
    PHI = (1 + math.sqrt(5)) / 2
    BRAHIM_SEQUENCE = (27, 42, 60, 75, 97, 117, 139, 154, 172, 187)  # Corrected 2026-01-26
    BRAHIM_SUM = 214
    BRAHIM_CENTER = 107
    REGULARITY_THRESHOLD = 0.0219

logger = logging.getLogger("cable.monitor")


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class SegmentType(Enum):
    """Types of cable segments."""
    DEEP_SEA = auto()         # >1000m depth, single armor
    SHALLOW_WATER = auto()    # <1000m, double armor
    SHORE_END = auto()        # Beach to 20m, heavy protection
    LANDING_STATION = auto()  # Terrestrial termination
    REPEATER = auto()         # Optical amplifier housing
    BRANCH_UNIT = auto()      # Multi-cable junction


class ThreatType(Enum):
    """Types of detected threats."""
    ANCHOR_DROP = auto()      # Sudden impact + dragging
    FISHING_ACTIVITY = auto() # Trawler nets
    VESSEL_PROXIMITY = auto() # Suspicious hovering
    SIGNAL_ANOMALY = auto()   # Unexpected attenuation
    SEISMIC_EVENT = auto()    # Earthquake/landslide
    SABOTAGE = auto()         # Intentional cutting
    ENVIRONMENTAL = auto()    # Current, temperature
    EQUIPMENT_FAULT = auto()  # Repeater/component failure
    UNKNOWN = auto()


class ThreatLevel(Enum):
    """Threat severity levels (color-coded like traffic)."""
    NOMINAL = "green"         # Normal operation
    ADVISORY = "blue"         # Monitoring increased
    WATCH = "yellow"          # Potential threat
    WARNING = "orange"        # Probable threat
    CRITICAL = "red"          # Active threat/damage


# Cable specifications
CABLE_SPECS = {
    "atlantic_crossing": {
        "length_km": 6600,
        "capacity_tbps": 200,
        "fiber_pairs": 16,
        "repeater_spacing_km": 80,
    },
    "pacific_crossing": {
        "length_km": 12000,
        "capacity_tbps": 180,
        "fiber_pairs": 12,
        "repeater_spacing_km": 60,
    },
    "mediterranean": {
        "length_km": 2000,
        "capacity_tbps": 100,
        "fiber_pairs": 8,
        "repeater_spacing_km": 100,
    },
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class GeoCoordinate:
    """Geographic coordinate with depth."""
    latitude: float
    longitude: float
    depth_m: float = 0.0

    def distance_to(self, other: GeoCoordinate) -> float:
        """Haversine distance in km."""
        R = 6371  # Earth radius km

        lat1, lat2 = math.radians(self.latitude), math.radians(other.latitude)
        dlat = math.radians(other.latitude - self.latitude)
        dlon = math.radians(other.longitude - self.longitude)

        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        return R * c

    def to_dict(self) -> Dict[str, float]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "depth_m": self.depth_m
        }


@dataclass
class CableSegment:
    """
    Universal abstraction for a cable segment.

    Analogous to GridNode in the grid optimizer.
    Each segment has a baseline state and current readings
    that can be compared for anomaly detection.
    """
    segment_id: str
    cable_id: str
    segment_type: SegmentType
    start_coord: GeoCoordinate
    end_coord: GeoCoordinate
    length_km: float
    depth_m: float

    # Baseline values (normal operation)
    baseline_attenuation_db: float = 0.2  # dB/km typical
    baseline_acoustic_level: float = 50.0  # dB ambient
    baseline_temperature_c: float = 4.0  # Deep sea ~4°C

    # Current readings
    current_attenuation_db: float = 0.2
    current_acoustic_level: float = 50.0
    current_temperature_c: float = 4.0

    # Status
    last_update: Optional[datetime] = None
    threat_level: ThreatLevel = ThreatLevel.NOMINAL
    active_threats: List[str] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def attenuation_anomaly(self) -> float:
        """Deviation from baseline attenuation (0 = normal)."""
        if self.baseline_attenuation_db == 0:
            return 0.0
        return abs(self.current_attenuation_db - self.baseline_attenuation_db) / self.baseline_attenuation_db

    @property
    def acoustic_anomaly(self) -> float:
        """Deviation from baseline acoustic level."""
        if self.baseline_acoustic_level == 0:
            return 0.0
        return abs(self.current_acoustic_level - self.baseline_acoustic_level) / self.baseline_acoustic_level

    @property
    def thermal_anomaly(self) -> float:
        """Deviation from baseline temperature."""
        return abs(self.current_temperature_c - self.baseline_temperature_c)

    @property
    def composite_anomaly(self) -> float:
        """Weighted composite anomaly score."""
        return (
            0.5 * self.attenuation_anomaly +
            0.3 * self.acoustic_anomaly +
            0.2 * min(self.thermal_anomaly / 5.0, 1.0)  # Normalize thermal
        )

    def threat_contribution(self, epsilon: float = 0.01) -> float:
        """
        Calculate this segment's contribution to overall threat level.

        Formula: 1 / (1 - anomaly + epsilon)²

        Same structure as grid stress contribution.
        """
        anomaly = min(self.composite_anomaly, 0.99)  # Cap at 99%
        headroom = 1.0 - anomaly + epsilon
        return 1.0 / (headroom ** 2)


@dataclass
class ThreatEvent:
    """Detected threat event."""
    event_id: str
    timestamp: datetime
    segment_id: str
    cable_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    confidence: float  # 0-1
    location: GeoCoordinate
    description: str
    sensor_data: Dict[str, Any] = field(default_factory=dict)
    vessel_info: Optional[Dict[str, Any]] = None
    recommended_action: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "segment_id": self.segment_id,
            "cable_id": self.cable_id,
            "threat_type": self.threat_type.name,
            "threat_level": self.threat_level.value,
            "confidence": self.confidence,
            "location": self.location.to_dict(),
            "description": self.description,
            "recommended_action": self.recommended_action,
        }


@dataclass
class CableSnapshot:
    """Complete cable system state at a point in time."""
    timestamp: datetime
    cable_id: str
    segments: List[CableSegment]
    total_length_km: float
    threat_score: float
    threat_level: ThreatLevel
    active_events: List[ThreatEvent]
    health_percentage: float


# =============================================================================
# CABLE THREAT CALCULATOR
# =============================================================================

class CableThreatCalculator:
    """
    Calculates cable threat levels using Brahim mathematics.

    Grid Formula:
        Stress(t) = Σ(1/(capacity - demand)²) × exp(-λ×t)

    Cable Formula:
        Threat(t) = Σ(1/(1 - anomaly)²) × exp(-λ×distance)

    The decay factor applies to distance from threat source,
    acknowledging that acoustic/seismic events attenuate with distance.
    """

    def __init__(
        self,
        genesis_threshold: float = GENESIS_CONSTANT,
        decay_lambda: float = GENESIS_CONSTANT,
        beta_attenuation: float = BETA_SECURITY,
        epsilon: float = 0.01
    ):
        """
        Initialize threat calculator.

        Args:
            genesis_threshold: Threat level trigger threshold
            decay_lambda: Spatial decay factor
            beta_attenuation: Expected attenuation per 100km (23.6%)
            epsilon: Small value to prevent division by zero
        """
        self.genesis_threshold = genesis_threshold
        self.decay_lambda = decay_lambda
        self.beta_attenuation = beta_attenuation
        self.epsilon = epsilon

        # Threat history for temporal analysis
        self._threat_history: List[Tuple[datetime, float]] = []
        self._max_history = 1000

        logger.info(
            "CableThreatCalculator initialized: genesis=%.6f, beta=%.4f",
            genesis_threshold, beta_attenuation
        )

    def compute_instantaneous_threat(self, segments: List[CableSegment]) -> float:
        """
        Compute instantaneous threat level (no temporal smoothing).

        Formula: Σ(1/(1 - anomaly + ε)²) / N
        """
        if not segments:
            return 0.0

        total_threat = 0.0
        for segment in segments:
            contribution = segment.threat_contribution(self.epsilon)
            if math.isinf(contribution):
                return float('inf')
            total_threat += contribution

        return total_threat / len(segments)

    def compute_threat(
        self,
        segments: List[CableSegment],
        timestamp: Optional[datetime] = None
    ) -> float:
        """
        Compute temporally-smoothed threat level.

        Applies exponential smoothing to prevent alert oscillation.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        instant_threat = self.compute_instantaneous_threat(segments)

        if math.isinf(instant_threat):
            return instant_threat

        # Temporal smoothing
        if self._threat_history:
            weighted_threat = instant_threat
            total_weight = 1.0

            for hist_time, hist_threat in self._threat_history[-20:]:
                delta_t = (timestamp - hist_time).total_seconds()
                if delta_t > 0:
                    weight = math.exp(-self.decay_lambda * delta_t / 60)  # Per-minute decay
                    weighted_threat += weight * hist_threat
                    total_weight += weight

            smoothed_threat = weighted_threat / total_weight
        else:
            smoothed_threat = instant_threat

        self._threat_history.append((timestamp, smoothed_threat))
        if len(self._threat_history) > self._max_history:
            self._threat_history.pop(0)

        return smoothed_threat

    def classify_threat_level(self, threat: float) -> ThreatLevel:
        """
        Classify threat level based on score.

        Thresholds derived from Brahim constants:
        - < 0.5 × Genesis: NOMINAL
        - < 1.0 × Genesis: ADVISORY
        - < 2.0 × Genesis: WATCH
        - < 5.0 × Genesis: WARNING
        - >= 5.0 × Genesis: CRITICAL
        """
        g = self.genesis_threshold

        if threat < 0.5 * g:
            return ThreatLevel.NOMINAL
        elif threat < g:
            return ThreatLevel.ADVISORY
        elif threat < 2 * g:
            return ThreatLevel.WATCH
        elif threat < 5 * g:
            return ThreatLevel.WARNING
        else:
            return ThreatLevel.CRITICAL

    def identify_threat_type(
        self,
        segment: CableSegment,
        vessel_nearby: bool = False,
        seismic_activity: bool = False
    ) -> ThreatType:
        """
        Identify most likely threat type based on sensor patterns.

        Uses pattern matching similar to Kelimutu 3-Lake classification.
        """
        acoustic = segment.acoustic_anomaly
        attenuation = segment.attenuation_anomaly
        thermal = segment.thermal_anomaly

        # Pattern matching
        if seismic_activity and acoustic > 0.5:
            return ThreatType.SEISMIC_EVENT

        if vessel_nearby:
            if acoustic > 0.8 and attenuation > 0.5:
                return ThreatType.ANCHOR_DROP
            elif acoustic > 0.3:
                return ThreatType.FISHING_ACTIVITY
            else:
                return ThreatType.VESSEL_PROXIMITY

        if attenuation > 0.8 and acoustic > 0.6:
            return ThreatType.SABOTAGE

        if attenuation > 0.5 and acoustic < 0.2:
            return ThreatType.EQUIPMENT_FAULT

        if thermal > 3.0:
            return ThreatType.ENVIRONMENTAL

        if attenuation > 0.3:
            return ThreatType.SIGNAL_ANOMALY

        return ThreatType.UNKNOWN

    def get_hotspots(
        self,
        segments: List[CableSegment],
        top_n: int = 5
    ) -> List[Tuple[str, float, ThreatType]]:
        """
        Identify segments with highest threat contribution.

        Returns list of (segment_id, threat_contribution, likely_threat_type).
        """
        hotspots = []

        for segment in segments:
            contribution = segment.threat_contribution(self.epsilon)
            threat_type = self.identify_threat_type(segment)
            hotspots.append((segment.segment_id, contribution, threat_type))

        hotspots.sort(key=lambda x: x[1], reverse=True)
        return hotspots[:top_n]

    def validate_signal_attenuation(
        self,
        segment: CableSegment
    ) -> Tuple[bool, str]:
        """
        Validate if signal attenuation is within expected range.

        Expected: β = 23.6% per 100km (Brahim Security Constant)
        """
        expected_loss_db = segment.length_km * segment.baseline_attenuation_db
        actual_loss_db = segment.current_attenuation_db * segment.length_km

        # Allow 10% deviation
        tolerance = expected_loss_db * 0.1
        deviation = abs(actual_loss_db - expected_loss_db)

        if deviation <= tolerance:
            return True, f"Attenuation nominal: {actual_loss_db:.2f} dB"
        else:
            excess_pct = (deviation / expected_loss_db) * 100
            return False, f"Attenuation anomaly: {excess_pct:.1f}% above expected"


# =============================================================================
# BRAHIM CABLE MONITOR (Main Engine)
# =============================================================================

class BrahimCableMonitor:
    """
    Main cable monitoring engine using Brahim Onion Architecture.

    Layer 4 (Intelligence):
    - Resonance Formula for threat calculation
    - Pattern matching for threat classification
    - Predictive analysis using Method of Characteristics
    - Genesis threshold for alert triggering

    This wraps Layers 1-3 (infrastructure, abstraction, sensors).
    """

    def __init__(
        self,
        threat_calculator: Optional[CableThreatCalculator] = None,
        genesis_threshold: float = GENESIS_CONSTANT,
        alert_cooldown_seconds: float = 60.0
    ):
        """
        Initialize cable monitor.

        Args:
            threat_calculator: Custom calculator or use default
            genesis_threshold: Threat threshold for alerts
            alert_cooldown_seconds: Minimum time between alerts per segment
        """
        self.threat_calculator = threat_calculator or CableThreatCalculator()
        self.genesis_threshold = genesis_threshold
        self.alert_cooldown = timedelta(seconds=alert_cooldown_seconds)

        # Cable and segment registry
        self._cables: Dict[str, Dict] = {}
        self._segments: Dict[str, CableSegment] = {}

        # Event tracking
        self._events: List[ThreatEvent] = []
        self._last_alert: Dict[str, datetime] = {}
        self._max_events = 10000

        # Callbacks
        self._on_threat: List[Callable[[ThreatEvent], None]] = []

        logger.info(
            "BrahimCableMonitor initialized: genesis=%.6f, cooldown=%.0fs",
            genesis_threshold, alert_cooldown_seconds
        )

    # =========================================================================
    # CABLE & SEGMENT MANAGEMENT
    # =========================================================================

    def register_cable(
        self,
        cable_id: str,
        name: str,
        start_location: str,
        end_location: str,
        length_km: float,
        capacity_tbps: float,
        fiber_pairs: int = 8,
        owner: str = "",
        metadata: Optional[Dict] = None
    ) -> None:
        """Register a submarine cable for monitoring."""
        self._cables[cable_id] = {
            "cable_id": cable_id,
            "name": name,
            "start_location": start_location,
            "end_location": end_location,
            "length_km": length_km,
            "capacity_tbps": capacity_tbps,
            "fiber_pairs": fiber_pairs,
            "owner": owner,
            "metadata": metadata or {},
            "registered_at": datetime.utcnow().isoformat(),
        }
        logger.info("Registered cable: %s (%s)", name, cable_id)

    def register_segment(self, segment: CableSegment) -> None:
        """Register a cable segment for monitoring."""
        self._segments[segment.segment_id] = segment
        logger.debug(
            "Registered segment: %s (cable: %s, %.1f km)",
            segment.segment_id, segment.cable_id, segment.length_km
        )

    def update_segment(
        self,
        segment_id: str,
        current_attenuation_db: Optional[float] = None,
        current_acoustic_level: Optional[float] = None,
        current_temperature_c: Optional[float] = None,
        **metadata
    ) -> None:
        """Update segment readings (called by sensor adapters)."""
        if segment_id not in self._segments:
            logger.warning("Unknown segment: %s", segment_id)
            return

        segment = self._segments[segment_id]
        segment.last_update = datetime.utcnow()

        if current_attenuation_db is not None:
            segment.current_attenuation_db = current_attenuation_db

        if current_acoustic_level is not None:
            segment.current_acoustic_level = current_acoustic_level

        if current_temperature_c is not None:
            segment.current_temperature_c = current_temperature_c

        if metadata:
            segment.metadata.update(metadata)

    def get_segment(self, segment_id: str) -> Optional[CableSegment]:
        """Get segment by ID."""
        return self._segments.get(segment_id)

    def get_cable_segments(self, cable_id: str) -> List[CableSegment]:
        """Get all segments for a cable."""
        return [s for s in self._segments.values() if s.cable_id == cable_id]

    def get_all_segments(self) -> List[CableSegment]:
        """Get all registered segments."""
        return list(self._segments.values())

    # =========================================================================
    # THREAT ANALYSIS
    # =========================================================================

    def analyze(
        self,
        cable_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> CableSnapshot:
        """
        Perform complete threat analysis.

        Args:
            cable_id: Analyze specific cable (or all if None)
            timestamp: Analysis timestamp

        Returns:
            CableSnapshot with current state and threat assessment
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        if cable_id:
            segments = self.get_cable_segments(cable_id)
            cable_info = self._cables.get(cable_id, {})
        else:
            segments = self.get_all_segments()
            cable_id = "ALL_CABLES"
            cable_info = {}

        if not segments:
            return CableSnapshot(
                timestamp=timestamp,
                cable_id=cable_id,
                segments=[],
                total_length_km=0,
                threat_score=0,
                threat_level=ThreatLevel.NOMINAL,
                active_events=[],
                health_percentage=100.0
            )

        # Calculate totals
        total_length = sum(s.length_km for s in segments)

        # Calculate threat
        threat_score = self.threat_calculator.compute_threat(segments, timestamp)
        threat_level = self.threat_calculator.classify_threat_level(threat_score)

        # Calculate health (inverse of threat)
        health = max(0, 100 * (1 - min(threat_score / (5 * self.genesis_threshold), 1)))

        # Get active events
        active_events = self._detect_threats(segments, timestamp)

        # Update segment threat levels
        for segment in segments:
            segment.threat_level = self.threat_calculator.classify_threat_level(
                segment.threat_contribution(0.01)
            )

        snapshot = CableSnapshot(
            timestamp=timestamp,
            cable_id=cable_id,
            segments=segments,
            total_length_km=total_length,
            threat_score=threat_score,
            threat_level=threat_level,
            active_events=active_events,
            health_percentage=health
        )

        return snapshot

    def _detect_threats(
        self,
        segments: List[CableSegment],
        timestamp: datetime
    ) -> List[ThreatEvent]:
        """Detect threats across segments."""
        events = []

        for segment in segments:
            # Check if threat exceeds threshold
            contribution = segment.threat_contribution(0.01)
            threat_level = self.threat_calculator.classify_threat_level(contribution)

            if threat_level in (ThreatLevel.WATCH, ThreatLevel.WARNING, ThreatLevel.CRITICAL):
                # Check cooldown
                last_alert = self._last_alert.get(segment.segment_id)
                if last_alert and (timestamp - last_alert) < self.alert_cooldown:
                    continue

                # Classify threat
                threat_type = self.threat_calculator.identify_threat_type(segment)

                # Calculate confidence based on anomaly strength
                confidence = min(segment.composite_anomaly * 2, 1.0)

                # Generate event
                event = self._create_threat_event(
                    segment, threat_type, threat_level, confidence, timestamp
                )

                events.append(event)
                self._events.append(event)
                self._last_alert[segment.segment_id] = timestamp

                # Notify callbacks
                for callback in self._on_threat:
                    try:
                        callback(event)
                    except Exception as e:
                        logger.error("Threat callback error: %s", e)

                logger.warning(
                    "Threat detected: %s on %s (confidence: %.1f%%)",
                    threat_type.name, segment.segment_id, confidence * 100
                )

        return events

    def _create_threat_event(
        self,
        segment: CableSegment,
        threat_type: ThreatType,
        threat_level: ThreatLevel,
        confidence: float,
        timestamp: datetime
    ) -> ThreatEvent:
        """Create a threat event record."""
        # Generate event ID
        event_hash = hashlib.sha256(
            f"{segment.segment_id}{timestamp.isoformat()}{threat_type.name}".encode()
        ).hexdigest()[:12]

        # Midpoint of segment as event location
        location = GeoCoordinate(
            latitude=(segment.start_coord.latitude + segment.end_coord.latitude) / 2,
            longitude=(segment.start_coord.longitude + segment.end_coord.longitude) / 2,
            depth_m=segment.depth_m
        )

        # Generate description
        descriptions = {
            ThreatType.ANCHOR_DROP: "Sudden acoustic impact detected, consistent with anchor deployment",
            ThreatType.FISHING_ACTIVITY: "Sustained acoustic pattern suggests trawling activity",
            ThreatType.VESSEL_PROXIMITY: "Vessel detected in proximity to cable route",
            ThreatType.SIGNAL_ANOMALY: "Unexpected signal attenuation detected",
            ThreatType.SEISMIC_EVENT: "Seismic activity detected near cable segment",
            ThreatType.SABOTAGE: "High-confidence deliberate interference pattern",
            ThreatType.ENVIRONMENTAL: "Environmental conditions outside normal parameters",
            ThreatType.EQUIPMENT_FAULT: "Repeater or equipment malfunction indicated",
            ThreatType.UNKNOWN: "Anomaly detected, cause undetermined",
        }

        # Generate recommended action
        actions = {
            ThreatLevel.WATCH: "Increase monitoring frequency, prepare response team",
            ThreatLevel.WARNING: "Alert response team, contact nearby vessels",
            ThreatLevel.CRITICAL: "Dispatch cable ship, activate traffic rerouting",
        }

        return ThreatEvent(
            event_id=f"THR_{timestamp.strftime('%Y%m%d%H%M%S')}_{event_hash}",
            timestamp=timestamp,
            segment_id=segment.segment_id,
            cable_id=segment.cable_id,
            threat_type=threat_type,
            threat_level=threat_level,
            confidence=confidence,
            location=location,
            description=descriptions.get(threat_type, "Threat detected"),
            sensor_data={
                "attenuation_anomaly": segment.attenuation_anomaly,
                "acoustic_anomaly": segment.acoustic_anomaly,
                "thermal_anomaly": segment.thermal_anomaly,
                "composite_anomaly": segment.composite_anomaly,
            },
            recommended_action=actions.get(threat_level, "Monitor situation"),
        )

    # =========================================================================
    # PREDICTIVE ANALYSIS
    # =========================================================================

    def predict_propagation(
        self,
        event: ThreatEvent,
        hours_ahead: int = 24
    ) -> List[Tuple[str, float, float]]:
        """
        Predict threat propagation using Method of Characteristics.

        For seismic events or spreading damage, predicts which
        segments may be affected over time.

        Args:
            event: Source threat event
            hours_ahead: Prediction horizon

        Returns:
            List of (segment_id, time_to_impact_hours, probability)
        """
        predictions = []
        source_segment = self.get_segment(event.segment_id)

        if not source_segment:
            return predictions

        # Get adjacent segments
        cable_segments = self.get_cable_segments(source_segment.cable_id)

        for segment in cable_segments:
            if segment.segment_id == source_segment.segment_id:
                continue

            # Calculate distance
            distance_km = source_segment.start_coord.distance_to(segment.start_coord)

            # Propagation speed depends on threat type
            if event.threat_type == ThreatType.SEISMIC_EVENT:
                speed_km_h = 20  # Seabed disturbance
            elif event.threat_type == ThreatType.ANCHOR_DROP:
                speed_km_h = 0.5  # Dragging anchor
            else:
                speed_km_h = 0  # No propagation

            if speed_km_h > 0:
                time_to_impact = distance_km / speed_km_h
                if time_to_impact <= hours_ahead:
                    # Probability decays with distance (β attenuation)
                    probability = math.exp(-self.threat_calculator.beta_attenuation * distance_km / 100)
                    predictions.append((segment.segment_id, time_to_impact, probability))

        predictions.sort(key=lambda x: x[1])
        return predictions

    # =========================================================================
    # STATUS & REPORTING
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get current monitoring status."""
        all_segments = self.get_all_segments()

        if not all_segments:
            return {
                "status": "NO_CABLES",
                "cables_monitored": 0,
                "segments_monitored": 0,
            }

        snapshot = self.analyze()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": snapshot.threat_level.value.upper(),
            "cables_monitored": len(self._cables),
            "segments_monitored": len(all_segments),
            "total_length_km": snapshot.total_length_km,
            "health_percentage": snapshot.health_percentage,
            "threat_score": snapshot.threat_score,
            "genesis_threshold": self.genesis_threshold,
            "active_threats": len(snapshot.active_events),
            "hotspots": [
                {
                    "segment_id": h[0],
                    "threat_contribution": h[1],
                    "threat_type": h[2].name
                }
                for h in self.threat_calculator.get_hotspots(all_segments, 5)
            ],
            "brahim_metrics": {
                "genesis": GENESIS_CONSTANT,
                "beta": BETA_SECURITY,
                "phi": PHI,
                "sequence_sum": BRAHIM_SUM,
            }
        }

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def on_threat(
        self,
        callback: Callable[[ThreatEvent], None]
    ) -> None:
        """Register callback for threat events."""
        self._on_threat.append(callback)


# =============================================================================
# MODULE-LEVEL SINGLETON
# =============================================================================

_monitor: Optional[BrahimCableMonitor] = None


def get_cable_monitor() -> BrahimCableMonitor:
    """Get the global cable monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = BrahimCableMonitor()
    return _monitor
