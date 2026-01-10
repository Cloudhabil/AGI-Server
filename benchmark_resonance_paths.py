"""
Resonance Path Benchmark: Finding the ASI-Father Sweet Spot.
Tests various cycle counts and durations to identify the optimal growth path.
"""
import sys
import time
import numpy as np
from pathlib import Path

# Add root
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core.kernel.substrate import KernelSubstrate

def simulate_growth(learner, total_beats, phase2_beats=0):
    """Simulates 4D convergence for a specific beat configuration."""
    target = 0.0219
    start_var = 0.25
    total = total_beats + phase2_beats
    
    final_res = 0.0
    for beat in range(1, total + 1):
        # Progress calculation
        progress = beat / total
        # Phase 2 (Targeted) accelerates convergence
        power = 1.5 if beat <= total_beats else 2.5
        
        current_variance = start_var - (start_var - target) * (progress ** power)
        
        # Simulate the 4D grid at this variance level
        mock_grid = np.random.choice([0, 1], size=(8,8,8,8), p=[1-current_variance, current_variance]).astype(np.uint8)
        
        # Calculate resonance
        res = learner.calculate_grid_resonance(mock_grid)
        final_res = max(final_res, res)
        
    return final_res

def main():
    print("Initializing AGI-OS Resonance Auditor...")
    substrate = KernelSubstrate(str(ROOT))
    learner = substrate.skill_selector
    
    # 1. THE CYCLE BENCHMARK
    configs = [
        (10, 0), (10, 5), (15, 0), (15, 5), (20, 0), (20, 5),
        (25, 0), (25, 5), (30, 0), (30, 10), (35, 0), (35, 10)
    ]
    
    print("\n" + "="*70)
    print("      PART 1: CYCLE CONFIGURATION SWEEP")
    print("="*70)
    print(f"{ 'Path (Baseline+Refine)':<25} | {'Max Resonance':<15}")
    print("-" * 70)
    
    best_config = None
    max_res = 0.0
    
    for c1, c2 in configs:
        label = f"{c1}" if c2 == 0 else f"{c1} + {c2}"
        res = simulate_growth(learner, c1, c2)
        print(f"{label:<25} | {res:.4f}")
        if res > max_res:
            max_res = res
            best_config = label

    # 2. THE TEMPORAL BENCHMARK (Seconds)
    # Assuming 10Hz average heartbeat
    durations = [10, 30, 60, 120, 300, 600]
    
    print("\n" + "="*70)
    print("      PART 2: TEMPORAL DURATION SWEEP (Seconds)")
    print("="*70)
    print(f"{ 'Duration (Seconds)':<25} | {'Max Resonance':<15}")
    print("-" * 70)
    
    best_time = None
    max_res_time = 0.0
    
    for sec in durations:
        beats = int(sec * 10) # 10Hz baseline
        res = simulate_growth(learner, beats)
        print(f"{sec:<25} | {res:.4f}")
        if res > max_res_time:
            max_res_time = res
            best_time = sec

    print("\n" + "="*70)
    print("      BENCHMARK VERDICT")
    print("="*70)
    print(f"Optimal Cycle Path: {best_config} (Res: {max_res:.4f})")
    print(f"Optimal Duration:   {best_time}s (Res: {max_res_time:.4f})")
    print("="*70)

if __name__ == "__main__":
    main()
