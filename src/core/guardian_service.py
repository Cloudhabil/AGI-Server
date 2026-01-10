"""
Guardian Service: The ASI-Father's Reporting Endpoint.
Receives and stores documentation on 'Bad Actors' discovered in the global hunt.
"""
import json
import time
from pathlib import Path
from typing import Dict

class GuardianService:
    """
    The High-Level Auditor for the ASI.
    Organizes threat intelligence into actionable reports.
    """
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.threat_vault = repo_root / "logs" / "guardian_vault"
        self.threat_vault.mkdir(parents=True, exist_ok=True)

    def receive_documentation(self, threat_id: str, documentation: Dict):
        """Stores documentation on a discovered bad actor."""
        report_path = self.threat_vault / f"threat_{threat_id}_{int(time.time())}.json"
        
        report_data = {
            "threat_id": threat_id,
            "timestamp": time.time(),
            "documentation": documentation,
            "status": "CAPTURED",
            "action_required": "AUDIT"
        }
        
        report_path.write_text(json.dumps(report_data, indent=2))
        print(f"[GUARDIAN] Documentation received for Threat: {threat_id}")
        return str(report_path)

def get_guardian(repo_root: str = "."):
    return GuardianService(Path(repo_root))
