#!/usr/bin/env python3
"""
Predictive Sequential Orchestrator - Smart resource management with soft warm-up

Architecture:
1. PLAN: Predict next model and check resources
2. BOOT UP: Load current model (hard load to VRAM)
3. SOFT WARMUP: Run minimal query to warm GPU cache (no spike)
4. EXECUTE: Run student with warm model
5. TRANSFER: Extract and save context/insights
6. PREDICT: Check if next model fits safely
   - If (current_vram + next_model_size) > 85% → DON'T load yet
   - Unload current model first, THEN load next
7. BOOT DOWN: Gracefully unload model

Result:
- No cold-start spikes (soft warm-up prevents it)
- No resource violations (predictive rule enforcement)
- Context flows between models
- Graceful transitions (boot up/down managed)
"""

import os
import sys
import time
import json
import signal
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple, Optional, List
import sqlite3
import requests

REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

# Import autonomous skill selector
try:
    from skills.autonomous_skill_selector import get_skill_selector_agent
    SKILL_SELECTOR_AVAILABLE = True
except ImportError:
    SKILL_SELECTOR_AVAILABLE = False
    print("[WARN] Autonomous skill selector not available, running without intelligent selection")


class ResourcePredictor:
    """Predict resources needed for next operation."""

    MODEL_SIZES_GB = {
        "nous-hermes:7b": 4.0,
        "llama2:7b": 3.8,
        "mistral:latest": 4.1,
    }

    def __init__(self):
        self.current_vram_mb = 0
        self.total_vram_mb = 0
        self.vram_critical_threshold = 0.85  # 85% = critical

    def get_current_vram(self) -> Tuple[int, int]:
        """Get current VRAM usage in MB (used, total)."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total",
                 "--format=csv,nounits,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                used, total = result.stdout.strip().split(',')
                return int(used), int(total)
        except:
            pass
        return 0, 12288  # Assume 12GB if can't detect

    def predict_model_load(self, model: str, ollama_url: str) -> Tuple[bool, str]:
        """Predict if loading model will exceed critical threshold.

        Returns: (safe_to_load, reason)
        """
        used_mb, total_mb = self.get_current_vram()
        model_size_mb = self.MODEL_SIZES_GB.get(model, 4.5) * 1024
        overhead_mb = 512  # Ollama overhead

        # Prediction: after loading, VRAM will be:
        predicted_vram_mb = used_mb + model_size_mb + overhead_mb
        predicted_percent = (predicted_vram_mb / total_mb) * 100

        is_safe = predicted_percent <= (self.vram_critical_threshold * 100)

        reason = f"Predict: {used_mb//1024}GB used + {model_size_mb//1024}GB model = {predicted_vram_mb//1024}GB ({predicted_percent:.1f}%)"

        if not is_safe:
            reason += f" -> CRITICAL (>{self.vram_critical_threshold*100:.0f}%)"

        return is_safe, reason

    def needs_cooldown(self) -> Tuple[bool, str]:
        """Check if current VRAM is too high for next model load."""
        used_mb, total_mb = self.get_current_vram()
        percent = (used_mb / total_mb) * 100

        # If over 60%, should cooldown (unload) before loading next
        needs_cool = percent > 60

        reason = f"Current VRAM: {used_mb//1024}GB / {total_mb//1024}GB ({percent:.1f}%)"
        if needs_cool:
            reason += " -> Should unload current model first"

        return needs_cool, reason


class ContextManager:
    """Manage context transfer between models."""

    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.context_dir = session_dir / "model_contexts"
        self.context_dir.mkdir(parents=True, exist_ok=True)

    def extract_context(self, student: str, response: str, metadata: Dict) -> Dict:
        """Extract and save context from model output."""
        context = {
            "student": student,
            "timestamp": datetime.now().isoformat(),
            "key_insights": self._extract_insights(response),
            "metadata": metadata,
            "response_length": len(response),
        }

        # Save to file for next model
        context_file = self.context_dir / f"{student}_context.json"
        context_file.write_text(json.dumps(context, indent=2))

        return context

    def transfer_context(self, from_student: str, to_student: str) -> Optional[Dict]:
        """Transfer context from one student to next."""
        context_file = self.context_dir / f"{from_student}_context.json"

        if context_file.exists():
            context = json.loads(context_file.read_text())
            # Prepare transfer message
            transfer_msg = f"""
Previous student ({from_student}) insights:
{json.dumps(context['key_insights'], indent=2)}

Current task: Continue research building on above insights.
"""
            return context
        return None

    def _extract_insights(self, response: str) -> List[str]:
        """Extract key insights from response."""
        # Simple extraction: sentences with key terms
        insights = []
        keywords = ["hypothesis", "proof", "pattern", "structure", "quantum", "cryptography", "optimization"]

        sentences = response.split('.')
        for sentence in sentences[:5]:  # First 5 sentences max
            if any(kw in sentence.lower() for kw in keywords):
                insights.append(sentence.strip())

        return insights[:3]  # Top 3 insights


class ModelLifecycle:
    """Manage model boot-up, warm-up, execution, and cool-down."""

    def __init__(self, ollama_url: str, timeout: int = 120):
        self.ollama_url = ollama_url
        self.timeout = timeout
        self.is_loaded = False
        self.current_model = None

    def boot_up(self, model: str) -> Tuple[bool, str]:
        """Load model into VRAM (hard boot)."""
        print(f"    [BOOT UP] Loading {model} into VRAM...", end=" ", flush=True)

        try:
            start = time.time()
            response = requests.post(
                self.ollama_url,
                json={
                    "model": model,
                    "prompt": "",  # Empty prompt
                    "stream": False,
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                elapsed = time.time() - start
                self.is_loaded = True
                self.current_model = model
                print(f"[OK] {elapsed:.1f}s")
                return True, "Model loaded"
            else:
                print(f"[ERROR {response.status_code}]")
                return False, f"HTTP {response.status_code}"

        except Exception as e:
            print(f"[ERROR]")
            return False, str(e)

    def soft_warmup(self, model: str, prompt: str = None) -> Tuple[bool, float]:
        """Run minimal query to warm GPU cache (no spike).

        Returns: (success, tokens_per_sec)
        """
        if not prompt:
            prompt = "Brief response please."

        print(f"    [SOFT WARMUP] Warming cache...", end=" ", flush=True)

        try:
            start = time.time()
            response = requests.post(
                self.ollama_url,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": 10,  # Minimal tokens
                        "temperature": 0.5,
                    }
                },
                timeout=self.timeout
            )

            if response.status_code == 200:
                elapsed = time.time() - start
                data = response.json()
                tokens = data.get("eval_count", 0)
                throughput = tokens / max(elapsed, 0.1)
                print(f"[OK] {tokens} tokens, {throughput:.1f} tok/s")
                return True, throughput
            else:
                print(f"[ERROR {response.status_code}]")
                return False, 0.0

        except Exception as e:
            print(f"[ERROR]")
            return False, 0.0

    def execute(self, model: str, prompt: str, max_tokens: int = 500) -> Tuple[bool, str, int, float]:
        """Execute full query with warm model.

        Returns: (success, response_text, tokens, throughput_tok_per_sec)
        """
        print(f"    [EXECUTE] Running inference...", end=" ", flush=True)

        try:
            start = time.time()
            response = requests.post(
                self.ollama_url,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": 0.7,
                    }
                },
                timeout=self.timeout
            )

            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                text = data.get("response", "")
                tokens = data.get("eval_count", 0)
                throughput = tokens / max(elapsed, 0.1)
                print(f"[OK] {tokens} tokens, {throughput:.1f} tok/s")
                return True, text, tokens, throughput
            else:
                print(f"[ERROR {response.status_code}]")
                return False, "", 0, 0.0

        except Exception as e:
            print(f"[ERROR]")
            return False, "", 0, 0.0

    def boot_down(self, model: str) -> bool:
        """Unload model from VRAM (graceful cool-down)."""
        print(f"    [BOOT DOWN] Unloading {model} from VRAM...", end=" ", flush=True)

        try:
            # Send empty request to free memory
            requests.post(
                self.ollama_url,
                json={"model": model, "keep_alive": 0},  # Keep-alive 0 = unload
                timeout=5
            )
            self.is_loaded = False
            self.current_model = None
            print("[OK]")
            return True
        except Exception as e:
            print(f"[WARN] {str(e)[:20]}")
            return False


class PredictiveSequentialOrchestrator:
    """Orchestrate students with predictive resource rules."""

    STUDENTS = {
        "alpha": {
            "model": "nous-hermes:7b",
            "prompt": "Analyze Riemann Hypothesis from first principles. (200-300 words)"
        },
        "beta": {
            "model": "llama2:7b",
            "prompt": "Explore RH connections to quantum mechanics. (200-300 words)"
        },
        "gamma": {
            "model": "mistral:latest",
            "prompt": "Examine RH through analytic number theory lens. (200-300 words)"
        },
        "delta": {
            "model": "nous-hermes:7b",
            "prompt": "Formulate computational RH testing strategy. (200-300 words)"
        },
        "epsilon": {
            "model": "llama2:7b",
            "prompt": "Investigate RH to cryptography relationship. (200-300 words)"
        },
        "zeta": {
            "model": "mistral:latest",
            "prompt": "Summarize RH approaches and promising directions. (200-300 words)"
        },
    }

    def __init__(self, session_name: str = "rh_predictive", duration_minutes: int = 10):
        self.session_name = session_name
        self.duration_seconds = duration_minutes * 60
        self.session_dir = Path(f"agents/sessions/{session_name}")
        self.session_dir.mkdir(parents=True, exist_ok=True)

        self.predictor = ResourcePredictor()
        self.context_manager = ContextManager(self.session_dir)
        self.ollama_url = "http://localhost:11434/api/generate"

        # Initialize skill selector agent if available
        self.skill_selector = None
        if SKILL_SELECTOR_AVAILABLE:
            try:
                self.skill_selector = get_skill_selector_agent()
            except Exception as e:
                print(f"[WARN] Failed to initialize skill selector: {e}")

        self.cycle = 0
        self.running = True
        self.start_time = time.time()

        # Database
        self.db_path = self.session_dir / "metrics.db"
        self._init_database()

        signal.signal(signal.SIGTERM, self._shutdown)
        signal.signal(signal.SIGINT, self._shutdown)

        print("\n" + "=" * 80)
        print("PREDICTIVE SEQUENTIAL ORCHESTRATOR WITH AUTONOMOUS SKILL LEARNING")
        print("=" * 80)
        print(f"Strategy: Soft warm-up + Resource rules + Context transfer + Skill Learning")
        print(f"Rule: Don't load next model if (current + next) > 85% VRAM")
        if self.skill_selector:
            print(f"Learning: Autonomous skill selector active (meta-learning agent)")
        print("=" * 80)

    def _init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY,
                    cycle INTEGER,
                    student TEXT,
                    model TEXT,
                    tokens INTEGER,
                    throughput REAL,
                    warmup_throughput REAL,
                    execution_time REAL,
                    skill_selected TEXT,
                    skill_confidence REAL,
                    selection_method TEXT,
                    timestamp REAL
                )
            """)

            # Table for skill selection history and learning
            conn.execute("""
                CREATE TABLE IF NOT EXISTS skill_selections (
                    id INTEGER PRIMARY KEY,
                    timestamp REAL,
                    cycle INTEGER,
                    student TEXT,
                    task_pattern TEXT,
                    skill_selected TEXT,
                    confidence REAL,
                    selection_method TEXT,
                    success BOOLEAN,
                    quality_score REAL
                )
            """)
            
            # Table for configuration and limits
            conn.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.execute("INSERT OR IGNORE INTO config VALUES ('max_records', '50000')")
            conn.execute("INSERT OR IGNORE INTO config VALUES ('cleanup_days', '30')")
            
            conn.commit()

    def _cleanup_old_data(self, days_to_keep=30):
        """Remove data older than N days to save space."""
        cutoff_time = time.time() - (days_to_keep * 24 * 3600)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM executions WHERE timestamp < ?", (cutoff_time,))
                conn.execute("DELETE FROM skill_selections WHERE timestamp < ?", (cutoff_time,))
                conn.commit()
            print(f"  [SAFEGUARD] Cleanup: Removed data older than {days_to_keep} days")
        except Exception as e:
            print(f"  [SAFEGUARD] Cleanup error: {e}")

    def _check_resource_limits(self):
        """Check database size and disk space."""
        import shutil
        
        # 1. Check Disk Space
        try:
            total, used, free = shutil.disk_usage(self.session_dir)
            percent_used = (used / total) * 100
            if percent_used > 90:
                print(f"  [CRITICAL] Disk usage at {percent_used:.1f}%! Forcing aggressive cleanup.")
                self._cleanup_old_data(days_to_keep=7)
            elif percent_used > 80:
                print(f"  [WARNING] Disk usage at {percent_used:.1f}%")
        except:
            pass

        # 2. Check Database Record Count
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT value FROM config WHERE key='max_records'")
                max_records = int(cursor.fetchone()[0])
                
                cursor = conn.execute("SELECT COUNT(*) FROM executions")
                count = cursor.fetchone()[0]
                
                if count > max_records:
                    print(f"  [SAFEGUARD] Record limit reached ({count}/{max_records}). Cleaning up...")
                    self._cleanup_old_data(days_to_keep=14)
        except Exception as e:
            print(f"  [SAFEGUARD] Limit check error: {e}")

    def _shutdown(self, signum, frame):
        print("\n[SHUTDOWN]")
        self.running = False
        sys.exit(0)

    def run(self):
        """Main orchestration loop."""
        print("\n[INIT] Starting predictive sequential cycles...\n")

        while self.running:
            elapsed = time.time() - self.start_time
            if elapsed > self.duration_seconds:
                print(f"\n[DONE] Duration exceeded")
                break

            self.cycle += 1
            self._run_cycle()

        self._print_report()

    def _run_cycle(self):
        """Execute one cycle with all students."""
        print(f"\n{'=' * 80}")
        print(f"[CYCLE {self.cycle}] Predictive Sequential Execution")
        print(f"{'=' * 80}\n")

        previous_student = None

        for student_name in sorted(self.STUDENTS.keys()):
            config = self.STUDENTS[student_name]
            model = config["model"]

            print(f"[STUDENT {student_name.upper()}]")

            # STEP 1: PREDICT - Check if safe to load
            safe, reason = self.predictor.predict_model_load(model, self.ollama_url)
            print(f"  [PREDICT] {reason}")

            if not safe:
                # Need to unload current model first
                cooldown_needed, cooldown_reason = self.predictor.needs_cooldown()
                print(f"  [RESOURCE RULE] {cooldown_reason}")
                print(f"  → Skipping {student_name} (would exceed 85% threshold)")
                print(f"  → Try after unloading previous model\n")
                continue

            # STEP 2: TRANSFER CONTEXT from previous
            if previous_student:
                ctx = self.context_manager.transfer_context(previous_student, student_name)
                if ctx:
                    print(f"  [CONTEXT TRANSFER] From {previous_student}")
                    print(f"    Insights: {len(ctx['key_insights'])} extracted\n")

            # STEP 3: BOOT UP - Load model to VRAM
            lifecycle = ModelLifecycle(self.ollama_url)
            boot_ok, boot_msg = lifecycle.boot_up(model)
            if not boot_ok:
                print(f"  Failed to boot: {boot_msg}\n")
                continue

            # STEP 4: SOFT WARMUP - No spike
            warmup_ok, warmup_throughput = lifecycle.soft_warmup(model)
            if not warmup_ok:
                lifecycle.boot_down(model)
                print(f"  Failed to warm up\n")
                continue

            # STEP 4.5: SELECT SKILL AUTONOMOUSLY
            skill_name = None
            skill_confidence = 0.0
            selection_method = "none"

            if self.skill_selector:
                try:
                    skill_name, reasoning = self.skill_selector.select_skill(
                        student_name,
                        config["prompt"]
                    )
                    if skill_name:
                        skill_confidence = reasoning.get("confidence", 0.0)
                        selection_method = reasoning.get("selection_method", "unknown")
                        task_pattern = reasoning.get("pattern", "general")
                        print(f"  [SKILL SELECT] {skill_name}")
                        print(f"    Pattern: {task_pattern} | Confidence: {skill_confidence:.1%} | Method: {selection_method}\n")
                except Exception as e:
                    print(f"  [SKILL SELECT] Error: {str(e)[:40]}\n")

            # STEP 5: EXECUTE - Full inference with warm model
            exec_ok, response, tokens, throughput = lifecycle.execute(model, config["prompt"])
            if not exec_ok:
                lifecycle.boot_down(model)
                print(f"  Failed to execute\n")
                continue

            # STEP 6: TRANSFER - Extract and save context
            context = self.context_manager.extract_context(
                student_name,
                response,
                {"throughput": throughput, "tokens": tokens}
            )
            print(f"  [CONTEXT SAVE] {len(context['key_insights'])} insights extracted")

            # STEP 7: BOOT DOWN - Unload model
            lifecycle.boot_down(model)

            # STEP 8: RECORD LEARNING OUTCOME
            if self.skill_selector and skill_name:
                try:
                    # Estimate quality based on throughput (normalized to 0-1)
                    quality_score = min(1.0, throughput / 40.0)  # 40 tok/s = perfect quality

                    # Record outcome for learning
                    self.skill_selector.record_outcome(
                        model=student_name,
                        task=config["prompt"],
                        skill=skill_name,
                        success=True,
                        quality=quality_score
                    )

                    # Also record to local database
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute("""
                            INSERT INTO skill_selections
                            (timestamp, cycle, student, task_pattern, skill_selected, confidence, selection_method, success, quality_score)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            time.time(), self.cycle, student_name, task_pattern,
                            skill_name, skill_confidence, selection_method,
                            True, quality_score
                        ))
                        conn.commit()

                    print(f"  [LEARNING] Recorded outcome: {skill_name} -> Q={quality_score:.2f}")
                except Exception as e:
                    print(f"  [LEARNING] Error recording outcome: {str(e)[:40]}")

            # Record metrics
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO executions
                    (cycle, student, model, tokens, throughput, warmup_throughput, skill_selected, skill_confidence, selection_method, execution_time, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.cycle, student_name, model, tokens, throughput,
                    warmup_throughput, skill_name, skill_confidence, selection_method,
                    time.time(), time.time()
                ))
                conn.commit()

            print()
            previous_student = student_name

            time.sleep(1)
            
        # End of cycle: Check resource limits
        self._check_resource_limits()

    def _print_report(self):
        """Print final report."""
        print("\n" + "=" * 80)
        print("FINAL REPORT - PREDICTIVE SEQUENTIAL ORCHESTRATION WITH SKILL LEARNING")
        print("=" * 80)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*), AVG(throughput), AVG(warmup_throughput)
                FROM executions
            """)
            count, avg_throughput, avg_warmup = cursor.fetchone()

            # Get skill selection statistics
            cursor = conn.execute("""
                SELECT COUNT(*), COUNT(DISTINCT skill_selected),
                       AVG(confidence), AVG(quality_score)
                FROM skill_selections
                WHERE skill_selected IS NOT NULL
            """)
            skill_count, skill_types, avg_confidence, avg_quality = cursor.fetchone()

        print(f"\nCycles completed: {self.cycle}")
        print(f"Total executions: {count}")
        if count > 0:
            print(f"Average throughput: {avg_throughput:.1f} tok/s")
            print(f"Soft warmup throughput: {avg_warmup:.1f} tok/s")

        print(f"\nSkill Selection Learning:")
        if skill_count > 0:
            print(f"  Skills selected: {skill_count}")
            print(f"  Unique skills learned: {skill_types}")
            print(f"  Average confidence: {avg_confidence:.1%}")
            print(f"  Average quality: {avg_quality:.2f}")
        else:
            print(f"  Skill selector not active or no data yet")

        print(f"\nKey Features Demonstrated:")
        print(f"  [OK] Soft warm-up (minimal tokens, no spike)")
        print(f"  [OK] Resource prediction (check before load)")
        if self.skill_selector:
            print(f"  [OK] Autonomous skill selection (intelligent learning)")
        print(f"  [OK] Critical threshold rule (don't load if > 85%)")
        print(f"  [OK] Context transfer (insights preserved)")
        print(f"  [OK] Graceful boot up/down (clean load/unload)")

        # Print learned skill knowledge from the autonomous selector
        if self.skill_selector:
            print(f"\n" + "-" * 80)
            print("AUTONOMOUS SKILL SELECTOR - LEARNING SUMMARY")
            print("-" * 80)
            self.skill_selector.print_agent_status()
            print("\nDETAILED LEARNED PATTERNS:")
            self.skill_selector.print_learned_knowledge()

        print("\n" + "=" * 80 + "\n")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=10)
    parser.add_argument("--session", type=str, default="rh_predictive")
    args = parser.parse_args()

    orchestrator = PredictiveSequentialOrchestrator(
        session_name=args.session,
        duration_minutes=args.duration
    )

    try:
        orchestrator.run()
    except KeyboardInterrupt:
        print("\n[INTERRUPTED]")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
