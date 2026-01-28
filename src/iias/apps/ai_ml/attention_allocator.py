"""
Attention Allocator - D2 (Attention) dimension with capacity 3
==============================================================

Manages attention allocation for token budgets using the IIAS D2
(Attention) dimension which has Lucas capacity of 3.

D2 Attention Characteristics:
    - Capacity: 3 (Lucas[1])
    - Silicon: NPU (fast, low latency)
    - Role: Focus allocation for token processing

The attention allocator distributes focus across competing requests
while respecting the capacity-3 constraint.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import heapq

# Constants
PHI = 1.618033988749895
TOTAL_STATES = 840
D2_CAPACITY = 3  # Lucas[1] = 3


class AttentionPriority(Enum):
    """Priority levels for attention allocation."""
    CRITICAL = 1    # Must process immediately
    HIGH = 2        # Process soon
    NORMAL = 3      # Standard processing
    LOW = 4         # Can wait
    BACKGROUND = 5  # Process when idle


@dataclass
class AttentionSlot:
    """A single attention slot (one of 3 available)."""
    slot_id: int
    is_occupied: bool = False
    request_id: Optional[str] = None
    token_budget: int = 0
    priority: AttentionPriority = AttentionPriority.NORMAL
    allocated_at: float = 0.0
    expires_at: float = 0.0

    @property
    def is_expired(self) -> bool:
        """Check if slot allocation has expired."""
        if not self.is_occupied:
            return False
        return time.time() > self.expires_at

    @property
    def remaining_time(self) -> float:
        """Remaining time before expiration in seconds."""
        if not self.is_occupied:
            return 0.0
        return max(0.0, self.expires_at - time.time())


@dataclass
class AttentionRequest:
    """A request for attention allocation."""
    request_id: str
    token_budget: int
    priority: AttentionPriority = AttentionPriority.NORMAL
    duration_ms: float = 100.0  # How long attention is needed
    created_at: float = field(default_factory=time.time)

    def __lt__(self, other: 'AttentionRequest') -> bool:
        """Compare for priority queue (lower priority value = higher priority)."""
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        return self.created_at < other.created_at


@dataclass
class AllocationResult:
    """Result of an attention allocation request."""
    request: AttentionRequest
    success: bool
    slot_id: Optional[int]
    wait_time_ms: float
    message: str


class AttentionAllocator:
    """
    Manages attention allocation across 3 slots (D2 capacity).

    The allocator ensures that at most 3 concurrent attention
    requests are being processed, matching the Lucas capacity
    of dimension 2 (Attention).
    """

    def __init__(self):
        self.phi = PHI
        self.total_states = TOTAL_STATES
        self.capacity = D2_CAPACITY

        # Initialize 3 attention slots
        self.slots: List[AttentionSlot] = [
            AttentionSlot(slot_id=i) for i in range(self.capacity)
        ]

        # Waiting queue (priority queue)
        self._queue: List[AttentionRequest] = []

        # Statistics
        self._stats = {
            "total_requests": 0,
            "immediate_allocations": 0,
            "queued_allocations": 0,
            "expired_evictions": 0,
            "priority_evictions": 0,
        }

    def allocate(self, request: AttentionRequest) -> AllocationResult:
        """
        Request attention allocation.

        Args:
            request: The attention request

        Returns:
            AllocationResult with allocation details
        """
        self._stats["total_requests"] += 1

        # First, clear any expired slots
        self._clear_expired()

        # Try to find a free slot
        free_slot = self._find_free_slot()
        if free_slot is not None:
            self._occupy_slot(free_slot, request)
            self._stats["immediate_allocations"] += 1
            return AllocationResult(
                request=request,
                success=True,
                slot_id=free_slot,
                wait_time_ms=0.0,
                message=f"Allocated to slot {free_slot}"
            )

        # Try priority eviction for critical requests
        if request.priority == AttentionPriority.CRITICAL:
            evicted_slot = self._try_priority_eviction(request)
            if evicted_slot is not None:
                self._stats["priority_evictions"] += 1
                return AllocationResult(
                    request=request,
                    success=True,
                    slot_id=evicted_slot,
                    wait_time_ms=0.0,
                    message=f"Critical request evicted slot {evicted_slot}"
                )

        # Queue the request
        heapq.heappush(self._queue, request)
        self._stats["queued_allocations"] += 1

        # Estimate wait time
        avg_remaining = sum(s.remaining_time for s in self.slots) / self.capacity
        wait_ms = avg_remaining * 1000

        return AllocationResult(
            request=request,
            success=False,
            slot_id=None,
            wait_time_ms=wait_ms,
            message=f"Queued (position {len(self._queue)})"
        )

    def _find_free_slot(self) -> Optional[int]:
        """Find an unoccupied slot."""
        for slot in self.slots:
            if not slot.is_occupied:
                return slot.slot_id
        return None

    def _occupy_slot(self, slot_id: int, request: AttentionRequest) -> None:
        """Occupy a slot with a request."""
        slot = self.slots[slot_id]
        slot.is_occupied = True
        slot.request_id = request.request_id
        slot.token_budget = request.token_budget
        slot.priority = request.priority
        slot.allocated_at = time.time()
        slot.expires_at = time.time() + (request.duration_ms / 1000.0)

    def _clear_expired(self) -> int:
        """Clear expired slots and process queue. Returns count cleared."""
        cleared = 0
        for slot in self.slots:
            if slot.is_expired:
                self._release_slot(slot.slot_id)
                cleared += 1
                self._stats["expired_evictions"] += 1

        return cleared

    def _try_priority_eviction(self, request: AttentionRequest) -> Optional[int]:
        """Try to evict a lower priority request."""
        # Find lowest priority slot
        min_priority = request.priority.value
        evict_slot = None

        for slot in self.slots:
            if slot.is_occupied and slot.priority.value > min_priority:
                if evict_slot is None or slot.priority.value > self.slots[evict_slot].priority.value:
                    evict_slot = slot.slot_id

        if evict_slot is not None:
            # Re-queue the evicted request
            evicted = self.slots[evict_slot]
            requeue_req = AttentionRequest(
                request_id=evicted.request_id,
                token_budget=evicted.token_budget,
                priority=evicted.priority,
                duration_ms=(evicted.remaining_time * 1000)
            )
            heapq.heappush(self._queue, requeue_req)

            # Allocate to new request
            self._occupy_slot(evict_slot, request)

        return evict_slot

    def release(self, slot_id: int) -> bool:
        """
        Release attention from a slot.

        Args:
            slot_id: The slot to release

        Returns:
            True if released, False if slot was not occupied
        """
        if slot_id < 0 or slot_id >= self.capacity:
            return False

        slot = self.slots[slot_id]
        if not slot.is_occupied:
            return False

        self._release_slot(slot_id)
        return True

    def _release_slot(self, slot_id: int) -> None:
        """Internal: release a slot and process queue."""
        slot = self.slots[slot_id]
        slot.is_occupied = False
        slot.request_id = None
        slot.token_budget = 0
        slot.priority = AttentionPriority.NORMAL
        slot.allocated_at = 0.0
        slot.expires_at = 0.0

        # Process waiting queue
        if self._queue:
            next_request = heapq.heappop(self._queue)
            self._occupy_slot(slot_id, next_request)

    def get_status(self) -> Dict[str, Any]:
        """Get current allocator status."""
        occupied = sum(1 for s in self.slots if s.is_occupied)

        slot_info = []
        for slot in self.slots:
            info = {
                "slot_id": slot.slot_id,
                "occupied": slot.is_occupied,
                "request_id": slot.request_id,
                "token_budget": slot.token_budget,
                "priority": slot.priority.name if slot.is_occupied else None,
                "remaining_ms": slot.remaining_time * 1000,
            }
            slot_info.append(info)

        return {
            "dimension": 2,
            "name": "ATTENTION",
            "capacity": self.capacity,
            "occupied": occupied,
            "available": self.capacity - occupied,
            "utilization": occupied / self.capacity,
            "queue_length": len(self._queue),
            "slots": slot_info,
            "stats": self._stats.copy(),
        }

    def get_token_budget(self) -> int:
        """Get total token budget across all active slots."""
        return sum(s.token_budget for s in self.slots if s.is_occupied)


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Attention Allocator Test (D2 Capacity=3)")
    print("=" * 60)

    allocator = AttentionAllocator()

    # Display configuration
    print(f"\nPHI = {PHI}")
    print(f"D2 Capacity = {D2_CAPACITY} (Lucas[1])")
    print(f"TOTAL_STATES = {TOTAL_STATES}")

    # Test allocations
    print("\n--- Allocation Tests ---")

    requests = [
        AttentionRequest("attn-1", token_budget=100, priority=AttentionPriority.NORMAL, duration_ms=500),
        AttentionRequest("attn-2", token_budget=150, priority=AttentionPriority.HIGH, duration_ms=300),
        AttentionRequest("attn-3", token_budget=80, priority=AttentionPriority.LOW, duration_ms=1000),
        AttentionRequest("attn-4", token_budget=200, priority=AttentionPriority.NORMAL, duration_ms=200),  # Should queue
        AttentionRequest("attn-5", token_budget=50, priority=AttentionPriority.CRITICAL, duration_ms=100),  # Should evict
    ]

    for req in requests:
        result = allocator.allocate(req)
        status = "OK" if result.success else "QUEUED"
        print(f"\n{req.request_id} ({req.priority.name}, {req.token_budget} tokens):")
        print(f"  Status: {status}")
        print(f"  Slot: {result.slot_id}")
        print(f"  Wait: {result.wait_time_ms:.1f}ms")
        print(f"  Message: {result.message}")

    # Show current status
    print("\n--- Current Status ---")
    status = allocator.get_status()
    print(f"Capacity: {status['occupied']}/{status['capacity']} "
          f"({status['utilization']:.0%})")
    print(f"Queue length: {status['queue_length']}")
    print(f"Total token budget: {allocator.get_token_budget()}")

    print("\n--- Slot Details ---")
    for slot in status['slots']:
        if slot['occupied']:
            print(f"  Slot {slot['slot_id']}: {slot['request_id']} "
                  f"({slot['priority']}, {slot['token_budget']} tokens, "
                  f"{slot['remaining_ms']:.0f}ms remaining)")
        else:
            print(f"  Slot {slot['slot_id']}: FREE")

    # Test release
    print("\n--- Release Test ---")
    released = allocator.release(0)
    print(f"Released slot 0: {released}")

    status = allocator.get_status()
    print(f"After release: {status['occupied']}/{status['capacity']}, "
          f"queue={status['queue_length']}")

    # Show statistics
    print("\n--- Statistics ---")
    for stat, value in status['stats'].items():
        print(f"  {stat}: {value}")

    print("\n" + "=" * 60)
    print("Attention Allocator Test Complete")
    print("=" * 60)
