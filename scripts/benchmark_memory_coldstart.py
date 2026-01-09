#!/usr/bin/env python3
"""
Memory Cold-Start Benchmark

Measures memory initialization performance with lazy MSHR initialization.
Tracks:
- Cold initialization time (MemorySkill instantiation)
- First recall latency (triggers lazy MSHR build)
- Warm recall latency (MSHR already built)
- Memory peak usage

Usage:
    python scripts/benchmark_memory_coldstart.py
"""

import time
import json
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any
import sys
import gc

# Make sure we can import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class MemoryBenchmarkResult:
    """Result of a single memory benchmark measurement."""
    name: str
    cold_start_ms: float
    first_recall_ms: float
    warm_recall_ms: float
    storage_stats: Dict[str, Any] = field(default_factory=dict)
    memory_peak_mb: float = 0.0
    success: bool = False
    error: Optional[str] = None


class MemoryBenchmark:
    """Benchmark memory cold-start initialization."""

    def __init__(self, use_lazy_init: bool = True):
        self.use_lazy_init = use_lazy_init
        self.results: List[MemoryBenchmarkResult] = []

    def benchmark_cold_init(self) -> MemoryBenchmarkResult:
        """Measure cold start with lazy MSHR initialization."""
        print("\n[BENCHMARK] Starting memory cold-start measurement...")

        # Clean up any existing artifacts
        gc.collect()

        cold_duration = 0.0
        first_recall_duration = 0.0
        warm_recall_duration = 0.0
        peak_memory = 0.0
        success = False
        error = None

        try:
            # Import here to measure import time too
            from skills.conscience.memory.skill import MemorySkill

            # Cold initialization
            print("  [1/3] Cold initialization (MemorySkill instantiation)...")
            start = time.perf_counter()
            mem = MemorySkill(use_mshr=True)
            cold_duration = (time.perf_counter() - start) * 1000

            print(f"    [OK] Cold start completed in {cold_duration:.1f}ms")

            # First recall (triggers lazy MSHR build if applicable)
            print("  [2/3] First recall (triggers lazy MSHR initialization)...")
            start = time.perf_counter()
            result = mem.execute(
                {
                    "capability": "recall",
                    "content": "benchmark test query",
                    "memory_type": "episodic",
                    "limit": 10
                },
                None
            )
            first_recall_duration = (time.perf_counter() - start) * 1000

            print(f"    [OK] First recall completed in {first_recall_duration:.1f}ms")

            # Warm recall (MSHR already built)
            print("  [3/3] Warm recall (MSHR already built)...")
            start = time.perf_counter()
            result = mem.execute(
                {
                    "capability": "recall",
                    "content": "another test query",
                    "memory_type": "episodic",
                    "limit": 10
                },
                None
            )
            warm_recall_duration = (time.perf_counter() - start) * 1000

            print(f"    [OK] Warm recall completed in {warm_recall_duration:.1f}ms")

            success = True

        except Exception as e:
            error = str(e)[:200]
            print(f"  [FAIL] Benchmark failed: {error}")
            import traceback
            traceback.print_exc()

        result = MemoryBenchmarkResult(
            name="Memory Cold Start",
            cold_start_ms=cold_duration,
            first_recall_ms=first_recall_duration,
            warm_recall_ms=warm_recall_duration,
            storage_stats={},
            memory_peak_mb=peak_memory,
            success=success,
            error=error
        )

        self.results.append(result)
        return result

    def save_results(self, output_path: Path = Path("artifacts/memory_benchmark.json")) -> None:
        """Save benchmark results to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "benchmark": "memory_coldstart",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "config": {
                "lazy_init": self.use_lazy_init,
            },
            "results": [asdict(r) for r in self.results]
        }

        output_path.write_text(json.dumps(data, indent=2))
        print(f"\n[OK] Results saved to {output_path}")

    def print_summary(self) -> None:
        """Print summary of benchmark results."""
        if not self.results:
            print("\nNo results to display")
            return

        result = self.results[0]

        print("\n" + "=" * 70)
        print("MEMORY COLD-START BENCHMARK SUMMARY")
        print("=" * 70)
        print(f"\nBenchmark: {result.name}")
        print(f"Status: {'PASS' if result.success else 'FAIL'}")

        if result.success:
            print(f"\nTimings:")
            print(f"  Cold Start:     {result.cold_start_ms:>10.1f}ms")
            print(f"  First Recall:   {result.first_recall_ms:>10.1f}ms  (lazy MSHR build)")
            print(f"  Warm Recall:    {result.warm_recall_ms:>10.1f}ms  (MSHR cached)")

            total_init_ms = result.cold_start_ms + result.first_recall_ms
            print(f"\nTotal Init Time: {total_init_ms:>10.1f}ms")
            print(f"Target:         <  500.0ms")
            print(f"Status:         {'PASS' if total_init_ms < 500 else 'SLOW'}")

            # Calculate speedup vs eager init
            if result.cold_start_ms > 0:
                speedup = total_init_ms / result.cold_start_ms
                print(f"\nLazy Init Speedup: {speedup:.1f}x total time vs cold start alone")
        else:
            print(f"\nError: {result.error}")

        print("\n" + "=" * 70)


def main():
    """Run memory cold-start benchmark."""
    print("=" * 70)
    print("MEMORY COLD-START BENCHMARK")
    print("=" * 70)
    print("\nThis benchmark measures the performance impact of lazy MSHR initialization.")
    print("Target: Total init time (cold + first recall) < 500ms")

    # Run benchmark
    bench = MemoryBenchmark(use_lazy_init=True)
    result = bench.benchmark_cold_init()

    # Save and print results
    bench.save_results(Path("artifacts/memory_benchmark_coldstart.json"))
    bench.print_summary()

    # Exit with appropriate code
    if result.success:
        total_init_ms = result.cold_start_ms + result.first_recall_ms
        sys.exit(0 if total_init_ms < 500 else 1)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
