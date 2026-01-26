"""
Hermes Trismegistos Biomedizin Module
=====================================

Applies Hermetic principles to biomedical optimization:
- Beneficial Pharmacy: Drug discovery via protein folding
- Better Diets: Nutritional optimization using metabolic pathways

Core Principle: "As above, so below"
- Molecular structure -> Biological effects -> Health outcomes

Author: GPIA Cognitive Ecosystem / Hermes Trismegistos Engine
Date: 2026-01-26
Version: 1.0.0

GOVERNANCE: Research use only. NOT for clinical decisions.
"""

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
    # Constants
    "GENESIS_BIO",
    "PHI_BIO",
    "BETA_HOMEOSTASIS",
    "LAMBDA_METABOLIC",
    "HYDROPHOBICITY",
    "ESSENTIAL_NUTRIENTS",
    "DRUG_TARGETS",

    # Enums
    "FoldingState",
    "TherapeuticCategory",
    "DietGoal",

    # Data Classes
    "AminoAcidSequence",
    "FoldingHypothesis",
    "Compound",
    "TherapeuticProfile",
    "NutrientIntake",
    "DietPlan",

    # Engines
    "HermesFoldingEngine",
    "BeneficialPharmacyEngine",
    "DietOptimizationEngine",
    "HermesPharmaeDietSystem",
]

__version__ = "1.0.0"
