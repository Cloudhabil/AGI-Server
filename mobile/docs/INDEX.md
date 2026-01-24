# BSI Documentation Index

**Brahim Secure Intelligence - Complete Documentation**

---

## Quick Navigation

| Document | Purpose | Audience |
|----------|---------|----------|
| [../README.md](../README.md) | Project overview | All users |
| [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) | Step-by-step implementation | Developers |
| [API_REFERENCE.md](API_REFERENCE.md) | Complete API documentation | Developers |
| [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) | Integration patterns | Integrators |

---

## Documentation Structure

```
mobile/
├── README.md                    # Main overview
├── docs/
│   ├── INDEX.md                 # This file
│   ├── ARCHITECTURE_GUIDE.md    # Implementation guide
│   ├── API_REFERENCE.md         # API documentation
│   └── INTEGRATION_GUIDE.md     # Integration patterns
├── python_standalone/
│   ├── bsi_app.py              # Python implementation
│   └── build_executable.py      # Build script
└── android/
    └── app/src/main/java/com/brahim/bsi/
        ├── core/BrahimConstants.kt
        ├── cipher/WormholeCipher.kt
        ├── safety/ASIOSGuard.kt
        ├── router/IntentRouter.kt
        └── agent/BOAAgent.kt
```

---

## Getting Started Path

### For New Users

1. Read [README.md](../README.md) - Understand the project
2. Run `python bsi_app.py --verify` - See it work
3. Read [ARCHITECTURE_GUIDE.md](ARCHITECTURE_GUIDE.md) - Understand how

### For Developers

1. Read [API_REFERENCE.md](API_REFERENCE.md) - Know the interfaces
2. Read [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Learn patterns
3. Study `bsi_app.py` source - See implementation

### For Researchers

1. Read the Mathematical Foundation sections
2. Verify identities with `--verify` flag
3. See publications in `../publications/academic/`

---

## Core Concepts Summary

### The Brahim Security Constant

```
beta = sqrt(5) - 2 = 1/phi^3 = 0.2360679774997897
```

This is the foundation of all BSI security and safety operations.

### The Golden Hierarchy

```
phi   → 1/phi  → alpha → beta → gamma
1.618 → 0.618  → 0.382 → 0.236 → 0.146
```

Self-similarity: alpha/beta = phi

### The Brahim Sequence

```
B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187}
S = 214, C = 107, C/S = 1/2
```

Defines the 10 territories for query routing.

### The 12 Wavelengths

```
delta → theta → alpha → beta → gamma → epsilon →
ganesha → lambda → mu → nu → omega → phi
```

Cognitive pipeline for agent processing.

---

## Key Equations

### Wormhole Transform
```
W*(sigma) = sigma/phi + C_bar * alpha
```

### Energy Functional (ASIOS)
```
E[psi] = (density - GENESIS_CONSTANT)^2
```

### Safety Score
```
safety_score = exp(-energy * 1000)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-24 | Initial release with all modules |

---

## Related Resources

- **Academic Papers**: `../../publications/academic/`
- **Source Code**: `../python_standalone/bsi_app.py`
- **Android Code**: `../android/app/src/main/java/`
- **Tests**: Run `python bsi_app.py --verify`
