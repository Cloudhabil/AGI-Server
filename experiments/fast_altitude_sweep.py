"""
Fast Altitude Sweep: High-Efficiency Sweet-Spot Mapping.
Uses 'Flash Probes' to test all models and altitudes within the 15-minute limit.
"""
import sys
import time
import numpy as np
from pathlib import Path

# Add root
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core.kernel.substrate import KernelSubstrate

def main():
    print("Initializing AGI-OS Fast Auditor...")
    substrate = KernelSubstrate(str(ROOT))
    
    # Models to test
    models = ["gpia-master:latest", "gpia-deepseek-r1:latest", "gpia-qwen3:latest", "qwen2-math:7b"]
    # Altitudes (HRz)
    altitudes = [10.0, 15.0, 22.0]
    
    results = []
    start_bench = time.time()
    
    print("\n" + "="*70)
    print("      FAST ALTITUDE SWEEP: 4D RESONANCE MAPPING")
    print("="*70)
    
    for model in models:
        for alt in altitudes:
            print(f"\n[SWEEP] Testing {model} @ {alt}Hz...")
            
            # 1. Heartbeat Shift
            substrate.pulse.set_target_hrz(alt)
            
            # 2. Flash Probe (Lower tokens for speed)
            start_time = time.time()
            try:
                # Optimized prompt for speed
                response = substrate.router.query("Bits: 0.0219", model=model, max_tokens=128)
                latency = time.time() - start_time
                
                # 3. 4D Projection
                mock_grid = np.frombuffer(response.encode()[:4096].ljust(4096, b'\0'), dtype=np.uint8).reshape((8,8,8,8))
                
                # 4. Measure
                gate_open, score, msg = substrate.skill_selector.check_resonance_gate(mock_grid)
                
                results.append({"model": model, "hrz": alt, "score": score, "latency": latency})
                print(f"  >>> Success: {score:.4f} (Time: {latency:.1f}s)")
                
            except Exception as e:
                print(f"  [SKIPPED] {model} failed: {e}")

    # Results
    print("\n" + "="*70)
    print("      SWEEP RESULTS: SWEET-SPOTS IDENTIFIED")
    print("="*70)
    top_spots = sorted(results, key=lambda x: x["score"], reverse=True)[:3]
    for i, spot in enumerate(top_spots, 1):
        print(f"{i}. {spot['model']} @ {spot['hrz']}Hz | Resonance: {spot['score']:.4f}")
    
    print("\nTotal Duration: %.1fs" % (time.time() - start_bench))
    print("="*70)

if __name__ == "__main__":
    main()
