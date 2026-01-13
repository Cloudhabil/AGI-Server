import os
import sys
import time
import requests
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

class TensorRTClient:
    """
    Client for the Nuke Eater TensorRT-LLM Sidecar.
    Manages the lifecycle of the Python 3.10 inference server.
    """
    def __init__(self, 
                 vault_root: Optional[Path] = None,
                 port: int = 8008):
        self.root = vault_root or Path(os.getcwd()) / "models" / "nuke_eater"
        self.python_exe = self.root / "python_310" / "python.exe"
        self.server_script = self.root / "python_310" / "server.py"
        self.base_url = f"http://127.0.0.1:{port}"
        self.process: Optional[subprocess.Popen] = None

    def start_server(self):
        """Starts the Python 3.10 Sidecar in a background process."""
        if self.is_alive():
            print("[TRT-Client] Server already running.")
            return True

        if not self.python_exe.exists():
            print(f"[TRT-Client] Error: Sidecar Python not found at {self.python_exe}")
            return False

        print(f"[TRT-Client] Igniting Engine Room (Sidecar)...")
        # Ensure environment isolation
        env = os.environ.copy()
        env["PYTHONHOME"] = str(self.root / "python_310")
        
        self.process = subprocess.Popen(
            [str(self.python_exe), str(self.server_script)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0
        )

        # Wait for health check
        max_retries = 30
        for i in range(max_retries):
            if self.is_alive():
                print(f"[TRT-Client] Engine synchronized on {self.base_url}")
                return True
            time.sleep(1)
            print(f"  Waiting for ignition... ({i+1}/{max_retries})", end="\r")
        
        print("\n[TRT-Client] Timeout waiting for engine ignition.")
        return False

    def is_alive(self) -> bool:
        """Check if the sidecar server is responding."""
        try:
            resp = requests.get(f"{self.base_url}/docs", timeout=1)
            return resp.status_code == 200
        except:
            return False

    def query(self, prompt: str, max_tokens: int = 512, temperature: float = 0.1) -> str:
        """Sends a prompt to the TensorRT engine."""
        if not self.is_alive():
            if not self.start_server():
                return "[Error] Engine offline and failed to start."

        try:
            payload = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            resp = requests.post(f"{self.base_url}/generate", json=payload, timeout=120)
            if resp.status_code == 200:
                return resp.json().get("text", "")
            else:
                return f"[Error] Engine returned status {resp.status_code}: {resp.text}"
        except Exception as e:
            return f"[Error] Communication failure: {e}"

    def stop_server(self):
        """Gracefully shuts down the sidecar."""
        if self.process:
            print("[TRT-Client] Powering down engine room...")
            self.process.terminate()
            self.process.wait()
            self.process = None

if __name__ == "__main__":
    # Self-test
    client = TensorRTClient()
    if client.start_server():
        print("\nTest Prompt: 'Explain the concept of entropy in one sentence.'")
        result = client.query("Explain the concept of entropy in one sentence.")
        print(f"Result: {result}")
        # client.stop_server()
