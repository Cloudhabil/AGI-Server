#!/usr/bin/env python3
"""
Provision a new GPIA agent workspace from a JSON request.

Usage:
  python scripts/provision_agent.py --input request.json
  echo '{...}' | python scripts/provision_agent.py
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from core.agent_creator_manager import AgentCreatorManager


def load_request(path: str | None) -> dict:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    payload = sys.stdin.read().strip()
    if not payload:
        return {}
    return json.loads(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Provision a GPIA agent workspace.")
    parser.add_argument("--input", help="Path to a JSON request file")
    args = parser.parse_args()

    request = load_request(args.input)
    manager = AgentCreatorManager()
    result = manager.provision(request)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
