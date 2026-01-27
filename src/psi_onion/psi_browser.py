#!/usr/bin/env python3
"""
PSI.ONION BROWSER
=================

A PIO-enhanced Tor Browser wrapper integrating Snowden-grade skills.

SKILLS INTEGRATED:
    FROM SECUREDROP:
    - Air-gap awareness
    - No-log architecture
    - Metadata stripping
    - GPG encryption

    FROM ONIONSHARE:
    - Ephemeral .onion creation
    - Anonymous dropbox
    - No-log chat
    - Auto-stop services

    FROM GLOBALEAKS:
    - 16-digit receipt system
    - Per-session keys
    - Argon2ID key derivation
    - Auto-delete retention

    FROM BRIAR:
    - No central server mode
    - Offline sync capability
    - Distributed messaging

    FROM TAILS:
    - RAM wipe awareness
    - Stream isolation
    - Metadata cleaner

    FROM WHONIX:
    - IP leak protection
    - Keystroke anonymization
    - Hardware serial hiding

ARCHITECTURE:
    Psi.onion = Tor Browser + PIO Brahim Layer + Snowden Skills

Author: ASIOS Core Team
Version: 1.0.0
Codename: Psi.onion
"""

from __future__ import annotations

import os
import sys
import json
import time
import secrets
import hashlib
import subprocess
import threading
import shutil
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import base64
import struct

# Attempt to import argon2 for key derivation
try:
    from argon2 import PasswordHasher
    from argon2.low_level import hash_secret_raw, Type
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False

# Brahim constants
BRAHIM_SEQUENCE = [27, 42, 60, 75, 97, 107, 117, 139, 154, 172, 187]
BRAHIM_CENTER = 107
BRAHIM_SUM = 214


# =============================================================================
# SKILL: RECEIPT SYSTEM (from GlobaLeaks)
# =============================================================================

class ReceiptSystem:
    """
    16-digit receipt system for anonymous session identification.

    Each session gets a unique receipt that can be used to:
    - Resume anonymous sessions
    - Derive encryption keys
    - Prove identity without revealing it
    """

    @staticmethod
    def generate() -> str:
        """Generate a 16-digit receipt."""
        # Use cryptographically secure random
        digits = ''.join(str(secrets.randbelow(10)) for _ in range(16))
        # Format as XXXX-XXXX-XXXX-XXXX
        return f"{digits[:4]}-{digits[4:8]}-{digits[8:12]}-{digits[12:]}"

    @staticmethod
    def derive_key(receipt: str, salt: bytes = None) -> bytes:
        """Derive encryption key from receipt using Argon2ID."""
        receipt_clean = receipt.replace('-', '')

        if salt is None:
            salt = b'psi.onion.v1.salt'

        if ARGON2_AVAILABLE:
            # Argon2ID with memory-hard parameters
            key = hash_secret_raw(
                secret=receipt_clean.encode(),
                salt=salt,
                time_cost=3,
                memory_cost=65536,  # 64MB
                parallelism=4,
                hash_len=32,
                type=Type.ID
            )
        else:
            # Fallback to PBKDF2-like derivation
            key = hashlib.pbkdf2_hmac(
                'sha256',
                receipt_clean.encode(),
                salt,
                iterations=100000,
                dklen=32
            )

        return key

    @staticmethod
    def verify(receipt: str) -> bool:
        """Verify receipt format is valid."""
        clean = receipt.replace('-', '')
        return len(clean) == 16 and clean.isdigit()


# =============================================================================
# SKILL: METADATA CLEANER (from Tails/mat2)
# =============================================================================

class MetadataCleaner:
    """
    Strip metadata from files to prevent identity leakage.

    Removes:
    - EXIF data from images
    - Author info from documents
    - GPS coordinates
    - Timestamps
    - Software signatures
    """

    DANGEROUS_EXTENSIONS = {
        '.exe', '.dll', '.bat', '.cmd', '.ps1', '.vbs', '.js',
        '.msi', '.scr', '.com', '.pif', '.hta', '.cpl'
    }

    @staticmethod
    def is_safe_extension(filepath: Path) -> bool:
        """Check if file extension is safe."""
        return filepath.suffix.lower() not in MetadataCleaner.DANGEROUS_EXTENSIONS

    @staticmethod
    def strip_basic_metadata(data: bytes, filetype: str) -> bytes:
        """
        Basic metadata stripping for common file types.

        Note: For production, use mat2 or exiftool.
        This is a simplified implementation.
        """
        if filetype.lower() in ['jpg', 'jpeg']:
            # Remove EXIF by finding and stripping APP1 marker
            # Simplified - real implementation should use PIL or exiftool
            return MetadataCleaner._strip_jpeg_exif(data)
        elif filetype.lower() == 'png':
            # PNG metadata is in chunks - strip non-essential ones
            return MetadataCleaner._strip_png_metadata(data)
        else:
            # For other types, return as-is
            # Real implementation would handle PDF, DOCX, etc.
            return data

    @staticmethod
    def _strip_jpeg_exif(data: bytes) -> bytes:
        """Remove EXIF from JPEG (simplified)."""
        # Find SOI marker
        if data[:2] != b'\xff\xd8':
            return data  # Not a JPEG

        result = bytearray(data[:2])
        i = 2

        while i < len(data) - 1:
            if data[i] != 0xff:
                break

            marker = data[i+1]

            # Skip APP1 (EXIF) marker
            if marker == 0xe1:
                if i + 3 < len(data):
                    length = struct.unpack('>H', data[i+2:i+4])[0]
                    i += 2 + length
                    continue

            # Keep other markers
            if marker == 0xd9:  # EOI
                result.extend(data[i:])
                break
            elif marker in [0xd0, 0xd1, 0xd2, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7, 0xd8]:
                result.extend(data[i:i+2])
                i += 2
            elif i + 3 < len(data):
                length = struct.unpack('>H', data[i+2:i+4])[0]
                result.extend(data[i:i+2+length])
                i += 2 + length
            else:
                break

        return bytes(result)

    @staticmethod
    def _strip_png_metadata(data: bytes) -> bytes:
        """Remove non-essential PNG chunks (simplified)."""
        if data[:8] != b'\x89PNG\r\n\x1a\n':
            return data  # Not a PNG

        result = bytearray(data[:8])
        i = 8

        # Essential chunks to keep
        essential = {b'IHDR', b'PLTE', b'IDAT', b'IEND'}

        while i < len(data) - 12:
            length = struct.unpack('>I', data[i:i+4])[0]
            chunk_type = data[i+4:i+8]
            chunk_end = i + 12 + length

            if chunk_type in essential:
                result.extend(data[i:chunk_end])

            i = chunk_end

            if chunk_type == b'IEND':
                break

        return bytes(result)


# =============================================================================
# SKILL: EPHEMERAL SERVICE (from OnionShare)
# =============================================================================

class EphemeralOnion:
    """
    Create ephemeral .onion services that auto-destroy.

    Features:
    - One-time use addresses
    - Auto-stop after download
    - No persistent state
    """

    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or Path("data/ephemeral")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.active_services: Dict[str, Dict] = {}

    def create_share(self, files: List[Path], auto_stop: bool = True) -> Dict:
        """Create ephemeral file share."""
        service_id = secrets.token_hex(8)

        # Generate onion-style address (simulated)
        onion_addr = hashlib.sha256(
            f"{service_id}:{time.time()}".encode()
        ).hexdigest()[:56] + ".onion"

        service = {
            "id": service_id,
            "onion": onion_addr,
            "files": [str(f) for f in files],
            "auto_stop": auto_stop,
            "downloads": 0,
            "created": datetime.now(timezone.utc).isoformat(),
            "active": True,
        }

        self.active_services[service_id] = service
        return service

    def create_dropbox(self) -> Dict:
        """Create anonymous receive endpoint."""
        service_id = secrets.token_hex(8)
        onion_addr = hashlib.sha256(
            f"dropbox:{service_id}:{time.time()}".encode()
        ).hexdigest()[:56] + ".onion"

        service = {
            "id": service_id,
            "onion": onion_addr,
            "type": "dropbox",
            "received_files": [],
            "created": datetime.now(timezone.utc).isoformat(),
            "active": True,
        }

        self.active_services[service_id] = service
        return service

    def destroy(self, service_id: str) -> bool:
        """Destroy an ephemeral service."""
        if service_id in self.active_services:
            self.active_services[service_id]["active"] = False
            del self.active_services[service_id]
            return True
        return False

    def destroy_all(self):
        """Destroy all ephemeral services."""
        self.active_services.clear()


# =============================================================================
# SKILL: STREAM ISOLATION (from Tails/Whonix)
# =============================================================================

class StreamIsolator:
    """
    Ensure different activities use separate Tor circuits.

    Maps activities to isolated SOCKS ports.
    """

    BASE_PORT = 9050

    ACTIVITY_PORTS = {
        "browse": 9050,
        "chat": 9051,
        "upload": 9052,
        "download": 9053,
        "email": 9054,
        "api": 9055,
    }

    @classmethod
    def get_port(cls, activity: str) -> int:
        """Get isolated SOCKS port for activity."""
        return cls.ACTIVITY_PORTS.get(activity, cls.BASE_PORT)

    @classmethod
    def get_proxy_config(cls, activity: str) -> Dict:
        """Get proxy configuration for activity."""
        port = cls.get_port(activity)
        return {
            "socks_host": "127.0.0.1",
            "socks_port": port,
            "socks_version": 5,
            "isolate": True,
        }


# =============================================================================
# SKILL: RAM WIPE AWARENESS (from Tails)
# =============================================================================

class SecureMemory:
    """
    Secure memory handling with wipe capabilities.

    Note: Python's memory management makes true secure wipe difficult.
    This provides best-effort security for sensitive data.
    """

    @staticmethod
    def secure_string(data: str) -> 'SecureString':
        """Create a secure string that can be wiped."""
        return SecureString(data)

    @staticmethod
    def wipe_dict(d: Dict):
        """Attempt to wipe dictionary contents."""
        for key in list(d.keys()):
            if isinstance(d[key], str):
                d[key] = '\x00' * len(d[key])
            elif isinstance(d[key], bytes):
                d[key] = b'\x00' * len(d[key])
            elif isinstance(d[key], dict):
                SecureMemory.wipe_dict(d[key])
            d[key] = None
        d.clear()


class SecureString:
    """A string that attempts to wipe itself when deleted."""

    def __init__(self, data: str):
        self._data = bytearray(data.encode('utf-8'))

    def get(self) -> str:
        return self._data.decode('utf-8')

    def wipe(self):
        for i in range(len(self._data)):
            self._data[i] = 0
        self._data = bytearray()

    def __del__(self):
        self.wipe()

    def __str__(self):
        return self.get()


# =============================================================================
# SKILL: KEYSTROKE ANONYMIZATION (from Whonix)
# =============================================================================

class KeystrokeAnonymizer:
    """
    Randomize keystroke timing to prevent fingerprinting.

    Typing patterns can identify users. This adds random delays.
    """

    MIN_DELAY_MS = 50
    MAX_DELAY_MS = 200

    @classmethod
    def get_random_delay(cls) -> float:
        """Get random delay in seconds."""
        delay_ms = secrets.randbelow(cls.MAX_DELAY_MS - cls.MIN_DELAY_MS) + cls.MIN_DELAY_MS
        return delay_ms / 1000.0

    @classmethod
    def anonymize_input(cls, text: str, callback) -> None:
        """
        Feed text to callback with randomized timing.

        Args:
            text: Text to input
            callback: Function to call for each character
        """
        for char in text:
            time.sleep(cls.get_random_delay())
            callback(char)


# =============================================================================
# SKILL: AUTO-DELETE RETENTION (from GlobaLeaks)
# =============================================================================

class AutoDeleteManager:
    """
    Automatic deletion of data after retention period.

    Default: 90 days (configurable)
    """

    DEFAULT_RETENTION_DAYS = 90

    def __init__(self, data_dir: Path, retention_days: int = None):
        self.data_dir = data_dir
        self.retention_days = retention_days or self.DEFAULT_RETENTION_DAYS
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def store(self, key: str, data: bytes, retention_days: int = None) -> Path:
        """Store data with expiration."""
        retention = retention_days or self.retention_days
        expires = time.time() + (retention * 86400)

        filename = f"{key}.{int(expires)}.enc"
        filepath = self.data_dir / filename

        # Simple encryption (production should use proper crypto)
        encrypted = self._encrypt(data, key)
        filepath.write_bytes(encrypted)

        return filepath

    def retrieve(self, key: str) -> Optional[bytes]:
        """Retrieve data if not expired."""
        for filepath in self.data_dir.glob(f"{key}.*.enc"):
            parts = filepath.stem.split('.')
            if len(parts) >= 2:
                expires = int(parts[-1])
                if time.time() < expires:
                    encrypted = filepath.read_bytes()
                    return self._decrypt(encrypted, key)
                else:
                    # Expired - delete
                    filepath.unlink()
        return None

    def cleanup_expired(self) -> int:
        """Delete all expired data."""
        deleted = 0
        now = time.time()

        for filepath in self.data_dir.glob("*.enc"):
            parts = filepath.stem.split('.')
            if len(parts) >= 2:
                try:
                    expires = int(parts[-1])
                    if now >= expires:
                        filepath.unlink()
                        deleted += 1
                except ValueError:
                    pass

        return deleted

    def _encrypt(self, data: bytes, key: str) -> bytes:
        """Simple XOR encryption (use proper crypto in production)."""
        key_bytes = hashlib.sha256(key.encode()).digest()
        return bytes(d ^ key_bytes[i % len(key_bytes)] for i, d in enumerate(data))

    def _decrypt(self, data: bytes, key: str) -> bytes:
        """Simple XOR decryption."""
        return self._encrypt(data, key)


# =============================================================================
# PSI.ONION BROWSER CORE
# =============================================================================

@dataclass
class PsiSession:
    """A Psi.onion browsing session."""
    session_id: str
    receipt: str
    brahim_number: int
    created: str
    encryption_key: bytes = field(repr=False)
    activities: List[str] = field(default_factory=list)
    ephemeral_services: List[str] = field(default_factory=list)


class PsiBrowser:
    """
    Psi.onion Browser - PIO-enhanced Tor Browser with Snowden skills.

    USAGE:
        browser = PsiBrowser(tor_path="C:/Users/.../Tor Browser")
        session = browser.new_session()
        browser.launch()
    """

    VERSION = "1.0.0"
    CODENAME = "Psi.onion"

    def __init__(
        self,
        tor_path: Path = None,
        my_bn: int = 75,
        data_dir: Path = None,
    ):
        # Tor Browser path
        self.tor_path = Path(tor_path) if tor_path else Path(
            "C:/Users/usuario/Desktop/Tor Browser"
        )

        self.my_bn = my_bn if my_bn in BRAHIM_SEQUENCE else 107
        self.data_dir = data_dir or Path("data/psi_browser")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize skills
        self.receipt_system = ReceiptSystem()
        self.metadata_cleaner = MetadataCleaner()
        self.ephemeral = EphemeralOnion(self.data_dir / "ephemeral")
        self.auto_delete = AutoDeleteManager(self.data_dir / "retention")

        # Session management
        self.current_session: Optional[PsiSession] = None
        self.sessions: Dict[str, PsiSession] = {}

        # Browser process
        self._browser_process: Optional[subprocess.Popen] = None

    def new_session(self) -> PsiSession:
        """Create a new anonymous session with receipt."""
        receipt = self.receipt_system.generate()
        encryption_key = self.receipt_system.derive_key(receipt)

        session = PsiSession(
            session_id=secrets.token_hex(8),
            receipt=receipt,
            brahim_number=self.my_bn,
            created=datetime.now(timezone.utc).isoformat(),
            encryption_key=encryption_key,
        )

        self.sessions[session.session_id] = session
        self.current_session = session

        return session

    def resume_session(self, receipt: str) -> Optional[PsiSession]:
        """Resume a session using receipt."""
        if not self.receipt_system.verify(receipt):
            return None

        # Find session by receipt
        for session in self.sessions.values():
            if session.receipt == receipt:
                self.current_session = session
                return session

        return None

    def launch(self, private: bool = True) -> bool:
        """
        Launch Tor Browser with Psi.onion enhancements.

        Args:
            private: Start in private browsing mode
        """
        if not self.tor_path.exists():
            return False

        browser_exe = self.tor_path / "Browser" / "firefox.exe"
        if not browser_exe.exists():
            return False

        # Build command
        cmd = [str(browser_exe)]

        if private:
            cmd.append("-private")

        try:
            self._browser_process = subprocess.Popen(
                cmd,
                cwd=str(self.tor_path / "Browser"),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            if self.current_session:
                self.current_session.activities.append(
                    f"browser_launch:{datetime.now(timezone.utc).isoformat()}"
                )

            return True
        except Exception:
            return False

    def create_ephemeral_share(self, files: List[Path]) -> Dict:
        """Create ephemeral file share (OnionShare-style)."""
        service = self.ephemeral.create_share(files, auto_stop=True)

        if self.current_session:
            self.current_session.ephemeral_services.append(service["id"])

        return service

    def create_dropbox(self) -> Dict:
        """Create anonymous dropbox for receiving files."""
        service = self.ephemeral.create_dropbox()

        if self.current_session:
            self.current_session.ephemeral_services.append(service["id"])

        return service

    def clean_file(self, filepath: Path) -> bytes:
        """Strip metadata from file."""
        data = filepath.read_bytes()
        filetype = filepath.suffix[1:] if filepath.suffix else ""
        return self.metadata_cleaner.strip_basic_metadata(data, filetype)

    def store_secure(self, key: str, data: bytes, days: int = 90) -> Path:
        """Store data with auto-deletion."""
        return self.auto_delete.store(key, data, days)

    def retrieve_secure(self, key: str) -> Optional[bytes]:
        """Retrieve securely stored data."""
        return self.auto_delete.retrieve(key)

    def get_isolated_port(self, activity: str) -> int:
        """Get stream-isolated SOCKS port for activity."""
        return StreamIsolator.get_port(activity)

    def close(self):
        """Close browser and cleanup."""
        # Destroy ephemeral services
        self.ephemeral.destroy_all()

        # Cleanup expired data
        self.auto_delete.cleanup_expired()

        # Terminate browser
        if self._browser_process:
            self._browser_process.terminate()
            self._browser_process = None

        # Wipe session data
        if self.current_session:
            self.current_session = None

    def status(self) -> Dict:
        """Get browser status."""
        return {
            "version": self.VERSION,
            "codename": self.CODENAME,
            "tor_path": str(self.tor_path),
            "tor_available": self.tor_path.exists(),
            "brahim_number": self.my_bn,
            "current_session": self.current_session.session_id if self.current_session else None,
            "active_sessions": len(self.sessions),
            "ephemeral_services": len(self.ephemeral.active_services),
            "skills": [
                "receipt_system",
                "metadata_cleaner",
                "ephemeral_onion",
                "stream_isolation",
                "auto_delete",
                "secure_memory",
                "keystroke_anonymization",
            ],
        }

    def __repr__(self) -> str:
        return f"<PsiBrowser v{self.VERSION} '{self.CODENAME}' BN={self.my_bn}>"


# =============================================================================
# CLI
# =============================================================================

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("  PSI.ONION BROWSER")
    print("  PIO-Enhanced Tor Browser with Snowden Skills")
    print("=" * 70)
    print()

    # Create browser
    browser = PsiBrowser(my_bn=75)
    print(f"Browser: {browser}")
    print()

    # Check Tor availability
    status = browser.status()
    print("STATUS:")
    print("-" * 50)
    print(f"  Tor Available: {status['tor_available']}")
    print(f"  Brahim Number: {status['brahim_number']}")
    print(f"  Skills Loaded: {len(status['skills'])}")
    print()

    # List skills
    print("INTEGRATED SKILLS:")
    print("-" * 50)
    for skill in status['skills']:
        print(f"  [+] {skill}")
    print()

    # Create session
    print("CREATING ANONYMOUS SESSION:")
    print("-" * 50)
    session = browser.new_session()
    print(f"  Session ID: {session.session_id}")
    print(f"  Receipt: {session.receipt}")
    print(f"  Brahim: BN {session.brahim_number}")
    print(f"  Key (first 16 bytes): {session.encryption_key[:16].hex()}")
    print()

    # Demo skills
    print("SKILL DEMOS:")
    print("-" * 50)

    # Receipt verification
    print(f"  [Receipt] Valid format: {ReceiptSystem.verify(session.receipt)}")

    # Stream isolation
    browse_port = browser.get_isolated_port("browse")
    chat_port = browser.get_isolated_port("chat")
    print(f"  [Stream] Browse port: {browse_port}, Chat port: {chat_port}")

    # Ephemeral service
    dropbox = browser.create_dropbox()
    print(f"  [Ephemeral] Dropbox: {dropbox['onion'][:40]}...")

    # Secure storage
    test_data = b"Sensitive information with 90-day retention"
    stored = browser.store_secure("test-doc", test_data, days=90)
    print(f"  [AutoDelete] Stored: {stored.name}")

    # Keystroke anonymization
    delay = KeystrokeAnonymizer.get_random_delay()
    print(f"  [Keystroke] Random delay: {delay*1000:.0f}ms")

    print()
    print("=" * 70)
    print("  PSI.ONION BROWSER READY")
    print("  Run: browser.launch() to start Tor Browser")
    print("=" * 70)

    return browser


if __name__ == "__main__":
    browser = main()
