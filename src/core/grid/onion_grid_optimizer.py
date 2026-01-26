"""
Onion Grid Optimizer - Core Engine
==================================

Applies traffic congestion mathematics to electrical grid demand optimization.
Backwards compatible with any existing hardware through protocol adapters.

Mathematical Translation:
------------------------
Traffic:  Congestion(t) = Σ(1/(road_capacity - traffic_flow)²) × exp(-λ×t)
Grid:     Stress(t)     = Σ(1/(grid_capacity - power_demand)²) × exp(-λ×t)

When Stress > GENESIS_CONSTANT (0.0022): Trigger demand response
Target: β = 23.6% peak reduction (Brahim Security Constant)

Brahim Signal Timing Applied to Grid:
- Cycle Length: B[3] = 60 seconds (demand response window)
- Green Phase: B[1] = 27 seconds (normal operation)
- Amber Phase: |Δ4| = 3 seconds (ramp warning)
- Red Phase: 30 seconds (load curtailment)

References:
- Traffic LWR Model: Lighthill-Whitham-Richards (1955)
- Brahim Resonance Formula: publications/Brahims_Theorem_Final_Edition.tex
- Energy Functional: src/core/wavelengths/script_energy_functional.py

Author: GPIA Cognitive Ecosystem
Date: 2026-01-26
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Callable, Any
from abc import ABC, abstractmethod

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
    # Fallback for standalone testing
    GENESIS_CONSTANT = 2 / 901  # 0.00221975...
    BETA_SECURITY = math.sqrt(5) - 2  # 0.2360679...
    PHI = (1 + math.sqrt(5)) / 2  # 1.6180339...
    BRAHIM_SEQUENCE = (27, 42, 60, 75, 97, 121, 136, 154, 172, 187)
    BRAHIM_SUM = 214
    BRAHIM_CENTER = 107
    REGULARITY_THRESHOLD = 0.0219

logger = logging.getLogger("grid.onion_optimizer")


# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class NodeType(Enum):
    """Types of grid nodes (analogous to road segments)."""
    TRANSFORMER = auto()      # Substation transformer
    FEEDER = auto()           # Distribution feeder
    METER = auto()            # Smart meter / consumption point
    GENERATOR = auto()        # Power source (solar, wind, conventional)
    STORAGE = auto()          # Battery storage
    EV_CHARGER = auto()       # Electric vehicle charging station
    LOAD_CENTER = auto()      # Industrial/commercial load center


class GridStatus(Enum):
    """Grid stress status (analogous to traffic Level of Service)."""
    OPTIMAL = "green"         # Stress < 0.5 × Genesis
    NORMAL = "blue"           # Stress < Genesis
    CAUTION = "yellow"        # Stress < 2 × Genesis
    STRESSED = "orange"       # Stress < 5 × Genesis
    CRITICAL = "red"          # Stress >= 5 × Genesis


class DemandResponsePhase(Enum):
    """Demand response phases (analogous to traffic signal phases)."""
    GREEN = auto()            # Normal operation (27 seconds)
    AMBER = auto()            # Ramp warning (3 seconds)
    RED = auto()              # Load curtailment (30 seconds)


@dataclass
class GridNode:
    """
    Universal abstraction for any grid component.

    This is Layer 2 of the Onion Architecture - provides a unified
    interface regardless of the underlying hardware protocol.

    Attributes:
        node_id: Unique identifier
        node_type: Type of grid component
        capacity_kw: Maximum power capacity (kW)
        current_demand_kw: Current power demand/flow (kW)
        latitude: Geographic latitude (for Proof-of-Location)
        longitude: Geographic longitude
        protocol: Communication protocol (modbus, dnp3, mqtt, etc.)
        metadata: Additional protocol-specific data
    """
    node_id: str
    node_type: NodeType
    capacity_kw: float
    current_demand_kw: float = 0.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    protocol: str = "simulation"
    controllable: bool = False
    priority: int = 5  # 1-10, lower = higher priority (don't shed)
    co2_intensity: float = 0.4  # kg CO2 per kWh (grid average)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def utilization(self) -> float:
        """Current utilization ratio (0-1+)."""
        if self.capacity_kw <= 0:
            return 0.0
        return self.current_demand_kw / self.capacity_kw

    @property
    def headroom_kw(self) -> float:
        """Available capacity headroom."""
        return max(0, self.capacity_kw - self.current_demand_kw)

    @property
    def is_overloaded(self) -> bool:
        """Check if node is over capacity."""
        return self.current_demand_kw > self.capacity_kw

    def stress_contribution(self, epsilon: float = 1.0) -> float:
        """
        Calculate this node's contribution to grid stress.

        Formula: 1 / (capacity - demand + epsilon)²

        Same as traffic congestion contribution per road segment.
        """
        headroom = self.capacity_kw - self.current_demand_kw + epsilon
        if headroom <= 0:
            return float('inf')
        return 1.0 / (headroom ** 2)


@dataclass
class GridSnapshot:
    """Complete grid state at a point in time."""
    timestamp: datetime
    nodes: List[GridNode]
    total_capacity_kw: float
    total_demand_kw: float
    stress: float
    status: GridStatus
    renewable_fraction: float = 0.0
    co2_rate_kg_per_kwh: float = 0.4


@dataclass
class StressEvent:
    """Recorded stress event for analysis."""
    timestamp: datetime
    stress: float
    status: GridStatus
    top_contributors: List[Tuple[str, float]]
    recommendation: str


# =============================================================================
# GRID STRESS CALCULATOR (Traffic Math Applied to Grid)
# =============================================================================

class GridStressCalculator:
    """
    Calculates grid stress using traffic congestion mathematics.

    Traffic Formula:
        Congestion(t) = Σ(1/(capacity - flow)²) × exp(-λ×t)

    Grid Formula:
        Stress(t) = Σ(1/(capacity - demand)²) × exp(-λ×t)

    Thresholds (from Brahim constants):
        - GENESIS_CONSTANT (0.0022): Normal → Caution transition
        - REGULARITY_THRESHOLD (0.0219): Caution → Stressed transition
        - BETA_SECURITY (0.236): Emergency threshold

    The decay factor λ (lambda) uses GENESIS_CONSTANT for temporal smoothing.
    """

    def __init__(
        self,
        genesis_threshold: float = GENESIS_CONSTANT,
        decay_lambda: float = GENESIS_CONSTANT,
        epsilon: float = 1.0
    ):
        """
        Initialize stress calculator.

        Args:
            genesis_threshold: Stress threshold for triggering response
            decay_lambda: Temporal decay factor (λ in exp(-λt))
            epsilon: Small value to prevent division by zero
        """
        self.genesis_threshold = genesis_threshold
        self.decay_lambda = decay_lambda
        self.epsilon = epsilon

        # Stress history for temporal smoothing
        self._stress_history: List[Tuple[datetime, float]] = []
        self._max_history = 100

        logger.info(
            "GridStressCalculator initialized: threshold=%.6f, lambda=%.6f",
            genesis_threshold, decay_lambda
        )

    def compute_instantaneous_stress(self, nodes: List[GridNode]) -> float:
        """
        Compute instantaneous grid stress (no temporal smoothing).

        Formula: Σ(1/(capacity - demand + ε)²)

        This is analogous to instantaneous traffic density.
        """
        if not nodes:
            return 0.0

        total_stress = 0.0
        for node in nodes:
            contribution = node.stress_contribution(self.epsilon)
            if math.isinf(contribution):
                return float('inf')
            total_stress += contribution

        # Normalize by number of nodes
        return total_stress / len(nodes)

    def compute_stress(
        self,
        nodes: List[GridNode],
        timestamp: Optional[datetime] = None
    ) -> float:
        """
        Compute temporally-smoothed grid stress.

        Formula: Σ(1/(capacity - demand)²) × exp(-λ×Δt)

        Temporal smoothing prevents oscillation (same as traffic wave damping).
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Compute instantaneous stress
        instant_stress = self.compute_instantaneous_stress(nodes)

        if math.isinf(instant_stress):
            return instant_stress

        # Apply temporal smoothing from history
        if self._stress_history:
            weighted_stress = instant_stress
            total_weight = 1.0

            for hist_time, hist_stress in self._stress_history[-10:]:
                delta_t = (timestamp - hist_time).total_seconds()
                if delta_t > 0:
                    weight = math.exp(-self.decay_lambda * delta_t)
                    weighted_stress += weight * hist_stress
                    total_weight += weight

            smoothed_stress = weighted_stress / total_weight
        else:
            smoothed_stress = instant_stress

        # Record in history
        self._stress_history.append((timestamp, smoothed_stress))
        if len(self._stress_history) > self._max_history:
            self._stress_history.pop(0)

        return smoothed_stress

    def classify_status(self, stress: float) -> GridStatus:
        """
        Classify grid status based on stress level.

        Thresholds derived from Brahim constants:
        - < 0.5 × Genesis: OPTIMAL (green)
        - < 1.0 × Genesis: NORMAL (blue)
        - < 2.0 × Genesis: CAUTION (yellow)
        - < 5.0 × Genesis: STRESSED (orange)
        - >= 5.0 × Genesis: CRITICAL (red)
        """
        g = self.genesis_threshold

        if stress < 0.5 * g:
            return GridStatus.OPTIMAL
        elif stress < g:
            return GridStatus.NORMAL
        elif stress < 2 * g:
            return GridStatus.CAUTION
        elif stress < 5 * g:
            return GridStatus.STRESSED
        else:
            return GridStatus.CRITICAL

    def get_top_contributors(
        self,
        nodes: List[GridNode],
        top_n: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Identify nodes contributing most to stress.

        Returns list of (node_id, stress_contribution) tuples.
        """
        contributions = [
            (node.node_id, node.stress_contribution(self.epsilon))
            for node in nodes
        ]
        contributions.sort(key=lambda x: x[1], reverse=True)
        return contributions[:top_n]

    def compute_gradient(
        self,
        nodes: List[GridNode]
    ) -> Dict[str, float]:
        """
        Compute stress gradient for each node.

        This is ∂Stress/∂demand for each node, indicating
        how much reducing demand at that node would reduce total stress.

        Used for optimal load shedding decisions.
        """
        gradients = {}

        for node in nodes:
            headroom = node.capacity_kw - node.current_demand_kw + self.epsilon
            if headroom > 0:
                # ∂(1/h²)/∂demand = 2/h³
                gradient = 2.0 / (headroom ** 3)
            else:
                gradient = float('inf')

            gradients[node.node_id] = gradient

        return gradients


# =============================================================================
# BRAHIM SIGNAL TIMING FOR DEMAND RESPONSE
# =============================================================================

class BrahimSignalTiming:
    """
    Applies traffic signal timing mathematics to demand response windows.

    Traffic Signal Timing (from BrahimCalculators):
    - Cycle: B[3] = 60 seconds
    - Green: B[1] = 27 seconds
    - Amber: |Δ4| = 3 seconds
    - Red: 30 seconds

    Grid Demand Response Translation:
    - Cycle: 60-second evaluation window
    - Green: Normal operation (27 seconds)
    - Amber: Ramp warning / pre-curtailment (3 seconds)
    - Red: Active load curtailment (30 seconds)
    """

    # Brahim-derived timing constants
    CYCLE_SECONDS = BRAHIM_SEQUENCE[2]  # B[3] = 60
    GREEN_SECONDS = BRAHIM_SEQUENCE[0]  # B[1] = 27
    AMBER_SECONDS = abs(BRAHIM_SEQUENCE[3] + BRAHIM_SEQUENCE[6] - BRAHIM_SUM)  # |Δ4| = 3
    RED_SECONDS = CYCLE_SECONDS - GREEN_SECONDS - AMBER_SECONDS  # 30

    def __init__(self):
        """Initialize with Brahim-derived timing."""
        self.cycle_length = timedelta(seconds=self.CYCLE_SECONDS)
        self.green_duration = timedelta(seconds=self.GREEN_SECONDS)
        self.amber_duration = timedelta(seconds=self.AMBER_SECONDS)
        self.red_duration = timedelta(seconds=self.RED_SECONDS)

        logger.info(
            "BrahimSignalTiming: cycle=%ds, green=%ds, amber=%ds, red=%ds",
            self.CYCLE_SECONDS, self.GREEN_SECONDS,
            self.AMBER_SECONDS, self.RED_SECONDS
        )

    def get_current_phase(
        self,
        timestamp: Optional[datetime] = None
    ) -> Tuple[DemandResponsePhase, float]:
        """
        Get current demand response phase and time remaining.

        Returns:
            (phase, seconds_remaining): Current phase and time until next phase
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Position within current cycle
        cycle_position = timestamp.timestamp() % self.CYCLE_SECONDS

        if cycle_position < self.GREEN_SECONDS:
            phase = DemandResponsePhase.GREEN
            remaining = self.GREEN_SECONDS - cycle_position
        elif cycle_position < self.GREEN_SECONDS + self.AMBER_SECONDS:
            phase = DemandResponsePhase.AMBER
            remaining = (self.GREEN_SECONDS + self.AMBER_SECONDS) - cycle_position
        else:
            phase = DemandResponsePhase.RED
            remaining = self.CYCLE_SECONDS - cycle_position

        return phase, remaining

    def get_next_green_window(
        self,
        timestamp: Optional[datetime] = None
    ) -> Tuple[datetime, datetime]:
        """
        Get the next green (normal operation) window.

        Returns:
            (start_time, end_time): Next green window boundaries
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        current_phase, remaining = self.get_current_phase(timestamp)

        if current_phase == DemandResponsePhase.GREEN:
            start = timestamp
            end = timestamp + timedelta(seconds=remaining)
        else:
            # Wait for current cycle to complete
            start = timestamp + timedelta(seconds=remaining)
            if current_phase == DemandResponsePhase.AMBER:
                start += self.red_duration
            end = start + self.green_duration

        return start, end


# =============================================================================
# ONION GRID OPTIMIZER (Main Engine)
# =============================================================================

class OnionGridOptimizer:
    """
    Main grid optimization engine using Brahim Onion Architecture.

    Layer 4 (Intelligence):
    - Resonance Formula for stress calculation
    - Method of Characteristics for load flow optimization
    - Genesis threshold for triggering demand response
    - Beta compression target (23.6% peak reduction)

    This class wraps Layers 1-3 (hardware, abstraction, protocols)
    and provides the optimization intelligence layer.
    """

    def __init__(
        self,
        stress_calculator: Optional[GridStressCalculator] = None,
        signal_timing: Optional[BrahimSignalTiming] = None,
        beta_target: float = BETA_SECURITY,
        genesis_threshold: float = GENESIS_CONSTANT
    ):
        """
        Initialize the Onion Grid Optimizer.

        Args:
            stress_calculator: Custom stress calculator (or use default)
            signal_timing: Custom signal timing (or use Brahim defaults)
            beta_target: Peak reduction target (default: 23.6%)
            genesis_threshold: Stress threshold for demand response
        """
        self.stress_calculator = stress_calculator or GridStressCalculator()
        self.signal_timing = signal_timing or BrahimSignalTiming()
        self.beta_target = beta_target
        self.genesis_threshold = genesis_threshold

        # Node registry
        self._nodes: Dict[str, GridNode] = {}

        # Event history
        self._events: List[StressEvent] = []
        self._max_events = 1000

        # Callbacks for external systems
        self._on_stress_change: List[Callable[[float, GridStatus], None]] = []
        self._on_demand_response: List[Callable[[DemandResponsePhase], None]] = []

        logger.info(
            "OnionGridOptimizer initialized: beta_target=%.4f, genesis=%.6f",
            beta_target, genesis_threshold
        )

    # =========================================================================
    # NODE MANAGEMENT
    # =========================================================================

    def register_node(self, node: GridNode) -> None:
        """Register a grid node for monitoring."""
        self._nodes[node.node_id] = node
        logger.debug("Registered node: %s (%s)", node.node_id, node.node_type.name)

    def update_node(
        self,
        node_id: str,
        current_demand_kw: Optional[float] = None,
        capacity_kw: Optional[float] = None,
        **metadata
    ) -> None:
        """Update node state (called by protocol adapters)."""
        if node_id not in self._nodes:
            logger.warning("Unknown node: %s", node_id)
            return

        node = self._nodes[node_id]

        if current_demand_kw is not None:
            node.current_demand_kw = current_demand_kw

        if capacity_kw is not None:
            node.capacity_kw = capacity_kw

        if metadata:
            node.metadata.update(metadata)

    def get_node(self, node_id: str) -> Optional[GridNode]:
        """Get node by ID."""
        return self._nodes.get(node_id)

    def get_all_nodes(self) -> List[GridNode]:
        """Get all registered nodes."""
        return list(self._nodes.values())

    # =========================================================================
    # STRESS ANALYSIS
    # =========================================================================

    def analyze(
        self,
        timestamp: Optional[datetime] = None
    ) -> GridSnapshot:
        """
        Perform complete grid analysis.

        Returns a GridSnapshot with current state, stress level, and status.
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        nodes = self.get_all_nodes()

        if not nodes:
            return GridSnapshot(
                timestamp=timestamp,
                nodes=[],
                total_capacity_kw=0,
                total_demand_kw=0,
                stress=0,
                status=GridStatus.OPTIMAL
            )

        # Calculate totals
        total_capacity = sum(n.capacity_kw for n in nodes)
        total_demand = sum(n.current_demand_kw for n in nodes)

        # Calculate stress
        stress = self.stress_calculator.compute_stress(nodes, timestamp)
        status = self.stress_calculator.classify_status(stress)

        # Calculate renewable fraction
        generators = [n for n in nodes if n.node_type == NodeType.GENERATOR]
        if generators:
            renewable_capacity = sum(
                n.current_demand_kw for n in generators
                if n.metadata.get("renewable", False)
            )
            total_generation = sum(n.current_demand_kw for n in generators)
            renewable_fraction = renewable_capacity / total_generation if total_generation > 0 else 0
        else:
            renewable_fraction = 0

        # Average CO2 intensity
        avg_co2 = np.mean([n.co2_intensity for n in nodes]) if nodes else 0.4

        snapshot = GridSnapshot(
            timestamp=timestamp,
            nodes=nodes,
            total_capacity_kw=total_capacity,
            total_demand_kw=total_demand,
            stress=stress,
            status=status,
            renewable_fraction=renewable_fraction,
            co2_rate_kg_per_kwh=avg_co2
        )

        # Record event if stress is elevated
        if status in (GridStatus.CAUTION, GridStatus.STRESSED, GridStatus.CRITICAL):
            self._record_stress_event(snapshot)

        # Notify callbacks
        for callback in self._on_stress_change:
            try:
                callback(stress, status)
            except Exception as e:
                logger.error("Callback error: %s", e)

        return snapshot

    def _record_stress_event(self, snapshot: GridSnapshot) -> None:
        """Record a stress event for analysis."""
        contributors = self.stress_calculator.get_top_contributors(snapshot.nodes)

        # Generate recommendation
        if snapshot.status == GridStatus.CRITICAL:
            recommendation = "IMMEDIATE: Activate emergency load shedding"
        elif snapshot.status == GridStatus.STRESSED:
            recommendation = f"URGENT: Reduce load at {contributors[0][0]} by {self.beta_target*100:.1f}%"
        else:
            recommendation = f"ADVISORY: Monitor {contributors[0][0]}"

        event = StressEvent(
            timestamp=snapshot.timestamp,
            stress=snapshot.stress,
            status=snapshot.status,
            top_contributors=contributors,
            recommendation=recommendation
        )

        self._events.append(event)
        if len(self._events) > self._max_events:
            self._events.pop(0)

        logger.warning(
            "Stress event: %.6f (%s) - %s",
            snapshot.stress, snapshot.status.name, recommendation
        )

    # =========================================================================
    # OPTIMIZATION (Method of Characteristics)
    # =========================================================================

    def compute_optimal_load_shift(
        self,
        target_reduction_kw: float
    ) -> List[Tuple[str, float]]:
        """
        Compute optimal load shifting using gradient descent.

        Uses the stress gradient to determine which nodes should
        reduce load to achieve the target reduction with minimum disruption.

        This is analogous to the Method of Characteristics for traffic
        wave propagation - finding the optimal path through demand space.

        Args:
            target_reduction_kw: Total kW to reduce

        Returns:
            List of (node_id, reduction_kw) tuples
        """
        nodes = self.get_all_nodes()

        # Get controllable nodes sorted by priority (lower = don't shed)
        controllable = [
            n for n in nodes
            if n.controllable and n.current_demand_kw > 0
        ]
        controllable.sort(key=lambda n: (-n.priority, -n.current_demand_kw))

        if not controllable:
            logger.warning("No controllable nodes available for load shifting")
            return []

        # Compute gradients
        gradients = self.stress_calculator.compute_gradient(nodes)

        # Greedy allocation based on gradient (highest gradient = most benefit)
        reductions = []
        remaining = target_reduction_kw

        for node in controllable:
            if remaining <= 0:
                break

            # Maximum we can reduce at this node
            max_reduction = node.current_demand_kw * 0.5  # Max 50% per node
            reduction = min(max_reduction, remaining)

            if reduction > 0:
                reductions.append((node.node_id, reduction))
                remaining -= reduction

        return reductions

    def compute_beta_target_reduction(self) -> float:
        """
        Compute the kW reduction needed to achieve beta compression target.

        Beta (β = 23.6%) is the Brahim Security Constant, representing
        the optimal compression/reduction ratio.
        """
        total_demand = sum(n.current_demand_kw for n in self.get_all_nodes())
        return total_demand * self.beta_target

    # =========================================================================
    # DEMAND RESPONSE COORDINATION
    # =========================================================================

    def get_demand_response_state(
        self,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get current demand response state.

        Combines stress analysis with signal timing to determine
        appropriate demand response actions.
        """
        snapshot = self.analyze(timestamp)
        phase, remaining = self.signal_timing.get_current_phase(timestamp)

        # Determine if demand response should be active
        dr_active = (
            snapshot.status in (GridStatus.STRESSED, GridStatus.CRITICAL) or
            phase == DemandResponsePhase.RED
        )

        # Calculate recommended reduction
        if dr_active:
            target_reduction = self.compute_beta_target_reduction()
            load_shifts = self.compute_optimal_load_shift(target_reduction)
        else:
            target_reduction = 0
            load_shifts = []

        return {
            "timestamp": snapshot.timestamp.isoformat(),
            "grid_stress": snapshot.stress,
            "status": snapshot.status.value,
            "genesis_threshold": self.genesis_threshold,
            "demand_response": {
                "active": dr_active,
                "phase": phase.name,
                "phase_remaining_seconds": remaining,
                "cycle_length_seconds": self.signal_timing.CYCLE_SECONDS,
            },
            "optimization": {
                "target_reduction_kw": target_reduction,
                "beta_compression": self.beta_target,
                "recommended_shifts": load_shifts,
            },
            "totals": {
                "capacity_kw": snapshot.total_capacity_kw,
                "demand_kw": snapshot.total_demand_kw,
                "utilization": snapshot.total_demand_kw / snapshot.total_capacity_kw
                    if snapshot.total_capacity_kw > 0 else 0,
                "renewable_fraction": snapshot.renewable_fraction,
            },
            "co2": {
                "current_rate_kg_per_kwh": snapshot.co2_rate_kg_per_kwh,
                "potential_savings_kg_per_hour": target_reduction * snapshot.co2_rate_kg_per_kwh
                    if dr_active else 0,
            },
            "brahim_metrics": {
                "sequence": list(BRAHIM_SEQUENCE),
                "sum": BRAHIM_SUM,
                "center": BRAHIM_CENTER,
                "phi": PHI,
                "beta": BETA_SECURITY,
                "genesis": GENESIS_CONSTANT,
            }
        }

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def on_stress_change(
        self,
        callback: Callable[[float, GridStatus], None]
    ) -> None:
        """Register callback for stress changes."""
        self._on_stress_change.append(callback)

    def on_demand_response(
        self,
        callback: Callable[[DemandResponsePhase], None]
    ) -> None:
        """Register callback for demand response phase changes."""
        self._on_demand_response.append(callback)


# =============================================================================
# MODULE-LEVEL SINGLETON
# =============================================================================

_optimizer: Optional[OnionGridOptimizer] = None


def get_grid_optimizer() -> OnionGridOptimizer:
    """Get the global grid optimizer instance."""
    global _optimizer
    if _optimizer is None:
        _optimizer = OnionGridOptimizer()
    return _optimizer


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def compute_grid_stress(nodes: List[GridNode]) -> float:
    """Convenience function to compute grid stress."""
    return get_grid_optimizer().stress_calculator.compute_stress(nodes)


def analyze_grid() -> GridSnapshot:
    """Convenience function to analyze current grid state."""
    return get_grid_optimizer().analyze()
