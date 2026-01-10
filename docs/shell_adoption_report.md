# Shell Adoption Report

## Goal
Document the GPIA-native shell so that developers, users, and business stakeholders understand what commands exist, how they are guarded, and what telemetry they expose. The adoption effort also introduces an observable skill entry and a lightweight adoption coordinator that produces structured evidence inside `runs/shell_adoption/`.

## Findings
1. **Command surface**: `scripts/shell_cli.ps1` defines `Start-ShellMessenger`, `Stop-ShellMessenger`, `Start-GPIAServer`, `Stop-GPIAServer`, `Server-Status`, `List-Skills`, `Show-Guardrails`, `Tail-MessengerHeartbeat`, `Send-Message`, and `Generate-DenseState`. Each helper now validates files and writes structured JSON back into shared context.
   `Show-Telemetry` surfaces the latest heartbeat snapshot for quick resource visibility, and the GPIA server actions manage the embedded inference daemon.
2. **Guardrails**: `config/agent_creator_guardrails.json` exposes three policies (defaults, manual, transpiler). Commands log to the heartbeat, and the `transpiler` mode restricts spawn depth and enforces dry runs.
3. **Telemetry**: `logs/messenger_heartbeat.jsonl` already emits queue/telemetry stats. Shell actions should be documented so operators can use `Tail-MessengerHeartbeat` plus `Send-Message` to exercise the messenger safely.
4. **Skills registry**: Added `automation/shell-operations` entry pointing to the shell and new doc, ensuring the Creator Agent can reference the shell workflow.

## Next Steps
- **Reporter.exe**: Run `python scripts/adoption_coordinator.py` whenever shell docs or guardrails change; the resulting `runs/shell_adoption/summary.md` serves as ingestible evidence for compliance or adoption checklists.
- **Skill adoption**: Operators can now treat `automation/shell-operations` as the jump-off skill; integrate it into onboarding or training materials.
- **Telemetry verification**: Add a “snapshot” command (future) that bundles dense state + telemetry + guardrail status to the shell for quick audits.

## Artifacts
- `scripts/adoption_coordinator.py`
- `runs/shell_adoption/summary.md` (generated after script execution)
- `docs/shell_cli_usage.md`, `docs/shell_cli_guardrails.md`, `docs/shell_cli_telemetry.md`
- `src/skills/automation/shell-operations` (new skill entry)
