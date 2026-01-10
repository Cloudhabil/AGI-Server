"""
Regional Resonance Audit: Iran Sector.
Targets Iranian scientific and technical infrastructure to find 0.0219 resonance.
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

def main():
    print("\n" + "="*70)
    print("      REGIONAL RESONANCE AUDIT: IRAN SECTOR")
    print("="*70)
    print("Objective: Map .ir technical infrastructure and discover hidden research nodes.")
    
    substrate = KernelSubstrate(str(ROOT))
    cortex = PlanetaryCortex(substrate)
    
    # Override seeds for Iran Sector
    cortex.SEED_NODES = [
        "https://www.irandoc.ac.ir",    # Scientific Archives
        "https://www.sharif.edu",      # Technical High-Entropy
        "https://www.ut.ac.ir",        # University of Tehran Core
        "https://ahmia.fi/search/?q=iran+onion" # Cross-reference for hidden Iranian nodes
    ]
    
    # Execute the Predatory Scout
    cortex.discover_and_audit(depth=2)
    
    print("\n" + "="*70)
    print("      IRAN SECTOR SUMMARY")
    print("="*70)
    resonant_nodes = cortex.remain_nodes
    print(f"Nodes Audited in Sector: {len(cortex.discovered_urls)}")
    print(f"Resonant/Interesting Nodes Captured: {len(resonant_nodes)}")
    
    for i, node in enumerate(resonant_nodes):
        print(f" [{i+1}] {node['url']} | Resonance: {node['resonance']:.4f} | Type: {node['type']}")
    print("="*70)

if __name__ == "__main__":
    main()
