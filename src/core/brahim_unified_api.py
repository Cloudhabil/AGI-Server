"""
Brahim Unified API
==================

A unified interface that combines:
    1. BrahimWormholeEngine - Wormhole geometry and traversability
    2. BrahimNumbersCalculator - Physics constants and sequence mathematics
    3. DimensionalCalculator - 12-dimensional convergence computation

This module provides the high-level API for all Brahim Mechanics operations,
enabling seamless computation across the golden ratio hierarchy.

Architecture:
    BrahimUnifiedAPI
        |
        +-- WormholeEngine (geometry, stability, transforms)
        +-- NumbersCalculator (physics constants, sequence)
        +-- DimensionalCalculator (12D convergence)
        |
        +-- Grand Unification at Phi_12

Author: Elias Oulad Brahim
Date: 2026-01-26
"""

import math
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime

# Import component modules
from .brahim_wormhole_engine import (
    BrahimWormholeEngine,
    WormholeGeometry,
    TraversabilityResult,
    StabilityResult,
    WormholeTransformResult,
    ApplicationDomain,
    PHI, PHI_INV, ALPHA, BETA, GAMMA,
    BRAHIM_SEQUENCE, PAIR_SUM, CENTER
)

from .dimensional_convergence import (
    DimensionalCalculator,
    ConvergenceOrchestrator,
    ConvergenceReport,
    DimensionalResult,
    KelimutuRouter,
    DimensionalAgent,
    WormholeConnection,
    dimensional_constant,
    convergence_strength,
    PHI_12, PHI_24, PHI_60,
    verify_grand_unification
)

# Optional: Import numbers calculator if available
try:
    from ..brahims_laws.brahim_numbers_calculator import (
        BrahimNumbersCalculator,
        PhysicsConstants,
        BrahimState,
        MirrorOperator
    )
    HAS_NUMBERS_CALCULATOR = True
except ImportError:
    HAS_NUMBERS_CALCULATOR = False


# =============================================================================
# UNIFIED CONSTANTS
# =============================================================================

UNIFIED_CONSTANTS = {
    # Golden Ratio Hierarchy
    "phi": PHI,
    "phi_inv": PHI_INV,
    "alpha": ALPHA,  # 1/phi^2 - Wormhole attraction
    "beta": BETA,    # 1/phi^3 - Security constant
    "gamma": GAMMA,  # 1/phi^4 - Tesseract constant

    # Grand Unification
    "phi_12": PHI_12,  # 1/phi^12 - First Grand Unification
    "phi_24": PHI_24,  # 1/phi^24 - Second Grand Unification
    "phi_60": PHI_60,  # 1/phi^60 - Full Convergence

    # Brahim Sequence
    "brahim_sequence": BRAHIM_SEQUENCE,
    "pair_sum": PAIR_SUM,
    "center": CENTER,

    # Dimensional
    "dimensions": 12,
    "harmonic_dimensions": [1, 2, 3, 4, 6, 12],  # Divisors of 12
    "beta_path": [3, 6, 9, 12],
    "gamma_path": [4, 8, 12],
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class UnifiedResult:
    """Result from unified calculation."""
    value: float
    method: str
    dimensional_results: Dict[int, float] = field(default_factory=dict)
    convergence_report: Optional[ConvergenceReport] = None
    wormhole_geometry: Optional[WormholeGeometry] = None
    traversability: Optional[TraversabilityResult] = None
    stability: Optional[StabilityResult] = None
    physics_constants: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class CompressionChain:
    """Result of multi-level compression."""
    input_size: float
    output_size: float
    compression_ratio: float
    method: str
    levels: List[Dict[str, float]] = field(default_factory=list)


# =============================================================================
# BRAHIM UNIFIED API
# =============================================================================

class BrahimUnifiedAPI:
    """
    Unified API for all Brahim Mechanics computations.

    This class provides a single interface to:
    - Wormhole geometry and traversability analysis
    - Physics constants calculation
    - 12-dimensional convergence computation
    - Model compression across dimensional hierarchy
    - Grand Unification verification

    Example:
        api = BrahimUnifiedAPI()

        # Calculate with convergence
        result = api.calculate([1, 2, 3, 4, 5], method="harmonic")

        # Analyze wormhole
        geom = api.analyze_wormhole(throat_radius=1.0)

        # Compress data
        compressed = api.compress(data, target_ratio=0.0031)  # Phi_12

        # Verify Grand Unification
        gu = api.verify_grand_unification()
    """

    def __init__(self, throat_radius: float = 1.0):
        """
        Initialize the unified API.

        Args:
            throat_radius: Initial wormhole throat radius
        """
        # Initialize components
        self.wormhole_engine = BrahimWormholeEngine(throat_radius)
        self.dimensional_calc = DimensionalCalculator()

        # Optional numbers calculator
        if HAS_NUMBERS_CALCULATOR:
            self.numbers_calc = BrahimNumbersCalculator()
        else:
            self.numbers_calc = None

        # Configuration
        self._default_method = "harmonic"
        self._calculation_history: List[UnifiedResult] = []

    # =========================================================================
    # CALCULATION METHODS
    # =========================================================================

    def calculate(self, data: Union[List, np.ndarray],
                  method: str = "harmonic",
                  include_physics: bool = False) -> UnifiedResult:
        """
        Perform calculation with specified method.

        Args:
            data: Input data array
            method: Calculation method
                - "harmonic": Use harmonic dimensions (1,2,3,4,6,12)
                - "beta": Use beta path (3,6,9,12)
                - "gamma": Use gamma path (4,8,12)
                - "all": Use all 12 dimensions
                - "wormhole": Use wormhole transform
            include_physics: Include physics constants in result

        Returns:
            UnifiedResult with computation results
        """
        data = np.array(data, dtype=np.float64)
        result = UnifiedResult(value=0.0, method=method)

        if method == "harmonic":
            report = self.dimensional_calc.converge_at_grand_unification(
                data, method="harmonic"
            )
            result.value = report.final_value
            result.convergence_report = report
            result.dimensional_results = self.dimensional_calc.calculate(
                data, [1, 2, 3, 4, 6, 12]
            )

        elif method == "beta":
            result.value = self.dimensional_calc.calculate_via_beta(data)
            result.dimensional_results = self.dimensional_calc.calculate(
                data, [3, 6, 9, 12]
            )

        elif method == "gamma":
            result.value = self.dimensional_calc.calculate_via_gamma(data)
            result.dimensional_results = self.dimensional_calc.calculate(
                data, [4, 8, 12]
            )

        elif method == "all":
            report = self.dimensional_calc.converge_at_grand_unification(
                data, method="all"
            )
            result.value = report.final_value
            result.convergence_report = report
            result.dimensional_results = self.dimensional_calc.calculate(data)

        elif method == "wormhole":
            transform = self.wormhole_engine.transform(data, iterations=3)
            result.value = np.sum(transform.output_vector)
            result.wormhole_geometry = self.wormhole_engine.analyze_geometry()

        else:
            raise ValueError(f"Unknown method: {method}")

        # Add physics constants if requested
        if include_physics and self.numbers_calc:
            result.physics_constants = {
                "fine_structure": self.numbers_calc.fine_structure(),
                "weinberg_angle": self.numbers_calc.weinberg_angle(),
            }

        self._calculation_history.append(result)
        return result

    def compare_methods(self, data: Union[List, np.ndarray]) -> Dict[str, Any]:
        """
        Compare all calculation methods.

        Args:
            data: Input data array

        Returns:
            Comparison of all methods
        """
        data = np.array(data, dtype=np.float64)

        results = {}
        for method in ["harmonic", "beta", "gamma", "all", "wormhole"]:
            result = self.calculate(data, method=method)
            results[method] = {
                "value": result.value,
                "dimensional_results": result.dimensional_results,
            }

        # Find best convergence
        values = [(m, r["value"]) for m, r in results.items()]
        values.sort(key=lambda x: abs(x[1] - PHI_12))

        return {
            "methods": results,
            "closest_to_phi_12": values[0][0],
            "phi_12_target": PHI_12,
            "grand_unification_verified": self.verify_grand_unification(),
        }

    # =========================================================================
    # WORMHOLE METHODS
    # =========================================================================

    def analyze_wormhole(self, throat_radius: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyze wormhole geometry and traversability.

        Args:
            throat_radius: Optional throat radius (uses engine default)

        Returns:
            Dictionary with geometry, traversability, and stability
        """
        if throat_radius:
            self.wormhole_engine.r0 = throat_radius

        return {
            "geometry": self.wormhole_engine.analyze_geometry(),
            "traversability": self.wormhole_engine.check_traversability(),
            "stability": self.wormhole_engine.analyze_stability(),
            "constants": self.wormhole_engine.get_constants(),
        }

    def wormhole_transform(self, data: Union[List, np.ndarray],
                           iterations: int = 1) -> WormholeTransformResult:
        """
        Apply wormhole transform to data.

        Args:
            data: Input data
            iterations: Number of transform iterations

        Returns:
            WormholeTransformResult
        """
        return self.wormhole_engine.transform(np.array(data), iterations)

    def route_through_wormhole(self, source: np.ndarray,
                               max_hops: int = 10) -> List[np.ndarray]:
        """
        Route data through wormhole network.

        Args:
            source: Source position/data
            max_hops: Maximum routing hops

        Returns:
            Path of positions at each hop
        """
        return self.wormhole_engine.route(source, max_hops)

    # =========================================================================
    # COMPRESSION METHODS
    # =========================================================================

    def compress(self, data: Union[List, np.ndarray],
                 target_ratio: float = 0.236,
                 method: str = "golden") -> CompressionChain:
        """
        Compress data using golden ratio hierarchy.

        Args:
            data: Input data
            target_ratio: Target compression ratio
                - 0.618 (phi_inv): Single phi compression
                - 0.382 (alpha): Wormhole attraction
                - 0.236 (beta): Security constant
                - 0.146 (gamma): Tesseract
                - 0.0031 (phi_12): Grand Unification
            method: Compression method
                - "golden": Standard golden ratio
                - "wormhole": Via wormhole transform
                - "dimensional": Via dimensional cascade

        Returns:
            CompressionChain with levels
        """
        data = np.array(data, dtype=np.float64)
        input_size = np.sum(np.abs(data))

        if method == "golden":
            return self._compress_golden(data, target_ratio)
        elif method == "wormhole":
            return self._compress_wormhole(data, target_ratio)
        elif method == "dimensional":
            return self._compress_dimensional(data, target_ratio)
        else:
            raise ValueError(f"Unknown compression method: {method}")

    def _compress_golden(self, data: np.ndarray,
                         target_ratio: float) -> CompressionChain:
        """Compress using golden ratio hierarchy."""
        input_size = np.sum(np.abs(data))
        current = data.copy()
        levels = []
        current_ratio = 1.0

        # Determine compression steps
        while current_ratio > target_ratio:
            # Choose compression factor
            if current_ratio / BETA > target_ratio:
                factor = BETA
                factor_name = "beta"
            elif current_ratio / GAMMA > target_ratio:
                factor = GAMMA
                factor_name = "gamma"
            elif current_ratio / PHI_INV > target_ratio:
                factor = PHI_INV
                factor_name = "phi_inv"
            else:
                factor = target_ratio / current_ratio
                factor_name = "final"

            current = current * factor
            current_ratio *= factor

            levels.append({
                "factor": factor,
                "factor_name": factor_name,
                "cumulative_ratio": current_ratio,
                "size": np.sum(np.abs(current)),
            })

            if len(levels) > 20:  # Safety limit
                break

        output_size = np.sum(np.abs(current))

        return CompressionChain(
            input_size=input_size,
            output_size=output_size,
            compression_ratio=output_size / input_size,
            method="golden",
            levels=levels
        )

    def _compress_wormhole(self, data: np.ndarray,
                           target_ratio: float) -> CompressionChain:
        """Compress using wormhole transform."""
        input_size = np.sum(np.abs(data))

        # Calculate iterations needed
        iterations = max(1, int(math.log(target_ratio) / math.log(PHI_INV)))

        result = self.wormhole_engine.compress(data, levels=iterations)

        levels = [{
            "factor": PHI_INV,
            "factor_name": f"wormhole_level_{lvl['level']}",
            "cumulative_ratio": lvl["compression_ratio"],
            "size": np.sum(np.abs(lvl["data"])),
        } for lvl in result["levels"]]

        return CompressionChain(
            input_size=input_size,
            output_size=result["final_size"],
            compression_ratio=result["total_compression"],
            method="wormhole",
            levels=levels
        )

    def _compress_dimensional(self, data: np.ndarray,
                              target_ratio: float) -> CompressionChain:
        """Compress using dimensional cascade."""
        input_size = np.sum(np.abs(data))
        levels = []

        # Use dimensional path based on target
        if target_ratio <= PHI_12:
            # Use beta^4 or gamma^3 path
            path = [3, 6, 9, 12] if target_ratio > BETA**4 else [4, 8, 12]
        else:
            # Use partial path
            path = [d for d in [1, 2, 3, 4, 6, 12]
                    if dimensional_constant(d) >= target_ratio]

        results = self.dimensional_calc.calculate(data, path)

        cumulative = 1.0
        for d in path:
            if d in results:
                factor = dimensional_constant(d) / dimensional_constant(path[0])
                cumulative *= factor
                levels.append({
                    "factor": dimensional_constant(d),
                    "factor_name": f"dim_{d}",
                    "cumulative_ratio": cumulative,
                    "size": results[d],
                })

        output_size = levels[-1]["size"] if levels else input_size

        return CompressionChain(
            input_size=input_size,
            output_size=output_size,
            compression_ratio=output_size / input_size if input_size > 0 else 0,
            method="dimensional",
            levels=levels
        )

    def compress_to_phi12(self, data: Union[List, np.ndarray],
                          path: str = "auto") -> CompressionChain:
        """
        Compress data to the Grand Unification point (Phi_12 = 0.31%).

        Args:
            data: Input data
            path: Compression path
                - "auto": Choose optimal path
                - "beta": Use beta^4 path (3->6->9->12)
                - "gamma": Use gamma^3 path (4->8->12)

        Returns:
            CompressionChain achieving Phi_12 compression
        """
        data = np.array(data, dtype=np.float64)

        if path == "auto":
            # Compare paths and choose best
            beta_result = self._compress_dimensional(data, BETA**4)
            gamma_result = self._compress_dimensional(data, GAMMA**3)

            if abs(beta_result.compression_ratio - PHI_12) < \
               abs(gamma_result.compression_ratio - PHI_12):
                return beta_result
            return gamma_result

        elif path == "beta":
            return self._compress_dimensional(data, BETA**4)

        elif path == "gamma":
            return self._compress_dimensional(data, GAMMA**3)

        else:
            raise ValueError(f"Unknown path: {path}")

    # =========================================================================
    # PHYSICS CONSTANTS
    # =========================================================================

    def get_physics_constants(self) -> Dict[str, Any]:
        """Get all physics constants derived from Brahim numbers."""
        if not self.numbers_calc:
            return {"error": "BrahimNumbersCalculator not available"}

        return self.numbers_calc.all_physics_constants()

    def get_fine_structure(self) -> Dict[str, Any]:
        """Get fine structure constant."""
        if not self.numbers_calc:
            # Manual calculation
            B = {i: BRAHIM_SEQUENCE[i-1] for i in range(1, 11)}
            computed = B[7] + 1 + 1/(B[1] + 1)
            return {
                "name": "Fine Structure Constant (1/alpha)",
                "computed": computed,
                "experimental": 137.035999084,
            }
        return self.numbers_calc.fine_structure()

    # =========================================================================
    # GRAND UNIFICATION
    # =========================================================================

    def verify_grand_unification(self) -> Dict[str, Any]:
        """Verify the Grand Unification identity."""
        return verify_grand_unification()

    def get_dimensional_constants(self) -> Dict[int, Dict[str, float]]:
        """Get all 12 dimensional constants."""
        return self.dimensional_calc.get_dimensional_constants()

    # =========================================================================
    # STATUS AND UTILITIES
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """Get unified API status."""
        return {
            "wormhole_engine": str(self.wormhole_engine),
            "dimensional_calc": self.dimensional_calc.get_status(),
            "numbers_calc_available": HAS_NUMBERS_CALCULATOR,
            "calculations_performed": len(self._calculation_history),
            "grand_unification": self.verify_grand_unification()["grand_unified"],
        }

    def get_constants(self) -> Dict[str, Any]:
        """Get all unified constants."""
        return UNIFIED_CONSTANTS.copy()

    def validate(self) -> Dict[str, bool]:
        """Run full validation suite."""
        return {
            "wormhole_valid": self.wormhole_engine.validate()["all_valid"],
            "grand_unification": self.verify_grand_unification()["grand_unified"],
            "sequence_symmetric": all(
                BRAHIM_SEQUENCE[i] + BRAHIM_SEQUENCE[9-i] == PAIR_SUM
                for i in range(5)
            ),
            "alpha_plus_beta": abs(ALPHA + BETA - PHI_INV) < 1e-14,
        }

    def __repr__(self) -> str:
        status = self.get_status()
        return (f"BrahimUnifiedAPI(calculations={status['calculations_performed']}, "
                f"unified={status['grand_unification']})")


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_api(throat_radius: float = 1.0) -> BrahimUnifiedAPI:
    """Create a new unified API instance."""
    return BrahimUnifiedAPI(throat_radius)


def quick_calculate(data: Union[List, np.ndarray],
                    method: str = "harmonic") -> float:
    """Quick calculation with specified method."""
    api = BrahimUnifiedAPI()
    result = api.calculate(data, method=method)
    return result.value


def quick_compress(data: Union[List, np.ndarray],
                   target: str = "phi_12") -> CompressionChain:
    """Quick compression to specified target."""
    api = BrahimUnifiedAPI()

    targets = {
        "phi_inv": PHI_INV,
        "alpha": ALPHA,
        "beta": BETA,
        "gamma": GAMMA,
        "phi_12": PHI_12,
    }

    return api.compress(data, target_ratio=targets.get(target, PHI_12))


# =============================================================================
# MAIN (Demo)
# =============================================================================

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("BRAHIM UNIFIED API - Test Suite")
    print("Wormhole Engine + Numbers Calculator + Dimensional Convergence")
    print("=" * 70)

    # Create API
    api = BrahimUnifiedAPI()
    print(f"\nAPI created: {api}")

    # Test data
    test_data = [100, 50, 200, 75, 150, 80, 120, 90, 160, 110]
    print(f"\nTest data: {test_data}")

    # 1. Calculate with different methods
    print("\n[1] CALCULATION METHODS")
    print("-" * 50)
    for method in ["harmonic", "beta", "gamma", "wormhole"]:
        result = api.calculate(test_data, method=method)
        print(f"  {method:>10}: {result.value:.6f}")

    # 2. Method comparison
    print("\n[2] METHOD COMPARISON")
    print("-" * 50)
    comparison = api.compare_methods(test_data)
    print(f"  Closest to Phi_12: {comparison['closest_to_phi_12']}")
    print(f"  Phi_12 target: {comparison['phi_12_target']:.6f}")

    # 3. Wormhole analysis
    print("\n[3] WORMHOLE ANALYSIS")
    print("-" * 50)
    analysis = api.analyze_wormhole()
    print(f"  Geometry valid: {analysis['geometry'].is_valid}")
    print(f"  Traversable: {analysis['traversability'].is_traversable}")
    print(f"  Stable: {analysis['stability'].is_stable}")

    # 4. Compression
    print("\n[4] COMPRESSION TO PHI_12")
    print("-" * 50)
    compressed = api.compress_to_phi12(test_data)
    print(f"  Input size: {compressed.input_size:.2f}")
    print(f"  Output size: {compressed.output_size:.6f}")
    print(f"  Compression: {compressed.compression_ratio:.6f} ({compressed.compression_ratio*100:.4f}%)")
    print(f"  Levels: {len(compressed.levels)}")

    # 5. Validation
    print("\n[5] VALIDATION")
    print("-" * 50)
    validation = api.validate()
    for test, passed in validation.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {test}: {status}")

    # 6. Constants
    print("\n[6] UNIFIED CONSTANTS")
    print("-" * 50)
    constants = api.get_constants()
    for name in ["phi", "alpha", "beta", "gamma", "phi_12"]:
        print(f"  {name}: {constants[name]:.10f}")

    print("\n" + "=" * 70)
    print("BRAHIM UNIFIED API READY")
    print("=" * 70)
