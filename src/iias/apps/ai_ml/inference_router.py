"""
Inference Router - Route inference requests to optimal silicon
==============================================================

Routes AI/ML inference requests to the optimal silicon layer (NPU/CPU/GPU)
based on the dimension and Lucas capacity constraints.

Dimension to Silicon Mapping:
    D1-D4 (NPU):  capacity 1+3+4+7 = 15
    D5-D8 (CPU):  capacity 11+18+29+47 = 105
    D9-D12 (GPU): capacity 76+123+199+322 = 720
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any

# Constants
PHI = 1.618033988749895
TOTAL_STATES = 840

# Lucas sequence for 12 dimensions
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]


class SiliconType(Enum):
    """Silicon layer types."""
    NPU = "NPU"
    CPU = "CPU"
    GPU = "GPU"


@dataclass
class SiliconCapacity:
    """Capacity configuration for a silicon layer."""
    silicon: SiliconType
    dimensions: List[int]
    capacities: List[int]
    total_capacity: int = field(init=False)

    def __post_init__(self):
        self.total_capacity = sum(self.capacities)


# Silicon layer configurations
SILICON_LAYERS = {
    SiliconType.NPU: SiliconCapacity(
        silicon=SiliconType.NPU,
        dimensions=[1, 2, 3, 4],
        capacities=[LUCAS[0], LUCAS[1], LUCAS[2], LUCAS[3]]  # 1+3+4+7=15
    ),
    SiliconType.CPU: SiliconCapacity(
        silicon=SiliconType.CPU,
        dimensions=[5, 6, 7, 8],
        capacities=[LUCAS[4], LUCAS[5], LUCAS[6], LUCAS[7]]  # 11+18+29+47=105
    ),
    SiliconType.GPU: SiliconCapacity(
        silicon=SiliconType.GPU,
        dimensions=[9, 10, 11, 12],
        capacities=[LUCAS[8], LUCAS[9], LUCAS[10], LUCAS[11]]  # 76+123+199+322=720
    ),
}


@dataclass
class InferenceRequest:
    """An inference request with dimension and load."""
    request_id: str
    dimension: int
    load: float  # 0.0 to 1.0 normalized load
    priority: int = 5  # 1-10, higher is more urgent

    @property
    def silicon_type(self) -> SiliconType:
        """Determine silicon type from dimension."""
        if 1 <= self.dimension <= 4:
            return SiliconType.NPU
        elif 5 <= self.dimension <= 8:
            return SiliconType.CPU
        elif 9 <= self.dimension <= 12:
            return SiliconType.GPU
        raise ValueError(f"Invalid dimension: {self.dimension}")

    @property
    def capacity(self) -> int:
        """Get Lucas capacity for this dimension."""
        if 1 <= self.dimension <= 12:
            return LUCAS[self.dimension - 1]
        raise ValueError(f"Invalid dimension: {self.dimension}")


@dataclass
class RoutingResult:
    """Result of routing an inference request."""
    request: InferenceRequest
    silicon: SiliconType
    dimension_capacity: int
    layer_utilization: float
    estimated_latency_ms: float
    success: bool
    message: str = ""


class InferenceRouter:
    """
    Routes inference requests to optimal silicon based on dimension.

    Uses the 12-dimension IIAS architecture where:
    - D1-D4 map to NPU (low latency, small capacity)
    - D5-D8 map to CPU (balanced)
    - D9-D12 map to GPU (high throughput, large capacity)
    """

    def __init__(self):
        self.silicon_layers = SILICON_LAYERS
        self.phi = PHI
        self.total_states = TOTAL_STATES

        # Track current utilization per silicon layer
        self._utilization: Dict[SiliconType, float] = {
            SiliconType.NPU: 0.0,
            SiliconType.CPU: 0.0,
            SiliconType.GPU: 0.0,
        }

        # Pending requests queue
        self._queue: List[InferenceRequest] = []

    def route(self, request: InferenceRequest) -> RoutingResult:
        """
        Route an inference request to the appropriate silicon.

        Args:
            request: The inference request to route

        Returns:
            RoutingResult with routing decision and metrics
        """
        silicon = request.silicon_type
        layer = self.silicon_layers[silicon]

        # Calculate current utilization
        current_util = self._utilization[silicon]
        new_util = current_util + request.load

        # Check capacity
        if new_util > 1.0:
            return RoutingResult(
                request=request,
                silicon=silicon,
                dimension_capacity=request.capacity,
                layer_utilization=current_util,
                estimated_latency_ms=float('inf'),
                success=False,
                message=f"{silicon.value} at capacity ({current_util:.1%})"
            )

        # Update utilization
        self._utilization[silicon] = new_util

        # Estimate latency based on PHI scaling
        base_latency = self._calculate_latency(silicon, request.load)

        return RoutingResult(
            request=request,
            silicon=silicon,
            dimension_capacity=request.capacity,
            layer_utilization=new_util,
            estimated_latency_ms=base_latency,
            success=True,
            message=f"Routed to {silicon.value} dimension {request.dimension}"
        )

    def _calculate_latency(self, silicon: SiliconType, load: float) -> float:
        """
        Calculate estimated latency using PHI-based scaling.

        NPU: fastest (1x base)
        CPU: moderate (PHI x base)
        GPU: throughput-optimized (PHI^2 x base, but better for batches)
        """
        base_ms = 1.0  # 1ms base latency

        multipliers = {
            SiliconType.NPU: 1.0,
            SiliconType.CPU: self.phi,
            SiliconType.GPU: self.phi ** 2,
        }

        return base_ms * multipliers[silicon] * (1 + load)

    def get_optimal_silicon(self, dimension: int) -> SiliconType:
        """Get the optimal silicon for a given dimension."""
        if 1 <= dimension <= 4:
            return SiliconType.NPU
        elif 5 <= dimension <= 8:
            return SiliconType.CPU
        elif 9 <= dimension <= 12:
            return SiliconType.GPU
        raise ValueError(f"Invalid dimension: {dimension}")

    def get_layer_status(self) -> Dict[str, Any]:
        """Get current status of all silicon layers."""
        status = {}
        for silicon, layer in self.silicon_layers.items():
            status[silicon.value] = {
                "dimensions": layer.dimensions,
                "total_capacity": layer.total_capacity,
                "utilization": self._utilization[silicon],
                "available": 1.0 - self._utilization[silicon],
            }
        return status

    def release(self, request: InferenceRequest) -> None:
        """Release resources from a completed request."""
        silicon = request.silicon_type
        self._utilization[silicon] = max(0.0, self._utilization[silicon] - request.load)

    def reset(self) -> None:
        """Reset all utilization counters."""
        for silicon in self._utilization:
            self._utilization[silicon] = 0.0


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Inference Router Test")
    print("=" * 60)

    router = InferenceRouter()

    # Display configuration
    print(f"\nPHI = {PHI}")
    print(f"TOTAL_STATES = {TOTAL_STATES}")
    print(f"\nLucas Sequence: {LUCAS}")
    print(f"Sum: {sum(LUCAS)} (should be {TOTAL_STATES})")

    print("\n--- Silicon Layer Configuration ---")
    for silicon, layer in SILICON_LAYERS.items():
        print(f"{silicon.value}: D{layer.dimensions[0]}-D{layer.dimensions[-1]} "
              f"capacity={layer.total_capacity} ({layer.capacities})")

    # Test routing
    print("\n--- Routing Tests ---")
    test_requests = [
        InferenceRequest("req-1", dimension=2, load=0.3),   # NPU
        InferenceRequest("req-2", dimension=6, load=0.5),   # CPU
        InferenceRequest("req-3", dimension=10, load=0.4),  # GPU
        InferenceRequest("req-4", dimension=1, load=0.8),   # NPU (should fit)
    ]

    for req in test_requests:
        result = router.route(req)
        print(f"\nRequest {req.request_id} (D{req.dimension}, load={req.load}):")
        print(f"  Silicon: {result.silicon.value}")
        print(f"  Capacity: {result.dimension_capacity}")
        print(f"  Utilization: {result.layer_utilization:.1%}")
        print(f"  Latency: {result.estimated_latency_ms:.2f}ms")
        print(f"  Success: {result.success}")

    # Test capacity overflow
    print("\n--- Capacity Overflow Test ---")
    overflow_req = InferenceRequest("req-overflow", dimension=1, load=0.5)
    result = router.route(overflow_req)
    print(f"Overflow request: {result.success} - {result.message}")

    # Display final status
    print("\n--- Final Layer Status ---")
    status = router.get_layer_status()
    for layer, info in status.items():
        print(f"{layer}: utilization={info['utilization']:.1%}, "
              f"available={info['available']:.1%}")

    print("\n" + "=" * 60)
    print("Inference Router Test Complete")
    print("=" * 60)
