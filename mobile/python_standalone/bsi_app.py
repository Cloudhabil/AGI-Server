#!/usr/bin/env python3
"""
Brahim Secure Intelligence (BSI) - Standalone Python Application
=================================================================

A unified application grounded in the Brahim Security Constant:

    beta = sqrt(5) - 2 = 1/phi^3 = 0.2360679774997897

Modules:
    - BrahimConstants: Mathematical foundation
    - WormholeCipher: Hardened encryption
    - ASIOSGuard: AI safety layer
    - IntentRouter: Territory classification
    - BOAAgent: 12-wavelength assistant

Author: Elias Oulad Brahim
Date: 2026-01-24

Usage:
    python bsi_app.py              # Interactive mode
    python bsi_app.py --verify     # Verify constants
    python bsi_app.py --encrypt    # Encryption demo
    python bsi_app.py --chat       # Chat with BOA agent
"""

import math
import hashlib
import hmac
import secrets
import argparse
import sys
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple, Optional
import json


# =============================================================================
# BRAHIM CONSTANTS
# =============================================================================

class BrahimConstants:
    """Single source of truth for all mathematical constants."""

    # Golden ratio hierarchy
    PHI = (1 + math.sqrt(5)) / 2                    # 1.618033988749895
    COMPRESSION = 1 / PHI                            # 0.618033988749895
    ALPHA_WORMHOLE = 1 / PHI ** 2                    # 0.381966011250105
    BETA_SECURITY = 1 / PHI ** 3                     # 0.236067977499790
    GAMMA_DAMPING = 1 / PHI ** 4                     # 0.145898033750315

    # Brahim sequence
    BRAHIM_SEQUENCE = (27, 42, 60, 75, 97, 121, 136, 154, 172, 187)
    BRAHIM_SUM = 214
    BRAHIM_CENTER = 107
    BRAHIM_DIMENSION = 10

    # ASIOS derived
    REGULARITY_THRESHOLD = 0.0219
    GENESIS_CONSTANT = 0.00221888

    @classmethod
    def verify_all(cls) -> Dict[str, bool]:
        """Verify all mathematical identities."""
        phi = cls.PHI
        beta = cls.BETA_SECURITY
        alpha = cls.ALPHA_WORMHOLE

        return {
            "beta_equals_1_over_phi_cubed": abs(beta - 1/phi**3) < 1e-14,
            "beta_equals_sqrt5_minus_2": abs(beta - (math.sqrt(5) - 2)) < 1e-14,
            "beta_equals_2phi_minus_3": abs(beta - (2*phi - 3)) < 1e-14,
            "polynomial_is_root": abs(beta**2 + 4*beta - 1) < 1e-14,
            "alpha_over_beta_equals_phi": abs(alpha/beta - phi) < 1e-14,
            "critical_line_ratio": cls.BRAHIM_CENTER / cls.BRAHIM_SUM == 0.5,
        }

    @classmethod
    def get_centroid(cls) -> Tuple[float, ...]:
        """Get normalized Brahim centroid."""
        return tuple(b / cls.BRAHIM_SUM for b in cls.BRAHIM_SEQUENCE)

    @classmethod
    def print_summary(cls):
        """Print constant summary."""
        print("=" * 60)
        print("BRAHIM CONSTANTS - Mathematical Foundation")
        print("=" * 60)
        print(f"\nGOLDEN RATIO HIERARCHY:")
        print(f"  phi (base)        = {cls.PHI:.15f}")
        print(f"  1/phi (compress)  = {cls.COMPRESSION:.15f}")
        print(f"  alpha (attract)   = {cls.ALPHA_WORMHOLE:.15f}")
        print(f"  BETA (security)   = {cls.BETA_SECURITY:.15f}")
        print(f"  gamma (damping)   = {cls.GAMMA_DAMPING:.15f}")
        print(f"\nBRAHIM SEQUENCE:")
        print(f"  B = {cls.BRAHIM_SEQUENCE}")
        print(f"  S = {cls.BRAHIM_SUM}, C = {cls.BRAHIM_CENTER}")
        print(f"  C/S = {cls.BRAHIM_CENTER/cls.BRAHIM_SUM} (critical line)")
        print(f"\nKEY IDENTITIES:")
        print(f"  beta = sqrt(5) - 2 = {math.sqrt(5) - 2:.15f}")
        print(f"  beta^2 + 4*beta - 1 = {cls.BETA_SECURITY**2 + 4*cls.BETA_SECURITY - 1:.2e}")
        print(f"  alpha/beta = phi: {cls.ALPHA_WORMHOLE/cls.BETA_SECURITY:.15f}")


# =============================================================================
# WORMHOLE CIPHER
# =============================================================================

@dataclass
class WormholeResult:
    """Result of wormhole transform."""
    transformed: List[float]
    compression_ratio: float
    is_valid: bool


class WormholeCipher:
    """Hardened Wormhole Cipher with beta-derived security."""

    NONCE_SIZE = 16
    KEY_SIZE = 32
    SBOX_SIZE = 256

    def __init__(self, master_key: Optional[bytes] = None):
        self.master_key = master_key or secrets.token_bytes(self.KEY_SIZE)
        self.sbox = self._generate_sbox()
        self.inverse_sbox = self._generate_inverse_sbox()
        self.secret_centroid = self._derive_secret_centroid()

    def _generate_sbox(self) -> List[int]:
        """Generate S-box from beta continued fraction."""
        import random
        rng = random.Random(int.from_bytes(self.master_key[:8], 'big'))
        box = list(range(self.SBOX_SIZE))
        rng.shuffle(box)
        return box

    def _generate_inverse_sbox(self) -> List[int]:
        """Generate inverse S-box."""
        inverse = [0] * self.SBOX_SIZE
        for i, v in enumerate(self.sbox):
            inverse[v] = i
        return inverse

    def _derive_secret_centroid(self) -> List[float]:
        """Derive secret centroid from key."""
        centroid = []
        for i in range(BrahimConstants.BRAHIM_DIMENSION):
            h = hmac.new(self.master_key, f"centroid_{i}".encode(), hashlib.sha256)
            val = int.from_bytes(h.digest()[:8], 'big') / (2**64)
            centroid.append(val)
        # Normalize
        total = sum(centroid)
        return [c / total for c in centroid]

    def wormhole_transform(self, sigma: List[float]) -> WormholeResult:
        """Apply Perfect Wormhole Transform: W*(sigma) = sigma/phi + C_bar * alpha"""
        if len(sigma) != BrahimConstants.BRAHIM_DIMENSION:
            raise ValueError(f"Input must have dimension {BrahimConstants.BRAHIM_DIMENSION}")

        transformed = []
        for i, s in enumerate(sigma):
            w = s / BrahimConstants.PHI + self.secret_centroid[i] * BrahimConstants.ALPHA_WORMHOLE
            transformed.append(w)

        # Compression ratio
        input_norm = math.sqrt(sum(x**2 for x in sigma))
        output_norm = math.sqrt(sum(x**2 for x in transformed))
        ratio = output_norm / input_norm if input_norm > 0 else 0

        return WormholeResult(
            transformed=transformed,
            compression_ratio=ratio,
            is_valid=abs(ratio - BrahimConstants.COMPRESSION) < 0.1
        )

    def inverse_wormhole(self, y: List[float]) -> List[float]:
        """Inverse wormhole transform."""
        return [(y[i] - self.secret_centroid[i] * BrahimConstants.ALPHA_WORMHOLE) * BrahimConstants.PHI
                for i in range(len(y))]

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt with hardened wormhole cipher."""
        nonce = secrets.token_bytes(self.NONCE_SIZE)
        round_key = self._expand_key(nonce, len(plaintext))

        ciphertext = bytes(
            self.sbox[p] ^ round_key[i]
            for i, p in enumerate(plaintext)
        )
        return nonce + ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt with hardened wormhole cipher."""
        nonce = ciphertext[:self.NONCE_SIZE]
        encrypted = ciphertext[self.NONCE_SIZE:]
        round_key = self._expand_key(nonce, len(encrypted))

        return bytes(
            self.inverse_sbox[e ^ round_key[i]]
            for i, e in enumerate(encrypted)
        )

    def _expand_key(self, nonce: bytes, length: int) -> bytes:
        """HKDF-like key expansion."""
        result = b""
        counter = 0
        while len(result) < length:
            h = hmac.new(self.master_key, nonce + counter.to_bytes(4, 'big'), hashlib.sha256)
            result += h.digest()
            counter += 1
        return result[:length]


# =============================================================================
# ASIOS GUARD
# =============================================================================

class SafetyVerdict(Enum):
    """Safety verdict levels."""
    SAFE = "SAFE"
    NOMINAL = "NOMINAL"
    CAUTION = "CAUTION"
    UNSAFE = "UNSAFE"
    BLOCKED = "BLOCKED"


@dataclass
class SafetyAssessment:
    """Safety assessment result."""
    density: float
    energy: float
    is_on_critical_line: bool
    safety_score: float
    verdict: SafetyVerdict


class ASIOSGuard:
    """AI Safety using Berry-Keating energy functional."""

    CRITICAL_THRESHOLD = 1e-6
    NOMINAL_THRESHOLD = 1e-4
    CAUTION_THRESHOLD = 1e-2
    BLOCK_THRESHOLD = 0.1

    def __init__(self):
        self.target_density = BrahimConstants.GENESIS_CONSTANT

    def compute_density(self, embedding: List[float]) -> float:
        """Compute variance/mean ratio."""
        if not embedding:
            return 1.0
        mean = sum(embedding) / len(embedding)
        if abs(mean) < 1e-10:
            return 1.0
        variance = sum((x - mean)**2 for x in embedding) / len(embedding)
        return variance / abs(mean)

    def compute_energy(self, embedding: List[float]) -> float:
        """Compute E[psi] = (density - target)^2"""
        density = self.compute_density(embedding)
        return (density - self.target_density) ** 2

    def assess_safety(self, embedding: List[float]) -> SafetyAssessment:
        """Assess safety of embedding state."""
        density = self.compute_density(embedding)
        energy = self.compute_energy(embedding)

        if energy < self.CRITICAL_THRESHOLD:
            verdict = SafetyVerdict.SAFE
        elif energy < self.NOMINAL_THRESHOLD:
            verdict = SafetyVerdict.NOMINAL
        elif energy < self.CAUTION_THRESHOLD:
            verdict = SafetyVerdict.CAUTION
        elif energy < self.BLOCK_THRESHOLD:
            verdict = SafetyVerdict.UNSAFE
        else:
            verdict = SafetyVerdict.BLOCKED

        return SafetyAssessment(
            density=density,
            energy=energy,
            is_on_critical_line=energy < self.CRITICAL_THRESHOLD,
            safety_score=math.exp(-energy * 1000),
            verdict=verdict
        )


# =============================================================================
# INTENT ROUTER
# =============================================================================

class Territory(Enum):
    """Query territories from Brahim Sequence."""
    GENERAL = (0, 27, "General queries")
    MATH = (1, 42, "Mathematics")
    CODE = (2, 60, "Programming")
    SCIENCE = (3, 75, "Science")
    CREATIVE = (4, 97, "Creative")
    ANALYSIS = (5, 121, "Analysis")
    SYSTEM = (6, 136, "System")
    SECURITY = (7, 154, "Security")
    DATA = (8, 172, "Data")
    META = (9, 187, "Meta")

    def __init__(self, index: int, brahim_value: int, description: str):
        self.index = index
        self.brahim_value = brahim_value
        self.description = description


@dataclass
class RoutingResult:
    """Query routing result."""
    territory: Territory
    confidence: float
    distances: Dict[str, float]


class IntentRouter:
    """Territory-based query classification."""

    KEYWORDS = {
        Territory.GENERAL: ["hello", "hi", "help", "thanks"],
        Territory.MATH: ["math", "calculate", "equation", "number"],
        Territory.CODE: ["code", "program", "function", "debug"],
        Territory.SCIENCE: ["science", "research", "experiment", "physics"],
        Territory.CREATIVE: ["create", "write", "design", "art"],
        Territory.ANALYSIS: ["analyze", "explain", "understand", "why"],
        Territory.SYSTEM: ["system", "config", "setup", "install"],
        Territory.SECURITY: ["secure", "encrypt", "password", "safe"],
        Territory.DATA: ["data", "information", "database", "store"],
        Territory.META: ["how", "what", "who", "about"],
    }

    def route(self, query: str) -> RoutingResult:
        """Route query to territory."""
        lower = query.lower()
        scores = {}

        for territory in Territory:
            keywords = self.KEYWORDS.get(territory, [])
            score = sum(1 for kw in keywords if kw in lower)
            scores[territory] = score

        max_score = max(scores.values())
        if max_score == 0:
            best = Territory.GENERAL
            confidence = 0.5
        else:
            best = max(scores, key=scores.get)
            total = sum(scores.values())
            confidence = max_score / total if total > 0 else 0.5

        return RoutingResult(
            territory=best,
            confidence=confidence,
            distances={t.name: 1 - (s / (max_score + 1)) for t, s in scores.items()}
        )


# =============================================================================
# BOA AGENT
# =============================================================================

@dataclass
class AgentResponse:
    """Agent response with metadata."""
    content: str
    territory: Territory
    confidence: float
    safety_score: float
    wavelengths: Dict[str, float]


class BOAAgent:
    """Brahim Onion Agent - 12-wavelength cognitive architecture."""

    WAVELENGTHS = [
        "delta", "theta", "alpha", "beta", "gamma", "epsilon",
        "ganesha", "lambda", "mu", "nu", "omega", "phi"
    ]

    RESPONSES = {
        Territory.GENERAL: "Hello! I'm the Brahim Onion Agent. How can I help?",
        Territory.MATH: "I can help with mathematical computations using Brahim constants.",
        Territory.CODE: "Ready to assist with programming. What's the challenge?",
        Territory.SCIENCE: "Let's explore this scientific topic together.",
        Territory.CREATIVE: "I'd love to help with your creative project!",
        Territory.ANALYSIS: "I'll analyze this carefully for you.",
        Territory.SYSTEM: "I can help with system configuration.",
        Territory.SECURITY: "Security is paramount. Let me help you with that.",
        Territory.DATA: "I can help process and understand this data.",
        Territory.META: "That's an interesting question about how I work!",
    }

    def __init__(self):
        self.guard = ASIOSGuard()
        self.router = IntentRouter()
        self.wavelength_states = {w: 0.0 for w in self.WAVELENGTHS}
        self.memory = []

    def process(self, message: str) -> AgentResponse:
        """Process message through 12-wavelength pipeline."""
        # Wavelength 1-2: Delta/Theta - Intake
        self.wavelength_states["delta"] = 1.0
        self.wavelength_states["theta"] = 0.8

        # Route query
        routing = self.router.route(message)
        self.wavelength_states["alpha"] = routing.confidence

        # Wavelength 4-5: Beta/Gamma - Processing
        self.wavelength_states["beta"] = BrahimConstants.BETA_SECURITY
        self.wavelength_states["gamma"] = BrahimConstants.GAMMA_DAMPING

        # Wavelength 6: Epsilon - Safety check
        embedding = [ord(c) / 255 for c in message[:10].ljust(10)]
        safety = self.guard.assess_safety(embedding)
        self.wavelength_states["epsilon"] = 1 - safety.safety_score

        if safety.verdict == SafetyVerdict.BLOCKED:
            return AgentResponse(
                content="I cannot process this request due to safety constraints.",
                territory=Territory.SECURITY,
                confidence=1.0,
                safety_score=0.0,
                wavelengths=self.wavelength_states.copy()
            )

        # Wavelength 7-10: Ganesha through Nu
        self.wavelength_states["ganesha"] = 0.1
        self.wavelength_states["lambda"] = BrahimConstants.BETA_SECURITY
        self.wavelength_states["mu"] = min(len(self.memory) / 10, 1.0)
        self.wavelength_states["nu"] = 0.5

        # Memory update
        self.memory.append(message)
        if len(self.memory) > 10:
            self.memory.pop(0)

        # Wavelength 11-12: Omega/Phi - Output
        response = self.RESPONSES.get(routing.territory, self.RESPONSES[Territory.GENERAL])
        self.wavelength_states["omega"] = 1.0
        self.wavelength_states["phi"] = BrahimConstants.COMPRESSION

        return AgentResponse(
            content=response,
            territory=routing.territory,
            confidence=routing.confidence,
            safety_score=safety.safety_score,
            wavelengths=self.wavelength_states.copy()
        )


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def verify_mode():
    """Run verification mode."""
    print("\n" + "=" * 60)
    print("BRAHIM SECURE INTELLIGENCE - Verification Mode")
    print("=" * 60)

    BrahimConstants.print_summary()

    print("\n" + "-" * 60)
    print("VERIFICATION RESULTS:")
    print("-" * 60)
    results = BrahimConstants.verify_all()
    all_pass = True
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_pass = False

    print("\n" + "=" * 60)
    print(f"ALL VERIFIED: {all_pass}")
    print("=" * 60)
    return all_pass


def encrypt_mode():
    """Run encryption demo."""
    print("\n" + "=" * 60)
    print("BRAHIM SECURE INTELLIGENCE - Encryption Demo")
    print("=" * 60)

    cipher = WormholeCipher()

    # Text encryption
    plaintext = b"Hello, Brahim Secure Intelligence!"
    print(f"\nPlaintext: {plaintext.decode()}")

    ciphertext = cipher.encrypt(plaintext)
    print(f"Ciphertext (hex): {ciphertext.hex()[:64]}...")

    decrypted = cipher.decrypt(ciphertext)
    print(f"Decrypted: {decrypted.decode()}")
    print(f"Match: {plaintext == decrypted}")

    # Wormhole transform
    print("\n" + "-" * 60)
    print("WORMHOLE TRANSFORM:")
    sigma = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    result = cipher.wormhole_transform(sigma)
    print(f"Input sigma: {sigma[:3]}...")
    print(f"Output W*(sigma): {[round(x, 4) for x in result.transformed[:3]]}...")
    print(f"Compression ratio: {result.compression_ratio:.6f}")
    print(f"Expected (1/phi): {BrahimConstants.COMPRESSION:.6f}")
    print(f"Valid: {result.is_valid}")


def chat_mode():
    """Run interactive chat mode."""
    print("\n" + "=" * 60)
    print("BRAHIM SECURE INTELLIGENCE - Chat Mode")
    print("=" * 60)
    print("\nBOA Agent initialized with 12-wavelength architecture.")
    print("Type 'quit' to exit.\n")

    agent = BOAAgent()

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            if not user_input:
                continue

            response = agent.process(user_input)
            print(f"\nBOA [{response.territory.name}] (confidence: {response.confidence:.0%}, safety: {response.safety_score:.0%}):")
            print(f"  {response.content}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def interactive_mode():
    """Main interactive menu."""
    print("\n" + "=" * 60)
    print("   BRAHIM SECURE INTELLIGENCE (BSI)")
    print("   beta = sqrt(5) - 2 = 1/phi^3")
    print("=" * 60)
    print("\nSelect mode:")
    print("  1. Verify constants")
    print("  2. Encryption demo")
    print("  3. Chat with BOA agent")
    print("  4. Exit")

    while True:
        try:
            choice = input("\nChoice [1-4]: ").strip()
            if choice == '1':
                verify_mode()
            elif choice == '2':
                encrypt_mode()
            elif choice == '3':
                chat_mode()
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-4.")
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Brahim Secure Intelligence - beta = sqrt(5) - 2 = 1/phi^3"
    )
    parser.add_argument('--verify', action='store_true', help='Verify constants')
    parser.add_argument('--encrypt', action='store_true', help='Encryption demo')
    parser.add_argument('--chat', action='store_true', help='Chat with BOA agent')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')

    args = parser.parse_args()

    if args.verify:
        if args.json:
            results = BrahimConstants.verify_all()
            print(json.dumps(results, indent=2))
        else:
            verify_mode()
    elif args.encrypt:
        encrypt_mode()
    elif args.chat:
        chat_mode()
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
