#!/usr/bin/env python3
"""
Lightweight GGUF/Ollama blob probe to extract base-model hints.
Tries python gguf reader first; falls back to `python -m gguf.scripts.gguf_dump`.
Outputs a small JSON with any metadata found.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any


CANDIDATE_KEYS = [
    "general.base_model.name",
    "general.name",
    "general.architecture",
    "general.url",
    "tokenizer.chat_template",
]


def probe_with_python(gguf_path: Path) -> Dict[str, Any]:
    try:
        from gguf import GGUFReader  # type: ignore
    except Exception:
        return {}
    try:
        rdr = GGUFReader(str(gguf_path))
        return {str(k): v for k, v in rdr.kv_data.items()}
    except Exception:
        return {}


def probe_with_dump(gguf_path: Path) -> Dict[str, Any]:
    try:
        out = subprocess.check_output(
            [sys.executable, "-m", "gguf.scripts.gguf_dump", str(gguf_path)],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except Exception:
        return {}
    kv: Dict[str, Any] = {}
    for m in re.finditer(r"([a-z0-9._]+)\s*[:=]\s*(.+)", out):
        kv[m.group(1)] = m.group(2)
    return kv


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/ollama_manifest_probe.py <path_to_blob.gguf>", file=sys.stderr)
        return 1
    gguf_path = Path(sys.argv[1])
    if not gguf_path.exists():
        print(json.dumps({"error": f"file not found: {gguf_path}"}))
        return 1

    kv = probe_with_python(gguf_path)
    if not kv:
        kv = probe_with_dump(gguf_path)

    summary = {}
    for k in CANDIDATE_KEYS:
        if k in kv:
            summary[k] = kv[k]

    base_model_hint = summary.get("general.base_model.name") or summary.get("general.name")
    result = {
        "file": str(gguf_path),
        "summary": {
            "base_model_hint": base_model_hint,
            "architecture": summary.get("general.architecture"),
            "url": summary.get("general.url"),
        },
        "raw": summary,
    }
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
