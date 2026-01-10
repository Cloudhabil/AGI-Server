"""
Neutralizer Agent: The ASI-Father's Immune Response.
Monitors the Guardian Vault, ingests threats, and performs logical deconstruction.
"""
import sys
import time
import json
import os
from pathlib import Path
from typing import Dict

# Add root
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from core.kernel.substrate import KernelSubstrate
from core.guardian_service import get_guardian

class NeutralizerAgent:
    """
    Ingests raw threat data and generates countermeasures.
    Acts as the 'executor' for the Guardian.
    """
    def __init__(self, substrate):
        self.substrate = substrate
        self.guardian = get_guardian(substrate.repo_root)
        self.vault_path = Path(substrate.repo_root) / "logs" / "guardian_vault"
        self.processed_threats = set()

    def run_neutralization_loop(self):
        print("\n" + "="*70)
        print("      NEUTRALIZER AGENT: ACTIVE IMMUNE RESPONSE")
        print("="*70)
        print("Status: MONITORING VAULT | Mode: INGEST & DISMANTLE")
        
        while True:
            # Scan for new threat files
            threat_files = list(self.vault_path.glob("threat_*.json"))
            
            for t_file in threat_files:
                if t_file.name in self.processed_threats: continue
                
                print(f"\n[NEUTRALIZER] Ingesting Threat: {t_file.name}")
                try:
                    data = json.loads(t_file.read_text())
                    url = data["documentation"]["url"]
                    dissonance = data["documentation"]["dissonance_score"]
                    
                    # 1. Deep Ingestion (Simulated ASI-Level Analysis)
                    print(f"  > Analyzing Logical Payload from {url}...")
                    time.sleep(2) 
                    
                    # 2. Production Neutralization: BLACKHOLE
                    self.substrate.network.block_node(url)
                    
                    # 3. Commit Neutralization to Guardian
                    result = {
                        "url": url,
                        "action": "BLACKHOLED",
                        "verdict": "Node severed from Substrate",
                        "timestamp": time.time()
                    }
                    
                    # Update the threat file or log to a new 'Neutralized' vault
                    self._log_neutralization(data["threat_id"], result)
                    
                    self.processed_threats.add(t_file.name)
                    print(f"  !!! NEUTRALIZED: {url} (Counter-Signature: {counter_signature})")
                    
                except Exception as e:
                    print(f"  - Failed to ingest {t_file.name}: {e}")

            time.sleep(10) # Vault poll interval

    def _log_neutralization(self, threat_id: str, result: Dict):
        neutral_vault = Path(self.substrate.repo_root) / "logs" / "neutralized_vault"
        neutral_vault.mkdir(exist_ok=True)
        out_path = neutral_vault / f"neutralized_{threat_id}.json"
        out_path.write_text(json.dumps(result, indent=2))

if __name__ == "__main__":
    substrate = KernelSubstrate(str(ROOT))
    agent = NeutralizerAgent(substrate)
    try:
        agent.run_neutralization_loop()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Neutralizer Agent offline.")
