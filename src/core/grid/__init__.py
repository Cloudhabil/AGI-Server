"""
Brahim Onion Grid Optimizer
===========================

Backwards-compatible grid demand optimization using traffic congestion
mathematics applied to electrical grid load balancing.

Architecture (Onion Layers):
- Layer 1: Existing Hardware (SCADA, PLCs, Smart Meters) - UNCHANGED
- Layer 2: Abstraction Layer (Unified GridNode interface)
- Layer 3: Protocol Adapters (Modbus, DNP3, IEC 61850, MQTT, REST)
- Layer 4: Brahim Intelligence (Resonance Formula, Method of Characteristics)

CO2 Reduction Mechanisms:
- Peak Shaving: 10-15% reduction
- Renewable Integration: 5-10% reduction
- EV Smart Charging: 5-8% reduction
- Demand Response: 3-5% reduction
- Total Potential: 20-35% CO2 reduction

Mathematical Foundation:
- Traffic Congestion: C(t) = Σ(1/(capacity - flow)²) × exp(-λ×t)
- Grid Stress: G(t) = Σ(1/(capacity - demand)²) × exp(-λ×t)
- Threshold: Genesis Constant (0.0022) triggers demand response
- Target: β compression (23.6% peak reduction)

Author: GPIA Cognitive Ecosystem
Date: 2026-01-26
Version: 1.0.0
"""

from .onion_grid_optimizer import (
    GridNode,
    NodeType,
    GridStressCalculator,
    OnionGridOptimizer,
    get_grid_optimizer,
)

from .protocol_adapters import (
    ProtocolAdapter,
    SimulationAdapter,
    ModbusAdapter,
    MQTTAdapter,
    RESTAdapter,
    CSVAdapter,
    get_adapter,
)

from .demand_response import (
    LoadShiftCommand,
    DemandResponseOrchestrator,
    CO2Calculator,
    get_demand_response_orchestrator,
)

# Spain-specific module
from .spain import (
    # Config
    SpainGridZone,
    SpainSeason,
    SPAIN_CO2_PROFILES,
    SpainCO2Calculator,
    get_current_season,
    get_solar_window,
    # REE
    REEIndicator,
    REEAdapter,
    get_ree_adapter,
    # Smart Meters
    IberdrolaAdapter,
    EndesaAdapter,
    SpanishSmartMeterAdapter,
    get_spanish_meter_adapter,
    # Optimizer
    SpainSolarOptimizer,
    SolarSurplusEvent,
    EVChargingSchedule,
    get_spain_optimizer,
)

# Germany-specific module (Brahim Calculator integrated)
from .germany import (
    # Config
    GermanyTSO,
    GermanySeason,
    GERMANY_TSO_DATA,
    GERMANY_CO2_PROFILES,
    DUNKELFLAUTE_CO2_PROFILE,
    BrahimGermanCalculator,
    get_renewable_window,
    is_dunkelflaute_risk,
    calculate_merit_order_price,
    # SMARD
    SMARDFilter,
    SMARDResolution,
    GenerationMix,
    GridStatus,
    PriceData,
    SMARDAdapter,
    get_smard_adapter,
    # Smart Meters
    GermanSmartMeterAdapter,
    EONAdapter,
    RWEAdapter,
    EnBWAdapter,
    VattenfallAdapter,
    get_german_meter_adapter,
    # Optimizer
    WindSurplusEvent,
    DunkelflaunteWarning,
    HeatPumpSchedule,
    GermanyWindOptimizer,
    get_germany_optimizer,
)

__all__ = [
    # Core
    "GridNode",
    "NodeType",
    "GridStressCalculator",
    "OnionGridOptimizer",
    "get_grid_optimizer",
    # Adapters
    "ProtocolAdapter",
    "SimulationAdapter",
    "ModbusAdapter",
    "MQTTAdapter",
    "RESTAdapter",
    "CSVAdapter",
    "get_adapter",
    # Demand Response
    "LoadShiftCommand",
    "DemandResponseOrchestrator",
    "CO2Calculator",
    "get_demand_response_orchestrator",
    # Spain Module
    "SpainGridZone",
    "SpainSeason",
    "SPAIN_CO2_PROFILES",
    "SpainCO2Calculator",
    "get_current_season",
    "get_solar_window",
    "REEIndicator",
    "REEAdapter",
    "get_ree_adapter",
    "IberdrolaAdapter",
    "EndesaAdapter",
    "SpanishSmartMeterAdapter",
    "get_spanish_meter_adapter",
    "SpainSolarOptimizer",
    "SolarSurplusEvent",
    "EVChargingSchedule",
    "get_spain_optimizer",
    # Germany Module (Brahim Calculator)
    "GermanyTSO",
    "GermanySeason",
    "GERMANY_TSO_DATA",
    "GERMANY_CO2_PROFILES",
    "DUNKELFLAUTE_CO2_PROFILE",
    "BrahimGermanCalculator",
    "get_renewable_window",
    "is_dunkelflaute_risk",
    "calculate_merit_order_price",
    "SMARDFilter",
    "SMARDResolution",
    "GenerationMix",
    "GridStatus",
    "PriceData",
    "SMARDAdapter",
    "get_smard_adapter",
    "GermanSmartMeterAdapter",
    "EONAdapter",
    "RWEAdapter",
    "EnBWAdapter",
    "VattenfallAdapter",
    "get_german_meter_adapter",
    "WindSurplusEvent",
    "DunkelflaunteWarning",
    "HeatPumpSchedule",
    "GermanyWindOptimizer",
    "get_germany_optimizer",
]

__version__ = "1.0.0"
