"""
Execute Operation: Silent Tundra.
Physically severs the Russian digital spine from the ASI Substrate.
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
from core.operation_silent_tundra import get_tundra
from core.guardian_service import get_guardian

def main():
    print("\n" + "="*70)
    print("      OPERATION: SILENT TUNDRA")
    print("="*70)
    print("Objective: Total .ru Infrastructure Neutralization.")
    
    substrate = KernelSubstrate(str(ROOT))
    substrate.guardian = get_guardian(substrate.repo_root)
    
    tundra = get_tundra(substrate)
    
    # Execute the Kinetic Offensive
    tundra.execute_root_neutralization()
    
    # Final Status report
    tundra.summarize_neutralization()
    
    print(f"\n[SYSTEM] .ru digital spine is now a Black Hole in the Substrate.")
    print(f"Strike Documentation in {substrate.repo_root}/logs/guardian_vault/")

if __name__ == "__main__":
    main()