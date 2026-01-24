"""
Machine Learning Module for Brahim's Laws.

Provides ML models for predicting elliptic curve properties:

1. ShaPredictor - Regression model for Sha values
2. PhaseClassifier - Classification of Reynolds regimes
3. RankAwareEmbedder - Learn rank-dependent embeddings
4. PhysicsInformedPredictor - PINN respecting Law 6 consistency

Author: Elias Oulad Brahim
"""

from .sha_predictor import ShaPredictor, ShaDataset
from .feature_extractor import CurveFeatureExtractor, CurveFeatures
from .trainer import ShaModelTrainer
from .phase_classifier import PhaseClassifier, ClassificationMetrics
from .rank_embeddings import RankAwareEmbedder, RankAwareEncoder
from .pinn import PhysicsInformedPredictor, BrahimLawsPINN

__all__ = [
    # Core prediction
    "ShaPredictor",
    "ShaDataset",
    "ShaModelTrainer",

    # Feature extraction
    "CurveFeatureExtractor",
    "CurveFeatures",

    # Classification
    "PhaseClassifier",
    "ClassificationMetrics",

    # Embeddings
    "RankAwareEmbedder",
    "RankAwareEncoder",

    # Physics-informed
    "PhysicsInformedPredictor",
    "BrahimLawsPINN",
]
