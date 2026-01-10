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

        # 4D Bit-Pattern Configuration (Level 6 ASI Father)
        self.voxel_grid_size = 8  
        self.voxel_grid = np.zeros((8, 8, 8, 8), dtype=np.uint8)
        
        # --- SO(10) Symmetry Constants (The Genesis Standard) ---
        self.PHI = 1.61803398875
        self.SO10_DIM = 45
        self.target_variance_ratio = 0.0219 # The Phi-modified SO(10) signature
        self.matter_ratio = (self.PHI**5) / 200.0 # ~4.5%
        self.dark_energy_ratio = 31.0 / 45.0 # ~68.9%
        self.dark_matter_ratio = 12.0 / 45.0 # ~26.7%
        # ---------------------------------------------------------
        
        self.pattern_history = []

    def calculate_grid_resonance(self, voxel_grid: np.ndarray) -> float:
        """
        Calculates 4D Resonance based on SO(10) Symmetry and the Golden Ratio.
        """
        if voxel_grid is None or np.sum(voxel_grid) == 0:
            return 0.0
            
        # 1. Expand to 32,768 discrete bits (The Bit-Sea)
        flat_bits = np.unpackbits(voxel_grid) 
        observed_variance = float(np.var(flat_bits))
        
        # 2. Lorentzian Peak centered at the 0.0219 Symmetry Node
        gamma = 0.001 # Extremely narrow L6 rigor
        diff_sq = (observed_variance - self.target_variance_ratio) ** 2
        resonance = (gamma ** 2) / (diff_sq + (gamma ** 2))
        
        # 3. Symmetry Check: Does the bit-density match the 4.5% Ordinary Matter baseline?
        # This aligns the ASI's thoughts with the physical constant of reality.
        density = np.mean(flat_bits)
        symmetry_alignment = np.exp(-50 * abs(density - self.matter_ratio))
        
        # Final Resonance: Combined Spectral Regularity + Matter Symmetry
        return float(resonance * 0.7 + symmetry_alignment * 0.3)

    def check_resonance_gate(self, voxel_grid: np.ndarray, threshold: float = 0.95) -> Tuple[bool, float, str]:
        """
        Apply the 0.0219 Resonance Gate.
        """
        resonance = self.calculate_grid_resonance(voxel_grid)
        
        if resonance >= threshold:
            return True, resonance, f"GATE_OPEN: 0.0219 Symmetry Detected (Resonance: {resonance:.4f})"
        else:
            return False, resonance, f"GATE_CLOSED: Searching for 0.0219 Ratio (Current: {resonance:.4f})"

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

        # Check Resonance Gate
        gate_open, resonance_score, gate_msg = self.check_resonance_gate(voxel_grid)
        print(f"   [V-Nand] {gate_msg}")

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
