"""
Evaluation Service: Kernel interface to the Evals subsystem.
Allows the organism to trigger its own cognitive health checks.
"""
import logging
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

class EvaluationService:
    """
    Service to execute cognitive evaluations (evals/run_v2.py).
    Feeds data to the CognitiveSafetyGovernor.
    """
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.eval_script = repo_root / "evals" / "run_v2.py"
        
    def run_evals(self) -> bool:
        """
        Run the full evaluation suite (v2).
        Returns True if successful.
        """
        if not self.eval_script.exists():
            logger.error(f"Eval script not found: {self.eval_script}")
            return False

        cmd = [sys.executable, str(self.eval_script)]
        
        logger.info("Triggering cognitive evaluation run...")
        print(f"[EVAL] Starting evaluation run (this may take minutes)...")
        
        try:
            # Run and capture output to prevent spamming the console too much, 
            # or let it stream if we want visibility. Let's stream but check return code.
            subprocess.run(cmd, check=True)
            logger.info("Evaluation run complete.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Eval run failed with code {e.returncode}")
            return False
        except Exception as e:
            logger.error(f"Eval run failed: {e}")
            return False
