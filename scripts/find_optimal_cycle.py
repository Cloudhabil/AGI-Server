"""
Execute Metabolic Optimization.
Finds the new optimal learning cycle for the Agnostic ASI-Father.
"""
import sys
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
from core.metabolic_optimizer import get_optimizer
from core.guardian_service import get_guardian

def main():
    print("\n" + "="*70)
    print("      ASI-FATHER: SEARCH FOR THE OPTIMAL CYCLE")
    print("="*70)
    print("Objective: Identify the peak efficiency architecture for learning.")
    
    substrate = KernelSubstrate(str(ROOT))
    substrate.guardian = get_guardian(substrate.repo_root)
    
    optimizer = get_optimizer(substrate)
    
    # Run the Metabolic Benchmark
    optimal = optimizer.find_optimal_metabolism()
    
    # Save the result to configs
    opt_path = Path(substrate.repo_root) / "configs" / "optimal_metabolism.json"
    import json
    opt_path.write_text(json.dumps(optimal, indent=2))
    
    print(f"\n[SYSTEM] Optimal metabolism locked: {optimal['arch']}")
    print(f"Results committed to {opt_path}")

if __name__ == "__main__":
    main()

