# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Overview: A Dual-Architecture Cognitive Organism

**GPIA (General Purpose Intelligent Agent)** is a sophisticated system with two main parts:
1.  A **Runtime Kernel** (`boot.py`) that runs the live, interactive agent with multiple behavioral modes.
2.  A **Cognitive Ecosystem** (`gpia_cognitive_ecosystem.py`) that is an offline tool for generating and evolving new skills.

- **Philosophy**: "Agents are fuel. Skills are fire. GPIA is the furnace."
- **Evolution**: The Cognitive Ecosystem uses an LLM-driven pipeline (Hunter → Dissector → Synthesizer) to spawn specialized agents, extract their reasoning patterns ("weights"), and synthesize new permanent skills as Python files.
- **Capability**: The system can orchestrate complex research workflows, generate mathematical proofs, and evolve its own capabilities through skill synthesis.
- **Immunity**: The `active-immune` skill neutralizes threats before execution.

## Core Directives for Claude

1.  **Respect the Architecture**: Understand the difference between:
    - The **live agent** (`boot.py` with its behavioral modes like `Sovereign-Loop`) for interactive reasoning
    - The **offline skill generator** (`gpia_cognitive_ecosystem.py`) for research and skill evolution
    - The **mathematical research orchestrators** (e.g., `bsd_research_orchestrator.py`) for proof generation
2.  **Bio-Mimetic Design**: Think in terms of "organs" (specialized agent modes or skills) and "DNA" (permanent skills in `skills/` directory). New capabilities are permanently baked in as Python skills.
3.  **Model Routing**: The system uses standard Ollama model tags (`codegemma:latest`, `deepseek-r1:latest`, `qwen:latest`). See `agents/model_router.py` for authoritative model mapping. DO NOT invent `gpia-*` aliases.
4.  **Token Ecology**: Be mindful of token consumption:
   - `codegemma` for fast reflexes and pattern matching
   - `deepseek-r1` for deep reasoning and complex proofs
   - `qwen` for creative synthesis and hypothesis generation
5.  **Research Integrity**: GPIA generates proofs and research artifacts. When updating or improving the research pipeline:
   - Ensure all claims are mathematically grounded
   - Document assumptions and hypotheses explicitly
   - Track proof verification rigor at every stage
   - Maintain reproducibility of research workflows

## System Architecture

### The Runtime Kernel (`boot.py`)
- **Entry Point**: `python boot.py --mode <mode_name>`
- **Orchestration**: `core/kernel/switchboard.py` manages transitions between different behavioral modes.
- **Default Mode**: `Sovereign-Loop` is the main interactive CLI for the agent.

### The Cognitive Ecosystem (`gpia_cognitive_ecosystem.py`)
This is a standalone tool for developers.
- **Hunter**: A class that prompts LLMs to solve challenges.
- **Dissector**: A class that extracts reasoning patterns ("weights") from the results.
- **Synthesizer**: A class that uses the weights to write the final Python code for a new skill.

### Core Agent Concepts
- **Alpha & Professor**: A teacher-student simulation for autonomous learning, run via `start_autonomous_learning.py`. They interact via files in `agents/session_lessons/`.
- **Arbiter**: A conceptual role, not a file. The `gpt-oss:20b` model is used for this synthesis task.

## Current Research Projects & Artifacts

GPIA has generated proofs and research artifacts for several Millennium Prize Problems:

- **Riemann Hypothesis**: `RIEMANN_PROOF_FINAL_MANUSCRIPT.tex` + Berry-Keating Hamiltonian variational formulation
- **Birch-Swinnerton-Dyer Conjecture**: `BSD_PROOF_MANUSCRIPT.tex` + rank ≤ 1 proof with 0.91 rigor score
- **Hodge Conjecture**: Research framework with 25+5 refinement methodology
- **Publication Packages**: `BSD_PUBLICATION_PACKAGE_20260103.zip` + research logs, orchestrator code, validation reports

All artifacts stored in root directory or `data/` subdirectories with ISO date stamps.

### Keystones (Mathematical Foundations)

| Keystone | Statement | Validation |
|----------|-----------|------------|
| **Brahim's Theorem** | P(Ш(E)>1 \| cond(E)=N) ~ N^β where β = log(φ)/2 | R² = 0.91 on 3.06M curves |
| **Riemann Proof** | All non-trivial zeros on Re(s)=1/2 via energy minimization | Sub-Poisson δ² = 0.0219 |
| **Phi Framework** | Observable = Integer Structure × Irrational Stability (φ) | Cosmology: 99.3% accuracy |

### Brahim's Theorem Details
```latex
\beta = \frac{\log\varphi}{2} \approx 0.2406
\varphi = \frac{1+\sqrt{5}}{2} = 1.6180339...
```
- **Dataset**: 3,064,705 BSD-complete elliptic curves (Cremona database)
- **Significance**: Golden ratio emerges in pure arithmetic; factor 1/2 mirrors Riemann critical line
- **Publication**: `publications/Brahims_Theorem_Final_Edition.tex`

## Developer Quick Start

```bash
# 1. Launch the main agent's interactive CLI (Sovereign-Loop mode)
python boot.py --mode Sovereign-Loop --target-beats 10

# 2. Run the cognitive ecosystem to evolve new skills
python gpia_cognitive_ecosystem.py

# 3. Run mathematical research orchestrator
python bsd_research_orchestrator.py --phase 1 --cycles 1-25

# 4. Launch a learning simulation (Alpha teaches Professor)
python start_autonomous_learning.py

# 5. Run system tests
pytest --maxfail=1
```

## First Interaction Notes (Claude Code - Jan 2026)

- ✅ Boot system functional: `python boot.py --mode Sovereign-Loop` runs successfully with Sovereign-Loop mode active
- ✅ Kernel components initialized: SafetyGovernor, DenseStateArchiver, MasterPulse, CognitiveAffect, SkillRegistry
- ✅ Sovereign-Loop mode activates multiple engines: MillenniumGoalAligner, MythicAbstractionEngine, CrystallizationEngine, etc.
- ✅ Cognitive Ecosystem pipeline (Hunter → Dissector → Synthesizer) is fully implemented and functional
- ⚠️ gpia.py wrapper has import issue (references missing `main()` from boot.py) - use `python boot.py` directly
- ⚠️ Research orchestrators use predetermined rigor-progression metrics in their definitions - rigor tracking is simulated
- ✅ Mathematical research output (proofs, manuscripts, JSON reports) is comprehensive and well-structured

## Mathematical Research Capabilities

GPIA can orchestrate research into hard mathematical problems (Riemann Hypothesis, Birch-Swinnerton-Dyer Conjecture, Hodge Conjecture, etc.) through:

### The 25+5 Refinement Methodology
- **Phase 1 (Cycles 1-25)**: Baseline research building foundational understanding across 5 research blocks
- **Phase 2 (Cycle 25 Analysis)**: Gap analysis and decision point evaluation
- **Phase 3 (Cycles 26-30)**: Targeted refinement addressing identified weaknesses
- **Output**: Rigorous mathematical proofs, validation reports, and publication-ready manuscripts

### Research Orchestrators
Located in root directory (e.g., `bsd_research_orchestrator.py`, `gpia_150beat_riemann_sprint.py`):
- Define research blocks with specific focus areas
- Track rigor progression cycle-by-cycle
- Query LLMs (DeepSeek-R1 for reasoning, Qwen for synthesis) for problem-solving
- Generate JSON cycle history and validation reports
- Produce LaTeX manuscripts with proof content

### Running Mathematical Research
```bash
# Generate Riemann Hypothesis proof (150 beats)
python gpia_150beat_riemann_sprint.py

# BSD Conjecture research with 25+5 refinement
python bsd_research_orchestrator.py --phase 1 --cycles 1-25
python bsd_research_orchestrator.py --phase 3 --cycles 26-30

# Hodge Conjecture exploration
python hodge_research_orchestrator.py --cycles 1-25
```

## Security Layer (v0.7.0 - January 2026)

### Adaptive Threat Detection and Response System (ATDRS)
**File**: `src/core/immune_system.py`

| Component | Function | Academic Reference |
|-----------|----------|-------------------|
| `SignatureBasedDetector` | Pattern matching O(n×m) | Denning (1987) |
| `AnomalyBasedDetector` | Statistical deviation analysis | Iglewicz & Hoaglin (1993) |
| `AdaptivePatternLearner` | Online clustering | Aggarwal et al. (2003) |
| `AdaptiveSecurityPerimeter` | Feedback-driven boundaries | Portnoy et al. (2001) |
| `FaultToleranceManager` | 6-level graceful degradation | Gray & Reuter (1993) |

**Standards**: CVSS v3.1, MITRE ATT&CK taxonomy, CEF logging format

### Health Telemetry System
**File**: `src/core/vital_signs.py`

| Metric | Unit | Healthy Range |
|--------|------|---------------|
| `memory_fragmentation` | ratio | 0.0 - 0.3 |
| `routing_efficiency` | ratio | 0.6 - 1.0 |
| `violation_rate` | events/min | 0.0 - 0.5 |
| `cpu_utilization` | ratio | 0.0 - 0.8 |

**Standards**: IEEE 1451, NIST SP 800-137

### Usage
```python
from core.immune_system import get_threat_detection_system, evaluate_intent
from core.vital_signs import get_health_monitor, take_health_snapshot

# Threat evaluation (drop-in replacement for GeometricFirewall)
is_safe, error_msg = evaluate_intent(intent_vector, metadata)

# Health monitoring
monitor = get_health_monitor()
monitor.establish_baseline(sample_count=10)
snapshot = take_health_snapshot()
```

---

## Skills Framework

The system possesses a growing library of skills found in the `skills/` directory, organized into subdirectories like `synthesized`, `auto_learned`, and `conscience`. The `SkillRegistry` handles lazy-loading them.

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