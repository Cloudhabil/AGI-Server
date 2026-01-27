"""
PSI.ONION - PIO-Enhanced Tor Browser Suite
==========================================

A Snowden-grade browser built on:
- Tor Browser (network anonymity)
- PIO Brahim Layer (11-layer routing)
- Integrated Snowden Skills

Skills from:
- SecureDrop (air-gap, no-log, metadata strip)
- OnionShare (ephemeral .onion, dropbox)
- GlobaLeaks (receipt system, auto-delete)
- Briar (P2P, offline sync)
- Tails (RAM wipe, stream isolation)
- Whonix (IP leak protection, keystroke anon)
"""

from .psi_browser import (
    PsiBrowser,
    PsiSession,
    ReceiptSystem,
    MetadataCleaner,
    EphemeralOnion,
    StreamIsolator,
    SecureMemory,
    SecureString,
    KeystrokeAnonymizer,
    AutoDeleteManager,
)

__version__ = "1.0.0"
__codename__ = "Psi.onion"

__all__ = [
    "PsiBrowser",
    "PsiSession",
    "ReceiptSystem",
    "MetadataCleaner",
    "EphemeralOnion",
    "StreamIsolator",
    "SecureMemory",
    "SecureString",
    "KeystrokeAnonymizer",
    "AutoDeleteManager",
]
