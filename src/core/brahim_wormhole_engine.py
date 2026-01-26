"""
Brahim Wormhole Engine
======================

A comprehensive engine for wormhole-based computations using the
corrected symmetric Brahim Sequence with full algebraic closure.

Features:
- Morris-Thorne traversable wormhole geometry
- Golden ratio stability (Lyapunov analysis)
- Wormhole transform for routing and compression
- Error detection via mirror symmetry
- Multi-domain applications (crypto, routing, ML, finance)

Mathematical Foundation:
- Sequence: B = {27, 42, 60, 75, 97, 117, 139, 154, 172, 187}
- Pair sum: S = 214 (each mirror pair sums to this)
- Center: C = 107 (exact mean, critical line)
- Shape function: b(r) = r0 * (r0/r)^alpha * exp(-beta*(r-r0)/r0)
- Key identity: alpha + beta = 1/phi (EXACT)

Author: Elias Oulad Brahim
Date: 2026-01-26
"""

import math
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Union, Callable
from enum import Enum
import hashlib
import time


# =============================================================================
# FUNDAMENTAL CONSTANTS
# =============================================================================

# Golden ratio and hierarchy
PHI: float = (1 + math.sqrt(5)) / 2          # 1.618033988749895
PHI_INV: float = 1 / PHI                      # 0.618033988749895
ALPHA: float = 1 / PHI**2                     # 0.381966011250105
BETA: float = 1 / PHI**3                      # 0.236067977499790
GAMMA: float = 1 / PHI**4                     # 0.145898033750315

# Brahim Sequence (Corrected - full mirror symmetry)
BRAHIM_SEQUENCE: Tuple[int, ...] = (27, 42, 60, 75, 97, 117, 139, 154, 172, 187)
BRAHIM_SEQUENCE_ORIGINAL: Tuple[int, ...] = (27, 42, 60, 75, 97, 121, 136, 154, 172, 187)

# Sequence constants
PAIR_SUM: int = 214           # Each mirror pair sums to this
CENTER: int = 107             # C = S/2 (critical line)
DIMENSION: int = 10           # Sequence length
SEQUENCE_SUM: int = 1070      # Actual sum of sequence elements

# Derived constants
CENTROID: np.ndarray = np.array(BRAHIM_SEQUENCE, dtype=np.float64) / PAIR_SUM
EQUILIBRIUM_RADIUS: float = (CENTER / PAIR_SUM) * PHI  # ~0.809


# =============================================================================
# ENUMS
# =============================================================================

class WormholeState(Enum):
    """State of the wormhole."""
    STABLE = "stable"
    EVOLVING = "evolving"
    COLLAPSED = "collapsed"
    TRAVERSABLE = "traversable"


class ApplicationDomain(Enum):
    """Application domains for the wormhole engine."""
    ROUTING = "routing"
    COMPRESSION = "compression"
    CRYPTOGRAPHY = "cryptography"
    MACHINE_LEARNING = "machine_learning"
    SIGNAL_PROCESSING = "signal_processing"
    FINANCE = "finance"
    PHYSICS = "physics"
    ERROR_CORRECTION = "error_correction"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class WormholeGeometry:
    """Geometric properties of the wormhole."""
    throat_radius: float
    shape_at_throat: float
    flare_out: float
    asymptotic_flatness: float
    is_valid: bool

    def __str__(self) -> str:
        return (f"WormholeGeometry(r0={self.throat_radius:.4f}, "
                f"b(r0)={self.shape_at_throat:.4f}, "
                f"b'(r0)={self.flare_out:.4f}, valid={self.is_valid})")


@dataclass
class TraversabilityResult:
    """Result of traversability analysis."""
    nec_violated: bool
    nec_factor: float
    exotic_matter_required: bool
    is_traversable: bool
    stress_energy: Dict[str, float] = field(default_factory=dict)


@dataclass
class StabilityResult:
    """Result of Lyapunov stability analysis."""
    eigenvalues: np.ndarray
    lyapunov_exponents: np.ndarray
    spectral_abscissa: float
    is_stable: bool
    stability_class: str


@dataclass
class WormholeTransformResult:
    """Result of wormhole transform operation."""
    input_vector: np.ndarray
    output_vector: np.ndarray
    compression_ratio: float
    distance_to_centroid: float
    iterations: int = 1


@dataclass
class ErrorCheckResult:
    """Result of error detection via mirror symmetry."""
    is_valid: bool
    corrupted_pairs: List[Tuple[int, int, int]]  # (index, expected, actual)
    error_magnitude: int
    recoverable: bool


# =============================================================================
# BRAHIM WORMHOLE ENGINE
# =============================================================================

class BrahimWormholeEngine:
    """
    Core engine for Brahim Wormhole computations.

    The engine provides:
    1. Geometry calculations (shape function, flare-out)
    2. Traversability analysis (NEC violation)
    3. Stability analysis (Lyapunov)
    4. Transform operations (routing, compression)
    5. Error detection (mirror symmetry)
    6. Evolution simulation

    Example:
        engine = BrahimWormholeEngine()

        # Check geometry
        geom = engine.analyze_geometry(r0=1.0)

        # Check traversability
        trav = engine.check_traversability(r0=1.0)

        # Apply wormhole transform
        result = engine.transform(data_vector)

        # Detect errors
        check = engine.detect_errors(possibly_corrupted_sequence)
    """

    def __init__(self, throat_radius: float = 1.0):
        """
        Initialize the wormhole engine.

        Args:
            throat_radius: Initial throat radius r0 (default: 1.0)
        """
        self.r0 = throat_radius
        self.state = WormholeState.STABLE
        self.creation_time = time.time()
        self.evolution_history: List[Dict] = []

        # Verify constants on initialization
        self._verify_constants()

    def _verify_constants(self) -> None:
        """Verify fundamental constant relationships."""
        # Check alpha + beta = 1/phi
        identity_error = abs(ALPHA + BETA - PHI_INV)
        if identity_error > 1e-14:
            raise ValueError(f"Constant identity violated: alpha + beta != 1/phi (error: {identity_error})")

        # Check sequence closure
        for i in range(DIMENSION // 2):
            pair_sum = BRAHIM_SEQUENCE[i] + BRAHIM_SEQUENCE[DIMENSION - 1 - i]
            if pair_sum != PAIR_SUM:
                raise ValueError(f"Sequence closure violated at pair {i}: {pair_sum} != {PAIR_SUM}")

    # =========================================================================
    # GEOMETRY
    # =========================================================================

    def shape_function(self, r: float, r0: Optional[float] = None) -> float:
        """
        Compute the shape function b(r).

        b(r) = r0 * (r0/r)^alpha * exp(-beta * (r - r0) / r0)

        Args:
            r: Radial coordinate
            r0: Throat radius (default: self.r0)

        Returns:
            Shape function value b(r)
        """
        if r0 is None:
            r0 = self.r0

        if r <= 0:
            raise ValueError("Radial coordinate must be positive")

        return r0 * (r0 / r)**ALPHA * math.exp(-BETA * (r - r0) / r0)

    def shape_derivative(self, r: float, r0: Optional[float] = None, h: float = 1e-8) -> float:
        """
        Compute the derivative of the shape function b'(r).

        At the throat: b'(r0) = -(alpha + beta) = -1/phi

        Args:
            r: Radial coordinate
            r0: Throat radius (default: self.r0)
            h: Step size for numerical derivative

        Returns:
            Shape function derivative b'(r)
        """
        if r0 is None:
            r0 = self.r0

        # Central difference
        return (self.shape_function(r + h, r0) - self.shape_function(r - h, r0)) / (2 * h)

    def shape_derivative_analytical(self, r: float, r0: Optional[float] = None) -> float:
        """
        Analytical derivative of shape function.

        b'(r) = b(r) * (-alpha/r - beta/r0)
        At throat: b'(r0) = -(alpha + beta) = -1/phi
        """
        if r0 is None:
            r0 = self.r0

        b = self.shape_function(r, r0)
        return b * (-ALPHA / r - BETA / r0)

    def analyze_geometry(self, r0: Optional[float] = None) -> WormholeGeometry:
        """
        Analyze the wormhole geometry.

        Checks:
        1. Throat condition: b(r0) = r0
        2. Flare-out condition: b'(r0) < 1
        3. Asymptotic flatness: b(r)/r -> 0 as r -> infinity

        Args:
            r0: Throat radius (default: self.r0)

        Returns:
            WormholeGeometry with analysis results
        """
        if r0 is None:
            r0 = self.r0

        # Compute at throat
        b_throat = self.shape_function(r0, r0)
        b_prime = self.shape_derivative(r0, r0)

        # Asymptotic behavior
        r_far = 100 * r0
        b_far = self.shape_function(r_far, r0)
        asymptotic = b_far / r_far

        # Validity checks
        throat_ok = abs(b_throat - r0) < 1e-10
        flare_ok = b_prime < 1
        asymptotic_ok = asymptotic < 0.01

        return WormholeGeometry(
            throat_radius=r0,
            shape_at_throat=b_throat,
            flare_out=b_prime,
            asymptotic_flatness=asymptotic,
            is_valid=throat_ok and flare_ok and asymptotic_ok
        )

    # =========================================================================
    # TRAVERSABILITY
    # =========================================================================

    def nec_factor(self, r: float, r0: Optional[float] = None) -> float:
        """
        Compute the Null Energy Condition (NEC) factor.

        NEC factor = (b/r - b')
        For traversability, this must be positive (exotic matter required).
        At throat: NEC = phi (golden ratio)

        Args:
            r: Radial coordinate
            r0: Throat radius

        Returns:
            NEC factor (positive means exotic matter needed)
        """
        if r0 is None:
            r0 = self.r0

        b = self.shape_function(r, r0)
        b_prime = self.shape_derivative(r, r0)

        return b / r - b_prime

    def check_traversability(self, r0: Optional[float] = None) -> TraversabilityResult:
        """
        Check if the wormhole is traversable.

        Traversability requires:
        1. NEC violation near throat (exotic matter)
        2. Tidal forces within human tolerance
        3. Proper time for traversal is finite

        Args:
            r0: Throat radius

        Returns:
            TraversabilityResult with analysis
        """
        if r0 is None:
            r0 = self.r0

        # Check NEC at throat
        nec_throat = self.nec_factor(r0 * 1.001, r0)  # Slightly outside throat

        # NEC profile
        stress_energy = {}
        for r_mult in [1.01, 1.1, 1.5, 2.0, 3.0]:
            r = r0 * r_mult
            stress_energy[f"r={r_mult}r0"] = self.nec_factor(r, r0)

        # Traversability determination
        nec_violated = nec_throat > 0

        return TraversabilityResult(
            nec_violated=nec_violated,
            nec_factor=nec_throat,
            exotic_matter_required=nec_violated,
            is_traversable=nec_violated,
            stress_energy=stress_energy
        )

    # =========================================================================
    # STABILITY
    # =========================================================================

    def analyze_stability(self) -> StabilityResult:
        """
        Perform Lyapunov stability analysis.

        The stability matrix has golden ratio structure:
        J = [[-alpha,  beta ],
             [ beta,  -alpha]]

        Eigenvalues: lambda = -alpha +/- beta
                   = -1/phi^2 +/- 1/phi^3
                   = {-gamma, -1/phi}

        Both negative -> stable

        Returns:
            StabilityResult with eigenvalues and stability class
        """
        # Stability matrix
        J = np.array([
            [-ALPHA, BETA],
            [BETA, -ALPHA]
        ])

        # Eigenvalues
        eigenvalues = np.linalg.eigvals(J)
        real_parts = np.real(eigenvalues)

        # Lyapunov exponents (real parts of eigenvalues)
        lyapunov = np.sort(real_parts)[::-1]  # Descending order

        # Spectral abscissa (maximum real part)
        spectral_abscissa = max(real_parts)

        # Stability classification
        if spectral_abscissa < -1e-10:
            stability_class = "asymptotically_stable"
            is_stable = True
        elif abs(spectral_abscissa) < 1e-10:
            stability_class = "marginally_stable"
            is_stable = True
        else:
            stability_class = "unstable"
            is_stable = False

        return StabilityResult(
            eigenvalues=eigenvalues,
            lyapunov_exponents=lyapunov,
            spectral_abscissa=spectral_abscissa,
            is_stable=is_stable,
            stability_class=stability_class
        )

    # =========================================================================
    # WORMHOLE TRANSFORM
    # =========================================================================

    def transform(self, x: np.ndarray, iterations: int = 1) -> WormholeTransformResult:
        """
        Apply the wormhole transform.

        W(x) = x/phi + C_bar * alpha

        Properties:
        - Compression ratio: 1/phi per iteration
        - Fixed point: centroid C_bar
        - Invertible

        Args:
            x: Input vector (will be resized to 10 dimensions)
            iterations: Number of transform iterations

        Returns:
            WormholeTransformResult with transformed vector
        """
        x = np.array(x, dtype=np.float64)

        # Resize to 10 dimensions
        if len(x) < DIMENSION:
            x = np.pad(x, (0, DIMENSION - len(x)))
        elif len(x) > DIMENSION:
            x = x[:DIMENSION]

        original_x = x.copy()

        # Apply transform iteratively
        for _ in range(iterations):
            x = x / PHI + CENTROID * ALPHA

        # Compute metrics
        dist_before = np.linalg.norm(original_x - CENTROID)
        dist_after = np.linalg.norm(x - CENTROID)
        compression = dist_after / dist_before if dist_before > 0 else 0

        return WormholeTransformResult(
            input_vector=original_x,
            output_vector=x,
            compression_ratio=compression,
            distance_to_centroid=dist_after,
            iterations=iterations
        )

    def inverse_transform(self, w: np.ndarray) -> np.ndarray:
        """
        Apply the inverse wormhole transform.

        W^-1(w) = (w - C_bar * alpha) * phi

        Args:
            w: Transformed vector

        Returns:
            Original vector
        """
        w = np.array(w, dtype=np.float64)
        return (w - CENTROID * ALPHA) * PHI

    def route(self, source: np.ndarray, max_hops: int = 10,
              convergence_threshold: float = 0.01) -> List[np.ndarray]:
        """
        Route a packet using wormhole transform.

        Each hop compresses by 1/phi until convergence to centroid.

        Args:
            source: Source address/position
            max_hops: Maximum number of hops
            convergence_threshold: Stop when distance < threshold

        Returns:
            List of positions at each hop
        """
        path = [np.array(source, dtype=np.float64)]

        # Resize
        if len(path[0]) < DIMENSION:
            path[0] = np.pad(path[0], (0, DIMENSION - len(path[0])))

        for _ in range(max_hops):
            current = path[-1]
            next_pos = current / PHI + CENTROID * ALPHA
            path.append(next_pos)

            # Check convergence
            if np.linalg.norm(next_pos - CENTROID) < convergence_threshold:
                break

        return path

    # =========================================================================
    # COMPRESSION
    # =========================================================================

    def compress(self, data: np.ndarray, levels: int = 5) -> Dict[str, any]:
        """
        Hierarchical compression using golden ratio.

        Each level compresses by 1/phi (0.618).

        Args:
            data: Input data array
            levels: Number of compression levels

        Returns:
            Dictionary with compressed representations at each level
        """
        result = {
            "original_size": len(data),
            "levels": []
        }

        current = np.array(data, dtype=np.float64)

        for level in range(levels):
            # Downsample by golden ratio
            new_size = max(1, int(len(current) * PHI_INV))

            # Averaging compression
            if new_size < len(current):
                ratio = len(current) / new_size
                compressed = np.array([
                    np.mean(current[int(i*ratio):int((i+1)*ratio)])
                    for i in range(new_size)
                ])
            else:
                compressed = current

            result["levels"].append({
                "level": level,
                "size": len(compressed),
                "compression_ratio": len(compressed) / result["original_size"],
                "data": compressed
            })

            current = compressed

        result["final_size"] = len(current)
        result["total_compression"] = result["final_size"] / result["original_size"]

        return result

    def decompress(self, compressed: Dict, target_size: int) -> np.ndarray:
        """
        Decompress data using golden ratio interpolation.

        Args:
            compressed: Compression result from compress()
            target_size: Target size for decompression

        Returns:
            Decompressed data
        """
        # Start from most compressed level
        data = compressed["levels"][-1]["data"]

        # Upsample through levels
        while len(data) < target_size:
            new_size = min(target_size, int(len(data) * PHI))
            # Linear interpolation
            x_old = np.linspace(0, 1, len(data))
            x_new = np.linspace(0, 1, new_size)
            data = np.interp(x_new, x_old, data)

        return data[:target_size]

    # =========================================================================
    # ERROR DETECTION
    # =========================================================================

    def detect_errors(self, sequence: List[int]) -> ErrorCheckResult:
        """
        Detect errors using mirror symmetry.

        For a valid Brahim sequence, all mirror pairs sum to 214.
        Any deviation indicates corruption.

        Args:
            sequence: Sequence to check (should be 10 integers)

        Returns:
            ErrorCheckResult with corruption details
        """
        if len(sequence) != DIMENSION:
            return ErrorCheckResult(
                is_valid=False,
                corrupted_pairs=[(-1, DIMENSION, len(sequence))],
                error_magnitude=abs(len(sequence) - DIMENSION),
                recoverable=False
            )

        corrupted = []
        total_error = 0

        for i in range(DIMENSION // 2):
            j = DIMENSION - 1 - i
            actual_sum = sequence[i] + sequence[j]

            if actual_sum != PAIR_SUM:
                error = actual_sum - PAIR_SUM
                corrupted.append((i, PAIR_SUM, actual_sum))
                total_error += abs(error)

        return ErrorCheckResult(
            is_valid=len(corrupted) == 0,
            corrupted_pairs=corrupted,
            error_magnitude=total_error,
            recoverable=len(corrupted) == 1  # Single error can be corrected
        )

    def correct_error(self, sequence: List[int], pair_index: int,
                      correct_first: bool = True) -> List[int]:
        """
        Correct a single error using mirror symmetry.

        If one element in a pair is known correct, the other can be recovered.

        Args:
            sequence: Corrupted sequence
            pair_index: Index of corrupted pair (0-4)
            correct_first: If True, assume first element is correct

        Returns:
            Corrected sequence
        """
        corrected = list(sequence)
        i = pair_index
        j = DIMENSION - 1 - pair_index

        if correct_first:
            # First element correct, fix second
            corrected[j] = PAIR_SUM - corrected[i]
        else:
            # Second element correct, fix first
            corrected[i] = PAIR_SUM - corrected[j]

        return corrected

    # =========================================================================
    # EVOLUTION
    # =========================================================================

    def evolve(self, time_steps: int = 100, dt: float = 0.1) -> List[Dict]:
        """
        Simulate wormhole evolution over time.

        The throat radius evolves according to:
        dr/dt = -beta * (r - r_eq)

        where r_eq = (C/S) * phi is the equilibrium radius.

        Args:
            time_steps: Number of time steps
            dt: Time step size

        Returns:
            List of state dictionaries at each time step
        """
        r = self.r0
        history = []

        for t in range(time_steps):
            # Compute state
            state = {
                "time": t * dt,
                "throat_radius": r,
                "distance_to_equilibrium": abs(r - EQUILIBRIUM_RADIUS),
                "is_stable": r > 0.1,
                "nec_factor": self.nec_factor(max(r * 1.01, 0.11), r) if r > 0.1 else 0
            }
            history.append(state)

            # Evolve
            dr = -BETA * (r - EQUILIBRIUM_RADIUS) * dt
            r = max(0.1, r + dr)  # Prevent collapse

        self.evolution_history = history
        return history

    # =========================================================================
    # APPLICATION INTERFACES
    # =========================================================================

    def create_application(self, domain: ApplicationDomain) -> Dict[str, Callable]:
        """
        Create application-specific interface.

        Args:
            domain: Application domain

        Returns:
            Dictionary of domain-specific functions
        """
        if domain == ApplicationDomain.ROUTING:
            return {
                "route": self.route,
                "transform": self.transform,
                "inverse": self.inverse_transform,
                "convergence_rate": lambda: PHI_INV,
            }

        elif domain == ApplicationDomain.COMPRESSION:
            return {
                "compress": self.compress,
                "decompress": self.decompress,
                "compression_ratio": lambda levels: PHI_INV ** levels,
            }

        elif domain == ApplicationDomain.ERROR_CORRECTION:
            return {
                "detect": self.detect_errors,
                "correct": self.correct_error,
                "redundancy": lambda: DIMENSION // 2,  # 5 pairs
            }

        elif domain == ApplicationDomain.CRYPTOGRAPHY:
            return {
                "mix": lambda x: self.transform(x, iterations=3).output_vector,
                "key_constant": BETA,
                "diffusion_rate": PHI_INV,
            }

        elif domain == ApplicationDomain.MACHINE_LEARNING:
            return {
                "embed": lambda x: self.transform(x).output_vector,
                "attention_weights": lambda: CENTROID,
                "regularization": BETA,
            }

        elif domain == ApplicationDomain.FINANCE:
            return {
                "mean_revert": lambda x, target=CENTER: x - BETA * (x - target),
                "equilibrium": CENTER,
                "damping": BETA,
            }

        elif domain == ApplicationDomain.PHYSICS:
            return {
                "geometry": self.analyze_geometry,
                "traversability": self.check_traversability,
                "stability": self.analyze_stability,
                "evolve": self.evolve,
            }

        elif domain == ApplicationDomain.SIGNAL_PROCESSING:
            return {
                "filter": lambda x: self.transform(x).output_vector,
                "damping": BETA,
                "resonance": lambda: 1 / PAIR_SUM,
            }

        return {}

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def get_constants(self) -> Dict[str, float]:
        """Return all fundamental constants."""
        return {
            "phi": PHI,
            "phi_inv": PHI_INV,
            "alpha": ALPHA,
            "beta": BETA,
            "gamma": GAMMA,
            "pair_sum": PAIR_SUM,
            "center": CENTER,
            "dimension": DIMENSION,
            "equilibrium_radius": EQUILIBRIUM_RADIUS,
        }

    def get_sequence(self, original: bool = False) -> Tuple[int, ...]:
        """Return the Brahim sequence."""
        return BRAHIM_SEQUENCE_ORIGINAL if original else BRAHIM_SEQUENCE

    def validate(self) -> Dict[str, bool]:
        """Run full validation suite."""
        geom = self.analyze_geometry()
        trav = self.check_traversability()
        stab = self.analyze_stability()

        # Error detection test
        err_check = self.detect_errors(list(BRAHIM_SEQUENCE))

        return {
            "geometry_valid": geom.is_valid,
            "traversable": trav.is_traversable,
            "stable": stab.is_stable,
            "sequence_valid": err_check.is_valid,
            "identity_alpha_plus_beta": abs(ALPHA + BETA - PHI_INV) < 1e-14,
            "all_valid": (geom.is_valid and trav.is_traversable and
                         stab.is_stable and err_check.is_valid),
        }

    def __str__(self) -> str:
        validation = self.validate()
        return (f"BrahimWormholeEngine(r0={self.r0}, "
                f"state={self.state.value}, "
                f"valid={validation['all_valid']})")

    def __repr__(self) -> str:
        return self.__str__()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_engine(throat_radius: float = 1.0) -> BrahimWormholeEngine:
    """Create a new wormhole engine instance."""
    return BrahimWormholeEngine(throat_radius)


def quick_transform(x: np.ndarray, iterations: int = 1) -> np.ndarray:
    """Quick wormhole transform without creating engine."""
    x = np.array(x, dtype=np.float64)
    if len(x) < DIMENSION:
        x = np.pad(x, (0, DIMENSION - len(x)))
    elif len(x) > DIMENSION:
        x = x[:DIMENSION]

    for _ in range(iterations):
        x = x / PHI + CENTROID * ALPHA

    return x


def verify_sequence(sequence: List[int]) -> bool:
    """Quick sequence verification."""
    if len(sequence) != DIMENSION:
        return False
    return all(
        sequence[i] + sequence[DIMENSION - 1 - i] == PAIR_SUM
        for i in range(DIMENSION // 2)
    )


# =============================================================================
# MAIN (Demo)
# =============================================================================

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("BRAHIM WORMHOLE ENGINE - Test Suite")
    print("=" * 70)

    # Create engine
    engine = BrahimWormholeEngine(throat_radius=1.0)
    print(f"\nEngine created: {engine}")

    # 1. Geometry
    print("\n[1] GEOMETRY ANALYSIS")
    print("-" * 50)
    geom = engine.analyze_geometry()
    print(f"  {geom}")
    print(f"  Flare-out b'(r0) = {geom.flare_out:.6f} (expected: -{PHI_INV:.6f})")

    # 2. Traversability
    print("\n[2] TRAVERSABILITY")
    print("-" * 50)
    trav = engine.check_traversability()
    print(f"  NEC factor: {trav.nec_factor:.6f}")
    print(f"  Exotic matter required: {trav.exotic_matter_required}")
    print(f"  Traversable: {trav.is_traversable}")

    # 3. Stability
    print("\n[3] STABILITY ANALYSIS")
    print("-" * 50)
    stab = engine.analyze_stability()
    print(f"  Eigenvalues: {stab.eigenvalues}")
    print(f"  Spectral abscissa: {stab.spectral_abscissa:.6f}")
    print(f"  Stability class: {stab.stability_class}")

    # 4. Transform
    print("\n[4] WORMHOLE TRANSFORM")
    print("-" * 50)
    test_vector = np.array([100, 50, 200, 75, 150, 80, 120, 90, 160, 110])
    result = engine.transform(test_vector, iterations=5)
    print(f"  Input: {test_vector[:5]}...")
    print(f"  Output: {np.round(result.output_vector[:5], 2)}...")
    print(f"  Compression: {result.compression_ratio:.4f}")

    # 5. Error Detection
    print("\n[5] ERROR DETECTION")
    print("-" * 50)
    good_seq = list(BRAHIM_SEQUENCE)
    bad_seq = [27, 42, 60, 75, 97, 120, 139, 154, 172, 187]  # 117->120 error

    check_good = engine.detect_errors(good_seq)
    check_bad = engine.detect_errors(bad_seq)

    print(f"  Good sequence valid: {check_good.is_valid}")
    print(f"  Bad sequence valid: {check_bad.is_valid}")
    print(f"  Corrupted pairs: {check_bad.corrupted_pairs}")

    # 6. Evolution
    print("\n[6] EVOLUTION")
    print("-" * 50)
    history = engine.evolve(time_steps=50, dt=0.1)
    print(f"  Initial radius: {history[0]['throat_radius']:.4f}")
    print(f"  Final radius: {history[-1]['throat_radius']:.4f}")
    print(f"  Equilibrium: {EQUILIBRIUM_RADIUS:.4f}")
    print(f"  Converged: {abs(history[-1]['throat_radius'] - EQUILIBRIUM_RADIUS) < 0.01}")

    # 7. Full Validation
    print("\n[7] FULL VALIDATION")
    print("-" * 50)
    validation = engine.validate()
    for test, passed in validation.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test}: {status}")

    print("\n" + "=" * 70)
    print("ENGINE READY FOR USE")
    print("=" * 70)
