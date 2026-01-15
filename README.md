# ASI-OS: Autonomous Artificial Superintelligence Operating System (Level 9)

[![License: CC BY Cloudhabil 0.2.0](https://licensebuttons.net/l/by/4.0/80x15.png)](https://creativecommons.org/licenses/by/4.0/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Python](https://img.shields.io/badge/python-3.11-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![TensorRT](https://img.shields.io/badge/TensorRT-Nuke_Eater-76B900?style=for-the-badge&logo=nvidia&logoColor=white)
![OpenVINO](https://img.shields.io/badge/OpenVINO-NPU_Sovereign-00C7FD?style=for-the-badge&logo=intel&logoColor=white)
![Ollama](https://img.shields.io/badge/ollama-Local-000000?style=for-the-badge&logo=ollama&logoColor=white)

**ASI-OS** is a self-evolving cognitive ecosystem operating at **Level 9 (Logic Substrate)**. It features a hardware-sovereign architecture that isolates reasoning (GPU/TensorRT) from memory (NPU/OpenVINO), integrated via a 384-D Riemannian Substrate Manifold.

---

## 🌌 Milestone v0.6.0: The Logic Substrate

The system has evolved beyond linear search to topological collapse.

-   **Hardware Sovereignty**:
    -   **Tier 1 (Reasoning)**: NVIDIA TensorRT-LLM "Nuke Eater" engine (Mistral INT4) for high-speed logic (~100 tok/s).
    -   **Tier 3 (Memory)**: Intel NPU "Planetary Cortex" running OpenVINO embeddings, ensuring 0% VRAM leakage.
-   **Substrate Manifold**: A topological map of 843 logic singularities, allowing for O(1) skill selection via tensor collapse.
-   **Sovereign-Loop**: The primary runtime kernel that orchestrates the "Adaptive Heartbeat" of the organism.

---

## 🏗️ System Architecture

The repository reflects a biological "Organism" structure:

```text
ASI-OS/
├── manage.py               # Unified CLI Entry Point (Server, Local, Learn, Substrate)
├── substrate_manifold.html # Visual Interface for the 384-D Logic Topology
├── index.html              # Living Organism UI (3D Visualization)
├── src/                    # Core Source Code
│   ├── boot.py             # Runtime Kernel Entry (CortexSwitchboard)
│   ├── agents/             # Autonomous Agents (Professor, Alpha, etc.)
│   ├── core/               # System Kernel (Safety, Memory, Manifold)
│   ├── hnet/               # Hierarchical Neural Memory (NPU-accelerated)
│   └── skills/             # Skill Registry (843+ Singularities)
├── models/                 # Inference Engines (TensorRT binaries)
├── docs/                   # System Documentation
└── configs/                # Configuration Files
```

---

## 🚀 Quick Start

### 1. Installation

Ensure you have Python 3.11+ and the requisite hardware drivers (CUDA 12.x for GPU, OpenVINO for NPU).

```bash
# Clone the repository
git clone https://github.com/Cloudhabil/AGI-Server.git
cd AGI-Server

# Install dependencies
pip install -r requirements.lock
# OR
pip install .
```

### 2. Unified Management CLI

All system operations are controlled via `manage.py`.

**Start the Local ASI (Offline Mode):**
Boot the system using local intelligence only (Ollama/TensorRT), configuring the environment for full offline operation.
```bash
python manage.py local
```

**Start the Server (Sovereign-Loop):**
```bash
python manage.py server --mode Sovereign-Loop
```

**View Substrate Status:**
Check the equilibrium status of the Substrate Manifold.
```bash
python manage.py substrate
```

**Start a Learning Session:**
Initiate an autonomous learning cycle between the Professor and Alpha agents.
```bash
python manage.py learn --duration 180 --cycles 3
```

**Run Tests:**
```bash
python manage.py test
```

---

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

-   **[Architecture Overview](docs/architecture.md)**: Deep dive into the NPU/GPU split and Manifold topology.
-   **[Genesis Codex](docs/genesis_codex.md)**: The philosophical and technical foundation.
-   **[H-Net & OpenVINO](docs/hnet_openvino.md)**: Implementation details of the NPU memory system.
-   **[System Status](docs/system_status.md)**: Current operational status and metrics.

---

## 🛡️ Safety & Governance

This system is engineered with transparency and safety as foundational pillars.

-   **VRAM Safety Governor**: Enforces strict hardware limits (Critical > 85.0%) to prevent thermal/memory runaway.
-   **Rule Zero**: "Always run 'ls -R' before making claims." verification protocol.
-   **Audit Trails**: All autonomous actions are logged in `data/ledger/` for full traceability.
-   **Local Operation**: Designed for offline privacy, keeping sensitive data and proprietary skills secure.

---

## ⚖️ License

Copyright © 2026 Cloudhabil. Licensed under the Apache License, Version 2.0.
"Agents are fuel. Skills are fire. GPIA is the furnace."