# Unified Shell Usage

## Commands
- `Start-ShellMessenger`: Launches the living messenger agent and records its PID.
- `Stop-ShellMessenger`: Signals the messenger to stop and cleans up artifacts.
- `Start-GPIAServer`: Starts the embedded GPIA Server utility (HTTP inference daemon).
- `Stop-GPIAServer`: Stops the embedded GPIA Server utility.
- `Server-Status`: Reports the GPIA server PID/status.
- `List-Skills`: Prints the first 10 automation/system skills.
- `Show-Guardrails`: Displays the guardrail policy configuration.
- `Tail-MessengerHeartbeat`: Streams the heartbeat log to stay hands-free.
- `Show-Telemetry`: Shows the latest heartbeat snapshot with CPU/RAM/VRAM/queue stats for quick visibility.
- `Send-Message`: Appends user text to the shared context so the messenger responds.
- `Generate-DenseState`: Seeds the Dense-State with deterministic float data.

Every command logs under `runs/shell_architect/` and honors `config/agent_creator_guardrails.json` limits.

For Dense-State improvement proof, run `python scripts/dense_state_proof.py` after generating multiple inference cycles; it summarizes tokens, resonance hashes, and span.
