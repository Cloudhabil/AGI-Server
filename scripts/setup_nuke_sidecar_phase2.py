import os
import shutil
import subprocess
import zipfile
import sys
from pathlib import Path

# Paths
ROOT = Path.cwd()
SOURCE_BASE = ROOT / "ChatWithRTX_Installer_8_25" / "ChatRTX" / "ChatRTX"
DEPENDENCIES_DIR = SOURCE_BASE / "dependencies"
VAULT = ROOT / "models" / "nuke_eater"
PYTHON_ZIP = SOURCE_BASE / "python-3.10.11-embed-amd64.zip"
GET_PIP = SOURCE_BASE / "get-pip.py"

# The Engine Wheel (Main Target)
TRT_LLM_WHEEL = VAULT / "tensorrt_llm-0.9.0-cp310-cp310-win_amd64.whl"

SIDECAR_DIR = VAULT / "python_310"
PYTHON_EXE = SIDECAR_DIR / "python.exe"

def run_sidecar_cmd(args, desc):
    print(f"[Sidecar] {desc}...")
    try:
        env = os.environ.copy()
        env["PYTHONHOME"] = str(SIDECAR_DIR)
        env["PYTHONPATH"] = str(SIDECAR_DIR / "Lib" / "site-packages")
        
        full_cmd = [str(PYTHON_EXE)] + args
        subprocess.run(full_cmd, cwd=SIDECAR_DIR, check=True, env=env)
        print(f"   -> Success.")
    except subprocess.CalledProcessError as e:
        print(f"   -> FAILED: {e}")

def setup_sidecar():
    print(f"=== Substrate Sidecar Setup (Phase 2: The Transplant) ===")
    
    # 1. Install Pre-requisite Wheels from Dependencies
    # We must install these FIRST to prevent pip from trying to build them.
    
    # Priority List (Install order matters)
    priority_wheels = [
        "torch-2.2.0+cu121-cp310-cp310-win_amd64.whl", # Core PyTorch
        "tensorrt_libs-9.3.0.post12.dev1-py2.py3-none-win_amd64.whl", # TRT Libs
        "tensorrt_bindings-9.3.0.post12.dev1-cp310-none-win_amd64.whl", # TRT Bindings
        "mpi4py-3.1.5-cp310-cp310-win_amd64.whl", # MPI
        "polygraphy-0.49.9-py2.py3-none-any.whl", 
        "ninja", # Usually needed for JIT
    ]
    
    print("Harvesting and Installing Donor Organs (Wheels)...")
    for wheel_name in priority_wheels:
        # Find partial match in dependencies
        matches = list(DEPENDENCIES_DIR.glob(f"*{wheel_name.split('-')[0]}*"))
        target = None
        for m in matches:
            if wheel_name in m.name:
                target = m
                break
        
        if target and target.exists():
            print(f"   -> Transplanting: {target.name}")
            run_sidecar_cmd(["-m", "pip", "install", str(target), "--no-deps"], f"Installing {target.name}")
        else:
            print(f"   -> [WARN] Could not find exact match for {wheel_name}, hoping for the best.")

    # 2. Install The Engine (TensorRT-LLM)
    # Now that libs are installed, this should link instead of build.
    if TRT_LLM_WHEEL.exists():
        run_sidecar_cmd(["-m", "pip", "install", str(TRT_LLM_WHEEL), "--no-index", "--find-links", str(DEPENDENCIES_DIR)], "Installing TensorRT-LLM Engine (Final Link)")
    else:
        print(f"[ERROR] TensorRT Wheel not found in vault!")

    print("\n=== Sidecar Ready ===")
    print(f"Interpreter: {PYTHON_EXE}")

if __name__ == "__main__":
    setup_sidecar()
