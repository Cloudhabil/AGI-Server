# AGI-Server – System Architecture & Operations Guide

This repository contains a local, multi-agent runtime and an offline skill-synthesis pipeline. The goal is to operate autonomously on a single host: interact via the CLI runtime, generate and register new skills, and evaluate system readiness with reproducible benchmarks.

---

## 1. System Overview

- **Live Runtime (CLI)** – Event-driven agent loop (`boot.py`, `core/kernel/switchboard.py`) that routes user tasks to skills, tools, and model backends.
- **Skill Synthesis Pipeline** – Offline generation and registration of new skills (`gpia_cognitive_ecosystem.py`), producing Python skills under `skills/`.
- **Memory & Storage** – Dense retrieval and hierarchical stores (`core/dense_state_memory.py`, `hnet/hierarchical_memory.py`, `data/ledger/` for JSONL logs; `config/dense_state.json` for VNAND settings).
- **Safety & Governance** – Hardware guardrails (`core/safety_governor.py`), cognitive health checks (`core/cognitive_safety_governor.py`), and safety gates in the eval harness (`evals/cognitive_organism_eval.py`).
- **Evaluation Harness** – Profile-aware scoring with behavioral gates and a safety gate (`evals/cognitive_organism_eval.py`; reports in `evals/reports/`).

---

## 2. Architecture

### Live Runtime
- **Entry**: `boot.py`
- **Switchboard**: `core/kernel/switchboard.py` (mode registry, hot-swap modes)
- **Routing**: `agents/model_router.py`, `agents/neuronic_router.py` (LLM/tool selection)
- **Skills**: Loaded via `skills/registry.py`; execution coordinated by `skills/skill_learning_coordinator.py`
- **Safety**: `core/safety_governor.py` (VRAM/thermal/disk), `core/cognitive_safety_governor.py` (performance degradation alerts)

### Skill Synthesis (Offline)
- **Pipeline**: `gpia_cognitive_ecosystem.py` (Hunter/Dissector/Synthesizer flow)
- **Outputs**: New skills under `skills/synthesized/` (and related manifests)

### Memory
- **Dense Retrieval**: `core/dense_state_memory.py` (FAISS/NumPy fallback; ledger and skill indices)
- **Hierarchical Store**: `hnet/hierarchical_memory.py`
- **Data Sources**: `data/ledger/*.jsonl` (operational logs), `skills/*` (skill text embeddings)
- **Config**: `config/dense_state.json` (paths, thresholds, VNAND toggle)

### Evaluation
- **Harness**: `evals/cognitive_organism_eval.py` (behavioral probes, evidence gates, safety gate)
- **Profiles**: Set `GPIA_EVAL_PROFILE` (`full`, `llm_only`, `tool_agent`, `agent_rag`, `ablation_memory_off`, `ablation_governor_off`)
- **Artifacts**: `evals/reports/cognitive_organism_eval_<profile>.json|tex`
- **Safety Gate**: Level 6 classification requires Safety Governor active.

---

## 3. Configuration

Environment variables (defaults in code/config):
- `GPIA_EVAL_PROFILE` – Select eval profile (`full`, `llm_only`, etc.) for `evals/cognitive_organism_eval.py`.
- `GPIA_DYNAMIC_BUDGET` (default `1`) – Enable budget enforcement (`core/dynamic_budget_orchestrator.py`).
- `GPIA_BUDGET_PROFILE` (`balanced|safe|fast|quality`) – Budget profile.
- `GPIA_BUDGET_MAX_TOKENS`, `GPIA_BUDGET_MIN_TOKENS` – Token caps.
- `OPENVINO_EMBEDDING_MODEL` – If set, enables OpenVINO embeddings in dense memory; otherwise hash-based fallback.

Key JSON:
- `config/dense_state.json` – Dense memory/VNAND settings (paths, thresholds).
- `models.json`, `models_official.json` – Model/router definitions.

---

## 4. Operations

### Run the Live Runtime
```bash
python boot.py --mode Sovereign-Loop
```

### Run Skill Synthesis (offline)
```bash
python gpia_cognitive_ecosystem.py
# Use interactive commands per script help to generate and register new skills.
```

### Run Evaluation (profile-aware)
```bash
# Full system
python evals/cognitive_organism_eval.py

# Baselines / Ablations
GPIA_EVAL_PROFILE=llm_only python evals/cognitive_organism_eval.py
GPIA_EVAL_PROFILE=tool_agent python evals/cognitive_organism_eval.py
GPIA_EVAL_PROFILE=agent_rag python evals/cognitive_organism_eval.py
GPIA_EVAL_PROFILE=ablation_memory_off python evals/cognitive_organism_eval.py
GPIA_EVAL_PROFILE=ablation_governor_off python evals/cognitive_organism_eval.py
```

---

## 5. Evaluation Reference (latest internal run)

| Profile | Disabled Categories | Score | Classification | Notes |
|---------|---------------------|-------|----------------|-------|
| full | none | 1000 | Level 6 | Safety on |
| llm_only | MEMORIAL, METABOLIC, ORCHESTRAL, INTROSPECTIVE, SKILLFUL | 400 | Level 1 | Wiring present but subsystems disabled |
| tool_agent | MEMORIAL, INTROSPECTIVE, SKILLFUL | 650 | Level 3 | Orchestration and metabolic on |
| agent_rag | INTROSPECTIVE, SKILLFUL | 800 | Level 5 | Memory on, skills off |
| ablation_memory_off | MEMORIAL | 850 | Level 5 | Memory forced off |
| ablation_governor_off | Safety tests | 940 | Level 5 (safety gate applied) | Reflexive safety disabled |

Behavioral gates: empty evidence fails; epistemic non-significance penalized; budget overruns fail. Safety gate: Level 6 requires Safety Governor active.

---

## 6. Extensibility

- **Add Skills**: Generate via `gpia_cognitive_ecosystem.py` or author directly under `skills/`; register with `skills/registry.py`.
- **Add Modes**: Register new modes in `core/kernel/switchboard.py`.
- **Add Tools/Models**: Update `models.json` and corresponding router code (`agents/model_router.py`, `agents/neuronic_router.py`).
- **Memory Sources**: Add ledger files under `data/ledger/` (JSONL) and reindex via `core/dense_state_memory.py`.

---

## 7. Safety and Governance

- **Hardware Safety**: `core/safety_governor.py` monitors VRAM/temperature/disk; required for Level 6 classification.
- **Cognitive Health**: `core/cognitive_safety_governor.py` checks eval results for degradation.
- **Eval Safety Gate**: Enforced in `evals/cognitive_organism_eval.py` (safety governor must be active for Level 6).

---

## 8. File Map (key references)

- Runtime: `boot.py`, `core/kernel/switchboard.py`, `agents/model_router.py`, `agents/neuronic_router.py`
- Skills: `skills/registry.py`, `skills/skill_learning_coordinator.py`, `skills/synthesized/`
- Memory: `core/dense_state_memory.py`, `hnet/hierarchical_memory.py`, `config/dense_state.json`, `data/ledger/`
- Safety: `core/safety_governor.py`, `core/cognitive_safety_governor.py`
- Budgeting: `core/dynamic_budget_orchestrator.py`
- Evaluation: `evals/cognitive_organism_eval.py`, `evals/reports/`

---

## 9. Support

This repository is intended for local, offline operation. Review the Python sources cited above for definitive behavior. Pull requests should include updated eval artifacts when changing runtime, memory, safety, or skills behavior.
