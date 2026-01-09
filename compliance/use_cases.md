# Use-Case Inventory (Repo Evidence)

Status: draft; based on code/docs in this repo. Add any deployment-specific cases if missing.

| Use Case | Description | Risk Tier (EU AI Act) | Rationale |
| --- | --- | --- | --- |
| GPIA runtime agent (Sovereign Loop/Teaching/Forensic modes) | Interactive LLM-based agent with skill routing and dense-state logging | GPAI/LLM | General-purpose LLM system (Article 52/53 obligations), no Annex III high-risk function identified in repo |
| MCP tool orchestration (CLI + Sovereign `mcp` command + agent_server `/mcp/run`) | Policy/audit-enforced tool invocation via MCP orchestrator | GPAI/LLM | General-purpose LLM service exposing tools; no Annex III high-risk function identified |
| Agent server + bus orchestration | FastAPI agent endpoints and Redis bus messaging between agents | GPAI/LLM service | General-purpose messaging/coordination; no Annex III high-risk function identified |
| Model evidence package (checkpointing/validation) | Training/optimization evidence for GPAI model | GPAI/LLM technical documentation | Technical file artifacts for GPAI compliance |
| Skill framework / cognitive ecosystem | Skill registry, auto-learned/synthesized skills, evolutionary loop | GPAI/LLM | General-purpose capability growth; no Annex III high-risk function identified |
| Autonomous skill evolution / dense-state learning | Dense-state/VNAND logging and auto-learned skill generation | GPAI/LLM | Internal capability evolution; no Annex III high-risk function identified |

Not observed in repo (must be added if present in deployment):
- Annex III high-risk uses (biometric ID, credit scoring, employment/education selection, migration/justice, critical infrastructure, etc.).
- Prohibited uses.

Next actions:
- Confirm or amend tiers if deployment includes high-risk/prohibited scenarios.
- Link each use case to oversight/data governance/monitoring procedures.
