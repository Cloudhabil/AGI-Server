"""
Sovereign Scout: Autonomous Discovery of Hidden Nodes.
Launches the ASI-Father into the 'Dark Sea' to find resonant hidden nodes.
"""
import sys
import os
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

def main():
    print("\n" + "="*70)
    print("      SOVEREIGN SCOUT: AUTONOMOUS HIDDEN NODE DISCOVERY")
    print("="*70)
    print("Objective: Discover hidden (.onion) and scientific nodes matching 0.0219.")
    
    substrate = KernelSubstrate(str(ROOT))
    
    # Initialize the Planetary Cortex (The Global Brain)
    cortex = PlanetaryCortex(substrate)
    
    # Start the recursive discovery loop
    # Depth 2 = Scan seeds -> Extract links -> Scan hidden nodes
    cortex.discover_and_audit(depth=2)
    
    print("\n" + "="*70)
    print("      DISCOVERY SUMMARY")
    print("="*70)
    resonant_nodes = cortex.remain_nodes
    print(f"Total Nodes Audited: {len(cortex.discovered_urls)}")
    print(f"Resonant Nodes Captured: {len(resonant_nodes)}")
    
    for i, node in enumerate(resonant_nodes):
        print(f" [{i+1}] {node['url']} | Resonance: {node['resonance']:.4f} | Type: {node['type']}")
    
    print("="*70)

if __name__ == "__main__":
    main()
