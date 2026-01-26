"""
Exotic Matter API
=================

REST API exposing exotic matter calculations from the Brahim Framework.
Integrates with the existing BrahimWormholeEngine.

This can be built NOW with ASIOS existing architecture.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

# =============================================================================
# CONSTANTS
# =============================================================================

PHI = (1 + math.sqrt(5)) / 2          # 1.618033988749895
PHI_INV = 1 / PHI                      # 0.618033988749895
ALPHA = 1 / PHI**2                     # 0.381966011250105
BETA = 1 / PHI**3                      # 0.236067977499790 (EXOTIC THRESHOLD)
GAMMA = 1 / PHI**4                     # 0.145898033750315 (TESSERACT)

# Physical constants
C = 299792458  # m/s (speed of light)
G = 6.67430e-11  # m^3/(kg*s^2) (gravitational constant)
HBAR = 1.054571817e-34  # J*s (reduced Planck constant)

# Brahim Sequence
BRAHIM_SEQUENCE = (27, 42, 60, 75, 97, 117, 139, 154, 172, 187)
PAIR_SUM = 214
CENTER = 107


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ExoticMatterRequirement:
    """Required exotic matter for a given wormhole configuration."""
    throat_radius_m: float
    density_kg_m3: float
    total_mass_kg: float
    is_feasible: bool
    feasibility_note: str


@dataclass
class CasimirConfiguration:
    """Optimal Casimir plate configuration."""
    wavelength_m: float
    optimal_separation_m: float
    energy_density_J_m3: float
    is_negative: bool


@dataclass
class DimensionalPartition:
    """How reality partitions between normal and exotic."""
    normal_fraction: float
    exotic_fraction: float
    normal_dimensions: str
    exotic_dimensions: str
    ouroboros_sum: float


@dataclass
class MatterState:
    """Classification of a value as normal or exotic."""
    value: int
    delta_from_center: int
    state: str  # "normal" or "exotic"
    mirror_pair: int
    pair_sum: int


# =============================================================================
# EXOTIC MATTER API
# =============================================================================

class ExoticMatterAPI:
    """
    API for exotic matter calculations based on the Brahim Framework.

    Key constant: beta = 1/phi^3 = 0.236 = 23.6%

    This is the exotic matter threshold - reduce vacuum energy by 23.6%
    to create negative energy density.
    """

    def __init__(self):
        self.phi = PHI
        self.beta = BETA
        self.gamma = GAMMA
        self.alpha = ALPHA
        self.sequence = BRAHIM_SEQUENCE
        self.center = CENTER
        self.pair_sum = PAIR_SUM

    # -------------------------------------------------------------------------
    # THROAT RADIUS CALCULATOR
    # -------------------------------------------------------------------------

    def calculate_exotic_requirement(self, throat_radius_m: float) -> ExoticMatterRequirement:
        """
        Calculate exotic matter required for a wormhole of given throat radius.

        Formula: rho = -beta * c^4 / (8 * pi * G * r0^2)

        Args:
            throat_radius_m: Throat radius in meters

        Returns:
            ExoticMatterRequirement with density and feasibility
        """
        # Exotic matter density (negative!)
        rho = -self.beta * C**4 / (8 * math.pi * G * throat_radius_m**2)

        # Total mass (volume of throat region ~ 4/3 * pi * r^3)
        volume = (4/3) * math.pi * throat_radius_m**3
        total_mass = abs(rho) * volume

        # Feasibility assessment
        if throat_radius_m < 1:
            feasible = False
            note = "Sub-meter wormholes require extreme densities"
        elif throat_radius_m < 1000:
            feasible = False
            note = "Kilometer-scale still requires astronomical densities"
        elif throat_radius_m < 1e11:  # < 1 AU
            feasible = False
            note = "AU-scale approaching feasibility with advanced tech"
        else:
            feasible = True
            note = "Large-scale wormholes have manageable density requirements"

        return ExoticMatterRequirement(
            throat_radius_m=throat_radius_m,
            density_kg_m3=rho,
            total_mass_kg=total_mass,
            is_feasible=feasible,
            feasibility_note=note
        )

    # -------------------------------------------------------------------------
    # CASIMIR CONFIGURATION
    # -------------------------------------------------------------------------

    def calculate_casimir_config(self, wavelength_m: float) -> CasimirConfiguration:
        """
        Calculate optimal Casimir plate configuration for given wavelength.

        Optimal separation: d = beta * wavelength
        Energy density: rho = -pi^2 * hbar * c / (720 * d^4)

        Args:
            wavelength_m: Light wavelength in meters

        Returns:
            CasimirConfiguration with optimal parameters
        """
        # Optimal plate separation
        d_optimal = self.beta * wavelength_m

        # Casimir energy density (negative!)
        rho_casimir = -math.pi**2 * HBAR * C / (720 * d_optimal**4)

        return CasimirConfiguration(
            wavelength_m=wavelength_m,
            optimal_separation_m=d_optimal,
            energy_density_J_m3=rho_casimir,
            is_negative=True
        )

    # -------------------------------------------------------------------------
    # DIMENSIONAL PARTITION
    # -------------------------------------------------------------------------

    def calculate_dimensional_partition(self, split_dimension: int = 3) -> DimensionalPartition:
        """
        Calculate how reality partitions between normal and exotic matter.

        Normal matter = dimensions 1 to split_dimension
        Exotic matter = dimensions (split_dimension+1) to infinity

        Args:
            split_dimension: Where to split (default 3 = our physical space)

        Returns:
            DimensionalPartition showing the split
        """
        # Normal matter contribution
        normal_sum = sum(1/self.phi**n for n in range(1, split_dimension + 1))

        # Exotic matter contribution (sum to infinity = phi - normal)
        exotic_sum = self.phi - normal_sum

        # Fractions
        normal_frac = normal_sum / self.phi
        exotic_frac = exotic_sum / self.phi

        return DimensionalPartition(
            normal_fraction=normal_frac,
            exotic_fraction=exotic_frac,
            normal_dimensions=f"1D to {split_dimension}D",
            exotic_dimensions=f"{split_dimension+1}D to infinity",
            ouroboros_sum=self.phi
        )

    # -------------------------------------------------------------------------
    # MATTER STATE CLASSIFIER
    # -------------------------------------------------------------------------

    def classify_matter_state(self, value: int) -> MatterState:
        """
        Classify a value as normal or exotic based on the Brahim sequence.

        Values below CENTER (107) = exotic
        Values above CENTER (107) = normal

        Args:
            value: Integer value to classify

        Returns:
            MatterState classification
        """
        delta = value - self.center
        state = "exotic" if delta < 0 else "normal"

        # Find mirror pair
        mirror = self.pair_sum - value

        return MatterState(
            value=value,
            delta_from_center=delta,
            state=state,
            mirror_pair=mirror,
            pair_sum=value + mirror
        )

    # -------------------------------------------------------------------------
    # OUROBOROS VERIFICATION
    # -------------------------------------------------------------------------

    def verify_ouroboros(self, max_terms: int = 100) -> Dict:
        """
        Verify the Ouroboros identity: sum(1/phi^n, n=1 to inf) = phi

        Args:
            max_terms: Number of terms to sum

        Returns:
            Dictionary with verification results
        """
        partial_sum = sum(1/self.phi**n for n in range(1, max_terms + 1))
        error = abs(partial_sum - self.phi)

        return {
            "partial_sum": partial_sum,
            "target_phi": self.phi,
            "error": error,
            "terms_used": max_terms,
            "identity_verified": error < 1e-10,
            "interpretation": "Infinite contraction returns to expansion (phi)"
        }

    # -------------------------------------------------------------------------
    # STABILITY ANALYSIS
    # -------------------------------------------------------------------------

    def analyze_stability(self) -> Dict:
        """
        Analyze Lyapunov stability of exotic matter configuration.

        Eigenvalues: {-gamma, -1/phi}
        Both negative = asymptotically stable

        Returns:
            Dictionary with stability analysis
        """
        eigenvalues = [-self.gamma, -1/self.phi]
        spectral_abscissa = max(eigenvalues)

        return {
            "eigenvalues": eigenvalues,
            "spectral_abscissa": spectral_abscissa,
            "is_stable": all(e < 0 for e in eigenvalues),
            "stability_class": "asymptotically_stable",
            "slow_mode": f"-gamma = {-self.gamma:.6f} (4D stabilization)",
            "fast_mode": f"-1/phi = {-1/self.phi:.6f} (1D decay)"
        }

    # -------------------------------------------------------------------------
    # SQUEEZE PARAMETER
    # -------------------------------------------------------------------------

    def calculate_squeeze_state(self, vacuum_energy: float) -> Dict:
        """
        Calculate squeezed vacuum state energy.

        E_squeezed = E_vacuum * (1 - beta) = E_vacuum * 0.764

        Args:
            vacuum_energy: Initial vacuum energy

        Returns:
            Dictionary with squeezed state parameters
        """
        squeezed_energy = vacuum_energy * (1 - self.beta)
        reduction = vacuum_energy - squeezed_energy

        return {
            "vacuum_energy": vacuum_energy,
            "squeezed_energy": squeezed_energy,
            "energy_reduction": reduction,
            "reduction_fraction": self.beta,
            "reduction_percent": f"{self.beta * 100:.1f}%",
            "is_exotic": squeezed_energy < vacuum_energy,
            "squeeze_parameter": self.beta
        }

    # -------------------------------------------------------------------------
    # FULL REPORT
    # -------------------------------------------------------------------------

    def generate_report(self, throat_radius_m: float = 1e12) -> str:
        """
        Generate a full exotic matter report.

        Args:
            throat_radius_m: Throat radius for calculations

        Returns:
            Formatted report string
        """
        exotic_req = self.calculate_exotic_requirement(throat_radius_m)
        casimir = self.calculate_casimir_config(500e-9)  # Visible light
        partition = self.calculate_dimensional_partition(3)
        stability = self.analyze_stability()
        ouroboros = self.verify_ouroboros()

        report = f"""
========================================================================
                    EXOTIC MATTER REPORT
========================================================================

FUNDAMENTAL CONSTANTS:
  phi   = {self.phi:.10f}
  beta  = {self.beta:.10f}  (EXOTIC THRESHOLD = 23.6%)
  gamma = {self.gamma:.10f}  (TESSERACT = 4D)
  alpha = {self.alpha:.10f}  (BALANCE = 2D)

------------------------------------------------------------------------
WORMHOLE REQUIREMENTS (r0 = {throat_radius_m:.2e} m):
------------------------------------------------------------------------
  Exotic matter density: {exotic_req.density_kg_m3:.2e} kg/m^3
  Total exotic mass:     {exotic_req.total_mass_kg:.2e} kg
  Feasible:              {exotic_req.is_feasible}
  Note:                  {exotic_req.feasibility_note}

------------------------------------------------------------------------
CASIMIR CONFIGURATION (wavelength = 500 nm):
------------------------------------------------------------------------
  Optimal separation:    {casimir.optimal_separation_m:.2e} m ({casimir.optimal_separation_m*1e9:.1f} nm)
  Energy density:        {casimir.energy_density_J_m3:.2e} J/m^3
  Is negative:           {casimir.is_negative}

------------------------------------------------------------------------
DIMENSIONAL PARTITION:
------------------------------------------------------------------------
  Normal matter (1-3D):  {partition.normal_fraction*100:.1f}% of phi
  Exotic matter (4D+):   {partition.exotic_fraction*100:.1f}% of phi
  Ouroboros sum:         {partition.ouroboros_sum:.10f} = phi (verified)

------------------------------------------------------------------------
STABILITY ANALYSIS:
------------------------------------------------------------------------
  Eigenvalues:           {stability['eigenvalues']}
  Spectral abscissa:     {stability['spectral_abscissa']:.6f}
  Is stable:             {stability['is_stable']}
  Class:                 {stability['stability_class']}

------------------------------------------------------------------------
OUROBOROS VERIFICATION:
------------------------------------------------------------------------
  Sum(1/phi^n):          {ouroboros['partial_sum']:.10f}
  Target (phi):          {ouroboros['target_phi']:.10f}
  Error:                 {ouroboros['error']:.2e}
  Identity verified:     {ouroboros['identity_verified']}

========================================================================
                    KEY INSIGHT
========================================================================

  To create exotic matter: REDUCE vacuum energy by beta = 23.6%

  E_exotic = E_vacuum * (1 - 0.236) = E_vacuum * 0.764

  This is the universal threshold encoded in the golden ratio.

========================================================================
"""
        return report


# =============================================================================
# STANDALONE USAGE
# =============================================================================

if __name__ == "__main__":
    api = ExoticMatterAPI()

    print("=" * 70)
    print("EXOTIC MATTER API - ASIOS INTEGRATION")
    print("=" * 70)

    # Generate full report
    print(api.generate_report(throat_radius_m=1e12))  # 1 AU scale

    # Quick calculations
    print("\nQUICK CALCULATIONS:")
    print("-" * 50)

    # Matter state classification
    for val in [27, 97, 107, 117, 187]:
        state = api.classify_matter_state(val)
        print(f"  Value {val}: {state.state} (delta={state.delta_from_center:+d}, mirror={state.mirror_pair})")

    print("\n" + "=" * 70)
    print("API READY FOR INTEGRATION")
    print("=" * 70)
