"""Dimension Router - Core IIAS Implementation"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any

from .constants import PHI, CENTER, BRAHIM_NUMBERS, LUCAS, B


class SiliconLayer(Enum):
    NPU = "NPU"
    CPU = "CPU"
    GPU = "GPU"


@dataclass(frozen=True)
class SiliconSpec:
    layer: SiliconLayer
    bandwidth_gbps: float
    saturation_k: float
    optimal_parallel: int

    def bandwidth(self, n: int) -> float:
        if n <= 0:
            return 0.0
        return self.bandwidth_gbps * (1 - math.exp(-n / self.saturation_k))


SILICON_SPECS = {
    SiliconLayer.NPU: SiliconSpec(SiliconLayer.NPU, 7.35, PHI, 16),
    SiliconLayer.CPU: SiliconSpec(SiliconLayer.CPU, 26.0, 0.90, 8),
    SiliconLayer.GPU: SiliconSpec(SiliconLayer.GPU, 12.0, 0.36, 3),
}


@dataclass
class Dimension:
    index: int
    name: str
    capacity: int
    silicon: SiliconLayer
    weight: float


def _weight(d: int) -> float:
    b_idx = min(d, 10)
    return LUCAS[d-1] * B[b_idx] / CENTER


DIMENSIONS = {
    1: Dimension(1, "PERCEPTION", LUCAS[0], SiliconLayer.NPU, _weight(1)),
    2: Dimension(2, "ATTENTION", LUCAS[1], SiliconLayer.NPU, _weight(2)),
    3: Dimension(3, "SECURITY", LUCAS[2], SiliconLayer.NPU, _weight(3)),
    4: Dimension(4, "STABILITY", LUCAS[3], SiliconLayer.NPU, _weight(4)),
    5: Dimension(5, "COMPRESSION", LUCAS[4], SiliconLayer.CPU, _weight(5)),
    6: Dimension(6, "HARMONY", LUCAS[5], SiliconLayer.CPU, _weight(6)),
    7: Dimension(7, "REASONING", LUCAS[6], SiliconLayer.CPU, _weight(7)),
    8: Dimension(8, "PREDICTION", LUCAS[7], SiliconLayer.CPU, _weight(8)),
    9: Dimension(9, "CREATIVITY", LUCAS[8], SiliconLayer.GPU, _weight(9)),
    10: Dimension(10, "WISDOM", LUCAS[9], SiliconLayer.GPU, _weight(10)),
    11: Dimension(11, "INTEGRATION", LUCAS[10], SiliconLayer.GPU, _weight(11)),
    12: Dimension(12, "UNIFICATION", LUCAS[11], SiliconLayer.GPU, _weight(12)),
}


class DimensionRouter:
    """Main IIAS router - maps requests to silicon via 12 dimensions."""

    def __init__(self):
        self.dimensions = DIMENSIONS
        self.specs = SILICON_SPECS
        total = sum(d.weight for d in DIMENSIONS.values())
        self._weights = {i: DIMENSIONS[i].weight / total for i in range(1, 13)}

    def initialize(self, request_data_mb: float) -> Dict[str, Any]:
        """Route a request through 12 dimensions to silicon."""
        ops = []
        for d, w in self._weights.items():
            dim = self.dimensions[d]
            ops.append({
                "dimension": d,
                "name": dim.name,
                "silicon": dim.silicon.value,
                "weight": w,
                "data_mb": request_data_mb * w,
            })

        # Group by silicon
        routing = {layer.value: {"dims": [], "data_mb": 0.0} for layer in SiliconLayer}
        for op in ops:
            routing[op["silicon"]]["dims"].append(op["dimension"])
            routing[op["silicon"]]["data_mb"] += op["data_mb"]

        # Calculate times
        times = {}
        for layer in SiliconLayer:
            spec = self.specs[layer]
            data = routing[layer.value]["data_mb"]
            bw = spec.bandwidth(spec.optimal_parallel)
            times[layer.value] = data / bw if bw > 0 else 0

        return {
            "request_mb": request_data_mb,
            "operations": ops,
            "routing": routing,
            "time_ms": times,
            "total_time_ms": max(times.values()),
            "conservation": 214,
        }
