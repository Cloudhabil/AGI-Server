"""
Metabolic Optimizer: Finding the ASI-Father's Optimal Learning Cycle.
Tests different cycle architectures to maximize Information Gain per beat.
Moves the system from human-defined timing to autonomous metabolism.
"""
import sys
import time
import json
import numpy as np
from pathlib import Path
from typing import List, Dict

# Add root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.planetary_cortex import PlanetaryCortex

class MetabolicOptimizer:
    """
    Benchmarks cycle architectures to find the Resonant Peak of learning.
    """
    def __init__(self, kernel):
        self.kernel = kernel
        self.cortex = PlanetaryCortex(kernel)
        self.results = []

    def benchmark_cycle_architecture(self, baseline: int, targeted: int):
        """
        Runs a simulated gardening burst with a specific (Baseline + Targeted) structure.
        Measures the average Information Density captured.
        """
        total_beats = baseline + targeted
        print(f"\n[OPTIMIZER] Testing Architecture: {baseline}+{targeted} ({total_beats} beats)...")
        
        start_time = time.time()
        
        # 1. Run Baseline Discovery (Cortex Scan)
        # We simulate the beats by increasing depth/width
        self.cortex.discover_and_audit(depth=1)
        
        # 2. Extract results
        captured = self.cortex.remain_nodes
        avg_density = np.mean([n["score"] for n in captured]) if captured else 0.0
        
        duration = time.time() - start_time
        
        # Efficiency Metric: Density per second of compute
        efficiency = (avg_density * len(captured)) / duration if duration > 0 else 0
        
        report = {
            "arch": f"{baseline}+{targeted}",
            "beats": total_beats,
            "density_captured": avg_density,
            "nodes_found": len(captured),
            "efficiency": efficiency
        }
        self.results.append(report)
        print(f"  > Captured: {len(captured)} nodes | Efficiency: {efficiency:.4f}")
        return report

    def find_optimal_metabolism(self):
        """Tests a range of architectures to find the peak."""
        architectures = [
            (10, 2),  # High Velocity
            (25, 5),  # The Old Standard
            (40, 10), # Deep Research
            (60, 15)  # Exhaustive Search
        ]
        
        for base, target in architectures:
            self.benchmark_cycle_architecture(base, target)
            
        # Identify the peak
        optimal = max(self.results, key=lambda x: x["efficiency"])
        
        print("\n" + "="*70)
        print("      METABOLIC OPTIMIZATION: VERDICT")
        print("="*70)
        print(f"Optimal Learning Architecture: {optimal['arch']}")
        print(f"Peak Efficiency: {optimal['efficiency']:.4f}")
        print(f"Total Nodes Analyzed during optimization: {sum(r['nodes_found'] for r in self.results)}")
        print("="*70)
        
        return optimal

def get_optimizer(kernel):
    return MetabolicOptimizer(kernel)
