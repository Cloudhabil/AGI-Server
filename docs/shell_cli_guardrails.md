# Shell Guardrails
+
+1. `Start-ShellMessenger` checks `policy_scope=manual` and logs in `agent_creator_audit.jsonl`.
+2. `Send-Message` writes into the shared context so `Sync-AgentContext` finds fresh Dense-State data.
+3. `Generate-DenseState` ensures 512 floats are written with a lock so the Messenger reads clean arrays.
+4. All commands stream `logs/messenger_heartbeat.jsonl` records for auditability.