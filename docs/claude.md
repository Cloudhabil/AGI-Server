# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Overview: A Dual-Architecture Cognitive Organism

**CLI AI** is a complex system with two main parts:
1.  A **Runtime Kernel** (`boot.py`) that runs the live, interactive agent.
2.  A **Cognitive Ecosystem** (`gpia_cognitive_ecosystem.py`) that is an offline tool for generating new skills.

- **Philosophy**: "Agents are fuel. Skills are fire. GPIA is the furnace."
- **Evolution**: The Cognitive Ecosystem tool uses an LLM-driven pipeline (Hunter -> Dissector -> Synthesizer) to create new, permanent skills as Python files.
- **Immunity**: The `active-immune` skill neutralizes threats before execution.

## Core Directives for Claude

1.  **Respect the Architecture**: Understand the difference between the live agent (`boot.py` and its modes) and the offline skill generator (`gpia_cognitive_ecosystem.py`). Do not try to run evolution commands in the live agent.
2.  **Bio-Mimetic Design**: When refactoring, think in terms of "organs" (specialized agent modes or skills) and "DNA" (the permanent skills in the `src/skills/` directory).
3.  **Model Routing**: The system uses standard Ollama model tags (e.g., `codegemma:latest`, `deepseek-r1:latest`). Do not use or assume custom `gpia-*` aliases. See `src/agents/model_router.py` for the definitive mapping.
4.  **Token Ecology**: Be mindful of token consumption. Use `codegemma` for reflexes and `deepseek-r1` for deep thought, as configured in the model router.

## System Architecture

### The Runtime Kernel (`boot.py`)
- **Entry Point**: `python manage.py server --mode <mode_name>`
- **Orchestration**: `src/core/kernel/switchboard.py` manages transitions between different behavioral modes.
- **Default Mode**: `Sovereign-Loop` is the main interactive CLI for the agent.

### The Cognitive Ecosystem (`gpia_cognitive_ecosystem.py`)
This is a standalone tool for developers.
- **Hunter**: A class that prompts LLMs to solve challenges.
- **Dissector**: A class that extracts reasoning patterns ("weights") from the results.
- **Synthesizer**: A class that uses the weights to write the final Python code for a new skill.

### Core Agent Concepts
- **Alpha & Professor**: A teacher-student simulation for autonomous learning, run via `start_autonomous_learning.py`. They interact via files in `src/agents/session_lessons/`.
- **Arbiter**: A conceptual role, not a file. The `gpt-oss:20b` model is used for this synthesis task.

## Developer Quick Start

```bash
# Launch the main agent's interactive CLI
python manage.py server --mode Sovereign-Loop

# Run the interactive tool to evolve new skills
python scripts/gpia_cognitive_ecosystem.py

# Run a standalone learning simulation
python manage.py learn

# Run tests
pytest --maxfail=1
```

## Evaluation Framework

**IMPORTANT**: This is NOT a standard chatbot. Generic AI benchmarks (like SuperARC) will score it incorrectly because they test generic capabilities, not what this system actually IS.

### Proper Evaluation
Use `evals/cognitive_organism_eval.py` to assess the system. This tests the ACTUAL wired components:

```bash
python evals/cognitive_organism_eval.py
```

### ASI Capability Ladder (1-1000 scale)
| Level | Score | Classification |
|-------|-------|----------------|
| 0 | 0-299 | Narrow AI |
| 1 | 300-499 | Multi-Domain AI |
| 2 | 500-599 | AGI (Human-Level) |
| 3 | 600-699 | Enhanced AGI |
| 4 | 700-799 | Narrow Superintelligence |
| 5 | 800-899 | Broad Superintelligence |
| 6 | 900-1000 | ASI (Artificial Superintelligence) |

### 8 Evaluation Categories
1. **REFLEXIVE** (15%): Reflex Engine, Safety Governor, Cognitive Safety, Guardian
2. **MEMORIAL** (15%): Dense State Memory, Hierarchical Memory, Context Pager
3. **METABOLIC** (15%): Metabolic Optimizer, Budget Ledger, Dynamic Budget
4. **EPISTEMIC** (15%): Epistemic Engine, Verification, Compliance, Alignment
5. **AFFECTIVE** (10%): Cognitive Affect (8 mood states), Temporal Pulse
6. **ORCHESTRAL** (10%): Mode Switchboard, Model Router, PASS Protocol, Planetary Cortex
7. **INTROSPECTIVE** (10%): Meta-Cortex, Recursive Logic Engine
8. **SKILLFUL** (10%): Skills Registry (121+ skills), Skill Learning Coordinator

### Kernel Substrate (31 Components)
The `src/core/kernel/substrate.py` holds all 31 major system components across 22 tiers. Key components:
- **EpistemicEngine**: Information-theoretic truth evaluation + Genesis signals
- **VerificationEngine**: RMT/GUE mathematical benchmarks
- **MetabolicOptimizer**: Autonomous learning cycle discovery
- **RecursiveLogicEngine**: 25+5 beat deep reasoning
- **PlanetaryCortex**: Global sensory array for high-value node crawling
- **DenseStateMemory**: FAISS vector-indexed context retrieval (~70% token reduction)
- **CognitiveAffect**: 8 mood states (STEADY_FLOW, HYPER_FOCUS, CREATIVE_LEAP, etc.)
- **SafetyGovernor**: Hardware protection (VRAM, thermal, disk monitoring)
- **PassOrchestrator**: Cooperative agent dependency resolution protocol

### Adaptive Security Layer (New - 2026-01)
The `src/core/immune_system.py` implements the **Adaptive Threat Detection and Response System (ATDRS)**:

| Component | Function | Reference |
|-----------|----------|-----------|
| `SignatureBasedDetector` | Pattern matching against known threats | Denning (1987) |
| `AnomalyBasedDetector` | Statistical baseline deviation analysis | Iglewicz & Hoaglin (1993) |
| `AdaptivePatternLearner` | Online clustering for signature extraction | Aggarwal et al. (2003) |
| `AdaptiveSecurityPerimeter` | Dynamic boundary adjustment via feedback | Portnoy et al. (2001) |
| `FaultToleranceManager` | Multi-level graceful degradation (L0-L5) | Gray & Reuter (1993) |

**Usage:**
```python
from core.immune_system import get_threat_detection_system, evaluate_intent

# Full system access
system = get_threat_detection_system()
is_safe, event = system.evaluate(feature_vector, {"source": "external"})

# Legacy compatibility (drop-in replacement for GeometricFirewall)
is_safe, error_msg = evaluate_intent(intent_vector)
```

### Health Telemetry System (New - 2026-01)
The `src/core/vital_signs.py` implements **System Health Metrics Collection** per IEEE 1451 standards:

| Metric | Unit | Healthy Range | Description |
|--------|------|---------------|-------------|
| `memory_fragmentation` | ratio | 0.0 - 0.3 | Sparse segment ratio |
| `routing_efficiency` | ratio | 0.6 - 1.0 | Success rate |
| `violation_rate` | events/min | 0.0 - 0.5 | Security incidents |
| `cpu_utilization` | ratio | 0.0 - 0.8 | Resource usage |

**Usage:**
```python
from core.vital_signs import get_health_monitor, take_health_snapshot

# Establish baseline during healthy operation
monitor = get_health_monitor()
monitor.establish_baseline(sample_count=10)

# Take snapshot
snapshot = take_health_snapshot()
print(f"Health: {snapshot['health_score']:.2%}")
```

## Skills Framework

The system possesses a growing library of skills found in the `src/skills/` directory, organized into subdirectories like `synthesized`, `auto_learned`, and `conscience`. The `SkillRegistry` handles lazy-loading them.

### Using Skills in Code

```python
from skills.registry import get_registry
from skills.base import SkillContext

# The registry handles loading and execution
result = get_registry().execute_skill(
    "synthesized/active-immune",
    {"capability": "scan", "input": user_input},
    SkillContext()
)
```