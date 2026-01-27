"""
PSI.FIREFOX - PIO-Enhanced Firefox Browser Suite
=================================================

A privacy-hardened Firefox built on:
- Firefox/Gecko Engine (mozilla-firefox/firefox)
- PIO Brahim Layer (11-layer routing)
- Integrated Snowden Skills

Gecko Components:
- browser/    Desktop UI (XUL, JavaScript, C++)
- dom/        DOM implementation
- layout/     Rendering engine (CSS boxes, frames)
- js/         SpiderMonkey JavaScript engine
- docshell/   Frame loading/embedding
- widget/     Cross-platform OS widgets
- xpcom/      Component Object Model

Skills from:
- SecureDrop (air-gap, no-log, metadata strip)
- OnionShare (ephemeral services)
- GlobaLeaks (receipt system, auto-delete)
- Tails (RAM wipe, stream isolation)
- Whonix (IP/DNS leak protection, keystroke anon)
"""

from .psi_firefox_browser import (
    PsiFirefox,
    PsiFirefoxSession,
    FirefoxLocator,
    ReceiptSystem,
    MetadataCleaner,
    DNSLeakPrevention,
    IPLeakProtection,
    StreamIsolator,
    SecureMemory,
    SecureString,
    KeystrokeAnonymizer,
    AutoDeleteManager,
    PrivacyProfileGenerator,
    GECKO_ENGINE,
    GECKO_SOURCE,
    GECKO_COMPONENTS,
)

__version__ = "1.0.0"
__codename__ = "Psi.firefox"

__all__ = [
    "PsiFirefox",
    "PsiFirefoxSession",
    "FirefoxLocator",
    "ReceiptSystem",
    "MetadataCleaner",
    "DNSLeakPrevention",
    "IPLeakProtection",
    "StreamIsolator",
    "SecureMemory",
    "SecureString",
    "KeystrokeAnonymizer",
    "AutoDeleteManager",
    "PrivacyProfileGenerator",
    "GECKO_ENGINE",
    "GECKO_SOURCE",
    "GECKO_COMPONENTS",
]
