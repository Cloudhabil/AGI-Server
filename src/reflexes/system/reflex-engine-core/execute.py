"""Kernel reflex: no-op marker for boot sequencing."""


def run(task, context, level, flags, runtime, manifest, policy, schema):
    """Return PASS to allow subsequent reflexes to run."""
    return {
        "action": "PASS",
        "payload": {},
        "audit": {"level": level, "decision": "pass"},
    }
