## Shell Operations

**Description**: The unified shell exposes developer, user, and business-friendly commands for interacting with the living messenger, telemetry logs, Dense-State generator, and guardrail audits. This skill documents the commands, ensures guardrail logging, and serves as the anchor point for the Creator Agent adoption workflow.

**Usage**:

- `Run-Shell start/stop/list/guardrails/tail/send/dense` to control the messenger and view telemetry.
- Each action validates key files (`memory/shared_context.json`, `logs/messenger_heartbeat.jsonl`) before mutating state, keeping guardrails enforceable.
- Use `Send-Message` to enqueue requests and `Generate-DenseState` to refresh formalism data for the messenger.

**Guardrails**:

- Tied to `config/agent_creator_guardrails.json` for manual and transpiler policies.
- Requires telemetry traces for auditability and informs the regression gate with sovereignty decisions.

