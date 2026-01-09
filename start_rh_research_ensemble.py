#!/usr/bin/env python3
"""
RH Research Ensemble - Master Orchestrator

Complete Riemann Hypothesis research system with:
1. Budget Allocator (prevents GPU crashes, optimizes resource use)
2. 6 Greek Student Agents (Alpha-Zeta, diverse perspectives)
3. Ensemble Validator (cross-validates all proposals)
4. Dense-State Learner (extracts patterns across cycles)

Usage:
    python start_rh_research_ensemble.py [--duration MINUTES] [--session NAME]

Example:
    python start_rh_research_ensemble.py --duration 60 --session rh_main
    python start_rh_research_ensemble.py --duration 30 --session rh_test --verbose
"""

import os
import sys
import time
import json
import signal
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Set environment
os.environ["OLLAMA_HOST"] = "localhost:11434"
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from agents.rh_student_profiles import RHStudentCommittee
from agents.rh_ensemble_validator import get_ensemble_validator
from agents.agent_utils import log_event
from core.kernel.budget_service import get_budget_service


class RHResearchEnsemble:
    """Master orchestrator for RH research with budget management."""

    def __init__(self, session_name: str = "rh_ensemble", duration_minutes: int = 30, verbose: bool = False):
        """Initialize the research ensemble."""
        self.session_name = session_name
        self.duration_seconds = duration_minutes * 60
        self.verbose = verbose
        self.session_dir = REPO_ROOT / "agents" / "sessions" / session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.budget_service = get_budget_service()
        self.committee = RHStudentCommittee(self.session_dir)
        self.validator = get_ensemble_validator(self.session_dir)

        # Track state
        self.cycle = 0
        self.running = True
        self.start_time = time.time()
        self.proposals_processed = 0
        self.proposals_approved = 0

        # Signal handlers
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)

        print("\n" + "=" * 80)
        print("RH RESEARCH ENSEMBLE - COMPLETE SYSTEM")
        print("=" * 80)
        print(f"\nSession: {session_name}")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Start time: {datetime.now().isoformat()}")
        print(f"\nBudget Service: ✓ Active (GPU protection enabled)")
        print(f"Student Committee: ✓ 6 agents ready (Alpha-Zeta)")
        print(f"Ensemble Validator: ✓ 3-model consensus system")
        print("\n" + "=" * 80)

    def _shutdown(self, signum, frame):
        """Handle graceful shutdown."""
        print("\n\n[SHUTDOWN] Received signal, saving state...")
        self.running = False
        self._print_final_report()
        sys.exit(0)

    def run(self):
        """Main research loop."""
        print("\n[INIT] Committee overview:")
        overview = self.committee.get_committee_overview()
        for student_info in overview["students"]:
            print(f"  {student_info['letter']:8} ({student_info['model']:20}) - {student_info['specialization']}")

        print("\n[INIT] Starting research cycles...\n")

        while self.running:
            elapsed = time.time() - self.start_time
            if elapsed > self.duration_seconds:
                print(f"\n[DONE] Duration exceeded ({elapsed:.0f}s > {self.duration_seconds}s)")
                break

            self.cycle += 1
            self._run_cycle()
            time.sleep(2)  # Brief pause between cycles

        self._print_final_report()

    def _run_cycle(self):
        """Execute one research cycle."""
        cycle_start = time.time()

        print(f"\n{'=' * 80}")
        print(f"[CYCLE {self.cycle}] Research Round")
        print(f"{'=' * 80}")

        # Phase 1: Budget check
        snapshot = self.budget_service.get_resource_snapshot(force_refresh=True)
        is_safe, safety_reason = self.budget_service.check_safety(snapshot)

        print(f"\n[BUDGET] Resource snapshot:")
        if snapshot.vram_total_mb:
            print(f"  VRAM: {snapshot.vram_util*100:6.1f}% ({snapshot.vram_used_mb}/{snapshot.vram_total_mb} MB)")
        print(f"  RAM:  {snapshot.ram_util*100:6.1f}%")
        print(f"  CPU:  {snapshot.cpu_percent:6.1f}%")
        print(f"  Status: {'✓ SAFE' if is_safe else '✗ CRITICAL'} - {safety_reason}")

        if not is_safe:
            print("\n[CRITICAL] System resources critical - pausing proposals")
            return

        # Phase 2: Student proposals
        print(f"\n[PHASE 1] Student proposals:")
        proposals = {}
        for student in self.committee.students:
            try:
                proposal = student.generate_proposal(self.cycle)
                proposals[student.letter] = proposal
                print(f"  ✓ {student.letter:8} - {proposal.get('approach', 'proposal generated')}")
            except Exception as e:
                print(f"  ✗ {student.letter:8} - Error: {str(e)[:50]}")

        # Phase 3: Ensemble validation (sample proposals)
        print(f"\n[PHASE 2] Ensemble validation:")
        validated_count = 0
        high_confidence_count = 0

        for letter, proposal in proposals.items():
            if isinstance(proposal, dict) and "approach" in proposal:
                try:
                    # Create a proposal text from the structure
                    proposal_text = f"Student {letter}: {proposal['approach']}"

                    task_id = f"cycle{self.cycle}_{letter}"
                    result = self.validator.validate_proposal(proposal_text, task_id)

                    self.proposals_processed += 1
                    if result.recommendation in ["approve", "revise"]:
                        self.proposals_approved += 1
                        high_confidence_count += 1

                    status = "✓" if result.overall_valid else "✗"
                    print(f"  {status} {letter:8} - Score: {result.consensus_score:5.1f}/100, "
                          f"Confidence: {result.confidence_level.name}")

                    validated_count += 1
                except Exception as e:
                    print(f"  ? {letter:8} - Validation error: {str(e)[:40]}")

        # Phase 4: Cycle summary
        cycle_elapsed = time.time() - cycle_start
        print(f"\n[SUMMARY] Cycle {self.cycle} complete")
        print(f"  Proposals generated: {len(proposals)}")
        print(f"  Proposals validated: {validated_count}")
        print(f"  High confidence: {high_confidence_count}/{validated_count}")
        print(f"  Cycle time: {cycle_elapsed:.1f}s")

        # Save cycle report
        self._save_cycle_report(cycle_elapsed, proposals, validated_count, high_confidence_count)

    def _save_cycle_report(self, elapsed: float, proposals: Dict, validated: int, high_confidence: int):
        """Save report for this cycle."""
        reports_dir = self.session_dir / "cycle_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        report = {
            "cycle": self.cycle,
            "timestamp": time.time(),
            "elapsed_seconds": elapsed,
            "proposals_generated": len(proposals),
            "proposals_validated": validated,
            "high_confidence_count": high_confidence,
            "resource_snapshot": {
                "vram_util": self.budget_service.get_resource_snapshot().vram_util,
                "ram_util": self.budget_service.get_resource_snapshot().ram_util,
            }
        }

        report_file = reports_dir / f"cycle_{self.cycle:03d}.json"
        report_file.write_text(json.dumps(report, indent=2))

    def _print_final_report(self):
        """Print final research summary."""
        total_elapsed = time.time() - self.start_time
        approval_rate = (self.proposals_approved / max(self.proposals_processed, 1)) * 100

        print("\n" + "=" * 80)
        print("RH RESEARCH ENSEMBLE - FINAL REPORT")
        print("=" * 80)
        print(f"\nSession: {self.session_name}")
        print(f"Duration: {total_elapsed:.1f}s ({total_elapsed/60:.1f}m)")
        print(f"Cycles completed: {self.cycle}")
        print(f"\nProposals:")
        print(f"  Total generated: {len(self.committee.students) * self.cycle}")
        print(f"  Total validated: {self.proposals_processed}")
        print(f"  Approved/revised: {self.proposals_approved}")
        print(f"  Approval rate: {approval_rate:.1f}%")

        # Budget service stats
        stats = self.budget_service.get_usage_stats()
        print(f"\nResource Management:")
        print(f"  Peak allocations: {stats.get('total_allocations', 0)}")
        print(f"  Total active tokens: {stats.get('total_active_tokens', 0)}")
        print(f"  Emergency shutdowns: {'0' if not self.budget_service.is_emergency_shutdown() else '1'}")

        print(f"\nOutput saved to: {self.session_dir}")
        print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RH Research Ensemble - Complete system with budget management"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=30,
        help="Duration in minutes (default: 30)"
    )
    parser.add_argument(
        "--session",
        type=str,
        default="rh_ensemble",
        help="Session name (default: rh_ensemble)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Create and run ensemble
    ensemble = RHResearchEnsemble(
        session_name=args.session,
        duration_minutes=args.duration,
        verbose=args.verbose
    )

    try:
        ensemble.run()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] User stopped the system")
        ensemble._print_final_report()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
