# Post-Market Monitoring (Draft)

Status: owner defaults; adjust thresholds/channels to deployment.

## Monitoring Scope
- MCP orchestration health: audit log volume, failure/block rates, timeout rates.
- Agent/bus services: uptime, error rates, queue depth (if available).
- Resource usage: CPU/RAM/VRAM/disk (see heartbeat logs).
- Security signals: policy blocks, denied approvals, anomaly detections (if available).

## Telemetry / Logs
- MCP audit: `memory/agent_state_v1/mcp_orchestrator_audit.jsonl`, `mcp_audit.jsonl`.
- Heartbeat/ledger: `logs/messenger_heartbeat.jsonl`, `memory/agent_state_v1/ledger.json`.
- Service logs: bus/agent/server logs.

## Alerts / Thresholds (defaults)
- MCP failure/block rate > 5% over 1 hour.
- Service downtime > 5 minutes.
- Resource saturation > 90% sustained for 5 minutes.
- Notification path: email/Slack to ops/compliance channel.

## Incident Response
1) Detect breach of threshold.
2) Assign incident commander (see `compliance/oversight.md` roles).
3) Contain: pause risky operations (disable tool access, stop services if needed).
4) Eradicate/recover: revert configs, restore from backups, rotate tokens if compromised.
5) Record: log incident, trace_id(s), timeline, actions taken.

## Owner Actions Needed
- Set actual alert channels and rotate on-call.
- Decide incident log location and retention.
