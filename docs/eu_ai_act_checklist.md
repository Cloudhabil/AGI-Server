# EU AI Act Compliance Checklist (Repo-Aligned)

Use this to track what is already in the repo and what still needs owner confirmation.

## 1) Use-Case Classification (provisional — needs owner confirmation)
- GPIA runtime agent + modes (Sovereign Loop, Teaching, Forensic): GPAI/LLM.
- MCP tool orchestration (CLI and Sovereign mode `mcp` command): GPAI/LLM service.
- Agent/bus servers (FastAPI + bus orchestration): GPAI/LLM service.
- Model training/evidence package (checkpointing, validation): GPAI/LLM (technical file).
- No explicit high-risk or prohibited use cases identified in repo content.

## 2) Control Mapping (per above use cases)
- Logging & audit: MCP orchestrator writes to `memory/agent_state_v1/mcp_orchestrator_audit.jsonl` and MCP skill audit; bus/agent logs also exist. Status: present for MCP; confirm coverage for other agents.
- Transparency notice/model card: `compliance/model_card.md` (filled with defaults; update if training data/custom models used).
- Data governance: `compliance/data_governance.md` (PII blocked by default; retention defaults set).
- Human oversight: `compliance/oversight.md` (roles/rollback filled with defaults).
- Robustness/evals: `compliance/generate_validation_metrics.py` and evidence JSONs. Status: present for model eval; broader system evals still not documented.
- Post-market monitoring: `compliance/post_market_monitoring.md` (defaults set; align channels/thresholds if needed).
- Technical documentation: `compliance/COMPLIANCE_COVER_LETTER.md`, `model_architecture.py`, checkpointing verification, validation metrics. Status: present for GPAI tech file.
- Kill switch / disable: MCP orchestrator honors `MCP_DISABLE_TOOLS` env or `memory/agent_state_v1/mcp_disabled.flag`; agent_server exposes `/mcp/disable` and `/mcp/enable`.
- Risk tiers: MCP orchestrator enforces allowed tiers via `MCP_ALLOWED_RISK_TIERS` (default low/medium/high), blocks otherwise.

## 3) MCP Enforcement (action boundary)
- All demo CLI `mcp` calls route through MCP orchestrator (policy + audit). Audit file: `memory/agent_state_v1/mcp_orchestrator_audit.jsonl`.
- Policy decisions recorded with trace id; verification/commit outcomes recorded with trace id.
- Agent server now exposes `/mcp/run` endpoint using MCP orchestrator (deterministic demo wiring).
- Bus server only transports messages; no tool calls. If tools are invoked via bus consumers, route them through MCP.

## 4) Transparency & Documentation
- Technical evidence: `compliance/COMPLIANCE_COVER_LETTER.md`, `model_architecture.py`, `checkpointing_verification.py`, `generate_validation_metrics.py`, evidence JSONs under `compliance/evidence/`.
- Model card / user-facing transparency notice: draft at `compliance/model_card.md`.
- Data sources/copyright: draft at `compliance/data_sources.md` (needs actual sources/licenses).

## 5) Robustness / Evaluation
- Available: `compliance/generate_validation_metrics.py` and generated JSONs.
- Missing: use-case-specific robustness tests for MCP/tool orchestration and agent workflows.

## 6) Human Oversight
- Manual gates exist in MCP policy (requires manual approval token for risky ops).
- Roles/rollback documented in `compliance/oversight.md` (defaults; adjust if needed).

## 7) Post-Market Monitoring
- Defaults set in `compliance/post_market_monitoring.md` (thresholds/channels configurable).

## 8) Open Gaps and Owners (fill in)
- Use-case inventory confirmation (owner: ___)
- Update model card/data sources if custom training/finetuning or new models (owner: ___)
- Confirm data governance/PII stance fits deployment (owner: ___)
- Confirm oversight roles/rollback align with org (owner: ___)
- Align monitoring thresholds/channels with ops (owner: ___)
- Confirm all tool paths route through MCP (owner: ___)
