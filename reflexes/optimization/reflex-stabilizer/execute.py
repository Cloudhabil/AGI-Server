"""Stabilizer: cache-based reuse of deterministic responses."""

import hashlib
import json
import time


def _hash(task, context):
    payload = json.dumps({"task": task, "context": context}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def run(task, context, level, flags, runtime, manifest, policy, schema):
    cache = runtime.get("cache", {})
    ttl = int(flags.get("stabilizer_ttl", 60))
    cache_key = _hash(task, context)
    now = time.time()

    entry = cache.get(cache_key)
    if entry and (now - entry["ts"]) <= ttl:
        return {
            "action": "REPLY",
            "payload": {"response": entry["response"]},
            "audit": {"level": level, "decision": "cache_hit"},
        }

    if flags.get("stabilizer_seed"):
        response = flags.get("stabilizer_response", "")
        if response:
            cache[cache_key] = {"response": response, "ts": now}
            return {
                "action": "PASS",
                "payload": {},
                "audit": {"level": level, "decision": "cache_seeded"},
            }

    return {"action": "PASS", "payload": {}, "audit": {"level": level, "decision": "pass"}}
