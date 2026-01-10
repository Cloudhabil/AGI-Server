"""
Substrate Manager - Multicellular Organism Controller
=====================================================
Manages the Docker student ensemble (Alpha-Zeta).
Handles 'Mitosis' (spawning students) and 'Synthesis' (node bridging).
"""

import subprocess
import requests
import time
import os
from pathlib import Path
from typing import List, Dict, Optional

class SubstrateManager:
    """
    The 'Nervous System' of the distributed organism.
    Bridges the Government Engine to the multicellular body.
    """
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.compose_file = repo_root / "docker-compose.rh-ensemble.yml"
        self.student_map = {
            "Alpha": 11435,
            "Beta": 11436,
            "Gamma": 11437,
            "Delta": 11438,
            "Epsilon": 11439,
            "Zeta": 11440
        }

    def check_student_health(self, port: int) -> bool:
        """Checks if a student node is responsive."""
        try:
            resp = requests.get(f"http://localhost:{port}/api/tags", timeout=1)
            return resp.status_code == 200
        except Exception:
            return False

    def spawn_student(self, name: str) -> bool:
        """
        Performs 'Mitosis': Spawns a Docker student container.
        """
        if name not in self.student_map:
            print(f"[SUBSTRATE] ERROR: Unknown student {name}")
            return False

        print(f"[SUBSTRATE] Initiating Mitosis: Spawning student {name}...")
        try:
            # Run docker-compose up for the specific service
            # service name in yaml is likely lowercase (alpha, beta, etc.)
            service_name = name.lower()
            cmd = ["docker-compose", "-f", str(self.compose_file), "up", "-d", service_name]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Wait for student stabilization
            port = self.student_map[name]
            print(f"[SUBSTRATE] Waiting for student {name} stabilization on port {port}...")
            for _ in range(30):
                if self.check_student_health(port):
                    print(f"[SUBSTRATE] Student {name} MITOSIS COMPLETE.")
                    return True
                time.sleep(2)
            
            return False
        except Exception as e:
            print(f"[SUBSTRATE] Mitosis failed for {name}: {e}")
            return False

    def allocate_cell(self, required_mb: float) -> Optional[str]:
        """
        Finds a healthy student cell or spawns one if needed.
        Returns the Ollama URL for the cell.
        """
        # 1. Search for already spawned/active students
        for name, port in self.student_map.items():
            if self.check_student_health(port):
                return f"http://localhost:{port}"

        # 2. If no students active, spawn the first one (Alpha)
        if self.spawn_student("Alpha"):
            return f"http://localhost:11435"

        return None

if __name__ == "__main__":
    # Test substrate discovery
    mgr = SubstrateManager(Path("."))
    print("[SUBSTRATE] Auditing Student Cells...")
    cell = mgr.allocate_cell(5000)
    if cell:
        print(f"[SUBSTRATE] Cell allocated: {cell}")
    else:
        print("[SUBSTRATE] Allocation failed. Body unresponsive.")
