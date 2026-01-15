import os
import subprocess
import sys
from pathlib import Path

# Paths
ROOT = Path.cwd()
VAULT = ROOT / "models" / "nuke_eater"
SIDECAR_PYTHON = VAULT / "python_310" / "python.exe"
BUILD_TOOL = VAULT / "python_310" / "Scripts" / "trtllm-build.exe"

CHECKPOINT_DIR = VAULT / "mistral_int4_awq" / "model_checkpoints"
ENGINE_DIR = VAULT / "mistral_int4_awq" / "engine"

def build_engine():
    print(f"=== Nuke Eater Engine Synthesis ===")
    
    if not ENGINE_DIR.exists():
        ENGINE_DIR.mkdir(parents=True, exist_ok=True)

    # Note: trtllm-build.exe is a wrapper. We can also call the module directly via python.
    # Using python -m tensorrt_llm.commands.build is often more reliable in isolated envs.
    
    cmd = [
        str(SIDECAR_PYTHON), "-m", "tensorrt_llm.commands.build",
        "--checkpoint_dir", str(CHECKPOINT_DIR),
        "--output_dir", str(ENGINE_DIR),
        "--gpt_attention_plugin", "float16",
        "--gemm_plugin", "float16",
        "--max_batch_size", "1",
        "--max_input_len", "7168",
        "--max_output_len", "1024",
        "--context_fmha", "enable"
    ]

    print(f"Building Engine (This may take several minutes)...")
    print(f"Command: {' '.join(cmd)}")
    
    # Ensure DLL paths are set for the build tool too
    env = os.environ.copy()
    site_packages = str(VAULT / "python_310" / "Lib" / "site-packages")
    trt_libs = os.path.join(site_packages, "tensorrt_libs")
    env["PATH"] = trt_libs + os.pathsep + env.get("PATH", "")
    
    try:
        # Use a longer timeout for the build process
        process = subprocess.run(cmd, env=env, check=True)
        print("\n[OK] Engine synthesis complete.")
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Build failed with exit code {e.returncode}")
    except Exception as e:
        print(f"\n[ERROR] Unexpected failure: {e}")

if __name__ == "__main__":
    build_engine()
