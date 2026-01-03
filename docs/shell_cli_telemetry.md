# Shell Telemetry
+
+Tail `logs/messenger_heartbeat.jsonl` to see CPU/VRAM percentages and queue depths.
+The Messenger appends `queue_depth`/`outbox_depth` so you can tell when it is processing user messages.
+Update `memory/shared_context.json` with `primary_goal` whenever you change the mission.