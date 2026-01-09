"""
RH Discovery Orchestrator - Main Controller

Orchestrates the complete Riemann Hypothesis discovery pipeline:
1. Alpha generates mathematical approaches
2. Professor validates with rigorous checks
3. Dense-state learner extracts patterns
4. Cognitive ecosystem evolves new approaches based on learnings
5. Iterate until breakthrough or resonance stability

Architecture: Multi-threaded with dense-state feedback loops
"""

import sys
import os
import time
import threading
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import numpy as np

# Set up paths
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

os.environ["OLLAMA_HOST"] = "localhost:11434"

from rh_alpha_professor_framework import RHAlpha, RHProfessor
from rh_dense_state_learner import RHDenseStateLearner


class RHDiscoveryOrchestrator:
    """Main orchestrator for RH research pipeline."""

    def __init__(self, session_name: str = "rh_research", duration_minutes: int = 20):
        self.session_name = session_name
        self.duration_seconds = duration_minutes * 60
        self.session_dir = REPO_ROOT / "agents" / session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.alpha = RHAlpha(self.session_dir)
        self.professor = RHProfessor(self.session_dir)
        self.learner = RHDenseStateLearner(self.session_dir)

        self.cycle = 0
        self.running = True
        self.breakthrough_indicators = []

        # Configuration
        self.min_high_promise_proposals = 2  # Stop early if found this many
        self.learning_check_interval = 120  # Check patterns every 2 minutes
        self.enable_cognitive_evolution = False  # Set to True to enable

    def monitor_high_promise_proposals(self) -> List[tuple]:
        """Monitor and report high-promise proposals."""
        high_promise = []

        evaluations = list(self.session_dir.glob("rh_evaluations/*.json"))
        for eval_file in evaluations:
            try:
                ev = json.loads(eval_file.read_text())
                if ev.get("validation_score", 0) > 0.65:
                    high_promise.append((eval_file.stem, ev["validation_score"], ev.get("proposal_type")))
            except:
                pass

        return sorted(high_promise, key=lambda x: x[1], reverse=True)

    def monitor_voxel_convergence(self) -> Tuple[bool, float]:
        """Monitor spatial variance for convergence detection (Phase 1 enhancement)."""
        try:
            voxels = self.learner.get_voxel_history(n_recent=5)

            if len(voxels) >= 3:
                # Compute spatial variance across voxel grids
                flat_voxels = [v.flatten() for v in voxels]
                spatial_variance = np.var(flat_voxels, axis=0).mean()

                # Convergence threshold (from Phase 1 design: variance < 0.01)
                convergence_threshold = 0.01
                is_converged = spatial_variance < convergence_threshold

                print(f"[ORCHESTRATOR] Voxel spatial variance: {spatial_variance:.6f}")

                if is_converged:
                    print(f"[ORCHESTRATOR] ✓ Patterns CONVERGED (variance < {convergence_threshold})")
                    print("[ORCHESTRATOR] → Mathematical patterns stabilized across cycles")
                    print("[ORCHESTRATOR] → Consider: Early stop or explore new parameter spaces")

                return is_converged, spatial_variance

            return False, 0.0

        except Exception as e:
            print(f"[ORCHESTRATOR] Warning: Could not monitor convergence: {e}")
            return False, 0.0

    def run_orchestration_cycle(self):
        """Run one complete orchestration cycle."""
        self.cycle += 1

        print(f"\n{'='*70}")
        print(f"[ORCHESTRATOR] === RESEARCH CYCLE {self.cycle} ===")
        print(f"{'='*70}")

        # Phase 1: Dense-State Learning (analyze previous cycle)
        print("\n[ORCHESTRATOR] Phase 1: Extracting mathematical patterns...")
        learnings = self.learner.run_learning_cycle()

        # Monitor voxel convergence (Phase 1 enhancement)
        is_converged, variance = self.monitor_voxel_convergence()

        if learnings:
            # Check for resonance stability
            is_stable, reason = self.learner.detect_resonance_stability()
            print(f"[ORCHESTRATOR] Pattern resonance stability: {is_stable}")

            # Generate feedback for Alpha
            feedback = self.learner.generate_feedback_for_alpha()
            if feedback:
                print("[ORCHESTRATOR] Feedback for next proposals:")
                for line in feedback.split('\n')[:5]:
                    if line.strip():
                        print(f"  {line}")

        # Phase 2: Monitor High-Promise Proposals
        print("\n[ORCHESTRATOR] Phase 2: Monitoring proposal quality...")
        high_promise = self.monitor_high_promise_proposals()

        if high_promise:
            print(f"[ORCHESTRATOR] Found {len(high_promise)} high-promise proposals:")
            for name, score, ptype in high_promise[:3]:
                print(f"  ✓ {ptype}: {score:.2f}")
                self.breakthrough_indicators.append({
                    "cycle": self.cycle,
                    "proposal": name,
                    "score": score,
                    "type": ptype,
                    "timestamp": datetime.now().isoformat()
                })

        # Phase 3: Cognitive Ecosystem Integration (optional)
        if self.enable_cognitive_evolution and len(high_promise) == 0:
            print("\n[ORCHESTRATOR] Phase 3: Spawning cognitive ecosystem evolution...")
            print("[ORCHESTRATOR] Note: Cognitive ecosystem integration coming soon")
            # This would spawn Hunter/Dissector/Synthesizer agents
            # to evolve new approaches based on pattern learnings

        # Phase 4: Report Status
        print("\n[ORCHESTRATOR] Phase 4: Research status report...")
        proposals_count = len(list(self.session_dir.glob("rh_proposals/*.json")))
        evaluations_count = len(list(self.session_dir.glob("rh_evaluations/*.json")))
        print(f"  Proposals generated: {proposals_count}")
        print(f"  Evaluations completed: {evaluations_count}")
        print(f"  High-promise count: {len(high_promise)}")
        print(f"  Breakthrough indicators: {len(self.breakthrough_indicators)}")

        # Check for breakthrough conditions
        if len(high_promise) >= self.min_high_promise_proposals:
            print("\n[ORCHESTRATOR] ⚡ BREAKTHROUGH INDICATOR DETECTED ⚡")
            print("[ORCHESTRATOR] High-promise proposals found - consider deeper analysis")
            self._save_breakthrough_report()

    def _save_breakthrough_report(self):
        """Save detailed report of breakthrough candidates."""
        report_file = self.session_dir / "breakthrough_analysis.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "cycle": self.cycle,
            "breakthrough_indicators": self.breakthrough_indicators,
            "high_promise_proposals": self.monitor_high_promise_proposals()
        }

        report_file.write_text(json.dumps(report, indent=2))
        print(f"[ORCHESTRATOR] Breakthrough analysis saved to {report_file}")

    def run_orchestration_session(self):
        """Run complete orchestration session."""
        print("="*70)
        print("RIEMANN HYPOTHESIS DISCOVERY ORCHESTRATOR")
        print("Multi-cycle Research Pipeline with Dense-State Learning")
        print("="*70)
        print()
        print(f"Session: {self.session_name}")
        print(f"Duration: {self.duration_seconds // 60} minutes")
        print(f"Session Dir: {self.session_dir}")
        print()
        print("Orchestration process:")
        print("  1. Alpha generates novel mathematical approaches")
        print("  2. Professor validates with rigorous analysis")
        print("  3. Dense-State Learner extracts success patterns")
        print("  4. Cognitive Ecosystem evolves based on learnings")
        print("  5. Iterate until breakthrough or convergence")
        print()
        print("Press Ctrl+C to stop early")
        print()

        start_time = datetime.now()
        last_learning_check = start_time

        # Start Alpha and Professor in background threads
        alpha_thread = threading.Thread(
            target=self.alpha.run_session,
            args=(self.duration_seconds,)
        )
        prof_thread = threading.Thread(
            target=self.professor.run_session,
            args=(self.duration_seconds,)
        )

        alpha_thread.daemon = True
        prof_thread.daemon = True

        alpha_thread.start()
        prof_thread.start()

        # Orchestration loop
        try:
            while self.running and (datetime.now() - start_time).total_seconds() < self.duration_seconds:
                current_time = datetime.now()

                # Run learning cycle every learning_check_interval seconds
                if (current_time - last_learning_check).total_seconds() >= self.learning_check_interval:
                    self.run_orchestration_cycle()
                    last_learning_check = current_time

                time.sleep(10)  # Check every 10 seconds

        except KeyboardInterrupt:
            print("\n[ORCHESTRATOR] Shutdown requested...")
            self.running = False
            self.alpha.running = False
            self.professor.running = False

        # Wait for threads to complete
        alpha_thread.join(timeout=10)
        prof_thread.join(timeout=10)

        # Final report
        self._generate_final_report()

    def _generate_final_report(self):
        """Generate comprehensive final research report."""
        elapsed = (datetime.now() - datetime.now()).total_seconds()  # Will be 0 if just started

        high_promise = self.monitor_high_promise_proposals()

        # Compile all learnings
        all_learnings = list(self.session_dir.glob("rh_patterns/learnings_*.json"))
        latest_learnings = {}
        if all_learnings:
            latest_learnings = json.loads(all_learnings[-1].read_text())

        final_report = {
            "session_name": self.session_name,
            "timestamp": datetime.now().isoformat(),
            "total_cycles": self.cycle,
            "statistics": {
                "proposals_generated": len(list(self.session_dir.glob("rh_proposals/*.json"))),
                "evaluations_completed": len(list(self.session_dir.glob("rh_evaluations/*.json"))),
                "high_promise_proposals": len(high_promise),
                "breakthrough_indicators": len(self.breakthrough_indicators)
            },
            "latest_patterns": latest_learnings.get("report", {}) if latest_learnings else {},
            "high_promise_proposals": [
                {
                    "proposal_id": name,
                    "score": score,
                    "type": ptype
                }
                for name, score, ptype in high_promise[:5]
            ],
            "breakthrough_history": self.breakthrough_indicators,
            "session_directory": str(self.session_dir)
        }

        report_file = self.session_dir / "final_research_report.json"
        report_file.write_text(json.dumps(final_report, indent=2))

        # Print summary
        print("\n" + "="*70)
        print("RH DISCOVERY RESEARCH SESSION COMPLETE")
        print("="*70)
        print()
        print(f"Session: {self.session_name}")
        print(f"Total cycles: {self.cycle}")
        print(f"Proposals generated: {final_report['statistics']['proposals_generated']}")
        print(f"Evaluations completed: {final_report['statistics']['evaluations_completed']}")
        print(f"High-promise proposals: {final_report['statistics']['high_promise_proposals']}")
        print(f"Breakthrough indicators: {final_report['statistics']['breakthrough_indicators']}")
        print()

        if high_promise:
            print("TOP HIGH-PROMISE PROPOSALS:")
            for name, score, ptype in high_promise[:5]:
                print(f"  * {ptype} (score: {score:.2f})")
        else:
            print("No high-promise proposals found in this session.")

        print()
        print(f"Full report saved to: {report_file}")
        print()
        print("Next Steps:")
        print("  1. Review high-promise proposals in detail")
        print("  2. Run deeper analysis on top candidates")
        print("  3. Launch cognitive ecosystem for approach evolution")
        print("  4. Continue research cycles to refine patterns")
        print()
        print("="*70)

        print(f"\n[COMPLETE] Research session concluded. Results in: {self.session_dir}")


def main():
    """Main entry point."""
    import sys

    # Parse command line arguments
    duration = 20  # Default 20 minutes
    session_name = "rh_research"

    if len(sys.argv) > 1:
        duration = int(sys.argv[1])
    if len(sys.argv) > 2:
        session_name = sys.argv[2]

    # Create and run orchestrator
    orchestrator = RHDiscoveryOrchestrator(
        session_name=session_name,
        duration_minutes=duration
    )

    orchestrator.run_orchestration_session()


if __name__ == "__main__":
    main()
