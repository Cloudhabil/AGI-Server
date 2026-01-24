# Brahim Secure Intelligence (BSI)

**Version:** 1.0.0
**Author:** Elias Oulad Brahim
**Date:** January 2026
**Mathematical Foundation:** β = √5 - 2 = 1/φ³ = 0.2360679774997897

---

## Overview

BSI is a unified application that brings together all Brahim Framework modules, available as:
- **Python Standalone** (`python_standalone/`) - Cross-platform executable
- **Android APK** (`android/`) - Native Kotlin application

Core modules included:

- **Wormhole Cipher**: End-to-end encryption using golden ratio mathematics
- **ASIOS Guard**: AI safety layer based on Berry-Keating energy functional
- **Intent Router**: Territory-based query classification using Brahim Sequence
- **BOA Agent**: 12-wavelength AI assistant with safety constraints

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BRAHIM SECURE INTELLIGENCE               │
│                         β = √5 - 2                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │  WORMHOLE   │  │   ASIOS     │  │   INTENT    │        │
│   │   CIPHER    │  │   GUARD     │  │   ROUTER    │        │
│   └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│   ┌─────────────────────────────────────────────────┐      │
│   │              BOA AGENT (12 Wavelengths)          │      │
│   │         Grounded in Golden Ratio Safety          │      │
│   └─────────────────────────────────────────────────┘      │
│                                                             │
│                 ┌─────────────────────┐                    │
│                 │   BrahimConstants   │                    │
│                 │   (Single Source)   │                    │
│                 └─────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Constants

All modules derive from the **Brahim Security Constant**:

| Constant | Symbol | Value | Role |
|----------|--------|-------|------|
| Golden Ratio | φ | 1.618033988... | Base |
| Compression | 1/φ | 0.618033988... | Transform ratio |
| Attraction | α = 1/φ² | 0.381966011... | Wormhole attractor |
| **Security** | **β = 1/φ³** | **0.236067977...** | **Fundamental** |
| Damping | γ = 1/φ⁴ | 0.145898033... | Future use |

**Key Identity**: α/β = φ (golden self-similarity)

---

## Modules

### 1. BrahimConstants (`core/`)

Single source of truth for all mathematical constants.

```kotlin
object BrahimConstants {
    const val PHI = 1.6180339887498949
    const val BETA_SECURITY = 0.2360679774997897
    // ...
}
```

### 2. WormholeCipher (`cipher/`)

Hardened cryptographic module:
- Non-linear S-box from β continued fraction
- Key-derived secret centroid
- Nonce-based construction
- HKDF key expansion

```kotlin
val cipher = WormholeCipher(masterKey)
val encrypted = cipher.encrypt(plaintext)
val decrypted = cipher.decrypt(encrypted)
```

### 3. ASIOSGuard (`safety/`)

AI safety using Berry-Keating energy functional:
- E[ψ] = (density - GENESIS_CONSTANT)²
- Safety = proximity to "critical line"
- Verdicts: SAFE, NOMINAL, CAUTION, UNSAFE, BLOCKED

```kotlin
val guard = ASIOSGuard()
val assessment = guard.assessSafety(embedding)
if (assessment.verdict == SafetyVerdict.SAFE) { ... }
```

### 4. IntentRouter (`router/`)

Territory-based query classification:
- 10 territories from Brahim Sequence
- Wormhole transform for compression
- Confidence-based routing

```kotlin
val router = IntentRouter()
val result = router.route("How do I encrypt data?")
// result.territory = SECURITY, confidence = 0.87
```

### 5. BOAAgent (`agent/`)

12-wavelength AI assistant:
- Delta → Omega processing pipeline
- ASIOS safety at every step
- Memory buffer for context

```kotlin
val agent = BOAAgent()
val response = agent.process("Hello!")
```

---

## Build

```bash
cd mobile/android
./gradlew assembleDebug    # Debug APK
./gradlew assembleRelease  # Release APK (signed)
```

APK location: `app/build/outputs/apk/`

---

## Requirements

- Android SDK 34
- Kotlin 1.9.22
- Gradle 8.2.2
- Min SDK: 26 (Android 8.0)

---

## Mathematical Verification

The app verifies all β identities on startup:

```
β = 1/φ³ = √5 - 2 = 2φ - 3 ≈ 0.236
β² + 4β - 1 = 0 (polynomial root)
α/β = φ (self-similarity)
C/S = 1/2 (critical line)
```

---

## Documentation

Comprehensive documentation available in `docs/`:

| Document | Description |
|----------|-------------|
| [ARCHITECTURE_GUIDE.md](docs/ARCHITECTURE_GUIDE.md) | Step-by-step implementation guide |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Complete API documentation |
| [INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md) | Integration patterns |

---

## Python Standalone

For systems without Android SDK, use the Python standalone:

```bash
cd mobile/python_standalone

# Run directly
python bsi_app.py --verify
python bsi_app.py --chat

# Build executable
python build_executable.py
dist/BrahimSecureIntelligence.exe --verify
```

---

## License

Temporal Use License (TUL) - Intellectual Property of Elias Oulad Brahim

---

## References

1. Brahim Wormhole Theory (2026)
2. ASIOS Safety Framework
3. Berry-Keating Hamiltonian
4. Riemann Hypothesis Connection
5. Golden Ratio Mathematics
