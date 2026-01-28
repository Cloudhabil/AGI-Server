"""
Message Router - Dimension-based channel selection

Routes messages across 12 channels corresponding to the 12 dimensions
of the ASIOS architecture. Each channel is mapped to a Lucas number
for capacity and priority weighting.

Dimensions (D1-D12):
- D1: Foundation (Lucas=1)
- D2: Connection (Lucas=3)
- D3: Structure (Lucas=4)
- D4: Flow (Lucas=7)
- D5: Compression (Lucas=11)
- D6: Harmony (Lucas=18)
- D7: Resonance (Lucas=29)
- D8: Transformation (Lucas=47)
- D9: Integration (Lucas=76)
- D10: Emergence (Lucas=123)
- D11: Transcendence (Lucas=199)
- D12: Unity (Lucas=322)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import IntEnum
import hashlib
import time

PHI = 1.618033988749895
SUM_CONSTANT = 214
D5_CAPACITY = 11
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]


class Dimension(IntEnum):
    """The 12 dimensions of ASIOS architecture."""
    D1_FOUNDATION = 1
    D2_CONNECTION = 2
    D3_STRUCTURE = 3
    D4_FLOW = 4
    D5_COMPRESSION = 5
    D6_HARMONY = 6
    D7_RESONANCE = 7
    D8_TRANSFORMATION = 8
    D9_INTEGRATION = 9
    D10_EMERGENCE = 10
    D11_TRANSCENDENCE = 11
    D12_UNITY = 12


@dataclass
class Message:
    """A message to be routed through dimensional channels."""
    payload: Any
    priority: int = 5
    dimension_hint: Optional[Dimension] = None
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default="")

    def __post_init__(self):
        if not self.message_id:
            content = f"{self.payload}{self.timestamp}"
            self.message_id = hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class Channel:
    """A dimensional channel for message routing."""
    dimension: Dimension
    capacity: int  # Lucas number for this dimension
    queue: List[Message] = field(default_factory=list)
    active: bool = True

    @property
    def load(self) -> float:
        """Current load as fraction of capacity."""
        if self.capacity == 0:
            return 1.0
        return len(self.queue) / self.capacity

    @property
    def phi_adjusted_capacity(self) -> float:
        """Capacity adjusted by PHI for harmonic scaling."""
        return self.capacity * PHI


class MessageRouter:
    """
    Routes messages across 12 dimensional channels.

    Channel selection is based on:
    1. Explicit dimension hint in message
    2. Priority-to-dimension mapping (higher priority -> higher dimension)
    3. Load balancing across channels using PHI-weighted distribution
    """

    def __init__(self):
        self.channels: Dict[Dimension, Channel] = {}
        self._initialize_channels()
        self.routed_count = 0
        self.total_lucas_capacity = sum(LUCAS)  # 840

    def _initialize_channels(self):
        """Initialize all 12 dimensional channels with Lucas capacities."""
        for dim in Dimension:
            lucas_idx = dim.value - 1
            capacity = LUCAS[lucas_idx]
            self.channels[dim] = Channel(dimension=dim, capacity=capacity)

    def select_channel(self, message: Message) -> Dimension:
        """
        Select optimal channel for a message.

        Selection algorithm:
        1. If dimension_hint provided and channel available, use it
        2. Map priority (1-10) to dimension range using PHI scaling
        3. Apply load balancing to find least loaded appropriate channel
        """
        # Check dimension hint
        if message.dimension_hint:
            channel = self.channels[message.dimension_hint]
            if channel.active and channel.load < 1.0:
                return message.dimension_hint

        # Map priority to base dimension using PHI
        # Priority 1-10 maps to dimensions 1-12
        base_dim_value = min(12, max(1, int(message.priority * PHI) % 12 + 1))

        # Find least loaded channel in vicinity of base dimension
        best_channel = None
        best_score = float('inf')

        for dim in Dimension:
            channel = self.channels[dim]
            if not channel.active or channel.load >= 1.0:
                continue

            # Score based on load and distance from preferred dimension
            distance = abs(dim.value - base_dim_value)
            # PHI-weighted score: load matters more than distance
            score = channel.load * PHI + distance / 12

            if score < best_score:
                best_score = score
                best_channel = dim

        return best_channel or Dimension.D1_FOUNDATION

    def route(self, message: Message) -> Dimension:
        """Route a message to its selected channel."""
        dimension = self.select_channel(message)
        channel = self.channels[dimension]

        # Add to queue if capacity allows
        if len(channel.queue) < channel.phi_adjusted_capacity:
            channel.queue.append(message)
            self.routed_count += 1

        return dimension

    def route_batch(self, messages: List[Message]) -> Dict[Dimension, List[Message]]:
        """Route multiple messages, returning dimension assignments."""
        assignments: Dict[Dimension, List[Message]] = {d: [] for d in Dimension}
        for msg in messages:
            dim = self.route(msg)
            assignments[dim].append(msg)
        return assignments

    def get_channel_status(self) -> Dict[str, Any]:
        """Get status of all channels."""
        status = {}
        for dim, channel in self.channels.items():
            status[dim.name] = {
                "capacity": channel.capacity,
                "queue_size": len(channel.queue),
                "load": round(channel.load, 3),
                "phi_capacity": round(channel.phi_adjusted_capacity, 2),
                "active": channel.active
            }
        return status

    def dequeue(self, dimension: Dimension) -> Optional[Message]:
        """Dequeue next message from a channel."""
        channel = self.channels[dimension]
        if channel.queue:
            return channel.queue.pop(0)
        return None

    def set_channel_active(self, dimension: Dimension, active: bool):
        """Enable or disable a channel."""
        self.channels[dimension].active = active


if __name__ == "__main__":
    print("=" * 60)
    print("MessageRouter - Dimension-based Channel Selection Test")
    print("=" * 60)

    router = MessageRouter()

    # Display channel configuration
    print("\n[Channel Configuration]")
    print(f"Total Lucas capacity: {router.total_lucas_capacity}")
    print(f"PHI constant: {PHI}")
    print()

    for dim in Dimension:
        channel = router.channels[dim]
        print(f"  {dim.name}: capacity={channel.capacity}, "
              f"phi_adjusted={channel.phi_adjusted_capacity:.2f}")

    # Test message routing
    print("\n[Routing Test Messages]")
    test_messages = [
        Message(payload="Low priority data", priority=2),
        Message(payload="Normal message", priority=5),
        Message(payload="High priority alert", priority=9),
        Message(payload="Compression request", dimension_hint=Dimension.D5_COMPRESSION),
        Message(payload="Unity broadcast", dimension_hint=Dimension.D12_UNITY),
    ]

    for msg in test_messages:
        dim = router.route(msg)
        print(f"  Message '{msg.payload[:30]}...' -> {dim.name}")

    # Batch routing test
    print("\n[Batch Routing Test]")
    batch = [Message(payload=f"Batch item {i}", priority=i % 10 + 1) for i in range(24)]
    assignments = router.route_batch(batch)

    for dim, msgs in assignments.items():
        if msgs:
            print(f"  {dim.name}: {len(msgs)} messages")

    # Channel status
    print("\n[Channel Status After Routing]")
    status = router.get_channel_status()
    for name, info in status.items():
        if info['queue_size'] > 0:
            print(f"  {name}: {info['queue_size']}/{info['capacity']} "
                  f"(load: {info['load']:.1%})")

    print("\n[Test Complete]")
    print(f"Total messages routed: {router.routed_count}")
