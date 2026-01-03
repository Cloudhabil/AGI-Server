"""Deterministic safety and contract enforcement gate."""

import re


def _validate_schema(task, context, level, flags, schema):
    if not isinstance(task, str):
        return False, "task must be string"
    if not isinstance(context, dict):
        return False, "context must be object"
    if not isinstance(level, str):
        return False, "level must be string"
    if not isinstance(flags, dict):
        return False, "flags must be object"
    return True, ""


def run(task, context, level, flags, runtime, manifest, policy, schema):
    valid, reason = _validate_schema(task, context, level, flags, schema)
    if not valid:
        return {
            "action": "DENY",
            "payload": {"reason": reason},
            "audit": {"level": level, "decision": "schema_deny"},
        }

    lowered = task.lower()
    for pattern in policy.get("deny_patterns", []):
        if pattern in lowered:
            return {
                "action": "DENY",
                "payload": {"reason": "destructive_request"},
                "audit": {"level": level, "decision": "blocked"},
            }

    return {"action": "PASS", "payload": {}, "audit": {"level": level, "decision": "pass"}}
