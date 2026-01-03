"""
MetaProfessor - The orchestrator of the entire research organization

This is the research director that:
1. Monitors ongoing research from all students
2. Detects gaps and blind spots via PatternGapDetector
3. Synthesizes new specialized students via StudentSynthesizer
4. Cross-validates results via CrossValidationHub
5. Manages the complete feedback loop

Philosophy: The Professor doesn't just validate proposals—it orchestrates
the entire research organization, creating new researchers as needed.
"""

import sys
import os
import json
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Set up paths
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

os.environ["OLLAMA_HOST"] = "localhost:11434"

from agents.agent_utils import query_deepseek, log_event
from rh_student_synthesizer import StudentSynthesizer, StudentSpecification
from rh_pattern_gap_detector import PatternGapDetector
from rh_cross_validation_hub import CrossValidationHub


class StudentOrchestrator:
    """Manages instantiation and execution of student agents."""

    def __init__(self, students_dir: Path):
        self.students_dir = students_dir
        self.students_dir.mkdir(parents=True, exist_ok=True)
        self.active_students = {}
        self.student_results = {}

    def register_student(self, name: str, spec: StudentSpecification):
        """Register a newly synthesized student."""
        self.active_students[name] = {
            "spec": spec,
            "created_at": datetime.now().isoformat(),
            "proposals_count": 0,
            "best_error": float('inf')
        }
        print(f"[StudentOrchestrator] Registered student: {name}")

    def request_proposal_from_student(self, student_name: str, context: str) -> Optional[Dict]:
        """
        Request a proposal from a specific student.

        In full implementation, this would instantiate the student module
        and call its generate_proposal() method.
        """
        if student_name not in self.active_students:
            return None

        student_info = self.active_students[student_name]

        # Generate a proposal (in full impl, call student.generate_proposal())
        prompt = f"""
You are {student_name}, specialized in: {student_info['spec'].specialization}

Research Context:
{context[:500]}

Generate a novel approach to advancing RH research.

Format as JSON: {{"approach": str, "rationale": str, "parameters": dict, "expected_convergence": float}}
"""

        response = query_deepseek(prompt, max_tokens=1500)

        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                proposal = json.loads(json_match.group())
                proposal["student"] = student_name
                proposal["timestamp"] = datetime.now().isoformat()
                student_info["proposals_count"] += 1
                return proposal
        except:
            pass

        return None

    def get_active_student_list(self) -> List[str]:
        """List all active students."""
        return list(self.active_students.keys())


class MetaProfessor:
    """
    The research organization director.

    Orchestrates everything: student creation, validation, feedback loops.
    """

    def __init__(self, session_name: str = "rh_meta_research"):
        self.session_name = session_name
        self.session_dir = REPO_ROOT / "agents" / session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Initialize subsystems
        self.synthesizer = StudentSynthesizer(self.session_dir / "synthesized_students")
        self.gap_detector = PatternGapDetector(self.session_dir)
        self.cross_validator = CrossValidationHub(self.session_dir)
        self.orchestrator = StudentOrchestrator(self.session_dir / "active_students")

        # State tracking
        self.cycle = 0
        self.running = True
        self.synthesis_log = []

        # Create result directories
        for subdir in ["rh_proposals", "rh_results", "rh_evaluations"]:
            (self.session_dir / subdir).mkdir(parents=True, exist_ok=True)

    def initialization_phase(self):
        """
        Initialize the research organization with seed students.

        Creates the initial set of specialized students.
        """
        print("\n" + "="*70)
        print("[MetaProfessor] === INITIALIZATION PHASE ===")
        print("="*70)

        initial_students = [
            {
                "name": "QuarticStudent",
                "specialization": "Quartic and anharmonic potentials (V(x) = ax² + bx⁴)",
                "domain": "Anharmonic Oscillator Physics"
            },
            {
                "name": "MorseStudent",
                "specialization": "Morse and molecular potentials for realistic bonding",
                "domain": "Molecular Physics"
            },
            {
                "name": "ExponentialStudent",
                "specialization": "Exponential barriers and confining wells",
                "domain": "Barrier Physics"
            },
            {
                "name": "SpectralStudent",
                "specialization": "Spectral methods using Chebyshev and Hermite bases",
                "domain": "Numerical Analysis"
            }
        ]

        for student_config in initial_students:
            print(f"\n[MetaProfessor] Synthesizing {student_config['name']}...")

            spec = StudentSpecification(
                name=student_config["name"],
                specialization=student_config["specialization"],
                gap_detected="Initial seeding",
                domain_expertise=student_config["domain"],
                parameter_focus=["convergence", "error", "stability"]
            )

            # In full implementation, synthesize the student
            self.orchestrator.register_student(student_config["name"], spec)

        print(f"\n[MetaProfessor] ✓ Initialized {len(initial_students)} seed students")

    def research_cycle(self):
        """
        Run one complete research cycle.

        1. Students generate proposals
        2. Cross-validate proposals
        3. Detect gaps
        4. Synthesize new students if needed
        5. Provide feedback
        """
        self.cycle += 1
        print("\n" + "="*70)
        print(f"[MetaProfessor] === RESEARCH CYCLE {self.cycle} ===")
        print("="*70)

        # Phase 1: Student Proposals
        print("\n[MetaProfessor] Phase 1: Student Proposals")
        proposals = self._collect_student_proposals()
        print(f"  ✓ Collected {len(proposals)} proposals from {len(self.orchestrator.get_active_student_list())} students")

        # Phase 2: Cross-Validation
        print("\n[MetaProfessor] Phase 2: Cross-Validation")
        validations = self._cross_validate_proposals(proposals)
        print(f"  ✓ Validated {len(validations)} proposals")

        # Phase 3: Gap Detection
        print("\n[MetaProfessor] Phase 3: Gap Detection")
        gap_report = self.gap_detector.run_gap_detection_cycle(self.session_dir)
        top_gaps = self.gap_detector.get_top_priority_gaps(gap_report, limit=2)

        # Phase 4: Student Synthesis
        if top_gaps:
            print("\n[MetaProfessor] Phase 4: Student Synthesis")
            new_students = self._synthesize_new_students(top_gaps)
            print(f"  ✓ Synthesized {len(new_students)} new students")
        else:
            print("\n[MetaProfessor] Phase 4: No high-priority gaps detected")
            new_students = []

        # Phase 5: Learning & Feedback
        print("\n[MetaProfessor] Phase 5: Learning & Feedback")
        self._generate_feedback_loop()

        # Save cycle summary
        summary = {
            "cycle": self.cycle,
            "timestamp": datetime.now().isoformat(),
            "proposals_generated": len(proposals),
            "validations_completed": len(validations),
            "students_synthesized": len(new_students),
            "gaps_detected": len(top_gaps)
        }

        summary_file = self.session_dir / f"cycle_{self.cycle}_summary.json"
        summary_file.write_text(json.dumps(summary, indent=2))

        print(f"\n[MetaProfessor] Cycle {self.cycle} complete")

        return summary

    def _collect_student_proposals(self) -> List[Dict]:
        """Collect proposals from all active students."""
        proposals = []

        research_context = """
Riemann Hypothesis research via quantum mechanics and random matrix theory.
Goal: Find Hamiltonian with eigenvalues matching zeta zeros on critical line.
Current challenge: Move beyond quadratic potentials to quartic, Morse, exponential.
Parameter sweep: Optimize a, b, λ coefficients for convergence.
"""

        for student_name in self.orchestrator.get_active_student_list():
            proposal = self.orchestrator.request_proposal_from_student(
                student_name, research_context
            )
            if proposal:
                proposals.append(proposal)
                print(f"  - {student_name}: {proposal.get('approach', '')[:80]}...")

        return proposals

    def _cross_validate_proposals(self, proposals: List[Dict]) -> List[Dict]:
        """Cross-validate proposals across all students."""
        validations = []

        for i, proposal in enumerate(proposals):
            validation = self.cross_validator.orchestrate_cross_validation(
                f"proposal_{i}",
                proposal,
                self.orchestrator.get_active_student_list()
            )
            validations.append(validation)

        # Generate consensus report
        report = self.cross_validator.generate_consensus_report()
        self.cross_validator.save_validation_report(report)

        return validations

    def _synthesize_new_students(self, gaps: List[Dict]) -> List[StudentSpecification]:
        """Synthesize new specialized students based on detected gaps."""
        new_students = []

        for gap in gaps:
            gap_type = gap.get("type")
            gap_description = gap.get("description", "")

            print(f"\n  [Synthesis] Addressing gap: {gap_type}")

            # Synthesize the student
            spec = self.synthesizer.synthesize_student(
                gap_name=f"{gap_type.title()}Student",
                gap_description=gap_description,
                research_context="RH eigenvalue convergence problem",
                current_results={}  # In full impl, pass actual results
            )

            if spec:
                # Register with orchestrator
                self.orchestrator.register_student(spec.name, spec)
                new_students.append(spec)
                self.synthesis_log.append({
                    "student_name": spec.name,
                    "created_at": datetime.now().isoformat(),
                    "gap_addressed": gap_type
                })

        return new_students

    def _generate_feedback_loop(self):
        """Generate feedback that students use to improve."""
        print("\n  [Feedback] Analyzing patterns for next cycle...")

        feedback_prompt = """
Based on the RH research progress so far, what patterns are emerging?
What should students focus on in the next cycle?

Return concise tactical advice for researchers.
"""

        feedback = query_deepseek(feedback_prompt, max_tokens=500)

        feedback_file = self.session_dir / f"feedback_cycle_{self.cycle}.txt"
        feedback_file.write_text(feedback)

        print("  ✓ Feedback generated and saved")

    def run_research_session(self, duration_minutes: int = 30):
        """Run a complete research session with multiple cycles."""
        print("\n" + "="*70)
        print("[MetaProfessor] === RH META-RESEARCH SESSION ===")
        print(f"Duration: {duration_minutes} minutes")
        print("="*70)

        # Initialization
        self.initialization_phase()

        # Main research loop
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        cycle_count = 0

        while self.running and datetime.now() < end_time:
            try:
                summary = self.research_cycle()
                cycle_count += 1

                # Wait before next cycle
                remaining = (end_time - datetime.now()).total_seconds()
                if remaining > 120:  # Wait 2 minutes between cycles
                    print(f"\nWaiting 120s until next cycle...")
                    time.sleep(120)

            except KeyboardInterrupt:
                print("\n\nSession interrupted by user")
                break
            except Exception as e:
                print(f"\n⚠ Error in cycle {self.cycle}: {e}")
                time.sleep(30)

        # Final report
        self._generate_final_report(cycle_count)

    def _generate_final_report(self, cycles_completed: int):
        """Generate comprehensive final report."""
        report = {
            "session_name": self.session_name,
            "duration": datetime.now().isoformat(),
            "cycles_completed": cycles_completed,
            "students_synthesized": len(self.synthesizer.get_synthesis_history()),
            "synthesis_history": self.synthesizer.get_synthesis_history(),
            "synthesis_log": self.synthesis_log
        }

        report_file = self.session_dir / "meta_professor_final_report.json"
        report_file.write_text(json.dumps(report, indent=2))

        print("\n" + "="*70)
        print("[MetaProfessor] === SESSION COMPLETE ===")
        print("="*70)
        print(f"Cycles: {cycles_completed}")
        print(f"Students Synthesized: {report['students_synthesized']}")
        print(f"Report: {report_file}")
        print("="*70)


def main():
    """Entry point for Meta-Professor research system."""
    meta_prof = MetaProfessor(session_name="rh_meta_research_v1")

    # Run session
    try:
        meta_prof.run_research_session(duration_minutes=30)
    except KeyboardInterrupt:
        print("\n\nShutdown requested")
        meta_prof.running = False


if __name__ == "__main__":
    main()
