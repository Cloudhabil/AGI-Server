import os
import shutil
import subprocess
import zipfile
import sys
from pathlib import Path

# Paths
ROOT = Path.cwd()
SOURCE_BASE = ROOT / "ChatWithRTX_Installer_8_25" / "ChatRTX" / "ChatRTX"
VAULT = ROOT / "models" / "nuke_eater"
PYTHON_ZIP = SOURCE_BASE / "python-3.10.11-embed-amd64.zip"
GET_PIP = SOURCE_BASE / "get-pip.py"
WHEEL = VAULT / "tensorrt_llm-0.9.0-cp310-cp310-win_amd64.whl"

SIDECAR_DIR = VAULT / "python_310"
PYTHON_EXE = SIDECAR_DIR / "python.exe"

def run_sidecar_cmd(args, desc):
    print(f"[Sidecar] {desc}...")
    try:
        # Pass environment with minimal isolation
        env = os.environ.copy()
        # Ensure we don't bleed into global python
        env["PYTHONHOME"] = str(SIDECAR_DIR)
        env["PYTHONPATH"] = str(SIDECAR_DIR / "Lib" / "site-packages")
        
        full_cmd = [str(PYTHON_EXE)] + args
        subprocess.run(full_cmd, cwd=SIDECAR_DIR, check=True, env=env)
        print(f"   -> Success.")
    except subprocess.CalledProcessError as e:
        print(f"   -> FAILED: {e}")
        # Don't exit, try to continue as some pip warnings are non-fatal

def setup_sidecar():
    print(f"=== Substrate Sidecar Setup (Python 3.10) ===")
    
    if not PYTHON_ZIP.exists():
        print(f"Error: Python 3.10 zip not found at {PYTHON_ZIP}")
        return

    # 1. Extract Python
    if not SIDECAR_DIR.exists():
        print(f"Extracting Python 3.10 to {SIDECAR_DIR}...")
        with zipfile.ZipFile(PYTHON_ZIP, 'r') as zip_ref:
            zip_ref.extractall(SIDECAR_DIR)
        
        # 2. Fix Embedded Python (Enable site-packages)
        # By default embedded python ignores site-packages. We must edit the ._pth file.
        pth_file = SIDECAR_DIR / "python310._pth"
        if pth_file.exists():
            print("Unlocking site-packages in ._pth file...")
            content = pth_file.read_text()
            # Uncomment 'import site'
            content = content.replace("#import site", "import site")
            pth_file.write_text(content)
    else:
        print(f"Sidecar Python already exists.")

    # 3. Install PIP
    # We need get-pip.py. If not in source, we can't easily proceed.
    if GET_PIP.exists():
        shutil.copy2(GET_PIP, SIDECAR_DIR / "get-pip.py")
        run_sidecar_cmd(["get-pip.py", "--no-warn-script-location"], "Installing PIP")
    else:
        print("[WARN] get-pip.py not found in source. Assuming PIP installed or manually handled.")

    # 4. Install Dependencies
    # Install standard reqs
    run_sidecar_cmd(["-m", "pip", "install", "numpy", "requests", "fastapi", "uvicorn"], "Installing Bridge Dependencies")

    # 5. Install The Engine (TensorRT-LLM)
    if WHEEL.exists():
        run_sidecar_cmd(["-m", "pip", "install", str(WHEEL)], "Installing TensorRT-LLM Engine")
    else:
        print(f"[ERROR] TensorRT Wheel not found in vault!")

    print("\n=== Sidecar Ready ===")
    print(f"Interpreter: {PYTHON_EXE}")
    print("You can now run the Bridge Server using this interpreter.")

if __name__ == "__main__":
    setup_sidecar()
