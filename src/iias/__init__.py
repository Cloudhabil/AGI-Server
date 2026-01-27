"""
Brahim IIAS - Intelligent Infrastructure as a Service
======================================================

Deterministic AI infrastructure framework based on measured hardware saturation.

Usage:
    from iias import DimensionRouter, genesis

    router = DimensionRouter()
    result = router.initialize(100.0)  # 100 MB request
"""

from .router import (
    DimensionRouter,
    Dimension,
    SiliconLayer,
    DIMENSIONS,
    LUCAS,
    SILICON_SPECS,
)

from .genesis import genesis, GENESIS_CONSTANT

from .constants import (
    PHI,
    CENTER,
    SUM_CONSTANT,
    BRAHIM_NUMBERS,
)

__version__ = "1.0.0"
__author__ = "Elias Oulad Brahim"
__all__ = [
    "DimensionRouter",
    "Dimension",
    "SiliconLayer",
    "DIMENSIONS",
    "LUCAS",
    "SILICON_SPECS",
    "genesis",
    "GENESIS_CONSTANT",
    "PHI",
    "CENTER",
    "SUM_CONSTANT",
    "BRAHIM_NUMBERS",
]
