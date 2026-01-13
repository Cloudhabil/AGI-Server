
import sys
import subprocess
import os
import shutil
from pathlib import Path
try:
    import typer
except ImportError:
    print("Error: 'typer' is not installed. Please run 'pip install typer' or 'pip install .'")
    sys.exit(1)

app = typer.Typer(help="CLI AI Manager - Unified Entry Point")

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
TESTS = ROOT / "tests"

# Ensure src is in python path for subprocesses if needed
# But usually subprocesses calling python scripts handle their own path setup now.

@app.command()
def server(
    mode: str = typer.Option("Sovereign-Loop", help="Runtime mode (e.g. Sovereign-Loop, Api-Mode)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """
    Run the GPIA Server (boot.py).
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    
    cmd = [sys.executable, str(SRC / "boot.py"), "--mode", mode]
    if verbose:
        cmd.append("--verbose")
    
    typer.echo(f"Starting Server in {mode} mode...")
    subprocess.run(cmd, env=env)

@app.command()
def local(
    model: str = typer.Option("gpia-master:latest", help="Local model to use as primary brain"),
    mode: str = typer.Option("Sovereign-Loop", help="Runtime mode"),
    endpoint: str = typer.Option("http://localhost:11434", help="Ollama API endpoint"),
    npu_offload: str = typer.Option(None, "--npu-offload", help="Tasks to offload to NPU (comma-separated: embeddings,vision,audio,classification)"),
    vram_limit: str = typer.Option(None, "--vram-limit", help="Max VRAM usage (e.g., 10200MB, 10.2GB) - prevents DWM contention"),
    substrate_equilibrium: bool = typer.Option(False, "--substrate-equilibrium", "-se", help="Enable auto-tuned substrate balancing (recommended)")
):
    """
    Boot the ASI-OS using local intelligence only (Ollama).
    Automatically configures the environment for offline operation.

    SUBSTRATE EQUILIBRIUM MODE (--substrate-equilibrium):
    Balances load across GPU VRAM, System RAM, and Intel NPU to prevent
    the "PCIe traffic jam" when GPU spills into shared memory.

    Example (optimal for 12GB VRAM + Intel NPU):
        python manage.py local --npu-offload "embeddings,vision" --vram-limit 10200MB

    This leaves 1.7GB buffer for Windows DWM and routes embeddings/vision
    through the NPU's direct memory path, freeing the PCIe bus for LLM inference.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    env["OLLAMA_URL"] = f"{endpoint}/api/generate"
    env["GPIA_LOCAL_OVERRIDE"] = model
    env["USE_GOVERNMENT_ENGINE"] = "0"  # Bypass cloud-heavy logic

    # SPEED OPTIMIZATIONS for Instant Chat
    env["METABOLIC_MODE"] = "REFLEX_ONLY"  # Disable heavy crystallization cycles
    env["USE_NEURONIC_ROUTER"] = "0"       # Use fast routing, skip neural checks
    env["OLLAMA_KEEP_ALIVE"] = "-1"        # Keep model in VRAM (instant subsequent replies)

    # HEARTBEAT PROTOCOL (Adaptive)
    env["ENABLE_MASTER_PULSE"] = "1"
    env["PULSE_MODE"] = "ADAPTIVE"         # Enable Latency-Aware Recalibration
    env["PULSE_START_HRZ"] = "10.0"        # Resting rate (scales up/down from here)

    # =========================================================================
    # SUBSTRATE EQUILIBRIUM CONTROLS
    # =========================================================================

    # Auto-tune if substrate equilibrium requested
    if substrate_equilibrium:
        # HARDWARE SOVEREIGNTY: Set the master flag
        env["SUBSTRATE_EQUILIBRIUM"] = "1"

        # Apply calibrated defaults (9750MB cliff, not 10200MB)
        npu_offload = npu_offload or "embeddings,vision,audio"
        vram_limit = vram_limit or "9750MB"  # CLIFF - calibrated to DWM + safety buffer
        typer.echo("[SUBSTRATE] HARDWARE SOVEREIGNTY ENABLED")
        typer.echo("[SUBSTRATE] VRAM cliff: 9750MB | NPU locked for embeddings")

    # NPU Offload Configuration
    if npu_offload:
        tasks = [t.strip().lower() for t in npu_offload.split(",")]
        env["NPU_OFFLOAD_TASKS"] = ",".join(tasks)

        # Enable specific NPU routing
        if "embeddings" in tasks:
            env["USE_NPU_EMBEDDINGS"] = "1"
            env["EMBEDDING_DEVICE"] = "NPU"
        if "vision" in tasks:
            env["USE_NPU_VISION"] = "1"
        if "audio" in tasks:
            env["USE_NPU_AUDIO"] = "1"
        if "classification" in tasks:
            env["USE_NPU_CLASSIFIER"] = "1"

        typer.echo(f"[SUBSTRATE] NPU offload: {tasks}")

    # VRAM Limit Configuration
    if vram_limit:
        # Parse limit (support MB and GB notation)
        limit_str = vram_limit.upper().strip()
        if limit_str.endswith("GB"):
            limit_mb = int(float(limit_str[:-2]) * 1024)
        elif limit_str.endswith("MB"):
            limit_mb = int(limit_str[:-2])
        else:
            limit_mb = int(limit_str)  # Assume MB

        env["VRAM_LIMIT_MB"] = str(limit_mb)
        env["OLLAMA_GPU_MEMORY"] = str(limit_mb)  # Ollama-specific
        env["CUDA_VISIBLE_MEMORY_LIMIT"] = f"{limit_mb}MiB"

        # Enable metabolic enforcement at the limit
        env["METABOLIC_EXPANSION_MIN_VRAM_MB"] = str(max(0, limit_mb - 500))
        env["METABOLIC_CRYSTALLIZATION_MIN_VRAM_MB"] = str(max(0, limit_mb - 1000))

        typer.echo(f"[SUBSTRATE] VRAM cap: {limit_mb}MB (prevents DWM contention)")
    else:
        # Default: Disable VRAM Throttling (Let the user crash it if they want speed)
        env["METABOLIC_EXPANSION_MIN_VRAM_MB"] = "0"
        env["METABOLIC_CRYSTALLIZATION_MIN_VRAM_MB"] = "0"

    env["GPIA_ENFORCE_GOVERNMENT"] = "0"

    # =========================================================================
    # BOOT SEQUENCE OUTPUT
    # =========================================================================
    typer.echo("------------------------------------------------------------")
    if substrate_equilibrium or npu_offload or vram_limit:
        typer.echo("ASI-OS LOCAL BOOT (SUBSTRATE EQUILIBRIUM MODE)")
        typer.echo("")
        typer.echo("  Tier 1: VRAM      → LLM Weights + KV Cache")
        if npu_offload:
            typer.echo(f"  Tier 3: NPU       → {npu_offload}")
        typer.echo("  Tier 2: DDR5 RAM  → Context Overflow (PCIe-bound)")
        typer.echo("  Tier 4: NVMe      → Long-term Memory")
    else:
        typer.echo("ASI-OS LOCAL BOOT SEQUENCE (UNLEASHED)")
    typer.echo("")
    typer.echo(f"  Primary Brain: {model}")
    typer.echo(f"  Endpoint:      {endpoint}")
    if vram_limit:
        typer.echo(f"  VRAM Limit:    {vram_limit}")
    typer.echo("------------------------------------------------------------")

    cmd = [sys.executable, str(SRC / "boot.py"), "--mode", mode]
    subprocess.run(cmd, env=env)

@app.command()
def learn(
    duration: int = typer.Option(180, help="Duration in seconds"),
    cycles: int = typer.Option(3, help="Number of cycles")
):
    """
    Start an autonomous learning session (Professor & Alpha).
    """
    cmd = [sys.executable, str(SCRIPTS / "start_autonomous_learning.py")]
    
    env = os.environ.copy()
    env["SESSION_DURATION"] = str(duration)
    env["LEARNING_CYCLES"] = str(cycles)
    # Ensure src is available to the script
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    
    typer.echo(f"🎓 Starting Learning Session ({duration}s, {cycles} cycles)...")
    subprocess.run(cmd, env=env)

@app.command()
def test(
    marker: str = typer.Option(None, "--marker", "-m", help="Run tests with specific marker"),
    keyword: str = typer.Option(None, "--keyword", "-k", help="Run tests matching keyword"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """
    Run the test suite.
    """
    cmd = [sys.executable, "-m", "pytest", str(TESTS)]
    if marker:
        cmd.extend(["-m", marker])
    if keyword:
        cmd.extend(["-k", keyword])
    if verbose:
        cmd.append("-v")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    
    typer.echo("🧪 Running Tests...")
    subprocess.run(cmd, env=env)

@app.command()
def substrate():
    """
    Show current Substrate Equilibrium status.

    Displays the hardware topology and which silicon is handling which tasks:
    - Tier 1: GPU VRAM (LLM weights, ~350 GB/s)
    - Tier 2: DDR5 RAM (context overflow, PCIe-bound ~26 GB/s)
    - Tier 3: Intel NPU (embeddings/vision, direct memory path)
    - Tier 4: NVMe SSD (long-term memory, high latency)
    """
    typer.echo("------------------------------------------------------------")
    typer.echo("SUBSTRATE EQUILIBRIUM STATUS")
    typer.echo("------------------------------------------------------------")

    # Add src to path for imports
    import sys
    sys.path.insert(0, str(SRC))

    try:
        from core.npu_utils import get_substrate_status, has_npu, get_npu_info

        status = get_substrate_status()

        typer.echo(f"\n[NPU Hardware]")
        typer.echo(f"  Available:    {status['npu_available']}")
        if status['npu_info']:
            typer.echo(f"  Device:       {status['npu_info'].get('name', 'Unknown')}")

        typer.echo(f"\n[Equilibrium Mode]")
        typer.echo(f"  Active:       {status['equilibrium_active']}")
        typer.echo(f"  VRAM Limit:   {status['vram_limit_mb']}MB" if status['vram_limit_mb'] else "  VRAM Limit:   None (unlimited)")
        typer.echo(f"  NPU Tasks:    {status['offload_tasks'] or 'None'}")

        if status['embedder']:
            typer.echo(f"\n[Embedding Backend]")
            typer.echo(f"  Backend:      {status['embedder'].get('backend', 'Unknown')}")
            typer.echo(f"  Device:       {status['embedder'].get('device', 'Unknown')}")

        typer.echo(f"\n[Substrate Tiers]")
        typer.echo("  Tier 1: VRAM      → LLM Weights + KV Cache (~350 GB/s)")
        typer.echo("  Tier 2: DDR5 RAM  → Context Overflow (PCIe-bound ~26 GB/s)")
        if status['npu_available']:
            typer.echo("  Tier 3: Intel NPU → Embeddings/Vision (direct memory path)")
        typer.echo("  Tier 4: NVMe SSD  → Long-term Memory (high latency)")

        typer.echo(f"\n[Recommended Command]")
        if not status['equilibrium_active']:
            typer.echo('  python manage.py local --substrate-equilibrium')
            typer.echo('  OR: python manage.py local --npu-offload "embeddings,vision" --vram-limit 10200MB')

    except Exception as e:
        typer.echo(f"Error getting substrate status: {e}")
        import traceback
        traceback.print_exc()

    typer.echo("------------------------------------------------------------")


@app.command()
def clean():
    """
    Clean up __pycache__, .pytest_cache, and temporary artifacts.
    """
    typer.echo("🧹 Cleaning up...")
    
    dirs_to_remove = ["__pycache__", ".pytest_cache", ".mypy_cache", "build", "dist", ".egg-info"]
    
    for root, dirs, files in os.walk(ROOT):
        for d in dirs:
            if d in dirs_to_remove or d.endswith(".egg-info"):
                path = Path(root) / d
                typer.echo(f"Removing {path}")
                shutil.rmtree(path, ignore_errors=True)
                
    typer.echo("Done.")

if __name__ == "__main__":
    app()
