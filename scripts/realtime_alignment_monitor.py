#!/usr/bin/env python3
"""
Real-Time Alignment Monitor

Run in separate terminal during 3-cycle test to see live progress:

Terminal 1:
    python scripts/alignment_calibration_3cycles.py

Terminal 2 (this script):
    python scripts/realtime_alignment_monitor.py alignment_calibration_3cycles

Shows live:
- Which cycle is running
- Which student is executing
- VRAM usage
- Progress toward 3-cycle completion
"""

import sys
import time
import sqlite3
from pathlib import Path
from datetime import datetime
import os


def clear_screen():
    """Clear terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def monitor_alignment(session_name: str, check_interval: int = 2):
    """Monitor alignment progress in real-time."""

    session_dir = Path("agents/sessions") / session_name
    db_path = session_dir / "scheduler_history" / "student_profiles.db"

    if not db_path.exists():
        print(f"Waiting for database at {db_path}...")
        while not db_path.exists():
            time.sleep(1)
        print("Database found! Starting monitoring...\n")
        time.sleep(2)

    print("="*80)
    print("REAL-TIME ALIGNMENT MONITOR")
    print("="*80)
    print(f"Session: {session_name}")
    print(f"Database: {db_path.name}")
    print(f"Update interval: {check_interval}s\n")

    last_run_count = 0
    last_cycle = 0

    while True:
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row

            # Get current progress
            cursor = conn.execute("""
                SELECT MAX(cycle) as max_cycle, COUNT(*) as total_runs
                FROM student_runs
            """)
            result = cursor.fetchone()
            max_cycle = result["max_cycle"] or 0
            total_runs = result["total_runs"]

            # Get detailed cycle info
            cursor = conn.execute("""
                SELECT cycle, COUNT(DISTINCT student) as unique_students,
                       ROUND(AVG(time_seconds), 1) as avg_time,
                       ROUND(AVG(vram_mb), 0) as avg_vram,
                       MAX(vram_mb) as peak_vram
                FROM student_runs
                GROUP BY cycle
                ORDER BY cycle
            """)

            cycle_data = {row["cycle"]: dict(row) for row in cursor.fetchall()}

            # Get latest run details
            cursor = conn.execute("""
                SELECT student, cycle, time_seconds, vram_mb, tokens
                FROM student_runs
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            latest = cursor.fetchone()

            # Get hardware status
            cursor = conn.execute("""
                SELECT timestamp, ROUND(vram_used/1024, 1) as vram_gb,
                       ROUND(vram_total/1024, 1) as vram_total_gb,
                       cpu_percent
                FROM hardware_snapshots
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            hw = cursor.fetchone()

            conn.close()

            # Display progress
            clear_screen()

            print("="*80)
            print("ALIGNMENT TEST PROGRESS")
            print("="*80)
            print(f"Time: {datetime.now().strftime('%H:%M:%S')}\n")

            # Current activity
            if latest:
                print("CURRENT ACTIVITY:")
                print("-"*80)
                print(f"Latest: {latest['student'].upper()} in Cycle {latest['cycle']}")
                print(f"  Time: {latest['time_seconds']:.1f}s")
                print(f"  VRAM: {latest['vram_mb']:.0f} MB")
                print(f"  Tokens: {latest['tokens']}")
                print()

            # Hardware status
            if hw:
                vram_pct = (hw["vram_used"] / hw["vram_total"]) * 100 if hw["vram_total"] else 0
                print("HARDWARE STATUS:")
                print("-"*80)
                print(f"VRAM: {hw['vram_used']:.1f} / {hw['vram_total']:.1f} GB ({vram_pct:.1f}%)", end="")
                if vram_pct > 85:
                    print(" ⚠️  CRITICAL")
                elif vram_pct > 75:
                    print(" ⚠️  HIGH")
                else:
                    print(" ✓ SAFE")
                print(f"CPU: {hw['cpu_percent']:.1f}%")
                print()

            # Cycle progress
            print("CYCLE PROGRESS:")
            print("-"*80)

            for cycle in range(1, 4):
                if cycle in cycle_data:
                    data = cycle_data[cycle]
                    students = data["unique_students"]
                    avg_time = data["avg_time"]
                    peak_vram = data["peak_vram"]

                    if students == 6:
                        status = "✓ COMPLETE"
                    elif students > 0:
                        status = f"~ IN PROGRESS ({students}/6)"
                    else:
                        status = "✗ NO DATA"

                    print(f"Cycle {cycle}: {status:25} | Avg: {avg_time:6.1f}s | Peak VRAM: {peak_vram:5.0f}MB")
                else:
                    print(f"Cycle {cycle}: ⏳ PENDING")

            print()

            # Completion estimate
            total_expected = 18  # 3 cycles × 6 students
            pct_complete = (total_runs / total_expected) * 100 if total_expected > 0 else 0

            print("OVERALL PROGRESS:")
            print("-"*80)
            print(f"Runs: {total_runs}/{total_expected} ({pct_complete:.0f}%)")

            if pct_complete < 100:
                progress_bar = "█" * int(pct_complete / 5) + "░" * (20 - int(pct_complete / 5))
                print(f"[{progress_bar}] {pct_complete:.0f}%")
            else:
                print("[████████████████████] 100% - TEST COMPLETE")

            print()
            print("="*80)
            print(f"Checking every {check_interval}s... (Ctrl+C to stop)")
            print("="*80)

            if total_runs != last_run_count or max_cycle != last_cycle:
                last_run_count = total_runs
                last_cycle = max_cycle
                time.sleep(check_interval)
            else:
                time.sleep(check_interval)

        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python realtime_alignment_monitor.py <session_name>")
        print("\nExample:")
        print("  python realtime_alignment_monitor.py alignment_calibration_3cycles")
        sys.exit(1)

    session_name = sys.argv[1]
    monitor_alignment(session_name)
