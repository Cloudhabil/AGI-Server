"""
PSI.APK - PIO + Tor Android Application Suite
==============================================

Core applications connecting PIO's 11-layer Brahim routing
with Tor's anonymity network for Android.

ARCHITECTURE:
    PIO Layer (11 Brahim Numbers) + Tor Layer (Orbot) + Snowden Skills

CORE APPLICATIONS:
    1. PsiMessenger  - Anonymous chat through 11 layers
    2. PsiVault      - Distributed encrypted storage
    3. PsiExchange   - Mirror-pair key exchange
    4. PsiDNS        - Decentralized .brahim naming
    5. PsiRelay      - Brahim beacon network node
    6. PsiMap        - Dark sector topology mapper

ANDROID COMPONENTS:
    - Orbot (Tor proxy) integration
    - Native Brahim layer routing
    - Snowden skills from Psi.onion/Psi.firefox
"""

from .psi_core import (
    PsiCore,
    PsiMessenger,
    PsiVault,
    PsiExchange,
    PsiDNS,
    PsiRelay,
    PsiMap,
    BRAHIM_SEQUENCE,
    BRAHIM_CENTER,
    MIRROR_PAIRS,
    LAYER_NAMES,
)

__version__ = "1.0.0"
__codename__ = "Psi.apk"

__all__ = [
    "PsiCore",
    "PsiMessenger",
    "PsiVault",
    "PsiExchange",
    "PsiDNS",
    "PsiRelay",
    "PsiMap",
    "BRAHIM_SEQUENCE",
    "BRAHIM_CENTER",
    "MIRROR_PAIRS",
    "LAYER_NAMES",
]
