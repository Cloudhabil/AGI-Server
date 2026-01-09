# Human Oversight & Escalation (Draft)

Status: owner-filled defaults; change roles to match deployment.

## Oversight Points
- MCP policy gate supports manual approval tokens for risky operations (network/fs/credentials/exfil patterns).
- High-risk steps must be blocked unless an authorized operator supplies `manual_approval_token`.
- For non-MCP tool paths, route through MCP orchestrator or add equivalent gate.

## Roles
- Oversight operator(s): Compliance Officer
- Approval authority for high-risk actions: Compliance Officer
- Incident commander (rollback/disable): Platform Lead (fallback: Compliance Officer)

## Procedures
1) Request comes in → MCP evaluates policy.
2) If manual gate triggered → Compliance Officer reviews goal/args → supplies approval token if acceptable.
3) If unsafe → deny and record reason in audit.
4) Rollback: if MCP/agent action caused a bad state, disable tool access (revoke tokens/stop service) and revert changes per environment SOP.

## Logging
- All approvals/denials must be traceable via MCP audit logs (trace_id).
- Keep a separate incident log if rollback/disable is invoked.

## Owner Actions Needed
- Fill roles and escalation contacts.
- Define rollback steps per environment (e.g., stop services, revoke tokens, restore from backup).
