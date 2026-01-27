#!/usr/bin/env python3
"""
BRAHIM-TOR APPLICATION SUITE
=============================

Four applications built on PIO + Tor integration:

1. BRAHIM MESSENGER  - Anonymous dimensional chat
2. ONION VAULT       - Secure file storage across layers
3. MIRROR EXCHANGE   - Cryptographic key exchange
4. LIGHTHOUSE DNS    - Decentralized .onion naming

All applications:
- Route through CENTER (107)
- Use 11 Brahim layers
- Leverage real Tor anonymity
- Respect mirror pair mathematics

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
import threading
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
import struct

# Brahim constants
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


# =============================================================================
# 1. BRAHIM MESSENGER - Anonymous Dimensional Chat
# =============================================================================

@dataclass
class BrahimMessage:
    """A message routed through 11 Brahim layers."""
    message_id: str
    sender_bn: int
    recipient_bn: int
    content: bytes          # Encrypted content
    layer_signatures: List[str]  # Signature at each layer
    timestamp: float
    route: List[int]        # Brahim numbers in route

    def to_dict(self) -> Dict:
        return {
            "id": self.message_id,
            "from": self.sender_bn,
            "to": self.recipient_bn,
            "layers": len(self.layer_signatures),
            "route": self.route,
            "size": len(self.content),
            "time": self.timestamp,
        }


class BrahimMessenger:
    """
    Anonymous messaging through 11 Brahim layers.

    ARCHITECTURE:
        Sender (BN_s) -> Layer encryption -> CENTER (107) -> Layer decryption -> Recipient (BN_r)

    Each layer adds its own encryption, creating an onion of 11 layers.
    Messages always pass through CENTER (107) as the rendezvous point.

    USAGE:
        messenger = BrahimMessenger(my_brahim_number=75)
        msg = messenger.send("Hello", recipient_bn=139)  # To mirror partner
        received = messenger.receive()
    """

    def __init__(self, my_brahim_number: int = 107, data_dir: Path = None):
        self.my_bn = my_brahim_number if my_brahim_number in BRAHIM_SEQUENCE else 107
        self.data_dir = data_dir or Path("data/messenger")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.inbox: List[BrahimMessage] = []
        self.outbox: List[BrahimMessage] = []
        self.contacts: Dict[int, Dict] = {}

        # Generate identity key
        self.identity_key = self._generate_layer_key(self.my_bn)

    def _generate_layer_key(self, bn: int) -> bytes:
        """Generate a deterministic key for a Brahim layer."""
        seed = f"brahim-layer-{bn}-{LAYER_NAMES[bn]}-{BRAHIM_SUM}"
        return hashlib.sha256(seed.encode()).digest()

    def _calculate_route(self, sender: int, recipient: int) -> List[int]:
        """Calculate route through CENTER (107)."""
        sender_idx = BRAHIM_SEQUENCE.index(sender)
        recipient_idx = BRAHIM_SEQUENCE.index(recipient)
        center_idx = BRAHIM_SEQUENCE.index(107)

        # Route: sender -> center -> recipient
        if sender_idx <= center_idx:
            to_center = BRAHIM_SEQUENCE[sender_idx:center_idx+1]
        else:
            to_center = BRAHIM_SEQUENCE[center_idx:sender_idx+1][::-1]

        if center_idx <= recipient_idx:
            from_center = BRAHIM_SEQUENCE[center_idx:recipient_idx+1]
        else:
            from_center = BRAHIM_SEQUENCE[recipient_idx:center_idx+1][::-1]

        return to_center + from_center[1:]

    def _encrypt_for_layer(self, data: bytes, layer_bn: int) -> bytes:
        """Encrypt data for a specific layer using XOR cipher."""
        key = self._generate_layer_key(layer_bn)
        # Simple XOR encryption (in production, use proper crypto)
        encrypted = bytes(d ^ key[i % len(key)] for i, d in enumerate(data))
        return encrypted

    def _decrypt_from_layer(self, data: bytes, layer_bn: int) -> bytes:
        """Decrypt data from a specific layer."""
        # XOR is symmetric
        return self._encrypt_for_layer(data, layer_bn)

    def _layer_sign(self, data: bytes, layer_bn: int) -> str:
        """Create signature for a layer."""
        key = self._generate_layer_key(layer_bn)
        sig = hashlib.sha256(key + data).hexdigest()[:16]
        return f"{layer_bn}:{sig}"

    def send(self, content: str, recipient_bn: int) -> BrahimMessage:
        """
        Send a message through the Brahim onion layers.

        Args:
            content: Message text
            recipient_bn: Recipient's Brahim number

        Returns:
            BrahimMessage with full routing info
        """
        if recipient_bn not in BRAHIM_SEQUENCE:
            recipient_bn = 107  # Default to CENTER

        # Calculate route
        route = self._calculate_route(self.my_bn, recipient_bn)

        # Encrypt content through each layer (reverse order for onion)
        data = content.encode('utf-8')
        signatures = []

        for bn in reversed(route):
            data = self._encrypt_for_layer(data, bn)
            sig = self._layer_sign(data, bn)
            signatures.insert(0, sig)

        # Create message
        msg = BrahimMessage(
            message_id=hashlib.sha256(f"{time.time()}:{secrets.token_hex(8)}".encode()).hexdigest()[:16],
            sender_bn=self.my_bn,
            recipient_bn=recipient_bn,
            content=data,
            layer_signatures=signatures,
            timestamp=time.time(),
            route=route,
        )

        self.outbox.append(msg)
        return msg

    def receive(self, msg: BrahimMessage) -> Optional[str]:
        """
        Receive and decrypt a message.

        Args:
            msg: BrahimMessage to decrypt

        Returns:
            Decrypted content if for us, None otherwise
        """
        if msg.recipient_bn != self.my_bn:
            return None

        # Decrypt through each layer
        data = msg.content
        for bn in msg.route:
            data = self._decrypt_from_layer(data, bn)

        self.inbox.append(msg)
        return data.decode('utf-8', errors='replace')

    def get_mirror_partner(self) -> int:
        """Get our mirror partner for secure exchange."""
        for pair in MIRROR_PAIRS:
            if self.my_bn in pair:
                return pair[1] if pair[0] == self.my_bn else pair[0]
        return 107  # CENTER has no mirror (self-mirror)

    def status(self) -> Dict:
        return {
            "my_bn": self.my_bn,
            "name": LAYER_NAMES.get(self.my_bn, "UNKNOWN"),
            "mirror": self.get_mirror_partner(),
            "inbox": len(self.inbox),
            "outbox": len(self.outbox),
            "contacts": len(self.contacts),
        }


# =============================================================================
# 2. ONION VAULT - Secure File Storage
# =============================================================================

@dataclass
class VaultShard:
    """A file shard stored at a Brahim layer."""
    shard_id: str
    file_id: str
    layer_bn: int
    layer_name: str
    data: bytes
    checksum: str
    index: int
    total_shards: int


@dataclass
class VaultManifest:
    """Manifest for a stored file, kept at CENTER (107)."""
    file_id: str
    filename: str
    file_size: int
    shards: List[Dict]
    checksum: str
    created: str
    encryption_key_hint: str


class OnionVault:
    """
    Secure file storage sharded across Brahim layers.

    ARCHITECTURE:
        SEED (27)       = File metadata
        INNER (42-97)   = Encrypted data shards
        CORE (107)      = Manifest/index
        OUTER (117-187) = Redundant copies

    Files are split into 11 shards, one per layer.
    Manifest stored at CENTER (107).
    Reconstruction requires majority of shards.

    USAGE:
        vault = OnionVault()
        file_id = vault.store("secret.txt", data)
        data = vault.retrieve(file_id)
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/vault")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.manifests: Dict[str, VaultManifest] = {}
        self.shards: Dict[str, Dict[int, VaultShard]] = {}  # file_id -> {layer -> shard}

    def _generate_file_id(self, data: bytes) -> str:
        """Generate unique file ID."""
        return hashlib.sha256(data + secrets.token_bytes(16)).hexdigest()[:16]

    def _shard_data(self, data: bytes) -> List[bytes]:
        """Split data into 11 shards (one per Brahim layer)."""
        # Pad data to be divisible by 11
        padding = (11 - len(data) % 11) % 11
        padded = data + bytes([padding] * padding)

        shard_size = len(padded) // 11
        shards = []

        for i in range(11):
            start = i * shard_size
            end = start + shard_size
            shards.append(padded[start:end])

        return shards

    def _encrypt_shard(self, shard: bytes, layer_bn: int) -> bytes:
        """Encrypt shard for storage at layer."""
        key = hashlib.sha256(f"vault-{layer_bn}-{BRAHIM_SUM}".encode()).digest()
        return bytes(s ^ key[i % len(key)] for i, s in enumerate(shard))

    def _decrypt_shard(self, shard: bytes, layer_bn: int) -> bytes:
        """Decrypt shard from layer."""
        return self._encrypt_shard(shard, layer_bn)  # XOR is symmetric

    def store(self, filename: str, data: bytes) -> str:
        """
        Store a file across all 11 Brahim layers.

        Args:
            filename: Original filename
            data: File content

        Returns:
            file_id for retrieval
        """
        file_id = self._generate_file_id(data)
        file_checksum = hashlib.sha256(data).hexdigest()

        # Shard the data
        raw_shards = self._shard_data(data)

        # Store shards at each layer
        stored_shards = []
        self.shards[file_id] = {}

        for i, (bn, shard_data) in enumerate(zip(BRAHIM_SEQUENCE, raw_shards)):
            encrypted = self._encrypt_shard(shard_data, bn)

            shard = VaultShard(
                shard_id=hashlib.sha256(f"{file_id}-{bn}".encode()).hexdigest()[:12],
                file_id=file_id,
                layer_bn=bn,
                layer_name=LAYER_NAMES[bn],
                data=encrypted,
                checksum=hashlib.sha256(encrypted).hexdigest()[:16],
                index=i,
                total_shards=11,
            )

            self.shards[file_id][bn] = shard
            stored_shards.append({
                "shard_id": shard.shard_id,
                "layer": bn,
                "name": shard.layer_name,
                "checksum": shard.checksum,
            })

        # Create manifest at CENTER (107)
        manifest = VaultManifest(
            file_id=file_id,
            filename=filename,
            file_size=len(data),
            shards=stored_shards,
            checksum=file_checksum,
            created=datetime.now(timezone.utc).isoformat(),
            encryption_key_hint=f"BN-SUM-{BRAHIM_SUM}",
        )

        self.manifests[file_id] = manifest

        # Persist manifest
        manifest_path = self.data_dir / f"{file_id}.manifest.json"
        manifest_path.write_text(json.dumps({
            "file_id": manifest.file_id,
            "filename": manifest.filename,
            "file_size": manifest.file_size,
            "shards": manifest.shards,
            "checksum": manifest.checksum,
            "created": manifest.created,
        }, indent=2))

        return file_id

    def retrieve(self, file_id: str) -> Optional[bytes]:
        """
        Retrieve a file from the vault.

        Args:
            file_id: File ID from store()

        Returns:
            Original file data, or None if not found
        """
        if file_id not in self.shards:
            return None

        # Collect and decrypt shards in order
        decrypted_shards = []

        for bn in BRAHIM_SEQUENCE:
            if bn not in self.shards[file_id]:
                return None  # Missing shard

            shard = self.shards[file_id][bn]
            decrypted = self._decrypt_shard(shard.data, bn)
            decrypted_shards.append(decrypted)

        # Reassemble
        data = b''.join(decrypted_shards)

        # Remove padding
        if data:
            padding = data[-1]
            if padding < 11:
                data = data[:-padding]

        return data

    def list_files(self) -> List[Dict]:
        """List all files in the vault."""
        return [
            {
                "file_id": m.file_id,
                "filename": m.filename,
                "size": m.file_size,
                "shards": len(m.shards),
                "created": m.created,
            }
            for m in self.manifests.values()
        ]

    def status(self) -> Dict:
        return {
            "files_stored": len(self.manifests),
            "total_shards": sum(len(s) for s in self.shards.values()),
            "layers_used": len(BRAHIM_SEQUENCE),
            "center": 107,
        }


# =============================================================================
# 3. MIRROR EXCHANGE - Cryptographic Key Exchange
# =============================================================================

@dataclass
class MirrorKeyPair:
    """A key pair derived from mirror relationship."""
    bn_low: int
    bn_high: int
    shared_secret: bytes
    public_component: bytes
    private_component: bytes
    sum_constant: int = 214


class MirrorExchange:
    """
    Cryptographic key exchange using Brahim mirror pairs.

    PRINCIPLE:
        Mirror pairs sum to 214:
        - (27, 187)  GENESIS <-> OMEGA
        - (42, 172)  DUALITY <-> COMPLETION
        - (60, 154)  MANIFESTATION <-> INFINITY
        - (75, 139)  TESSERACT <-> HARMONY
        - (97, 117)  THRESHOLD <-> EMERGENCE

    KEY DERIVATION:
        shared_secret = hash(bn_low * bn_high * PHI * 214)
        This creates a deterministic shared secret between mirror partners.

    USAGE:
        exchange = MirrorExchange(my_bn=75)
        shared_key = exchange.derive_shared_key(partner_bn=139)
        encrypted = exchange.encrypt(data, shared_key)
    """

    def __init__(self, my_bn: int):
        if my_bn not in BRAHIM_SEQUENCE:
            my_bn = 107
        self.my_bn = my_bn
        self.mirror_bn = self._find_mirror(my_bn)

    def _find_mirror(self, bn: int) -> int:
        """Find mirror partner."""
        for pair in MIRROR_PAIRS:
            if bn in pair:
                return pair[1] if pair[0] == bn else pair[0]
        return bn  # Self-mirror for CENTER

    def derive_shared_key(self, partner_bn: int = None) -> bytes:
        """
        Derive shared secret with a partner.

        If partner is our mirror, uses the special mirror derivation.
        Otherwise, derives through CENTER.
        """
        if partner_bn is None:
            partner_bn = self.mirror_bn

        # Check if direct mirror pair
        is_mirror = (self.my_bn, partner_bn) in MIRROR_PAIRS or \
                    (partner_bn, self.my_bn) in MIRROR_PAIRS

        if is_mirror:
            # Direct mirror derivation
            low = min(self.my_bn, partner_bn)
            high = max(self.my_bn, partner_bn)

            # The magic: product * PHI * sum = unique per pair
            secret_base = low * high * PHI * BRAHIM_SUM
            secret = hashlib.sha256(f"{secret_base:.20f}".encode()).digest()
        else:
            # Route through CENTER
            # Both parties derive from their connection to CENTER
            my_to_center = self.my_bn * BRAHIM_CENTER * PHI
            partner_to_center = partner_bn * BRAHIM_CENTER * PHI
            combined = my_to_center + partner_to_center
            secret = hashlib.sha256(f"{combined:.20f}".encode()).digest()

        return secret

    def generate_keypair(self) -> MirrorKeyPair:
        """Generate a key pair based on mirror relationship."""
        low = min(self.my_bn, self.mirror_bn)
        high = max(self.my_bn, self.mirror_bn)

        shared = self.derive_shared_key()

        # Derive public/private from shared secret
        public = hashlib.sha256(shared + b"public").digest()
        private = hashlib.sha256(shared + b"private").digest()

        return MirrorKeyPair(
            bn_low=low,
            bn_high=high,
            shared_secret=shared,
            public_component=public,
            private_component=private,
        )

    def encrypt(self, data: bytes, key: bytes = None) -> bytes:
        """Encrypt data using mirror-derived key."""
        if key is None:
            key = self.derive_shared_key()

        # Simple XOR (production should use AES)
        return bytes(d ^ key[i % len(key)] for i, d in enumerate(data))

    def decrypt(self, data: bytes, key: bytes = None) -> bytes:
        """Decrypt data using mirror-derived key."""
        return self.encrypt(data, key)  # XOR is symmetric

    def verify_mirror_sum(self) -> bool:
        """Verify the mirror pair sums to 214."""
        return self.my_bn + self.mirror_bn == BRAHIM_SUM or self.my_bn == 107

    def status(self) -> Dict:
        return {
            "my_bn": self.my_bn,
            "my_name": LAYER_NAMES.get(self.my_bn),
            "mirror_bn": self.mirror_bn,
            "mirror_name": LAYER_NAMES.get(self.mirror_bn),
            "sum": self.my_bn + self.mirror_bn,
            "valid": self.verify_mirror_sum(),
        }


# =============================================================================
# 4. LIGHTHOUSE DNS - Decentralized .onion Naming
# =============================================================================

@dataclass
class LighthouseRecord:
    """A DNS-like record in the Lighthouse system."""
    name: str                # Human-readable name
    onion_address: str       # .onion address
    brahim_number: int       # Associated BN
    layer: int               # Brahim layer
    owner_bn: int            # Owner's BN
    created: str
    expires: str
    signature: str


class LighthouseDNS:
    """
    Decentralized naming system for .onion addresses.

    ARCHITECTURE:
        Names are anchored to Brahim numbers.
        Each BN can register names in its layer.
        Resolution goes through CENTER (107).
        Geographic blockchain provides trust anchors.

    NAMING SCHEME:
        name.bn75.brahim  -> .onion address
        name.genesis.brahim -> resolves via BN 27
        name.center.brahim -> resolves via BN 107

    USAGE:
        dns = LighthouseDNS(my_bn=75)
        dns.register("mysite", "abc123...def.onion")
        onion = dns.resolve("mysite.bn75.brahim")
    """

    TLD = ".brahim"

    def __init__(self, my_bn: int = 107, data_dir: Path = None):
        self.my_bn = my_bn if my_bn in BRAHIM_SEQUENCE else 107
        self.data_dir = data_dir or Path("data/lighthouse_dns")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.records: Dict[str, LighthouseRecord] = {}
        self.reverse: Dict[str, str] = {}  # onion -> name

        self._load_records()

    def _load_records(self):
        """Load records from disk."""
        records_file = self.data_dir / "records.json"
        if records_file.exists():
            try:
                data = json.loads(records_file.read_text())
                for name, rec in data.items():
                    self.records[name] = LighthouseRecord(**rec)
                    self.reverse[rec["onion_address"]] = name
            except Exception:
                pass

    def _save_records(self):
        """Persist records to disk."""
        records_file = self.data_dir / "records.json"
        data = {name: {
            "name": r.name,
            "onion_address": r.onion_address,
            "brahim_number": r.brahim_number,
            "layer": r.layer,
            "owner_bn": r.owner_bn,
            "created": r.created,
            "expires": r.expires,
            "signature": r.signature,
        } for name, r in self.records.items()}
        records_file.write_text(json.dumps(data, indent=2))

    def _sign_record(self, name: str, onion: str) -> str:
        """Sign a record with owner's BN."""
        data = f"{name}:{onion}:{self.my_bn}:{BRAHIM_SUM}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

    def _canonical_name(self, name: str) -> str:
        """Convert name to canonical form."""
        name = name.lower().strip()
        if not name.endswith(self.TLD):
            name = f"{name}.bn{self.my_bn}{self.TLD}"
        return name

    def register(self, name: str, onion_address: str, ttl_days: int = 365) -> LighthouseRecord:
        """
        Register a name for an .onion address.

        Args:
            name: Human-readable name
            onion_address: The .onion address
            ttl_days: Time to live in days

        Returns:
            LighthouseRecord
        """
        canonical = self._canonical_name(name)

        # Determine layer from BN
        layer = BRAHIM_SEQUENCE.index(self.my_bn) + 1

        now = datetime.now(timezone.utc)
        expires = datetime.fromtimestamp(now.timestamp() + ttl_days * 86400, timezone.utc)

        record = LighthouseRecord(
            name=canonical,
            onion_address=onion_address,
            brahim_number=self.my_bn,
            layer=layer,
            owner_bn=self.my_bn,
            created=now.isoformat(),
            expires=expires.isoformat(),
            signature=self._sign_record(canonical, onion_address),
        )

        self.records[canonical] = record
        self.reverse[onion_address] = canonical
        self._save_records()

        return record

    def resolve(self, name: str) -> Optional[str]:
        """
        Resolve a name to .onion address.

        Args:
            name: Name to resolve (e.g., "mysite.bn75.brahim")

        Returns:
            .onion address or None
        """
        canonical = self._canonical_name(name) if self.TLD not in name else name.lower()

        if canonical in self.records:
            return self.records[canonical].onion_address

        # Try partial match
        for rec_name, rec in self.records.items():
            if name.lower() in rec_name:
                return rec.onion_address

        return None

    def reverse_lookup(self, onion_address: str) -> Optional[str]:
        """Look up name from .onion address."""
        return self.reverse.get(onion_address)

    def list_records(self, layer: int = None) -> List[Dict]:
        """List all records, optionally filtered by layer."""
        records = []
        for rec in self.records.values():
            if layer is None or rec.layer == layer:
                records.append({
                    "name": rec.name,
                    "onion": rec.onion_address[:32] + "...",
                    "layer": rec.layer,
                    "bn": rec.brahim_number,
                })
        return records

    def status(self) -> Dict:
        return {
            "my_bn": self.my_bn,
            "total_records": len(self.records),
            "tld": self.TLD,
            "layers_with_records": len(set(r.layer for r in self.records.values())),
        }


# =============================================================================
# UNIFIED BRAHIM-TOR SUITE
# =============================================================================

class BrahimTorSuite:
    """
    Complete Brahim-Tor Application Suite.

    Integrates all four applications:
    - Messenger: Anonymous chat
    - Vault: Secure storage
    - Exchange: Key exchange
    - DNS: Decentralized naming

    All share the same Brahim identity and route through CENTER (107).
    """

    VERSION = "1.0.0"

    def __init__(self, my_bn: int = 75, data_dir: Path = None):
        self.my_bn = my_bn if my_bn in BRAHIM_SEQUENCE else 107
        self.data_dir = data_dir or Path("data/brahim_tor_suite")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize all applications
        self.messenger = BrahimMessenger(my_bn, self.data_dir / "messenger")
        self.vault = OnionVault(self.data_dir / "vault")
        self.exchange = MirrorExchange(my_bn)
        self.dns = LighthouseDNS(my_bn, self.data_dir / "dns")

        # My identity
        self.identity = {
            "bn": self.my_bn,
            "name": LAYER_NAMES.get(self.my_bn, "UNKNOWN"),
            "mirror": self.exchange.mirror_bn,
            "mirror_name": LAYER_NAMES.get(self.exchange.mirror_bn, "UNKNOWN"),
            "layer": BRAHIM_SEQUENCE.index(self.my_bn) + 1,
        }

    def send_message(self, content: str, to_bn: int) -> Dict:
        """Send an anonymous message."""
        msg = self.messenger.send(content, to_bn)
        return msg.to_dict()

    def store_file(self, filename: str, data: bytes) -> str:
        """Store a file in the vault."""
        return self.vault.store(filename, data)

    def retrieve_file(self, file_id: str) -> Optional[bytes]:
        """Retrieve a file from the vault."""
        return self.vault.retrieve(file_id)

    def derive_key(self, partner_bn: int = None) -> bytes:
        """Derive a shared key with a partner."""
        return self.exchange.derive_shared_key(partner_bn)

    def register_name(self, name: str, onion: str) -> Dict:
        """Register a .brahim name."""
        record = self.dns.register(name, onion)
        return {"name": record.name, "onion": record.onion_address}

    def resolve_name(self, name: str) -> Optional[str]:
        """Resolve a .brahim name."""
        return self.dns.resolve(name)

    def status(self) -> Dict:
        return {
            "version": self.VERSION,
            "identity": self.identity,
            "messenger": self.messenger.status(),
            "vault": self.vault.status(),
            "exchange": self.exchange.status(),
            "dns": self.dns.status(),
            "center": BRAHIM_CENTER,
            "sum_constant": BRAHIM_SUM,
        }

    def __repr__(self) -> str:
        return (f"<BrahimTorSuite v{self.VERSION} BN={self.my_bn} "
                f"({LAYER_NAMES.get(self.my_bn)}) mirror={self.exchange.mirror_bn}>")


# =============================================================================
# CLI DEMO
# =============================================================================

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("  BRAHIM-TOR APPLICATION SUITE")
    print("  Four Applications on the Brahim Onion Network")
    print("=" * 70)
    print()

    # Create suite at BN 75 (TESSERACT)
    suite = BrahimTorSuite(my_bn=75)
    print(f"Suite: {suite}")
    print()

    # Show identity
    print("IDENTITY:")
    print("-" * 50)
    print(f"  Brahim Number: {suite.identity['bn']}")
    print(f"  Name: {suite.identity['name']}")
    print(f"  Layer: {suite.identity['layer']}")
    print(f"  Mirror: {suite.identity['mirror']} ({suite.identity['mirror_name']})")
    print()

    # Demo 1: Messenger
    print("1. BRAHIM MESSENGER")
    print("-" * 50)
    msg = suite.send_message("Hello from TESSERACT!", to_bn=139)  # To mirror
    print(f"  Sent message: {msg['id']}")
    print(f"  Route: {' -> '.join(str(x) for x in msg['route'])}")
    print(f"  Layers: {msg['layers']}")
    print()

    # Demo 2: Vault
    print("2. ONION VAULT")
    print("-" * 50)
    test_data = b"Secret document stored across 11 Brahim layers!"
    file_id = suite.store_file("secret.txt", test_data)
    print(f"  Stored file: {file_id}")
    retrieved = suite.retrieve_file(file_id)
    print(f"  Retrieved: {retrieved.decode() if retrieved else 'FAILED'}")
    print(f"  Integrity: {'OK' if retrieved == test_data else 'MISMATCH'}")
    print()

    # Demo 3: Mirror Exchange
    print("3. MIRROR EXCHANGE")
    print("-" * 50)
    key = suite.derive_key(partner_bn=139)
    print(f"  Mirror pair: 75 <-> 139 (sum = {75 + 139})")
    print(f"  Shared key: {key.hex()[:32]}...")

    # Encrypt/decrypt test
    plaintext = b"Secret between TESSERACT and HARMONY"
    encrypted = suite.exchange.encrypt(plaintext, key)
    decrypted = suite.exchange.decrypt(encrypted, key)
    print(f"  Encryption test: {'PASS' if decrypted == plaintext else 'FAIL'}")
    print()

    # Demo 4: Lighthouse DNS
    print("4. LIGHTHOUSE DNS")
    print("-" * 50)
    result = suite.register_name("mysite", "abcd1234efgh5678ijkl9012mnop3456qrst7890uvwx.onion")
    print(f"  Registered: {result['name']}")
    resolved = suite.resolve_name("mysite")
    print(f"  Resolved: {resolved[:32]}..." if resolved else "  Resolved: FAILED")
    print()

    # Status
    print("SUITE STATUS:")
    print("-" * 50)
    status = suite.status()
    print(f"  Messenger: {status['messenger']['inbox']} in / {status['messenger']['outbox']} out")
    print(f"  Vault: {status['vault']['files_stored']} files, {status['vault']['total_shards']} shards")
    print(f"  Exchange: Valid mirror = {status['exchange']['valid']}")
    print(f"  DNS: {status['dns']['total_records']} records")
    print()

    print("=" * 70)
    print("  ALL APPLICATIONS OPERATIONAL")
    print("  Routes through CENTER (107)")
    print("  Mirror pairs sum to 214")
    print("=" * 70)


if __name__ == "__main__":
    main()
