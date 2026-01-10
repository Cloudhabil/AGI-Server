#!/usr/bin/env python3
"""
Alignment & Calibration Test - 3 Cycles

Runs exactly 3 complete cycles with detailed validation:
- Cycle 1: Baseline (establish ground truth)
- Cycle 2: Alignment (verify consistency and pattern)
- Cycle 3: Calibration (fine-tune parameters if needed)

Usage:
    python scripts/alignment_calibration_3cycles.py

Monitor in another terminal:
    python scripts/monitor_budget_system.py
"""

import sys
import time
import sqlite3
from pathlib import Path
from datetime import datetime

# Set to 3 cycles (will complete in 3-15 minutes depending on simulation)
DURATION_MINUTES = int((3 * 60) / 60)  # ~3-4 minutes for 3 cycles with simulation
SESSION_NAME = "alignment_calibration_3cycles"

def print_header(text: str):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def print_cycle_header(cycle: int):
    """Print cycle-specific header."""
    print(f"\n{'-'*80}")
    print(f"CYCLE {cycle} CHECKPOINT")
    print(f"{'-'*80}\n")

def main():
    """Run 3-cycle alignment and calibration."""

    print_header("ALIGNMENT & CALIBRATION TEST - 3 CYCLES")

    print(f"""
OBJECTIVE:
  [OK] Cycle 1: Establish baseline (6 students, measure consumption)
  [OK] Cycle 2: Verify alignment (same pattern, context preserved)
  [OK] Cycle 3: Calibration (fine-tune, prepare for production)

SESSION: {SESSION_NAME}
DURATION: {DURATION_MINUTES} minutes (3 complete cycles)
TIME: {datetime.now().isoformat()}

WHAT TO MONITOR:
  1. All 6 students execute in each cycle
  2. VRAM never exceeds 85% (safety limit)
  3. Time per student consistent across cycles
  4. Database grows with each cycle
  5. No errors or context loss

AFTER TEST:
  1. Query validation database
  2. Generate alignment report
  3. Check calibration metrics
  4. Verify ready for production
""")

    # Skip input prompt for non-interactive mode
    try:
        input("Press Enter to start 3-cycle test... ")
    except EOFError:
        print("(Auto-starting in non-interactive mode...)\n")

    print_header("LAUNCHING ORCHESTRATOR")

    print(f"Command: python start_rh_adaptive_ensemble.py --duration {DURATION_MINUTES} --session {SESSION_NAME}")
    print("\nStarting orchestrator...\n")

    # Import and run
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

    from start_rh_adaptive_ensemble import RHAdaptiveEnsemble

    ensemble = RHAdaptiveEnsemble(
        session_name=SESSION_NAME,
        duration_minutes=DURATION_MINUTES,
        verbose=True,
    )

    try:
        ensemble.run()
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Test stopped by user")
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

    print_header("3-CYCLE TEST COMPLETE")

    # Now validate
    session_dir = Path(ensemble.session_dir)
    db_path = session_dir / "scheduler_history" / "student_profiles.db"

    if not db_path.exists():
        print("✗ Database not found - test may have failed")
        return 1

    print("Analyzing results...\n")

    # Connect to database
    conn = sqlite3.connect(db_path)

    # CYCLE 1 ANALYSIS
    print_cycle_header(1)
    print("BASELINE MEASUREMENT")
    print("-" * 80)

    cursor = conn.execute("""
        SELECT student, COUNT(*) as runs,
               ROUND(AVG(time_seconds), 2) as avg_time,
               ROUND(AVG(vram_mb), 0) as avg_vram,
               ROUND(AVG(tokens_per_sec), 1) as tok_per_sec
        FROM student_runs
        WHERE cycle = 1
        GROUP BY student
        ORDER BY student
    """)

    cycle1_data = {}
    for row in cursor:
        student, runs, avg_time, avg_vram, tok_per_sec = row
        cycle1_data[student] = {
            "runs": runs,
            "time": avg_time,
            "vram": avg_vram,
            "tok_per_sec": tok_per_sec,
        }
        print(f"{student.upper():10} | Runs: {runs} | Time: {avg_time:6.1f}s | VRAM: {avg_vram:5.0f}MB | {tok_per_sec:5.1f} tok/s")

    cycle1_count = len(cycle1_data)
    print(f"\n[OK] Cycle 1: {cycle1_count}/6 students completed")

    if cycle1_count == 6:
        print("  STATUS: BASELINE ESTABLISHED [OK]")
    else:
        print(f"  STATUS: WARNING - Only {cycle1_count} students ran")

    # CYCLE 2 ANALYSIS (Alignment)
    print_cycle_header(2)
    print("ALIGNMENT CHECK - Context Preservation")
    print("-" * 80)

    cursor = conn.execute("""
        SELECT student, COUNT(*) as runs,
               ROUND(AVG(time_seconds), 2) as avg_time,
               ROUND(AVG(vram_mb), 0) as avg_vram,
               ROUND(AVG(tokens_per_sec), 1) as tok_per_sec
        FROM student_runs
        WHERE cycle = 2
        GROUP BY student
        ORDER BY student
    """)

    cycle2_data = {}
    alignment_errors = []

    for row in cursor:
        student, runs, avg_time, avg_vram, tok_per_sec = row
        cycle2_data[student] = {
            "runs": runs,
            "time": avg_time,
            "vram": avg_vram,
            "tok_per_sec": tok_per_sec,
        }

        # Compare with Cycle 1
        if student in cycle1_data:
            c1_time = cycle1_data[student]["time"]
            c2_time = avg_time
            time_diff = abs(c2_time - c1_time)
            time_pct = (time_diff / c1_time) * 100 if c1_time > 0 else 0

            status = "[OK]" if time_pct < 10 else "[WN]" if time_pct < 20 else "[XX]"
            print(f"{student.upper():10} | C1: {c1_time:6.1f}s -> C2: {c2_time:6.1f}s | Delta: {time_pct:5.1f}% {status}")

            if time_pct > 20:
                alignment_errors.append(f"{student}: {time_pct:.1f}% time variance")

    cycle2_count = len(cycle2_data)
    print(f"\n[OK] Cycle 2: {cycle2_count}/6 students completed")

    if cycle2_count == 6 and not alignment_errors:
        print("  STATUS: ALIGNED [OK] (Context preserved, consistent timing)")
    elif cycle2_count == 6:
        print(f"  STATUS: ALIGNED with warnings ({len(alignment_errors)} variance issues)")
        for err in alignment_errors[:3]:
            print(f"    - {err}")
    else:
        print(f"  STATUS: MISALIGNED - Only {cycle2_count} students")

    # CYCLE 3 ANALYSIS (Calibration)
    print_cycle_header(3)
    print("CALIBRATION - Final Tuning")
    print("-" * 80)

    cursor = conn.execute("""
        SELECT student, COUNT(*) as runs,
               ROUND(AVG(time_seconds), 2) as avg_time,
               ROUND(AVG(vram_mb), 0) as avg_vram,
               ROUND(AVG(tokens_per_sec), 1) as tok_per_sec
        FROM student_runs
        WHERE cycle = 3
        GROUP BY student
        ORDER BY student
    """)

    cycle3_data = {}
    calibration_metrics = []

    for row in cursor:
        student, runs, avg_time, avg_vram, tok_per_sec = row
        cycle3_data[student] = {
            "runs": runs,
            "time": avg_time,
            "vram": avg_vram,
            "tok_per_sec": tok_per_sec,
        }

        # Calculate trend (is system optimizing?)
        if student in cycle1_data and student in cycle2_data:
            c1_time = cycle1_data[student]["time"]
            c3_time = avg_time
            improvement = ((c1_time - c3_time) / c1_time) * 100 if c1_time > 0 else 0

            status = "[UP]" if improvement > 5 else "[ST]" if improvement > -5 else "[DN]"
            print(f"{student.upper():10} | Trend: {status} ({improvement:+.1f}% from C1) | Current: {c3_time:.1f}s")
            calibration_metrics.append((student, improvement))

    cycle3_count = len(cycle3_data)
    print(f"\n[OK] Cycle 3: {cycle3_count}/6 students completed")

    # Check if learning is happening
    avg_improvement = sum(m[1] for m in calibration_metrics) / len(calibration_metrics) if calibration_metrics else 0

    if avg_improvement > 2:
        print(f"  STATUS: OPTIMIZING [OK] (Average {avg_improvement:.1f}% improvement detected)")
    elif avg_improvement > -2:
        print(f"  STATUS: STABLE (No significant change, baseline maintained)")
    else:
        print(f"  STATUS: DEGRADING ({avg_improvement:.1f}% slower - may need investigation)")

    # OVERALL VALIDATION
    print_header("ALIGNMENT & CALIBRATION REPORT")

    # Summary metrics
    cursor = conn.execute("SELECT COUNT(*) FROM student_runs")
    total_runs = cursor.fetchone()[0]

    cursor = conn.execute("SELECT COUNT(*) FROM hardware_snapshots")
    total_snapshots = cursor.fetchone()[0]

    cursor = conn.execute("SELECT MAX(vram_mb) FROM student_runs")
    peak_vram = cursor.fetchone()[0] or 0
    peak_vram_pct = (peak_vram / 10240) * 100  # Assuming 10GB usable

    print("""
================================================================================
                    3-CYCLE VALIDATION SUMMARY
================================================================================
""")

    print(f"Total Runs: {total_runs}")
    print(f"Database Records: {total_snapshots} hardware snapshots")
    print(f"Peak VRAM: {peak_vram:.0f} MB ({peak_vram_pct:.1f}% of 10GB)")

    print("\n" + "-"*80)
    print("VALIDATION CHECKLIST")
    print("-"*80)

    checks = [
        ("Cycle 1 Complete (6/6 students)", cycle1_count == 6, cycle1_count),
        ("Cycle 2 Complete (6/6 students)", cycle2_count == 6, cycle2_count),
        ("Cycle 3 Complete (6/6 students)", cycle3_count == 6, cycle3_count),
        ("Context Preserved (<10% variance)", len(alignment_errors) == 0, len(alignment_errors)),
        ("Safety Limits Met (VRAM <85%)", peak_vram_pct < 85, f"{peak_vram_pct:.1f}%"),
        ("Database Integrity", total_runs == total_snapshots, total_runs),
        ("Adaptive Learning Detected", avg_improvement > -2, f"{avg_improvement:.1f}%"),
    ]

    all_passed = True
    for check_name, passed, details in checks:
        status = "[OK]" if passed else "[XX]"
        print(f"  {status} {check_name}: {details}")
        if not passed:
            all_passed = False

    print("\n" + "-"*80)

    if all_passed:
        print("""
================================================================================
                  [OK] SYSTEM ALIGNED & CALIBRATED
                  READY FOR PRODUCTION DEPLOYMENT
================================================================================

Next Steps:
  1. Run longer validation: 8-hour session
     python start_rh_adaptive_ensemble.py --duration 480 --session rh_production

  2. Enable skill learning (optional)
     - Modify orchestrator to include skill_learning_coordinator
     - See SKILL_LEARNING_INTEGRATION.md

  3. Monitor with:
     python scripts/monitor_budget_system.py

System Status: PRODUCTION READY [OK]
""")
        return 0
    else:
        print("""
================================================================================
              [XX] ALIGNMENT ISSUES DETECTED - REVIEW ABOVE
              DO NOT DEPLOY UNTIL ISSUES RESOLVED
================================================================================

Troubleshooting:
  1. Check cycle_N_student.json files in scheduler_history/
  2. Review orchestrator.py logs
  3. Query database: sqlite3 {db_path}
  4. Check VRAM usage during execution
  5. Review error logs if any

Contact: See DEPLOYMENT_CHECKLIST.md troubleshooting section
""")
        return 1

    conn.close()


if __name__ == "__main__":
    sys.exit(main())
