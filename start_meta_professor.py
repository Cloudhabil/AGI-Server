#!/usr/bin/env python3
"""
Start the Meta-Professor RH Research System

This is the entry point that launches the complete end-to-end system:
- StudentOrchestrator (manages active students)
- StudentSynthesizer (creates new agents dynamically)
- PatternGapDetector (analyzes research progress)
- CrossValidationHub (validates proposals)
- MetaProfessor (orchestrates everything)

Usage:
    python start_meta_professor.py [--duration MINUTES] [--session NAME]

Example:
    python start_meta_professor.py --duration 60 --session rh_breakthrough_v2
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Set up paths
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from rh_meta_professor import MetaProfessor


def print_banner():
    """Print startup banner."""
    print("\n" + "="*80)
    print("█" + " "*78 + "█")
    print("█" + " "*20 + "RH META-PROFESSOR: RESEARCH ORGANIZATION" + " "*18 + "█")
    print("█" + " "*78 + "█")
    print("█" + " "*15 + "Riemann Hypothesis Discovery via Synthesized Agents" + " "*13 + "█")
    print("█" + " "*78 + "█")
    print("="*80 + "\n")


def print_architecture():
    """Print system architecture."""
    architecture = """
SYSTEM ARCHITECTURE:
───────────────────

MetaProfessor (Orchestrator)
│
├─ StudentOrchestrator (Agent Factory)
│  ├─ QuarticStudent (Seed)
│  ├─ MorseStudent (Seed)
│  ├─ ExponentialStudent (Seed)
│  ├─ SpectralStudent (Seed)
│  └─ [Dynamically Synthesized Students...]
│
├─ StudentSynthesizer (GPIA Pipeline)
│  ├─ Phase 1: HUNT (Identify needs)
│  ├─ Phase 2: DISSECT (Extract patterns)
│  └─ Phase 3: SYNTHESIZE (Generate code)
│
├─ PatternGapDetector (Analysis)
│  ├─ Convergence Analysis
│  ├─ Parameter Space Coverage
│  ├─ Reasoning Blind Spots
│  └─ Emerging Patterns
│
└─ CrossValidationHub (Validation)
   ├─ Peer Review
   ├─ Consensus Detection
   ├─ Divergence Analysis
   └─ Confidence Scoring

RESEARCH LOOP:
──────────────

1. GENERATE PROPOSALS ──> [Students propose approaches]
2. CROSS-VALIDATE ─────> [Peers review each proposal]
3. DETECT GAPS ────────> [Analyze coverage & convergence]
4. SYNTHESIZE AGENTS ──> [Create specialized students]
5. FEEDBACK & LEARN ───> [Improve next cycle]
                          [Repeat]

EXPECTED OUTCOMES:
──────────────────

✓ Autonomous student agent generation
✓ Self-improving research organization
✓ Consensus-based validation
✓ Non-human specialization discovery
✓ Eigenvalue convergence improvement
✓ Multi-cycle learning progression
"""
    print(architecture)


def print_session_info(session_name: str, duration: int):
    """Print session configuration."""
    print("SESSION CONFIGURATION:")
    print("─" * 50)
    print(f"Session Name:       {session_name}")
    print(f"Duration:           {duration} minutes")
    print(f"Start Time:         {datetime.now().isoformat()}")
    print(f"Session Root:       agents/{session_name}/")
    print()


def print_startup_checklist():
    """Print pre-startup checklist."""
    checks = [
        ("OLLAMA running", "http://localhost:11434"),
        ("Models available", "deepseek-r1, qwen, codegemma"),
        ("Session directory", "agents/"),
        ("Write permissions", "agents/ directory"),
    ]

    print("STARTUP CHECKLIST:")
    print("─" * 50)
    for check, note in checks:
        print(f"  □ {check:<30} ({note})")
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Launch the Meta-Professor RH Research System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXAMPLES:
  python start_meta_professor.py
      → Run for default 30 minutes

  python start_meta_professor.py --duration 120
      → Run for 120 minutes (2 hours)

  python start_meta_professor.py --session rh_long_form --duration 180
      → Run custom session for 3 hours

CONTROL:
  Press Ctrl+C at any time to gracefully stop the research session.
  Results will be saved to agents/{session_name}/
        """
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
        default="rh_meta_research_v1",
        help="Session name (default: rh_meta_research_v1)"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Skip banner and info output"
    )

    args = parser.parse_args()

    # Print startup information
    if not args.quiet:
        print_banner()
        print_architecture()
        print_session_info(args.session, args.duration)
        print_startup_checklist()

    print("LAUNCHING META-PROFESSOR...")
    print("=" * 80)
    print()

    try:
        # Create and run Meta-Professor
        meta_prof = MetaProfessor(session_name=args.session)

        # Run research session
        meta_prof.run_research_session(duration_minutes=args.duration)

    except KeyboardInterrupt:
        print("\n\n" + "="*80)
        print("SHUTDOWN REQUESTED BY USER")
        print("="*80)
        print()
        print("Results saved to: agents/" + args.session + "/")
        print()
        print("Files generated:")
        print("  - meta_professor_final_report.json")
        print("  - gap_detection_report.json")
        print("  - cross_validation_report.json")
        print("  - cycle_N_summary.json (one per cycle)")
        print("  - synthesized_students/ (created agents)")
        print()

    except Exception as e:
        print("\n" + "="*80)
        print("ERROR DURING EXECUTION")
        print("="*80)
        print(f"\n{type(e).__name__}: {e}\n")
        print("Debugging info:")
        print(f"  Session: agents/{args.session}/")
        print(f"  Check for partial results in session directory")
        print()
        raise


if __name__ == "__main__":
    main()
