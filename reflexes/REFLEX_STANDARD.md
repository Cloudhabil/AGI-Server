# REFLEX STANDARD v1

Reflexes are host-level control primitives that execute before any model call.
They are deterministic, minimal, and safe by default. Reflexes are not skills.

Principles:
- Pre-boot execution with strict time budget.
- JSON-only input/output with fixed contracts.
- No network calls; API-only memory access.
- Safety deferral is mandatory for destructive requests.
- L1-L4 benchmark awareness is enforced by reflex rules.
