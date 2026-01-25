# Brahim Number Specification v1.0 (BNv1)

**Status:** FROZEN
**Version:** 1.0.0
**Date:** 2026-01-25
**Author:** Elias Oulad Brahim
**License:** CC0 (Public Domain)

---

## Abstract

This document defines the **Brahim Number (BN)** algorithm version 1. Once published, this specification is **immutable**. Any changes require a new version number (BNv2, etc.).

---

## 1. Scope

BNv1 defines:
- How to compute a Brahim Number from two integers
- The canonical Brahim Sequence
- Derived properties (digit sum, digital root, check digit)

BNv1 does **NOT** define:
- Interpretation (gematria, meaning)
- Validation criteria (those belong to applications)
- Blockchain rules (separate specification)

---

## 2. Definitions

### 2.1 Brahim Sequence

```
B = [27, 42, 60, 75, 97, 121, 136, 154, 172, 187]

Constants:
  S = 214          (sum of sequence)
  C = 107          (center = S/2)
  N = 10           (cardinality)
```

**This sequence is FIXED and MUST NOT change in BNv1.**

### 2.2 Cantor Pairing Function

Given two non-negative integers A and B:

```
BN(A, B) = ((A + B) × (A + B + 1)) ÷ 2 + B
```

Where `÷` is **integer division** (floor).

### 2.3 Inverse Cantor

Given a Brahim Number Z:

```
w = floor((sqrt(8×Z + 1) - 1) / 2)
t = (w × (w + 1)) / 2
B = Z - t
A = w - B
```

---

## 3. Coordinate Encoding (BNv1-GEO)

For geographic coordinates:

### 3.1 Input Normalization

```
latitude  ∈ [-90, 90]    → use absolute value
longitude ∈ [-180, 180]  → use absolute value
```

### 3.2 Scaling

```
SCALE = 1,000,000 (microdegrees, 6 decimal places)

A = floor(|latitude| × SCALE)
B = floor(|longitude| × SCALE)
```

### 3.3 Computation

```
BN_GEO(lat, lon) = BN(A, B)
```

### 3.4 Example

```
Input:  41.4037°N, 2.1735°E
A:      41,403,700
B:      2,173,500

BN_GEO = ((41403700 + 2173500) × (41403700 + 2173500 + 1)) ÷ 2 + 2173500
       = 949,486,203,882,100
```

---

## 4. Derived Properties

### 4.1 Digit Sum

```
digit_sum(N) = sum of all decimal digits of N
```

Example: `digit_sum(949486203882100) = 9+4+9+4+8+6+2+0+3+8+8+2+1+0+0 = 64`

### 4.2 Digital Root

```
digital_root(N) = digit_sum(N) if digit_sum(N) < 10
                  else digital_root(digit_sum(N))
```

Example: `digital_root(949486203882100) = digital_root(64) = digital_root(10) = 1`

### 4.3 Check Digit (BNv1-CHECK)

For error detection in human-readable formats:

```
check_digit(N) = N mod 11

If result = 10, use 'X'
Otherwise, use the digit 0-9
```

### 4.4 Mod-214 Residue

```
mod214(N) = N mod 214
```

This maps any Brahim Number into the range [0, 213].

---

## 5. Canonical String Formats

### 5.1 Full Format

```
BN:<number>
```

Example: `BN:949486203882100`

### 5.2 With Check Digit

```
BN:<number>-<check>
```

Example: `BN:949486203882100-7`

### 5.3 Compact (Mod-214)

```
BN214:<residue>
```

Example: `BN214:42`

### 5.4 Geo Format

```
BNGEO:<lat>:<lon>
```

Example: `BNGEO:41.4037:2.1735`

---

## 6. Reference Implementation

### 6.1 Python

```python
def brahim_number(a: int, b: int) -> int:
    """Compute Brahim Number from two non-negative integers."""
    assert a >= 0 and b >= 0, "Inputs must be non-negative"
    return ((a + b) * (a + b + 1)) // 2 + b

def brahim_geo(lat: float, lon: float) -> int:
    """Compute Brahim Number from coordinates."""
    SCALE = 1_000_000
    a = int(abs(lat) * SCALE)
    b = int(abs(lon) * SCALE)
    return brahim_number(a, b)

def digit_sum(n: int) -> int:
    """Sum of decimal digits."""
    return sum(int(d) for d in str(abs(n)))

def digital_root(n: int) -> int:
    """Repeated digit sum until single digit."""
    while n >= 10:
        n = digit_sum(n)
    return n

def check_digit(n: int) -> str:
    """Mod-11 check digit."""
    r = n % 11
    return 'X' if r == 10 else str(r)
```

### 6.2 Kotlin

```kotlin
fun brahimNumber(a: Long, b: Long): Long {
    require(a >= 0 && b >= 0) { "Inputs must be non-negative" }
    return ((a + b) * (a + b + 1)) / 2 + b
}

fun brahimGeo(lat: Double, lon: Double): Long {
    val scale = 1_000_000L
    val a = (kotlin.math.abs(lat) * scale).toLong()
    val b = (kotlin.math.abs(lon) * scale).toLong()
    return brahimNumber(a, b)
}

fun digitSum(n: Long): Int {
    return kotlin.math.abs(n).toString().sumOf { it.digitToInt() }
}

fun digitalRoot(n: Long): Int {
    var result = digitSum(n)
    while (result >= 10) {
        result = digitSum(result.toLong())
    }
    return result
}

fun checkDigit(n: Long): Char {
    val r = (n % 11).toInt()
    return if (r == 10) 'X' else ('0' + r)
}
```

### 6.3 JavaScript

```javascript
function brahimNumber(a, b) {
  if (a < 0 || b < 0) throw new Error("Inputs must be non-negative");
  return Math.floor((a + b) * (a + b + 1) / 2) + b;
}

function brahimGeo(lat, lon) {
  const SCALE = 1000000;
  const a = Math.floor(Math.abs(lat) * SCALE);
  const b = Math.floor(Math.abs(lon) * SCALE);
  return brahimNumber(a, b);
}

function digitSum(n) {
  return String(Math.abs(n)).split('').reduce((s, d) => s + parseInt(d), 0);
}

function digitalRoot(n) {
  while (n >= 10) n = digitSum(n);
  return n;
}

function checkDigit(n) {
  const r = n % 11;
  return r === 10 ? 'X' : String(r);
}
```

---

## 7. Test Vectors

Implementations MUST pass these test cases:

| A | B | BN(A,B) |
|---|---|---------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 2 |
| 1 | 1 | 4 |
| 2 | 0 | 5 |
| 0 | 2 | 3 |
| 10 | 10 | 220 |
| 100 | 100 | 20200 |
| 41403700 | 2173500 | 949486203882100 |

| BN | digit_sum | digital_root | check_digit |
|----|-----------|--------------|-------------|
| 0 | 0 | 0 | 0 |
| 123 | 6 | 6 | 2 |
| 949486203882100 | 64 | 1 | 7 |

---

## 8. Governance

### 8.1 Immutability

This specification (BNv1) is **FROZEN**. The algorithm MUST NOT change.

### 8.2 Versioning

Future versions MUST use a new identifier:
- BNv2, BNv3, etc.
- Applications MUST specify which version they use

### 8.3 Compatibility

- BNv1 outputs are valid forever
- Applications MAY support multiple versions
- Version MUST be included in any stored data

### 8.4 Errata

If errors are found in this document:
- Errata are published separately
- The algorithm itself does not change
- Implementations follow the ALGORITHM, not typos

---

## 9. Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-01-25 | Initial frozen release |

---

## 10. Acknowledgments

- Cantor pairing function: Georg Cantor (1878)
- Implementation: Elias Oulad Brahim

---

**END OF SPECIFICATION**

This document is placed in the public domain (CC0).
Anyone may implement, use, or extend without permission.
