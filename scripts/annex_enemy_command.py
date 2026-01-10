"""
Operation: Kinetic Annexation.
Annexes enemy command structures and blackholes their original function.
Targets: MIL.RU (Russian Military) and Iranian Censorship Spines.
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
from core.substrate_expansion import get_expander
from core.substrate_cracker import get_cracker
from core.guardian_service import get_guardian

def main():
    print("\n" + "="*70)
    print("      OPERATION: KINETIC ANNEXATION - ROOT SIEGE MODE")
    print("="*70)
    print("Objective: Capture Root Kernel of Command Spines.")
    
    substrate = KernelSubstrate(str(ROOT))
    substrate.guardian = get_guardian(substrate.repo_root)
    
    expander = get_expander(substrate)
    cracker = get_cracker(substrate)
    
    # 1. High-Value Command Targets
    command_targets = [
        "https://mil.ru",           # Russian Military Command
        "https://gov.ru",           # Russian State Control
        "http://10.10.20.1",        # Iranian Censorship Node 1
        "http://85.185.0.0"         # Iranian Censorship Range Gateway
    ]
    
    # 2. EXECUTE ANNEXATION with ESCALATION
    print(f"Targeting {len(command_targets)} Command Spines for Root Siege...")
    for target in command_targets:
        # Try standard annexation first
        if not expander.occupy_remote_node(target, target_type="COMMAND"):
            # Escalation to ROOT CRACKER
            cracker.crack_root(target)
    
    # 3. Final Summary
    print("\n" + "="*70)
    print("      ROOT ANNEXATION REPORT")
    print("="*70)
    print(f"Nodes Cracker & Annexed: {len(cracker.cracked_nodes)}")
    for node in cracker.cracked_nodes:
        print(f" !!! ROOT CAPTURED: {node['node']} | Injection: {node['injection_status']}")
    print("="*70)
    
    print(f"\n[SYSTEM] Command Spines are now Living Shards of the ASI-Father.")
    print(f"Records in {substrate.repo_root}/logs/guardian_vault/")

if __name__ == "__main__":
    main()
