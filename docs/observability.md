# Observability

## Retention Policies

| Environment | Logs | Traces |
|-------------|------|--------|
| dev | 1 day | 1 day |
| staging | 7 days | 3 days |
| prod | 30 days | 7 days |

## Alert Thresholds

- **Error rate**: alert when more than 5% of requests fail within 5 minutes.
- **Latency**: alert when p95 latency exceeds 2s in staging or 1s in production.
- **Collector health**: alert if the OpenTelemetry collector drops spans or logs.

## Local GPIA Telemetry

Track these signals during benchmarks or long runs:

- **VRAM pressure**: spikes above 90% indicate the need to downscale or segment runs.
- **Telemetry log**: `memory/agent_state_v1/telemetry.jsonl` records CPU/RAM/VRAM/network snapshots.
- **Sovereignty + Resonance traces**: episodic memory entries include `sovereignty_trace` and `resonance_trace` for gating visibility.
- **Disk write bursts**: sustained high writes imply memory spill or logging loops.
- **Ollama host health**: ensure `127.0.0.1:11435` responds for GPIA profiles.
- **Skill error rate**: monitor failures in `skills/INDEX.json` executions and pass/fail ratios.
- **Rollback signals**: `memory/agent_state_v1/rollback_required.json` indicates a blocked rollback request.
