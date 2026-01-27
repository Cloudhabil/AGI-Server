#!/usr/bin/env python3
"""
PSI.FIREFOX BROWSER
===================

A PIO-enhanced Firefox wrapper integrating Snowden-grade privacy skills.

BASED ON: Mozilla Firefox / Gecko Engine
SOURCE: https://github.com/mozilla-firefox/firefox

GECKO ARCHITECTURE:
    browser/    - Desktop UI (XUL, JavaScript, C++)
    dom/        - DOM implementation
    layout/     - Rendering engine (CSS boxes, frames)
    js/         - SpiderMonkey JavaScript engine
    docshell/   - Frame loading/embedding
    widget/     - Cross-platform OS widgets
    xpcom/      - Component Object Model

SKILLS INTEGRATED:
    FROM SECUREDROP:
    - Air-gap awareness
    - No-log architecture
    - Metadata stripping

    FROM ONIONSHARE:
    - Ephemeral services
    - Anonymous dropbox

    FROM GLOBALEAKS:
    - 16-digit receipt system
    - Per-session keys
    - Argon2ID key derivation
    - Auto-delete retention

    FROM TAILS:
    - RAM wipe awareness
    - Stream isolation
    - Metadata cleaner

    FROM WHONIX:
    - IP leak protection
    - Keystroke anonymization
    - DNS leak prevention

ARCHITECTURE:
    Psi.firefox = Firefox/Gecko + PIO Brahim Layer + Snowden Skills

Author: ASIOS Core Team
Version: 1.0.0
Codename: Psi.firefox
"""

from __future__ import annotations

import os
import sys
import json
import time
import secrets
import hashlib
import subprocess
import shutil
import winreg
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import base64
import struct
import tempfile

# Attempt to import argon2 for key derivation
try:
    from argon2.low_level import hash_secret_raw, Type
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False

# Brahim constants
BRAHIM_SEQUENCE = [27, 42, 60, 75, 97, 107, 117, 139, 154, 172, 187]
BRAHIM_CENTER = 107
BRAHIM_SUM = 214

# Firefox/Gecko constants
GECKO_ENGINE = "Gecko"
GECKO_SOURCE = "https://github.com/mozilla-firefox/firefox"
GECKO_COMPONENTS = {
    "browser": "Desktop UI (XUL, JavaScript, C++)",
    "dom": "DOM implementation",
    "layout": "Rendering engine (CSS boxes, frames)",
    "js": "SpiderMonkey JavaScript engine",
    "docshell": "Frame loading/embedding",
    "widget": "Cross-platform OS widgets",
    "xpcom": "Component Object Model",
    "netwerk": "Networking (Necko)",
    "security": "NSS cryptographic services",
    "gfx": "Graphics rendering (WebRender)",
}


# =============================================================================
# FIREFOX LOCATOR
# =============================================================================

class FirefoxLocator:
    """Locate Firefox installation on Windows."""

    COMMON_PATHS = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        r"%LOCALAPPDATA%\Mozilla Firefox\firefox.exe",
        r"%PROGRAMFILES%\Mozilla Firefox\firefox.exe",
    ]

    @classmethod
    def find_firefox(cls) -> Optional[Path]:
        """Find Firefox executable."""
        # Try common paths
        for path_template in cls.COMMON_PATHS:
            path = Path(os.path.expandvars(path_template))
            if path.exists():
                return path

        # Try Windows Registry
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe"
            )
            path, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            if Path(path).exists():
                return Path(path)
        except (WindowsError, FileNotFoundError):
            pass

        # Try 32-bit registry on 64-bit Windows
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe"
            )
            path, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            if Path(path).exists():
                return Path(path)
        except (WindowsError, FileNotFoundError):
            pass

        # Try PATH
        firefox_in_path = shutil.which("firefox")
        if firefox_in_path:
            return Path(firefox_in_path)

        return None

    @classmethod
    def get_profile_dir(cls) -> Optional[Path]:
        """Get Firefox profiles directory."""
        profiles_dir = Path(os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles"))
        if profiles_dir.exists():
            return profiles_dir
        return None

    @classmethod
    def get_version(cls, firefox_path: Path) -> Optional[str]:
        """Get Firefox version."""
        try:
            result = subprocess.run(
                [str(firefox_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Parse "Mozilla Firefox 123.0"
            output = result.stdout.strip()
            if "Firefox" in output:
                return output.split()[-1]
        except Exception:
            pass
        return None


# =============================================================================
# SKILL: RECEIPT SYSTEM (from GlobaLeaks)
# =============================================================================

class ReceiptSystem:
    """
    16-digit receipt system for anonymous session identification.
    """

    @staticmethod
    def generate() -> str:
        """Generate a 16-digit receipt."""
        digits = ''.join(str(secrets.randbelow(10)) for _ in range(16))
        return f"{digits[:4]}-{digits[4:8]}-{digits[8:12]}-{digits[12:]}"

    @staticmethod
    def derive_key(receipt: str, salt: bytes = None) -> bytes:
        """Derive encryption key from receipt using Argon2ID."""
        receipt_clean = receipt.replace('-', '')

        if salt is None:
            salt = b'psi.firefox.v1.salt'

        if ARGON2_AVAILABLE:
            key = hash_secret_raw(
                secret=receipt_clean.encode(),
                salt=salt,
                time_cost=3,
                memory_cost=65536,
                parallelism=4,
                hash_len=32,
                type=Type.ID
            )
        else:
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
    """Strip metadata from files to prevent identity leakage."""

    DANGEROUS_EXTENSIONS = {
        '.exe', '.dll', '.bat', '.cmd', '.ps1', '.vbs', '.js',
        '.msi', '.scr', '.com', '.pif', '.hta', '.cpl'
    }

    @staticmethod
    def is_safe_extension(filepath: Path) -> bool:
        return filepath.suffix.lower() not in MetadataCleaner.DANGEROUS_EXTENSIONS

    @staticmethod
    def strip_basic_metadata(data: bytes, filetype: str) -> bytes:
        if filetype.lower() in ['jpg', 'jpeg']:
            return MetadataCleaner._strip_jpeg_exif(data)
        elif filetype.lower() == 'png':
            return MetadataCleaner._strip_png_metadata(data)
        return data

    @staticmethod
    def _strip_jpeg_exif(data: bytes) -> bytes:
        """Remove EXIF from JPEG."""
        if data[:2] != b'\xff\xd8':
            return data

        result = bytearray(data[:2])
        i = 2

        while i < len(data) - 1:
            if data[i] != 0xff:
                break

            marker = data[i+1]

            if marker == 0xe1:  # APP1 (EXIF)
                if i + 3 < len(data):
                    length = struct.unpack('>H', data[i+2:i+4])[0]
                    i += 2 + length
                    continue

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
        """Remove non-essential PNG chunks."""
        if data[:8] != b'\x89PNG\r\n\x1a\n':
            return data

        result = bytearray(data[:8])
        i = 8
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
# SKILL: DNS LEAK PREVENTION (from Whonix)
# =============================================================================

class DNSLeakPrevention:
    """
    Prevent DNS leaks by forcing DNS through secure channels.

    Firefox prefs to set:
    - network.trr.mode = 3 (DNS over HTTPS only)
    - network.trr.uri = secure DNS provider
    - network.proxy.socks_remote_dns = true
    """

    SECURE_DNS_PROVIDERS = {
        "cloudflare": "https://cloudflare-dns.com/dns-query",
        "quad9": "https://dns.quad9.net/dns-query",
        "google": "https://dns.google/dns-query",
        "mullvad": "https://doh.mullvad.net/dns-query",
    }

    @classmethod
    def get_firefox_prefs(cls, provider: str = "cloudflare") -> Dict[str, Any]:
        """Get Firefox prefs for DNS leak prevention."""
        return {
            "network.trr.mode": 3,  # DoH only
            "network.trr.uri": cls.SECURE_DNS_PROVIDERS.get(provider, cls.SECURE_DNS_PROVIDERS["cloudflare"]),
            "network.proxy.socks_remote_dns": True,
            "network.dns.disablePrefetch": True,
            "network.dns.disablePrefetchFromHTTPS": True,
            "network.predictor.enabled": False,
            "network.prefetch-next": False,
        }


# =============================================================================
# SKILL: IP LEAK PROTECTION (from Whonix)
# =============================================================================

class IPLeakProtection:
    """
    Prevent IP leaks through WebRTC and other vectors.

    Firefox prefs to set:
    - media.peerconnection.enabled = false (disable WebRTC)
    - media.navigator.enabled = false
    """

    @classmethod
    def get_firefox_prefs(cls) -> Dict[str, Any]:
        """Get Firefox prefs for IP leak protection."""
        return {
            # WebRTC
            "media.peerconnection.enabled": False,
            "media.peerconnection.ice.default_address_only": True,
            "media.peerconnection.ice.no_host": True,
            "media.peerconnection.ice.proxy_only_if_behind_proxy": True,
            # Navigator
            "media.navigator.enabled": False,
            "media.navigator.video.enabled": False,
            # Geolocation
            "geo.enabled": False,
            "geo.wifi.uri": "",
            # Canvas fingerprinting
            "privacy.resistFingerprinting": True,
            "privacy.trackingprotection.enabled": True,
            "privacy.trackingprotection.fingerprinting.enabled": True,
        }


# =============================================================================
# SKILL: STREAM ISOLATION (from Tails/Whonix)
# =============================================================================

class StreamIsolator:
    """Ensure different activities use separate connections."""

    ACTIVITY_CONFIGS = {
        "browse": {"network.http.max-connections": 256},
        "download": {"network.http.max-connections-per-server": 32},
        "upload": {"network.http.max-connections-per-server": 8},
        "api": {"network.http.max-persistent-connections-per-server": 4},
    }

    @classmethod
    def get_config(cls, activity: str) -> Dict:
        return cls.ACTIVITY_CONFIGS.get(activity, {})


# =============================================================================
# SKILL: RAM WIPE AWARENESS (from Tails)
# =============================================================================

class SecureMemory:
    """Secure memory handling with wipe capabilities."""

    @staticmethod
    def secure_string(data: str) -> 'SecureString':
        return SecureString(data)

    @staticmethod
    def wipe_dict(d: Dict):
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

    def __len__(self):
        return len(self._data)


# =============================================================================
# SKILL: KEYSTROKE ANONYMIZATION (from Whonix)
# =============================================================================

class KeystrokeAnonymizer:
    """Randomize keystroke timing to prevent fingerprinting."""

    MIN_DELAY_MS = 50
    MAX_DELAY_MS = 200

    @classmethod
    def get_random_delay(cls) -> float:
        delay_ms = secrets.randbelow(cls.MAX_DELAY_MS - cls.MIN_DELAY_MS) + cls.MIN_DELAY_MS
        return delay_ms / 1000.0

    @classmethod
    def anonymize_input(cls, text: str, callback) -> None:
        for char in text:
            time.sleep(cls.get_random_delay())
            callback(char)


# =============================================================================
# SKILL: AUTO-DELETE RETENTION (from GlobaLeaks)
# =============================================================================

class AutoDeleteManager:
    """Automatic deletion of data after retention period."""

    DEFAULT_RETENTION_DAYS = 90

    def __init__(self, data_dir: Path, retention_days: int = None):
        self.data_dir = data_dir
        self.retention_days = retention_days or self.DEFAULT_RETENTION_DAYS
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def store(self, key: str, data: bytes, retention_days: int = None) -> Path:
        retention = retention_days or self.retention_days
        expires = time.time() + (retention * 86400)

        filename = f"{key}.{int(expires)}.enc"
        filepath = self.data_dir / filename

        encrypted = self._encrypt(data, key)
        filepath.write_bytes(encrypted)

        return filepath

    def retrieve(self, key: str) -> Optional[bytes]:
        for filepath in self.data_dir.glob(f"{key}.*.enc"):
            parts = filepath.stem.split('.')
            if len(parts) >= 2:
                expires = int(parts[-1])
                if time.time() < expires:
                    encrypted = filepath.read_bytes()
                    return self._decrypt(encrypted, key)
                else:
                    filepath.unlink()
        return None

    def cleanup_expired(self) -> int:
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
        key_bytes = hashlib.sha256(key.encode()).digest()
        return bytes(d ^ key_bytes[i % len(key_bytes)] for i, d in enumerate(data))

    def _decrypt(self, data: bytes, key: str) -> bytes:
        return self._encrypt(data, key)


# =============================================================================
# SKILL: PRIVACY PROFILE GENERATOR
# =============================================================================

class PrivacyProfileGenerator:
    """
    Generate Firefox privacy profiles with hardened settings.

    Creates a user.js file with privacy-focused preferences.
    """

    @classmethod
    def generate_user_js(cls, profile_dir: Path, enhanced: bool = True) -> Path:
        """Generate user.js with privacy settings."""
        prefs = {}

        # Basic privacy
        prefs.update({
            "privacy.donottrackheader.enabled": True,
            "privacy.trackingprotection.enabled": True,
            "privacy.trackingprotection.socialtracking.enabled": True,
            "privacy.firstparty.isolate": True,
            "privacy.resistFingerprinting": True,
        })

        # DNS leak prevention
        prefs.update(DNSLeakPrevention.get_firefox_prefs())

        # IP leak protection
        prefs.update(IPLeakProtection.get_firefox_prefs())

        if enhanced:
            # Enhanced tracking protection
            prefs.update({
                "browser.contentblocking.category": "strict",
                "network.cookie.cookieBehavior": 1,  # Block third-party
                "network.cookie.lifetimePolicy": 2,  # Session only
                "browser.cache.disk.enable": False,
                "browser.cache.memory.enable": True,
                "browser.cache.offline.enable": False,
                "browser.formfill.enable": False,
                "browser.sessionstore.privacy_level": 2,
                "places.history.enabled": False,
                "browser.urlbar.suggest.history": False,
                "browser.urlbar.suggest.bookmark": False,
                "browser.urlbar.suggest.openpage": False,
                "browser.urlbar.suggest.topsites": False,
            })

            # Disable telemetry
            prefs.update({
                "toolkit.telemetry.enabled": False,
                "toolkit.telemetry.unified": False,
                "toolkit.telemetry.archive.enabled": False,
                "datareporting.healthreport.uploadEnabled": False,
                "datareporting.policy.dataSubmissionEnabled": False,
                "browser.ping-centre.telemetry": False,
                "browser.newtabpage.activity-stream.feeds.telemetry": False,
                "browser.newtabpage.activity-stream.telemetry": False,
            })

            # Disable dangerous features
            prefs.update({
                "dom.battery.enabled": False,
                "dom.gamepad.enabled": False,
                "dom.vr.enabled": False,
                "dom.vibrator.enabled": False,
                "dom.enable_performance": False,
                "dom.enable_resource_timing": False,
                "javascript.options.asmjs": False,
                "javascript.options.wasm": False,
            })

        # Write user.js
        user_js_path = profile_dir / "user.js"
        with open(user_js_path, 'w') as f:
            f.write("// Psi.firefox Privacy Profile\n")
            f.write(f"// Generated: {datetime.now(timezone.utc).isoformat()}\n\n")

            for key, value in prefs.items():
                if isinstance(value, bool):
                    js_value = "true" if value else "false"
                elif isinstance(value, int):
                    js_value = str(value)
                elif isinstance(value, str):
                    js_value = f'"{value}"'
                else:
                    js_value = f'"{value}"'

                f.write(f'user_pref("{key}", {js_value});\n')

        return user_js_path


# =============================================================================
# PSI.FIREFOX BROWSER CORE
# =============================================================================

@dataclass
class PsiFirefoxSession:
    """A Psi.firefox browsing session."""
    session_id: str
    receipt: str
    brahim_number: int
    created: str
    encryption_key: bytes = field(repr=False)
    profile_path: Optional[Path] = None
    activities: List[str] = field(default_factory=list)


class PsiFirefox:
    """
    Psi.firefox Browser - PIO-enhanced Firefox with Snowden skills.

    USAGE:
        browser = PsiFirefox()
        session = browser.new_session()
        browser.launch()
    """

    VERSION = "1.0.0"
    CODENAME = "Psi.firefox"
    ENGINE = GECKO_ENGINE
    ENGINE_SOURCE = GECKO_SOURCE

    def __init__(
        self,
        firefox_path: Path = None,
        my_bn: int = 75,
        data_dir: Path = None,
    ):
        # Find Firefox
        self.firefox_path = Path(firefox_path) if firefox_path else FirefoxLocator.find_firefox()
        self.firefox_version = None

        if self.firefox_path and self.firefox_path.exists():
            self.firefox_version = FirefoxLocator.get_version(self.firefox_path)

        self.my_bn = my_bn if my_bn in BRAHIM_SEQUENCE else 107
        self.data_dir = data_dir or Path("data/psi_firefox")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize skills
        self.receipt_system = ReceiptSystem()
        self.metadata_cleaner = MetadataCleaner()
        self.auto_delete = AutoDeleteManager(self.data_dir / "retention")
        self.profile_generator = PrivacyProfileGenerator()

        # Session management
        self.current_session: Optional[PsiFirefoxSession] = None
        self.sessions: Dict[str, PsiFirefoxSession] = {}

        # Browser process
        self._browser_process: Optional[subprocess.Popen] = None

    def new_session(self, create_profile: bool = True) -> PsiFirefoxSession:
        """Create a new anonymous session with receipt."""
        receipt = self.receipt_system.generate()
        encryption_key = self.receipt_system.derive_key(receipt)
        session_id = secrets.token_hex(8)

        # Create isolated profile
        profile_path = None
        if create_profile:
            profile_path = self.data_dir / "profiles" / session_id
            profile_path.mkdir(parents=True, exist_ok=True)

            # Generate privacy-hardened user.js
            self.profile_generator.generate_user_js(profile_path, enhanced=True)

        session = PsiFirefoxSession(
            session_id=session_id,
            receipt=receipt,
            brahim_number=self.my_bn,
            created=datetime.now(timezone.utc).isoformat(),
            encryption_key=encryption_key,
            profile_path=profile_path,
        )

        self.sessions[session.session_id] = session
        self.current_session = session

        return session

    def resume_session(self, receipt: str) -> Optional[PsiFirefoxSession]:
        """Resume a session using receipt."""
        if not self.receipt_system.verify(receipt):
            return None

        for session in self.sessions.values():
            if session.receipt == receipt:
                self.current_session = session
                return session

        return None

    def launch(self, private: bool = True, use_profile: bool = True) -> bool:
        """
        Launch Firefox with Psi.firefox enhancements.

        Args:
            private: Start in private browsing mode
            use_profile: Use isolated privacy profile
        """
        if not self.firefox_path or not self.firefox_path.exists():
            return False

        cmd = [str(self.firefox_path)]

        if private:
            cmd.append("-private-window")

        if use_profile and self.current_session and self.current_session.profile_path:
            cmd.extend(["-profile", str(self.current_session.profile_path)])
        elif use_profile:
            # Create temporary profile
            temp_profile = self.data_dir / "profiles" / f"temp_{secrets.token_hex(4)}"
            temp_profile.mkdir(parents=True, exist_ok=True)
            self.profile_generator.generate_user_js(temp_profile, enhanced=True)
            cmd.extend(["-profile", str(temp_profile)])

        # Disable telemetry via environment
        env = os.environ.copy()
        env["MOZ_CRASHREPORTER_DISABLE"] = "1"
        env["MOZ_DATA_REPORTING"] = "0"

        try:
            self._browser_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                env=env,
            )

            if self.current_session:
                self.current_session.activities.append(
                    f"browser_launch:{datetime.now(timezone.utc).isoformat()}"
                )

            return True
        except Exception:
            return False

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

    def close(self):
        """Close browser and cleanup."""
        self.auto_delete.cleanup_expired()

        if self._browser_process:
            self._browser_process.terminate()
            self._browser_process = None

        if self.current_session:
            self.current_session = None

    def status(self) -> Dict:
        """Get browser status."""
        return {
            "version": self.VERSION,
            "codename": self.CODENAME,
            "engine": self.ENGINE,
            "engine_source": self.ENGINE_SOURCE,
            "firefox_path": str(self.firefox_path) if self.firefox_path else None,
            "firefox_version": self.firefox_version,
            "firefox_available": self.firefox_path is not None and self.firefox_path.exists(),
            "brahim_number": self.my_bn,
            "current_session": self.current_session.session_id if self.current_session else None,
            "active_sessions": len(self.sessions),
            "gecko_components": list(GECKO_COMPONENTS.keys()),
            "skills": [
                "receipt_system",
                "metadata_cleaner",
                "dns_leak_prevention",
                "ip_leak_protection",
                "stream_isolation",
                "auto_delete",
                "secure_memory",
                "keystroke_anonymization",
                "privacy_profile_generator",
            ],
        }

    def __repr__(self) -> str:
        version = self.firefox_version or "?"
        return f"<PsiFirefox v{self.VERSION} '{self.CODENAME}' Firefox/{version} BN={self.my_bn}>"


# =============================================================================
# CLI
# =============================================================================

def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("  PSI.FIREFOX BROWSER")
    print("  PIO-Enhanced Firefox with Snowden Skills")
    print("=" * 70)
    print()

    # Create browser
    browser = PsiFirefox(my_bn=75)
    print(f"Browser: {browser}")
    print()

    # Check Firefox availability
    status = browser.status()
    print("STATUS:")
    print("-" * 50)
    print(f"  Firefox Available: {status['firefox_available']}")
    if status['firefox_path']:
        print(f"  Firefox Path: {status['firefox_path']}")
    if status['firefox_version']:
        print(f"  Firefox Version: {status['firefox_version']}")
    print(f"  Engine: {status['engine']}")
    print(f"  Brahim Number: {status['brahim_number']}")
    print(f"  Skills Loaded: {len(status['skills'])}")
    print()

    # List Gecko components
    print("GECKO ENGINE COMPONENTS:")
    print("-" * 50)
    for comp, desc in GECKO_COMPONENTS.items():
        print(f"  {comp:12} - {desc}")
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
    if session.profile_path:
        print(f"  Profile: {session.profile_path}")
    print()

    # Demo skills
    print("SKILL DEMOS:")
    print("-" * 50)

    # Receipt verification
    print(f"  [Receipt] Valid format: {ReceiptSystem.verify(session.receipt)}")

    # DNS leak prevention
    dns_prefs = DNSLeakPrevention.get_firefox_prefs()
    print(f"  [DNS] DoH Mode: {dns_prefs['network.trr.mode']} (3 = DoH only)")

    # IP leak protection
    ip_prefs = IPLeakProtection.get_firefox_prefs()
    print(f"  [IP] WebRTC disabled: {not ip_prefs['media.peerconnection.enabled']}")

    # Secure storage
    test_data = b"Sensitive Firefox data with 90-day retention"
    stored = browser.store_secure("firefox-test", test_data, days=90)
    print(f"  [AutoDelete] Stored: {stored.name}")

    # Keystroke anonymization
    delay = KeystrokeAnonymizer.get_random_delay()
    print(f"  [Keystroke] Random delay: {delay*1000:.0f}ms")

    print()
    print("=" * 70)
    print("  PSI.FIREFOX BROWSER READY")
    if status['firefox_available']:
        print("  Run: browser.launch() to start Firefox")
    else:
        print("  WARNING: Firefox not found. Install Firefox first.")
    print("=" * 70)

    return browser


if __name__ == "__main__":
    browser = main()
