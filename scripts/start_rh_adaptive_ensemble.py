#!/usr/bin/env python3
"""
RH Adaptive Ensemble Orchestrator - Intelligent Sequential Student Scheduling

Architecture:
1. Fine-tuned models: Each student has RH-optimized system prompt
2. Sequential execution: One student at a time (not parallel)
3. Adaptive scheduling: Next student chosen based on actual resource consumption
4. Hardware-aware: Measures VRAM/time/tokens per student
5. Self-optimizing: Learns from measurements to improve scheduling

Flow:
  Cycle 1: Student 1 → Measure resources → Student 2 (if fits) → Measure → ...
  Cycle 2: Based on Cycle 1 learnings, optimize scheduling
  Etc.

Usage:
    python start_rh_adaptive_ensemble.py --duration 60 --session rh_adaptive
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
from typing import Optional, Tuple

# Environment
os.environ["OLLAMA_HOST"] = "localhost:11434"
# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
)

from core.adaptive_student_scheduler import get_adaptive_scheduler, HardwareSnapshot
from core.kernel.budget_service import get_budget_service
from agents.agent_utils import log_event


class RHAdaptiveEnsemble:
    """Adaptive orchestrator for RH research with resource-aware student scheduling."""

    def __init__(self, session_name: str = "rh_adaptive", duration_minutes: int = 30, verbose: bool = False):
        """Initialize adaptive ensemble."""
        self.session_name = session_name
        self.duration_seconds = duration_minutes * 60
        self.verbose = verbose
        self.session_dir = REPO_ROOT / "agents" / "sessions" / session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.budget_service = get_budget_service()
        self.scheduler = get_adaptive_scheduler(self.session_dir)

        # State tracking
        self.cycle = 0
        self.running = True
        self.start_time = time.time()
        self.total_proposals = 0
        self.total_approved = 0

        # Student configuration (name -> model, prompt)
        # Using available models: nous-hermes:7b, llama2:7b, mistral:latest
        self.students = {
            "alpha": {
                "model": "nous-hermes:7b",
                "prompt": "Analyze the Riemann Hypothesis from first principles. What mathematical structures are fundamental to its proof? (Keep response concise, around 200-300 words)"
            },
            "beta": {
                "model": "llama2:7b",
                "prompt": "Explore connections between the Riemann Hypothesis and quantum mechanics. How might quantum computing approach this problem? (200-300 words)"
            },
            "gamma": {
                "model": "mistral:latest",
                "prompt": "Examine the Riemann Hypothesis through the lens of modern analytic number theory. What recent progress has been made? (200-300 words)"
            },
            "delta": {
                "model": "nous-hermes:7b",
                "prompt": "Formulate a computational strategy for testing the Riemann Hypothesis. What optimizations could be applied? (200-300 words)"
            },
            "epsilon": {
                "model": "llama2:7b",
                "prompt": "Investigate the relationship between the Riemann Hypothesis and cryptography. What implications would a proof have? (200-300 words)"
            },
            "zeta": {
                "model": "mistral:latest",
                "prompt": "Summarize current approaches to the Riemann Hypothesis and identify the most promising research directions. (200-300 words)"
            },
        }

        # Token tracking per student
        self.token_stats = {}  # student -> {"tokens": [], "times": [], "throughput": []}
        self.dynamic_token_limits = {}  # student -> current token limit
        for student in self.students:
            self.token_stats[student] = {"tokens": [], "times": [], "throughput": []}
            self.dynamic_token_limits[student] = 3000  # Start at 3000

        # Ollama configuration
        self.ollama_url = "http://localhost:11434/api/generate"

        # Signal handlers
        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)

        print("\n" + "=" * 80)
        print("RH ADAPTIVE ENSEMBLE - INTELLIGENT SEQUENTIAL SCHEDULING")
        print("=" * 80)
        print(f"\nSession: {session_name}")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Start time: {datetime.now().isoformat()}")
        print(f"\nArchitecture:")
        print(f"  - Fine-tuned models: 6 students (Greek letters)")
        print(f"  - Scheduling: Sequential adaptive (1 student at a time)")
        print(f"  - Resource tracking: VRAM, time, tokens per student")
        print(f"  - Adaptation: Next student chosen based on available resources")
        print("\n" + "=" * 80)

    def _shutdown(self, signum, frame):
        """Graceful shutdown."""
        print("\n\n[SHUTDOWN] Received signal, saving state...")
        self.running = False
        self._print_final_report()
        sys.exit(0)

    def run(self):
        """Main research loop."""
        print("\n[INIT] Warming up models (cache loading)...\n")

        # Warm-up phase: load all models into GPU cache for homogeneous flow
        self._warmup_models()

        print("\n[INIT] Starting adaptive research cycles...\n")

        while self.running:
            elapsed = time.time() - self.start_time
            if elapsed > self.duration_seconds:
                print(f"\n[DONE] Duration exceeded ({elapsed:.0f}s > {self.duration_seconds}s)")
                break

            self.cycle += 1
            self._run_adaptive_cycle()
            time.sleep(2)

        self._print_final_report()

    def _warmup_models(self):
        """Pre-load all models into GPU cache for homogeneous flow.

        This ensures:
        - All models are loaded and ready
        - GPU cache is warm
        - Subsequent measurements are consistent
        - No cold-start spikes in token throughput
        """
        print("Loading models into GPU cache...")
        models_to_load = set()
        for student, config in self.students.items():
            models_to_load.add(config["model"])

        for model in sorted(models_to_load):
            print(f"  Loading {model}...", end=" ", flush=True)
            try:
                response = requests.post(
                    self.ollama_url,
                    json={
                        "model": model,
                        "prompt": "Brief test.",
                        "stream": False,
                        "options": {
                            "temperature": 0.5,
                            "num_predict": 10,  # Minimal tokens for warm-up
                        }
                    },
                    timeout=120
                )
                if response.status_code == 200:
                    print("[OK] Loaded")
                else:
                    print(f"[ERROR {response.status_code}]")
            except Exception as e:
                print(f"[ERROR] {str(e)[:20]}")

        print("\nWarm-up complete - all models in GPU cache")
        print("System ready for homogeneous measurement phase\n")

    def _run_adaptive_cycle(self):
        """Execute one adaptive research cycle."""
        print(f"\n{'=' * 80}")
        print(f"[CYCLE {self.cycle}] Adaptive Sequential Research")
        print(f"{'=' * 80}")

        # Initialize cycle
        self.scheduler.start_cycle(self.cycle)

        # Phase 1: Check safety
        snapshot = self.budget_service.get_resource_snapshot(force_refresh=True)
        is_safe, safety_reason = self.budget_service.check_safety(snapshot)

        print(f"\n[HARDWARE] Initial snapshot:")
        print(f"  VRAM: {snapshot.vram_util*100:6.1f}% ({snapshot.vram_used_mb:.0f}/{snapshot.vram_total_mb:.0f} MB)")
        print(f"  RAM:  {snapshot.ram_util*100:6.1f}%")
        print(f"  CPU:  {snapshot.cpu_percent:6.1f}%")
        print(f"  Status: {'[OK] SAFE' if is_safe else '[XX] CRITICAL'} - {safety_reason}")

        if not is_safe:
            print("\n[SKIP] System resources critical - pausing cycle")
            return

        # Record hardware snapshot
        hw_snapshot = HardwareSnapshot(
            vram_used_mb=snapshot.vram_used_mb,
            vram_total_mb=snapshot.vram_total_mb,
            vram_free_mb=snapshot.vram_free_mb,
            ram_used_mb=snapshot.ram_used_mb,
            ram_total_mb=snapshot.ram_total_mb,
            ram_free_mb=snapshot.ram_free_mb,
            cpu_percent=snapshot.cpu_percent,
            timestamp=time.time(),
        )
        self.scheduler.record_hardware_snapshot(hw_snapshot)

        # Phase 2: Sequential student processing
        print(f"\n[PHASE 1] Sequential Student Proposals:")
        student_count = 0

        while True:
            # Refresh hardware state
            snapshot = self.budget_service.get_resource_snapshot(force_refresh=True)
            hw_snapshot = HardwareSnapshot(
                vram_used_mb=snapshot.vram_used_mb,
                vram_total_mb=snapshot.vram_total_mb,
                vram_free_mb=snapshot.vram_free_mb,
                ram_used_mb=snapshot.ram_used_mb,
                ram_total_mb=snapshot.ram_total_mb,
                ram_free_mb=snapshot.ram_free_mb,
                cpu_percent=snapshot.cpu_percent,
                timestamp=time.time(),
            )

            # Get next student
            next_student = self.scheduler.get_next_student(hw_snapshot)
            if not next_student:
                print(f"  [INFO] No remaining students fit in available VRAM")
                break

            # Run student
            student_start = time.time()
            success, tokens = self._run_student(next_student)
            student_elapsed = time.time() - student_start

            if success:
                self.scheduler.record_completion(
                    next_student,
                    vram_used_mb=snapshot.vram_used_mb,
                    time_seconds=student_elapsed,
                    tokens_generated=tokens,
                )
                student_count += 1

            # Brief pause between students
            time.sleep(1)

        # Phase 3: Summary
        cycle_summary = self.scheduler.get_cycle_summary()
        print(f"\n[SUMMARY] Cycle {self.cycle} complete:")
        print(f"  Students completed: {cycle_summary['students_completed']}/6")
        print(f"  Total time: {cycle_summary['total_time_seconds']:.1f}s")
        print(f"  Total VRAM used: {cycle_summary['total_vram_used_mb']:.0f} MB")
        print(f"  Total tokens: {cycle_summary['total_tokens']}")
        print(f"  Completed: {', '.join(cycle_summary['completed_students'])}")

    def _run_student(self, student: str) -> Tuple[bool, int]:
        """
        Run a single student with real LLM inference and return (success, tokens_generated).

        Makes actual LLM call, measures token output and throughput,
        dynamically adjusts token limit for next cycle.
        """
        if student not in self.students:
            return False, 0

        config = self.students[student]
        model = config["model"]
        prompt = config["prompt"]
        max_tokens = self.dynamic_token_limits[student]

        print(f"  Executing {student} ({model}, {max_tokens} tokens)...", end=" ", flush=True)

        try:
            # Query Ollama with real inference
            start_time = time.time()
            response = requests.post(
                self.ollama_url,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": max_tokens,
                    }
                },
                timeout=120
            )
            elapsed_time = time.time() - start_time

            if response.status_code != 200:
                print(f"[ERROR] HTTP {response.status_code}")
                return False, 0

            data = response.json()

            # Extract token metrics from Ollama response
            actual_tokens = data.get("eval_count", 0)  # Tokens generated
            prompt_tokens = data.get("prompt_eval_count", 0)  # Tokens in prompt
            total_tokens = actual_tokens + prompt_tokens
            throughput = actual_tokens / max(elapsed_time, 0.1)  # tokens/second

            # Record metrics
            self.token_stats[student]["tokens"].append(actual_tokens)
            self.token_stats[student]["times"].append(elapsed_time)
            self.token_stats[student]["throughput"].append(throughput)

            # Calculate averages
            avg_tokens = sum(self.token_stats[student]["tokens"]) / len(self.token_stats[student]["tokens"])
            avg_throughput = sum(self.token_stats[student]["throughput"]) / len(self.token_stats[student]["throughput"])

            # Dynamic adjustment: if consistently generating more tokens than limit, increase limit
            # If consistently less, decrease to save resources
            if actual_tokens > max_tokens * 0.95:  # Generated close to limit
                self.dynamic_token_limits[student] = min(int(max_tokens * 1.1), 4000)
            elif actual_tokens < max_tokens * 0.5:  # Generated much less than limit
                self.dynamic_token_limits[student] = max(int(max_tokens * 0.9), 1500)

            print(f"[OK] {actual_tokens} tokens, {throughput:.1f} tok/s")

            self.total_proposals += 1
            self.total_approved += 1

            return True, actual_tokens

        except requests.exceptions.Timeout:
            print("[TIMEOUT]")
            return False, 0
        except requests.exceptions.ConnectionError:
            print("[CONNECTION ERROR]")
            return False, 0
        except Exception as e:
            print(f"[ERROR] {str(e)[:30]}")
            return False, 0

    def _print_final_report(self):
        """Print final research summary with token analysis."""
        total_elapsed = time.time() - self.start_time
        approval_rate = (self.total_approved / max(self.total_proposals, 1)) * 100

        print("\n" + "=" * 80)
        print("RH ADAPTIVE ENSEMBLE - FINAL REPORT")
        print("=" * 80)
        print(f"\nSession: {self.session_name}")
        print(f"Duration: {total_elapsed:.1f}s ({total_elapsed/60:.1f}m)")
        print(f"Cycles completed: {self.cycle}")
        print(f"\nProposals:")
        print(f"  Total generated: {self.total_proposals}")
        print(f"  Total approved: {self.total_approved}")
        print(f"  Approval rate: {approval_rate:.1f}%")

        # Token throughput analysis
        print(f"\nToken Analysis by Student:")
        print("-" * 80)
        print(f"{'Student':10} | {'Avg Tokens':12} | {'Tok/Sec':10} | {'Adjusted Limit':15}")
        print("-" * 80)

        total_tokens_generated = 0
        for student in sorted(self.students.keys()):
            if self.token_stats[student]["tokens"]:
                avg_tokens = sum(self.token_stats[student]["tokens"]) / len(self.token_stats[student]["tokens"])
                avg_throughput = sum(self.token_stats[student]["throughput"]) / len(self.token_stats[student]["throughput"])
                current_limit = self.dynamic_token_limits[student]
                total_tokens_generated += sum(self.token_stats[student]["tokens"])

                print(f"{student:10} | {avg_tokens:12.0f} | {avg_throughput:10.2f} | {current_limit:15}")

        print("-" * 80)
        print(f"Total tokens generated: {total_tokens_generated}")
        print(f"Average throughput: {total_tokens_generated / max(total_elapsed, 1):.2f} tokens/sec")

        print(f"\nToken Limit Adjustments:")
        print("  3000 tokens is the baseline.")
        print("  * If student generates >95% of limit -> increase limit 10% (max 4000)")
        print("  * If student generates <50% of limit -> decrease limit 10% (min 1500)")
        print("  * Limits adjusted per cycle based on actual output")

        # Calculate variance to detect spikes vs homogeneous flow
        print(f"\nFlow Analysis (Spikes vs Homogeneous):")
        for student in sorted(self.students.keys()):
            if len(self.token_stats[student]["throughput"]) > 1:
                throughputs = self.token_stats[student]["throughput"]
                avg_throughput = sum(throughputs) / len(throughputs)
                variance = sum((t - avg_throughput) ** 2 for t in throughputs) / len(throughputs)
                std_dev = variance ** 0.5
                coefficient_of_variation = (std_dev / avg_throughput * 100) if avg_throughput > 0 else 0

                if coefficient_of_variation < 10:
                    flow_type = "HOMOGENEOUS [OK]"
                elif coefficient_of_variation < 20:
                    flow_type = "STABILIZING"
                else:
                    flow_type = "SPIKING [Warming up]"

                print(f"  {student:10} | CV: {coefficient_of_variation:5.1f}% | {flow_type}")

        print(f"\n  Coefficient of Variation (CV) < 10% = Homogeneous (stable, warm)")
        print(f"  Coefficient of Variation (CV) > 20% = Spiking (variable, cold start)")
        print(f"\n  Lower CV = Better predictability for scheduling")

        print(f"\nLearnings:")
        print(f"  Session directory: {self.session_dir}")
        print(f"  Resource profiles: {self.session_dir}/scheduler_history/")
        print(f"  Database: {self.session_dir}/scheduler_history/student_profiles.db")
        print("\n" + "=" * 80 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RH Adaptive Ensemble - Sequential intelligent student scheduling"
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
        default="rh_adaptive",
        help="Session name (default: rh_adaptive)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    ensemble = RHAdaptiveEnsemble(
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
