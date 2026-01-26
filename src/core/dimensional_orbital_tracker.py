"""
Dimensional Orbital Tracker
===========================

Tracks computation position within the Dimensional Onion structure,
monitoring orbital transitions through dimensional shells as they
converge toward the Grand Unification core (Φ₁₂).

Architecture:
    ╭─────────────────────────────────────╮
    │         DIMENSION 1 (outermost)     │
    │   ╭─────────────────────────────╮   │
    │   │       DIMENSION 3 (β)       │   │
    │   │   ╭─────────────────────╮   │   │
    │   │   │    DIMENSION 6      │   │   │
    │   │   │   ╭─────────────╮   │   │   │
    │   │   │   │  DIM 12     │   │   │   │
    │   │   │   │   Φ₁₂       │   │   │   │
    │   │   │   │   CORE      │   │   │   │
    │   │   │   ╰─────────────╯   │   │   │
    │   │   ╰─────────────────────╯   │   │
    │   ╰─────────────────────────────╯   │
    ╰─────────────────────────────────────╯

Concepts:
    - Shell/Layer: Dimension number (1-12)
    - Orbital radius: Dimensional constant 1/φⁿ
    - Orbital transition: Wormhole hop between dimensions
    - Decay to core: Convergence toward Φ₁₂
    - Orbital path: Beta (3→6→9→12) or Gamma (4→8→12)

Author: Elias Oulad Brahim
Date: 2026-01-26
"""

import math
import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any, Callable
from enum import Enum
from collections import deque
import threading


# =============================================================================
# CONSTANTS
# =============================================================================

PHI: float = (1 + math.sqrt(5)) / 2
PHI_INV: float = 1 / PHI
BETA: float = 1 / PHI**3
GAMMA: float = 1 / PHI**4
PHI_12: float = 1 / PHI**12  # Grand Unification Core

# Dimensional constants lookup
DIMENSIONAL_CONSTANTS: Dict[int, float] = {
    d: 1 / PHI**d for d in range(1, 13)
}

# Shell radii (normalized so dimension 1 = 1.0, dimension 12 = PHI_12)
SHELL_RADII: Dict[int, float] = {
    d: 1 / PHI**d for d in range(1, 13)
}

# Predefined orbital paths
ORBITAL_PATHS = {
    "beta": [3, 6, 9, 12],      # β⁴ path
    "gamma": [4, 8, 12],         # γ³ path
    "harmonic": [1, 2, 3, 4, 6, 12],  # Divisors of 12
    "sequential": list(range(1, 13)),  # All dimensions
    "fibonacci": [1, 2, 3, 5, 8],      # Fibonacci dimensions
}


# =============================================================================
# ENUMS
# =============================================================================

class OrbitalState(Enum):
    """State of the orbital tracker."""
    IDLE = "idle"
    TRACKING = "tracking"
    TRANSITIONING = "transitioning"
    AT_CORE = "at_core"
    DIVERGING = "diverging"


class TransitionType(Enum):
    """Type of dimensional transition."""
    INWARD = "inward"    # Toward core (smaller constant)
    OUTWARD = "outward"  # Away from core (larger constant)
    LATERAL = "lateral"  # Same shell level


class OrbitalPath(Enum):
    """Named orbital paths."""
    BETA = "beta"
    GAMMA = "gamma"
    HARMONIC = "harmonic"
    SEQUENTIAL = "sequential"
    CUSTOM = "custom"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class OrbitalPosition:
    """Current position in the dimensional onion."""
    dimension: int
    shell_radius: float
    distance_to_core: float
    angular_position: float  # 0-360 degrees around the shell
    depth_ratio: float       # 0.0 (outermost) to 1.0 (core)
    timestamp: float = field(default_factory=time.time)

    def __repr__(self) -> str:
        return (f"OrbitalPosition(dim={self.dimension}, "
                f"radius={self.shell_radius:.6f}, "
                f"depth={self.depth_ratio:.2%})")


@dataclass
class OrbitalTransition:
    """Record of a transition between dimensions."""
    from_dimension: int
    to_dimension: int
    transition_type: TransitionType
    compression_factor: float
    energy_cost: float
    timestamp: float = field(default_factory=time.time)

    @property
    def delta(self) -> int:
        """Dimensional change (positive = inward, negative = outward)."""
        return self.to_dimension - self.from_dimension


@dataclass
class OrbitalTrajectory:
    """Complete trajectory through dimensions."""
    path_name: str
    positions: List[OrbitalPosition]
    transitions: List[OrbitalTransition]
    start_dimension: int
    end_dimension: int
    total_compression: float
    convergence_achieved: bool
    duration: float


@dataclass
class OnionVisualization:
    """ASCII visualization of the dimensional onion."""
    ascii_art: str
    current_position: OrbitalPosition
    highlighted_path: List[int]


# =============================================================================
# DIMENSIONAL ORBITAL TRACKER
# =============================================================================

class DimensionalOrbitalTracker:
    """
    Tracks computation position within the Dimensional Onion structure.

    The tracker monitors:
    - Current dimensional shell (1-12)
    - Orbital radius (1/φⁿ)
    - Distance to Grand Unification core (Φ₁₂)
    - Transition history
    - Convergence progress

    Example:
        tracker = DimensionalOrbitalTracker()

        # Start tracking from dimension 3
        tracker.enter_dimension(3)

        # Transition to dimension 6
        tracker.transition_to(6)

        # Follow beta path to core
        tracker.follow_path("beta")

        # Check convergence
        print(tracker.convergence_progress())
    """

    def __init__(self, start_dimension: int = 1):
        """
        Initialize the orbital tracker.

        Args:
            start_dimension: Starting dimension (1-12)
        """
        self.state = OrbitalState.IDLE
        self._current_position: Optional[OrbitalPosition] = None
        self._position_history: deque = deque(maxlen=1000)
        self._transition_history: List[OrbitalTransition] = []
        self._active_path: Optional[str] = None
        self._path_index: int = 0

        # Callbacks for events
        self._on_transition: Optional[Callable] = None
        self._on_core_reached: Optional[Callable] = None

        # Thread safety
        self._lock = threading.Lock()

        # Initialize at start dimension
        if start_dimension:
            self.enter_dimension(start_dimension)

    # =========================================================================
    # POSITION MANAGEMENT
    # =========================================================================

    def enter_dimension(self, dimension: int, angular_position: float = 0.0) -> OrbitalPosition:
        """
        Enter a specific dimension (shell) in the onion.

        Args:
            dimension: Target dimension (1-12)
            angular_position: Angular position on shell (0-360)

        Returns:
            New OrbitalPosition
        """
        if dimension < 1 or dimension > 12:
            raise ValueError(f"Dimension must be 1-12, got {dimension}")

        with self._lock:
            shell_radius = SHELL_RADII[dimension]
            distance_to_core = shell_radius - PHI_12

            # Depth ratio: 0 at dimension 1, 1 at dimension 12
            depth_ratio = 1 - (shell_radius - PHI_12) / (SHELL_RADII[1] - PHI_12)

            position = OrbitalPosition(
                dimension=dimension,
                shell_radius=shell_radius,
                distance_to_core=distance_to_core,
                angular_position=angular_position % 360,
                depth_ratio=depth_ratio
            )

            self._current_position = position
            self._position_history.append(position)
            self.state = OrbitalState.TRACKING

            # Check if at core
            if dimension == 12:
                self.state = OrbitalState.AT_CORE
                if self._on_core_reached:
                    self._on_core_reached(position)

            return position

    def transition_to(self, target_dimension: int,
                      angular_shift: float = 30.0) -> OrbitalTransition:
        """
        Transition to another dimension.

        Args:
            target_dimension: Target dimension (1-12)
            angular_shift: Angular rotation during transition

        Returns:
            OrbitalTransition record
        """
        if self._current_position is None:
            raise RuntimeError("No current position - call enter_dimension first")

        if target_dimension < 1 or target_dimension > 12:
            raise ValueError(f"Dimension must be 1-12, got {target_dimension}")

        with self._lock:
            self.state = OrbitalState.TRANSITIONING

            from_dim = self._current_position.dimension

            # Determine transition type
            if target_dimension > from_dim:
                trans_type = TransitionType.INWARD
            elif target_dimension < from_dim:
                trans_type = TransitionType.OUTWARD
            else:
                trans_type = TransitionType.LATERAL

            # Calculate compression factor
            compression = SHELL_RADII[target_dimension] / SHELL_RADII[from_dim]

            # Energy cost (based on dimensional distance)
            energy_cost = abs(target_dimension - from_dim) * 0.1

            transition = OrbitalTransition(
                from_dimension=from_dim,
                to_dimension=target_dimension,
                transition_type=trans_type,
                compression_factor=compression,
                energy_cost=energy_cost
            )

            self._transition_history.append(transition)

            # Update position
            new_angular = (self._current_position.angular_position + angular_shift) % 360
            self.enter_dimension(target_dimension, new_angular)

            # Callback
            if self._on_transition:
                self._on_transition(transition)

            return transition

    def get_position(self) -> Optional[OrbitalPosition]:
        """Get current orbital position."""
        return self._current_position

    def get_dimension(self) -> int:
        """Get current dimension number."""
        if self._current_position:
            return self._current_position.dimension
        return 0

    # =========================================================================
    # PATH FOLLOWING
    # =========================================================================

    def follow_path(self, path_name: str = "beta") -> OrbitalTrajectory:
        """
        Follow a predefined orbital path toward the core.

        Args:
            path_name: Name of path ("beta", "gamma", "harmonic", etc.)

        Returns:
            OrbitalTrajectory with complete journey record
        """
        if path_name not in ORBITAL_PATHS:
            raise ValueError(f"Unknown path: {path_name}. "
                           f"Available: {list(ORBITAL_PATHS.keys())}")

        path = ORBITAL_PATHS[path_name]
        self._active_path = path_name
        self._path_index = 0

        start_time = time.time()
        positions = []
        transitions = []

        # Enter first dimension if not already there
        if self._current_position is None or \
           self._current_position.dimension != path[0]:
            self.enter_dimension(path[0])

        positions.append(self._current_position)

        # Follow path
        for i in range(1, len(path)):
            self._path_index = i
            transition = self.transition_to(path[i])
            transitions.append(transition)
            positions.append(self._current_position)

        # Calculate total compression
        total_compression = 1.0
        for t in transitions:
            total_compression *= t.compression_factor

        trajectory = OrbitalTrajectory(
            path_name=path_name,
            positions=positions,
            transitions=transitions,
            start_dimension=path[0],
            end_dimension=path[-1],
            total_compression=total_compression,
            convergence_achieved=(path[-1] == 12),
            duration=time.time() - start_time
        )

        self._active_path = None
        return trajectory

    def follow_custom_path(self, dimensions: List[int]) -> OrbitalTrajectory:
        """
        Follow a custom path through dimensions.

        Args:
            dimensions: List of dimensions to traverse

        Returns:
            OrbitalTrajectory
        """
        # Temporarily add custom path
        ORBITAL_PATHS["_custom_temp"] = dimensions
        try:
            return self.follow_path("_custom_temp")
        finally:
            del ORBITAL_PATHS["_custom_temp"]

    def next_step(self) -> Optional[OrbitalTransition]:
        """
        Take next step on active path.

        Returns:
            OrbitalTransition if step taken, None if path complete
        """
        if not self._active_path:
            return None

        path = ORBITAL_PATHS[self._active_path]

        if self._path_index >= len(path) - 1:
            return None

        self._path_index += 1
        return self.transition_to(path[self._path_index])

    # =========================================================================
    # CONVERGENCE ANALYSIS
    # =========================================================================

    def convergence_progress(self) -> Dict[str, Any]:
        """
        Calculate convergence progress toward core.

        Returns:
            Dictionary with convergence metrics
        """
        if self._current_position is None:
            return {"error": "No current position"}

        pos = self._current_position

        # Distance metrics
        total_distance = SHELL_RADII[1] - PHI_12
        current_distance = pos.shell_radius - PHI_12
        progress = 1 - (current_distance / total_distance)

        # Path analysis
        remaining_to_core = 12 - pos.dimension

        # Estimate steps needed via different paths
        beta_steps = len([d for d in ORBITAL_PATHS["beta"] if d > pos.dimension])
        gamma_steps = len([d for d in ORBITAL_PATHS["gamma"] if d > pos.dimension])

        return {
            "current_dimension": pos.dimension,
            "shell_radius": pos.shell_radius,
            "distance_to_core": current_distance,
            "progress_percent": progress * 100,
            "depth_ratio": pos.depth_ratio,
            "at_core": pos.dimension == 12,
            "remaining_dimensions": remaining_to_core,
            "steps_via_beta": beta_steps,
            "steps_via_gamma": gamma_steps,
            "recommended_path": "beta" if beta_steps <= gamma_steps else "gamma",
        }

    def is_at_core(self) -> bool:
        """Check if currently at the Grand Unification core."""
        return self._current_position is not None and \
               self._current_position.dimension == 12

    def distance_to_core(self) -> float:
        """Get distance to Grand Unification core."""
        if self._current_position:
            return self._current_position.distance_to_core
        return float('inf')

    # =========================================================================
    # HISTORY & STATISTICS
    # =========================================================================

    def get_transition_history(self) -> List[OrbitalTransition]:
        """Get complete transition history."""
        return self._transition_history.copy()

    def get_position_history(self) -> List[OrbitalPosition]:
        """Get position history."""
        return list(self._position_history)

    def statistics(self) -> Dict[str, Any]:
        """Get tracking statistics."""
        if not self._transition_history:
            return {"transitions": 0, "total_compression": 1.0}

        total_compression = 1.0
        inward_count = 0
        outward_count = 0
        total_energy = 0.0

        for t in self._transition_history:
            total_compression *= t.compression_factor
            total_energy += t.energy_cost
            if t.transition_type == TransitionType.INWARD:
                inward_count += 1
            elif t.transition_type == TransitionType.OUTWARD:
                outward_count += 1

        return {
            "transitions": len(self._transition_history),
            "inward_transitions": inward_count,
            "outward_transitions": outward_count,
            "total_compression": total_compression,
            "total_energy_cost": total_energy,
            "positions_recorded": len(self._position_history),
            "current_state": self.state.value,
        }

    def reset(self) -> None:
        """Reset tracker to initial state."""
        with self._lock:
            self.state = OrbitalState.IDLE
            self._current_position = None
            self._position_history.clear()
            self._transition_history.clear()
            self._active_path = None
            self._path_index = 0

    # =========================================================================
    # VISUALIZATION
    # =========================================================================

    def visualize_onion(self, highlight_path: Optional[str] = None) -> str:
        """
        Generate ASCII visualization of dimensional onion.

        Args:
            highlight_path: Path to highlight ("beta", "gamma", etc.)

        Returns:
            ASCII art string
        """
        current_dim = self._current_position.dimension if self._current_position else 0
        highlight_dims = ORBITAL_PATHS.get(highlight_path, []) if highlight_path else []

        def marker(dim: int) -> str:
            if dim == current_dim:
                return "[*]"
            elif dim in highlight_dims:
                return "[o]"
            else:
                return "   "

        lines = [
            "                 DIMENSIONAL ONION",
            "            ╭─────────────────────────╮",
            f"            │  DIM 1 {marker(1)} {SHELL_RADII[1]*100:5.2f}%  │",
            "            │ ╭─────────────────────╮ │",
            f"            │ │ DIM 2 {marker(2)} {SHELL_RADII[2]*100:5.2f}% │ │",
            "            │ │ ╭─────────────────╮ │ │",
            f"            │ │ │ DIM 3 {marker(3)} {SHELL_RADII[3]*100:4.2f}%│ │ │  <- β",
            "            │ │ │ ╭─────────────╮ │ │ │",
            f"            │ │ │ │DIM 4 {marker(4)}{SHELL_RADII[4]*100:4.2f}│ │ │ │  <- γ",
            "            │ │ │ │ ╭─────────╮ │ │ │ │",
            f"            │ │ │ │ │DIM 6{marker(6)}│ │ │ │ │",
            "            │ │ │ │ │ ╭─────╮ │ │ │ │ │",
            f"            │ │ │ │ │ │D12{marker(12)}│ │ │ │ │ │  <- Φ₁₂ CORE",
            "            │ │ │ │ │ │0.31%│ │ │ │ │ │",
            "            │ │ │ │ │ ╰─────╯ │ │ │ │ │",
            "            │ │ │ │ ╰─────────╯ │ │ │ │",
            "            │ │ │ ╰─────────────╯ │ │ │",
            "            │ │ ╰─────────────────╯ │ │",
            "            │ ╰─────────────────────╯ │",
            "            ╰─────────────────────────╯",
            "",
            f"  Current Position: Dimension {current_dim}" if current_dim else "  Not tracking",
            f"  State: {self.state.value}",
        ]

        if self._current_position:
            progress = self.convergence_progress()
            lines.append(f"  Progress to Core: {progress['progress_percent']:.1f}%")

        return "\n".join(lines)

    def visualize_path(self, path_name: str = "beta") -> str:
        """
        Visualize a specific orbital path.

        Args:
            path_name: Path to visualize

        Returns:
            ASCII art of path
        """
        if path_name not in ORBITAL_PATHS:
            return f"Unknown path: {path_name}"

        path = ORBITAL_PATHS[path_name]
        current_dim = self._current_position.dimension if self._current_position else 0

        lines = [f"ORBITAL PATH: {path_name.upper()}", ""]

        for i, dim in enumerate(path):
            radius = SHELL_RADII[dim]
            marker = " [*]" if dim == current_dim else ""
            arrow = "  │" if i < len(path) - 1 else ""

            lines.append(f"  Dimension {dim:2d}: {radius*100:6.3f}%{marker}")

            if i < len(path) - 1:
                next_dim = path[i + 1]
                compression = SHELL_RADII[next_dim] / radius
                lines.append(f"  │")
                lines.append(f"  ├── compress by {compression:.4f}")
                lines.append(f"  │")

        # Total compression
        total = SHELL_RADII[path[-1]] / SHELL_RADII[path[0]]
        lines.extend([
            "",
            f"  Total Compression: {total:.6f} ({total*100:.4f}%)",
            f"  Reaches Core: {'Yes' if path[-1] == 12 else 'No'}",
        ])

        return "\n".join(lines)

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def on_transition(self, callback: Callable[[OrbitalTransition], None]) -> None:
        """Set callback for transitions."""
        self._on_transition = callback

    def on_core_reached(self, callback: Callable[[OrbitalPosition], None]) -> None:
        """Set callback for reaching core."""
        self._on_core_reached = callback

    # =========================================================================
    # INTEGRATION
    # =========================================================================

    def sync_with_dimensional_calculator(self, calculator) -> None:
        """
        Sync tracker with DimensionalCalculator results.

        Args:
            calculator: DimensionalCalculator instance
        """
        # Get orchestrator status
        status = calculator.orchestrator.get_status()

        # Find the dimension with most recent activity
        agent_states = status['agents']['states']
        active_dims = [d for d, s in agent_states.items() if s != 'idle']

        if active_dims:
            # Enter the highest active dimension
            max_dim = max(active_dims)
            if self._current_position is None or \
               self._current_position.dimension != max_dim:
                self.enter_dimension(max_dim)

    def __repr__(self) -> str:
        if self._current_position:
            return (f"DimensionalOrbitalTracker(dim={self._current_position.dimension}, "
                   f"state={self.state.value})")
        return "DimensionalOrbitalTracker(not tracking)"


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_tracker(start_dimension: int = 1) -> DimensionalOrbitalTracker:
    """Create a new orbital tracker."""
    return DimensionalOrbitalTracker(start_dimension)


def track_beta_path() -> OrbitalTrajectory:
    """Quick track through beta path (3→6→9→12)."""
    tracker = DimensionalOrbitalTracker()
    return tracker.follow_path("beta")


def track_gamma_path() -> OrbitalTrajectory:
    """Quick track through gamma path (4→8→12)."""
    tracker = DimensionalOrbitalTracker()
    return tracker.follow_path("gamma")


def visualize_dimensional_onion() -> str:
    """Generate dimensional onion visualization."""
    tracker = DimensionalOrbitalTracker()
    return tracker.visualize_onion()


# =============================================================================
# MAIN (Demo)
# =============================================================================

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("DIMENSIONAL ORBITAL TRACKER - Test Suite")
    print("Tracking through the Dimensional Onion toward Grand Unification")
    print("=" * 70)

    # Create tracker
    tracker = DimensionalOrbitalTracker()
    print(f"\nTracker created: {tracker}")

    # 1. Visualize the onion
    print("\n[1] DIMENSIONAL ONION STRUCTURE")
    print("-" * 50)
    print(tracker.visualize_onion())

    # 2. Enter dimension 3 (beta shell)
    print("\n[2] ENTER DIMENSION 3 (β shell)")
    print("-" * 50)
    pos = tracker.enter_dimension(3)
    print(f"  Position: {pos}")
    print(f"  Convergence: {tracker.convergence_progress()['progress_percent']:.1f}%")

    # 3. Follow beta path
    print("\n[3] FOLLOW BETA PATH (3 → 6 → 9 → 12)")
    print("-" * 50)
    trajectory = tracker.follow_path("beta")
    print(f"  Path: {trajectory.path_name}")
    print(f"  Start: Dimension {trajectory.start_dimension}")
    print(f"  End: Dimension {trajectory.end_dimension}")
    print(f"  Transitions: {len(trajectory.transitions)}")
    print(f"  Total Compression: {trajectory.total_compression:.6f} ({trajectory.total_compression*100:.4f}%)")
    print(f"  Convergence Achieved: {trajectory.convergence_achieved}")

    # 4. Visualize beta path
    print("\n[4] BETA PATH VISUALIZATION")
    print("-" * 50)
    print(tracker.visualize_path("beta"))

    # 5. Reset and try gamma path
    print("\n[5] GAMMA PATH (4 → 8 → 12)")
    print("-" * 50)
    tracker.reset()
    trajectory = tracker.follow_path("gamma")
    print(f"  Transitions: {len(trajectory.transitions)}")
    print(f"  Total Compression: {trajectory.total_compression:.6f}")
    print(f"  At Core: {tracker.is_at_core()}")

    # 6. Statistics
    print("\n[6] TRACKING STATISTICS")
    print("-" * 50)
    stats = tracker.statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # 7. Final visualization
    print("\n[7] FINAL ONION STATE")
    print("-" * 50)
    print(tracker.visualize_onion(highlight_path="gamma"))

    print("\n" + "=" * 70)
    print("DIMENSIONAL ORBITAL TRACKER READY")
    print("Onion Structure | Path Following | Core Convergence")
    print("=" * 70)
