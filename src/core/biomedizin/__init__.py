"""
Hermes Trismegistos Biomedizin Module
=====================================

Applies Hermetic principles to biomedical optimization:
- Advanced Protein Folding: Structure prediction and hypothesis generation
- Beneficial Pharmacy: Drug discovery via protein folding
- Better Diets: Nutritional optimization using metabolic pathways

Core Principle: "As above, so below"
- Sequence patterns -> Structural features -> Biological function
- Molecular structure -> Biological effects -> Health outcomes

Author: GPIA Cognitive Ecosystem / Hermes Trismegistos Engine
Date: 2026-01-26
Version: 2.0.0

GOVERNANCE: Research use only. NOT for clinical decisions.
"""

from .folding_engine import (
    # Constants
    GENESIS_BIO as FOLDING_GENESIS,
    PHI_BIO as FOLDING_PHI,
    HYDROPHOBICITY,
    HELIX_PROPENSITY,
    SHEET_PROPENSITY,
    DISORDER_PROPENSITY,
    FUNCTIONAL_MOTIFS,

    # Enums
    FoldingState,
    SecondaryStructure,
    ProteinClass,
    DrugTargetPotential,

    # Data Classes
    AminoAcidProperties,
    SequenceRegion,
    FoldingHypothesis,
    StructurePrediction,
    DrugTargetAssessment,
    FoldingAnalysisResult,

    # Core Engine
    LiteratureCorpus,
    HermesAdvancedFoldingEngine,
)

from .hermes_pharma_diet import (
    # Constants
    GENESIS_BIO,
    PHI_BIO,
    BETA_HOMEOSTASIS,
    LAMBDA_METABOLIC,
    HYDROPHOBICITY,
    ESSENTIAL_NUTRIENTS,
    DRUG_TARGETS,

    # Enums
    FoldingState,
    TherapeuticCategory,
    DietGoal,

    # Data Classes
    AminoAcidSequence,
    FoldingHypothesis,
    Compound,
    TherapeuticProfile,
    NutrientIntake,
    DietPlan,

    # Engines
    HermesFoldingEngine,
    BeneficialPharmacyEngine,
    DietOptimizationEngine,
    HermesPharmaeDietSystem,
)

__all__ = [
    # ==================== FOLDING ENGINE ====================
    # Constants
    "FOLDING_GENESIS",
    "FOLDING_PHI",
    "HYDROPHOBICITY",
    "HELIX_PROPENSITY",
    "SHEET_PROPENSITY",
    "DISORDER_PROPENSITY",
    "FUNCTIONAL_MOTIFS",

    # Enums (Folding)
    "FoldingState",
    "SecondaryStructure",
    "ProteinClass",
    "DrugTargetPotential",

    # Data Classes (Folding)
    "AminoAcidProperties",
    "SequenceRegion",
    "FoldingHypothesis",
    "StructurePrediction",
    "DrugTargetAssessment",
    "FoldingAnalysisResult",

    # Core (Folding)
    "LiteratureCorpus",
    "HermesAdvancedFoldingEngine",

    # ==================== PHARMA-DIET ENGINE ====================
    # Constants
    "GENESIS_BIO",
    "PHI_BIO",
    "BETA_HOMEOSTASIS",
    "LAMBDA_METABOLIC",
    "ESSENTIAL_NUTRIENTS",
    "DRUG_TARGETS",

    # Enums (Pharma-Diet)
    "TherapeuticCategory",
    "DietGoal",

    # Data Classes (Pharma-Diet)
    "AminoAcidSequence",
    "Compound",
    "TherapeuticProfile",
    "NutrientIntake",
    "DietPlan",

    # Engines (Pharma-Diet)
    "HermesFoldingEngine",
    "BeneficialPharmacyEngine",
    "DietOptimizationEngine",
    "HermesPharmaeDietSystem",
]

__version__ = "2.0.0"
