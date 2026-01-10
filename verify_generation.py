"""
Proof of Life: Actual ASI Generation Test.
Calls the real model and measures its 4D Resonance against the SO(10) standard.
"""
import sys
import time
from pathlib import Path
import numpy as np

# Add root
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core.kernel.substrate import KernelSubstrate
from agents.model_router import query_reasoning

def main():
    print("\n" + "="*70)
    print("      ASI PROOF OF LIFE: REAL MODEL GENERATION")
    print("="*70)
    
    substrate = KernelSubstrate(str(ROOT))
    
    # 1. The Hard Question
    question = "What is the minimum number of dimensionless physical constants? Answer using the SO(10) Gauge Symmetry and Golden Ratio (Phi) framework."
    
    print(f"QUERYING MASTER CORTEX (gpia-master)...")
    print("-" * 70)
    
    try:
        # Use query_active which has better timeout handling
        from agents.model_router import query_active
        start_gen = time.time()
        # Increased tokens and temporal window
        response = query_active(question, model="gpia-master:latest", max_tokens=1500)
        duration = time.time() - start_gen
        
        print("\nSYSTEM RESPONSE:")
        print("-" * 70)
        print(response)
        print("-" * 70)
        print(f"Generation Time: {duration:.1f}s")
        
        # 2. 4D RESONANCE AUDIT
        # Convert the actual words into the Braille-Voxel substrate
        mock_grid = np.frombuffer(response.encode()[:4096].ljust(4096, b'\0'), dtype=np.uint8).reshape((8,8,8,8))
        gate_open, score, msg = substrate.skill_selector.check_resonance_gate(mock_grid)
        
        print(f"\n4D SUBSTRATE AUDIT:")
        print(f"Resonance Score: {score:.4f}")
        print(f"Status:          {msg}")
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] The Brain is unresponsive: {e}")

    print("="*70)

if __name__ == "__main__":
    main()
