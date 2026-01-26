"""
Dimensional Convergence Engine
==============================

The Convergent Architecture: 12 dimensional agents connected by wormholes,
converging at the Grand Unification point Phi_12 = 1/phi^12 = 0.31%.

Architecture:
    12 AGENTS (native to dimensions 1-12)
            +
    WORMHOLES (connections between them, compress by beta/gamma)
            +
    KELIMUTU (energy routing for wormhole traversal)
            =
    CONVERGENCE at PHI_12 (where answers emerge)

Key Mathematical Foundation:
    - Each dimension n has constant 1/phi^n
    - Grand Unification: beta^4 = gamma^3 = 1/phi^12 (3D and 4D converge at dim 12)
    - Convergence strength U(n) = divisor count of n
    - Harmonic dimensions: 12 (6 divisors), 24 (8), 60 (12)

This module provides:
    1. DimensionalAgent - Agent native to a specific dimension
    2. WormholeConnection - Link between dimensions with compression
    3. KelimutuRouter - Energy routing for wormhole traversal
    4. ConvergenceOrchestrator - Collects results at Grand Unification
    5. DimensionalCalculator - High-level API for dimensional computation

Author: Elias Oulad Brahim
Date: 2026-01-26
"""

import math
import time
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Callable, Any, Union
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import queue


# =============================================================================
# FUNDAMENTAL CONSTANTS
# =============================================================================

PHI: float = (1 + math.sqrt(5)) / 2          # Golden ratio: 1.618...
PHI_INV: float = 1 / PHI                      # Compression: 0.618...
ALPHA: float = 1 / PHI**2                     # Wormhole attraction: 0.382...
BETA: float = 1 / PHI**3                      # Security constant: 0.236...
GAMMA: float = 1 / PHI**4                     # Tesseract constant: 0.146...

# Grand Unification Constants
PHI_12: float = 1 / PHI**12                   # First Grand Unification: 0.31%
PHI_24: float = 1 / PHI**24                   # Second Grand Unification
PHI_60: float = 1 / PHI**60                   # Full Convergence

# Dimensional Constant Generator
def dimensional_constant(n: int) -> float:
    """Return the dimensional constant 1/phi^n for dimension n."""
    return 1 / PHI**n


def divisor_count(n: int) -> int:
    """Return U(n) = number of divisors = convergence strength."""
    return sum(1 for d in range(1, n + 1) if n % d == 0)


def convergence_strength(dimension: int) -> int:
    """Return the convergence strength of a dimension."""
    return divisor_count(dimension)


# Brahim Sequence
BRAHIM_SEQUENCE: Tuple[int, ...] = (27, 42, 60, 75, 97, 117, 139, 154, 172, 187)
BRAHIM_CENTER: int = 107
BRAHIM_PAIR_SUM: int = 214


# =============================================================================
# ENUMS
# =============================================================================

class AgentState(Enum):
    """State of a dimensional agent."""
    IDLE = "idle"
    COMPUTING = "computing"
    TRANSMITTING = "transmitting"
    RECEIVING = "receiving"
    CONVERGING = "converging"
    COMPLETE = "complete"
    ERROR = "error"


class WormholeState(Enum):
    """State of a wormhole connection."""
    CLOSED = "closed"
    OPEN = "open"
    TRAVERSING = "traversing"
    COLLAPSED = "collapsed"


class ConvergenceLevel(Enum):
    """Level of convergence achieved."""
    NONE = 0
    PARTIAL = 1
    DIMENSIONAL = 2      # Single dimension complete
    HARMONIC = 3         # Multiple dimensions harmonized
    GRAND_UNIFIED = 4    # Full convergence at Phi_12


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DimensionalResult:
    """Result from a dimensional computation."""
    dimension: int
    value: float
    dimensional_constant: float
    compression_applied: float
    iterations: int
    timestamp: float = field(default_factory=time.time)


@dataclass
class WormholePacket:
    """Data packet for wormhole transmission."""
    source_dimension: int
    target_dimension: int
    payload: np.ndarray
    compression_factor: float
    hops: int = 0
    path: List[int] = field(default_factory=list)


@dataclass
class ConvergenceReport:
    """Report from convergence orchestrator."""
    final_value: float
    convergence_level: ConvergenceLevel
    participating_dimensions: List[int]
    total_hops: int
    compression_achieved: float
    phi_12_distance: float
    is_unified: bool


@dataclass
class KelimutuState:
    """State of the Kelimutu energy router."""
    total_energy: float
    active_wormholes: int
    energy_per_wormhole: Dict[Tuple[int, int], float] = field(default_factory=dict)
    thermal_state: str = "stable"


# =============================================================================
# DIMENSIONAL AGENT
# =============================================================================

class DimensionalAgent:
    """
    An agent native to a specific dimension.

    Each agent operates in its dimensional space with constant 1/phi^n,
    and can communicate with other dimensions via wormholes.

    Attributes:
        dimension: The dimension number (1-12)
        constant: The dimensional constant 1/phi^n
        convergence_strength: Number of divisors (paths to this dimension)
    """

    def __init__(self, dimension: int, name: Optional[str] = None):
        """
        Initialize a dimensional agent.

        Args:
            dimension: Dimension number (1-12)
            name: Optional agent name
        """
        if dimension < 1 or dimension > 12:
            raise ValueError(f"Dimension must be 1-12, got {dimension}")

        self.dimension = dimension
        self.name = name or f"Agent-D{dimension}"
        self.constant = dimensional_constant(dimension)
        self.convergence_strength_value = convergence_strength(dimension)
        self.state = AgentState.IDLE

        # Internal buffers
        self._input_buffer: queue.Queue = queue.Queue()
        self._output_buffer: queue.Queue = queue.Queue()
        self._results: List[DimensionalResult] = []

        # Computation function (can be customized)
        self._compute_fn: Optional[Callable] = None

    def set_compute_function(self, fn: Callable[[np.ndarray, int], np.ndarray]) -> None:
        """Set the computation function for this agent."""
        self._compute_fn = fn

    def compute(self, data: np.ndarray, iterations: int = 1) -> DimensionalResult:
        """
        Perform computation in this dimensional space.

        The default computation applies dimensional compression:
        output = data * (1/phi^n) * iterations

        Args:
            data: Input data array
            iterations: Number of compression iterations

        Returns:
            DimensionalResult with computed value
        """
        self.state = AgentState.COMPUTING

        try:
            if self._compute_fn is not None:
                result_data = self._compute_fn(data, iterations)
            else:
                # Default: dimensional compression
                result_data = data.copy()
                for _ in range(iterations):
                    result_data = result_data * self.constant

            compression = self.constant ** iterations

            result = DimensionalResult(
                dimension=self.dimension,
                value=float(np.sum(result_data)),
                dimensional_constant=self.constant,
                compression_applied=compression,
                iterations=iterations
            )

            self._results.append(result)
            self.state = AgentState.COMPLETE
            return result

        except Exception as e:
            self.state = AgentState.ERROR
            raise RuntimeError(f"Agent {self.name} computation failed: {e}")

    def transform_for_transmission(self, data: np.ndarray,
                                    target_dimension: int) -> WormholePacket:
        """
        Prepare data for wormhole transmission to another dimension.

        The compression factor depends on the dimensional distance.

        Args:
            data: Data to transmit
            target_dimension: Target dimension number

        Returns:
            WormholePacket ready for transmission
        """
        self.state = AgentState.TRANSMITTING

        dim_distance = abs(target_dimension - self.dimension)
        compression_factor = PHI_INV ** dim_distance

        compressed_data = data * compression_factor

        return WormholePacket(
            source_dimension=self.dimension,
            target_dimension=target_dimension,
            payload=compressed_data,
            compression_factor=compression_factor,
            hops=1,
            path=[self.dimension]
        )

    def receive_transmission(self, packet: WormholePacket) -> np.ndarray:
        """
        Receive data from a wormhole transmission.

        Args:
            packet: Incoming wormhole packet

        Returns:
            Decompressed data in this dimensional space
        """
        self.state = AgentState.RECEIVING

        # Apply dimensional scaling
        scale = self.constant / dimensional_constant(packet.source_dimension)
        received_data = packet.payload * scale

        self._input_buffer.put(received_data)
        return received_data

    def get_dimensional_signature(self) -> Dict[str, Any]:
        """Return the dimensional signature of this agent."""
        return {
            "dimension": self.dimension,
            "name": self.name,
            "constant": self.constant,
            "constant_percent": self.constant * 100,
            "convergence_strength": self.convergence_strength_value,
            "is_grand_unification": self.dimension == 12,
            "divisors": [d for d in range(1, self.dimension + 1)
                        if self.dimension % d == 0],
        }

    def __repr__(self) -> str:
        return (f"DimensionalAgent(dim={self.dimension}, "
                f"const=1/phi^{self.dimension}={self.constant:.6f}, "
                f"state={self.state.value})")


# =============================================================================
# WORMHOLE CONNECTION
# =============================================================================

class WormholeConnection:
    """
    A wormhole connection between two dimensions.

    The connection compresses data by beta or gamma depending on the
    dimensional distance, enabling efficient information transfer.
    """

    def __init__(self, dim_a: int, dim_b: int):
        """
        Create a wormhole connection between two dimensions.

        Args:
            dim_a: First dimension
            dim_b: Second dimension
        """
        self.dim_a = min(dim_a, dim_b)
        self.dim_b = max(dim_a, dim_b)
        self.distance = self.dim_b - self.dim_a
        self.state = WormholeState.CLOSED

        # Compression depends on dimensional distance
        self.compression_factor = self._compute_compression()

        # Traversal statistics
        self.traversal_count = 0
        self.total_data_transferred = 0.0

    def _compute_compression(self) -> float:
        """Compute the compression factor for this wormhole."""
        if self.distance <= 3:
            return BETA  # 3D compression
        elif self.distance <= 4:
            return GAMMA  # 4D compression
        else:
            return PHI_INV ** self.distance

    def open(self) -> bool:
        """Open the wormhole for traversal."""
        if self.state == WormholeState.COLLAPSED:
            return False
        self.state = WormholeState.OPEN
        return True

    def close(self) -> None:
        """Close the wormhole."""
        self.state = WormholeState.CLOSED

    def traverse(self, packet: WormholePacket,
                 direction: str = "forward") -> WormholePacket:
        """
        Traverse the wormhole with a data packet.

        Args:
            packet: Data packet to transmit
            direction: "forward" (a->b) or "backward" (b->a)

        Returns:
            Packet after traversal with compression applied
        """
        if self.state != WormholeState.OPEN:
            raise RuntimeError(f"Wormhole {self.dim_a}->{self.dim_b} is not open")

        self.state = WormholeState.TRAVERSING

        # Apply compression
        compressed_payload = packet.payload * self.compression_factor

        # Update packet
        new_source = self.dim_a if direction == "forward" else self.dim_b
        new_target = self.dim_b if direction == "forward" else self.dim_a

        new_packet = WormholePacket(
            source_dimension=new_source,
            target_dimension=new_target,
            payload=compressed_payload,
            compression_factor=packet.compression_factor * self.compression_factor,
            hops=packet.hops + 1,
            path=packet.path + [new_target]
        )

        # Update statistics
        self.traversal_count += 1
        self.total_data_transferred += np.sum(np.abs(packet.payload))

        self.state = WormholeState.OPEN
        return new_packet

    def get_nec_factor(self) -> float:
        """
        Get the Null Energy Condition factor for this wormhole.

        NEC > 0 means exotic matter is required (wormhole is traversable).
        """
        return PHI - self.compression_factor  # Always positive for golden ratio

    def __repr__(self) -> str:
        return (f"WormholeConnection({self.dim_a}<->{self.dim_b}, "
                f"compression={self.compression_factor:.4f}, "
                f"state={self.state.value})")


# =============================================================================
# KELIMUTU ENERGY ROUTER
# =============================================================================

class KelimutuRouter:
    """
    The Kelimutu Energy Router.

    Named after the tri-colored volcanic lakes of Kelimutu, this router
    manages energy distribution across wormhole connections, ensuring
    stable traversal and optimal routing.

    The router implements:
    1. Energy allocation per wormhole
    2. Thermal management (prevent collapse)
    3. Optimal path finding through dimensional space
    """

    def __init__(self, total_energy: float = 1.0):
        """
        Initialize the Kelimutu router.

        Args:
            total_energy: Total energy budget for routing
        """
        self.state = KelimutuState(
            total_energy=total_energy,
            active_wormholes=0
        )
        self._wormholes: Dict[Tuple[int, int], WormholeConnection] = {}
        self._energy_lock = threading.Lock()

    def register_wormhole(self, wormhole: WormholeConnection) -> None:
        """Register a wormhole with the router."""
        key = (wormhole.dim_a, wormhole.dim_b)
        self._wormholes[key] = wormhole

    def allocate_energy(self, dim_a: int, dim_b: int,
                        energy: float) -> bool:
        """
        Allocate energy to a wormhole connection.

        Args:
            dim_a: First dimension
            dim_b: Second dimension
            energy: Energy to allocate

        Returns:
            True if allocation successful
        """
        with self._energy_lock:
            if energy > self.state.total_energy:
                return False

            key = (min(dim_a, dim_b), max(dim_a, dim_b))
            self.state.energy_per_wormhole[key] = energy
            self.state.total_energy -= energy
            self.state.active_wormholes += 1
            return True

    def find_optimal_path(self, source: int, target: int) -> List[int]:
        """
        Find the optimal path from source to target dimension.

        Uses the golden ratio hierarchy to minimize total compression loss.

        Args:
            source: Source dimension
            target: Target dimension

        Returns:
            List of dimensions in the optimal path
        """
        if source == target:
            return [source]

        # For the 12-dimensional system, we use harmonic stepping
        path = [source]
        current = source

        while current != target:
            # Step size based on convergence strength
            if abs(target - current) >= 4:
                step = 4  # Gamma step (4D)
            elif abs(target - current) >= 3:
                step = 3  # Beta step (3D)
            else:
                step = 1  # Single step

            direction = 1 if target > current else -1
            next_dim = current + direction * min(step, abs(target - current))

            # Ensure we stay in bounds
            next_dim = max(1, min(12, next_dim))

            path.append(next_dim)
            current = next_dim

        return path

    def route_packet(self, packet: WormholePacket) -> WormholePacket:
        """
        Route a packet through the optimal wormhole path.

        Args:
            packet: Packet to route

        Returns:
            Packet after routing (with accumulated compression)
        """
        path = self.find_optimal_path(packet.source_dimension,
                                       packet.target_dimension)

        current_packet = packet

        for i in range(len(path) - 1):
            key = (min(path[i], path[i+1]), max(path[i], path[i+1]))

            if key in self._wormholes:
                wormhole = self._wormholes[key]
                if wormhole.state == WormholeState.CLOSED:
                    wormhole.open()

                direction = "forward" if path[i] < path[i+1] else "backward"
                current_packet = wormhole.traverse(current_packet, direction)

        return current_packet

    def compute_total_compression(self, path: List[int]) -> float:
        """Compute the total compression for a path."""
        compression = 1.0
        for i in range(len(path) - 1):
            dim_distance = abs(path[i+1] - path[i])
            compression *= PHI_INV ** dim_distance
        return compression

    def get_thermal_state(self) -> str:
        """Get the thermal state of the routing system."""
        active_ratio = self.state.active_wormholes / max(1, len(self._wormholes))

        if active_ratio < 0.3:
            return "cold"
        elif active_ratio < 0.7:
            return "stable"
        elif active_ratio < 0.9:
            return "warm"
        else:
            return "critical"

    def __repr__(self) -> str:
        return (f"KelimutuRouter(energy={self.state.total_energy:.4f}, "
                f"active={self.state.active_wormholes}, "
                f"thermal={self.get_thermal_state()})")


# =============================================================================
# CONVERGENCE ORCHESTRATOR
# =============================================================================

class ConvergenceOrchestrator:
    """
    The Convergence Orchestrator.

    Manages 12 dimensional agents and their wormhole connections,
    orchestrating computation to achieve convergence at Phi_12.

    The orchestrator implements:
    1. Agent lifecycle management
    2. Parallel computation across dimensions
    3. Result aggregation at Grand Unification point
    4. Convergence verification
    """

    def __init__(self, max_workers: int = 12):
        """
        Initialize the convergence orchestrator.

        Args:
            max_workers: Maximum parallel workers (default: 12 for 12 dimensions)
        """
        self.max_workers = max_workers

        # Create 12 dimensional agents
        self.agents: Dict[int, DimensionalAgent] = {
            d: DimensionalAgent(d) for d in range(1, 13)
        }

        # Create wormhole mesh
        self.wormholes: Dict[Tuple[int, int], WormholeConnection] = {}
        self._create_wormhole_mesh()

        # Initialize Kelimutu router
        self.router = KelimutuRouter(total_energy=12.0)  # 1 unit per dimension
        for wh in self.wormholes.values():
            self.router.register_wormhole(wh)

        # Results storage
        self._results: Dict[int, DimensionalResult] = {}
        self._convergence_history: List[ConvergenceReport] = []

    def _create_wormhole_mesh(self) -> None:
        """Create the wormhole mesh connecting all dimensions."""
        # Connect each dimension to neighbors and harmonics
        for d1 in range(1, 13):
            for d2 in range(d1 + 1, 13):
                # Connect if: adjacent, or harmonic relationship
                distance = d2 - d1
                is_harmonic = d2 % d1 == 0 or d1 % d2 == 0

                if distance <= 4 or is_harmonic:
                    key = (d1, d2)
                    self.wormholes[key] = WormholeConnection(d1, d2)

    def compute_parallel(self, data: np.ndarray,
                         dimensions: Optional[List[int]] = None,
                         iterations: int = 1) -> Dict[int, DimensionalResult]:
        """
        Compute in parallel across specified dimensions.

        Args:
            data: Input data array
            dimensions: Dimensions to compute in (default: all 12)
            iterations: Computation iterations per dimension

        Returns:
            Dictionary mapping dimension to result
        """
        if dimensions is None:
            dimensions = list(range(1, 13))

        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(
                    self.agents[d].compute,
                    data.copy(),
                    iterations
                ): d for d in dimensions
            }

            for future in as_completed(futures):
                dim = futures[future]
                try:
                    result = future.result()
                    results[dim] = result
                    self._results[dim] = result
                except Exception as e:
                    print(f"Dimension {dim} failed: {e}")

        return results

    def converge_at_phi12(self, data: np.ndarray,
                          method: str = "harmonic") -> ConvergenceReport:
        """
        Converge computation at the Grand Unification point (dimension 12).

        Args:
            data: Input data array
            method: "harmonic" (use harmonic dimensions) or "all" (use all 12)

        Returns:
            ConvergenceReport with final unified value
        """
        if method == "harmonic":
            # Use harmonic dimensions: 1, 2, 3, 4, 6, 12
            dimensions = [d for d in range(1, 13) if 12 % d == 0]
        else:
            dimensions = list(range(1, 13))

        # Phase 1: Parallel computation across dimensions
        results = self.compute_parallel(data, dimensions, iterations=1)

        # Phase 2: Route results to dimension 12 through wormholes
        total_hops = 0
        accumulated_value = 0.0

        for dim, result in results.items():
            if dim == 12:
                accumulated_value += result.value
                continue

            # Create packet for transmission
            packet = WormholePacket(
                source_dimension=dim,
                target_dimension=12,
                payload=np.array([result.value]),
                compression_factor=1.0,
                path=[dim]
            )

            # Route through Kelimutu
            final_packet = self.router.route_packet(packet)
            total_hops += final_packet.hops
            accumulated_value += np.sum(final_packet.payload)

        # Phase 3: Apply Grand Unification compression
        unified_value = accumulated_value * PHI_12
        phi_12_distance = abs(unified_value - PHI_12)

        # Determine convergence level
        if phi_12_distance < 1e-10:
            level = ConvergenceLevel.GRAND_UNIFIED
        elif len(dimensions) >= 6:
            level = ConvergenceLevel.HARMONIC
        elif len(dimensions) >= 1:
            level = ConvergenceLevel.DIMENSIONAL
        else:
            level = ConvergenceLevel.NONE

        report = ConvergenceReport(
            final_value=unified_value,
            convergence_level=level,
            participating_dimensions=dimensions,
            total_hops=total_hops,
            compression_achieved=PHI_12 ** len(dimensions),
            phi_12_distance=phi_12_distance,
            is_unified=level == ConvergenceLevel.GRAND_UNIFIED
        )

        self._convergence_history.append(report)
        return report

    def compute_with_beta_path(self, data: np.ndarray) -> DimensionalResult:
        """
        Compute using the beta (3D) path: dimensions 3, 6, 9, 12.

        This follows the beta constant hierarchy: beta^4 = 1/phi^12
        """
        beta_dimensions = [3, 6, 9, 12]
        results = self.compute_parallel(data, beta_dimensions)

        # Accumulate along beta path
        accumulated = 0.0
        for d in beta_dimensions:
            if d in results:
                accumulated += results[d].value * (BETA ** (d // 3))

        return DimensionalResult(
            dimension=12,
            value=accumulated,
            dimensional_constant=BETA,
            compression_applied=BETA ** 4,
            iterations=4
        )

    def compute_with_gamma_path(self, data: np.ndarray) -> DimensionalResult:
        """
        Compute using the gamma (4D) path: dimensions 4, 8, 12.

        This follows the gamma constant hierarchy: gamma^3 = 1/phi^12
        """
        gamma_dimensions = [4, 8, 12]
        results = self.compute_parallel(data, gamma_dimensions)

        # Accumulate along gamma path
        accumulated = 0.0
        for d in gamma_dimensions:
            if d in results:
                accumulated += results[d].value * (GAMMA ** (d // 4))

        return DimensionalResult(
            dimension=12,
            value=accumulated,
            dimensional_constant=GAMMA,
            compression_applied=GAMMA ** 3,
            iterations=3
        )

    def verify_grand_unification(self) -> Dict[str, Any]:
        """
        Verify the Grand Unification identity: beta^4 = gamma^3 = 1/phi^12.
        """
        beta_4 = BETA ** 4
        gamma_3 = GAMMA ** 3
        phi_12 = PHI_12

        return {
            "beta_4": beta_4,
            "gamma_3": gamma_3,
            "phi_12": phi_12,
            "beta_4_equals_gamma_3": abs(beta_4 - gamma_3) < 1e-14,
            "beta_4_equals_phi_12": abs(beta_4 - phi_12) < 1e-14,
            "gamma_3_equals_phi_12": abs(gamma_3 - phi_12) < 1e-14,
            "grand_unified": (abs(beta_4 - gamma_3) < 1e-14 and
                             abs(gamma_3 - phi_12) < 1e-14),
        }

    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the orchestrator."""
        agent_states = {d: a.state.value for d, a in self.agents.items()}

        return {
            "agents": {
                "total": 12,
                "states": agent_states,
                "idle": sum(1 for s in agent_states.values() if s == "idle"),
                "computing": sum(1 for s in agent_states.values() if s == "computing"),
            },
            "wormholes": {
                "total": len(self.wormholes),
                "open": sum(1 for w in self.wormholes.values()
                           if w.state == WormholeState.OPEN),
            },
            "router": {
                "energy": self.router.state.total_energy,
                "thermal": self.router.get_thermal_state(),
            },
            "convergences": len(self._convergence_history),
        }

    def __repr__(self) -> str:
        status = self.get_status()
        return (f"ConvergenceOrchestrator("
                f"agents={status['agents']['total']}, "
                f"wormholes={status['wormholes']['total']}, "
                f"convergences={status['convergences']})")


# =============================================================================
# DIMENSIONAL CALCULATOR (HIGH-LEVEL API)
# =============================================================================

class DimensionalCalculator:
    """
    High-level API for dimensional calculation.

    This is the main interface for performing calculations across
    12 dimensions using the Convergent Architecture.

    Example:
        calc = DimensionalCalculator()

        # Simple calculation
        result = calc.calculate([1, 2, 3, 4, 5])

        # Specify computation path
        result = calc.calculate_via_beta([1, 2, 3, 4, 5])
        result = calc.calculate_via_gamma([1, 2, 3, 4, 5])

        # Full convergence at Phi_12
        report = calc.converge_at_grand_unification([1, 2, 3, 4, 5])
    """

    def __init__(self):
        """Initialize the dimensional calculator."""
        self.orchestrator = ConvergenceOrchestrator()
        self._calculation_count = 0

    def calculate(self, data: Union[List, np.ndarray],
                  dimensions: Optional[List[int]] = None) -> Dict[int, float]:
        """
        Calculate across specified dimensions.

        Args:
            data: Input data (list or array)
            dimensions: Dimensions to use (default: all 12)

        Returns:
            Dictionary mapping dimension to result value
        """
        data = np.array(data, dtype=np.float64)
        results = self.orchestrator.compute_parallel(data, dimensions)
        self._calculation_count += 1

        return {d: r.value for d, r in results.items()}

    def calculate_via_beta(self, data: Union[List, np.ndarray]) -> float:
        """
        Calculate using the beta (3D) path.

        Path: 3 -> 6 -> 9 -> 12
        Compression: beta^4 = 1/phi^12

        Args:
            data: Input data

        Returns:
            Final converged value
        """
        data = np.array(data, dtype=np.float64)
        result = self.orchestrator.compute_with_beta_path(data)
        self._calculation_count += 1
        return result.value

    def calculate_via_gamma(self, data: Union[List, np.ndarray]) -> float:
        """
        Calculate using the gamma (4D) path.

        Path: 4 -> 8 -> 12
        Compression: gamma^3 = 1/phi^12

        Args:
            data: Input data

        Returns:
            Final converged value
        """
        data = np.array(data, dtype=np.float64)
        result = self.orchestrator.compute_with_gamma_path(data)
        self._calculation_count += 1
        return result.value

    def converge_at_grand_unification(self,
                                       data: Union[List, np.ndarray],
                                       method: str = "harmonic") -> ConvergenceReport:
        """
        Converge calculation at the Grand Unification point.

        Args:
            data: Input data
            method: "harmonic" or "all"

        Returns:
            ConvergenceReport with unified result
        """
        data = np.array(data, dtype=np.float64)
        report = self.orchestrator.converge_at_phi12(data, method)
        self._calculation_count += 1
        return report

    def compare_paths(self, data: Union[List, np.ndarray]) -> Dict[str, Any]:
        """
        Compare beta and gamma computation paths.

        Both paths should converge to the same value at Phi_12.

        Args:
            data: Input data

        Returns:
            Comparison results
        """
        data = np.array(data, dtype=np.float64)

        beta_result = self.calculate_via_beta(data)
        gamma_result = self.calculate_via_gamma(data)

        return {
            "beta_path": {
                "dimensions": [3, 6, 9, 12],
                "compression": BETA ** 4,
                "result": beta_result,
            },
            "gamma_path": {
                "dimensions": [4, 8, 12],
                "compression": GAMMA ** 3,
                "result": gamma_result,
            },
            "difference": abs(beta_result - gamma_result),
            "unified": abs(beta_result - gamma_result) < 1e-10,
            "grand_unification_verified": self.orchestrator.verify_grand_unification(),
        }

    def get_dimensional_constants(self) -> Dict[int, Dict[str, float]]:
        """Get all 12 dimensional constants."""
        return {
            d: {
                "constant": dimensional_constant(d),
                "constant_percent": dimensional_constant(d) * 100,
                "convergence_strength": convergence_strength(d),
            }
            for d in range(1, 13)
        }

    def get_status(self) -> Dict[str, Any]:
        """Get calculator status."""
        return {
            "calculations_performed": self._calculation_count,
            "orchestrator": self.orchestrator.get_status(),
            "grand_unification": self.orchestrator.verify_grand_unification(),
        }

    def __repr__(self) -> str:
        return f"DimensionalCalculator(calculations={self._calculation_count})"


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_calculator() -> DimensionalCalculator:
    """Create a new dimensional calculator instance."""
    return DimensionalCalculator()


def quick_calculate(data: Union[List, np.ndarray]) -> float:
    """Quick calculation converging at Phi_12."""
    calc = DimensionalCalculator()
    report = calc.converge_at_grand_unification(data)
    return report.final_value


def verify_grand_unification() -> Dict[str, Any]:
    """Verify the Grand Unification identity."""
    return ConvergenceOrchestrator().verify_grand_unification()


# =============================================================================
# MAIN (Demo)
# =============================================================================

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("DIMENSIONAL CONVERGENCE ENGINE - Test Suite")
    print("The Convergent Architecture: 12 Agents + Wormholes + Kelimutu")
    print("=" * 70)

    # Create calculator
    calc = DimensionalCalculator()
    print(f"\nCalculator created: {calc}")

    # 1. Dimensional Constants
    print("\n[1] DIMENSIONAL CONSTANTS (1/phi^n)")
    print("-" * 50)
    print(f"{'Dim':>4} | {'Constant':>12} | {'Percent':>8} | {'U(n)':>4} | Divisors")
    print("-" * 50)
    for d in range(1, 13):
        const = dimensional_constant(d)
        cs = convergence_strength(d)
        divisors = [i for i in range(1, d+1) if d % i == 0]
        marker = " <-- GRAND UNIFICATION" if d == 12 else ""
        print(f"{d:>4} | {const:>12.6f} | {const*100:>7.4f}% | {cs:>4} | {divisors}{marker}")

    # 2. Grand Unification Verification
    print("\n[2] GRAND UNIFICATION VERIFICATION")
    print("-" * 50)
    gu = verify_grand_unification()
    print(f"  beta^4  = {gu['beta_4']:.15f}")
    print(f"  gamma^3 = {gu['gamma_3']:.15f}")
    print(f"  1/phi^12 = {gu['phi_12']:.15f}")
    print(f"  beta^4 = gamma^3: {gu['beta_4_equals_gamma_3']}")
    print(f"  GRAND UNIFIED: {gu['grand_unified']}")

    # 3. Test Calculation
    print("\n[3] TEST CALCULATION")
    print("-" * 50)
    test_data = [100, 50, 200, 75, 150, 80, 120, 90, 160, 110]
    print(f"  Input: {test_data}")

    # Calculate across all dimensions
    results = calc.calculate(test_data)
    print(f"\n  Results per dimension:")
    for d in sorted(results.keys()):
        print(f"    Dim {d:2d}: {results[d]:.6f}")

    # 4. Path Comparison
    print("\n[4] BETA vs GAMMA PATH COMPARISON")
    print("-" * 50)
    comparison = calc.compare_paths(test_data)
    print(f"  Beta path (3->6->9->12):")
    print(f"    Compression: {comparison['beta_path']['compression']:.6f}")
    print(f"    Result: {comparison['beta_path']['result']:.6f}")
    print(f"  Gamma path (4->8->12):")
    print(f"    Compression: {comparison['gamma_path']['compression']:.6f}")
    print(f"    Result: {comparison['gamma_path']['result']:.6f}")
    print(f"  Difference: {comparison['difference']:.2e}")
    print(f"  Unified: {comparison['unified']}")

    # 5. Grand Unification Convergence
    print("\n[5] CONVERGENCE AT GRAND UNIFICATION (Phi_12)")
    print("-" * 50)
    report = calc.converge_at_grand_unification(test_data, method="harmonic")
    print(f"  Final Value: {report.final_value:.10f}")
    print(f"  Convergence Level: {report.convergence_level.name}")
    print(f"  Participating Dimensions: {report.participating_dimensions}")
    print(f"  Total Wormhole Hops: {report.total_hops}")
    print(f"  Compression Achieved: {report.compression_achieved:.6f}")
    print(f"  Distance to Phi_12: {report.phi_12_distance:.2e}")
    print(f"  Is Unified: {report.is_unified}")

    # 6. Orchestrator Status
    print("\n[6] ORCHESTRATOR STATUS")
    print("-" * 50)
    status = calc.orchestrator.get_status()
    print(f"  Agents: {status['agents']['total']} total")
    print(f"    - Idle: {status['agents']['idle']}")
    print(f"    - Computing: {status['agents']['computing']}")
    print(f"  Wormholes: {status['wormholes']['total']} total")
    print(f"    - Open: {status['wormholes']['open']}")
    print(f"  Router: energy={status['router']['energy']:.2f}, "
          f"thermal={status['router']['thermal']}")
    print(f"  Convergences: {status['convergences']}")

    # 7. Quick Calculate
    print("\n[7] QUICK CALCULATE")
    print("-" * 50)
    quick_result = quick_calculate([1, 2, 3, 4, 5])
    print(f"  Input: [1, 2, 3, 4, 5]")
    print(f"  Result: {quick_result:.10f}")

    print("\n" + "=" * 70)
    print("DIMENSIONAL CONVERGENCE ENGINE READY")
    print("12 Agents | Wormhole Mesh | Kelimutu Routing | Phi_12 Convergence")
    print("=" * 70)
