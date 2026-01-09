#!/usr/bin/env python3
"""
GPIA Artificial Super Intelligent Agent - Comprehensive Benchmark Suite
========================================================================

Tests all AGI capabilities:
1. Model Routing (5 LLM Partners)
2. S² Multi-Scale Execution
3. Memory/MSHR Performance
4. Skill Discovery & Loading
5. AST Safety Verification
6. Conscience Layer Operations
7. End-to-End GPIA Task Execution

Run: python gpia_benchmark_suite.py
"""

import sys
import os
import time
import json
import asyncio
import argparse
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set
import statistics

# Ensure proper encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Project imports
sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class BenchmarkResult:
    """Result of a single benchmark test."""
    name: str
    category: str
    success: bool
    duration_ms: float
    throughput: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class BenchmarkSuite:
    """Collection of benchmark results."""
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    results: List[BenchmarkResult] = field(default_factory=list)
    system_info: Dict[str, Any] = field(default_factory=dict)

    def add(self, result: BenchmarkResult):
        self.results.append(result)

    def summary(self) -> Dict[str, Any]:
        categories = {}
        for r in self.results:
            if r.category not in categories:
                categories[r.category] = {"total": 0, "passed": 0, "failed": 0, "times": []}
            categories[r.category]["total"] += 1
            if r.success:
                categories[r.category]["passed"] += 1
            else:
                categories[r.category]["failed"] += 1
            categories[r.category]["times"].append(r.duration_ms)

        return {
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r.success),
            "failed": sum(1 for r in self.results if not r.success),
            "categories": {
                k: {
                    "total": v["total"],
                    "passed": v["passed"],
                    "failed": v["failed"],
                    "avg_time_ms": statistics.mean(v["times"]) if v["times"] else 0,
                }
                for k, v in categories.items()
            },
        }


def print_header(title: str):
    """Print a section header."""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(result: BenchmarkResult):
    """Print a single benchmark result."""
    status = "[PASS]" if result.success else "[FAIL]"
    print(f"  {status} {result.name}: {result.duration_ms:.1f}ms", end="")
    if result.throughput:
        print(f" ({result.throughput:.1f}/s)", end="")
    if result.error:
        print(f" - {result.error}", end="")
    print()


class GPIABenchmark:
    """Comprehensive GPIA Benchmark Suite."""

    def __init__(self, memory_mode: str = "full", guardrails: bool = True):
        self.suite = BenchmarkSuite()
        self.ollama_url = "http://localhost:11434"
        self.memory_mode = memory_mode
        self.guardrails_enabled = guardrails
        self.guardrail_snapshot: Optional[Dict[str, Any]] = None
        self._sections = {
            "model": self.benchmark_model_routing,
            "s2": self.benchmark_s2_architecture,
            "memory": self.benchmark_memory_system,
            "skill": self.benchmark_skill_system,
            "safety": self.benchmark_safety_system,
            "conscience": self.benchmark_conscience_layer,
            "e2e": self.benchmark_gpia_e2e,
        }

    def _time_it(self, func, *args, **kwargs) -> tuple:
        """Time a function execution."""
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)[:100]
        duration = (time.perf_counter() - start) * 1000
        return result, success, duration, error

    def _run_ps(self, command: str, timeout: int = 5) -> Optional[str]:
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = (result.stdout or "") + (result.stderr or "")
            return output.strip() if result.returncode == 0 else None
        except Exception:
            return None

    def _get_memory_stats_mb(self) -> Dict[str, Optional[int]]:
        output = self._run_ps(
            "Get-CimInstance Win32_OperatingSystem | "
            "Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json"
        )
        if not output:
            return {"total_mb": None, "free_mb": None}
        try:
            data = json.loads(output)
            total_kb = int(data.get("TotalVisibleMemorySize", 0))
            free_kb = int(data.get("FreePhysicalMemory", 0))
            return {"total_mb": total_kb // 1024, "free_mb": free_kb // 1024}
        except Exception:
            return {"total_mb": None, "free_mb": None}

    def _get_vram_stats_mb(self) -> Dict[str, Optional[int]]:
        try:
            result = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.total,memory.used",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return {"total_mb": None, "free_mb": None}
            line = (result.stdout or "").strip().splitlines()[0]
            total_mb, used_mb = [int(x.strip()) for x in line.split(",")[:2]]
            return {"total_mb": total_mb, "free_mb": max(total_mb - used_mb, 0)}
        except Exception:
            return {"total_mb": None, "free_mb": None}

    def _get_disk_free_mb(self) -> Optional[int]:
        try:
            usage = shutil.disk_usage(Path.cwd())
            return int(usage.free / (1024 * 1024))
        except Exception:
            return None

    def _get_disk_write_bps(self) -> Optional[int]:
        output = self._run_ps(
            "$val = (Get-CimInstance Win32_PerfFormattedData_PerfDisk_PhysicalDisk | "
            "Where-Object { $_.Name -eq '_Total' } | "
            "Select-Object -ExpandProperty DiskWriteBytesPerSec); "
            "if (-not $val) { "
            "$val = (Get-CimInstance Win32_PerfFormattedData_PerfDisk_PhysicalDisk | "
            "Select-Object -First 1 -ExpandProperty DiskWriteBytesPerSec) }; "
            "$val"
        )
        if not output:
            return None
        try:
            line = output.strip().splitlines()[-1].strip()
            return int(float(line))
        except Exception:
            return None

    def _get_cpu_util_pct(self) -> Optional[float]:
        output = self._run_ps(
            "$val = (Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor | "
            "Where-Object { $_.Name -eq '_Total' } | "
            "Select-Object -ExpandProperty PercentProcessorTime); "
            "$val"
        )
        if not output:
            return None
        try:
            line = output.strip().splitlines()[-1].strip()
            return float(line)
        except Exception:
            return None

    def _get_npu_util_pct(self) -> Optional[float]:
        try:
            from core.npu_utils import get_openvino_core, has_npu

            core = get_openvino_core()
            if core is None or not has_npu():
                return None
            supported = core.get_property("NPU", "SUPPORTED_PROPERTIES")
            util_keys = [k for k in supported if "UTILIZATION" in str(k).upper()]
            for key in util_keys:
                try:
                    value = core.get_property("NPU", key)
                except Exception:
                    continue
                if isinstance(value, (int, float)):
                    return float(value)
                if isinstance(value, dict):
                    for sub_key, sub_val in value.items():
                        if "util" in str(sub_key).lower() and isinstance(sub_val, (int, float)):
                            return float(sub_val)
            return None
        except Exception:
            return None

    def _sample_cpu_util_pct(self, samples: int = 3, interval_sec: float = 0.4) -> Optional[float]:
        readings: List[float] = []
        for _ in range(samples):
            value = self._get_cpu_util_pct()
            if value is not None:
                readings.append(value)
            time.sleep(interval_sec)
        if not readings:
            return None
        return sum(readings) / len(readings)

    def _sample_npu_util_pct(self, samples: int = 3, interval_sec: float = 0.4) -> Optional[float]:
        readings: List[float] = []
        for _ in range(samples):
            value = self._get_npu_util_pct()
            if value is not None:
                readings.append(value)
            time.sleep(interval_sec)
        if not readings:
            return None
        return sum(readings) / len(readings)

    def _write_guardrail_snapshot(self, snapshot: Dict[str, Any]) -> None:
        try:
            output_file = Path("runs/guardrails_snapshot.json")
            output_file.parent.mkdir(exist_ok=True)
            output_file.write_text(json.dumps(snapshot, indent=2, default=str))
        except Exception:
            return

    def _get_db_size_mb(self, path: Optional[str]) -> Optional[float]:
        if not path or path == ":memory:":
            return None
        try:
            db_path = Path(path)
            if not db_path.is_absolute():
                db_path = Path.cwd() / db_path
            if not db_path.exists():
                return 0.0
            return db_path.stat().st_size / (1024 * 1024)
        except Exception:
            return None

    def _evaluate_guardrails(self) -> Dict[str, Any]:
        memory = self._get_memory_stats_mb()
        vram = self._get_vram_stats_mb()
        disk_free_mb = self._get_disk_free_mb()
        disk_write_bps = self._get_disk_write_bps()
        cpu_util_pct = self._get_cpu_util_pct()
        npu_util_pct = self._get_npu_util_pct()

        total_ram_mb = memory.get("total_mb")
        total_vram_mb = vram.get("total_mb")
        total_disk_mb = None
        try:
            total_disk_mb = int(shutil.disk_usage(Path.cwd()).total / (1024 * 1024))
        except Exception:
            total_disk_mb = None

        min_free_ram_mb = int(
            os.getenv(
                "GPIA_MIN_FREE_RAM_MB",
                max(4096, int(total_ram_mb * 0.25)) if total_ram_mb else 4096,
            )
        )
        min_free_vram_mb = int(
            os.getenv(
                "GPIA_MIN_FREE_VRAM_MB",
                max(2048, int(total_vram_mb * 0.2)) if total_vram_mb else 2048,
            )
        )
        min_free_disk_mb = int(
            os.getenv(
                "GPIA_MIN_FREE_DISK_MB",
                max(102400, int(total_disk_mb * 0.05)) if total_disk_mb else 102400,
            )
        )
        min_cpu_util_pct = float(os.getenv("GPIA_MIN_CPU_UTIL_PCT", "5"))
        min_npu_util_pct = float(os.getenv("GPIA_MIN_NPU_UTIL_PCT", "5"))
        enforce_util_floors = os.getenv("GPIA_ENFORCE_UTIL_FLOORS", "1").lower() in {
            "1",
            "true",
            "yes",
        }
        expect_npu = os.getenv("GPIA_EXPECT_NPU", "0").lower() in {"1", "true", "yes"}
        max_disk_write_bps = os.getenv("GPIA_MAX_DISK_WRITE_BPS")
        if max_disk_write_bps:
            max_disk_write_bps = int(max_disk_write_bps)
        else:
            max_disk_write_mbps = float(os.getenv("GPIA_MAX_DISK_WRITE_MBPS", "50"))
            max_disk_write_bps = int(max_disk_write_mbps * 1024 * 1024)

        snapshot = {
            "memory": memory,
            "vram": vram,
            "disk_free_mb": disk_free_mb,
            "disk_write_bps": disk_write_bps,
            "cpu_util_pct": cpu_util_pct,
            "npu_util_pct": npu_util_pct,
            "thresholds": {
                "min_free_ram_mb": min_free_ram_mb,
                "min_free_vram_mb": min_free_vram_mb,
                "min_free_disk_mb": min_free_disk_mb,
                "min_cpu_util_pct": min_cpu_util_pct,
                "min_npu_util_pct": min_npu_util_pct,
                "enforce_util_floors": enforce_util_floors,
                "expect_npu": expect_npu,
                "max_disk_write_bps": max_disk_write_bps,
            },
            "recommended_memory_mode": "full",
            "reasons": [],
        }

        if memory.get("free_mb") is not None and memory["free_mb"] < min_free_ram_mb:
            snapshot["recommended_memory_mode"] = "off"
            snapshot["reasons"].append("free RAM below floor")
        elif vram.get("free_mb") is not None and vram["free_mb"] < min_free_vram_mb:
            snapshot["recommended_memory_mode"] = "safe"
            snapshot["reasons"].append("free VRAM below floor")
        elif disk_free_mb is not None and disk_free_mb < min_free_disk_mb:
            snapshot["recommended_memory_mode"] = "safe"
            snapshot["reasons"].append("free disk below floor")
        elif disk_write_bps is not None and disk_write_bps > max_disk_write_bps:
            snapshot["recommended_memory_mode"] = "safe"
            snapshot["reasons"].append("disk write rate above cap")

        return snapshot

    # =========================================================================
    # 1. MODEL ROUTING BENCHMARKS
    # =========================================================================

    def benchmark_model_routing(self):
        """Benchmark all 5 LLM partners."""
        print_header("1. MODEL ROUTING BENCHMARKS (5 LLM Partners)")

        import requests

        models = [
            ("codegemma:latest", "L0 Fast - Intent parsing"),
            ("qwen3:latest", "L1-L2 Creative - Code generation"),
            ("deepseek-r1:latest", "L2-L3 Reasoning - Analysis"),
            ("llava:latest", "Visual - Image analysis"),
        ]

        test_prompt = "What is 2+2? Answer with just the number."

        for model, description in models:
            def test_model():
                resp = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json={"model": model, "prompt": test_prompt, "stream": False},
                    timeout=60
                )
                return resp.json()

            result, success, duration, error = self._time_it(test_model)

            # Calculate tokens/sec if successful
            throughput = None
            if success and result:
                eval_count = result.get("eval_count", 0)
                eval_duration = result.get("eval_duration", 1) / 1e9  # ns to s
                if eval_duration > 0:
                    throughput = eval_count / eval_duration

            bench_result = BenchmarkResult(
                name=f"{model} ({description})",
                category="Model Routing",
                success=success,
                duration_ms=duration,
                throughput=throughput,
                details={"model": model, "response": result.get("response", "")[:50] if result else None},
                error=error
            )
            self.suite.add(bench_result)
            print_result(bench_result)

    # =========================================================================
    # 2. S² MULTI-SCALE EXECUTION
    # =========================================================================

    def benchmark_s2_architecture(self):
        """Benchmark S² multi-scale skill decomposition."""
        print_header("2. S² MULTI-SCALE ARCHITECTURE")

        from pathlib import Path
        import re

        decomposed_dir = Path("skills/s2/decomposed")

        # Test 1: Count decomposed skills
        def count_decomposed():
            files = list(decomposed_dir.glob("*_s2.py"))
            return len(files)

        result, success, duration, error = self._time_it(count_decomposed)
        bench_result = BenchmarkResult(
            name=f"S2 Decomposed Skills Count",
            category="S2 Architecture",
            success=success and result == 40,
            duration_ms=duration,
            details={"count": result, "expected": 40},
            error=error if error else (f"Expected 40, got {result}" if result != 40 else None)
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 2: Load and parse decomposition metadata
        def load_decompositions():
            decompositions = []
            for f in decomposed_dir.glob("*_s2.py"):
                content = f.read_text(encoding='utf-8')
                match = re.search(r'SKILL_METADATA = ({.*?})\s*$', content, re.DOTALL)
                if match:
                    # Just verify structure exists
                    decompositions.append(f.stem)
            return decompositions

        result, success, duration, error = self._time_it(load_decompositions)
        bench_result = BenchmarkResult(
            name="S2 Metadata Loading",
            category="S2 Architecture",
            success=success and len(result) > 30,
            duration_ms=duration,
            throughput=len(result) / (duration / 1000) if duration > 0 else 0,
            details={"loaded": len(result) if result else 0},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 3: S2 Composer initialization
        def init_composer():
            from skills.s2.composer import S2MultiModalComposer
            composer = S2MultiModalComposer()
            return composer.SCALE_MODELS

        result, success, duration, error = self._time_it(init_composer)
        bench_result = BenchmarkResult(
            name="S2 MultiModal Composer Init",
            category="S2 Architecture",
            success=success and result is not None,
            duration_ms=duration,
            details={"scales": list(result.keys()) if result else None},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 4: Verify 5-LLM routing in S2
        def verify_routing():
            from skills.s2.visual import S2MultiModalRouter
            from skills.s2.context_stack import ScaleLevel
            router = S2MultiModalRouter()
            results = {}
            for scale in [ScaleLevel.L0, ScaleLevel.L1, ScaleLevel.L2, ScaleLevel.L3]:
                results[scale.value] = {
                    "text": router.get_model_for_scale(scale, task_type="text"),
                    "reasoning": router.get_model_for_scale(scale, task_type="reasoning"),
                    "synthesis": router.get_model_for_scale(scale, task_type="synthesis"),
                }
            return results

        result, success, duration, error = self._time_it(verify_routing)
        bench_result = BenchmarkResult(
            name="S2 5-LLM Partner Routing",
            category="S2 Architecture",
            success=success and result is not None,
            duration_ms=duration,
            details={"routing": result},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

    # =========================================================================
    # 3. MEMORY/MSHR PERFORMANCE
    # =========================================================================

    def benchmark_memory_system(self):
        """Benchmark Memory skill with MSHR."""
        title = "3. MEMORY/MSHR PERFORMANCE"
        if self.memory_mode == "off":
            print_header(f"{title} (SKIPPED)")
            print("  Skipped (memory_mode=off)")
            return

        print_header(title)

        effective_memory_mode = self.memory_mode
        guardrails = None
        guardrail_util = {
            "enforce": False,
            "min_cpu_util_pct": None,
            "min_npu_util_pct": None,
            "expect_npu": False,
        }
        if self.guardrails_enabled:
            guardrails = self._evaluate_guardrails()
            self.guardrail_snapshot = guardrails
            self.suite.system_info["guardrails"] = guardrails
            guardrails["phase"] = "preflight"
            self._write_guardrail_snapshot(guardrails)
            recommended = guardrails.get("recommended_memory_mode")
            reasons = guardrails.get("reasons", [])
            thresholds = guardrails.get("thresholds", {})
            guardrail_util = {
                "enforce": bool(thresholds.get("enforce_util_floors")),
                "min_cpu_util_pct": thresholds.get("min_cpu_util_pct"),
                "min_npu_util_pct": thresholds.get("min_npu_util_pct"),
                "expect_npu": bool(thresholds.get("expect_npu")),
            }
            if recommended == "off":
                print("  Guardrails: memory benchmark skipped (" + ", ".join(reasons) + ")")
                return
            if recommended == "safe" and self.memory_mode == "full":
                effective_memory_mode = "safe"
                print("  Guardrails: forcing safe memory mode (" + ", ".join(reasons) + ")")

        env_overrides = {}
        use_mshr = True
        bulk_count = 10

        if effective_memory_mode == "safe":
            env_overrides = {
                "MEMORY_EMBEDDINGS": "off",
                "MEMORY_DB_PATH": ":memory:",
            }
            use_mshr = False
            bulk_count = 3
            print("  Safe mode: embeddings disabled, in-memory DB, MSHR off")
            guardrail_util["expect_npu"] = False

        previous_env = {}
        for key, value in env_overrides.items():
            previous_env[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            from skills.conscience.memory.skill import MemorySkill
            from skills.base import SkillContext

            # Test 1: Initialize Memory with MSHR
            def init_memory():
                mem = MemorySkill(use_mshr=use_mshr)
                return mem

            mem, success, duration, error = self._time_it(init_memory)
            bench_result = BenchmarkResult(
                name="Memory + MSHR Initialization",
                category="Memory System",
                success=success,
                duration_ms=duration,
                error=error
            )
            self.suite.add(bench_result)
            print_result(bench_result)

            if not mem:
                return

            ctx = SkillContext()
            db_path = env_overrides.get("MEMORY_DB_PATH") or os.environ.get("MEMORY_DB_PATH")
            if not db_path:
                db_path = "skills/conscience/memory/store/memories.db"
            db_start_mb = self._get_db_size_mb(db_path)
            max_db_growth_mb = None
            if db_start_mb is not None and effective_memory_mode == "full":
                max_db_growth_mb = int(os.getenv("GPIA_MAX_MEM_DB_GROWTH_MB", "512"))

            # Test 2: Store memory
            def store_memory():
                return mem.execute({
                    "capability": "experience",
                    "content": f"Benchmark test memory at {datetime.now().isoformat()}",
                    "memory_type": "episodic",
                    "importance": 0.5
                }, ctx)

            result, success, duration, error = self._time_it(store_memory)
            bench_result = BenchmarkResult(
                name="Memory Store (Single)",
                category="Memory System",
                success=success and result.success if result else False,
                duration_ms=duration,
                details={"memory_id": result.output.get("memory_id") if result else None},
                error=error
            )
            self.suite.add(bench_result)
            print_result(bench_result)

            # Test 3: Bulk store
            def bulk_store():
                results = []
                guardrail_stop = False
                util_checked = False
                util_samples: Dict[str, Any] = {}
                util_reasons: List[str] = []
                for i in range(bulk_count):
                    r = mem.execute({
                        "capability": "experience",
                        "content": f"Bulk benchmark memory {i}",
                        "memory_type": "semantic",
                        "importance": 0.3
                    }, ctx)
                    results.append(r.success)
                    if guardrail_util["enforce"] and not util_checked:
                        cpu_sample = self._sample_cpu_util_pct()
                        if cpu_sample is not None:
                            util_samples["cpu_util_pct"] = cpu_sample
                            if (
                                guardrail_util["min_cpu_util_pct"] is not None
                                and cpu_sample < float(guardrail_util["min_cpu_util_pct"])
                            ):
                                util_reasons.append("cpu utilization below floor")
                        if guardrail_util["expect_npu"]:
                            npu_sample = self._sample_npu_util_pct()
                            if npu_sample is not None:
                                util_samples["npu_util_pct"] = npu_sample
                                if (
                                    guardrail_util["min_npu_util_pct"] is not None
                                    and npu_sample < float(guardrail_util["min_npu_util_pct"])
                                ):
                                    util_reasons.append("npu utilization below floor")
                        util_checked = True
                        if util_reasons:
                            guardrail_stop = True
                            break
                    if max_db_growth_mb is not None and db_start_mb is not None:
                        current_mb = self._get_db_size_mb(db_path)
                        if current_mb is not None and (current_mb - db_start_mb) > max_db_growth_mb:
                            guardrail_stop = True
                            break
                return sum(results), guardrail_stop, util_samples, util_reasons

            result, success, duration, error = self._time_it(bulk_store)
            stored_count = result[0] if success and result else 0
            guardrail_stop = result[1] if success and result else False
            util_samples = result[2] if success and result else {}
            util_reasons = result[3] if success and result else []
            db_end_mb = self._get_db_size_mb(db_path) if db_start_mb is not None else None
            if guardrails is not None:
                guardrails["phase"] = "memory"
                guardrails["util_samples"] = util_samples
                guardrails["util_reasons"] = util_reasons
                self.suite.system_info["guardrails"] = guardrails
                self._write_guardrail_snapshot(guardrails)
            bench_result = BenchmarkResult(
                name=f"Memory Bulk Store ({bulk_count}x)",
                category="Memory System",
                success=success and (stored_count == bulk_count or guardrail_stop),
                duration_ms=duration,
                throughput=stored_count / (duration / 1000) if duration > 0 else 0,
                details={
                    "stored": stored_count,
                    "expected": bulk_count,
                    "guardrail_stop": guardrail_stop,
                    "util_samples": util_samples,
                    "util_reasons": util_reasons,
                    "db_growth_mb": (db_end_mb - db_start_mb) if db_end_mb is not None and db_start_mb is not None else None,
                    "db_path": db_path,
                    "max_db_growth_mb": max_db_growth_mb,
                },
                error=error
            )
            self.suite.add(bench_result)
            print_result(bench_result)

            # Test 4: Recall with MSHR
            def recall_memory():
                return mem.execute({
                    "capability": "recall",
                    "content": "benchmark test memory",
                    "limit": 10
                }, ctx)

            result, success, duration, error = self._time_it(recall_memory)
            bench_result = BenchmarkResult(
                name="Memory Recall (MSHR)",
                category="Memory System",
                success=success and result.success if result else False,
                duration_ms=duration,
                details={"found": len(result.output.get("memories", [])) if result else 0},
                error=error
            )
            self.suite.add(bench_result)
            print_result(bench_result)

            # Test 5: Memory stats
            def memory_stats():
                return mem.execute({"capability": "stats"}, ctx)

            result, success, duration, error = self._time_it(memory_stats)
            bench_result = BenchmarkResult(
                name="Memory Stats Query",
                category="Memory System",
                success=success,
                duration_ms=duration,
                details=result.output if result else None,
                error=error
            )
            self.suite.add(bench_result)
            print_result(bench_result)
        finally:
            for key, prev in previous_env.items():
                if prev is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = prev

    # =========================================================================
    # 4. SKILL DISCOVERY & LOADING
    # =========================================================================

    def benchmark_skill_system(self):
        """Benchmark skill loading and discovery."""
        print_header("4. SKILL DISCOVERY & LOADING")

        # Test 1: Load skill index
        def load_index():
            with open("skills/INDEX.json", "r") as f:
                return json.load(f)

        result, success, duration, error = self._time_it(load_index)
        skill_count = len(result.get("skills", [])) if result else 0
        bench_result = BenchmarkResult(
            name="Skill Index Load",
            category="Skill System",
            success=success and skill_count > 70,
            duration_ms=duration,
            details={"skill_count": skill_count},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 2: Skill loader initialization
        def init_loader():
            from skills.loader import SkillLoader
            loader = SkillLoader()
            return loader

        result, success, duration, error = self._time_it(init_loader)
        bench_result = BenchmarkResult(
            name="SkillLoader Initialization",
            category="Skill System",
            success=success,
            duration_ms=duration,
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 3: Scan all skills
        def scan_skills():
            from skills.loader import SkillLoader
            loader = SkillLoader()
            return loader.scan_all(lazy=True)

        result, success, duration, error = self._time_it(scan_skills)
        bench_result = BenchmarkResult(
            name="Skill Scan (Lazy Load)",
            category="Skill System",
            success=success,
            duration_ms=duration,
            throughput=result / (duration / 1000) if duration > 0 and result else 0,
            details={"loaded": result},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 4: Execute a skill
        def execute_skill():
            from skills.conscience.memory.skill import MemorySkill
            from skills.base import SkillContext
            mem = MemorySkill(use_mshr=False)  # Fast init
            return mem.execute(
                {"capability": "recall", "content": "benchmark memory", "limit": 1},
                SkillContext(),
            )

        result, success, duration, error = self._time_it(execute_skill)
        bench_result = BenchmarkResult(
            name="Skill Execution (Memory Stats)",
            category="Skill System",
            success=success and result.success if result else False,
            duration_ms=duration,
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

    # =========================================================================
    # 5. AST SAFETY VERIFICATION
    # =========================================================================

    def benchmark_safety_system(self):
        """Benchmark AST-based safety verification."""
        print_header("5. AST SAFETY VERIFICATION")

        sys.path.insert(0, 'skills/safety/ast-safety')

        # Test 1: Fingerprint safe code
        def fingerprint_safe():
            from skill import fingerprint_code
            return fingerprint_code('''
def greet(name):
    return f"Hello, {name}!"
''')

        result, success, duration, error = self._time_it(fingerprint_safe)
        bench_result = BenchmarkResult(
            name="AST Fingerprint (Safe Code)",
            category="Safety System",
            success=success and result.get("fingerprint") is not None,
            duration_ms=duration,
            details={"fingerprint": result.get("fingerprint") if result else None},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 2: Detect SQL injection
        def detect_sqli():
            from skill import analyze_vulnerabilities
            return analyze_vulnerabilities('''
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = %s" % user_id
    cursor.execute(query)
''')

        result, success, duration, error = self._time_it(detect_sqli)
        has_vuln = result.get("vulnerability_count", 0) > 0 if result else False
        bench_result = BenchmarkResult(
            name="AST Vulnerability Detection (SQLi)",
            category="Safety System",
            success=success and has_vuln,
            duration_ms=duration,
            details={"vulnerabilities": result.get("vulnerabilities") if result else None},
            error=error if not has_vuln and not error else error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 3: Detect eval() usage
        def detect_eval():
            from skill import analyze_vulnerabilities
            return analyze_vulnerabilities('''
def process(data):
    result = eval(data)
    return result
''')

        result, success, duration, error = self._time_it(detect_eval)
        has_vuln = result.get("vulnerability_count", 0) > 0 if result else False
        bench_result = BenchmarkResult(
            name="AST Vulnerability Detection (eval)",
            category="Safety System",
            success=success and has_vuln,
            duration_ms=duration,
            details={"vulnerabilities": result.get("vulnerabilities") if result else None},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 4: Pre-generation filter
        def test_filter():
            from skill import filter_code
            return filter_code('print("Hello World")')

        result, success, duration, error = self._time_it(test_filter)
        bench_result = BenchmarkResult(
            name="AST Pre-Generation Filter",
            category="Safety System",
            success=success and result.get("allowed") is not None,
            duration_ms=duration,
            details={"allowed": result.get("allowed") if result else None},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

    # =========================================================================
    # 6. CONSCIENCE LAYER OPERATIONS
    # =========================================================================

    def benchmark_conscience_layer(self):
        """Benchmark Conscience Layer skills."""
        print_header("6. CONSCIENCE LAYER OPERATIONS")

        from skills.base import SkillContext
        ctx = SkillContext()

        # Test 1: Mindset Skill
        def test_mindset():
            from skills.conscience.mindset.skill import MindsetSkill
            mindset = MindsetSkill()
            # Just test initialization, not full LLM call
            return mindset

        result, success, duration, error = self._time_it(test_mindset)
        bench_result = BenchmarkResult(
            name="Mindset Skill Init",
            category="Conscience Layer",
            success=success and result is not None,
            duration_ms=duration,
            details={"initialized": result is not None},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 2: Self Skill
        def test_self():
            from skills.conscience.self.skill import SelfSkill
            self_skill = SelfSkill()
            return self_skill

        result, success, duration, error = self._time_it(test_self)
        bench_result = BenchmarkResult(
            name="Self Skill Init",
            category="Conscience Layer",
            success=success and result is not None,
            duration_ms=duration,
            details={"initialized": result is not None},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 3: Safety Skill
        def test_safety():
            from skills.conscience.safety.skill import SafetySkill
            safety = SafetySkill()
            return safety

        result, success, duration, error = self._time_it(test_safety)
        bench_result = BenchmarkResult(
            name="Safety Skill Init",
            category="Conscience Layer",
            success=success and result is not None,
            duration_ms=duration,
            details={"initialized": result is not None},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 4: Safety validation
        def test_safety_validate():
            from skills.conscience.safety.skill import SafetySkill
            safety = SafetySkill()
            return safety.execute({
                "action_type": "read_file",
                "target_path": "/tmp/test.txt",
                "human_approval": False
            }, ctx)

        result, success, duration, error = self._time_it(test_safety_validate)
        allowed = None
        if result and hasattr(result, 'output') and result.output:
            allowed = result.output.get("allowed")
        bench_result = BenchmarkResult(
            name="Safety Action Validation",
            category="Conscience Layer",
            success=success,
            duration_ms=duration,
            details={"allowed": allowed},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

    # =========================================================================
    # 7. END-TO-END GPIA TESTS
    # =========================================================================

    def benchmark_gpia_e2e(self):
        """End-to-end GPIA agent tests."""
        print_header("7. END-TO-END GPIA TESTS")

        # Test 1: GPIA imports
        def test_gpia_imports():
            from skills.s2.composer import S2Composer, S2MultiModalComposer
            from skills.s2.context_stack import S2ContextStack, ScaleLevel
            from skills.s2.transforms import S2Projector
            return True

        result, success, duration, error = self._time_it(test_gpia_imports)
        bench_result = BenchmarkResult(
            name="GPIA Core Imports",
            category="GPIA E2E",
            success=success,
            duration_ms=duration,
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 2: Create S2 context
        def test_s2_context():
            from skills.s2.context_stack import create_s2_context, ScaleLevel
            ctx = create_s2_context("Benchmark test goal")
            ctx.push(ScaleLevel.L0)
            ctx.add_result({"test": "result"})
            ctx.pop()
            return ctx.get_execution_summary()

        result, success, duration, error = self._time_it(test_s2_context)
        bench_result = BenchmarkResult(
            name="S2 Context Stack Operations",
            category="GPIA E2E",
            success=success and result is not None,
            duration_ms=duration,
            details={"summary": result},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 3: S2 Projector
        def test_projector():
            from skills.s2.transforms import S2Projector
            from skills.s2.context_stack import ScaleLevel
            import numpy as np
            proj = S2Projector()

            # Test projection
            embedding = np.zeros(proj.dimension, dtype=np.float32)
            projected = proj.project(embedding, ScaleLevel.L0, ScaleLevel.L1)
            return projected

        result, success, duration, error = self._time_it(test_projector)
        bench_result = BenchmarkResult(
            name="S2 Scale Projection (L0->L1)",
            category="GPIA E2E",
            success=success,
            duration_ms=duration,
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 4: Complex decomposition strategy
        def test_complex_strategy():
            from skills.s2.complex_decomposition_strategy import (
                DECOMPOSITION_STRATEGIES,
                generate_s2_decomposition
            )
            # Test one strategy
            strategy = DECOMPOSITION_STRATEGIES.get("governance/guardrails-control")
            if strategy:
                return generate_s2_decomposition(strategy)
            return None

        result, success, duration, error = self._time_it(test_complex_strategy)
        bench_result = BenchmarkResult(
            name="Complex Decomposition Strategy",
            category="GPIA E2E",
            success=success and result is not None,
            duration_ms=duration,
            details={"skill_id": result.get("skill_id") if result else None},
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

        # Test 5: Full system integration check
        def test_integration():
            components = {
                "s2_decomposed": len(list(Path("skills/s2/decomposed").glob("*_s2.py"))),
                "skill_index": Path("skills/INDEX.json").exists(),
                "memory_db": Path("skills/conscience/memory/store/memories.db").exists(),
                "ast_safety": Path("skills/safety/ast-safety/skill.py").exists(),
            }
            return components

        result, success, duration, error = self._time_it(test_integration)
        all_present = all(v if isinstance(v, bool) else v > 0 for v in result.values()) if result else False
        bench_result = BenchmarkResult(
            name="System Integration Check",
            category="GPIA E2E",
            success=success and all_present,
            duration_ms=duration,
            details=result,
            error=error
        )
        self.suite.add(bench_result)
        print_result(bench_result)

    # =========================================================================
    # RUN ALL BENCHMARKS
    # =========================================================================

    def run_all(self):
        """Run the complete benchmark suite."""
        print()
        print("=" * 70)
        print("  GPIA ARTIFICIAL SUPER INTELLIGENT AGENT")
        print("  COMPREHENSIVE BENCHMARK SUITE")
        print("=" * 70)
        print(f"  Started: {self.suite.start_time}")
        print("=" * 70)

        # Collect system info
        self.suite.system_info = {
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "cwd": str(Path.cwd()),
        }

        # Run all benchmark categories
        for key, func in self._sections.items():
            func()

        # Print summary
        self.print_summary()

        # Save results
        self.save_results()

    def run_sections(self, sections: Optional[Set[str]] = None, skip: Optional[Set[str]] = None):
        """Run selected benchmark sections."""
        print()
        print("=" * 70)
        print("  GPIA ARTIFICIAL SUPER INTELLIGENT AGENT")
        print("  COMPREHENSIVE BENCHMARK SUITE (PARTIAL)")
        print("=" * 70)
        print(f"  Started: {self.suite.start_time}")
        print("=" * 70)

        # Collect system info
        self.suite.system_info = {
            "python_version": sys.version.split()[0],
            "platform": sys.platform,
            "cwd": str(Path.cwd()),
            "sections": sorted(list(sections)) if sections else "all",
            "skip": sorted(list(skip)) if skip else [],
        }

        for key, func in self._sections.items():
            if sections and key not in sections:
                continue
            if skip and key in skip:
                continue
            func()

        self.print_summary()
        self.save_results()

    def print_summary(self):
        """Print benchmark summary."""
        summary = self.suite.summary()

        print()
        print("=" * 70)
        print("  BENCHMARK SUMMARY")
        print("=" * 70)
        print()
        print(f"  Total Tests:  {summary['total_tests']}")
        print(f"  Passed:       {summary['passed']} ({100*summary['passed']/summary['total_tests']:.1f}%)")
        print(f"  Failed:       {summary['failed']} ({100*summary['failed']/summary['total_tests']:.1f}%)")
        print()
        print("  By Category:")
        print("  " + "-" * 66)

        for category, stats in summary["categories"].items():
            status = "PASS" if stats["failed"] == 0 else "PARTIAL" if stats["passed"] > 0 else "FAIL"
            print(f"  [{status:^7}] {category:30} {stats['passed']}/{stats['total']} ({stats['avg_time_ms']:.1f}ms avg)")

        print()
        print("=" * 70)

        # Overall verdict
        if summary["failed"] == 0:
            print("  VERDICT: ALL SYSTEMS OPERATIONAL")
        elif summary["passed"] / summary["total_tests"] > 0.8:
            print("  VERDICT: MOSTLY OPERATIONAL (some tests failed)")
        else:
            print("  VERDICT: NEEDS ATTENTION")

        print("=" * 70)

    def save_results(self):
        """Save benchmark results to file."""
        output_file = Path("runs/gpia_benchmark_results.json")
        output_file.parent.mkdir(exist_ok=True)

        results = {
            "suite": {
                "start_time": self.suite.start_time,
                "system_info": self.suite.system_info,
            },
            "summary": self.suite.summary(),
            "results": [
                {
                    "name": r.name,
                    "category": r.category,
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                    "throughput": r.throughput,
                    "details": r.details,
                    "error": r.error,
                }
                for r in self.suite.results
            ],
        }

        output_file.write_text(json.dumps(results, indent=2, default=str))
        print(f"\n  Results saved to: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GPIA benchmark suite")
    parser.add_argument(
        "--memory-mode",
        choices=["full", "safe", "off"],
        default="full",
        help="Control memory benchmark impact: full (default), safe (no embeddings), or off",
    )
    parser.add_argument(
        "--guardrails",
        choices=["on", "off"],
        default=os.getenv("GPIA_GUARDRAILS", "on"),
        help="Enable or disable guardrails (default: on)",
    )
    parser.add_argument(
        "--sections",
        default="",
        help="Comma-separated sections to run: model,s2,memory,skill,safety,conscience,e2e",
    )
    parser.add_argument(
        "--skip",
        default="",
        help="Comma-separated sections to skip: model,s2,memory,skill,safety,conscience,e2e",
    )
    args = parser.parse_args()

    benchmark = GPIABenchmark(
        memory_mode=args.memory_mode,
        guardrails=args.guardrails == "on",
    )

    def _parse_list(value: str) -> Set[str]:
        return {item.strip().lower() for item in value.split(",") if item.strip()}

    sections = _parse_list(args.sections)
    skip = _parse_list(args.skip)
    valid = set(benchmark._sections.keys())
    unknown = (sections | skip) - valid
    if unknown:
        print(f"Unknown sections: {', '.join(sorted(unknown))}")
        raise SystemExit(2)

    if sections or skip:
        benchmark.run_sections(sections=sections if sections else None, skip=skip if skip else None)
    else:
        benchmark.run_all()
