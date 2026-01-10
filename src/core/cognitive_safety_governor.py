"""
COGNITIVE SAFETY GOVERNOR
=========================

The hardware SafetyGovernor prevents physical damage.
This prevents COGNITIVE degradation and catches performance failures.

Missing from GPIA: Self-awareness of performance collapse.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class CognitiveSafetyGovernor:
    """
    Monitors GPIA's cognitive health and performance.

    Hardware SafetyGovernor asks: "Am I physically safe?"
    Cognitive SafetyGovernor asks: "Am I mentally competent?"
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.eval_dir = repo_root / "out" / "evidence_v2"
        self.log_dir = repo_root / "logs" / "cognitive_safety"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Performance Thresholds
        self.min_math_accuracy = 0.7  # Below 70% = ALERT
        self.min_coding_pass_rate = 0.6
        self.min_orchestration = 0.5

        # Degradation Detection
        self.baseline_scores = {}
        self.degradation_threshold = 0.2  # 20% drop = CRITICAL

        logging.basicConfig(
            filename=self.log_dir / "cognitive_health.log",
            level=logging.WARNING,
            format='%(asctime)s - [COGNITIVE] - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def check_eval_results(self) -> Dict[str, float]:
        """Load latest eval v2 results and extract scores"""
        scores = {}

        if not self.eval_dir.exists():
            return {"error": "No eval results found"}

        # Find latest model results
        model_dirs = [d for d in self.eval_dir.iterdir() if d.is_dir()]
        if not model_dirs:
            return {"error": "No model evaluation directories"}

        # Use most recent
        latest_dir = max(model_dirs, key=lambda d: d.stat().st_mtime)

        # Load scores from summary if exists
        summary_file = latest_dir / "summary.json"
        if summary_file.exists():
            with open(summary_file) as f:
                data = json.load(f)
                scores = data.get("scores", {})
        else:
            # Manually compute from result files
            for domain in ["math", "coding", "orchestration", "creative", "sentiment"]:
                result_file = latest_dir / f"{domain}.json"
                if result_file.exists():
                    with open(result_file) as f:
                        data = json.load(f)
                        scores[domain] = data.get("score", 0.0)

        return scores

    def audit_cognitive_health(self) -> Tuple[bool, str, Dict]:
        """
        Perform cognitive health audit.

        Returns: (is_healthy, alert_message, details)
        """
        scores = self.check_eval_results()

        if "error" in scores:
            return True, scores["error"], {}  # Can't verify, assume OK

        alerts = []
        critical = False

        # Check absolute performance
        if "math" in scores and scores["math"] < self.min_math_accuracy:
            msg = f"MATH FAILURE: {scores['math']:.1%} < {self.min_math_accuracy:.1%}"
            alerts.append(msg)
            if scores["math"] == 0.0:
                critical = True
                msg += " (ZERO PERFORMANCE - TOTAL FAILURE)"
            self.logger.error(msg)

        if "coding" in scores and scores["coding"] < self.min_coding_pass_rate:
            msg = f"CODING FAILURE: {scores['coding']:.1%} < {self.min_coding_pass_rate:.1%}"
            alerts.append(msg)
            self.logger.warning(msg)

        if "orchestration" in scores and scores["orchestration"] < self.min_orchestration:
            msg = f"ORCHESTRATION FAILURE: {scores['orchestration']:.1%}"
            alerts.append(msg)
            self.logger.warning(msg)

        # Check for degradation if we have baseline
        if self.baseline_scores:
            for domain, current in scores.items():
                if domain in self.baseline_scores:
                    baseline = self.baseline_scores[domain]
                    drop = baseline - current
                    if drop > self.degradation_threshold:
                        msg = f"DEGRADATION ALERT: {domain} dropped {drop:.1%}"
                        alerts.append(msg)
                        critical = True
                        self.logger.critical(msg)

        # Overall verdict
        if critical:
            return False, "CRITICAL COGNITIVE FAILURE DETECTED", {
                "scores": scores,
                "alerts": alerts,
                "timestamp": datetime.now().isoformat()
            }
        elif alerts:
            return False, "COGNITIVE PERFORMANCE BELOW THRESHOLD", {
                "scores": scores,
                "alerts": alerts,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return True, "COGNITIVE_HEALTH_NORMAL", {
                "scores": scores,
                "timestamp": datetime.now().isoformat()
            }

    def should_alert_user(self, scores: Dict[str, float]) -> Tuple[bool, str]:
        """
        Determine if user needs to be alerted about performance.

        This is what GPIA SHOULD HAVE DONE when eval v2 showed 0% math.
        """
        # Zero performance in any domain = IMMEDIATE ALERT
        for domain, score in scores.items():
            if score == 0.0:
                return True, f"CRITICAL: {domain.upper()} completely failed (0%)"

        # Below 50% in core domains = ALERT
        core_domains = ["math", "coding", "orchestration"]
        for domain in core_domains:
            if domain in scores and scores[domain] < 0.5:
                return True, f"WARNING: {domain.upper()} below 50% ({scores[domain]:.1%})"

        return False, "Performance acceptable"

    def set_baseline(self, scores: Dict[str, float]):
        """Store current scores as baseline for degradation detection"""
        self.baseline_scores = scores.copy()
        baseline_file = self.log_dir / "baseline_scores.json"
        with open(baseline_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "scores": scores
            }, f, indent=2)
        self.logger.info(f"Baseline set: {scores}")


def main():
    """Demonstration: What GPIA SHOULD do automatically"""
    print("="*70)
    print("COGNITIVE SAFETY GOVERNOR: What GPIA SHOULD Have Done")
    print("="*70)

    gov = CognitiveSafetyGovernor(Path("."))

    print("\n1. Checking evaluation results...")
    scores = gov.check_eval_results()
    print(f"   Scores: {scores}")

    print("\n2. Auditing cognitive health...")
    healthy, message, details = gov.audit_cognitive_health()

    print(f"\n   Status: {'HEALTHY' if healthy else 'UNHEALTHY'}")
    print(f"   Message: {message}")

    if details.get("alerts"):
        print(f"\n   Alerts:")
        for alert in details["alerts"]:
            print(f"     - {alert}")

    print("\n3. Should user be alerted?")
    should_alert, alert_msg = gov.should_alert_user(scores)

    if should_alert:
        print(f"\n   *** USER ALERT REQUIRED ***")
        print(f"   Message: {alert_msg}")
        print(f"\n   This is what GPIA SHOULD have told you automatically.")
    else:
        print(f"   No alert needed: {alert_msg}")

    print("\n" + "="*70)
    print("CONCLUSION: GPIA lacks cognitive self-monitoring")
    print("="*70)
    print("\nGPIA monitors:")
    print("  [OK] Hardware health (GPU temp, VRAM, disk)")
    print("  [MISSING] Performance quality")
    print("  [MISSING] Evaluation results")
    print("  [MISSING] Cognitive degradation")
    print("\nResult: You caught the failure. GPIA didn't.")


if __name__ == "__main__":
    main()
