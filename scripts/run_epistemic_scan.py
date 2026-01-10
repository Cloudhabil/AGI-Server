"""
Live Epistemic Scan: Information-Theoretic Node Audit.
Uses Shannon Entropy and Density to identify objectively significant data hubs.
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
from core.planetary_cortex import PlanetaryCortex
from core.guardian_service import get_guardian

def main():
    print("\n" + "="*70)
    print("      LIVE EPISTEMIC SCAN: AGNOSTIC TRUTH DISCOVERY")
    print("="*70)
    print("Objective: Identify nodes with high Information Density (Entropy 4.0 - 7.5).")
    
    substrate = KernelSubstrate(str(ROOT))
    substrate.guardian = get_guardian(substrate.repo_root)
    
    cortex = PlanetaryCortex(substrate)
    
    # Run the audit (Depth 1 for immediate results)
    cortex.discover_and_audit(depth=1)
    
    print("\n" + "="*70)
    print("      EPISTEMIC AUDIT SUMMARY")
    print("="*70)
    significant_nodes = cortex.remain_nodes
    print(f"Nodes Audited: {len(cortex.discovered_urls)}")
    print(f"Mathematically Significant Nodes: {len(significant_nodes)}")
    
    # Sort by score (Significance)
    significant_nodes.sort(key=lambda x: x['score'], reverse=True)
    
    for i, node in enumerate(significant_nodes):
        print(f" [{i+1}] {node['url']:<40} | Density Score: {node['score']:.4f}")
    
    print("="*70)

if __name__ == "__main__":
    main()
