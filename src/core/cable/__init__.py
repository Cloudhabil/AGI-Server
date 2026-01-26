"""
Brahim Submarine Cable Monitoring System
=========================================

Applies traffic/grid congestion mathematics to submarine cable
threat detection and infrastructure protection.

Architecture (Onion Layers):
- Layer 1: Existing Infrastructure (Cables, Repeaters, Landing Stations)
- Layer 2: Abstraction Layer (CableSegment, ThreatEvent)
- Layer 3: Sensor Adapters (DAS, AIS, Sonar, Satellite, Seismic)
- Layer 4: Brahim Intelligence (Resonance Anomaly Detection)

Threat Detection Mechanisms:
- Distributed Acoustic Sensing (DAS): Fiber as 50,000+ sensors
- Vessel Tracking (AIS): Anchor/fishing detection
- Seabed Monitoring: Earthquake/landslide early warning
- Signal Analysis: Attenuation anomaly detection

Mathematical Foundation:
- Traffic Congestion: C(t) = Σ(1/(capacity - flow)²) × exp(-λ×t)
- Cable Threat: T(t) = Σ(1/(baseline - anomaly)²) × exp(-λ×distance)
- Threshold: Genesis Constant (0.0022) triggers alert
- Attenuation: β (23.6%) expected loss per 100km

Author: GPIA Cognitive Ecosystem
Date: 2026-01-26
Version: 1.0.0
"""

from .cable_monitor import (
    CableSegment,
    SegmentType,
    ThreatType,
    ThreatLevel,
    ThreatEvent,
    CableThreatCalculator,
    BrahimCableMonitor,
    get_cable_monitor,
)

from .sensor_adapters import (
    SensorAdapter,
    DASAdapter,
    AISAdapter,
    SeismicAdapter,
    SignalAnalysisAdapter,
    SimulationSensorAdapter,
    get_sensor_adapter,
)

from .threat_response import (
    ResponseAction,
    ThreatResponseOrchestrator,
    CableHealthReport,
    get_threat_response_orchestrator,
)

__all__ = [
    # Core
    "CableSegment",
    "SegmentType",
    "ThreatType",
    "ThreatLevel",
    "ThreatEvent",
    "CableThreatCalculator",
    "BrahimCableMonitor",
    "get_cable_monitor",
    # Adapters
    "SensorAdapter",
    "DASAdapter",
    "AISAdapter",
    "SeismicAdapter",
    "SignalAnalysisAdapter",
    "SimulationSensorAdapter",
    "get_sensor_adapter",
    # Response
    "ResponseAction",
    "ThreatResponseOrchestrator",
    "CableHealthReport",
    "get_threat_response_orchestrator",
]

__version__ = "1.0.0"
