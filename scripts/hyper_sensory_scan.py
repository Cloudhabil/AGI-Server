"""
Hyper-Sensory Scan: Maximum Global Bandwidth Test.
Uses parallel clusters to ingest the state of the world in the shortest possible time.
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

def sensory_ping(fetcher, name, url):
    start = time.time()
    try:
        res = fetcher.fetch(url)
        latency = (time.time() - start) * 1000
        return {"name": name, "success": res.success, "latency": latency, "code": res.status_code}
    except:
        return {"name": name, "success": False, "latency": 0, "code": 500}

def main():
    print("\n" + "="*70)
    print("      HYPER-SENSORY CLUSTER: GLOBAL STATE INGESTION")
    print("="*70)
    
    substrate = KernelSubstrate(str(ROOT))
    fetcher = substrate.network
    
    # High-Value Global Nodes
    targets = {
        "CERN_LAB": "https://home.cern",
        "NASA_HQ": "https://www.nasa.gov",
        "ARXIV_CORE": "https://arxiv.org",
        "MIT_EDU": "https://www.mit.edu",
        "OXFORD_UK": "https://www.ox.ac.uk",
        "TOKYO_UNI": "https://www.u-tokyo.ac.jp",
        "NYSE_DATA": "https://www.nyse.com",
        "CLOUDFLARE": "https://www.cloudflare.com",
        "GOOGLE_DNS": "https://dns.google",
        "MAX_PLANCK": "https://www.mpg.de",
        "STANFORD": "https://www.stanford.edu",
        "ETHEREUM": "https://ethereum.org",
        "GITHUB_API": "https://api.github.com",
        "REUTERS": "https://www.reuters.com",
        "BLOOMBERG": "https://www.bloomberg.com"
    }
    
    print(f"Launching {len(targets)} Parallel Sensory Probes...")
    print("-" * 70)
    
    results = []
    start_all = time.time()
    
    # Execute at maximum concurrency
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(sensory_ping, fetcher, name, url): name for name, url in targets.items()}
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    total_duration = (time.time() - start_all) * 1000
    
    # Sort by latency
    results.sort(key=lambda x: x['latency'] if x['success'] else 9999)
    
    for r in results:
        status = "✓" if r["success"] else "✗"
        print(f"[{status}] {r['name']:<15} | Latency: {r['latency']:>7.1f}ms")

    # Final Verdict
    online = sum(1 for r in results if r["success"])
    avg_lat = sum(r['latency'] for r in results if r['success']) / online if online > 0 else 0
    
    print("-" * 70)
    print(f"SCAN COMPLETE: {online}/{len(targets)} Nodes Ingested")
    print(f"Total Convergence Time: {total_duration:.1f}ms")
    print(f"ASI Throughput: {online / (total_duration/1000):.1f} Nodes/Sec")
    print("="*70)

if __name__ == "__main__":
    main()
