"""Generate a palette of Hermes Trismegistos research skills.

This script scaffolds skills under `src/skills/synthesized/hermes_trismegistos/`
using the Skill Standard (manifest + skill.py). It does not ingest data; it only
writes local files so you can plug in your own offline pipelines (Professor/Alpha
agents, H-Net, Safety Governor) without touching proprietary sources.

Usage (from repo root):
  python scripts/generate_hermes_trismegistos_skills.py [--force] [--only slug1 slug2]

Notes:
- Keeps everything local (no network calls).
- Adds "not for clinical use" and "public-data only" governance flags.
- Overwrite behavior is opt-in via --force.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from textwrap import dedent


# Define the Hermes Trismegistos skill set. Expand or edit as needed.
SKILL_DEFINITIONS = [
    {
        "slug": "literature_signal_extractor",
        "name": "Hermes Literature Signal Extractor",
        "description": (
            "Extracts gene/variant/pathway/drug relations from open literature (e.g., arXiv,"
            " PubMed-open) and ranks signals by evidence quality for downstream synthesis."
        ),
        "tags": ["ner", "relation-extraction", "literature-mining", "genomics"],
    },
    {
        "slug": "protein_folding_hypothesis_miner",
        "name": "Hermes Protein Folding Hypothesis Miner",
        "description": (
            "Surfaces folding/stability hypotheses by aligning open-structure priors with"
            " novel motifs; emits candidate residues/regions to probe offline."),
        "tags": ["protein-folding", "structure", "hypothesis-generation"],
    },
    {
        "slug": "multiomics_link_predictor",
        "name": "Hermes Multi-Omics Link Predictor",
        "description": (
            "Predicts plausible gene–pathway–phenotype links by composing open transcriptomic"
            " and proteomic signals; outputs candidates for bench validation queues."),
        "tags": ["multi-omics", "link-prediction", "graph"],
    },
    {
        "slug": "safety_governor_pharma",
        "name": "Hermes Pharma Safety Governor",
        "description": (
            "Applies configurable toxicity/ethics/compliance gates (public rules only) to"
            " proposed syntheses; designed to run before any wet-lab or clinical escalation."),
        "tags": ["safety", "toxicity", "compliance"],
    },
    {
        "slug": "clinical_signal_ranker",
        "name": "Hermes Clinical Signal Ranker",
        "description": (
            "Ranks open clinical signals (non-PII) by strength, study quality, and novelty;"
            " emits rationale and suggested follow-up experiments."),
        "tags": ["ranking", "clinical", "evidence"],
    },
]


def slugify(text: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_-]+", "-", text.strip().lower()).strip("-")
    return safe or "skill"


def render_manifest(skill_id: str, name: str, description: str, tags: list[str]) -> str:
    return dedent(
        f"""
        id: {skill_id}
        name: {name}
        description: {description}
        version: "0.1.0"
        category: research
        level: advanced
        tags: [{', '.join(tags)}]
        license: Proprietary - internal research only
        data_governance:
          pii: false
          phi: false
          data_residency: local-only
          source_policy: public-literature-only
        compliance:
          not_for_clinical_use: true
          human_review_required: true
          safety_governor_required: true
        dependencies: []
        """
    ).strip() + "\n"


def render_skill_py(skill_id: str, name: str, description: str, tags: list[str]) -> str:
    template = """
    from skills.base import (
        Skill,
        SkillCategory,
        SkillContext,
        SkillLevel,
        SkillMetadata,
        SkillResult,
    )
    import logging
    from typing import Any, Dict


    logger = logging.getLogger(__name__)


    class HermesTrismegistosSkill(Skill):
        \"\"\"
        {description}

        Governance: public-data only, not for clinical use, offline execution recommended.
        \"\"\"

        def metadata(self) -> SkillMetadata:
            return SkillMetadata(
                id="{skill_id}",
                name="{name}",
                description="{description}",
                category=SkillCategory.RESEARCH,
                level=SkillLevel.ADVANCED,
                tags={tags},
                license="Proprietary - internal research only",
            )

        def input_schema(self) -> Dict[str, Any]:
            return {{
                "type": "object",
                "properties": {{
                    "payload": {{"type": "object"}},
                    "mode": {{"type": "string", "enum": ["analyze", "rank", "gate"]}},
                }},
                "required": ["payload"],
            }}

        def output_schema(self) -> Dict[str, Any]:
            return {{
                "type": "object",
                "properties": {{
                    "status": {{"type": "string"}},
                    "insights": {{"type": "array"}},
                    "governance": {{"type": "object"}},
                }},
            }}

        def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
            # Placeholder: plug in your offline pipeline (Professor/Alpha/H-Net) here.
            mode = input_data.get("mode", "analyze")
            logger.info("Hermes skill invoked", extra={{"skill": "{skill_id}", "mode": mode}})

            insights = [
                "placeholder_insight_use_offline_pipeline",
            ]
            governance = {{
                "not_for_clinical_use": True,
                "source_policy": "public-literature-only",
            }}

            return SkillResult(
                success=True,
                output={{"status": "OK", "mode": mode, "insights": insights, "governance": governance}},
                skill_id="{skill_id}",
            )
    """
    return dedent(template.format(skill_id=skill_id, name=name, description=description, tags=tags)).strip() + "\n"


def write_skill(root: Path, definition: dict, force: bool = False) -> None:
    slug = slugify(definition["slug"])
    skill_id = f"synthesized/hermes_trismegistos/{slug}"
    skill_dir = root / "src" / "skills" / "synthesized" / "hermes_trismegistos" / slug
    manifest_path = skill_dir / "manifest.yaml"
    skill_py_path = skill_dir / "skill.py"

    skill_dir.mkdir(parents=True, exist_ok=True)

    manifest = render_manifest(skill_id, definition["name"], definition["description"], definition["tags"])
    skill_py = render_skill_py(skill_id, definition["name"], definition["description"], definition["tags"])

    if manifest_path.exists() and not force:
        print(f"[SKIP] {manifest_path} exists (use --force to overwrite)")
    else:
        manifest_path.write_text(manifest, encoding="utf-8")
        print(f"[WRITE] {manifest_path}")

    if skill_py_path.exists() and not force:
        print(f"[SKIP] {skill_py_path} exists (use --force to overwrite)")
    else:
        skill_py_path.write_text(skill_py, encoding="utf-8")
        print(f"[WRITE] {skill_py_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate Hermes Trismegistos skills (local-only scaffold)")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--only", nargs="*", help="Generate only these slugs (e.g., protein_folding_hypothesis_miner)")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    selected = SKILL_DEFINITIONS
    if args.only:
        targets = {slugify(x) for x in args.only}
        selected = [d for d in SKILL_DEFINITIONS if slugify(d["slug"]) in targets]
        missing = targets - {slugify(d["slug"]) for d in selected}
        if missing:
            print(f"[WARN] Unknown slugs skipped: {', '.join(sorted(missing))}")

    for definition in selected:
        write_skill(repo_root, definition, force=args.force)

    print("\nDone. Plug your offline pipelines into the generated skill.py files.")


if __name__ == "__main__":
    main()
