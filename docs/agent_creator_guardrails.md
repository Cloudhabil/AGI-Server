# Agent Creator Guardrails

This document defines the governance contract for provisioning agents.

## Policy Scopes

- **manual**: direct user/ops provisioning (default).
- **transpiler**: Skill → Agent compilation (stricter guardrails).
- **runtime**: in-memory registration for live agents (metadata-only).

## Source of Truth

- `config/agent_creator_guardrails.json`

## Enforcement Points

1) **Creator Manager intake**  
   Applies quotas, approval gates, allowlists, TTL/expiry, and spawn-depth limits.

2) **Transpiler provision**  
   Uses `policy_scope=transpiler`, which enforces approvals, forced ephemeral mode,
   stricter quotas, and allowlisted categories.

3) **Agent runner execution**  
   Executes only explicit plan operations and validates post-step state.

## Guardrail Signals

Each provisioning attempt is recorded to:

- `data/gpia/agents/agent_creator_audit.jsonl`

The log includes:
- decision: `allowed` | `blocked`
- policy_scope
- session_id
- requester_id / requester_type
- errors (if any)
- adjustments (caps, forced ephemeral, etc.)

## Minimum Alignment Guarantees

- No provisioning without required approvals (transpiler).
- Category allowlist enforced for transpiler.
- Max agents per session/hour enforced by policy.
- Spawn depth capped for transpiler.
- All requests audited with timestamps and decisions.

## Living Messenger Notes

- Use `agent_template=living_messenger` for a persistent loop runner.
- Stop condition: workspace `stop.signal` file or TTL expiry.
- Heartbeat log: `logs/messenger_heartbeat.jsonl`.
