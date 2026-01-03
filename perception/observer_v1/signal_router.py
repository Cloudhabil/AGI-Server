import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

try:
    import yaml
except Exception:
    yaml = None

DEFAULT_CONFIG = {
    "queue_path": "perception/observer_v1/queue.json",
    "warm_memory_path": "perception/observer_v1/warm_memory.jsonl",
    "ledger_path": "memory/agent_state_v1/ledger.json",
    "context_id": "env_local_v1",
    "tiers": {
        "ambient": {"interrupt_priority": 20},
        "event": {"interrupt_priority": 140},
        "urgent": {"interrupt_priority": 240},
    },
    "sources": [],
}


def load_config(path: str | None) -> dict:
    if not path:
        return DEFAULT_CONFIG
    cfg_path = Path(path)
    if not cfg_path.exists():
        return DEFAULT_CONFIG
    if yaml is None:
        raise RuntimeError("PyYAML not available")
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    merged = DEFAULT_CONFIG.copy()
    merged.update(data)
    return merged


def to_hash(source_id: str, payload: dict) -> str:
    raw = json.dumps({"source": source_id, "payload": payload}, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def classify(event: dict) -> str:
    if event.get("tier") in {"ambient", "event", "urgent"}:
        return event["tier"]
    severity = str(event.get("severity", "")).lower()
    kind = str(event.get("kind", "")).lower()
    if severity in {"critical", "fatal", "emergency"}:
        return "urgent"
    if kind in {"safety_violation", "exception", "urgent"}:
        return "urgent"
    if kind in {"telemetry", "status", "metric", "ambient"}:
        return "ambient"
    return "event"


def source_integrity(source_id: str, cfg: dict) -> float:
    for src in cfg.get("sources", []):
        if src.get("id") == source_id:
            return float(src.get("integrity", 0.6))
    return 0.6


def urgency_score(tier: str, event: dict) -> float:
    base = {"ambient": 0.1, "event": 0.4, "urgent": 0.9}.get(tier, 0.3)
    override = event.get("urgency")
    if isinstance(override, (int, float)):
        return max(0.0, min(float(override), 1.0))
    return base


def load_queue(path: Path) -> list:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def write_queue(path: Path, queue: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(queue, indent=2), encoding="utf-8")


def append_warm(path: Path, packet: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(packet, ensure_ascii=True) + "\n")


def build_packet(event: dict, cfg: dict) -> dict:
    source_id = str(event.get("source", "unknown"))
    tier = classify(event)
    priority = int(cfg.get("tiers", {}).get(tier, {}).get("interrupt_priority", 100))
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else event
    packet = {
        "schema_version": "signal_packet_v1",
        "id": event.get("id") or hashlib.sha256(f"{source_id}:{time.time()}".encode("utf-8")).hexdigest()[:16],
        "timestamp": event.get("timestamp") or int(time.time()),
        "tier": tier,
        "interrupt_priority": priority,
        "source": {
            "id": source_id,
            "kind": event.get("kind", "event"),
        },
        "source_integrity": source_integrity(source_id, cfg),
        "perceptual_hash": to_hash(source_id, payload),
        "emotional_urgency_score": urgency_score(tier, event),
        "environmental_context_id": event.get("environmental_context_id") or cfg.get("context_id", "env_local_v1"),
        "payload": payload,
        "corroborations": event.get("corroborations", []),
    }
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description="Route raw events into queue.json")
    parser.add_argument("--input", help="JSON input file")
    parser.add_argument("--config", default="perception/observer_v1/sensor_config.yaml")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = load_config(args.config)
    if args.input:
        raw = Path(args.input).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps({"status": "error", "reason": "empty_input"}))
        return 2
    event = json.loads(raw)

    packet = build_packet(event, cfg)
    tier = packet["tier"]

    if args.dry_run:
        print(json.dumps({"status": "dry_run", "tier": tier, "packet": packet}, ensure_ascii=True))
        return 0

    if tier == "ambient":
        print(json.dumps({"status": "discarded", "tier": tier, "packet_id": packet["id"]}))
        return 0

    if tier == "event":
        append_warm(Path(cfg["warm_memory_path"]), packet)
        print(json.dumps({"status": "logged", "tier": tier, "packet_id": packet["id"]}))
        return 0

    queue_path = Path(cfg["queue_path"])
    queue = load_queue(queue_path)
    queue.insert(0, packet)
    write_queue(queue_path, queue)
    print(json.dumps({"status": "queued", "tier": tier, "packet_id": packet["id"], "queue_size": len(queue)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
