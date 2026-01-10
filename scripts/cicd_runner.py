#!/usr/bin/env python3
"""
CI/CD Runner - Autonomous Pipeline Executor
============================================

This runner provides a continuous CI/CD service that:
1. Watches for pipeline triggers (API, file changes, schedules)
2. Executes pipelines using multi-model intelligence
3. Reports results and learns from outcomes

Multi-Model Strategy:
- CodeGemma (133 tok/s): Quick validation, linting, syntax checks
- Qwen3 (87 tok/s): Code generation, skill creation, improvements
- DeepSeek-R1 (74 tok/s): Deep analysis, debugging, architecture decisions

Usage:
    python cicd_runner.py                    # Run continuously
    python cicd_runner.py --once             # Single pipeline run
    python cicd_runner.py --watch /workspace # Watch directory for changes
    python cicd_runner.py --improve-skills   # Run skill improvement cycle
"""
# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [CICD] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class CICDRunner:
    """
    Autonomous CI/CD pipeline runner.

    This integrates with:
    - CICDPipelineSkill for pipeline execution
    - GrowthSkill for skill improvement
    - MemorySkill for learning from outcomes
    - MindsetSkill for intelligent decision making
    """

    def __init__(self, workspace: str = "/workspace"):
        self.workspace = Path(workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)

        self._pipeline = None
        self._growth = None
        self._memory = None
        self._mindset = None

        self.run_count = 0
        self.last_run = None

        # Configuration
        self.poll_interval = int(os.environ.get("CICD_POLL_INTERVAL", "60"))
        self.auto_improve = os.environ.get("CICD_AUTO_IMPROVE", "true").lower() == "true"

    @property
    def pipeline(self):
        if self._pipeline is None:
            try:
                import importlib
                cicd_module = importlib.import_module("skills.automation.cicd-pipeline.skill")
                self._pipeline = cicd_module.CICDPipelineSkill()
                logger.info("CICDPipelineSkill loaded")
            except Exception as e:
                logger.error(f"Failed to load CICDPipelineSkill: {e}")
        return self._pipeline

    @property
    def growth(self):
        if self._growth is None:
            try:
                from skills.conscience.growth.skill import GrowthSkill
                self._growth = GrowthSkill()
                logger.info("GrowthSkill loaded")
            except Exception as e:
                logger.warning(f"GrowthSkill not available: {e}")
        return self._growth

    @property
    def memory(self):
        if self._memory is None:
            try:
                from skills.conscience.memory.skill import MemorySkill
                self._memory = MemorySkill()
                logger.info("MemorySkill loaded")
            except Exception as e:
                logger.warning(f"MemorySkill not available: {e}")
        return self._memory

    @property
    def mindset(self):
        if self._mindset is None:
            try:
                from skills.conscience.mindset.skill import MindsetSkill
                self._mindset = MindsetSkill()
                logger.info("MindsetSkill loaded")
            except Exception as e:
                logger.warning(f"MindsetSkill not available: {e}")
        return self._mindset

    def _get_context(self):
        """Create skill context."""
        from skills.base import SkillContext
        return SkillContext(agent_role="cicd_runner")

    def run_pipeline(
        self,
        target: str = ".",
        stages: Optional[List[str]] = None,
        environment: str = "dev",
    ) -> Dict[str, Any]:
        """
        Run a CI/CD pipeline.

        Uses multi-model routing:
        - Validate stage: CodeGemma (fast)
        - Analyze stage: DeepSeek (deep reasoning)
        - Improve stage: Qwen3 (creative)
        """
        if not self.pipeline:
            return {"success": False, "error": "Pipeline skill not available"}

        logger.info(f"Starting pipeline for {target}")
        logger.info(f"Stages: {stages or ['validate', 'analyze', 'test', 'build']}")
        logger.info(f"Environment: {environment}")

        context = self._get_context()

        result = self.pipeline.execute({
            "capability": "run",
            "target": target,
            "stages": stages or ["validate", "analyze", "test", "build"],
            "environment": environment,
        }, context)

        self.run_count += 1
        self.last_run = datetime.now()

        if result.success:
            logger.info(f"Pipeline completed successfully: {result.output.get('run_id')}")
        else:
            logger.error(f"Pipeline failed: {result.error}")

        return {
            "success": result.success,
            "run_id": result.output.get("run_id") if result.output else None,
            "status": result.output.get("status") if result.output else "failed",
            "stages": result.output.get("stages") if result.output else {},
            "error": result.error,
        }

    def improve_skill(self, skill_id: str) -> Dict[str, Any]:
        """
        Improve a specific skill using multi-model reasoning.

        Process:
        1. DeepSeek analyzes the skill (deep reasoning)
        2. Qwen3 generates improvements (creative synthesis)
        3. CodeGemma validates the changes (quick check)
        """
        if not self.pipeline:
            return {"success": False, "error": "Pipeline skill not available"}

        logger.info(f"Improving skill: {skill_id}")

        context = self._get_context()

        result = self.pipeline.execute({
            "capability": "improve_skill",
            "target": skill_id,
        }, context)

        if result.success:
            logger.info(f"Skill improvement completed with {len(result.output.get('improvements', []))} suggestions")
        else:
            logger.error(f"Skill improvement failed: {result.error}")

        return {
            "success": result.success,
            "skill_id": skill_id,
            "improvements": result.output.get("improvements") if result.output else [],
            "error": result.error,
        }

    def improve_all_skills(self) -> Dict[str, Any]:
        """
        Run improvement cycle on all skills.

        Uses GrowthSkill to identify which skills need improvement,
        then applies multi-model reasoning to improve each.
        """
        logger.info("Starting skill improvement cycle")

        # Get list of skills
        skills_dir = Path("skills")
        skill_ids = []

        for manifest in skills_dir.rglob("manifest.yaml"):
            try:
                import yaml
                with open(manifest) as f:
                    data = yaml.safe_load(f)
                    if data and data.get("id"):
                        skill_ids.append(data["id"])
            except Exception:
                pass

        logger.info(f"Found {len(skill_ids)} skills to analyze")

        results = []
        for skill_id in skill_ids:
            # Skip system skills for safety
            if skill_id.startswith("conscience/safety"):
                continue

            result = self.improve_skill(skill_id)
            results.append(result)

            # Rate limit to avoid overwhelming the models
            time.sleep(5)

        successful = sum(1 for r in results if r.get("success"))
        logger.info(f"Skill improvement complete: {successful}/{len(results)} skills improved")

        return {
            "success": True,
            "skills_analyzed": len(results),
            "skills_improved": successful,
            "results": results,
        }

    def create_skill(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new skill from specification.

        Uses Qwen3 for code generation with DeepSeek validation.
        """
        if not self.pipeline:
            return {"success": False, "error": "Pipeline skill not available"}

        logger.info(f"Creating new skill: {spec.get('id', 'unknown')}")

        context = self._get_context()

        result = self.pipeline.execute({
            "capability": "create_skill",
            "skill_spec": spec,
        }, context)

        if result.success:
            logger.info(f"Skill created: {result.output.get('skill_path')}")
        else:
            logger.error(f"Skill creation failed: {result.error}")

        return {
            "success": result.success,
            "skill_id": spec.get("id"),
            "skill_path": result.output.get("skill_path") if result.output else None,
            "error": result.error,
        }

    def watch_and_run(self, watch_path: str = ".") -> None:
        """
        Watch for file changes and trigger pipelines.
        """
        logger.info(f"Watching {watch_path} for changes...")

        last_mtime = {}

        while True:
            try:
                # Check for file changes
                changed = False
                for path in Path(watch_path).rglob("*.py"):
                    mtime = path.stat().st_mtime
                    if str(path) not in last_mtime:
                        last_mtime[str(path)] = mtime
                    elif mtime > last_mtime[str(path)]:
                        logger.info(f"Change detected: {path}")
                        changed = True
                        last_mtime[str(path)] = mtime

                if changed:
                    self.run_pipeline(target=watch_path)

                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                logger.info("Watch stopped by user")
                break
            except Exception as e:
                logger.error(f"Watch error: {e}")
                time.sleep(30)

    def run_continuous(self) -> None:
        """
        Run continuous CI/CD service.

        This provides:
        1. Periodic skill improvement (if enabled)
        2. Pipeline execution on demand
        3. Learning from outcomes
        """
        logger.info("=" * 60)
        logger.info("CI/CD Runner starting")
        logger.info(f"Workspace: {self.workspace}")
        logger.info(f"Auto-improve: {self.auto_improve}")
        logger.info(f"Poll interval: {self.poll_interval}s")
        logger.info("=" * 60)

        # Initial skill check
        self._log_available_skills()

        cycle = 0
        improve_interval = 3600  # Improve skills every hour
        last_improve = 0

        while True:
            try:
                cycle += 1
                now = time.time()

                # Periodic skill improvement
                if self.auto_improve and (now - last_improve) > improve_interval:
                    logger.info("Running periodic skill improvement...")
                    self.improve_all_skills()
                    last_improve = now

                # Log status
                if cycle % 10 == 0:
                    self._log_status()

                time.sleep(self.poll_interval)

            except KeyboardInterrupt:
                logger.info("CI/CD Runner stopped by user")
                break
            except Exception as e:
                logger.error(f"Runner error: {e}")
                time.sleep(30)

    def _log_available_skills(self) -> None:
        """Log available skills."""
        skills_dir = Path("skills")
        count = 0

        for manifest in skills_dir.rglob("manifest.yaml"):
            count += 1

        logger.info(f"Available skills: {count}")

    def _log_status(self) -> None:
        """Log current status."""
        logger.info(f"Status: runs={self.run_count}, last_run={self.last_run}")


def main():
    parser = argparse.ArgumentParser(description="CI/CD Runner")
    parser.add_argument("--once", action="store_true", help="Run single pipeline")
    parser.add_argument("--watch", type=str, help="Watch directory for changes")
    parser.add_argument("--improve-skills", action="store_true", help="Run skill improvement cycle")
    parser.add_argument("--create-skill", type=str, help="Create skill from JSON spec file")
    parser.add_argument("--target", type=str, default=".", help="Target path")
    parser.add_argument("--stages", type=str, help="Comma-separated stages")
    parser.add_argument("--workspace", type=str, default="/workspace", help="Workspace directory")

    args = parser.parse_args()

    runner = CICDRunner(workspace=args.workspace)

    if args.once:
        stages = args.stages.split(",") if args.stages else None
        result = runner.run_pipeline(target=args.target, stages=stages)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    elif args.watch:
        runner.watch_and_run(args.watch)

    elif args.improve_skills:
        result = runner.improve_all_skills()
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    elif args.create_skill:
        with open(args.create_skill) as f:
            spec = json.load(f)
        result = runner.create_skill(spec)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["success"] else 1)

    else:
        runner.run_continuous()


if __name__ == "__main__":
    main()