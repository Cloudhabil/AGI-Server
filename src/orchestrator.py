import os
import subprocess
import time
import yaml
import typer
import requests
import atexit
import logging
import secrets
from pathlib import Path
from typing import List
from admin_policy import evaluate_ceo_decision

app = typer.Typer()
profile_app = typer.Typer()
app.add_typer(profile_app, name="profile")
ROOT = Path(__file__).parent
try:
    with open(ROOT / "configs" / "agents.yaml", encoding="utf-8") as f:
        CONFIG_AGENTS = yaml.safe_load(f)
except FileNotFoundError as exc:
    raise RuntimeError("Missing agents.yaml configuration") from exc
try:
    with open(ROOT / "configs" / "models.yaml", encoding="utf-8") as f:
        CONFIG_MODELS = yaml.safe_load(f)
except FileNotFoundError as exc:
    raise RuntimeError("Missing models.yaml configuration") from exc

processes: List[subprocess.Popen[bytes]] = []


def _ensure_tokens() -> None:
    """Generate missing shared secrets for local boot."""
    if not os.environ.get("BUS_TOKEN"):
        os.environ["BUS_TOKEN"] = secrets.token_hex(32)
        logging.info("BUS_TOKEN was missing; generated a new one for this session.")
    if not os.environ.get("AGENT_SHARED_SECRET"):
        os.environ["AGENT_SHARED_SECRET"] = secrets.token_hex(32)
        logging.info("AGENT_SHARED_SECRET was missing; generated a new one for this session.")


def _shutdown():
    """Terminate spawned subprocesses on exit."""
    for p in processes:
        if p.poll() is None:
            p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()


atexit.register(_shutdown)


def spawn_bus():
    _ensure_tokens()
    try:
        p = subprocess.Popen(["python", "bus_server.py"], shell=False)
    except OSError as exc:
        raise RuntimeError("Failed to start bus server") from exc
    processes.append(p)
    os.environ["BUS_URL"] = "http://127.0.0.1:7088"
    _wait_health("http://127.0.0.1:7088/health")


def spawn_stripe():
    _ensure_tokens()
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT)
        p = subprocess.Popen(
            ["python", "server/stripe_server.py"],
            cwd=ROOT,
            env=env,
            shell=False,
        )
    except OSError as exc:
        raise RuntimeError("Failed to start stripe server") from exc
    processes.append(p)
    _wait_health("http://127.0.0.1:7077/health")


def spawn_agent(role: str, info: dict):
    _ensure_tokens()
    model_cfg = CONFIG_MODELS["models"][info["model"]]
    env = os.environ.copy()
    env.update(
        {
            "ROLE": role,
            "PORT": str(info["port"]),
            "PROMPT_FILE": str(info["prompt"]),
            "MODEL_KIND": model_cfg["kind"],
            "MODEL_ENDPOINT": model_cfg["endpoint"],
            "MODEL_NAME": model_cfg["model"],
            "BUS_URL": os.environ.get("BUS_URL", ""),
        }
    )
    try:
        p = subprocess.Popen(["python", "agent_server.py"], env=env, shell=False)
    except OSError as exc:
        raise RuntimeError(f"Failed to start agent {role}") from exc
    processes.append(p)
    _wait_health(f"http://127.0.0.1:{info['port']}/health")
    requests.post(f"http://127.0.0.1:{info['port']}/wake")


def _wait_health(
    url: str,
    retries: int = 20,
    backoff: float = 1.5,
    initial_delay: float = 1.0,
):
    """Poll a health endpoint until it responds or retries expire.

    Args:
        url: Health check URL.
        retries: Number of attempts before failing.
        backoff: Multiplier applied to the delay after each failed attempt.
        initial_delay: Initial sleep interval between attempts.
    """

    delay = initial_delay
    last_exc: Exception | None = None
    for _ in range(retries):
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                return
        except Exception as exc:
            last_exc = exc
        time.sleep(delay)
        delay *= backoff
    logging.error(
        "Service %s not healthy after %d retries. Last error: %s",
        url,
        retries,
        last_exc,
    )
    raise RuntimeError(f"service {url} not healthy: {last_exc}") from last_exc


def route(sender: str, target: str, text: str):
    bus = os.environ.get("BUS_URL", "http://127.0.0.1:7088")
    requests.post(
        f"{bus}/publish", json={"topic": target, "data": {"sender": sender, "text": text}}
    )


def check_ceo(decision_summary: str):
    verdict = evaluate_ceo_decision(decision_summary)
    if verdict == "harmful":
        route("admin", "CHRO", decision_summary)
        route("admin", "COO", decision_summary)
    return verdict


@app.command()
def boot():
    spawn_bus()
    spawn_stripe()
    for role in CONFIG_AGENTS["admin"]["wake_order"]:
        spawn_agent(role, CONFIG_AGENTS["agents"][role])
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        pass


@app.command()
def shell(
    minimal: bool = typer.Option(False, "--minimal", help="Launch minimal workspace interface"),
):
    if minimal:
        from ui.workspace_minimal import main as ui_main
    else:
        from admin_tui import main as ui_main

    ui_main(route, check_ceo)


@profile_app.command("pixel-edit")
def pixel_edit(user_id: str, size: int = 32):
    """Open pixel avatar editor for the given user."""
    from ui.pixel_avatar import edit_avatar

    edit_avatar(user_id, size)


if __name__ == "__main__":
    app()
