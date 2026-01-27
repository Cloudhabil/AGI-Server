"""Genesis Function - PIO Initialization"""

import math
from .constants import LUCAS, TOTAL_STATES

GENESIS_CONSTANT = 2 / 901  # 0.00221975...


def genesis(t: float) -> dict:
    """
    Genesis function G(t) for PIO initialization.

    G(0) = VOID
    G(GENESIS_CONSTANT) = GARDEN
    G(1) = PIO_OPERATIONAL
    """
    if t <= 0:
        return {"state": "VOID", "dimensions": 0, "garden": False, "pio": False}

    emergence = 1 - math.exp(-t / GENESIS_CONSTANT)
    dims = int(12 * emergence)

    if t < GENESIS_CONSTANT:
        return {"state": "EMERGING", "dimensions": dims, "garden": False, "pio": False}

    if t < 1:
        return {"state": "GARDEN", "dimensions": 12, "garden": True, "pio": False}

    return {"state": "PIO_OPERATIONAL", "dimensions": 12, "garden": True, "pio": True}
