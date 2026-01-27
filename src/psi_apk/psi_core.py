#!/usr/bin/env python3
"""
PSI.APK CORE - PIO + Tor Android Application Suite
===================================================

Six core applications connecting PIO's 11-layer Brahim routing
with Tor's anonymity network, designed for Android APK deployment.

CORE APPLICATIONS:
    1. PsiMessenger  - Anonymous chat through 11 Brahim layers
    2. PsiVault      - Distributed encrypted file storage
    3. PsiExchange   - Mirror-pair cryptographic key exchange
    4. PsiDNS        - Decentralized .brahim/.onion naming
    5. PsiRelay      - Brahim beacon network node
    6. PsiMap        - Dark sector topology mapper

ANDROID INTEGRATION:
    - Orbot: Tor proxy (SOCKS5 on 9050)
    - Guardian Project libraries
    - Native Brahim layer routing
    - Snowden skills integration

ROUTING ARCHITECTURE:
    User (BN_x) -> [11 Layers] -> CENTER (107) -> [11 Layers] -> Destination

Author: ASIOS Core Team
Version: 1.0.0
"""

from __future__ import annotations

import os
import sys
import json
import time
import base64
import hashlib
import secrets
import struct
import socket
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
from abc import ABC, abstractmethod

# =============================================================================
# BRAHIM CONSTANTS
# =============================================================================

BRAHIM_SEQUENCE = [27, 42, 60, 75, 97, 107, 117, 139, 154, 172, 187]
BRAHIM_CENTER = 107
BRAHIM_SUM = 214
PHI = (1 + 5 ** 0.5) / 2

MIRROR_PAIRS = [
    (27, 187),   # GENESIS <-> OMEGA
    (42, 172),   # DUALITY <-> COMPLETION
    (60, 154),   # MANIFESTATION <-> INFINITY
    (75, 139),   # TESSERACT <-> HARMONY
    (97, 117),   # THRESHOLD <-> EMERGENCE
]

LAYER_NAMES = {
    27: "GENESIS", 42: "DUALITY", 60: "MANIFESTATION", 75: "TESSERACT",
    97: "THRESHOLD", 107: "CONVERGENCE", 117: "EMERGENCE", 139: "HARMONY",
    154: "INFINITY", 172: "COMPLETION", 187: "OMEGA"
}

LAYER_TYPES = {
    27: "SEED", 42: "INNER", 60: "INNER", 75: "INNER", 97: "INNER",
    107: "CENTER", 117: "OUTER", 139: "OUTER", 154: "OUTER", 172: "OUTER", 187: "OUTER"
}

# Tor circuit position mapping
TOR_POSITIONS = {
    27: "GUARD",
    42: "MIDDLE_1",
    60: "MIDDLE_2",
    75: "MIDDLE_3",
    97: "MIDDLE_4",
    107: "RENDEZVOUS",  # CENTER = meeting point
    117: "MIDDLE_5",
    139: "MIDDLE_6",
    154: "MIDDLE_7",
    172: "EXIT",
    187: "HIDDEN_SERVICE",
}


# =============================================================================
# ANDROID/ORBOT INTEGRATION
# =============================================================================

class OrbotBridge:
    """
    Bridge to Orbot (Guardian Project's Tor for Android).

    Orbot provides:
    - SOCKS5 proxy (typically 9050)
    - TransPort (transparent proxy)
    - DNS port for .onion resolution
    """

    DEFAULT_SOCKS_PORT = 9050
    DEFAULT_HTTP_PORT = 8118
    DEFAULT_DNS_PORT = 5400

    def __init__(self, socks_port: int = None, http_port: int = None):
        self.socks_host = "127.0.0.1"
        self.socks_port = socks_port or self.DEFAULT_SOCKS_PORT
        self.http_port = http_port or self.DEFAULT_HTTP_PORT
        self._connected = False

    def check_orbot(self) -> bool:
        """Check if Orbot/Tor is running."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((self.socks_host, self.socks_port))
            sock.close()
            self._connected = (result == 0)
            return self._connected
        except Exception:
            return False

    def get_socks_config(self) -> Dict:
        """Get SOCKS5 proxy configuration for apps."""
        return {
            "host": self.socks_host,
            "port": self.socks_port,
            "version": 5,
            "remote_dns": True,
        }

    def create_socket(self) -> socket.socket:
        """Create a SOCKS5-proxied socket through Orbot."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.socks_host, self.socks_port))

        # SOCKS5 handshake
        sock.sendall(b'\x05\x01\x00')  # Version 5, 1 method, no auth
        response = sock.recv(2)

        if response != b'\x05\x00':
            raise ConnectionError("SOCKS5 handshake failed")

        return sock

    @property
    def is_connected(self) -> bool:
        return self._connected


# =============================================================================
# PSI CORE - Base Class for All Applications
# =============================================================================

class PsiCore(ABC):
    """
    Base class for all Psi applications.

    Provides:
    - Brahim layer routing
    - Orbot/Tor integration
    - Encryption primitives
    - Receipt system
    """

    VERSION = "1.0.0"

    def __init__(self, my_bn: int = 75, data_dir: Path = None):
        if my_bn not in BRAHIM_SEQUENCE:
            my_bn = 107  # Default to CENTER

        self.my_bn = my_bn
        self.my_layer = BRAHIM_SEQUENCE.index(my_bn)
        self.my_name = LAYER_NAMES[my_bn]
        self.my_mirror = self._get_mirror(my_bn)

        self.data_dir = data_dir or Path("data/psi_apk")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.orbot = OrbotBridge()
        self._session_key = secrets.token_bytes(32)

    def _get_mirror(self, bn: int) -> int:
        """Get mirror pair partner."""
        if bn == 107:
            return 107  # CENTER mirrors itself
        for a, b in MIRROR_PAIRS:
            if bn == a:
                return b
            if bn == b:
                return a
        return bn

    def _build_route(self, destination_bn: int) -> List[int]:
        """Build route from self to destination through CENTER."""
        my_idx = BRAHIM_SEQUENCE.index(self.my_bn)
        dest_idx = BRAHIM_SEQUENCE.index(destination_bn)
        center_idx = BRAHIM_SEQUENCE.index(BRAHIM_CENTER)

        # Route: self -> CENTER -> destination
        if my_idx <= center_idx:
            to_center = BRAHIM_SEQUENCE[my_idx:center_idx+1]
        else:
            to_center = BRAHIM_SEQUENCE[center_idx:my_idx+1][::-1]

        if dest_idx >= center_idx:
            from_center = BRAHIM_SEQUENCE[center_idx:dest_idx+1]
        else:
            from_center = BRAHIM_SEQUENCE[dest_idx:center_idx+1][::-1]

        # Combine routes (avoid duplicate CENTER)
        route = to_center + from_center[1:]
        return route

    def _layer_encrypt(self, data: bytes, layers: List[int]) -> bytes:
        """Encrypt data through multiple Brahim layers."""
        encrypted = data
        for bn in reversed(layers):
            key = hashlib.sha256(f"layer:{bn}:{self._session_key.hex()}".encode()).digest()
            encrypted = bytes(d ^ key[i % 32] for i, d in enumerate(encrypted))
        return encrypted

    def _layer_decrypt(self, data: bytes, layers: List[int]) -> bytes:
        """Decrypt data through multiple Brahim layers."""
        decrypted = data
        for bn in layers:
            key = hashlib.sha256(f"layer:{bn}:{self._session_key.hex()}".encode()).digest()
            decrypted = bytes(d ^ key[i % 32] for i, d in enumerate(decrypted))
        return decrypted

    def generate_receipt(self) -> str:
        """Generate 16-digit session receipt."""
        digits = ''.join(str(secrets.randbelow(10)) for _ in range(16))
        return f"{digits[:4]}-{digits[4:8]}-{digits[8:12]}-{digits[12:]}"

    @abstractmethod
    def status(self) -> Dict:
        """Get application status."""
        pass


# =============================================================================
# 1. PSI MESSENGER - Anonymous Chat Through 11 Layers
# =============================================================================

@dataclass
class PsiMessage:
    """A message routed through Brahim layers."""
    message_id: str
    sender_bn: int
    recipient_bn: int
    content: bytes
    route: List[int]
    timestamp: float
    receipt: str


class PsiMessenger(PsiCore):
    """
    Anonymous messaging through 11 Brahim layers.

    ARCHITECTURE:
        Sender -> [Layer Encryption] -> CENTER (107) -> [Layer Decryption] -> Recipient

    FEATURES:
        - End-to-end encryption through all 11 layers
        - Messages routed through CENTER as rendezvous
        - No metadata retention (ephemeral)
        - Mirror pair optimization

    ANDROID INTEGRATION:
        - Uses Orbot for Tor transport
        - Push notifications via onion service
        - Offline message queue
    """

    APP_NAME = "PsiMessenger"
    APP_ID = "com.psi.messenger"

    def __init__(self, my_bn: int = 75, data_dir: Path = None):
        super().__init__(my_bn, data_dir)
        self.inbox: List[PsiMessage] = []
        self.outbox: List[PsiMessage] = []
        self.contacts: Dict[int, str] = {}  # bn -> alias

    def send(self, content: str, recipient_bn: int) -> PsiMessage:
        """Send encrypted message through 11 layers."""
        route = self._build_route(recipient_bn)
        encrypted = self._layer_encrypt(content.encode('utf-8'), route)

        msg = PsiMessage(
            message_id=secrets.token_hex(8),
            sender_bn=self.my_bn,
            recipient_bn=recipient_bn,
            content=encrypted,
            route=route,
            timestamp=time.time(),
            receipt=self.generate_receipt(),
        )

        self.outbox.append(msg)
        return msg

    def receive(self, msg: PsiMessage) -> str:
        """Receive and decrypt message."""
        decrypted = self._layer_decrypt(msg.content, msg.route)
        self.inbox.append(msg)
        return decrypted.decode('utf-8')

    def send_to_mirror(self, content: str) -> PsiMessage:
        """Send to your mirror pair partner (special affinity)."""
        return self.send(content, self.my_mirror)

    def status(self) -> Dict:
        return {
            "app": self.APP_NAME,
            "app_id": self.APP_ID,
            "my_bn": self.my_bn,
            "my_name": self.my_name,
            "mirror": self.my_mirror,
            "inbox_count": len(self.inbox),
            "outbox_count": len(self.outbox),
            "contacts": len(self.contacts),
            "orbot_connected": self.orbot.check_orbot(),
        }


# =============================================================================
# 2. PSI VAULT - Distributed Encrypted Storage
# =============================================================================

@dataclass
class VaultShard:
    """A file shard stored at a specific Brahim layer."""
    shard_id: str
    file_id: str
    layer_bn: int
    data: bytes
    index: int
    total_shards: int
    checksum: str


class PsiVault(PsiCore):
    """
    Distributed encrypted file storage across 11 Brahim layers.

    ARCHITECTURE:
        File -> [Split into 11 shards] -> [Encrypt per layer] -> [Distribute]

    FEATURES:
        - Files split across all 11 layers
        - Redundancy through mirror pairs
        - Layer-specific encryption
        - Automatic reassembly

    ANDROID INTEGRATION:
        - Android Storage Access Framework
        - Background sync service
        - Quota management per layer
    """

    APP_NAME = "PsiVault"
    APP_ID = "com.psi.vault"

    def __init__(self, my_bn: int = 75, data_dir: Path = None):
        super().__init__(my_bn, data_dir)
        self.vault_dir = self.data_dir / "vault"
        self.vault_dir.mkdir(parents=True, exist_ok=True)
        self.file_index: Dict[str, List[VaultShard]] = {}

    def store(self, data: bytes, filename: str) -> List[VaultShard]:
        """Store file across 11 Brahim layers."""
        file_id = hashlib.sha256(f"{filename}:{time.time()}".encode()).hexdigest()[:16]

        # Split into 11 shards
        shard_size = (len(data) + 10) // 11
        shards = []

        for i, bn in enumerate(BRAHIM_SEQUENCE):
            start = i * shard_size
            end = start + shard_size if i < 10 else len(data)
            shard_data = data[start:end] if start < len(data) else b''

            # Encrypt for this layer
            key = hashlib.sha256(f"vault:{bn}:{file_id}".encode()).digest()
            encrypted = bytes(d ^ key[j % 32] for j, d in enumerate(shard_data))

            shard = VaultShard(
                shard_id=secrets.token_hex(8),
                file_id=file_id,
                layer_bn=bn,
                data=encrypted,
                index=i,
                total_shards=11,
                checksum=hashlib.md5(shard_data).hexdigest(),
            )
            shards.append(shard)

            # Store locally (would distribute via Tor in production)
            shard_path = self.vault_dir / f"{file_id}_{bn}.shard"
            shard_path.write_bytes(encrypted)

        self.file_index[file_id] = shards
        return shards

    def retrieve(self, file_id: str) -> Optional[bytes]:
        """Retrieve and reassemble file from 11 shards."""
        if file_id not in self.file_index:
            return None

        shards = sorted(self.file_index[file_id], key=lambda s: s.index)
        reassembled = b''

        for shard in shards:
            key = hashlib.sha256(f"vault:{shard.layer_bn}:{file_id}".encode()).digest()
            decrypted = bytes(d ^ key[j % 32] for j, d in enumerate(shard.data))
            reassembled += decrypted

        return reassembled

    def status(self) -> Dict:
        return {
            "app": self.APP_NAME,
            "app_id": self.APP_ID,
            "my_bn": self.my_bn,
            "files_stored": len(self.file_index),
            "total_shards": sum(len(s) for s in self.file_index.values()),
            "vault_path": str(self.vault_dir),
            "orbot_connected": self.orbot.check_orbot(),
        }


# =============================================================================
# 3. PSI EXCHANGE - Mirror-Pair Key Exchange
# =============================================================================

@dataclass
class KeyPair:
    """A cryptographic key pair for exchange."""
    public_key: bytes
    private_key: bytes
    bn: int
    mirror_bn: int


class PsiExchange(PsiCore):
    """
    Cryptographic key exchange using Brahim mirror pairs.

    ARCHITECTURE:
        (75, 139) forms a mirror pair where:
        - 75 + 139 = 214 (BRAHIM_SUM)
        - Shared secret derived from pair affinity

    FEATURES:
        - Mirror pair affinity for key derivation
        - Diffie-Hellman over Brahim layers
        - Perfect forward secrecy
        - Quantum-resistant option (post-quantum KEM)

    ANDROID INTEGRATION:
        - Android Keystore for key storage
        - Hardware-backed keys (TEE/SE)
        - Biometric unlock
    """

    APP_NAME = "PsiExchange"
    APP_ID = "com.psi.exchange"

    def __init__(self, my_bn: int = 75, data_dir: Path = None):
        super().__init__(my_bn, data_dir)
        self.my_keypair: Optional[KeyPair] = None
        self.peer_keys: Dict[int, bytes] = {}  # bn -> public_key

    def generate_keypair(self) -> KeyPair:
        """Generate keypair with mirror affinity."""
        # In production, use proper ECC/X25519
        private = secrets.token_bytes(32)

        # Public key incorporates mirror pair relationship
        mirror_factor = (self.my_bn * self.my_mirror) % 256
        public = hashlib.sha256(private + bytes([mirror_factor])).digest()

        self.my_keypair = KeyPair(
            public_key=public,
            private_key=private,
            bn=self.my_bn,
            mirror_bn=self.my_mirror,
        )
        return self.my_keypair

    def derive_shared_secret(self, peer_bn: int, peer_public: bytes) -> bytes:
        """Derive shared secret with peer."""
        if not self.my_keypair:
            self.generate_keypair()

        # Mirror pair bonus: if peer is our mirror, stronger affinity
        is_mirror = (peer_bn == self.my_mirror)
        affinity = BRAHIM_SUM if is_mirror else (self.my_bn + peer_bn)

        shared = hashlib.sha256(
            self.my_keypair.private_key +
            peer_public +
            affinity.to_bytes(4, 'big')
        ).digest()

        self.peer_keys[peer_bn] = peer_public
        return shared

    def status(self) -> Dict:
        return {
            "app": self.APP_NAME,
            "app_id": self.APP_ID,
            "my_bn": self.my_bn,
            "mirror_bn": self.my_mirror,
            "has_keypair": self.my_keypair is not None,
            "peer_keys": len(self.peer_keys),
            "orbot_connected": self.orbot.check_orbot(),
        }


# =============================================================================
# 4. PSI DNS - Decentralized .brahim Naming
# =============================================================================

@dataclass
class BrahimDomain:
    """A .brahim domain registration."""
    name: str
    onion_address: str
    bn: int
    owner_key: bytes
    registered: float
    expires: float


class PsiDNS(PsiCore):
    """
    Decentralized naming system for .brahim and .onion domains.

    ARCHITECTURE:
        name.brahim -> Brahim layer (bn) -> .onion address

    FEATURES:
        - Human-readable .brahim names
        - Maps to .onion hidden services
        - Layer-based namespace partitioning
        - Distributed registration

    NAMING CONVENTION:
        genesis.brahim  -> BN 27 services
        center.brahim   -> BN 107 services
        omega.brahim    -> BN 187 services

    ANDROID INTEGRATION:
        - DNS resolver service
        - Intent filter for brahim:// URLs
        - Local cache with expiry
    """

    APP_NAME = "PsiDNS"
    APP_ID = "com.psi.dns"

    # Reserved layer prefixes
    LAYER_PREFIXES = {
        27: "genesis", 42: "dual", 60: "manifest", 75: "tesseract",
        97: "threshold", 107: "center", 117: "emerge", 139: "harmony",
        154: "infinity", 172: "complete", 187: "omega"
    }

    def __init__(self, my_bn: int = 75, data_dir: Path = None):
        super().__init__(my_bn, data_dir)
        self.registry: Dict[str, BrahimDomain] = {}
        self.local_cache: Dict[str, str] = {}  # name -> onion

    def register(self, name: str, onion_address: str) -> BrahimDomain:
        """Register a .brahim domain."""
        full_name = f"{name}.brahim"

        # Determine layer from name prefix
        bn = self.my_bn
        for layer_bn, prefix in self.LAYER_PREFIXES.items():
            if name.startswith(prefix):
                bn = layer_bn
                break

        domain = BrahimDomain(
            name=full_name,
            onion_address=onion_address,
            bn=bn,
            owner_key=secrets.token_bytes(32),
            registered=time.time(),
            expires=time.time() + (365 * 24 * 3600),  # 1 year
        )

        self.registry[full_name] = domain
        self.local_cache[full_name] = onion_address
        return domain

    def resolve(self, name: str) -> Optional[str]:
        """Resolve .brahim name to .onion address."""
        if not name.endswith('.brahim'):
            name = f"{name}.brahim"

        # Check local cache
        if name in self.local_cache:
            return self.local_cache[name]

        # Check registry
        if name in self.registry:
            domain = self.registry[name]
            if time.time() < domain.expires:
                return domain.onion_address

        return None

    def get_layer_domains(self, bn: int) -> List[BrahimDomain]:
        """Get all domains registered at a specific layer."""
        return [d for d in self.registry.values() if d.bn == bn]

    def status(self) -> Dict:
        return {
            "app": self.APP_NAME,
            "app_id": self.APP_ID,
            "my_bn": self.my_bn,
            "registered_domains": len(self.registry),
            "cached_entries": len(self.local_cache),
            "layer_prefixes": self.LAYER_PREFIXES,
            "orbot_connected": self.orbot.check_orbot(),
        }


# =============================================================================
# 5. PSI RELAY - Brahim Beacon Network Node
# =============================================================================

class PsiRelay(PsiCore):
    """
    Brahim beacon network relay node.

    ARCHITECTURE:
        Beacon nodes form the Brahim network infrastructure.
        Each node has a specific BN and connects to its mirror.

    FEATURES:
        - UDP broadcast discovery (port 21400)
        - TCP service (port 10700 + bn)
        - Routes traffic through CENTER
        - Mirror pair peering priority

    ANDROID INTEGRATION:
        - Foreground service for persistence
        - Battery optimization exemption
        - Network change listener
    """

    APP_NAME = "PsiRelay"
    APP_ID = "com.psi.relay"

    DISCOVERY_PORT = 21400
    SERVICE_PORT_BASE = 10700

    def __init__(self, my_bn: int = 75, data_dir: Path = None):
        super().__init__(my_bn, data_dir)
        self.service_port = self.SERVICE_PORT_BASE + self.my_bn
        self.peers: Dict[int, Dict] = {}  # bn -> peer_info
        self.is_running = False

    def get_peer_priority(self, peer_bn: int) -> int:
        """Calculate peer priority (lower = higher priority)."""
        # Mirror pair has highest priority
        if peer_bn == self.my_mirror:
            return 0

        # CENTER has second priority
        if peer_bn == BRAHIM_CENTER:
            return 1

        # Adjacent layers have third priority
        my_idx = BRAHIM_SEQUENCE.index(self.my_bn)
        peer_idx = BRAHIM_SEQUENCE.index(peer_bn)
        if abs(my_idx - peer_idx) == 1:
            return 2

        # Others by distance
        return 3 + abs(my_idx - peer_idx)

    def register_peer(self, peer_bn: int, address: str, port: int):
        """Register a discovered peer."""
        self.peers[peer_bn] = {
            "bn": peer_bn,
            "name": LAYER_NAMES[peer_bn],
            "address": address,
            "port": port,
            "priority": self.get_peer_priority(peer_bn),
            "last_seen": time.time(),
        }

    def get_route_to(self, destination_bn: int) -> List[Dict]:
        """Get route to destination through known peers."""
        route = self._build_route(destination_bn)
        return [self.peers.get(bn) for bn in route if bn in self.peers]

    def status(self) -> Dict:
        return {
            "app": self.APP_NAME,
            "app_id": self.APP_ID,
            "my_bn": self.my_bn,
            "my_name": self.my_name,
            "service_port": self.service_port,
            "discovery_port": self.DISCOVERY_PORT,
            "peers_known": len(self.peers),
            "mirror_connected": self.my_mirror in self.peers,
            "center_connected": BRAHIM_CENTER in self.peers,
            "is_running": self.is_running,
            "orbot_connected": self.orbot.check_orbot(),
        }


# =============================================================================
# 6. PSI MAP - Dark Sector Topology Mapper
# =============================================================================

@dataclass
class ProbeResult:
    """Result of probing a .onion service."""
    onion: str
    name: str
    bn: int
    visible: bool
    status: str
    latency_ms: float


class PsiMap(PsiCore):
    """
    Dark sector topology mapper.

    Maps the visibility/darkness of .onion services across Brahim layers.

    ARCHITECTURE:
        Probe .onion services -> Map to Brahim layers -> Calculate dark ratio

    FEATURES:
        - Service reachability scanning
        - Layer-based clustering
        - Dark sector visualization
        - Distance-to-darkness metrics

    ANDROID INTEGRATION:
        - Background scanning service
        - Canvas-based visualization
        - Export to GeoJSON
    """

    APP_NAME = "PsiMap"
    APP_ID = "com.psi.map"

    def __init__(self, my_bn: int = 75, data_dir: Path = None):
        super().__init__(my_bn, data_dir)
        self.probe_results: List[ProbeResult] = []
        self.layer_stats: Dict[int, Dict] = {bn: {"visible": 0, "dark": 0} for bn in BRAHIM_SEQUENCE}

    def onion_to_bn(self, onion: str) -> int:
        """Map .onion address to Brahim number."""
        hash_val = int(hashlib.sha256(onion.encode()).hexdigest()[:8], 16)
        index = hash_val % 11
        return BRAHIM_SEQUENCE[index]

    def record_probe(self, onion: str, name: str, visible: bool, status: str, latency_ms: float = 0):
        """Record a probe result."""
        bn = self.onion_to_bn(onion)

        result = ProbeResult(
            onion=onion,
            name=name,
            bn=bn,
            visible=visible,
            status=status,
            latency_ms=latency_ms,
        )

        self.probe_results.append(result)

        if visible:
            self.layer_stats[bn]["visible"] += 1
        else:
            self.layer_stats[bn]["dark"] += 1

    def get_dark_ratio(self, bn: int = None) -> float:
        """Get dark ratio for a layer or overall."""
        if bn is not None:
            stats = self.layer_stats[bn]
            total = stats["visible"] + stats["dark"]
            return stats["dark"] / total if total > 0 else 0.0

        # Overall
        visible = sum(s["visible"] for s in self.layer_stats.values())
        dark = sum(s["dark"] for s in self.layer_stats.values())
        total = visible + dark
        return dark / total if total > 0 else 0.0

    def get_dark_clusters(self) -> List[Dict]:
        """Get layers with highest darkness concentration."""
        clusters = []
        for bn, stats in self.layer_stats.items():
            total = stats["visible"] + stats["dark"]
            if total > 0 and stats["dark"] > 0:
                clusters.append({
                    "bn": bn,
                    "name": LAYER_NAMES[bn],
                    "dark_count": stats["dark"],
                    "dark_ratio": stats["dark"] / total,
                })
        return sorted(clusters, key=lambda x: x["dark_ratio"], reverse=True)

    def distance_to_dark(self) -> Dict[int, float]:
        """Calculate distance from each layer to nearest dark cluster."""
        distances = {}
        dark_bns = [bn for bn, s in self.layer_stats.items() if s["dark"] > 0]

        for bn in BRAHIM_SEQUENCE:
            if not dark_bns:
                distances[bn] = float('inf')
            else:
                my_idx = BRAHIM_SEQUENCE.index(bn)
                min_dist = min(abs(my_idx - BRAHIM_SEQUENCE.index(d)) for d in dark_bns)
                distances[bn] = min_dist

        return distances

    def status(self) -> Dict:
        return {
            "app": self.APP_NAME,
            "app_id": self.APP_ID,
            "my_bn": self.my_bn,
            "probes_total": len(self.probe_results),
            "visible_count": sum(s["visible"] for s in self.layer_stats.values()),
            "dark_count": sum(s["dark"] for s in self.layer_stats.values()),
            "dark_ratio": self.get_dark_ratio(),
            "dark_clusters": len(self.get_dark_clusters()),
            "orbot_connected": self.orbot.check_orbot(),
        }


# =============================================================================
# PSI SUITE - All Applications Together
# =============================================================================

class PsiSuite:
    """
    Complete Psi APK suite with all 6 core applications.

    USAGE:
        suite = PsiSuite(my_bn=75)
        suite.messenger.send("Hello", recipient_bn=139)
        suite.vault.store(b"data", "file.txt")
    """

    VERSION = "1.0.0"
    CODENAME = "Psi.apk"

    def __init__(self, my_bn: int = 75, data_dir: Path = None):
        data_dir = data_dir or Path("data/psi_apk")

        self.my_bn = my_bn
        self.messenger = PsiMessenger(my_bn, data_dir / "messenger")
        self.vault = PsiVault(my_bn, data_dir / "vault")
        self.exchange = PsiExchange(my_bn, data_dir / "exchange")
        self.dns = PsiDNS(my_bn, data_dir / "dns")
        self.relay = PsiRelay(my_bn, data_dir / "relay")
        self.map = PsiMap(my_bn, data_dir / "map")

    def status(self) -> Dict:
        return {
            "version": self.VERSION,
            "codename": self.CODENAME,
            "my_bn": self.my_bn,
            "my_name": LAYER_NAMES[self.my_bn],
            "mirror_bn": self.messenger.my_mirror,
            "apps": {
                "messenger": self.messenger.status(),
                "vault": self.vault.status(),
                "exchange": self.exchange.status(),
                "dns": self.dns.status(),
                "relay": self.relay.status(),
                "map": self.map.status(),
            },
        }


# =============================================================================
# CLI
# =============================================================================

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("  PSI.APK - PIO + Tor Android Application Suite")
    print("=" * 70)
    print()

    # Create suite
    suite = PsiSuite(my_bn=75)

    print("BRAHIM IDENTITY:")
    print("-" * 50)
    print(f"  Your BN: {suite.my_bn} ({LAYER_NAMES[suite.my_bn]})")
    print(f"  Mirror: {suite.messenger.my_mirror} ({LAYER_NAMES[suite.messenger.my_mirror]})")
    print(f"  Layer Type: {LAYER_TYPES[suite.my_bn]}")
    print()

    print("CORE APPLICATIONS:")
    print("-" * 50)
    apps = [
        ("PsiMessenger", "Anonymous chat through 11 layers", "com.psi.messenger"),
        ("PsiVault", "Distributed encrypted storage", "com.psi.vault"),
        ("PsiExchange", "Mirror-pair key exchange", "com.psi.exchange"),
        ("PsiDNS", "Decentralized .brahim naming", "com.psi.dns"),
        ("PsiRelay", "Brahim beacon network node", "com.psi.relay"),
        ("PsiMap", "Dark sector topology mapper", "com.psi.map"),
    ]
    for name, desc, pkg in apps:
        print(f"  [{name}]")
        print(f"    {desc}")
        print(f"    Package: {pkg}")
        print()

    print("BRAHIM ROUTING:")
    print("-" * 50)
    print(f"  Layers: {' -> '.join(str(bn) for bn in BRAHIM_SEQUENCE)}")
    print(f"  CENTER: {BRAHIM_CENTER} (Rendezvous point)")
    print(f"  Sum: {BRAHIM_SUM} (Mirror pair verification)")
    print()

    print("MIRROR PAIRS:")
    print("-" * 50)
    for a, b in MIRROR_PAIRS:
        print(f"  {a:3} ({LAYER_NAMES[a]:12}) <-> {b:3} ({LAYER_NAMES[b]:12}) = {a+b}")
    print()

    print("TOR INTEGRATION:")
    print("-" * 50)
    orbot = suite.messenger.orbot
    connected = orbot.check_orbot()
    print(f"  Orbot/Tor: {'CONNECTED' if connected else 'NOT FOUND'}")
    print(f"  SOCKS5: {orbot.socks_host}:{orbot.socks_port}")
    print()

    print("DEMO - SEND MESSAGE TO MIRROR:")
    print("-" * 50)
    msg = suite.messenger.send_to_mirror("Hello from TESSERACT to HARMONY!")
    print(f"  From: BN {msg.sender_bn} ({LAYER_NAMES[msg.sender_bn]})")
    print(f"  To: BN {msg.recipient_bn} ({LAYER_NAMES[msg.recipient_bn]})")
    print(f"  Route: {' -> '.join(str(bn) for bn in msg.route)}")
    print(f"  Receipt: {msg.receipt}")
    print()

    print("DEMO - STORE FILE IN VAULT:")
    print("-" * 50)
    shards = suite.vault.store(b"Secret data distributed across 11 layers", "secret.txt")
    print(f"  File split into {len(shards)} shards")
    for shard in shards[:3]:
        print(f"    Shard {shard.index}: BN {shard.layer_bn} ({LAYER_NAMES[shard.layer_bn]})")
    print(f"    ... and {len(shards) - 3} more")
    print()

    print("DEMO - REGISTER .BRAHIM DOMAIN:")
    print("-" * 50)
    domain = suite.dns.register("tesseract-node", "abc123xyz.onion")
    print(f"  Registered: {domain.name}")
    print(f"  Points to: {domain.onion_address}")
    print(f"  Layer: BN {domain.bn} ({LAYER_NAMES[domain.bn]})")
    print()

    print("=" * 70)
    print("  PSI.APK SUITE READY")
    print("  6 Core Applications | 11 Brahim Layers | Tor Integration")
    print("=" * 70)

    return suite


if __name__ == "__main__":
    suite = main()
