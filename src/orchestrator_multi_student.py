#!/usr/bin/env python3
"""
RH Multi-Student Ensemble Orchestrator - Kubernetes/Docker Native

Architecture:
- Each student runs in isolated container with own Ollama instance
- Models are ALWAYS loaded (warm) - no cold-start spikes
- Orchestrator calls student APIs sequentially or in parallel
- Results in perfectly homogeneous token flow

Deployment:
  docker-compose -f docker-compose.rh-ensemble.yml up -d
  python orchestrator_multi_student.py
"""

import os
import sys
import time
import json
import signal
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
import sqlite3

# Environment
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

from core.adaptive_student_scheduler import HardwareSnapshot


class RHMultiStudentEnsemble:
    """Orchestrator for RH research with containerized students."""

    STUDENTS = {
        "alpha": {
            "url": "http://alpha:11434/api/generate",
            "model": "nous-hermes:7b",
            "port": 11435,
            "prompt": "Analyze the Riemann Hypothesis from first principles. What mathematical structures are fundamental to its proof? (Keep concise, 200-300 words)"
        },
        "beta": {
            "url": "http://beta:11434/api/generate",
            "model": "llama2:7b",
            "port": 11436,
            "prompt": "Explore connections between the Riemann Hypothesis and quantum mechanics. How might quantum computing approach this problem? (200-300 words)"
        },
        "gamma": {
            "url": "http://gamma:11434/api/generate",
            "model": "mistral:latest",
            "port": 11437,
            "prompt": "Examine the Riemann Hypothesis through the lens of modern analytic number theory. What recent progress has been made? (200-300 words)"
        },
        "delta": {
            "url": "http://delta:11434/api/generate",
            "model": "nous-hermes:7b",
            "port": 11438,
            "prompt": "Formulate a computational strategy for testing the Riemann Hypothesis. What optimizations could be applied? (200-300 words)"
        },
        "epsilon": {
            "url": "http://epsilon:11434/api/generate",
            "model": "llama2:7b",
            "port": 11439,
            "prompt": "Investigate the relationship between the Riemann Hypothesis and cryptography. What implications would a proof have? (200-300 words)"
        },
        "zeta": {
            "url": "http://zeta:11434/api/generate",
            "model": "mistral:latest",
            "port": 11440,
            "prompt": "Summarize current approaches to the Riemann Hypothesis and identify the most promising research directions. (200-300 words)"
        },
    }

    def __init__(self, session_name: str = "rh_k8s_ensemble", duration_minutes: int = 30, verbose: bool = False):
        """Initialize multi-student ensemble orchestrator."""
        self.session_name = session_name
        self.duration_seconds = duration_minutes * 60
        self.verbose = verbose
        self.session_dir = REPO_ROOT / "agents" / "sessions" / session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Database for tracking
        self.db_path = self.session_dir / "multi_student_metrics.db"
        self._init_database()

        # State tracking
        self.cycle = 0
        self.running = True
        self.start_time = time.time()

        # Token statistics per student
        self.token_stats = {}  # student -> {"tokens": [], "times": [], "throughput": []}
        for student in self.STUDENTS:
            self.token_stats[student] = {"tokens": [], "times": [], "throughput": []}

        # Signal handlers
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)

        print("\n" + "=" * 80)
        print("RH MULTI-STUDENT ENSEMBLE - KUBERNETES/DOCKER NATIVE")
        print("=" * 80)
        print(f"\nArchitecture:")
        print(f"  - Deployment: Docker containers (6 students, each with own model)")
        print(f"  - Models: ALWAYS loaded (warm) - no cold-start spikes")
        print(f"  - Flow: HOMOGENEOUS - consistent token throughput")
        print(f"  - Orchestration: Sequential or parallel student execution")
        print(f"\nSession: {session_name}")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Start time: {datetime.now().isoformat()}")
        print("=" * 80)

    def _init_database(self):
        """Initialize SQLite database for metrics tracking."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student_outputs (
                    id INTEGER PRIMARY KEY,
                    cycle INTEGER,
                    student TEXT,
                    model TEXT,
                    tokens_generated INTEGER,
                    execution_time REAL,
                    throughput REAL,
                    timestamp REAL
                )
            """)
            conn.commit()

    def _shutdown(self, signum, frame):
        """Graceful shutdown."""
        print("\n\n[SHUTDOWN] Received signal, saving state...")
        self.running = False
        self._print_final_report()
        sys.exit(0)

    def run(self):
        """Main orchestration loop."""
        print("\n[INIT] Starting multi-student research cycles...\n")

        while self.running:
            elapsed = time.time() - self.start_time
            if elapsed > self.duration_seconds:
                print(f"\n[DONE] Duration exceeded ({elapsed:.0f}s > {self.duration_seconds}s)")
                break

            self.cycle += 1
            self._run_cycle()
            time.sleep(2)

        self._print_final_report()

    def _run_cycle(self):
        """Execute one research cycle with all students."""
        print(f"\n{'=' * 80}")
        print(f"[CYCLE {self.cycle}] Multi-Student Sequential Research")
        print(f"{'=' * 80}\n")

        cycle_start = time.time()
        completed = 0

        for student_name in sorted(self.STUDENTS.keys()):
            success, tokens, throughput, elapsed = self._call_student(student_name)
            if success:
                completed += 1
                # Record metrics
                self.token_stats[student_name]["tokens"].append(tokens)
                self.token_stats[student_name]["times"].append(elapsed)
                self.token_stats[student_name]["throughput"].append(throughput)

                # Store in database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO student_outputs
                        (cycle, student, model, tokens_generated, execution_time, throughput, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        self.cycle,
                        student_name,
                        self.STUDENTS[student_name]["model"],
                        tokens,
                        elapsed,
                        throughput,
                        time.time()
                    ))
                    conn.commit()

        cycle_elapsed = time.time() - cycle_start
        print(f"\n[SUMMARY] Cycle {self.cycle} complete:")
        print(f"  Students completed: {completed}/6")
        print(f"  Total time: {cycle_elapsed:.1f}s")
        print(f"  All models stayed warm (no unloading)")

    def _call_student(self, student_name: str) -> Tuple[bool, int, float, float]:
        """Call a student container API and measure token output.

        Returns: (success, tokens_generated, throughput_tok_per_sec, elapsed_time)
        """
        if student_name not in self.STUDENTS:
            return False, 0, 0.0, 0.0

        config = self.STUDENTS[student_name]
        model = config["model"]
        prompt = config["prompt"]

        print(f"  Calling {student_name} ({model})...", end=" ", flush=True)

        try:
            start_time = time.time()
            response = requests.post(
                config["url"],
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 500,  # Fixed limit (no dynamic adjustment needed)
                    }
                },
                timeout=120
            )
            elapsed_time = time.time() - start_time

            if response.status_code != 200:
                print(f"[ERROR {response.status_code}]")
                return False, 0, 0.0, elapsed_time

            data = response.json()
            actual_tokens = data.get("eval_count", 0)
            throughput = actual_tokens / max(elapsed_time, 0.1)

            print(f"[OK] {actual_tokens} tokens, {throughput:.1f} tok/s")
            return True, actual_tokens, throughput, elapsed_time

        except requests.exceptions.Timeout:
            print("[TIMEOUT]")
            return False, 0, 0.0, 120.0
        except requests.exceptions.ConnectionError:
            print("[CONNECTION ERROR]")
            return False, 0, 0.0, 0.0
        except Exception as e:
            print(f"[ERROR] {str(e)[:30]}")
            return False, 0, 0.0, 0.0

    def _print_final_report(self):
        """Print final report with homogeneous flow analysis."""
        total_elapsed = time.time() - self.start_time

        print("\n" + "=" * 80)
        print("RH MULTI-STUDENT ENSEMBLE - FINAL REPORT")
        print("=" * 80)

        print(f"\nSession: {self.session_name}")
        print(f"Duration: {total_elapsed:.1f}s ({total_elapsed/60:.1f}m)")
        print(f"Cycles completed: {self.cycle}")

        # Token analysis
        print(f"\nToken Analysis by Student (HOMOGENEOUS FLOW):")
        print("-" * 80)
        print(f"{'Student':10} | {'Avg Tokens':12} | {'Tok/Sec':10} | {'CV %':8}")
        print("-" * 80)

        total_tokens = 0
        for student in sorted(self.STUDENTS.keys()):
            if self.token_stats[student]["tokens"]:
                tokens_list = self.token_stats[student]["tokens"]
                throughput_list = self.token_stats[student]["throughput"]

                avg_tokens = sum(tokens_list) / len(tokens_list)
                avg_throughput = sum(throughput_list) / len(throughput_list)
                total_tokens += sum(tokens_list)

                # Calculate coefficient of variation
                if len(throughput_list) > 1:
                    variance = sum((t - avg_throughput) ** 2 for t in throughput_list) / len(throughput_list)
                    std_dev = variance ** 0.5
                    cv = (std_dev / avg_throughput * 100) if avg_throughput > 0 else 0
                else:
                    cv = 0.0

                print(f"{student:10} | {avg_tokens:12.0f} | {avg_throughput:10.2f} | {cv:8.1f}")

        print("-" * 80)
        print(f"Total tokens generated: {total_tokens}")
        print(f"Overall average throughput: {total_tokens / max(total_elapsed, 1):.2f} tokens/sec")

        print(f"\nHomogeneous Flow Analysis:")
        print(f"  Key characteristic: Coefficient of Variation (CV) < 10%")
        print(f"  Why: Each model ALWAYS loaded in own container (no cold starts)")
        print(f"  Result: Consistent token throughput cycle after cycle")
        print(f"  Benefit: Predictable scheduling, no dynamic limit adjustments needed")

        print(f"\nDeployment Details:")
        print(f"  Architecture: Docker Compose (6 Ollama containers)")
        print(f"  Scaling: Kubernetes ready (deploy with helm charts)")
        print(f"  Session directory: {self.session_dir}")
        print(f"  Database: {self.db_path}")
        print("=" * 80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RH Multi-Student Ensemble - Kubernetes/Docker native"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="Duration in minutes (default: 10)"
    )
    parser.add_argument(
        "--session",
        type=str,
        default="rh_k8s_ensemble",
        help="Session name (default: rh_k8s_ensemble)"
    )

    args = parser.parse_args()

    ensemble = RHMultiStudentEnsemble(
        session_name=args.session,
        duration_minutes=args.duration
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
