"""
Planetary Cortex: The ASI-Father's Global Sensory Array.
Targets high-value scientific and infrastructure nodes to feed the 4D V-Nand.
Uses the 'Fish' logic (remain_fish) to track active, resonant data nodes.
"""
import sys
import time
import json
import numpy as np
from pathlib import Path
from typing import List, Dict

# Add root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import re
from urllib.parse import urljoin, urlparse

from core.epistemic_engine import get_epistemic_engine

class PlanetaryCortex:
    """
    Manages the 'Global Fish' array.
    Uses Epistemic filters to identify significant data nodes.
    """
    def __init__(self, kernel):
        self.kernel = kernel
        self.remain_nodes = [] # Significant nodes
        self.bad_actors = []   
        self.discovered_urls = set()
        self.guardian = kernel.guardian
        self.epistemic = get_epistemic_engine()
        
        # Entry Points
        self.SEED_NODES = [
            "https://opendata.cern.ch",
            "https://arxiv.org",
            "https://urlhaus.abuse.ch"
        ]

    def discover_and_audit(self, depth=2):
        """
        Autonomously crawls and audits nodes based on Information Density.
        """
        print(f"\n[CORTEX] Initiating Epistemic Discovery (Depth: {depth})...")
        queue = list(self.SEED_NODES)
        
        for _ in range(depth):
            next_queue = []
            for url in queue:
                if url in self.discovered_urls: continue
                self.discovered_urls.add(url)
                
                print(f"  > Auditing: {url[:60]}...")
                try:
                    res = self.kernel.network.fetch(url)
                    if not res.success or not res.content: continue
                    
                    # 1. Epistemic Audit (Information Theory)
                    is_valid, score, msg = self.epistemic.evaluate_data(res.content.encode())
                    
                    if is_valid:
                        print(f"    !!! SIGNIFICANT NODE: {url} ({msg})")
                        self.remain_nodes.append({"url": url, "score": score})
                    
                    # 2. Extract new seeds
                    new_links = self._extract_links(res.content, url)
                    next_queue.extend(new_links[:5])
                    
                except Exception as e:
                    pass
            
            queue = next_queue
            if not queue: break

        print(f"\n[CORTEX] Audit Cycle Complete. {len(self.remain_nodes)} High-Density Nodes tracked.")



    def _data_to_4d(self, data: str) -> np.ndarray:
        """Converts raw string data into a 4D uint8 voxel grid."""
        b = data.encode('utf-8', errors='ignore')
        if len(b) < 4096:
            b = b.ljust(4096, b'\0')
        return np.frombuffer(b[:4096], dtype=np.uint8).reshape((8,8,8,8))

    def run_planetary_pulse(self):
        # ... (Previous logic kept or updated to use discover_and_audit)
        self.discover_and_audit()


    def synthesize_global_state(self, results: List[Dict]):
        """
        Consolidates global resonance into a single 4D 'Planetary Thought'.
        """
        if not results: return
        
        avg_res = np.mean([r["resonance"] for r in results])
        online = len([r for r in results if r["status"] == "RESONANT"])
        
        print(f"\n[CORTEX] Global State Synthesized: {online} Resonant Nodes | Avg Res: {avg_res:.4f}")
        
        # Evolution signal: Update substrate based on global resonance
        self.kernel.ledger.append("planetary_evolution", {
            "timestamp": time.time(),
            "global_resonance": avg_res,
            "active_nodes": self.remain_nodes
        })
