import json
import re
from datetime import datetime
from pathlib import Path


def collect_shell_actions(shell_path: Path) -> list[str]:
    text = shell_path.read_text()
    matches = re.findall(r"function\s+([A-Za-z0-9_-]+)", text)
    return sorted(set(matches))


def load_guardrails(path: Path) -> dict:
    return json.loads(path.read_text())


def render_summary(actions: list[str], docs: list[Path], guardrails: dict) -> str:
    lines = []
    lines.append("# Shell Adoption Coordinator Report")
    lines.append(f"Generated: {datetime.utcnow().isoformat()}Z")
    lines.append("")
    lines.append("## Active Shell Actions")
    for action in actions:
        lines.append(f"- `{action}`")
    lines.append("")
    lines.append("## Documentation References")
    for doc in docs:
        lines.append(f"- `{doc}`")
    lines.append("")
    lines.append("## Guardrail Modes")
    for mode, cfg in guardrails.items():
        lines.append(f"- **{mode}**: max_agents_per_hour={cfg.get('max_agents_per_hour')}, max_steps={cfg.get('max_steps_limit')}, ttl_hours={cfg.get('ttl_hours')}")
    lines.append("")
    lines.append("## Adoption Signals")
    lines.append("- Guardrails cover manual/transpiler flows and are surfaced via shell commands.")
    lines.append("- Shared context telemetry (heartbeat + dense state) remains live for status snapshots.")
    lines.append("- Skills registry is aligned with a dedicated shell skill.")
    return "\n".join(lines)


def main():
    root = Path(__file__).resolve().parent.parent
    shell = root / "scripts" / "shell_cli.ps1"
    guardrails = root / "config" / "agent_creator_guardrails.json"
    docs = [
        root / "docs" / "shell_cli_usage.md",
        root / "docs" / "shell_cli_guardrails.md",
        root / "docs" / "shell_cli_telemetry.md",
    ]
    actions = collect_shell_actions(shell)
    guardrail_cfg = load_guardrails(guardrails)
    summary = render_summary(actions, docs, guardrail_cfg)

    target_dir = root / "runs" / "shell_adoption"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "summary.md").write_text(summary, encoding="utf8")
    print(f"Shell adoption summary written to {target_dir / 'summary.md'}")


if __name__ == "__main__":
    main()
