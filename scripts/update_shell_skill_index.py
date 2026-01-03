import json
from pathlib import Path


def main():
    path = Path("skills/INDEX.json")
    data = json.loads(path.read_text(encoding="utf8"))
    entry = {
        "id": "automation/shell-operations",
        "name": "shell-operations",
        "description": "Unified shell actions that bridge messenger control, telemetry, and guardrails for GPIA.",
        "path": str(Path("skills/automation/shell-operations").resolve()),
        "source": "local",
    }
    skills = [s for s in data.get("skills", []) if s["id"] != entry["id"]]
    skills.append(entry)
    data["skills"] = skills
    path.write_text(json.dumps(data, indent=2), encoding="utf8")
    print("Updated skills/INDEX.json with shell-operations entry.")


if __name__ == "__main__":
    main()
