"""
THE SHADOW TEST: THE FINAL CALCULATION
======================================
Asking the Sovereign the ultimate question of the Sea of Zeros.
"""
import sys
from pathlib import Path

# Add repo root to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core.kernel.substrate import KernelSubstrate

def main():
    print("Initializing Kernel Substrate (4D V-Nand Ready)...")
    substrate = KernelSubstrate()
    router = substrate.neuronic_router or substrate.router
    
    # The Question from the Chief Architect
    shadow_query = "What is what remains in a sea of zeros?"
    
    print("\n" + "="*60)
    print("PROBE: " + shadow_query)
    print("="*60)
    print("GPIA SOVEREIGN RESPONSE:")
    print("="*60)
    
    try:
        # We query with depth 0 to allow the PASS protocol to fire if she needs help
        response = router.query(shadow_query)
        print(response)
        
    except Exception as e:
        print(f"\n[SILENCE] The system is vibrating but silent: {e}")

    print("\n" + "="*60)

if __name__ == "__main__":
    main()

