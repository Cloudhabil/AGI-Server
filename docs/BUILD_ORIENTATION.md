# BUIM Build Orientation Guide

**Status:** APPROVED FOR BUILD
**Date:** 2026-01-26

---

## Quick Reference: 5 Approved Concepts

| # | Concept | Core File | Status |
|---|---------|-----------|--------|
| 1 | Brahim Gematria | `gematria/BrahimGematria.kt` | ✅ Exists |
| 2 | Elliptic Curves ↔ Fluid Dynamics | `brahims_laws/core/brahim_laws.py` | ✅ Exists |
| 3 | Biophilic Design | `core/BrahimConstants.kt` | ✅ Exists |
| 4 | Statistical Validation | `scripts/validate_brahims_laws.py` | ✅ NEW |
| 5 | Deterministic-First ML | `industry/BrahimIndustryLabel.kt` | ✅ NEW |

---

## New Files Created

### Specification
```
docs/BUIM_UNIFIED_ARCHITECTURE_SPEC.md
```
Complete specification of all 5 concepts with:
- Mathematical definitions
- Code structures
- Test vectors
- Build priorities

### Industry Labels (Kotlin)
```
buim_apk/app/src/main/java/com/brahim/buim/industry/BrahimIndustryLabel.kt
```
- `Sector` enum (10 sectors mapped to Brahim sequence)
- `DataType` enum (9 data types)
- `Source` enum (deterministic vs ML flagging)
- `BrahimIndustryLabel` data class
- `BrahimIndustryLabelFactory` (create, parse, verify, upgrade)

### Query Engine (Kotlin)
```
buim_apk/app/src/main/java/com/brahim/buim/industry/DeterministicQueryEngine.kt
```
- `IndustryQuery` input class
- `QueryResult` with provenance tracking
- `DeterministicQueryEngine` (deterministic-first philosophy)
- `LearningLoopProcessor` (verification → training)
- Database interfaces (to implement)

### Validation Script (Python)
```
scripts/validate_brahims_laws.py
```
- `test_law1()` - Sha ~ Im(τ)^α regression
- `test_law4()` - Sha ~ Rey^γ regression
- `test_law3()` - Regime independence χ² test
- Academic output format with confidence intervals

---

## Build Priorities

### Phase 1: Core Infrastructure (Week 1)
```kotlin
// Already exists, verify:
com.brahim.buim.core.BrahimConstants
com.brahim.buim.gematria.BrahimGematria

// New:
com.brahim.buim.industry.BrahimIndustryLabel      ✅ Created
com.brahim.buim.industry.DeterministicQueryEngine ✅ Created
```

### Phase 2: Knowledge Bases (Week 2)
```kotlin
// Implement interfaces:
interface StandardsDatabase    // IEC, ISO, DIN lookup
interface DatasheetDatabase    // Manufacturer specs
interface HandbookDatabase     // Engineering references
```

Embed core data:
- IEC 60617 electrical symbols (~2MB)
- Basic engineering formulas (~500KB)
- Unit conversion tables (~100KB)

### Phase 3: Validation (Week 3)
```bash
# Run statistical validation
python scripts/validate_brahims_laws.py

# Expected output:
# Law 1: α = X.XXX ± X.XXX [CI]
# Law 4: γ = X.XXX ± X.XXX [CI]
# Law 3: χ² = X.XX, p = X.XXX
```

### Phase 4: ML Integration (Week 4)
```kotlin
// Implement ML agent
class MLPredictionAgentImpl : MLPredictionAgent {
    override suspend fun predict(query, sector): MLPrediction
}

// Connect learning loop
class LearningLoopProcessor  // Already created
```

---

## Key Architectural Principles

### 1. Cantor Pairing Everywhere
```kotlin
fun cantorPair(a: Long, b: Long): Long {
    return ((a + b) * (a + b + 1)) / 2 + b
}
```
Used for:
- Geographic coordinates → BrahimGeoID
- Phone numbers → BrahimPhoneID
- Industry data → BIL codes
- Elliptic curve invariants → CurveID

### 2. Deterministic-First Query
```
Query → Search Standards → Search Validated → ML Fallback (FLAGGED)
                ↓                  ↓                    ↓
           100% trust         99% trust          70% + WARNING
```

### 3. Source Tracking
```kotlin
// Every data point knows its provenance
data class BrahimIndustryLabel(
    val source: Source,           // IEC_STANDARD, ML_PREDICTION, etc.
    val isDeterministic: Boolean, // Can we trust this 100%?
    val confidence: Double,       // 1.0 for standards, <1.0 for ML
    val warning: String?          // Non-null if ML-derived
)
```

### 4. Learning Loop
```
ML Prediction → Human Verifies → Training Data
      ↓               ↓               ↓
  Source=901      Source=100      ML improves
  (flagged)       (upgraded)      routing
```

---

## Test Commands

### Kotlin Tests
```bash
cd buim_apk
./gradlew test
```

### Python Validation
```bash
# Install dependencies
pip install scipy statsmodels numpy

# Run validation
python scripts/validate_brahims_laws.py
```

### Check BIL Generation
```kotlin
// In REPL or test
val bil = BrahimIndustryLabelFactory.create(
    sector = Sector.ELECTRICAL,
    dataType = DataType.SPECIFICATION,
    source = Source.IEC_STANDARD,
    itemId = 60617
)
println(bil.fullLabel)  // BIL:27:1:100:60617-X
```

---

## File Locations Summary

```
CLI-main/
├── docs/
│   ├── BUIM_UNIFIED_ARCHITECTURE_SPEC.md  ← Full specification
│   └── BUILD_ORIENTATION.md               ← This file
│
├── buim_apk/app/src/main/java/com/brahim/buim/
│   ├── core/
│   │   └── BrahimConstants.kt             ← Golden ratio, sequence
│   ├── gematria/
│   │   └── BrahimGematria.kt              ← Coordinate → symbolic
│   └── industry/
│       ├── BrahimIndustryLabel.kt         ← BIL system (NEW)
│       └── DeterministicQueryEngine.kt    ← Query engine (NEW)
│
├── src/brahims_laws/
│   └── core/
│       └── brahim_laws.py                 ← Scaling laws
│
├── scripts/
│   └── validate_brahims_laws.py           ← Statistical tests (NEW)
│
└── data/cremona/
    └── *.json, *.jsonl                    ← Elliptic curve data
```

---

## Contact & Attribution

**Author:** Elias Oulad Brahim
**Intellectual Property:** All concepts documented herein
**License:** Proprietary (BUIM project)

---

**END OF ORIENTATION GUIDE**
