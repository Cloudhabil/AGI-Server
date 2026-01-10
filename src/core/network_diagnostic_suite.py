"""
Substrate Network Diagnostic Suite: Professional Monitoring & Analysis.
Provides real-time telemetry, SSL integrity audits, and path-trace mapping.
Designed for authorized network engineering and data analysis.
"""
import sys
import time
import socket
import ssl
import subprocess
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional

# Add root
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

class NetworkDiagnosticSuite:
    """
    High-fidelity network analysis engine.
    Monitors global connectivity health and path integrity.
    """
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.history_dir = self.repo_root / "logs" / "network_telemetry"
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def audit_ssl_integrity(self, host: str, port: int = 443) -> Dict:
        """Validates the SSL/TLS certificate chain for a given host."""
        print(f"  > Auditing SSL Integrity for {host}...")
        context = ssl.create_default_context()
        try:
            with socket.create_connection((host, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    return {
                        "host": host,
                        "status": "SECURE",
                        "issuer": cert.get('issuer'),
                        "version": ssock.version(),
                        "cipher": ssock.cipher()
                    }
        except Exception as e:
            return {"host": host, "status": "TAMPERED_OR_BLOCKED", "error": str(e)}

    def analyze_path_latency(self, target: str, count: int = 5) -> Dict:
        """Performs statistical latency analysis using ICMP/Ping."""
        print(f"  > Analyzing Path Latency to {target}...")
        latencies = []
        try:
            # Platform-specific ping command
            cmd = ["ping", "-n" if sys.platform == "win32" else "-c", str(count), target]
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
            
            # Extract times using parsing
            for line in output.splitlines():
                if "tiempo=" in line: # Spanish Windows locale check
                    t_str = line.split("tiempo=")[-1].split("ms")[0].replace("<", "")
                    latencies.append(float(t_str))
                elif "time=" in line: # English locale check
                    t_str = line.split("time=")[-1].split("ms")[0].replace("<", "")
                    latencies.append(float(t_str))
            
            if not latencies: return {"target": target, "status": "UNREACHABLE"}
            
            return {
                "target": target,
                "min_ms": float(np.min(latencies)),
                "max_ms": float(np.max(latencies)),
                "avg_ms": float(np.mean(latencies)),
                "jitter": float(np.std(latencies)),
                "packet_loss": 0.0
            }
        except Exception as e:
            return {"target": target, "status": "FAILED", "error": str(e)}

    def run_full_diagnostics(self, targets: List[str]):
        """Executes a complete telemetry sweep."""
        print("\n" + "="*70)
        print("      SUBSTRATE NETWORK TELEMETRY SWEEP")
        print("="*70)
        
        results = []
        for target in targets:
            domain = target.split("//")[-1].split("/")[0]
            
            # 1. Latency Analysis
            latency_data = self.analyze_path_latency(domain)
            
            # 2. Integrity Audit
            ssl_data = self.audit_ssl_integrity(domain)
            
            entry = {
                "timestamp": time.time(),
                "latency": latency_data,
                "integrity": ssl_data
            }
            results.append(entry)
            
            if latency_data.get("status") != "FAILED" and latency_data.get("status") != "UNREACHABLE":
                print(f" [{entry['integrity']['status']}] {domain:<30} | Avg: {latency_data['avg_ms']:.1f}ms | Jitter: {latency_data['jitter']:.2f}")
            else:
                print(f" [FAILED] {domain:<30} | Status: {latency_data.get('status')}")

        # Save to history
        log_path = self.history_dir / f"telemetry_{int(time.time())}.json"
        log_path.write_text(json.dumps(results, indent=2))
        return results

def get_diag_suite(repo_root: str = "."):
    return NetworkDiagnosticSuite(repo_root)
