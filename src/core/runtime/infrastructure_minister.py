"""
Minister of Infrastructure - Substrate Self-Healing
===================================================
Responsible for monitoring and restarting the inference server (Ollama).
Ensures the system's 'Vital Spark' is always active.
"""

import subprocess
import time
import requests
import os
import shutil
from pathlib import Path

class InfrastructureMinister:
    """
    The 'Heart Surgeon' of the substrate.
    Restarts the Ollama process if health checks fail.
    """
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.process = None

    def check_vital_spark(self) -> bool:
        """Heartbeat check to the inference server."""
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    def jumpstart_server(self):
        """Attempts to start the Ollama server process."""
        print("[INFRASTRUCTURE] Vital Spark lost. Attempting Substrate Jumpstart...")
        
        # 1. Check if ollama is in PATH
        ollama_bin = shutil.which("ollama")
        if not ollama_bin:
            # Try common Windows path
            user_home = os.environ.get("USERPROFILE", "")
            ollama_bin = os.path.join(user_home, "AppData", "Local", "Programs", "Ollama", "ollama.exe")
            if not os.path.exists(ollama_bin):
                print("[INFRASTRUCTURE] ERROR: Ollama binary not found. Self-healing impossible.")
                return False

        # 2. Launch background process
        try:
            # We use subprocess.Popen to let it run independently
            print(f"[INFRASTRUCTURE] Launching {ollama_bin} serve...")
            env = os.environ.copy()
            # Ensure OLLAMA_HOST is set for local access
            env["OLLAMA_HOST"] = "127.0.0.1:11434"
            
            # Start process without window
            self.process = subprocess.Popen(
                [ollama_bin, "serve"],
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # 3. Wait for warmup
            print("[INFRASTRUCTURE] Waiting for spark stabilization (10s)...")
            for _ in range(10):
                if self.check_vital_spark():
                    print("[INFRASTRUCTURE] SUBSTRATE RESTORED. Spark detected.")
                    return True
                time.sleep(1)
                
            return False
        except Exception as e:
            print(f"[INFRASTRUCTURE] Jumpstart failed: {e}")
            return False

    def heal_substrate(self):
        """Mandatory healing cycle."""
        if not self.check_vital_spark():
            return self.jumpstart_server()
        return True

if __name__ == "__main__":
    # Test/Demo script
    infra = InfrastructureMinister()
    print(f"Substrate Status: {'ACTIVE' if infra.check_vital_spark() else 'DOWN'}")
    if not infra.check_vital_spark():
        success = infra.jumpstart_server()
        print(f"Jumpstart Success: {success}")
