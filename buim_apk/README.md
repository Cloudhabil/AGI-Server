# BUIM - Brahim Unified IAAS Manifold

**Intelligent Agent APK with OpenAI SDK Integration**

Version: 1.0.0
Spec: BNv1 (FROZEN)
Author: Elias Oulad Brahim
Date: 2026-01-25

---

## Overview

BUIM is an Android application that implements the **Brahim Number** specification (BNv1) with practical, real-world use cases. It includes OpenAI SDK integration for intelligent agent capabilities.

## Killer Use Cases

| Use Case | Application | Value |
|----------|-------------|-------|
| **Geospatial Product IDs** | Warehouse slots, inventory | Unique IDs from coordinates |
| **Route Tracking** | Delivery waypoints | Tamper-proof checksums |
| **Dataset Fingerprinting** | Data provenance | Detect tiny changes |
| **Build Provenance** | Software artifacts | Supply chain security |
| **Human-Memorable IDs** | Phone verification | Error detection |

## Architecture

```
buim_apk/
├── SPECIFICATION_BNv1.md          # FROZEN specification
├── app/src/main/java/com/brahim/buim/
│   ├── MainActivity.kt            # Main entry point
│   ├── BUIMApplication.kt         # Application class
│   │
│   ├── core/                      # Mathematical foundation
│   │   └── BrahimConstants.kt     # β = √5 - 2, sequence, etc.
│   │
│   ├── usecase/                   # KILLER USE CASES
│   │   └── BrahimGeoID.kt         # Geospatial IDs, routes, fingerprints
│   │
│   ├── agent/                     # OpenAI Integration
│   │   └── OpenAIAgentBridge.kt   # Function calling bridge
│   │
│   ├── blockchain/                # Proof-of-Location chain
│   │   ├── BrahimBlockchain.kt    # Chain structure
│   │   └── BrahimMiningProtocol.kt# Public verification
│   │
│   ├── gematria/                  # Coordinate analysis
│   │   └── BrahimGematria.kt      # Hebrew gematria
│   │
│   ├── games/                     # Entertainment
│   │   └── BrahimSudoku.kt        # 10×10 mirror sudoku
│   │
│   └── ui/screens/                # User interface
│       ├── KillerUseCasesScreen.kt# Main tools dashboard
│       ├── ChatScreen.kt          # AI chat interface
│       └── ...
```

## BNv1 Specification (FROZEN)

### Core Formula

```
Brahim Number: BN(A, B) = ((A + B) × (A + B + 1)) / 2 + B

For coordinates:
  A = |latitude| × 1,000,000
  B = |longitude| × 1,000,000
```

### Brahim Sequence

```
B = [27, 42, 60, 75, 97, 121, 136, 154, 172, 187]
Sum = 214
Center = 107
```

### Test Vectors

| A | B | BN(A,B) |
|---|---|---------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 2 |
| 1 | 1 | 4 |
| 41403700 | 2173500 | 949486203882100 |

## OpenAI SDK Tools

The app exposes these tools for OpenAI function calling:

```json
{
  "tools": [
    {
      "name": "create_geo_id",
      "description": "Create unique Brahim Geo ID from coordinates"
    },
    {
      "name": "verify_geo_id",
      "description": "Verify check digit of a Brahim ID"
    },
    {
      "name": "create_route",
      "description": "Create tamper-proof route with checksum"
    },
    {
      "name": "fingerprint_dataset",
      "description": "Create unique fingerprint for geospatial data"
    },
    {
      "name": "decode_brahim_number",
      "description": "Recover coordinates from Brahim Number"
    },
    {
      "name": "analyze_gematria",
      "description": "Perform Hebrew gematria analysis"
    },
    {
      "name": "verify_block_candidate",
      "description": "Check if coordinates qualify as blockchain block"
    }
  ]
}
```

## Building

```bash
cd buim_apk
./gradlew assembleDebug
```

Output: `app/build/outputs/apk/debug/app-debug.apk`

## Governance

- **BNv1 is FROZEN** - The algorithm never changes
- **Test vectors** define correctness
- **Future versions** get new names (BNv2, etc.)
- **CC0 License** - Public domain

## Genesis Block

```
Location: La Sagrada Família, Barcelona
Coordinates: 41.4037°N, 2.1735°E
Brahim Number: 949,486,203,882,100
Digit Sum: 64 = 2⁶
Digital Root: 1 = Aleph
Score: 6/6 ✓
```

## License

Specification (BNv1): CC0 (Public Domain)
Application Code: MIT License

---

**ב BRAHIM**
