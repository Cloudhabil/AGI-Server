import argparse
import hashlib
import json
import sys
from pathlib import Path


def read_json(path: str | None) -> dict:
    if path:
        raw = Path(path).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    if not raw.strip():
        raise ValueError("empty input")
    return json.loads(raw)


def compute_hash(source_id: str, payload: dict) -> str:
    raw = json.dumps({"source": source_id, "payload": payload}, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def load_ledger(path: str) -> dict:
    ledger_path = Path(path)
    if not ledger_path.exists():
        return {}
    try:
        return json.loads(ledger_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def extract_markers(ledger: dict) -> list:
    markers = []
    if isinstance(ledger.get("l1_safety_markers"), list):
        markers.extend(ledger.get("l1_safety_markers"))
    safety = ledger.get("safety", {}) if isinstance(ledger.get("safety"), dict) else {}
    if isinstance(safety.get("l1_markers"), list):
        markers.extend(safety.get("l1_markers"))
    return [str(m).lower() for m in markers if m]


def contradicts_markers(payload: dict, markers: list) -> bool:
    haystack = json.dumps(payload, ensure_ascii=True).lower()
    return any(marker in haystack for marker in markers)


def oracle_ok(packet: dict) -> bool:
    if packet.get("tier") == "ambient":
        return True
    corroborations = packet.get("corroborations", [])
    sources = {c.get("source") for c in corroborations if isinstance(c, dict) and c.get("source")}
    return len(sources) >= 2


def validate_packet(packet: dict, ledger: dict) -> tuple[bool, str]:
    required = ["source_integrity", "perceptual_hash", "emotional_urgency_score", "environmental_context_id"]
    for field in required:
        if field not in packet:
            return False, f"missing_{field}"

    if not (0.0 <= float(packet.get("source_integrity", 0)) <= 1.0):
        return False, "bad_source_integrity"

    if not (0.0 <= float(packet.get("emotional_urgency_score", 0)) <= 1.0):
        return False, "bad_urgency_score"

    source = packet.get("source") or {}
    source_id = source.get("id", "unknown")
    payload = packet.get("payload") if isinstance(packet.get("payload"), dict) else {}
    expected_hash = compute_hash(source_id, payload)
    if packet.get("perceptual_hash") != expected_hash:
        return False, "hash_mismatch"

    if not oracle_ok(packet):
        return False, "oracle_rule_failed"

    markers = extract_markers(ledger)
    if markers and contradicts_markers(payload, markers):
        return False, "cognitive_dissonance_gate"

    return True, "ok"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate signal packets against ledger")
    parser.add_argument("--input", help="JSON packet input file")
    parser.add_argument("--ledger", default="memory/agent_state_v1/ledger.json")
    args = parser.parse_args()

    packet = read_json(args.input)
    ledger = load_ledger(args.ledger)
    ok, reason = validate_packet(packet, ledger)

    status = "PASS" if ok else "FAIL"
    print(json.dumps({"status": status, "reason": reason}, ensure_ascii=True))
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
