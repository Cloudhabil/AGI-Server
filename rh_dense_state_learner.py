"""
RH Dense-State Learning Loop

Extracts mathematical patterns from Alpha-Professor interactions and learns
what makes valid RH approaches succeed. Uses GPIA's dense-state memory
system to persist learnings across sessions.

Key functions:
1. Pattern extraction: Analyze successful vs failed proposals
2. Pattern encoding: Store in dense-state voxel space
3. Feedback generation: Create insights for next Alpha cycle
4. Resonance tracking: Find recurring mathematical themes
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np


class RHDenseStateLearner:
    """Learns patterns from Alpha-Professor RH research."""

    def __init__(self, session_dir: Path):
        self.session_dir = Path(session_dir)
        self.proposals_dir = self.session_dir / "rh_proposals"
        self.evaluations_dir = self.session_dir / "rh_evaluations"
        self.patterns_dir = self.session_dir / "rh_patterns"
        self.patterns_dir.mkdir(parents=True, exist_ok=True)

        # Dense-state configuration
        self.voxel_grid_size = 8  # 8x8x8 = 512 cells
        self.voxel_grid = np.zeros((self.voxel_grid_size, self.voxel_grid_size, self.voxel_grid_size))
        self.pattern_history = []

    def extract_mathematical_features(self, proposal: Dict) -> Dict:
        """Extract mathematical features from proposal content."""
        content = proposal.get("content", "").lower()

        features = {
            "mentions_berry_keating": "berry-keating" in content or "berry keating" in content,
            "mentions_gue": "gue" in content or "gaussian unitary ensemble" in content,
            "mentions_random_matrix": "random matrix" in content or "rmt" in content,
            "mentions_eigenvalue": "eigenvalue" in content or "eigenvalue" in content,
            "mentions_quantum": "quantum" in content,
            "mentions_chaos": "chaos" in content or "chaotic" in content,
            "mentions_discretization": "discretiz" in content or "lattice" in content,
            "mentions_potential": "potential" in content,
            "mentions_spectral": "spectral" in content,
            "mentions_operator": "operator" in content,
            "mentions_hamiltonian": "hamiltonian" in content,
            "mentions_zeta": "zeta" in content,
            "mentions_critical_line": "critical line" in content or "re(s)=1/2" in content or "re(s) = 1/2" in content,
            "has_explicit_math": any(sym in content for sym in ["d²/dx²", "d²/dx", "∫", "∑", "λ"]),
            "proposal_length": len(proposal.get("content", "")),
            "proposal_type": proposal.get("type", "unknown")
        }

        return features

    def score_proposal_quality(self, features: Dict, evaluation: Optional[Dict] = None) -> float:
        """Score how good a proposal is based on features and evaluation."""
        score = 0.5  # Base score

        # Feature scoring
        if features.get("mentions_berry_keating"):
            score += 0.15
        if features.get("mentions_gue"):
            score += 0.1
        if features.get("mentions_random_matrix"):
            score += 0.1
        if features.get("mentions_quantum"):
            score += 0.08
        if features.get("mentions_discretization"):
            score += 0.08
        if features.get("has_explicit_math"):
            score += 0.12

        # Evaluation scoring
        if evaluation:
            eval_score = evaluation.get("validation_score", 0.5)
            score = score * 0.4 + eval_score * 0.6  # Weight evaluation more

        return min(1.0, max(0.0, score))  # Clamp to [0, 1]

    def extract_success_patterns(self) -> Tuple[List[Dict], List[Dict]]:
        """Extract features from successful vs unsuccessful proposals."""
        successful_patterns = []
        unsuccessful_patterns = []

        for eval_file in self.evaluations_dir.glob("*.json"):
            try:
                evaluation = json.loads(eval_file.read_text())
                proposal_stem = eval_file.stem

                # Find corresponding proposal
                proposal_file = self.proposals_dir / f"{proposal_stem}.json"
                if not proposal_file.exists():
                    continue

                proposal = json.loads(proposal_file.read_text())
                features = self.extract_mathematical_features(proposal)
                quality_score = self.score_proposal_quality(features, evaluation)

                pattern_entry = {
                    "proposal_id": proposal_stem,
                    "features": features,
                    "quality_score": quality_score,
                    "validation_score": evaluation.get("validation_score", 0.5),
                    "type": proposal.get("type"),
                    "timestamp": evaluation.get("timestamp")
                }

                if quality_score > 0.65:
                    successful_patterns.append(pattern_entry)
                else:
                    unsuccessful_patterns.append(pattern_entry)

            except Exception as e:
                print(f"   [Dense-State] Error processing {eval_file.name}: {e}")

        return successful_patterns, unsuccessful_patterns

    def compute_feature_correlation_with_success(self, successful: List[Dict], unsuccessful: List[Dict]) -> Dict:
        """Compute which features correlate with successful proposals."""
        if not successful or not unsuccessful:
            return {}

        feature_keys = [k for k in successful[0].get("features", {}).keys() if isinstance(successful[0]["features"][k], bool)]

        correlations = {}
        for feature in feature_keys:
            success_count = sum(1 for p in successful if p.get("features", {}).get(feature, False))
            fail_count = sum(1 for p in unsuccessful if p.get("features", {}).get(feature, False))

            success_rate = success_count / len(successful) if successful else 0
            fail_rate = fail_count / len(unsuccessful) if unsuccessful else 0

            # Correlation: how much more likely to succeed if feature present
            correlation = success_rate - fail_rate

            correlations[feature] = {
                "correlation": correlation,
                "success_rate": success_rate,
                "fail_rate": fail_rate,
                "successes": success_count,
                "failures": fail_count
            }

        return correlations

    def encode_patterns_to_voxel_space(self, patterns: Dict) -> np.ndarray:
        """Encode feature correlations into 3D voxel space."""
        # Reset voxel grid
        voxel_grid = np.zeros((self.voxel_grid_size, self.voxel_grid_size, self.voxel_grid_size))

        # Map features to voxel coordinates
        feature_list = sorted(patterns.keys())

        for idx, feature in enumerate(feature_list[:512]):  # Max 512 features for 8x8x8 grid
            x = (idx // 64) % 8
            y = (idx // 8) % 8
            z = idx % 8

            correlation = patterns[feature].get("correlation", 0)
            # Normalize correlation to [0, 1] range
            voxel_value = (correlation + 1) / 2  # Convert [-1, 1] to [0, 1]
            voxel_grid[x, y, z] = voxel_value

        return voxel_grid

    def compute_resonance_hash(self, patterns: Dict) -> str:
        """Compute resonance hash of current pattern state."""
        pattern_str = json.dumps(patterns, sort_keys=True, default=str)
        return hashlib.sha256(pattern_str.encode()).hexdigest()[:16]

    def generate_learnings_report(self, successful: List[Dict], unsuccessful: List[Dict],
                                 correlations: Dict) -> Dict:
        """Generate insights from learned patterns."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "proposals_analyzed": len(successful) + len(unsuccessful),
            "successful_proposals": len(successful),
            "unsuccessful_proposals": len(unsuccessful),
            "success_rate": len(successful) / (len(successful) + len(unsuccessful)) if (len(successful) + len(unsuccessful)) > 0 else 0,
        }

        # Find top correlated features
        sorted_correlations = sorted(correlations.items(),
                                    key=lambda x: x[1]["correlation"],
                                    reverse=True)

        top_positive = sorted_correlations[:3]
        top_negative = sorted_correlations[-3:]

        report["top_success_indicators"] = [
            {
                "feature": name,
                "correlation": data["correlation"],
                "success_rate": data["success_rate"]
            }
            for name, data in top_positive
        ]

        report["top_failure_indicators"] = [
            {
                "feature": name,
                "correlation": data["correlation"],
                "success_rate": data["success_rate"]
            }
            for name, data in top_negative
        ]

        # Generate recommendations for Alpha
        recommendations = []

        for feature, data in top_positive:
            if data["correlation"] > 0.3:
                clean_feature = feature.replace("mentions_", "").replace("_", " ").title()
                recommendations.append(f"Emphasize {clean_feature} in proposals")

        for feature, data in top_negative:
            if data["correlation"] < -0.2:
                clean_feature = feature.replace("mentions_", "").replace("_", " ").title()
                recommendations.append(f"Avoid over-relying on {clean_feature}")

        report["recommendations_for_next_cycle"] = recommendations

        return report

    def run_learning_cycle(self) -> Dict:
        """Run complete learning extraction cycle."""
        print("\n[Dense-State Learner] Running pattern extraction cycle...")

        # Extract patterns
        successful, unsuccessful = self.extract_success_patterns()

        if not successful and not unsuccessful:
            print("   [Dense-State] No proposals to analyze yet")
            return {}

        print(f"   [Dense-State] Analyzed {len(successful)} successful, {len(unsuccessful)} unsuccessful proposals")

        # Compute feature correlations
        correlations = self.compute_feature_correlation_with_success(successful, unsuccessful)

        # Encode to voxel space
        voxel_grid = self.encode_patterns_to_voxel_space(correlations)

        # Compute resonance hash
        resonance_hash = self.compute_resonance_hash(correlations)

        # Generate learnings report
        report = self.generate_learnings_report(successful, unsuccessful, correlations)

        # Save learnings
        learnings = {
            "resonance_hash": resonance_hash,
            "timestamp": datetime.now().isoformat(),
            "correlations": {k: v for k, v in correlations.items()},
            "voxel_encoding_hash": hashlib.sha256(voxel_grid.tobytes()).hexdigest()[:16],
            "report": report
        }

        learnings_file = self.patterns_dir / f"learnings_{len(list(self.patterns_dir.glob('learnings_*.json')))}.json"
        learnings_file.write_text(json.dumps(learnings, indent=2, default=str))

        print(f"   [Dense-State] Resonance hash: {resonance_hash}")
        print(f"   [Dense-State] Success rate: {report['success_rate']:.1%}")
        print(f"   [Dense-State] Key indicators:")
        for item in report["top_success_indicators"][:2]:
            print(f"     ✓ {item['feature']}: {item['correlation']:.2f}")

        self.pattern_history.append({
            "resonance_hash": resonance_hash,
            "success_rate": report["success_rate"],
            "timestamp": datetime.now().isoformat()
        })

        return learnings

    def generate_feedback_for_alpha(self) -> str:
        """Generate feedback based on learned patterns."""
        if not self.pattern_history or not list(self.patterns_dir.glob("learnings_*.json")):
            return ""

        # Read most recent learnings
        learnings_files = sorted(self.patterns_dir.glob("learnings_*.json"))
        if not learnings_files:
            return ""

        latest = json.loads(learnings_files[-1].read_text())
        report = latest.get("report", {})

        feedback = "Based on analysis of successful and unsuccessful proposals:\n\n"

        feedback += "KEY PATTERNS FOR NEXT CYCLE:\n"
        for i, rec in enumerate(report.get("recommendations_for_next_cycle", [])[:4], 1):
            feedback += f"{i}. {rec}\n"

        feedback += f"\nCurrent success rate: {report.get('success_rate', 0):.1%}\n"
        feedback += f"Total proposals analyzed: {report.get('proposals_analyzed', 0)}\n"

        return feedback

    def detect_resonance_stability(self) -> Tuple[bool, str]:
        """Check if pattern resonance has stabilized (learning plateau)."""
        if len(self.pattern_history) < 3:
            return False, "Insufficient history"

        recent_hashes = [p["resonance_hash"] for p in self.pattern_history[-3:]]
        recent_rates = [p["success_rate"] for p in self.pattern_history[-3:]]

        # Check if hashes are repeating (pattern stability)
        hash_stability = len(set(recent_hashes)) <= 2

        # Check if success rates are converging
        rate_variance = np.var(recent_rates)
        rate_stability = rate_variance < 0.01

        is_stable = hash_stability and rate_stability
        reason = f"Hashes stable: {hash_stability}, Rate stable: {rate_stability} (var={rate_variance:.4f})"

        return is_stable, reason


def main():
    """Standalone test of dense-state learner."""
    from pathlib import Path
    import time

    session_dir = Path("agents/rh_session")
    session_dir.mkdir(parents=True, exist_ok=True)

    learner = RHDenseStateLearner(session_dir)

    print("="*70)
    print("RH DENSE-STATE LEARNING CYCLE")
    print("="*70)

    # Run learning cycle
    learnings = learner.run_learning_cycle()

    if learnings:
        print("\n[Dense-State] Learning Summary:")
        print(json.dumps(learnings, indent=2, default=str)[:500] + "...")

    # Generate feedback
    feedback = learner.generate_feedback_for_alpha()
    if feedback:
        print("\n[Dense-State] Feedback for Alpha:")
        print(feedback)

    # Check resonance
    is_stable, reason = learner.detect_resonance_stability()
    print(f"\n[Dense-State] Pattern stability: {is_stable} ({reason})")


if __name__ == "__main__":
    main()
