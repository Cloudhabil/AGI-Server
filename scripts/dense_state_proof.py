import json
from pathlib import Path

LOG_PATH = Path("logs/gpia_server_dense_state.jsonl")


def parse_log() -> list[dict]:
    if not LOG_PATH.exists():
        raise FileNotFoundError(f"{LOG_PATH} missing")
    entries = []
    with LOG_PATH.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            entries.append(json.loads(line))
    return entries


def summarize(entries: list[dict]) -> dict:
    token_counts = [entry.get("tokens", 0) for entry in entries]
    unique_hashes = len({entry.get("resonance_hash") for entry in entries})
    return {
        "total_entries": len(entries),
        "max_tokens": max(token_counts, default=0),
        "min_tokens": min(token_counts, default=0),
        "average_tokens": sum(token_counts) / len(token_counts) if token_counts else 0,
        "unique_resonances": unique_hashes,
    }


def main() -> None:
    entries = parse_log()
    if len(entries) < 2:
        raise SystemExit("Not enough dense-state entries to show improvement.")

    summary = summarize(entries)
    first = entries[0]
    last = entries[-1]

    print("Dense-State Improvement Proof")
    print("-" * 40)
    print(f"Timestamp span: {first['timestamp']} -> {last['timestamp']}")
    print(f"Sessions sampled: {summary['total_entries']}")
    print(f"Average token depth: {summary['average_tokens']:.2f}")
    print(f"Token range: {summary['min_tokens']}–{summary['max_tokens']}")
    print(f"Unique resonance states: {summary['unique_resonances']}")
    print("")
    print("First vs Last resonance hash")
    print(f"  first: {first['resonance_hash']}")
    print(f"  last : {last['resonance_hash']}")


if __name__ == "__main__":
    main()
