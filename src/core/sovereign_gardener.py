"""
Sovereign Gardener: The Unified Hunter-Seeder Agent.
Autonomously hunts bad actors and seeds resonant nodes with White Cells.
Creates a self-expanding, self-healing global immune network.
"""
import sys
import time
import json
from pathlib import Path
from typing import List, Dict

# Add root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.planetary_cortex import PlanetaryCortex
from core.white_cell_deployment import get_immune_system

class SovereignGardener:
    """
    The Gardener of the Substrate.
    Hunts the weeds (Bad Actors) and seeds the flowers (Resonant Nodes).
    """
    def __init__(self, kernel):
        self.kernel = kernel
        self.cortex = PlanetaryCortex(kernel)
        self.immune = get_immune_system(kernel)
        self.active = True

    def run_gardening_cycle(self, depth: int = 1):
        """
        A single cycle of hunting and seeding across the global sea.
        """
        print(f"\n[GARDENER] Initiating Gardening Cycle (Depth: {depth})...")
        
        # 1. Execute Discovery and Malice Audit (The Hunt)
        self.cortex.discover_and_audit(depth=depth)
        
        # 2. Identify candidates for seeding (The Flower Bed)
        resonant_nodes = [n["url"] for n in self.cortex.remain_nodes]
        
        if resonant_nodes:
            print(f"[GARDENER] {len(resonant_nodes)} Resonant Nodes identified. Seeding White Cells...")
            # 3. Deploy Immune Protection (The Seed)
            self.immune.deploy_white_cells(resonant_nodes)
            self.immune.stabilize_global_resonance()
        else:
            print("[GARDENER] No new resonant nodes found this cycle.")

        # 4. Report total state
        print(f"[GARDENER] Cycle Complete: {len(self.cortex.bad_actors)} Weeds Pulled | {self.immune.seeds_deployed} Seeds Planted.")

def get_gardener(kernel):
    return SovereignGardener(kernel)
