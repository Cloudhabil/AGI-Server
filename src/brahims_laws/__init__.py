"""
Brahim's Laws Calculator for Elliptic Curves

A computational framework implementing all 6 of Brahim's Laws governing
the statistical behavior of the Tate-Shafarevich group Sha(E).

Laws:
    1. Brahim Conjecture: Sha_median ~ Im(tau)^(2/3) ~ Omega^(-4/3)
    2. Arithmetic Reynolds Number: Rey = N/(Tam*Omega)
    3. Phase Transition: Rey_c in [10, 30]
    4. Dynamic Scaling: Sha_max ~ Rey^(5/12)
    5. Cascade Law: Var(log Sha | p) ~ p^(-1/4)
    6. Consistency Relation: 2/3 = 5/12 + 1/4

Includes:
    - Brahim Mechanics: Discrete framework for physics constants derivation
    - Brahim Geometry: Axiom-based framework connecting number theory and gauge theory
    - Brahim Agents SDK: OpenAI-compatible function calling for AI agents
    - Brahim Onion Agent: Multi-layer computational agent (AgentKit compatible)

Usage:
    from brahims_laws import BrahimLawsEngine, EllipticCurveData
    from brahims_laws import BrahimNumbersCalculator, BrahimGeometry
    from brahims_laws import BrahimCalculatorAgent, BRAHIM_FUNCTIONS

    # Elliptic curve analysis
    engine = BrahimLawsEngine()
    reynolds = engine.compute_reynolds(curve)
    regime = engine.classify_regime(reynolds)

    # Brahim Mechanics
    calc = BrahimNumbersCalculator()
    alpha = calc.fine_structure()  # 2 ppm accuracy

    # Brahim Geometry
    geometry = BrahimGeometry()
    axioms = geometry.verify_axioms()  # 7/7 verified

    # Brahim Agents SDK (OpenAI-compatible)
    agent = BrahimCalculatorAgent()
    result = agent.physics("fine_structure")  # 137.0357...
    cosmos = agent.cosmology()  # Dark matter 27%, Dark energy 68%
    ym = agent.yang_mills()  # Mass gap 1721 MeV

CLI:
    brahims-laws analyze 11a1
    brahims-laws batch curves.json --gpu
    brahims-laws verify-consistency
    python -m brahims_laws.agents_sdk  # Run SDK demo

Author: Elias Oulad Brahim
License: TUL (Technology Unified License)
DOI: 10.5281/zenodo.18352681
"""

__version__ = "1.4.0"
__author__ = "Elias Oulad Brahim"

from .core.brahim_laws import BrahimLawsEngine
from .core.reynolds import ReynoldsAnalyzer
from .core.constants import BrahimConstants
from .models.curve_data import EllipticCurveData, Regime
from .models.analysis_result import BrahimAnalysisResult

# Brahim Mechanics modules
from .brahim_numbers_calculator import (
    BrahimNumbersCalculator,
    BrahimState,
    MirrorOperator,
    MirrorProduct,
    PhysicsConstants,
)
from .brahim_geometry import (
    BrahimGeometry,
    BrahimManifold,
    PythagoreanStructure,
    GaugeCorrespondence,
    RegulatorTheory,
    Axiom,
)

# Brahim Agents SDK (OpenAI-compatible)
from .agents_sdk import (
    BrahimCalculatorAgent,
    BrahimNumber,
    MirrorPair,
    CalculationResult,
    CosmologyResult,
    YangMillsResult,
    BRAHIM_FUNCTIONS,
    execute_function,
    fine_structure_constant,
    weinberg_angle,
    muon_electron_ratio,
    proton_electron_ratio,
    cosmic_fractions,
    yang_mills_mass_gap,
    mirror_operator,
    get_sequence,
    verify_mirror_symmetry,
)

# Brahim Onion Agent (OpenAI Agents SDK / AgentKit compatible)
from .openai_agent import (
    BrahimOnionAgent,
    BrahimAgentBuilder,
    AgentConfig,
    AgentResponse,
    LayerPacket,
    LayerID,
    Intent,
    ModelType,
    BRAHIM_AGENT_TOOLS,
    HANDOFF_DEFINITIONS,
    BrahimGuardrails,
)

# 12-Wavelength ML Integration
from .ml.wavelength_integration import (
    WavelengthPipeline,
    SubstrateState,
    ConvergenceResult,
    get_pipeline,
    process_with_wavelengths,
    BRAHIM_SEQUENCE,
    SUM_CONSTANT,
    CENTER,
    PHI,
)

# BOA Wavelength Agent (12-Wave + 3-Layer Onion)
from .boa_wavelength_agent import (
    BOAWavelengthAgent,
    BOAResponse,
    BOA_WAVELENGTH_TOOLS,
)

__all__ = [
    # Core Brahim Laws (Elliptic Curves)
    "BrahimLawsEngine",
    "ReynoldsAnalyzer",
    "BrahimConstants",
    "EllipticCurveData",
    "BrahimAnalysisResult",
    "Regime",
    # Brahim Mechanics (Physics Constants)
    "BrahimNumbersCalculator",
    "BrahimState",
    "MirrorOperator",
    "MirrorProduct",
    "PhysicsConstants",
    # Brahim Geometry (Axiom Framework)
    "BrahimGeometry",
    "BrahimManifold",
    "PythagoreanStructure",
    "GaugeCorrespondence",
    "RegulatorTheory",
    "Axiom",
    # Brahim Agents SDK (OpenAI-compatible)
    "BrahimCalculatorAgent",
    "BrahimNumber",
    "MirrorPair",
    "CalculationResult",
    "CosmologyResult",
    "YangMillsResult",
    "BRAHIM_FUNCTIONS",
    "execute_function",
    "fine_structure_constant",
    "weinberg_angle",
    "muon_electron_ratio",
    "proton_electron_ratio",
    "cosmic_fractions",
    "yang_mills_mass_gap",
    "mirror_operator",
    "get_sequence",
    "verify_mirror_symmetry",
    # Brahim Onion Agent (OpenAI Agents SDK / AgentKit)
    "BrahimOnionAgent",
    "BrahimAgentBuilder",
    "AgentConfig",
    "AgentResponse",
    "LayerPacket",
    "LayerID",
    "Intent",
    "ModelType",
    "BRAHIM_AGENT_TOOLS",
    "HANDOFF_DEFINITIONS",
    "BrahimGuardrails",
    # 12-Wavelength ML Integration
    "WavelengthPipeline",
    "SubstrateState",
    "ConvergenceResult",
    "get_pipeline",
    "process_with_wavelengths",
    "BRAHIM_SEQUENCE",
    "SUM_CONSTANT",
    "CENTER",
    "PHI",
    # BOA Wavelength Agent (12-Wave + 3-Layer Onion)
    "BOAWavelengthAgent",
    "BOAResponse",
    "BOA_WAVELENGTH_TOOLS",
]
