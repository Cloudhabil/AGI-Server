# Release Notes (Post v0.2.0 → v0.5.0)

## What’s New
- **Hardware Sovereignty (Substrate Equilibrium v0.5.0)**
  - Enforced VRAM ceiling at 9,750 MB (~79% of 12 GB) to prevent DWM/driver contention.
  - Embeddings locked to NPU for PCIe offload; status via `manage.py substrate`.
  - Default local run supports `--substrate-equilibrium` to auto-apply safe limits.
- **Cognitive Safety Gate**
  - ImmuneValidator integrated as mandatory middleware in the cognitive pipeline.
- **Skill Expansion**
  - Added model search/orchestration skill `src/skills/integration/demodelis_ganesha` (underscore path is canonical).
- **Benchmarks & Validation**
  - `benchmarks/collision_test.py` + `docs/substrate_collision_test.md` to measure LLM TPS under embedding load (contention vs equilibrium).
  - Expected: <10% TPS variance during equilibrium runs.
- **Docs & Licensing**
  - Clarified dual licensing: Apache 2.0 + Cloudhabil Skills Additional License (CSAL).
  - README/CHANGELOG and eval docs updated for current structure and safety posture.
- **Maintenance & Security**
  - Dependency bumps across pip/npm (requests, jinja2, js-yaml, vite, etc.).
  - Hygiene fixes in model routing/runtime to respect new resource ceilings.

## Upgrade Notes
- Preferred local run: `python manage.py local --substrate-equilibrium`.
- Verify hardware routing: `python manage.py substrate`.
- Run collision test in both modes and confirm TPS drop <10% under equilibrium:
  - `python benchmarks/collision_test.py --embedding-count 1000 --duration 30 --embedding-delay 5 --model gpia_core`.

## Compliance & Auditability
- No manifold HTML scaffold included (prior scaffold reverted).
- Skills: underscore path is canonical; hyphenated demodelis path not used.
- ImmuneValidator enforces pre-execution checks across the cognitive pipeline.

## Scope
- Changes listed are post-`v0.2.0` and present on `main`.
- No API-breaking changes; reinstall/refresh dependencies recommended.
- Data/config files are unchanged by this release tag; hardware limits are applied at runtime via CLI/env.
