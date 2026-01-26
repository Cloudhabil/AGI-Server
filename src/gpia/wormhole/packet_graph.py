"""
Packet Graph - Data Points as Routable Packets

Each node in the manifold is a DataPacket that can be:
- Addressed uniquely (Brahim Address)
- Connected via wormholes to distant nodes
- Retrieved in O(1) via wormhole routing

Architecture:
┌────────────────────────────────────────────────────────────────┐
│                    PACKET GRAPH MANIFOLD                       │
│                                                                │
│   [P₁]───────[P₂]───────[P₃]          Standard edges          │
│     │         │           │           (sequential)             │
│     │    ═════╪═══════════╪═════      Wormhole bridge          │
│     │         │           │           (instant)                │
│   [P₄]───────[P₅]───────[P₆]                                   │
│     ║                     ║                                    │
│     ╚═══════════════════════════════  Cross-region wormhole    │
│                                                                │
│   [P₇]───────[P₈]───────[P₉]                                   │
└────────────────────────────────────────────────────────────────┘

Mathematical Foundation:
- Packet address uses Brahim sequence encoding
- Wormhole distance: d_w = d_euclidean × β (compression by β = 0.236)
- Bridge threshold: τ = φ⁻³ (connect if similarity > τ)

Author: Elias Oulad Brahim
"""

from __future__ import annotations

import hashlib
import math
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from collections import defaultdict
import numpy as np

# Brahim Constants
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio
BETA = math.sqrt(5) - 2        # Security constant = 1/φ³
ALPHA = PHI - 1                # Wormhole constant = 1/φ
GENESIS = 0.0219               # Resonance target

# Brahim sequence for address encoding (Corrected 2026-01-26)
BRAHIM_SEQUENCE = [27, 42, 60, 75, 97, 117, 139, 154, 172, 187]
BRAHIM_SEQUENCE_ORIGINAL = [27, 42, 60, 75, 97, 121, 136, 154, 172, 187]
BRAHIM_SUM = 214  # Pair sum


@dataclass
class DataPacket:
    """
    A data point treated as a routable packet.

    Each packet has:
    - Unique address (Brahim-encoded)
    - Payload (the actual data)
    - Embedding (for similarity routing)
    - Metadata (timestamps, source, etc.)
    - Wormhole links (instant connections)
    """

    packet_id: str
    address: str                           # Brahim-encoded address
    payload: Any                           # Actual data content
    embedding: Optional[np.ndarray]        # Vector representation
    created_at: float = field(default_factory=time.time)
    source: str = "unknown"
    packet_type: str = "data"              # data, skill, voxel, embedding

    # Routing metadata
    hop_count: int = 0
    ttl: int = 64                          # Time-to-live in hops
    priority: float = 1.0

    # Wormhole connections (direct links to distant packets)
    wormhole_links: Set[str] = field(default_factory=set)

    # Content hash for integrity
    content_hash: str = ""

    def __post_init__(self):
        if not self.content_hash:
            self.content_hash = self._compute_hash()
        if not self.address:
            self.address = self._encode_address()

    def _compute_hash(self) -> str:
        """Compute β-weighted content hash."""
        content = str(self.payload).encode()
        base_hash = hashlib.sha256(content).hexdigest()

        # Apply Brahim weighting to first 8 chars
        weighted = ""
        for i, char in enumerate(base_hash[:8]):
            weight = BRAHIM_SEQUENCE[i % 10]
            weighted += format((int(char, 16) * weight) % 16, 'x')

        return weighted + base_hash[8:16]

    def _encode_address(self) -> str:
        """
        Generate Brahim-encoded address.

        Format: B<type>:<sequence_index>:<hash_segment>
        Example: Bdata:3:7a2f9c
        """
        type_code = self.packet_type[0].upper()
        hash_segment = self.content_hash[:6]

        # Map to Brahim sequence position
        hash_int = int(hash_segment, 16)
        seq_index = hash_int % 10

        return f"B{type_code}:{seq_index}:{hash_segment}"

    def add_wormhole(self, target_id: str) -> None:
        """Add a wormhole link to another packet."""
        self.wormhole_links.add(target_id)

    def remove_wormhole(self, target_id: str) -> None:
        """Remove a wormhole link."""
        self.wormhole_links.discard(target_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize packet to dictionary."""
        return {
            "packet_id": self.packet_id,
            "address": self.address,
            "payload": self.payload,
            "embedding": self.embedding.tolist() if self.embedding is not None else None,
            "created_at": self.created_at,
            "source": self.source,
            "packet_type": self.packet_type,
            "hop_count": self.hop_count,
            "ttl": self.ttl,
            "priority": self.priority,
            "wormhole_links": list(self.wormhole_links),
            "content_hash": self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DataPacket:
        """Deserialize packet from dictionary."""
        embedding = np.array(data["embedding"]) if data.get("embedding") else None
        wormhole_links = set(data.get("wormhole_links", []))

        return cls(
            packet_id=data["packet_id"],
            address=data.get("address", ""),
            payload=data["payload"],
            embedding=embedding,
            created_at=data.get("created_at", time.time()),
            source=data.get("source", "unknown"),
            packet_type=data.get("packet_type", "data"),
            hop_count=data.get("hop_count", 0),
            ttl=data.get("ttl", 64),
            priority=data.get("priority", 1.0),
            wormhole_links=wormhole_links,
            content_hash=data.get("content_hash", ""),
        )


class PacketGraph:
    """
    Graph structure where all data points are packets.

    Features:
    - O(1) packet lookup by ID or address
    - Wormhole connections for instant traversal
    - Similarity-based routing
    - ASIOS-compatible safety zones
    """

    def __init__(self, dimension: int = 384):
        """
        Initialize packet graph.

        Args:
            dimension: Embedding dimension (default 384-D)
        """
        self.dimension = dimension
        self._lock = threading.RLock()

        # Packet storage
        self._packets: Dict[str, DataPacket] = {}
        self._address_map: Dict[str, str] = {}  # address → packet_id

        # Graph structure
        self._edges: Dict[str, Set[str]] = defaultdict(set)  # Standard edges
        self._wormholes: Dict[str, Set[str]] = defaultdict(set)  # Wormhole edges

        # Spatial index for similarity search
        self._embeddings: List[Tuple[str, np.ndarray]] = []

        # Statistics
        self._stats = {
            "packets_added": 0,
            "wormholes_created": 0,
            "queries_processed": 0,
            "wormhole_traversals": 0,
        }

    def add_packet(
        self,
        packet_id: str,
        payload: Any,
        embedding: Optional[np.ndarray] = None,
        packet_type: str = "data",
        source: str = "unknown",
        auto_wormhole: bool = True,
    ) -> DataPacket:
        """
        Add a packet to the graph.

        Args:
            packet_id: Unique identifier
            payload: Data content
            embedding: Vector representation
            packet_type: Type of packet (data, skill, voxel, embedding)
            source: Origin of the packet
            auto_wormhole: Automatically create wormholes to similar packets

        Returns:
            Created DataPacket
        """
        with self._lock:
            # Create packet
            packet = DataPacket(
                packet_id=packet_id,
                address="",
                payload=payload,
                embedding=embedding,
                source=source,
                packet_type=packet_type,
            )

            # Store
            self._packets[packet_id] = packet
            self._address_map[packet.address] = packet_id

            # Index embedding
            if embedding is not None:
                self._embeddings.append((packet_id, embedding))

                # Auto-create wormholes to similar packets
                if auto_wormhole:
                    self._create_auto_wormholes(packet)

            self._stats["packets_added"] += 1
            return packet

    def _create_auto_wormholes(
        self,
        packet: DataPacket,
        threshold: float = ALPHA,  # φ⁻¹ ≈ 0.618
        max_wormholes: int = 5,
    ) -> None:
        """
        Automatically create wormholes to similar packets.

        Uses Brahim-weighted similarity threshold.
        """
        if packet.embedding is None:
            return

        # Find similar packets
        similarities = []
        for other_id, other_emb in self._embeddings:
            if other_id == packet.packet_id:
                continue

            # Cosine similarity
            sim = self._cosine_similarity(packet.embedding, other_emb)
            if sim > threshold:
                similarities.append((other_id, sim))

        # Sort by similarity and take top N
        similarities.sort(key=lambda x: x[1], reverse=True)

        for target_id, sim in similarities[:max_wormholes]:
            self._create_wormhole(packet.packet_id, target_id, sim)

    def _create_wormhole(
        self,
        source_id: str,
        target_id: str,
        strength: float = 1.0,
    ) -> None:
        """Create a bidirectional wormhole connection."""
        with self._lock:
            # Add to wormhole graph
            self._wormholes[source_id].add(target_id)
            self._wormholes[target_id].add(source_id)

            # Update packet wormhole links
            if source_id in self._packets:
                self._packets[source_id].add_wormhole(target_id)
            if target_id in self._packets:
                self._packets[target_id].add_wormhole(source_id)

            self._stats["wormholes_created"] += 1

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

    def get_packet(self, packet_id: str) -> Optional[DataPacket]:
        """Get packet by ID."""
        with self._lock:
            return self._packets.get(packet_id)

    def get_by_address(self, address: str) -> Optional[DataPacket]:
        """Get packet by Brahim address."""
        with self._lock:
            packet_id = self._address_map.get(address)
            if packet_id:
                return self._packets.get(packet_id)
            return None

    def query_similar(
        self,
        query_embedding: np.ndarray,
        k: int = 10,
        use_wormholes: bool = True,
    ) -> List[Tuple[DataPacket, float]]:
        """
        Find similar packets using wormhole-accelerated search.

        Args:
            query_embedding: Query vector
            k: Number of results
            use_wormholes: Use wormhole connections for acceleration

        Returns:
            List of (packet, similarity) tuples
        """
        with self._lock:
            self._stats["queries_processed"] += 1

            # Compute all similarities
            results = []
            for packet_id, embedding in self._embeddings:
                sim = self._cosine_similarity(query_embedding, embedding)
                results.append((packet_id, sim))

            # Sort by similarity
            results.sort(key=lambda x: x[1], reverse=True)

            # Expand via wormholes if enabled
            if use_wormholes:
                expanded = self._expand_via_wormholes(results[:k])
                results = expanded

            # Return top k packets
            return [
                (self._packets[pid], sim)
                for pid, sim in results[:k]
                if pid in self._packets
            ]

    def _expand_via_wormholes(
        self,
        initial_results: List[Tuple[str, float]],
    ) -> List[Tuple[str, float]]:
        """
        Expand results by traversing wormhole connections.

        Wormhole traversal applies β compression to distance.
        """
        seen = set()
        expanded = list(initial_results)

        for packet_id, base_sim in initial_results[:3]:  # Expand from top 3
            if packet_id not in self._wormholes:
                continue

            for wormhole_target in self._wormholes[packet_id]:
                if wormhole_target in seen:
                    continue
                seen.add(wormhole_target)

                # Wormhole bonus: similarity boosted by β
                wormhole_sim = base_sim * (1 + BETA)
                expanded.append((wormhole_target, min(wormhole_sim, 1.0)))

                self._stats["wormhole_traversals"] += 1

        # Re-sort and deduplicate
        expanded_dict = {}
        for pid, sim in expanded:
            if pid not in expanded_dict or sim > expanded_dict[pid]:
                expanded_dict[pid] = sim

        return sorted(expanded_dict.items(), key=lambda x: x[1], reverse=True)

    def get_wormhole_neighbors(self, packet_id: str) -> List[DataPacket]:
        """Get all packets connected via wormhole."""
        with self._lock:
            neighbor_ids = self._wormholes.get(packet_id, set())
            return [
                self._packets[nid]
                for nid in neighbor_ids
                if nid in self._packets
            ]

    def route_packet(
        self,
        source_id: str,
        target_id: str,
        use_wormholes: bool = True,
    ) -> List[str]:
        """
        Find route from source to target packet.

        With wormholes: O(1) if direct wormhole exists
        Without: BFS traversal
        """
        with self._lock:
            # Check direct wormhole
            if use_wormholes and target_id in self._wormholes.get(source_id, set()):
                return [source_id, target_id]

            # BFS with wormhole shortcuts
            visited = {source_id}
            queue = [(source_id, [source_id])]

            while queue:
                current, path = queue.pop(0)

                # Get neighbors (standard + wormhole)
                neighbors = self._edges.get(current, set())
                if use_wormholes:
                    neighbors = neighbors | self._wormholes.get(current, set())

                for neighbor in neighbors:
                    if neighbor == target_id:
                        return path + [neighbor]

                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))

            return []  # No route found

    def connect_packets(self, packet_id_1: str, packet_id_2: str) -> None:
        """Create standard edge between packets."""
        with self._lock:
            self._edges[packet_id_1].add(packet_id_2)
            self._edges[packet_id_2].add(packet_id_1)

    def stats(self) -> Dict[str, Any]:
        """Get graph statistics."""
        with self._lock:
            return {
                **self._stats,
                "total_packets": len(self._packets),
                "total_edges": sum(len(e) for e in self._edges.values()) // 2,
                "total_wormholes": sum(len(w) for w in self._wormholes.values()) // 2,
                "avg_wormholes_per_packet": (
                    sum(len(w) for w in self._wormholes.values()) / max(len(self._packets), 1)
                ),
            }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entire graph."""
        with self._lock:
            return {
                "dimension": self.dimension,
                "packets": {
                    pid: p.to_dict()
                    for pid, p in self._packets.items()
                },
                "edges": {k: list(v) for k, v in self._edges.items()},
                "wormholes": {k: list(v) for k, v in self._wormholes.items()},
                "stats": self._stats,
            }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PacketGraph:
        """Deserialize graph from dictionary."""
        graph = cls(dimension=data.get("dimension", 384))

        # Restore packets
        for pid, pdata in data.get("packets", {}).items():
            packet = DataPacket.from_dict(pdata)
            graph._packets[pid] = packet
            graph._address_map[packet.address] = pid
            if packet.embedding is not None:
                graph._embeddings.append((pid, packet.embedding))

        # Restore edges
        for k, v in data.get("edges", {}).items():
            graph._edges[k] = set(v)

        # Restore wormholes
        for k, v in data.get("wormholes", {}).items():
            graph._wormholes[k] = set(v)

        graph._stats = data.get("stats", graph._stats)

        return graph
