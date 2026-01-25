# BUIM APK Build Instructions

## Prerequisites

### 1. Install Android SDK

Download Android Studio from: https://developer.android.com/studio

Or install just the command-line tools:
https://developer.android.com/studio#command-tools

Required SDK components:
- Android SDK Platform 34
- Android SDK Build-Tools 34.0.0
- Android SDK Platform-Tools

### 2. Configure SDK Path

Create `local.properties` in the `buim_apk/` directory:

```properties
sdk.dir=C:\\Users\\YourUsername\\AppData\\Local\\Android\\Sdk
```

Or set the environment variable:
```bash
export ANDROID_HOME=/path/to/android/sdk
```

### 3. Install Java 17+

Ensure Java 17 or higher is installed and in your PATH.

Check with:
```bash
java -version
```

## Building

### Debug Build

```bash
cd buim_apk
./gradlew assembleDebug
```

Output: `app/build/outputs/apk/debug/app-debug.apk`

### Release Build

```bash
cd buim_apk
./gradlew assembleRelease
```

Output: `app/build/outputs/apk/release/app-release.apk`

### Run Tests

```bash
./gradlew test
```

## Project Structure

```
buim_apk/
├── app/src/main/java/com/brahim/buim/
│   ├── core/           # BrahimConstants, Sequence, GoldenRatio
│   ├── cipher/         # WormholeCipher, OnionProtocol
│   ├── physics/        # BrahimCalculator
│   ├── manifold/       # UnifiedManifold, BallTree, VNAND
│   ├── ml/             # KelimutuSubnet
│   ├── games/          # BrahimSudoku
│   ├── solar/          # SolarMap, MarsPlanner
│   ├── network/        # BrahimNetworkProtocol
│   ├── blockchain/     # BrahimBlockchain, MiningProtocol
│   ├── sdk/            # BOAAgent, SDK agents
│   ├── agent/          # BOAMainAgent, OpenAIBridge
│   ├── safety/         # ASIOSGuard, GeometricFirewall
│   ├── services/       # ManifoldService, AgentService
│   └── ui/             # Compose screens and components
└── app/src/test/       # Unit tests
```

## Unified Brahim System Components

| Component | File | Description |
|-----------|------|-------------|
| Calculator | `BrahimCalculator.kt` | Physics constants from sequence |
| Wormhole | `WormholeCipher.kt` | β-based cryptography |
| Sudoku | `BrahimSudoku.kt` | 10×10 constraint puzzle |
| Geospacing | `BrahimGeoID.kt` | Cantor pairing coordinates |
| Network | `BrahimNetworkProtocol.kt` | Geographic-aware protocol |
| Solar | `BrahimSolarMap.kt` | Heliocentric coordinates |
| Mars | `BrahimMarsPlanner.kt` | Mission planning |

## Key Mathematical Constants

```kotlin
val SEQUENCE = intArrayOf(27, 42, 60, 75, 97, 121, 136, 154, 172, 187)
val SUM = 214
val PHI = 1.6180339887498949
val BETA = 0.2360679774997897  // √5 - 2
```

## DOI Reference

DOI: 10.5281/zenodo.18368980

---

*BUIM - Brahim Unified IAAS Manifold*
*© 2026 Elias Oulad Brahim*
