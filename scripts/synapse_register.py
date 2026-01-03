"""
Synapse Registration (ASI Action 1)

Stub: reads SKILL.md + module text and prints a vector registration placeholder.
"""

from pathlib import Path
import json


def register_skill(skill_dir: str) -> dict:
    skill_path = Path(skill_dir)
    skill_md = skill_path / "SKILL.md"
    py_files = list(skill_path.glob("*.py"))

    body = skill_md.read_text(encoding="utf-8") if skill_md.exists() else ""
    sources = {p.name: p.read_text(encoding="utf-8") for p in py_files}

    embedding_def = {
        "skill_id": skill_path.name.replace("_", "-"),
        "summary": body[:200],
        "files": list(sources.keys()),
    }
    print(json.dumps({"registered": embedding_def}, indent=2))
    return embedding_def


if __name__ == "__main__":
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "skills/lifecycle/ephemeral_synthesis"
    register_skill(target)
