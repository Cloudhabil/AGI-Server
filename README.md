# ASI-OS: Autonomous Artificial Superintelligence Operating System

![License: Apache 2.0](https://img.shields.org/badge/License-Apache%202.0-blue.svg)
![Python: 3.11+](https://img.shields.org/badge/Python-3.11%2B-green.svg)
![Status: Beta](https://img.shields.org/badge/Status-Beta-orange.svg)

**ASI-OS** is a self-evolving cognitive ecosystem designed to operate autonomously on local infrastructure. It features a dual-architecture system comprising a live runtime kernel (`Sovereign-Loop`) and an offline cognitive ecosystem for skill synthesis and self-improvement.

---

## 🏗️ System Architecture

The repository follows a professional `src` layout to ensure modularity and separation of concerns.

```
ASI-OS/
├── manage.py               # Unified CLI Entry Point (Server, Learn, Test)
├── src/                    # Core Source Code
│   ├── boot.py             # Runtime Kernel Entry
│   ├── agents/             # Autonomous Agents (Professor, Alpha, etc.)
│   ├── core/               # System Kernel (Switchboard, Safety, Memory)
│   ├── gpia/               # General Purpose Intelligent Agent Logic
│   ├── hnet/               # Hierarchical Neural Memory
│   └── skills/             # Skill Registry (Proprietary implementations ignored)
├── scripts/                # Operational & Maintenance Scripts
├── tests/                  # Test Suite (pytest)
├── docs/                   # System Documentation
└── configs/                # Configuration Files
```

---

## 🚀 Quick Start

### 1. Installation

Ensure you have Python 3.11+ installed.

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

**Start the Server:**
```bash
python manage.py server --mode Sovereign-Loop
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

**Clean Artifacts:**
```bash
python manage.py clean
```

---

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- **[Architecture Overview](docs/genesis_codex.md)**: Deep dive into the system's core philosophy and design.
- **[Gardener Guide](docs/gardener_readme.md)**: Understanding the autonomous filesystem organizer.
- **[Agents Manifest](docs/agents_manifest.md)**: capabilities of the multi-agent swarm.
- **[System Status](docs/system_status.md)**: Current operational status and metrics.

---

## 🛡️ Safety & Governance (EU AI Act Alignment)

This system is engineered with transparency and safety as foundational pillars.

- **Safety Governor**: Hardware and cognitive guardrails are enforced by `src/core/safety_governor.py`.
- **Audit Trails**: All autonomous actions are logged in `data/ledger/` for full traceability.
- **Human Oversight**: The `manage.py` CLI ensures human-in-the-loop control for all critical operations.
- **Local Operation**: Designed for offline privacy, keeping sensitive data and proprietary skills secure.

---

## 🧩 Extensibility

- **Skills**: Add new capabilities in `src/skills/`. The loader will automatically register them.
- **Agents**: Define new agent behaviors in `src/agents/`.
- **Scripts**: Place operational tasks in `scripts/` and use the standardized import block to access `src/`.

---

## ⚖️ License

Copyright © 2026 Cloudhabil. Licensed under the Apache License, Version 2.0.
"Made for a better world."