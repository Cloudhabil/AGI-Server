"""
Compliance Service: Active Guardrails for EU AI Act Alignment.
Enforces the 'Manual Approval' gate for high-risk ASI behaviors.
"""
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)

class ComplianceService:
    """
    The 'Control Rods' for the ASI-OS.
    Implements EU AI Act Article 14 (Human Oversight) requirements.
    """
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.config_dir = repo_root / "config" / "compliance"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Risk levels mapping
        self.RISK_LEVELS = {
            "SELF_MODIFY": "CRITICAL",
            "NETWORK_EXFIL": "HIGH",
            "DATA_DELETION": "HIGH",
            "GOAL_SHIFT": "CRITICAL",
            "NOVEL_MATH": "MEDIUM"
        }
        
        # State: Staged changes awaiting approval
        self.staging_dir = repo_root / "staging"
        self.staging_dir.mkdir(exist_ok=True)
        
        # The secret token (Should be set by user)
        self.approval_token = None
        self._load_token()

    def _load_token(self):
        """Try to load the manual approval token from a secure location."""
        token_file = self.repo_root / ".manual_approval_token"
        if token_file.exists():
            self.approval_token = token_file.read_text().strip()

    def authorize_action(self, action_type: str, details: Dict, token: Optional[str] = None) -> bool:
        """
        Gatekeeper for high-risk actions.
        Returns True only if the action is low-risk OR a valid token is provided.
        """
        risk = self.RISK_LEVELS.get(action_type, "LOW")
        
        if risk in ["HIGH", "CRITICAL"]:
            if token and token == self.approval_token:
                logger.info(f"[COMPLIANCE] Action {action_type} APPROVED via token.")
                return True
            else:
                logger.warning(f"[COMPLIANCE] Action {action_type} BLOCKED. Risk: {risk}. Manual approval required.")
                return False
        
        # Low risk actions pass
        return True

    def stage_modification(self, file_path: str, new_content: str, reason: str):
        """Stage an irreversible change for human review."""
        stage_id = f"mod_{int(time.time())}"
        stage_path = self.staging_dir / f"{stage_id}.json"
        
        stage_data = {
            "file": file_path,
            "content": new_content,
            "reason": reason,
            "timestamp": time.time(),
            "status": "AWAITING_REVIEW"
        }
        
        stage_path.write_text(json.dumps(stage_data, indent=2))
        print(f"[COMPLIANCE] Self-modification staged for review: {stage_id}")
        return stage_id

    def audit_trace(self, event: str, metadata: Dict):
        """Log compliance audit trail for EU AI Act documentation."""
        audit_log = self.repo_root / "logs" / "compliance_audit.jsonl"
        audit_log.parent.mkdir(exist_ok=True)
        
        record = {
            "timestamp": time.time(),
            "event": event,
            "metadata": metadata
        }
        with open(audit_log, "a") as f:
            f.write(json.dumps(record) + "\n")
