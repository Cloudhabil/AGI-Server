import os
import shutil
import zipfile
from pathlib import Path

# Paths
ROOT = Path.cwd()
SOURCE_BASE = ROOT / "ChatWithRTX_Installer_8_25" / "ChatRTX" / "ChatRTX"
TARGET_VAULT = ROOT / "models" / "nuke_eater"

# Targets
TARGET_WEIGHTS = SOURCE_BASE / "mistral_7b_AWQ_int4_chat"
TARGET_WHEEL = SOURCE_BASE / "tensorrt_llm-0.9.0-cp310-cp310-win_amd64.whl"
TARGET_RAG_ZIP = SOURCE_BASE / "trt-llm-rag-windows-ChatRTX_0.4.0.zip"

def cannibalize():
    print(f"=== Operation NUKE EATER ===")
    print(f"Source: {SOURCE_BASE}")
    print(f"Vault:  {TARGET_VAULT}")
    
    if not SOURCE_BASE.exists():
        print(f"Error: Source directory not found at {SOURCE_BASE}")
        return

    # 1. Create Vault
    if not TARGET_VAULT.exists():
        print(f"Creating vault: {TARGET_VAULT}")
        TARGET_VAULT.mkdir(parents=True, exist_ok=True)

    # 2. Extract Weights (The Gold)
    dest_weights = TARGET_VAULT / "mistral_int4_awq"
    if TARGET_WEIGHTS.exists():
        if dest_weights.exists():
            print(f"[SKIP] Weights already secured at {dest_weights}")
        else:
            print(f"Cannibalizing Weights: {TARGET_WEIGHTS.name}...")
            shutil.copytree(TARGET_WEIGHTS, dest_weights)
            print(f"[OK] Weights secured.")
    else:
        print(f"[MISSING] Weights folder not found: {TARGET_WEIGHTS}")

    # 3. Extract Engine Wheel (The Ferrari Engine)
    if TARGET_WHEEL.exists():
        dest_wheel = TARGET_VAULT / TARGET_WHEEL.name
        if dest_wheel.exists():
            print(f"[SKIP] Engine Wheel already secured.")
        else:
            print(f"Cannibalizing Engine: {TARGET_WHEEL.name}...")
            shutil.copy2(TARGET_WHEEL, dest_wheel)
            print(f"[OK] Engine secured.")
    else:
        print(f"[MISSING] TensorRT Wheel not found.")

    # 4. Extract Glue Code (The Brains)
    if TARGET_RAG_ZIP.exists():
        glue_dir = TARGET_VAULT / "glue_code"
        print(f"Extracting Glue Code from RAG Zip...")
        try:
            with zipfile.ZipFile(TARGET_RAG_ZIP, 'r') as zip_ref:
                # We specifically want the python engine logic
                zip_ref.extractall(glue_dir)
            print(f"[OK] Glue code extracted to {glue_dir}")
            
            # Locate the backend.py for instant verification
            backend_path = glue_dir / "trt-llm-rag-windows-ChatRTX_0.4.0" / "ChatRTXUI" / "engine" / "backend.py"
            if backend_path.exists():
                print(f"    -> Found Logic Core: {backend_path}")
        except Exception as e:
            print(f"[ERROR] Failed to unzip RAG glue: {e}")
    else:
        print(f"[MISSING] RAG Zip not found.")

    print("\n=== Operation Complete ===")
    print(f"Assets secure in {TARGET_VAULT}")

if __name__ == "__main__":
    cannibalize()
