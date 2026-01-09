# Data Governance (Draft)

Status: owner-filled policy for default deployment; adjust if deployment differs.

## Scope
- Runtime data: user inputs/commands, tool arguments/outputs, MCP audits, dense-state logs.
- Stored locations (repo defaults):
  - MCP audit: `memory/agent_state_v1/mcp_orchestrator_audit.jsonl`, `memory/agent_state_v1/mcp_audit.jsonl`
  - Dense-state/VNAND: `data/vnand`, `memory/agent_state_v1`
  - Compliance evidence: `compliance/evidence/`
  - Logs: `logs/`, `memory/agent_state_v1/ledger.json`, `reflexes/governance/status.json`

## PII Handling
- Default stance: block PII in MCP tool arguments and agent inputs unless a lawful basis is documented.
- Redaction: operators must redact names/emails/IDs/secrets before tool calls; automated redaction not provided.
- If PII is processed, record lawful basis and retention; otherwise reject.

## Provenance
- MCP tool calls should record provenance via MCP skill orchestrator; ensure tool outputs include source metadata where possible.
- If ingesting external data (APIs/files), log source and time in audit.

## Retention / Deletion
- MCP audit logs: retain 30 days, then rotate/purge.
- Dense-state data: retain 30 days for ops; purge older unless explicitly required.
- Compliance evidence: retain as required for audits (default 1 year); rotate logs monthly.
- Adjust if legal/contractual requirements differ.

## Access Control
- Limit write/read of `memory/` and `data/` to authorized operators.
- Store secrets (tokens) in environment vars; avoid committing to repo.

## Owner Actions Needed
- If deployment requires PII, document lawful basis and specific retention overrides.
- Confirm retention windows fit operational/legal needs.
- Document access control and backup/restore for compliance evidence and logs.
