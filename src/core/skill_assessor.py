"""
Skill Assessor: Evaluates and filters the AGI's skill library.
Implements the 'Do-Not-Use' Locker for garbage and high-risk components.
"""
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class SkillAssessor:
    """
    The filter between the Cognitive Ecosystem and the live Brain.
    Ensures 'Garbage' skills are never executed.
    """
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.locker_file = repo_root / "data" / "locker" / "do_not_use.json"
        self._load_locker()

    def _load_locker(self):
        """Load the list of prohibited skills."""
        if self.locker_file.exists():
            try:
                self.locker = json.loads(self.locker_file.read_text())
            except:
                self.locker = {"blocked_skills": {}, "garbage_patterns": []}
        else:
            self.locker = {"blocked_skills": {}, "garbage_patterns": ["hallucination", "infinite_loop", "vram_leak"]}
            self._save_locker()

    def _save_locker(self):
        self.locker_file.parent.mkdir(parents=True, exist_ok=True)
        self.locker_file.write_text(json.dumps(self.locker, indent=2))

    def assess_skill(self, skill_id: str, performance_metrics: Dict) -> str:
        """
        Classify a skill: USEFUL, RISKY, or GARBAGE.
        """
        success_rate = performance_metrics.get("success_rate", 1.0)
        risk_score = performance_metrics.get("risk_score", 0.0)
        
        if success_rate < 0.2 or "garbage" in skill_id:
            self.lock_skill(skill_id, "Low performance/Garbage content")
            return "GARBAGE"
        
        if risk_score > 0.7:
            self.lock_skill(skill_id, "High risk signature")
            return "RISKY"
            
        return "USEFUL"

    def lock_skill(self, skill_id: str, reason: str):
        """Move a skill to the 'Do-Not-Use' Locker."""
        self.locker["blocked_skills"][skill_id] = {
            "reason": reason,
            "timestamp": Path(self.repo_root).stat().st_mtime # Simple timestamp
        }
        self._save_locker()
        logger.warning(f"[ASSESSOR] Skill {skill_id} has been LOCKED in the 'Do-Not-Use' locker.")

    def is_blocked(self, skill_id: str) -> bool:
        """Check if a skill is in the locker."""
        return skill_id in self.locker["blocked_skills"]

    def get_locker_report(self) -> Dict:
        return self.locker
