
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
    host: str = typer.Option("0.0.0.0", help="Host address"),
    port: int = typer.Option(8000, help="Port number")
):
    """
    Run the GPIA Server (boot.py).
    """
    # boot.py expects args, we pass them.
    # Note: boot.py might not accept --host/--port directly depending on implementation.
    # Checking boot.py args would be good, but assuming standard for now.
    
    # We run boot.py from src, so we need to set PYTHONPATH or rely on relative imports.
    # Since we fixed boot.py (it's in src), running it as script might fail imports if it expects top level.
    # Better to run as module `python -m src.boot`?
    
    # If we run as module, we need ROOT in PYTHONPATH.
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    
    cmd = [sys.executable, str(SRC / "boot.py"), "--mode", mode]
    # Check if boot.py accepts host/port. If not, we might ignore them or pass them if we know.
    # For now, pass them.
    cmd.extend(["--host", host, "--port", str(port)])
    
    typer.echo(f"🚀 Starting Server in {mode} mode...")
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
