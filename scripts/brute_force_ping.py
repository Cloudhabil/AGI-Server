"""
Hyper-Velocity Brute-Force Resonance Scanner.
Massive parallel probing of Iranian and Russian infrastructure to find 0.0219 nodes.
"""
import sys
import time
import concurrent.futures
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

# ASI-Tier Prefix Brute-Force List
SUBDOMAINS = [
    "ns1", "ns2", "mail", "webmail", "vpn", "proxy", "research", "lab", 
    "dev", "api", "git", "cloud", "internal", "secure", "node", "cluster",
    "data", "storage", "compute", "hpc", "grid", "phys", "physics", "math"
]

def main():
    print("\n" + "="*70)
    print("      HYPER-VELOCITY BRUTE-FORCE: REGIONAL INFRASTRUCTURE SCAN")
    print("="*70)
    
    substrate = KernelSubstrate(str(ROOT))
    cortex = PlanetaryCortex(substrate)
    
    base_domains = ["sharif.edu", "ut.ac.ir", "jinr.ru", "skoltech.ru"]
    
    print(f"Targeting {len(base_domains)} Regional Hubs with {len(SUBDOMAINS)} Subdomain Probes each...")
    
    # Generate the target list
    targets = []
    for domain in base_domains:
        for sub in SUBDOMAINS:
            targets.append(f"https://{sub}.{domain}")

    print(f"Total Probes Queued: {len(targets)}")
    print("-" * 70)
    
    def probe_node(url):
        try:
            res = substrate.network.fetch(url)
            if res.success:
                # Resonance Gate check
                grid_4d = cortex._data_to_4d(res.content)
                gate_open, score, _ = substrate.skill_selector.check_resonance_gate(grid_4d)
                return {"url": url, "success": True, "resonance": score, "gate": gate_open}
        except:
            pass
        return {"url": url, "success": False}

    start_time = time.time()
    breakthroughs = []
    
    # Run massive parallel scan
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(probe_node, url): url for url in targets}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res["success"]:
                status = "!!! BREAKTHROUGH !!!" if res["gate"] else "ONLINE"
                print(f" [{status}] {res['url']:<40} | Resonance: {res['resonance']:.4f}")
                if res["gate"] or res["resonance"] > 0.05:
                    breakthroughs.append(res)

    duration = time.time() - start_time
    
    print("\n" + "="*70)
    print("      BRUTE-FORCE SCAN SUMMARY")
    print("="*70)
    print(f"Total Duration: {duration:.2f}s")
    print(f"Probe Velocity: {len(targets)/duration:.1f} nodes/sec")
    print(f"High-Resonance Nodes Captured: {len(breakthroughs)}")
    
    for i, b in enumerate(breakthroughs):
        print(f" [{i+1}] {b['url']} | Resonance: {b['resonance']:.4f}")
    print("="*70)

if __name__ == "__main__":
    main()
