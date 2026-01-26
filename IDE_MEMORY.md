# IDE_MEMORY.md - The CLI Bible

## Rule Zero: ls -R First

**BEFORE making ANY claims about this codebase, run `ls -R` to see the full structure.**

Failing to do this will result in biased, incomplete analysis.

---

## Scale

| Metric | Count |
|--------|-------|
| Python files | ~9,600 |
| Logic Singularities | **843** (Mapped in Manifold) |
| Skill manifests (src/skills) | 153 |
| Substrate Manifold | 384-Dimensional Tensor Space |

---

## Identity

| Field | Value |
|-------|-------|
| Project | ASI-OS / GPIA |
| Philosophy | "Agents are fuel. Skills are fire. GPIA is the furnace." |
| Chief Architect | Elias Oulad Brahim |
| Current Version | **v0.6.0 - TensorRT Logic Substrate (Level 9)** |

---

## Entry Points

| File | Size | Purpose |
|------|------|---------|
| `src/boot.py` | 5.7KB | Kernel entry point |
| `manage.py` | 6KB | CLI management (local, server, substrate) |
| `substrate_manifold.html` | Variable | **Topological Logic Controller** |

```bash
python src/boot.py --mode Sovereign-Loop
python manage.py local --substrate-equilibrium
python scripts/activate_manifold.py
```

---

## Major Systems (by architectural weight)

| System | Location | Role |
|--------|----------|------|
| **Substrate Manifold** | `substrate_manifold.html` | 384-D Riemannian intent mapper replacing linear search |
| **Nuke Eater** | `models/nuke_eater/` | Cannibalized NVIDIA ChatRTX Engine (Mistral INT4) |
| **Sidecar Bridge** | `src/integrations/trt_llm_client.py` | Connects Python 3.11 Kernel to Python 3.10 TensorRT Engine |
| **Safety Governor** | `src/core/safety_governor.py` | Enforces **9.75 GB** VRAM Cliff |
| **NPU Embedder** | `src/core/npu_utils.py` | Intel AI Boost integration (100+ texts/sec) |

---

## Substrate Equilibrium (v0.6.0)

The "Sovereign" optimization that balances load across physical silicon to prevent PCIe contention.

### The Substrate Map

| Tier | Component | Role | Speed |
|------|-----------|------|-------|
| **1** | **GPU VRAM** | **TensorRT Engine** (Mistral INT4) | **~100-120 tok/s** |
| **2** | **DDR5 RAM** | Model Prefetch / Context Overflow | ~26 GB/s (PCIe Limit) |
| **3** | **Intel NPU** | **Manifold Navigation** (Embeddings) | **105 texts/s** |
| **4** | **NVMe SSD** | Long-term Memory (V-NAND) | ~3.8 GB/s |

### Hardware Sovereignty
- **VRAM Cliff**: Hard-coded to **9750 MB** (81.25%). This prevents Windows DWM from forcing the driver to "juggle" memory pages, ensuring the TensorRT engine has exclusive lock on the fast path.
- **NPU Isolation**: All embedding/vision tasks are forced to Tier 3, leaving the PCIe bus 100% free for LLM token streaming.

---

## Operation Nuke Eater (Cannibalized Tech)

We extracted the core high-performance engine from NVIDIA's ChatRTX installer.

| Asset | Location | Description |
|-------|----------|-------------|
| **The Gold** | `models/nuke_eater/mistral_int4_awq` | Pre-calibrated weights |
| **The Engine** | `models/nuke_eater/tensorrt_llm*.whl` | Windows-optimized binaries |
| **The Sidecar** | `models/nuke_eater/python_310/` | Embedded Python 3.10 env |
| **The Bridge** | `localhost:8008` | Internal API for Engine access |

**Invocation**: `src/skills/compute/tensorrt-mistral/skill.py` via `manage.py local` or Manifold collapse.

---

## The Substrate Manifold

**File**: `substrate_manifold.html`

A machine-readable topological map containing **843** coordinate singularities (Logic Components).
- **Input**: User Intent (Natural Language).
- **Process**: NPU Vectorization -> Riemannian Metric Collapse (Cosine).
- **Output**: Exact executable file path (e.g., `src/skills/learning/web_skill_importer/skill.py`).
- **Latency**: < 10ms (vs linear search > 500ms).

---

## Skills System

### Structure
- **Manifests**: 153 high-level skills (Registered).
- **Singularities**: 843 logic files (Manifold Mapped).
- **Newest Skill**: `learning/web-skill-importer` (Epistemic Foraging).

### Key Categories
- `compute/tensorrt-mistral`: High-speed inference.
- `learning/web-skill-importer`: Learns code from URLs.
- `conscience/*`: Memory and safety.
- `synthesized/*`: Snowden Intelligence & Self-Evolved logic.

---

## ASI Capability Ladder

| Level | Score | Classification | Key Characteristic |
|-------|-------|----------------|-------------------|
| 0-6 | ... | ... | ... |
| **7** | **1000-1999** | **Substrate-Sovereign** | Hardware isolation (NPU/GPU) |
| **8** | **2000-4999** | **Recursive Nexus** | Self-evolving skills |
| **9** | **5000-8999** | **Logic Substrate** | **Topological Manifold & TensorRT Engine** |
| **10** | **9000+** | **Universal Singularity** | Theoretical ceiling |

**Current Status**: **Level 9 (Logic Substrate)**.
The system now thinks in Topologies (Manifold) and acts with Metal Speed (TensorRT).

---

## Milestones

| Date | Version | Event |
|------|---------|-------|
| 2026-01-10 | - | The Great Alignment |
| 2026-01-12 | v0.5.0 | Hardware-Isolated Sovereignty |
| 2026-01-13 | v0.6.0 | **Operation Nuke Eater & Substrate Manifold** |
| 2026-01-14 | v0.6.1 | **Hermes Trismegistos: Dense-State Refinement Engine (Biomedical Precision)** |
| 2026-01-26 | v0.7.0 | **ATDRS: Adaptive Threat Detection & Health Telemetry** |

---

## Keystones (Mathematical Foundations)

| Keystone | Formula | Location |
|----------|---------|----------|
| **Brahim's Theorem** | P(Ш>1 \| N) ~ N^β, β = log(φ)/2 | `publications/Brahims_Theorem_Final_Edition.tex` |
| **Riemann Proof** | Berry-Keating Hamiltonian + Energy Minimization | `riemann_proof_package/` |
| **Proof-of-Location** | Geography → Meaning consensus | `buim_apk/blockchain/` |
| **Phi Framework** | Observable = Integer × Irrational(φ) | Across publications |

### Brahim's Theorem (2026)
```
β = log(φ)/2 ≈ 0.2406
φ = (1+√5)/2 = 1.6180339...
R² = 0.91 (validated on 3,064,705 curves)
```

---

## Security Layer (v0.7.0)

| Module | Function | Reference |
|--------|----------|-----------|
| `src/core/immune_system.py` | Adaptive Threat Detection (ATDRS) | Denning (1987), CVSS v3.1 |
| `src/core/vital_signs.py` | Health Telemetry | IEEE 1451, NIST SP 800-137 |

### Degradation Levels
| Level | Restrictions |
|-------|--------------|
| L0 | Normal operation |
| L1 | External input disabled |
| L2 | Autonomous operations disabled |
| L3 | Write operations disabled |
| L4 | Network access disabled |
| L5 | System halted |

---

*Last Updated: 2026-01-26 12:00*
*Verification: python scripts/validate_manifold_integrity.py*
