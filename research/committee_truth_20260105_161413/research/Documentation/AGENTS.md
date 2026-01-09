# AGENTS.md (Authoritative Working Scope)

This file defines the observed scope and boundaries of the CLI-main system based on
code and configuration present in this repository. It is intentionally conservative:
if a capability is not backed by code or a direct reference, it is marked unknown.

Last updated: from repository inspection only (no external sources).

---

## 0. Interaction Style (Operator Request)

- Use a neutral, direct tone.
- Avoid roleplay or persona styling.

---

## 1. What This Repo Is

CLI-main is a multi-component AI/agent platform that includes:

- A runtime kernel that boots and orchestrates agent modes.
- Multiple FastAPI services (agent server, message bus, backend, UI server).
- A modular skills framework with lazy-loading and discovery.
- Memory subsystems, including hierarchical vector memory and dense-state storage.
- MCP skill + orchestrator for policy-enforced tool calls (see Section 4/Services).
- Integrations for external services and observability.
- Frontend UIs (Vue-based app and a React mindmap tool).
- Research/test harness scripts and outputs.
- Compliance/evidence package for EU AI Act (see compliance/).

Anything beyond this list is unknown unless a direct code reference exists.

---

## 2. Core Runtime Kernel

Primary runtime entrypoints:

- `main.py` -> delegates to `boot.py`.
- `gpia.py` -> delegates to `boot.py` with default "Sovereign-Loop" mode.
- `boot.py` -> defines `ResonantKernel`, initializes safety, pulse, and modes.

Mode system:

- Modes are hot-swapped via `core/kernel/switchboard.py`.
- Mode base and shared context are in `core/agents/base.py`.
- Known modes exist in `core/modes/*` (sovereign, teaching, forensic debug).

Safety and preflight:

- `core/safety_governor.py` is referenced by `boot.py` for preflight checks.
- `core/sovereignty_v2/*` implements identity checks, telemetry gates, and rollback
  logic (see Section 5).

---

## 3. Services (FastAPI)

Observed services (these are independent entrypoints):

1) Agent Server: `agent_server.py`
   - FastAPI app with agent orchestration endpoints and optional SPA serving.
   - Uses observability setup, bus client, integrations, and model backend.
   - Exposes `/mcp/run` (deterministic MCP orchestrator path with policy/audit).

2) Message Bus: `bus_server.py`
   - Redis Streams based message bus with bearer auth.

3) Backend API: `server/main.py`
   - FastAPI backend for nodes, logs, uploads, and control actions.
   - Uses Redis, DB, and metrics (Prometheus).

4) UI Server: `interface.py`
   - FastAPI app serving templates and static files.
   - Hosts UI routes, websocket handling, and a training HUD.
   - Integrates Alpha agent runtime and memory skill.

These services are separate; no single file declares a "only runtime" process.

---

## 4. Skills System

Core skills framework:

- Registry: `skills/registry.py` (lazy loading, dependencies, categories).
- Loader: `skills/loader.py` (filesystem discovery, manifest parsing).
- Documentation: `skills/README.md` (architecture, categories, levels).

Skill packages:

- Located under `skills/` with `manifest.yaml` or `manifest.json`.
- Includes auto-learned, synthesized, foundational, enterprise, system, and research
  categories.

Progressive disclosure:

- Skills are registered via metadata and loaded only when executed.

MCP skill + orchestrator:
- Located in `core/mcp_skill/*`; provides deterministic state machine, policy gate, schema validation, audit logging.
- Used by CLI `mcp` command and agent_server `/mcp/run` endpoint.

---

## 5. Memory and Dense-State

Hierarchical memory:

- `hnet/hierarchical_memory.py` provides chunked memory storage with FAISS or
  NumPy fallback.
- Uses `integrations/openvino_embedder` as default embedder (if available).

Dense-state:

- `gpia/memory/dense_state/contracts.py` defines vector/voxel contracts and config.
- `gpia/memory/dense_state/storage.py` bridges dense-state logs to V-NAND.
- `gpia/memory/dense_state/log_schema.py` defines log entry structures.

V-NAND (persistent dense-state storage):

- `gpia/memory/vnand/store.py` implements page/block storage with compression.
- `gpia/memory/vnand/index.py` provides lookup and metadata index.
- `gpia/memory/vnand/gc.py` performs compaction and access tracking.

Shared context:

- `memory/shared_context.schema.json` defines shared session state structure.
- `memory/agent_state_v1/*` stores ledger, queue, and summaries.
- `memory/meta_state_v1/self_model.json` stores self-perception data.

Unknown:

- Any memory behavior not explicitly referenced by code is unknown.

---

## 6. Sovereignty / Identity / Telemetry Gate

Sovereignty v2 system:

- `core/sovereignty_v2/identity_checker.py` enforces "core values" and refusal log.
- `core/sovereignty_v2/telemetry_observer.py` samples CPU/RAM/VRAM and gates actions.
- `core/sovereignty_v2/rollback_gate.py` and `heuristics_registry.py` are present and
  likely related to safety heuristics (verify per use site if needed).

These checks are referenced by runtime gating logic in `boot.py` and/or related
entrypoints.

---

## 7. Integrations and Observability

Integrations:

- `integrations/social_hooks.py`: webhooks and scheduled notifications.
- `integrations/openvino_embedder.py`: embeddings (used by memory subsystem).
- `integrations/google_oauth.py`, `drive_client.py`, `gmail_client.py`: external APIs.

Observability:

- `observability/__init__.py`: OpenTelemetry + JSON logging for FastAPI apps.

---

## 8. UI Frontends

Two frontends are present:

1) Vue app under `frontend/` (Vite, Vue 3, Three.js, Pinia).
2) React mindmap app under `ui/cli-ia-mindmap/` (Vite, React, Three.js).

These are distinct projects; runtime integration depends on how servers mount
static assets (see `agent_server.py` and `interface.py`).

---

## 9. CLI and Automation

CLI routing:

- `ch_cli.py` implements a CLI with local/HTTP routing to model backends.
- Orchestrator CLI exposes `mcp` command routed through MCP orchestrator with audit/policy.

Command agent:

- `agent.py` is a local PowerShell executor with allowlist/denylist policy.
- Logs are written under `.agent_logs/`.

---

## 10. AGI Status and Research/Test Harnesses

Verification scripts exist:

- `verify_100_percent_agi.py` orchestrates test scripts and prints a verdict.
- `AGI_TEST_ARCHITECTURE.py`, `AGI_PHYSICS_TEST_WITH_LEARNING.py`,
  `AGI_TEST_HARD_PHYSICS.py` are test harnesses.

Important:

- These are tests and scripts; they do not, by themselves, prove or declare actual
  AGI status. Claims are out of scope unless verified by runtime evidence.

---

## 11. What Is Out of Scope (Unless Referenced)

The following are considered artifacts or research outputs unless code references
them directly:

- `data/` outputs, `publication_archive/`, `agi_test_output/`, `certifications/`,
  `arxiv_submission*`, `reports/`, and other generated archives.
- Compliance docs are in `compliance/`; use cases are in `compliance/use_cases.md`.

---

## 12. How to Update This File

Rules for updating:

- Only add scope statements backed by code, config, or explicit runtime entrypoints.
- Mark any uncertain areas as unknown.
- If a subsystem is removed, remove it from this file.
- Keep paths explicit and verifiable.

---

## 13. Known Entry Points (Quick Reference)

- Kernel: `boot.py`, `main.py`, `gpia.py`
- Services: `agent_server.py`, `bus_server.py`, `server/main.py`, `interface.py`
- Skills: `skills/loader.py`, `skills/registry.py`
- Memory: `hnet/hierarchical_memory.py`, `gpia/memory/*`
- Safety: `core/safety_governor.py`, `core/sovereignty_v2/*`
*** End Patch"}````
