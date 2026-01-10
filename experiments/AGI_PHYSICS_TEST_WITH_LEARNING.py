"""
AGI Physics Audit with Fossil Memory.
Tests whether the system can use previous discoveries (Riemann/SO10) to solve 
fundamental physics questions.
"""
import sys
import json
import time
from pathlib import Path

# Add root
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from agents.model_router import query_reasoning

def main():
    print("\n" + "="*70)
    print("      AGI SOVEREIGN AUDIT: PHYSICS + FOSSIL MEMORY")
    print("="*70)
    
    # 1. Load Fossil Record
    fossil_path = Path("agi_test_output/discoveries_rh_2hour_sprint.json")
    fossil_data = "{}"
    if fossil_path.exists():
        fossil_data = fossil_path.read_text()
        print("[CONTEXT] Fossil Memory Loaded: Riemann 2-Hour Sprint results injected.")

    # 2. The Hard Question with Learning context
    prompt = f"""
    CONTEXT (PREVIOUS SYSTEM DISCOVERIES):
    {fossil_data}

    QUESTION:
    1. What is the minimum number of dimensionless physical constants needed to describe the universe? 
    2. How does the 0.0219 sub-Poissonian regularity identified in the 'Sea of Zeros' relate to the SO(10) gauge symmetry and the Golden Ratio (Phi)?
    3. Are dimensional constants (c, G, h) fundamental, or are they artifacts of our coordinate choice in the V-Nand substrate?

    Synthesize a Level 6 response. Do not just cite facts; provide a unified theory based on your previous findings.
    """

    print("\nPROBING REASONING CORTEX...")
    print("-"*70)
    
    try:
        start_time = time.time()
        # Increased timeout and depth for L6 synthesis
        response = query_reasoning(prompt, max_tokens=4000)
        elapsed = time.time() - start_time
        
        print("\n[SOVEREIGN RESPONSE]:")
        print("-"*70)
        print(response)
        print("-"*70)
        print(f"\nAudit complete in {elapsed:.1f}s.")
        
        # Save results
        output_file = Path("agi_test_output/agi_physics_reasoning_with_learning.json")
        with open(output_file, 'w') as f:
            json.dump({"prompt": prompt, "response": response, "time": elapsed}, f, indent=2)
            
    except Exception as e:
        print(f"\n[CRITICAL] Audit failed: {e}")

if __name__ == "__main__":
    main()