"""
GPIA Step1 Registry Agent
=========================
Runs the Step1 workflow (skill registry integrity scan) and writes JSONL reports.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from skills.loader import SkillLoader
from skills.registry import get_registry


@dataclass
class LogRecord:
    level: str
    logger: str
    message: str
    timestamp: str


class CaptureHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: List[LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(
            LogRecord(
                level=record.levelname,
                logger=record.name,
                message=record.getMessage(),
                timestamp=datetime.fromtimestamp(record.created).isoformat(),
            )
        )


def _skill_category_from_id(skill_id: str) -> str:
    if not skill_id:
        return "system"
    prefix = skill_id.split("/", 1)[0].strip().lower()
    mapping = {
        "automation": "automation",
        "ops": "automation",
        "operations": "automation",
        "code": "code",
        "data": "data",
        "writing": "writing",
        "research": "research",
        "integration": "integration",
        "interface": "integration",
        "reasoning": "reasoning",
        "cognition": "reasoning",
        "learning": "reasoning",
        "governance": "system",
        "system": "system",
        "memory": "system",
        "enterprise": "automation",
        "safety": "system",
        "foundational": "foundational",
        "creative": "creative",
    }
    return mapping.get(prefix, "system")


def _render_sbi_stub(skill_id: str, name: str, description: str, category: str) -> str:
    return f'''"""
SBI Stub Skill
==============

Auto-generated stub for {skill_id}.
"""

from typing import Any, Dict

from skills.base import (
    Skill,
    SkillCategory,
    SkillContext,
    SkillLevel,
    SkillMetadata,
    SkillResult,
)


class SBIStubSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="{skill_id}",
            name="{name}",
            description="{description}",
            category=SkillCategory("{category}"),
            level=SkillLevel.INTERMEDIATE,
            tags=["sbi", "artifact"],
        )

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        return SkillResult(
            success=False,
            output={{"error": "SBI artifact stub. Run main.py directly for execution."}},
            error="SBI artifact stub",
            skill_id=self.metadata().id,
        )


Skill = SBIStubSkill
__all__ = ["SBIStubSkill", "Skill"]
'''


def _ensure_sbi_stub(skill_dir: Path) -> Optional[str]:
    manifest_path = skill_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    skill_path = skill_dir / "skill.py"
    if skill_path.exists():
        return None
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    skill_id = data.get("skill_id") or data.get("id") or f"automation/{skill_dir.name}"
    name = data.get("name") or skill_id.split("/")[-1].replace("-", " ").title()
    description = data.get("description") or f"SBI artifact stub for {skill_id}."
    category = _skill_category_from_id(skill_id)
    stub = _render_sbi_stub(skill_id, name, description, category)
    skill_path.write_text(stub, encoding="utf-8")
    return skill_id


def _fix_sbi_stubs() -> Dict[str, Any]:
    created = []
    skipped = []
    for manifest_path in REPO_ROOT.glob("skills/*-sbi/v1/manifest.json"):
        skill_dir = manifest_path.parent
        created_id = _ensure_sbi_stub(skill_dir)
        if created_id:
            created.append(str(skill_dir))
        else:
            skipped.append(str(skill_dir))
    return {"created": created, "skipped": skipped}


def _normalize_skill_encoding() -> Dict[str, Any]:
    fixed = []
    scanned = 0
    for path in REPO_ROOT.glob("skills/**/skill.py"):
        scanned += 1
        try:
            path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="latin-1")
            cleaned = "".join(ch if ord(ch) < 128 else "-" for ch in text)
            path.write_text(cleaned, encoding="utf-8")
            fixed.append(str(path))
    return {"scanned": scanned, "fixed": fixed}


def _run_scan() -> Dict[str, Any]:
    handler = CaptureHandler()
    root_logger = logging.getLogger()
    prior_level = root_logger.level
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    loader = SkillLoader()
    count = loader.scan_all(lazy=False)
    stats = get_registry().get_stats()

    root_logger.removeHandler(handler)
    root_logger.setLevel(prior_level)

    warnings = [asdict(r) for r in handler.records if r.level in {"WARNING", "ERROR"}]
    infos = [asdict(r) for r in handler.records if r.level == "INFO"]

    return {
        "timestamp": datetime.now().isoformat(),
        "registered_count": count,
        "stats": stats,
        "warnings": warnings,
        "info_count": len(infos),
        "warning_count": len(warnings),
    }


def _snapshot_skills() -> Dict[str, float]:
    roots = REPO_ROOT / "skills"
    patterns = [
        "manifest.yaml",
        "manifest.yml",
        "manifest.json",
        "skill.json",
        "SKILL.md",
        "skill.py",
        "__init__.py",
    ]
    snapshot: Dict[str, float] = {}
    for pattern in patterns:
        for path in roots.rglob(pattern):
            try:
                snapshot[str(path)] = path.stat().st_mtime
            except OSError:
                continue
    return snapshot


def _diff_snapshot(prev: Dict[str, float], current: Dict[str, float]) -> List[str]:
    changed: List[str] = []
    for path, mtime in current.items():
        if path not in prev or prev[path] != mtime:
            changed.append(path)
    return changed


def _write_reports(report: Dict[str, Any], output_path: Path, latest_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(report, ensure_ascii=True) + "\n")
    latest_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Step1 skill registry integrity scan")
    parser.add_argument("--runs", type=int, default=1, help="How many scans to run (0 = infinite)")
    parser.add_argument("--interval", type=int, default=0, help="Seconds between runs")
    parser.add_argument("--fix", action="store_true", help="Attempt repairs before scanning")
    parser.add_argument("--watch", action="store_true", help="Watch skills/ for changes and auto-run")
    parser.add_argument("--watch-interval", type=int, default=5, help="Seconds between change checks")
    parser.add_argument(
        "--output",
        type=str,
        default=str(REPO_ROOT / "runs" / "step1_registry_agent.jsonl"),
        help="JSONL output path",
    )
    parser.add_argument(
        "--latest",
        type=str,
        default=str(REPO_ROOT / "runs" / "step1_registry_agent_latest.json"),
        help="Latest JSON output path",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    latest_path = Path(args.latest)

    runs = args.runs
    interval = max(0, args.interval)
    if runs != 1 and interval == 0:
        interval = 60

    iteration = 0
    if args.watch:
        last_snapshot = _snapshot_skills()
        while True:
            time.sleep(max(1, int(args.watch_interval)))
            current = _snapshot_skills()
            changed = _diff_snapshot(last_snapshot, current)
            if not changed:
                continue
            iteration += 1
            repairs: Optional[Dict[str, Any]] = None
            if args.fix:
                repairs = {
                    "sbi_stubs": _fix_sbi_stubs(),
                    "encoding": _normalize_skill_encoding(),
                }
                current = _snapshot_skills()
            report = _run_scan()
            report["iteration"] = iteration
            report["trigger"] = {"change_count": len(changed), "changed": changed[:20]}
            if repairs:
                report["repairs"] = repairs
            _write_reports(report, output_path, latest_path)
            print(json.dumps(report, indent=2))
            last_snapshot = current
        return 0

    while True:
        iteration += 1
        repairs: Optional[Dict[str, Any]] = None
        if args.fix:
            repairs = {
                "sbi_stubs": _fix_sbi_stubs(),
                "encoding": _normalize_skill_encoding(),
            }
        report = _run_scan()
        report["iteration"] = iteration
        if repairs:
            report["repairs"] = repairs
        _write_reports(report, output_path, latest_path)
        print(json.dumps(report, indent=2))

        if runs > 0 and iteration >= runs:
            break
        if interval > 0:
            time.sleep(interval)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
