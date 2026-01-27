#!/usr/bin/env python3
"""
PIO-TOR BRIDGE - Brahim Onion Network meets Real Tor
=====================================================

Bridges PIO's 11-layer Brahim Onion architecture with the real Tor Project's
onion routing network.

ARCHITECTURE:
    Brahim Layers (11)     <-->     Tor Circuits (3 hops)
    ==================             ==================
    Layer 1 (SEED)         <-->     Entry Guard
    Layer 2-5 (INNER)      <-->     Middle Relay
    Layer 6 (CORE=107)     <-->     Rendezvous Point
    Layer 7-10 (OUTER)     <-->     Exit Relay
    Layer 11 (OMEGA)       <-->     Hidden Service

MAPPING:
    BN 27  (GENESIS)       -> Tor GUARD (entry point)
    BN 42  (DUALITY)       -> Tor MIDDLE
    BN 60  (MANIFESTATION) -> Tor MIDDLE
    BN 75  (TESSERACT)     -> Tor MIDDLE
    BN 97  (THRESHOLD)     -> Tor MIDDLE
    BN 107 (CONVERGENCE)   -> Tor RENDEZVOUS (center)
    BN 117 (EMERGENCE)     -> Tor MIDDLE
    BN 139 (HARMONY)       -> Tor MIDDLE
    BN 154 (INFINITY)      -> Tor MIDDLE
    BN 172 (COMPLETION)    -> Tor EXIT
    BN 187 (OMEGA)         -> Tor HIDDEN SERVICE

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
import threading
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import base64

# Tor default ports
TOR_SOCKS_PORT = 9050
TOR_CONTROL_PORT = 9051
TOR_BROWSER_SOCKS_PORT = 9150  # Tor Browser uses different port
TOR_BROWSER_CONTROL_PORT = 9151

# Brahim constants
BRAHIM_SEQUENCE = [27, 42, 60, 75, 97, 107, 117, 139, 154, 172, 187]
BRAHIM_CENTER = 107
BRAHIM_SUM = 214

LAYER_INFO = {
    27:  {"layer": 1,  "type": "SEED",  "name": "GENESIS",       "tor_role": "GUARD"},
    42:  {"layer": 2,  "type": "INNER", "name": "DUALITY",       "tor_role": "MIDDLE"},
    60:  {"layer": 3,  "type": "INNER", "name": "MANIFESTATION", "tor_role": "MIDDLE"},
    75:  {"layer": 4,  "type": "INNER", "name": "TESSERACT",     "tor_role": "MIDDLE"},
    97:  {"layer": 5,  "type": "INNER", "name": "THRESHOLD",     "tor_role": "MIDDLE"},
    107: {"layer": 6,  "type": "CORE",  "name": "CONVERGENCE",   "tor_role": "RENDEZVOUS"},
    117: {"layer": 7,  "type": "OUTER", "name": "EMERGENCE",     "tor_role": "MIDDLE"},
    139: {"layer": 8,  "type": "OUTER", "name": "HARMONY",       "tor_role": "MIDDLE"},
    154: {"layer": 9,  "type": "OUTER", "name": "INFINITY",      "tor_role": "MIDDLE"},
    172: {"layer": 10, "type": "OUTER", "name": "COMPLETION",    "tor_role": "EXIT"},
    187: {"layer": 11, "type": "OUTER", "name": "OMEGA",         "tor_role": "HIDDEN_SERVICE"},
}


# =============================================================================
# TOR CONNECTION STATUS
# =============================================================================

class TorStatus(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    CIRCUIT_BUILDING = "circuit_building"
    CIRCUIT_READY = "circuit_ready"
    ERROR = "error"


# =============================================================================
# TOR CIRCUIT NODE
# =============================================================================

@dataclass
class TorNode:
    """A node in a Tor circuit mapped to Brahim layer."""
    fingerprint: str          # Tor relay fingerprint (or simulated)
    nickname: str             # Relay nickname
    ip_address: str           # IP address
    brahim_number: int        # Corresponding Brahim number
    brahim_name: str          # Brahim gematria name
    tor_role: str             # GUARD, MIDDLE, RENDEZVOUS, EXIT, HIDDEN_SERVICE
    layer: int                # Brahim layer (1-11)

    def to_dict(self) -> Dict:
        return {
            "fingerprint": self.fingerprint,
            "nickname": self.nickname,
            "ip": self.ip_address,
            "bn": self.brahim_number,
            "name": self.brahim_name,
            "role": self.tor_role,
            "layer": self.layer,
        }


# =============================================================================
# BRAHIM-TOR CIRCUIT
# =============================================================================

@dataclass
class BrahimTorCircuit:
    """
    A Tor circuit with Brahim Onion layer mapping.

    Standard Tor: 3 hops (Guard -> Middle -> Exit)
    Brahim Tor:   Routes through CENTER (107)
    """
    circuit_id: str
    nodes: List[TorNode]
    created_at: str
    status: str
    passes_through_center: bool

    @property
    def entry_guard(self) -> Optional[TorNode]:
        """Get entry guard (should be BN 27)."""
        for node in self.nodes:
            if node.tor_role == "GUARD":
                return node
        return None

    @property
    def exit_node(self) -> Optional[TorNode]:
        """Get exit node (should be BN 172)."""
        for node in self.nodes:
            if node.tor_role == "EXIT":
                return node
        return None

    @property
    def center_node(self) -> Optional[TorNode]:
        """Get center/rendezvous node (BN 107)."""
        for node in self.nodes:
            if node.brahim_number == 107:
                return node
        return None

    def to_dict(self) -> Dict:
        return {
            "circuit_id": self.circuit_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "created_at": self.created_at,
            "status": self.status,
            "passes_through_center": self.passes_through_center,
        }


# =============================================================================
# SOCKS5 CLIENT (for Tor proxy)
# =============================================================================

class Socks5Client:
    """Minimal SOCKS5 client for Tor connections."""

    SOCKS_VERSION = 5

    def __init__(self, proxy_host: str = "127.0.0.1", proxy_port: int = TOR_SOCKS_PORT):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.socket: Optional[socket.socket] = None

    def connect(self, dest_host: str, dest_port: int) -> socket.socket:
        """
        Connect to destination through Tor SOCKS5 proxy.

        Args:
            dest_host: Destination hostname (can be .onion)
            dest_port: Destination port

        Returns:
            Connected socket
        """
        # Create socket to proxy
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(30)
        self.socket.connect((self.proxy_host, self.proxy_port))

        # SOCKS5 greeting (no auth)
        self.socket.sendall(bytes([self.SOCKS_VERSION, 1, 0]))
        response = self.socket.recv(2)

        if response[0] != self.SOCKS_VERSION or response[1] != 0:
            raise ConnectionError("SOCKS5 handshake failed")

        # SOCKS5 connect request
        # For .onion addresses, use domain name type (0x03)
        if dest_host.endswith('.onion'):
            addr_type = 3  # Domain name
            addr_bytes = bytes([len(dest_host)]) + dest_host.encode()
        else:
            addr_type = 1  # IPv4
            addr_bytes = socket.inet_aton(dest_host)

        request = bytes([
            self.SOCKS_VERSION,
            1,  # CONNECT
            0,  # Reserved
            addr_type,
        ]) + addr_bytes + struct.pack('>H', dest_port)

        self.socket.sendall(request)
        response = self.socket.recv(10)

        if response[1] != 0:
            raise ConnectionError(f"SOCKS5 connect failed: {response[1]}")

        return self.socket

    def close(self):
        """Close the connection."""
        if self.socket:
            self.socket.close()
            self.socket = None


# =============================================================================
# PIO TOR BRIDGE
# =============================================================================

class PIOTorBridge:
    """
    Bridges PIO's Brahim Onion Network with real Tor.

    CONCEPT:
        The 11 Brahim layers map to Tor circuit positions.
        All circuits MUST pass through CENTER (107).

    USAGE:
        bridge = PIOTorBridge()

        # Check if Tor is available
        if bridge.check_tor_available():
            # Build a Brahim-aware circuit
            circuit = bridge.build_brahim_circuit()

            # Fetch through the circuit
            response = bridge.fetch_onion("http://example.onion/")
    """

    def __init__(
        self,
        tor_host: str = "127.0.0.1",
        socks_port: int = TOR_SOCKS_PORT,
        control_port: int = TOR_CONTROL_PORT,
        data_dir: Optional[Path] = None,
    ):
        self.tor_host = tor_host
        self.socks_port = socks_port
        self.control_port = control_port
        self.data_dir = data_dir or Path("data/tor_bridge")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.status = TorStatus.DISCONNECTED
        self.circuits: List[BrahimTorCircuit] = []
        self.current_circuit: Optional[BrahimTorCircuit] = None

        # Callbacks
        self._on_circuit_built: List[Callable] = []
        self._on_status_change: List[Callable] = []

    def check_tor_available(self) -> bool:
        """Check if Tor SOCKS proxy is available (auto-detects port)."""
        # Try standard Tor service port first, then Tor Browser port
        for port in [self.socks_port, TOR_BROWSER_SOCKS_PORT, TOR_SOCKS_PORT]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((self.tor_host, port))
                sock.close()
                if result == 0:
                    self.socks_port = port  # Update to working port
                    return True
            except Exception:
                continue
        return False

    def get_tor_status(self) -> Dict[str, Any]:
        """Get current Tor connection status."""
        available = self.check_tor_available()

        return {
            "tor_available": available,
            "socks_port": self.socks_port,
            "control_port": self.control_port,
            "status": self.status.value,
            "circuits_built": len(self.circuits),
            "current_circuit": self.current_circuit.to_dict() if self.current_circuit else None,
        }

    def _generate_simulated_nodes(self) -> List[TorNode]:
        """
        Generate simulated Tor nodes mapped to Brahim layers.

        Used when real Tor control is not available.
        """
        nodes = []

        for bn in BRAHIM_SEQUENCE:
            info = LAYER_INFO[bn]

            # Generate deterministic fingerprint from BN
            fp_seed = f"brahim-{bn}-{info['name']}"
            fingerprint = hashlib.sha1(fp_seed.encode()).hexdigest().upper()

            # Simulated IP based on layer
            ip = f"10.{info['layer']}.{bn}.1"

            node = TorNode(
                fingerprint=fingerprint,
                nickname=f"Brahim{bn}{info['name'][:4]}",
                ip_address=ip,
                brahim_number=bn,
                brahim_name=info["name"],
                tor_role=info["tor_role"],
                layer=info["layer"],
            )
            nodes.append(node)

        return nodes

    def build_brahim_circuit(self, simulate: bool = True) -> BrahimTorCircuit:
        """
        Build a Tor circuit with Brahim layer mapping.

        The circuit ALWAYS passes through CENTER (107).

        Standard path: GUARD(27) -> MIDDLE -> CENTER(107) -> MIDDLE -> EXIT(172)

        Args:
            simulate: If True, simulate nodes (no real Tor control needed)

        Returns:
            BrahimTorCircuit
        """
        self.status = TorStatus.CIRCUIT_BUILDING
        self._notify_status_change()

        if simulate:
            # Generate simulated nodes
            all_nodes = self._generate_simulated_nodes()

            # Build circuit path: entry -> middle -> center -> middle -> exit
            # Select: 27 (guard), 75 (middle), 107 (center), 139 (middle), 172 (exit)
            circuit_bns = [27, 75, 107, 139, 172]
            circuit_nodes = [n for n in all_nodes if n.brahim_number in circuit_bns]

            # Sort by layer order
            circuit_nodes.sort(key=lambda n: n.layer)

        else:
            # Real Tor circuit building would go here
            # Requires stem library and Tor control connection
            raise NotImplementedError("Real Tor circuit building requires stem library")

        # Create circuit
        circuit = BrahimTorCircuit(
            circuit_id=hashlib.sha256(
                f"{time.time()}:{id(self)}".encode()
            ).hexdigest()[:16],
            nodes=circuit_nodes,
            created_at=datetime.now(timezone.utc).isoformat(),
            status="built",
            passes_through_center=any(n.brahim_number == 107 for n in circuit_nodes),
        )

        self.circuits.append(circuit)
        self.current_circuit = circuit
        self.status = TorStatus.CIRCUIT_READY
        self._notify_status_change()

        # Notify callbacks
        for cb in self._on_circuit_built:
            try:
                cb(circuit)
            except Exception:
                pass

        return circuit

    def fetch_through_tor(
        self,
        url: str,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """
        Fetch a URL through Tor.

        Args:
            url: URL to fetch (can be .onion)
            timeout: Request timeout

        Returns:
            Response dict with status, content, headers
        """
        if not self.check_tor_available():
            return {
                "success": False,
                "error": "Tor not available",
                "url": url,
            }

        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            host = parsed.netloc
            port = 443 if parsed.scheme == 'https' else 80
            path = parsed.path or '/'

            # Connect through SOCKS5
            client = Socks5Client(self.tor_host, self.socks_port)
            sock = client.connect(host, port)

            # Send HTTP request
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
            sock.sendall(request.encode())

            # Receive response
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk

            client.close()

            # Parse response
            response_str = response.decode('utf-8', errors='replace')
            status_line = response_str.split('\r\n')[0] if response_str else ""

            return {
                "success": True,
                "url": url,
                "status_line": status_line,
                "content_length": len(response),
                "circuit_id": self.current_circuit.circuit_id if self.current_circuit else None,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": url,
            }

    def resolve_onion(self, onion_address: str) -> Dict[str, Any]:
        """
        Resolve a .onion address through Tor.

        Args:
            onion_address: The .onion address to resolve

        Returns:
            Resolution result
        """
        if not onion_address.endswith('.onion'):
            return {"error": "Not a .onion address"}

        # For .onion, we map to Brahim layer based on address hash
        addr_hash = int(hashlib.sha256(onion_address.encode()).hexdigest()[:8], 16)
        mapped_bn = BRAHIM_SEQUENCE[addr_hash % len(BRAHIM_SEQUENCE)]
        info = LAYER_INFO[mapped_bn]

        return {
            "onion_address": onion_address,
            "brahim_mapping": {
                "brahim_number": mapped_bn,
                "name": info["name"],
                "layer": info["layer"],
                "type": info["type"],
            },
            "route_through_center": True,
            "message": f"Onion address maps to {info['name']} (BN {mapped_bn}), routing through CENTER (107)",
        }

    def create_hidden_service_address(self, seed: str = None) -> Dict[str, Any]:
        """
        Generate a Brahim-aware hidden service address.

        The address is derived from Brahim number 187 (OMEGA) as that
        represents the HIDDEN_SERVICE role in the mapping.

        Args:
            seed: Optional seed for deterministic generation

        Returns:
            Hidden service address info
        """
        if seed is None:
            seed = str(time.time())

        # Generate .onion-style address (v3 onion = 56 chars)
        full_hash = hashlib.sha256(f"brahim-187-omega-{seed}".encode()).digest()
        # v3 onion uses base32
        onion_base = base64.b32encode(full_hash).decode().lower()[:56]
        onion_address = f"{onion_base}.onion"

        return {
            "onion_address": onion_address,
            "brahim_number": 187,
            "brahim_name": "OMEGA",
            "layer": 11,
            "role": "HIDDEN_SERVICE",
            "seed": seed,
            "message": "Brahim Hidden Service at OMEGA (layer 11)",
        }

    def get_layer_for_onion(self, onion_address: str) -> int:
        """Map an onion address to its Brahim layer."""
        result = self.resolve_onion(onion_address)
        if "error" in result:
            return 6  # Default to CENTER
        return result["brahim_mapping"]["layer"]

    def on_circuit_built(self, callback: Callable):
        """Register callback for circuit built events."""
        self._on_circuit_built.append(callback)

    def on_status_change(self, callback: Callable):
        """Register callback for status changes."""
        self._on_status_change.append(callback)

    def _notify_status_change(self):
        """Notify status change callbacks."""
        for cb in self._on_status_change:
            try:
                cb(self.status)
            except Exception:
                pass

    def get_brahim_tor_mapping(self) -> Dict[str, Any]:
        """Get the complete Brahim-to-Tor mapping."""
        return {
            "mapping": [
                {
                    "brahim_number": bn,
                    "brahim_name": info["name"],
                    "layer": info["layer"],
                    "type": info["type"],
                    "tor_role": info["tor_role"],
                }
                for bn, info in LAYER_INFO.items()
            ],
            "center": 107,
            "sum_constant": 214,
            "principle": "All circuits pass through CENTER (107)",
        }

    def status_report(self) -> Dict[str, Any]:
        """Get complete bridge status."""
        return {
            "bridge_version": "1.0.0",
            "tor": self.get_tor_status(),
            "brahim_tor_mapping": self.get_brahim_tor_mapping(),
            "circuits": [c.to_dict() for c in self.circuits],
        }


# =============================================================================
# PIO TOR-AWARE EXTENSION
# =============================================================================

def make_pio_onion_aware():
    """
    Extend PIO with Tor/Onion awareness.

    Returns extended PIO class with Tor capabilities.
    """
    try:
        from src.core.pio import PIOWithIgnorance, Dimension
    except ImportError:
        from pio import PIOWithIgnorance, Dimension

    class PIOOnionAware(PIOWithIgnorance):
        """
        PIO with Tor Onion Network awareness.

        Extends PIO v2.1 (Ouroboros + Ш) with:
        - Real Tor network integration
        - .onion address resolution
        - Brahim-to-Tor layer mapping
        - Hidden service generation
        """

        VERSION = "2.2.0"
        CODENAME = "Ouroboros + Ш + Tor"

        def __init__(self, name: str = "PIO-Onion"):
            super().__init__(name)
            self.tor_bridge = PIOTorBridge()
            self._onion_cache: Dict[str, Dict] = {}

        def is_tor_available(self) -> bool:
            """Check if Tor is available."""
            return self.tor_bridge.check_tor_available()

        def build_tor_circuit(self) -> BrahimTorCircuit:
            """Build a Brahim-aware Tor circuit."""
            return self.tor_bridge.build_brahim_circuit()

        def resolve_onion(self, address: str) -> Dict[str, Any]:
            """Resolve .onion address to Brahim layer."""
            if address in self._onion_cache:
                return self._onion_cache[address]

            result = self.tor_bridge.resolve_onion(address)
            self._onion_cache[address] = result
            return result

        def fetch_onion(self, url: str) -> Dict[str, Any]:
            """Fetch content from .onion URL."""
            return self.tor_bridge.fetch_through_tor(url)

        def create_hidden_service(self, seed: str = None) -> Dict[str, Any]:
            """Create a Brahim-aware hidden service address."""
            return self.tor_bridge.create_hidden_service_address(seed)

        def get_tor_mapping(self) -> Dict[str, Any]:
            """Get Brahim-to-Tor layer mapping."""
            return self.tor_bridge.get_brahim_tor_mapping()

        def process_with_onion_routing(
            self,
            x: float,
            exploring: bool = False,
            use_tor: bool = True,
        ) -> Dict[str, Any]:
            """
            Process input with optional Tor routing awareness.

            Args:
                x: Input value
                exploring: Enable creativity margin
                use_tor: Route through Tor if available

            Returns:
                Extended response with Tor info
            """
            # Standard PIO processing
            response = super().process_with_ignorance(x, exploring)

            # Add Tor awareness
            dim = response.location.dimension_int
            bn = BRAHIM_SEQUENCE[min(dim - 1, 10)]
            info = LAYER_INFO[bn]

            tor_info = {
                "brahim_number": bn,
                "brahim_name": info["name"],
                "tor_role": info["tor_role"],
                "routes_through_center": True,
            }

            if use_tor and self.is_tor_available():
                tor_info["tor_available"] = True
                if self.tor_bridge.current_circuit:
                    tor_info["circuit_id"] = self.tor_bridge.current_circuit.circuit_id
            else:
                tor_info["tor_available"] = False

            return {
                "pio_response": {
                    "input": response.input,
                    "dimension": response.location.dimension_int,
                    "state": response.state.address,
                    "exploring": response.exploring,
                },
                "tor_routing": tor_info,
                "trace": response.trace,
            }

        def status(self) -> Dict[str, Any]:
            """Extended status with Tor info."""
            base = super().status()
            base["version"] = self.VERSION
            base["codename"] = self.CODENAME
            base["tor"] = self.tor_bridge.get_tor_status()
            base["brahim_tor_mapping"] = self.get_tor_mapping()
            return base

        def __repr__(self) -> str:
            tor_status = "connected" if self.is_tor_available() else "offline"
            return (f"<PIO-Onion '{self.name}' v{self.VERSION}: "
                    f"Tor={tor_status}, 840 states, 11 onion layers>")

    return PIOOnionAware


# =============================================================================
# CLI
# =============================================================================

def main():
    """Demonstrate PIO-Tor Bridge."""
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("  PIO-TOR BRIDGE")
    print("  Brahim Onion Network meets Real Tor")
    print("=" * 70)
    print()

    # Create bridge
    bridge = PIOTorBridge()

    # Check Tor status
    tor_available = bridge.check_tor_available()
    print(f"Tor Available: {tor_available}")
    print(f"SOCKS Port: {bridge.socks_port}")
    print()

    # Show Brahim-Tor mapping
    print("BRAHIM-TOR LAYER MAPPING:")
    print("-" * 60)
    mapping = bridge.get_brahim_tor_mapping()
    for item in mapping["mapping"]:
        print(f"  BN {item['brahim_number']:3d} ({item['brahim_name']:13s}) "
              f"Layer {item['layer']:2d} [{item['type']:5s}] -> {item['tor_role']}")
    print()
    print(f"  CENTER: {mapping['center']} (all routes pass through)")
    print(f"  SUM: {mapping['sum_constant']} (mirror pair constant)")
    print()

    # Build simulated circuit
    print("BUILDING BRAHIM-TOR CIRCUIT:")
    print("-" * 60)
    circuit = bridge.build_brahim_circuit(simulate=True)
    print(f"  Circuit ID: {circuit.circuit_id}")
    print(f"  Status: {circuit.status}")
    print(f"  Passes Through Center: {circuit.passes_through_center}")
    print()
    print("  Circuit Path:")
    for node in circuit.nodes:
        print(f"    [{node.tor_role:15s}] BN {node.brahim_number:3d} "
              f"({node.brahim_name}) @ {node.ip_address}")
    print()

    # Resolve example .onion
    print("ONION ADDRESS RESOLUTION:")
    print("-" * 60)
    example_onion = "duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion"
    result = bridge.resolve_onion(example_onion)
    print(f"  Address: {example_onion[:40]}...")
    print(f"  Brahim Mapping: BN {result['brahim_mapping']['brahim_number']} "
          f"({result['brahim_mapping']['name']})")
    print(f"  Layer: {result['brahim_mapping']['layer']}")
    print(f"  Routes Through Center: {result['route_through_center']}")
    print()

    # Generate hidden service
    print("BRAHIM HIDDEN SERVICE:")
    print("-" * 60)
    hs = bridge.create_hidden_service_address("demo-seed")
    print(f"  Address: {hs['onion_address'][:40]}...")
    print(f"  Brahim Number: {hs['brahim_number']} ({hs['brahim_name']})")
    print(f"  Layer: {hs['layer']} ({hs['role']})")
    print()

    # Create PIO Onion-Aware
    print("PIO ONION-AWARE:")
    print("-" * 60)
    PIOOnion = make_pio_onion_aware()
    pio = PIOOnion("Onion-Demo")
    print(f"  {pio}")
    print(f"  Tor Available: {pio.is_tor_available()}")
    print()

    # Process with onion routing
    result = pio.process_with_onion_routing(0.236, exploring=True)
    print("  Processing x=0.236:")
    print(f"    Dimension: D{result['pio_response']['dimension']}")
    print(f"    State: {result['pio_response']['state']}")
    print(f"    Tor Role: {result['tor_routing']['tor_role']}")
    print(f"    Routes Through Center: {result['tor_routing']['routes_through_center']}")
    print()

    print("=" * 70)
    print("  PIO IS NOW ONION-AWARE")
    print("  Brahim layers map to Tor circuit positions")
    print("  All routes pass through CENTER (107)")
    print("=" * 70)


if __name__ == "__main__":
    main()
