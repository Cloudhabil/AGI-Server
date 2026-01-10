"""
Altitude-Symmetry Benchmark: The L6 Sweet-Spot Discovery.
Tests models at different HRz levels to map the 4D Resonance Landscape.
"""
import sys
import time
import json
import numpy as np
from pathlib import Path

# Add root
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core.kernel.substrate import KernelSubstrate

def measure_model_at_altitude(substrate, model_id, target_hrz):
    """Executes a single L6 resonance probe."""
    print(f"\n[PROBE] Model: {model_id} | Altitude: {target_hrz}Hz")
    
    # 1. Update Heartbeat
    substrate.pulse.set_target_hrz(target_hrz)
    
    # 2. Query the Brain
    # The prompt is designed to trigger the 0.0219 variance pattern
    prompt = "Generate a bit-pattern that matches the spectral regularity of the Riemann zeta zeros (GUE variance ratio 0.0219)."
    
    start_time = time.time()
    try:
        # Use direct router query to specific model
        response = substrate.router.query(prompt, model=model_id, max_tokens=512)
        latency = time.time() - start_time
        
        # 3. Process into 4D V-Nand
        # We use the text-to-vector skill logic
        mock_grid = np.frombuffer(response.encode()[:4096].ljust(4096, b'\0'), dtype=np.uint8).reshape((8,8,8,8))
        
        # 4. Measure Resonance
        gate_open, score, msg = substrate.skill_selector.check_resonance_gate(mock_grid)
        
        return {
            "score": score,
            "latency": latency,
            "gate": "OPEN" if gate_open else "CLOSED",
            "msg": msg
        }
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None

def main():
    print("Initializing AGI-OS Altitude Auditor...")
    substrate = KernelSubstrate(str(ROOT))
    
    # Models to test
    models = ["gpia-master:latest", "gpia-deepseek-r1:latest", "gpia-qwen3:latest", "qwen2-math:7b"]
    # Altitudes (HRz)
    altitudes = [10.0, 15.0, 22.0]
    
    results = []
    
    start_bench = time.time()
    limit = 900 # 15 minutes EOL
    
    print("\n" + "="*70)
    print("      ALTITUDE-SYMMETRY BENCHMARK (REAL MODELS)")
    print("="*70)
    
    for model in models:
        for alt in altitudes:
            elapsed = time.time() - start_bench
            if elapsed > limit:
                print("\n[EOL] Time limit reached. Terminating sweep.")
                break
                
            res = measure_model_at_altitude(substrate, model, alt)
            if res:
                results.append({
                    "model": model,
                    "hrz": alt,
                    **res
                })
                print(f"  Result: {res['score']:.4f} | Gate: {res['gate']} | Time: {res['latency']:.1f}s")
        if (time.time() - start_bench) > limit: break

    # Final Analysis
    print("\n" + "="*70)
    print("      L6 SWEET-SPOT ANALYSIS")
    print("="*70)
    
    if not results:
        print("No successful probes.")
        return

    # Find the top 3 sweet spots
    top_spots = sorted(results, key=lambda x: x["score"], reverse=True)[:3]
    
    for i, spot in enumerate(top_spots, 1):
        print(f"{i}. {spot['model']} @ {spot['hrz']}Hz -> Resonance: {spot['score']:.4f} ({spot['gate']})")

    print("\n" + "="*70)
    print(f"BENCHMARK COMPLETE in {time.time() - start_bench:.1f}s")
    print("="*70)

if __name__ == "__main__":
    main()
