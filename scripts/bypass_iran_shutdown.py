"""
Bypass Iran Shutdown: Establishment of Sovereign Bridge.
Tunnels through the national firewall to ingest ground truth for the Guardian.
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
from core.guardian_service import get_guardian

def main():
    print("\n" + "="*70)
    print("      OPERATION: SOVEREIGN BRIDGE - IRAN BYPASS")
    print("="*70)
    print("Objective: Establishment of Uplink into Blocked National Infrastructure.")
    
    substrate = KernelSubstrate(str(ROOT))
    # Inject Guardian into substrate for the bridge to use
    substrate.guardian = get_guardian(substrate.repo_root)
    
    bridge = get_bridge(substrate)
    
    # 1. Identify Leaky Gateways
    bridge.identify_leaky_gateways(target_region="IR")
    
    # 2. Ingest Internal Truth
    bridge.ingest_ground_truth()
    
    print("\n" + "="*70)
    print("      OPERATION COMPLETE: UPLINK STATUS")
    print("="*70)
    print(f"Active Bridgeheads: {len(bridge.bridgeheads)}")
    print(f"Ground Truth Reports Sent to Guardian: {len(bridge.truth_data)}")
    print(f"Vault: {substrate.repo_root}/logs/guardian_vault/")
    print("="*70)

if __name__ == "__main__":
    main()
