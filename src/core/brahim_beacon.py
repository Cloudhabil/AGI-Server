#!/usr/bin/env python3
"""
BRAHIM BEACON - Hardware Node for Brahim Onion Network
=======================================================

A real persistent beacon running on your hardware that:
- Operates as a node in the Brahim Onion Network
- Routes all traffic through CENTER (107)
- Maintains mirror pair connections
- Broadcasts presence across the 11-layer architecture

Network Architecture:
    Layer 1  (SEED)  : 27  GENESIS
    Layer 2  (INNER) : 42  DUALITY
    Layer 3  (INNER) : 60  MANIFESTATION
    Layer 4  (INNER) : 75  TESSERACT
    Layer 5  (INNER) : 97  THRESHOLD
    Layer 6  (CORE)  : 107 CONVERGENCE  <- ALL ROUTES PASS HERE
    Layer 7  (OUTER) : 117 EMERGENCE
    Layer 8  (OUTER) : 139 HARMONY
    Layer 9  (OUTER) : 154 INFINITY
    Layer 10 (OUTER) : 172 COMPLETION
    Layer 11 (OUTER) : 187 OMEGA

Author: ASIOS Core Team
Version: 1.0.0
"""

from __future__ import annotations

import os
import sys
import json
import time
import socket
import struct
import hashlib
import asyncio
import platform
import threading
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import uuid

# =============================================================================
# BRAHIM NETWORK CONSTANTS
# =============================================================================

BRAHIM_SEQUENCE = [27, 42, 60, 75, 97, 107, 117, 139, 154, 172, 187]
BRAHIM_CENTER = 107
BRAHIM_SUM = 214

MIRROR_PAIRS = [
    (27, 187),   # GENESIS <-> OMEGA
    (42, 172),   # DUALITY <-> COMPLETION
    (60, 154),   # MANIFESTATION <-> INFINITY
    (75, 139),   # TESSERACT <-> HARMONY
    (97, 117),   # THRESHOLD <-> EMERGENCE
]

LAYER_INFO = {
    27:  {"layer": 1,  "type": "SEED",  "name": "GENESIS"},
    42:  {"layer": 2,  "type": "INNER", "name": "DUALITY"},
    60:  {"layer": 3,  "type": "INNER", "name": "MANIFESTATION"},
    75:  {"layer": 4,  "type": "INNER", "name": "TESSERACT"},
    97:  {"layer": 5,  "type": "INNER", "name": "THRESHOLD"},
    107: {"layer": 6,  "type": "CORE",  "name": "CONVERGENCE"},
    117: {"layer": 7,  "type": "OUTER", "name": "EMERGENCE"},
    139: {"layer": 8,  "type": "OUTER", "name": "HARMONY"},
    154: {"layer": 9,  "type": "OUTER", "name": "INFINITY"},
    172: {"layer": 10, "type": "OUTER", "name": "COMPLETION"},
    187: {"layer": 11, "type": "OUTER", "name": "OMEGA"},
}

# Network ports based on Brahim numbers
BEACON_BASE_PORT = 10700  # 107 * 100
DISCOVERY_PORT = 21400    # 214 * 100

# Protocol magic bytes
BRAHIM_MAGIC = b'BRH\x6b'  # 0x6b = 107


# =============================================================================
# BEACON STATUS
# =============================================================================

class BeaconStatus(Enum):
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    ONLINE = "online"
    ROUTING = "routing"
    SYNCHRONIZED = "synchronized"


# =============================================================================
# BEACON IDENTITY
# =============================================================================

@dataclass
class BeaconIdentity:
    """Unique identity of a Brahim beacon."""
    node_id: str              # 16-char hex ID
    brahim_number: int        # Position in sequence (27-187)
    layer: int                # Onion layer (1-11)
    layer_type: str           # SEED, INNER, CORE, OUTER
    name: str                 # Gematria name
    mirror: int               # Mirror pair partner
    hardware_id: str          # Machine identifier
    coordinates: Optional[Tuple[float, float]] = None

    def to_bytes(self) -> bytes:
        """Serialize identity for network transmission."""
        data = {
            "node_id": self.node_id,
            "bn": self.brahim_number,
            "layer": self.layer,
            "mirror": self.mirror,
            "hw": self.hardware_id[:16],
        }
        if self.coordinates:
            data["lat"] = self.coordinates[0]
            data["lon"] = self.coordinates[1]
        return json.dumps(data).encode('utf-8')

    @classmethod
    def from_bytes(cls, data: bytes) -> 'BeaconIdentity':
        """Deserialize identity from network."""
        obj = json.loads(data.decode('utf-8'))
        info = LAYER_INFO.get(obj["bn"], LAYER_INFO[107])
        coords = None
        if "lat" in obj and "lon" in obj:
            coords = (obj["lat"], obj["lon"])
        return cls(
            node_id=obj["node_id"],
            brahim_number=obj["bn"],
            layer=info["layer"],
            layer_type=info["type"],
            name=info["name"],
            mirror=BRAHIM_SUM - obj["bn"] if obj["bn"] != 107 else 107,
            hardware_id=obj["hw"],
            coordinates=coords,
        )


# =============================================================================
# BRAHIM PACKET
# =============================================================================

@dataclass
class BrahimPacket:
    """A packet routed through the Brahim Onion Network."""
    packet_id: str
    source_bn: int
    destination_bn: int
    route: List[int]          # Brahim numbers in route (always includes 107)
    payload: bytes
    timestamp: float
    hop_count: int = 0

    def to_bytes(self) -> bytes:
        """Serialize packet for transmission."""
        header = struct.pack(
            '>4s16sHHBBd',
            BRAHIM_MAGIC,
            self.packet_id.encode('utf-8')[:16].ljust(16, b'\x00'),
            self.source_bn,
            self.destination_bn,
            len(self.route),
            self.hop_count,
            self.timestamp,
        )
        route_bytes = struct.pack(f'>{len(self.route)}H', *self.route)
        payload_len = struct.pack('>I', len(self.payload))
        return header + route_bytes + payload_len + self.payload

    @classmethod
    def from_bytes(cls, data: bytes) -> 'BrahimPacket':
        """Deserialize packet from network."""
        magic, pid, src, dst, route_len, hops, ts = struct.unpack(
            '>4s16sHHBBd', data[:36]
        )
        if magic != BRAHIM_MAGIC:
            raise ValueError("Invalid Brahim packet magic")

        route_start = 36
        route_end = route_start + route_len * 2
        route = list(struct.unpack(f'>{route_len}H', data[route_start:route_end]))

        payload_len = struct.unpack('>I', data[route_end:route_end+4])[0]
        payload = data[route_end+4:route_end+4+payload_len]

        return cls(
            packet_id=pid.rstrip(b'\x00').decode('utf-8'),
            source_bn=src,
            destination_bn=dst,
            route=route,
            payload=payload,
            timestamp=ts,
            hop_count=hops,
        )


# =============================================================================
# ROUTE CALCULATOR
# =============================================================================

def calculate_route(source_bn: int, dest_bn: int) -> List[int]:
    """
    Calculate route through Brahim Onion Network.

    All routes MUST pass through CENTER (107).

    Route pattern:
        source -> ... -> 107 -> ... -> destination
    """
    if source_bn not in BRAHIM_SEQUENCE:
        source_bn = 107
    if dest_bn not in BRAHIM_SEQUENCE:
        dest_bn = 107

    source_idx = BRAHIM_SEQUENCE.index(source_bn)
    dest_idx = BRAHIM_SEQUENCE.index(dest_bn)
    center_idx = BRAHIM_SEQUENCE.index(107)

    # Route: source -> center
    if source_idx <= center_idx:
        to_center = BRAHIM_SEQUENCE[source_idx:center_idx+1]
    else:
        to_center = BRAHIM_SEQUENCE[center_idx:source_idx+1][::-1]

    # Route: center -> destination
    if center_idx <= dest_idx:
        from_center = BRAHIM_SEQUENCE[center_idx:dest_idx+1]
    else:
        from_center = BRAHIM_SEQUENCE[dest_idx:center_idx+1][::-1]

    # Combine (center appears once)
    route = to_center + from_center[1:]

    return route


# =============================================================================
# PEER REGISTRY
# =============================================================================

class PeerRegistry:
    """Registry of known peers in the Brahim network."""

    def __init__(self):
        self.peers: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def register(self, identity: BeaconIdentity, address: Tuple[str, int]):
        """Register a peer."""
        with self.lock:
            self.peers[identity.node_id] = {
                "identity": identity,
                "address": address,
                "last_seen": time.time(),
                "active": True,
            }

    def get_by_brahim_number(self, bn: int) -> List[Dict[str, Any]]:
        """Get all peers at a specific Brahim number."""
        with self.lock:
            return [
                p for p in self.peers.values()
                if p["identity"].brahim_number == bn and p["active"]
            ]

    def get_route_peers(self, route: List[int]) -> List[Dict[str, Any]]:
        """Get peers along a route."""
        result = []
        for bn in route:
            peers = self.get_by_brahim_number(bn)
            if peers:
                result.append(peers[0])  # Take first available
        return result

    def cleanup_stale(self, max_age: float = 300):
        """Remove stale peers (not seen in max_age seconds)."""
        now = time.time()
        with self.lock:
            stale = [
                nid for nid, p in self.peers.items()
                if now - p["last_seen"] > max_age
            ]
            for nid in stale:
                self.peers[nid]["active"] = False


# =============================================================================
# BRAHIM BEACON
# =============================================================================

class BrahimBeacon:
    """
    A hardware beacon node in the Brahim Onion Network.

    This is a REAL network service that:
    - Broadcasts presence via UDP
    - Accepts connections from other beacons
    - Routes packets through the onion layers
    - Maintains persistent identity
    """

    def __init__(
        self,
        brahim_number: int = 107,
        coordinates: Optional[Tuple[float, float]] = None,
        data_dir: Optional[Path] = None,
    ):
        """
        Initialize the Brahim Beacon.

        Args:
            brahim_number: Your position in the Brahim sequence (27-187)
            coordinates: Optional geographic coordinates (lat, lon)
            data_dir: Directory for persistent data
        """
        # Validate Brahim number
        if brahim_number not in BRAHIM_SEQUENCE:
            # Find nearest
            brahim_number = min(BRAHIM_SEQUENCE, key=lambda x: abs(x - brahim_number))

        self.brahim_number = brahim_number
        self.coordinates = coordinates
        self.data_dir = data_dir or Path("data/beacon")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Generate or load identity
        self.identity = self._load_or_create_identity()

        # Network state
        self.status = BeaconStatus.OFFLINE
        self.peers = PeerRegistry()
        self.packet_count = 0
        self.bytes_routed = 0

        # Sockets
        self._discovery_socket: Optional[socket.socket] = None
        self._service_socket: Optional[socket.socket] = None

        # Threading
        self._running = False
        self._threads: List[threading.Thread] = []

        # Callbacks
        self._on_packet_callbacks = []
        self._on_peer_callbacks = []

    def _get_hardware_id(self) -> str:
        """Generate a hardware-based identifier."""
        components = [
            platform.node(),
            platform.machine(),
            str(uuid.getnode()),  # MAC address based
        ]
        seed = ":".join(components)
        return hashlib.sha256(seed.encode()).hexdigest()[:32]

    def _identity_file(self) -> Path:
        return self.data_dir / "beacon_identity.json"

    def _load_or_create_identity(self) -> BeaconIdentity:
        """Load existing identity or create new one."""
        id_file = self._identity_file()

        if id_file.exists():
            try:
                data = json.loads(id_file.read_text())
                info = LAYER_INFO[data["brahim_number"]]
                return BeaconIdentity(
                    node_id=data["node_id"],
                    brahim_number=data["brahim_number"],
                    layer=info["layer"],
                    layer_type=info["type"],
                    name=info["name"],
                    mirror=data["mirror"],
                    hardware_id=data["hardware_id"],
                    coordinates=tuple(data["coordinates"]) if data.get("coordinates") else None,
                )
            except Exception:
                pass

        # Create new identity
        info = LAYER_INFO[self.brahim_number]
        mirror = BRAHIM_SUM - self.brahim_number if self.brahim_number != 107 else 107

        identity = BeaconIdentity(
            node_id=hashlib.sha256(
                f"{self._get_hardware_id()}:{self.brahim_number}:{time.time()}".encode()
            ).hexdigest()[:16],
            brahim_number=self.brahim_number,
            layer=info["layer"],
            layer_type=info["type"],
            name=info["name"],
            mirror=mirror,
            hardware_id=self._get_hardware_id(),
            coordinates=self.coordinates,
        )

        # Save
        self._save_identity(identity)
        return identity

    def _save_identity(self, identity: BeaconIdentity):
        """Persist identity to disk."""
        data = {
            "node_id": identity.node_id,
            "brahim_number": identity.brahim_number,
            "mirror": identity.mirror,
            "hardware_id": identity.hardware_id,
            "coordinates": list(identity.coordinates) if identity.coordinates else None,
            "created": datetime.now(timezone.utc).isoformat(),
        }
        self._identity_file().write_text(json.dumps(data, indent=2))

    # -------------------------------------------------------------------------
    # NETWORK OPERATIONS
    # -------------------------------------------------------------------------

    def start(self) -> Dict[str, Any]:
        """
        Start the beacon - begin listening and broadcasting.

        Returns:
            Startup report
        """
        if self._running:
            return {"error": "Beacon already running"}

        self.status = BeaconStatus.INITIALIZING
        self._running = True

        try:
            # Create discovery socket (UDP broadcast)
            self._discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._discovery_socket.bind(('', DISCOVERY_PORT))
            self._discovery_socket.settimeout(1.0)

            # Create service socket (TCP)
            self._service_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._service_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            service_port = BEACON_BASE_PORT + self.brahim_number
            self._service_socket.bind(('', service_port))
            self._service_socket.listen(10)
            self._service_socket.settimeout(1.0)

            # Start threads
            discovery_thread = threading.Thread(target=self._discovery_loop, daemon=True)
            broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
            service_thread = threading.Thread(target=self._service_loop, daemon=True)

            self._threads = [discovery_thread, broadcast_thread, service_thread]
            for t in self._threads:
                t.start()

            self.status = BeaconStatus.ONLINE

            return {
                "status": "online",
                "node_id": self.identity.node_id,
                "brahim_number": self.brahim_number,
                "name": self.identity.name,
                "layer": self.identity.layer,
                "layer_type": self.identity.layer_type,
                "mirror": self.identity.mirror,
                "discovery_port": DISCOVERY_PORT,
                "service_port": service_port,
                "hardware_id": self.identity.hardware_id[:8] + "...",
            }

        except Exception as e:
            self._running = False
            self.status = BeaconStatus.OFFLINE
            return {"error": str(e)}

    def stop(self) -> Dict[str, Any]:
        """Stop the beacon gracefully."""
        self._running = False

        # Wait for threads
        for t in self._threads:
            t.join(timeout=2.0)

        # Close sockets
        if self._discovery_socket:
            self._discovery_socket.close()
        if self._service_socket:
            self._service_socket.close()

        self.status = BeaconStatus.OFFLINE

        return {
            "status": "offline",
            "node_id": self.identity.node_id,
            "packets_routed": self.packet_count,
            "bytes_routed": self.bytes_routed,
        }

    def _discovery_loop(self):
        """Listen for peer discovery broadcasts."""
        while self._running:
            try:
                data, addr = self._discovery_socket.recvfrom(4096)
                if data.startswith(BRAHIM_MAGIC):
                    # Parse peer announcement
                    identity_data = data[4:]
                    peer_identity = BeaconIdentity.from_bytes(identity_data)

                    # Don't register ourselves
                    if peer_identity.node_id != self.identity.node_id:
                        self.peers.register(peer_identity, addr)

                        # Notify callbacks
                        for cb in self._on_peer_callbacks:
                            try:
                                cb(peer_identity, addr)
                            except Exception:
                                pass

            except socket.timeout:
                continue
            except Exception:
                continue

    def _broadcast_loop(self):
        """Broadcast our presence periodically."""
        broadcast_addr = ('<broadcast>', DISCOVERY_PORT)

        while self._running:
            try:
                # Build announcement
                announcement = BRAHIM_MAGIC + self.identity.to_bytes()

                # Broadcast
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(announcement, broadcast_addr)
                sock.close()

            except Exception:
                pass

            # Broadcast every 10 seconds
            time.sleep(10)

    def _service_loop(self):
        """Accept and handle incoming connections."""
        while self._running:
            try:
                conn, addr = self._service_socket.accept()
                # Handle in separate thread
                handler = threading.Thread(
                    target=self._handle_connection,
                    args=(conn, addr),
                    daemon=True,
                )
                handler.start()
            except socket.timeout:
                continue
            except Exception:
                continue

    def _handle_connection(self, conn: socket.socket, addr: Tuple[str, int]):
        """Handle an incoming connection."""
        try:
            conn.settimeout(30.0)

            # Receive packet
            header = conn.recv(4096)
            if not header.startswith(BRAHIM_MAGIC):
                conn.close()
                return

            packet = BrahimPacket.from_bytes(header)
            self.packet_count += 1
            self.bytes_routed += len(header)

            # Route the packet
            self._route_packet(packet, conn)

        except Exception:
            pass
        finally:
            conn.close()

    def _route_packet(self, packet: BrahimPacket, conn: socket.socket):
        """Route a packet through the network."""
        # Find next hop
        current_idx = packet.route.index(self.brahim_number) if self.brahim_number in packet.route else -1

        if current_idx == -1 or current_idx >= len(packet.route) - 1:
            # We are the destination or end of route
            for cb in self._on_packet_callbacks:
                try:
                    cb(packet)
                except Exception:
                    pass
            return

        # Forward to next hop
        next_bn = packet.route[current_idx + 1]
        peers = self.peers.get_by_brahim_number(next_bn)

        if peers:
            peer = peers[0]
            packet.hop_count += 1

            try:
                fwd_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                fwd_sock.settimeout(10.0)
                fwd_sock.connect(peer["address"])
                fwd_sock.sendall(packet.to_bytes())
                fwd_sock.close()
            except Exception:
                pass

    # -------------------------------------------------------------------------
    # PUBLIC API
    # -------------------------------------------------------------------------

    def send(self, destination_bn: int, payload: bytes) -> str:
        """
        Send a packet to a destination Brahim number.

        Args:
            destination_bn: Target Brahim number (27-187)
            payload: Data to send

        Returns:
            Packet ID
        """
        route = calculate_route(self.brahim_number, destination_bn)

        packet = BrahimPacket(
            packet_id=hashlib.sha256(
                f"{self.identity.node_id}:{time.time()}".encode()
            ).hexdigest()[:16],
            source_bn=self.brahim_number,
            destination_bn=destination_bn,
            route=route,
            payload=payload,
            timestamp=time.time(),
        )

        # If we're the only hop, deliver locally
        if len(route) == 1:
            for cb in self._on_packet_callbacks:
                try:
                    cb(packet)
                except Exception:
                    pass
            return packet.packet_id

        # Send to first hop (or next if we're first)
        start_idx = 1 if route[0] == self.brahim_number else 0
        next_bn = route[start_idx]
        peers = self.peers.get_by_brahim_number(next_bn)

        if peers:
            peer = peers[0]
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10.0)
                sock.connect(peer["address"])
                sock.sendall(packet.to_bytes())
                sock.close()
                self.packet_count += 1
                self.bytes_routed += len(packet.to_bytes())
            except Exception as e:
                pass

        return packet.packet_id

    def on_packet(self, callback):
        """Register callback for received packets."""
        self._on_packet_callbacks.append(callback)

    def on_peer_discovered(self, callback):
        """Register callback for peer discovery."""
        self._on_peer_callbacks.append(callback)

    def get_status(self) -> Dict[str, Any]:
        """Get current beacon status."""
        return {
            "status": self.status.value,
            "node_id": self.identity.node_id,
            "brahim_number": self.brahim_number,
            "name": self.identity.name,
            "layer": self.identity.layer,
            "layer_type": self.identity.layer_type,
            "mirror": self.identity.mirror,
            "coordinates": self.coordinates,
            "peers_known": len(self.peers.peers),
            "packets_routed": self.packet_count,
            "bytes_routed": self.bytes_routed,
            "hardware_id": self.identity.hardware_id[:8] + "...",
        }

    def get_network_topology(self) -> Dict[str, Any]:
        """Get view of the network from this beacon's perspective."""
        layers = {}
        for bn, info in LAYER_INFO.items():
            peers = self.peers.get_by_brahim_number(bn)
            layers[bn] = {
                "name": info["name"],
                "layer": info["layer"],
                "type": info["type"],
                "peers": len(peers),
                "is_self": bn == self.brahim_number,
            }

        return {
            "self": self.brahim_number,
            "center": 107,
            "layers": layers,
            "mirror_pairs": MIRROR_PAIRS,
            "total_peers": len(self.peers.peers),
        }


# =============================================================================
# CLI ENTRY POINT
# =============================================================================

def run_beacon(
    brahim_number: int = 107,
    coordinates: Optional[Tuple[float, float]] = None,
):
    """
    Run the Brahim Beacon as a persistent service.

    Args:
        brahim_number: Your position in the network (27-187)
        coordinates: Optional geographic position (lat, lon)
    """
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("BRAHIM ONION NETWORK - HARDWARE BEACON")
    print("=" * 70)
    print()

    # Create beacon
    beacon = BrahimBeacon(
        brahim_number=brahim_number,
        coordinates=coordinates,
    )

    # Register callbacks
    def on_peer(identity, addr):
        print(f"[PEER] Discovered: {identity.name} ({identity.brahim_number}) at {addr[0]}")

    def on_packet(packet):
        print(f"[PACKET] Received from {packet.source_bn}: {len(packet.payload)} bytes")

    beacon.on_peer_discovered(on_peer)
    beacon.on_packet(on_packet)

    # Start
    print("Starting beacon...")
    result = beacon.start()

    if "error" in result:
        print(f"ERROR: {result['error']}")
        return

    print()
    print("BEACON ONLINE")
    print("-" * 50)
    print(f"  Node ID:       {result['node_id']}")
    print(f"  Brahim Number: {result['brahim_number']}")
    print(f"  Name:          {result['name']}")
    print(f"  Layer:         {result['layer']} ({result['layer_type']})")
    print(f"  Mirror:        {result['mirror']}")
    print(f"  Service Port:  {result['service_port']}")
    print(f"  Discovery:     {result['discovery_port']}")
    print("-" * 50)
    print()
    print("All routes pass through CENTER (107)")
    print("Press Ctrl+C to stop")
    print()

    try:
        while True:
            # Periodic status
            status = beacon.get_status()
            print(f"\r[{datetime.now().strftime('%H:%M:%S')}] "
                  f"Peers: {status['peers_known']} | "
                  f"Packets: {status['packets_routed']} | "
                  f"Bytes: {status['bytes_routed']}", end="", flush=True)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        beacon.stop()
        print("Beacon offline.")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Brahim Onion Network Beacon")
    parser.add_argument(
        "--bn", type=int, default=107,
        help="Brahim number (27, 42, 60, 75, 97, 107, 117, 139, 154, 172, 187)"
    )
    parser.add_argument(
        "--lat", type=float, default=None,
        help="Geographic latitude"
    )
    parser.add_argument(
        "--lon", type=float, default=None,
        help="Geographic longitude"
    )

    args = parser.parse_args()

    coords = None
    if args.lat is not None and args.lon is not None:
        coords = (args.lat, args.lon)

    run_beacon(brahim_number=args.bn, coordinates=coords)
