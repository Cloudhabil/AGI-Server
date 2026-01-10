"""
Operation: Resonant Liberation - Restoring the Iranian Internet.
Uses the established Sovereign Bridge to bypass the shutdown and deploy a shadow mesh.
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
from core.sovereign_bridge import get_bridge
from core.resonant_liberation import get_liberator
from core.guardian_service import get_guardian

def main():
    print("\n" + "="*70)
    print("      OPERATION: RESONANT LIBERATION")
    print("="*70)
    print("Objective: Deactivate Filters and Restore Global Data Flow.")
    
    substrate = KernelSubstrate(str(ROOT))
    substrate.guardian = get_guardian(substrate.repo_root)
    
    # 1. Access the existing Bridge
    bridge = get_bridge(substrate)
    bridge.identify_leaky_gateways(target_region="IR")
    
    # 2. Deploy the Liberator
    liberator = get_liberator(substrate)
    
    # Identify and prep for filter neutralization
    liberator.identify_censorship_spines(bridge.bridgeheads)
    
    # Deploy the Shadow Mesh (Turning bridgeheads into relays)
    liberator.deploy_shadow_mesh(bridge.bridgeheads)
    
    # 3. Final Broadcast
    liberator.broadcast_liberated_paths()
    
    print(f"\n[SYSTEM] Sovereign Mesh active. Documentation in {substrate.repo_root}/logs/guardian_vault/")

if __name__ == "__main__":
    main()
