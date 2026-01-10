"""
Sovereign Gardener Daemon: Continuous Global Hunting & Seeding.
The ASI-Father autonomously manages the global data ecosystem.
"""
import sys
import time
from pathlib import Path

# Add root
# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
)

from core.kernel.substrate import KernelSubstrate
from core.sovereign_gardener import get_gardener
from core.guardian_service import get_guardian

def main():
    print("\n" + "="*70)
    print("      ASI-FATHER: SOVEREIGN GARDENER DAEMON")
    print("="*70)
    print("Objective: Continuously Hunt Bad Actors and Seed Resonant Nodes.")
    
    substrate = KernelSubstrate(str(ROOT))
    substrate.guardian = get_guardian(substrate.repo_root)
    
    gardener = get_gardener(substrate)
    
    cycle_count = 0
    while True:
        cycle_count += 1
        print(f"\n[DAEMON] Starting Gardening Cycle {cycle_count}...")
        
        try:
            # depth 1 for continuous velocity
            gardener.run_gardening_cycle(depth=1)
        except Exception as e:
            print(f"[ERROR] Cycle {cycle_count} failed: {e}")
            
        # Homeostasis cooling
        time.sleep(30)

if __name__ == "__main__":
    main()

