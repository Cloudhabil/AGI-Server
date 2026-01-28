"""
Context Manager - 840-state context window management
======================================================

Manages context windows using the IIAS 840-state architecture.
The 840 total states are distributed across 12 dimensions following
the Lucas sequence.

State Distribution:
    D1-D4 (NPU):  1+3+4+7 = 15 states
    D5-D8 (CPU):  11+18+29+47 = 105 states
    D9-D12 (GPU): 76+123+199+322 = 720 states
    Total: 840 states
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Deque
from collections import deque
from enum import Enum
import time

# Constants
PHI = 1.618033988749895
TOTAL_STATES = 840

# Lucas sequence for 12 dimensions
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]

# Dimension names
DIMENSION_NAMES = [
    "PERCEPTION", "ATTENTION", "SECURITY", "STABILITY",
    "COMPRESSION", "HARMONY", "REASONING", "PREDICTION",
    "CREATIVITY", "WISDOM", "INTEGRATION", "UNIFICATION"
]


class ContextType(Enum):
    """Types of context entries."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    MEMORY = "memory"


@dataclass
class ContextEntry:
    """A single context entry."""
    entry_id: str
    content: str
    context_type: ContextType
    dimension: int
    tokens: int
    timestamp: float = field(default_factory=time.time)
    priority: float = 1.0

    @property
    def age(self) -> float:
        """Age of entry in seconds."""
        return time.time() - self.timestamp


@dataclass
class DimensionWindow:
    """Context window for a single dimension."""
    dimension: int
    name: str
    capacity: int  # Lucas number
    entries: Deque[ContextEntry] = field(default_factory=deque)

    @property
    def used_tokens(self) -> int:
        """Total tokens used in this window."""
        return sum(e.tokens for e in self.entries)

    @property
    def available_tokens(self) -> int:
        """Available token capacity."""
        return max(0, self.capacity - self.used_tokens)

    @property
    def utilization(self) -> float:
        """Current utilization ratio."""
        if self.capacity == 0:
            return 0.0
        return self.used_tokens / self.capacity

    def can_fit(self, tokens: int) -> bool:
        """Check if tokens can fit in this window."""
        return self.available_tokens >= tokens


class ContextManager:
    """
    Manages 840-state context windows across 12 dimensions.

    Each dimension has a Lucas-number capacity, and entries
    are distributed based on their type and importance.
    """

    def __init__(self):
        self.phi = PHI
        self.total_states = TOTAL_STATES

        # Initialize dimension windows
        self.windows: Dict[int, DimensionWindow] = {}
        for i in range(12):
            dim = i + 1
            self.windows[dim] = DimensionWindow(
                dimension=dim,
                name=DIMENSION_NAMES[i],
                capacity=LUCAS[i]
            )

        # Context type to dimension mapping
        self._type_dimensions = {
            ContextType.SYSTEM: [3, 4],      # Security, Stability
            ContextType.USER: [1, 2],        # Perception, Attention
            ContextType.ASSISTANT: [7, 8],   # Reasoning, Prediction
            ContextType.TOOL: [5, 6],        # Compression, Harmony
            ContextType.MEMORY: [9, 10, 11, 12],  # High-capacity GPU dims
        }

        # Entry counter for IDs
        self._entry_counter = 0

    def add(self, content: str, context_type: ContextType,
            tokens: Optional[int] = None,
            dimension: Optional[int] = None,
            priority: float = 1.0) -> Optional[ContextEntry]:
        """
        Add content to the context window.

        Args:
            content: The content to add
            context_type: Type of context entry
            tokens: Token count (estimated if not provided)
            dimension: Specific dimension (auto-selected if not provided)
            priority: Priority for eviction (higher = keep longer)

        Returns:
            ContextEntry if successful, None if no space available
        """
        if tokens is None:
            # Rough token estimate: ~4 chars per token
            tokens = max(1, len(content) // 4)

        # Select dimension
        if dimension is None:
            dimension = self._select_dimension(context_type, tokens)

        if dimension is None:
            return None

        window = self.windows[dimension]

        # Evict if necessary
        while not window.can_fit(tokens) and len(window.entries) > 0:
            self._evict_from(dimension)

        if not window.can_fit(tokens):
            return None

        # Create entry
        self._entry_counter += 1
        entry = ContextEntry(
            entry_id=f"ctx-{self._entry_counter:06d}",
            content=content,
            context_type=context_type,
            dimension=dimension,
            tokens=tokens,
            priority=priority
        )

        window.entries.append(entry)
        return entry

    def _select_dimension(self, context_type: ContextType, tokens: int) -> Optional[int]:
        """Select the best dimension for a context type."""
        preferred_dims = self._type_dimensions.get(context_type, list(range(1, 13)))

        # Find dimension with capacity
        for dim in preferred_dims:
            if self.windows[dim].can_fit(tokens):
                return dim

        # Fall back to any dimension with capacity
        for dim in range(12, 0, -1):  # Start from highest capacity
            if self.windows[dim].can_fit(tokens):
                return dim

        return None

    def _evict_from(self, dimension: int) -> Optional[ContextEntry]:
        """Evict the lowest priority/oldest entry from a dimension."""
        window = self.windows[dimension]
        if not window.entries:
            return None

        # Find entry with lowest priority * recency score
        min_score = float('inf')
        min_idx = 0

        for i, entry in enumerate(window.entries):
            # Score based on priority and recency (older = lower)
            recency = 1.0 / (1.0 + entry.age / 60.0)  # Decay over minutes
            score = entry.priority * recency

            if score < min_score:
                min_score = score
                min_idx = i

        # Remove the entry
        evicted = window.entries[min_idx]
        del window.entries[min_idx]
        return evicted

    def get_context(self, dimensions: Optional[List[int]] = None) -> List[ContextEntry]:
        """Get all context entries, optionally filtered by dimensions."""
        if dimensions is None:
            dimensions = list(range(1, 13))

        entries = []
        for dim in dimensions:
            entries.extend(self.windows[dim].entries)

        # Sort by timestamp
        entries.sort(key=lambda e: e.timestamp)
        return entries

    def get_status(self) -> Dict[str, Any]:
        """Get current context manager status."""
        total_used = sum(w.used_tokens for w in self.windows.values())
        total_capacity = sum(w.capacity for w in self.windows.values())

        dim_status = {}
        for dim, window in self.windows.items():
            dim_status[dim] = {
                "name": window.name,
                "capacity": window.capacity,
                "used": window.used_tokens,
                "entries": len(window.entries),
                "utilization": window.utilization,
            }

        # Group by silicon
        npu_used = sum(self.windows[d].used_tokens for d in [1, 2, 3, 4])
        cpu_used = sum(self.windows[d].used_tokens for d in [5, 6, 7, 8])
        gpu_used = sum(self.windows[d].used_tokens for d in [9, 10, 11, 12])

        return {
            "total_states": self.total_states,
            "total_used": total_used,
            "total_available": total_capacity - total_used,
            "overall_utilization": total_used / total_capacity if total_capacity > 0 else 0,
            "npu_used": npu_used,
            "cpu_used": cpu_used,
            "gpu_used": gpu_used,
            "dimensions": dim_status,
        }

    def clear(self, dimension: Optional[int] = None) -> int:
        """Clear context entries. Returns number of entries cleared."""
        count = 0
        if dimension is not None:
            count = len(self.windows[dimension].entries)
            self.windows[dimension].entries.clear()
        else:
            for window in self.windows.values():
                count += len(window.entries)
                window.entries.clear()
        return count


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Context Manager Test")
    print("=" * 60)

    manager = ContextManager()

    # Display configuration
    print(f"\nPHI = {PHI}")
    print(f"TOTAL_STATES = {TOTAL_STATES}")

    print("\n--- Dimension Capacities ---")
    for dim, window in manager.windows.items():
        print(f"D{dim:2d} ({window.name:12s}): capacity = {window.capacity:3d}")

    print(f"\nTotal capacity: {sum(w.capacity for w in manager.windows.values())}")

    # Test adding context
    print("\n--- Adding Context Entries ---")

    entries = [
        ("You are a helpful AI assistant.", ContextType.SYSTEM, 8),
        ("What is the weather today?", ContextType.USER, 6),
        ("I'll check the weather for you.", ContextType.ASSISTANT, 8),
        ("Weather API response: Sunny, 22C", ContextType.TOOL, 7),
        ("User prefers metric units.", ContextType.MEMORY, 5),
    ]

    for content, ctx_type, tokens in entries:
        entry = manager.add(content, ctx_type, tokens=tokens)
        if entry:
            print(f"Added {entry.entry_id}: D{entry.dimension} ({ctx_type.value}) "
                  f"[{tokens} tokens]")
        else:
            print(f"Failed to add: {content[:30]}...")

    # Test large memory entry
    print("\n--- Testing Large Memory Entry ---")
    large_entry = manager.add(
        "This is a large memory entry with lots of historical context...",
        ContextType.MEMORY,
        tokens=100
    )
    if large_entry:
        print(f"Large entry added to D{large_entry.dimension}: "
              f"{large_entry.tokens} tokens")

    # Get status
    print("\n--- Context Status ---")
    status = manager.get_status()
    print(f"Total used: {status['total_used']}/{status['total_states']} "
          f"({status['overall_utilization']:.1%})")
    print(f"NPU: {status['npu_used']}/15")
    print(f"CPU: {status['cpu_used']}/105")
    print(f"GPU: {status['gpu_used']}/720")

    # Show dimension utilization
    print("\n--- Dimension Utilization ---")
    for dim, info in status['dimensions'].items():
        if info['used'] > 0:
            print(f"D{dim:2d}: {info['used']:3d}/{info['capacity']:3d} "
                  f"({info['utilization']:.1%}) - {info['entries']} entries")

    # Get all context
    print("\n--- Current Context ---")
    context = manager.get_context()
    for entry in context:
        print(f"  [{entry.context_type.value:9s}] D{entry.dimension}: "
              f"{entry.content[:40]}...")

    print("\n" + "=" * 60)
    print("Context Manager Test Complete")
    print("=" * 60)
