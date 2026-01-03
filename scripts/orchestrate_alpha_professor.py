#!/usr/bin/env python3
"""
Ephemeral orchestrator: Alpha attempts blob probe -> HF source; Professor verifies.
Usage:
  python scripts/orchestrate_alpha_professor.py --blob <path_to_blob> [--target <dir>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def alpha_probe(blob: Path) -> Dict[str, Any]:
    """Alpha: run manifest probe on the blob to suggest a base model."""
    from subprocess import check_output, CalledProcessError

    try:
        out = check_output([sys.executable, "scripts/ollama_manifest_probe.py", str(blob)], text=True)
        data = json.loads(out)
    except (CalledProcessError, json.JSONDecodeError) as exc:
        return {"error": f"probe_failed: {exc}"}
    return data


def professor_verify(alpha_result: Dict[str, Any]) -> Dict[str, Any]:
    """Professor: verify hint presence and basic sanity."""
    summary = alpha_result.get("summary") or {}
    base = summary.get("base_model_hint")
    if not base:
        return {"status": "fail", "reason": "no_base_model_hint"}
    return {"status": "pass", "base_model_hint": base, "architecture": summary.get("architecture")}


def maybe_download(base_model: str, target: Optional[Path]) -> Optional[str]:
    """Optional download via huggingface_hub if target specified."""
    if target is None:
        return None
    try:
        from huggingface_hub import snapshot_download
    except Exception as exc:
        return f"huggingface_hub_missing: {exc}"
    try:
        snapshot_download(
            repo_id=base_model,
            local_dir=str(target),
            allow_patterns=["tokenizer.model", "tokenizer.json", "config.json", "generation_config.json", "*.safetensors"],
        )
        return None
    except Exception as exc:
        return f"download_failed: {exc}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--blob", required=True, help="Path to Ollama/GGUF blob")
    ap.add_argument("--target", help="Optional local dir to download HF model")
    args = ap.parse_args()

    blob = Path(args.blob)
    target = Path(args.target) if args.target else None

    alpha = alpha_probe(blob)
    professor = professor_verify(alpha)
    download_status = None
    if professor.get("status") == "pass" and target:
        download_status = maybe_download(professor["base_model_hint"], target)

    result = {
        "alpha": alpha,
        "professor": professor,
        "download_status": download_status,
    }
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
