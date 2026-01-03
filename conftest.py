from __future__ import annotations

from datetime import datetime
from pathlib import Path
import gc
import shutil
from uuid import uuid4
import getpass
import os
import subprocess

import pytest


def pytest_configure(config) -> None:
    """
    Use a unique temp directory per run to avoid Windows file-lock collisions.
    Falls back to a per-run root if .pytest-temp is locked.
    """
    root = Path(config.rootpath)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def make_run_dir(base: Path, prefix: str) -> Path:
        for _ in range(5):
            run_id = uuid4().hex[:8]
            run_temp = base / f"{prefix}_{timestamp}_{run_id}"
            try:
                run_temp.mkdir(parents=True, exist_ok=False)
                return run_temp
            except PermissionError:
                continue
            except FileExistsError:
                continue
        raise PermissionError(f"Unable to create writable temp dir under {base}")

    root_temp = root / "pytest-temp"
    try:
        root_temp.mkdir(parents=True, exist_ok=True)
        run_temp = make_run_dir(root_temp, "run")
    except PermissionError:
        run_temp = make_run_dir(root, "pytest-run")

    config.option.basetemp = str(run_temp)

    if os.name == "nt":
        try:
            user = getpass.getuser()
            subprocess.run(
                ["icacls", str(run_temp), "/inheritance:e"],
                check=False,
                capture_output=True,
            )
            subprocess.run(
                ["icacls", str(run_temp), "/grant", f"{user}:(OI)(CI)F"],
                check=False,
                capture_output=True,
            )
        except Exception:
            pass

    try:
        import _pytest.pathlib as pytest_pathlib
        import _pytest.tmpdir as pytest_tmpdir
    except Exception:
        return

    original_cleanup = pytest_pathlib.cleanup_dead_symlinks

    def safe_cleanup(root: Path) -> None:
        try:
            original_cleanup(root)
        except PermissionError:
            print(f"[cleanup] Permission denied on {root}, skipping cleanup.")

    pytest_pathlib.cleanup_dead_symlinks = safe_cleanup
    pytest_tmpdir.cleanup_dead_symlinks = safe_cleanup


def pytest_sessionfinish(session, exitstatus) -> None:
    """
    Best-effort cleanup of older run directories without crashing on locks.
    """
    root = Path(session.config.rootpath)
    current = Path(session.config.option.basetemp)

    root_temp = root / "pytest-temp"
    if root_temp.exists():
        for path in root_temp.glob("run_*"):
            if path == current:
                continue
            if not path.is_dir():
                continue
            try:
                shutil.rmtree(path)
            except PermissionError:
                print(f"[cleanup] Locked temp dir, skipping: {path.name}")
            except Exception as exc:
                print(f"[cleanup] Failed to remove {path.name}: {exc}")

    for path in root.glob("pytest-run*"):
        if path == current:
            continue
        if not path.is_dir():
            continue
        try:
            shutil.rmtree(path)
        except PermissionError:
            print(f"[cleanup] Locked temp dir, skipping: {path.name}")
        except Exception as exc:
            print(f"[cleanup] Failed to remove {path.name}: {exc}")


@pytest.fixture(autouse=True)
def close_resources_on_teardown():
    """
    Encourage release of file handles between tests on Windows.
    """
    yield
    gc.collect()


@pytest.fixture
def tmp_path() -> Path:
    """
    Custom tmp_path fixture to avoid pytest tmpdir plugin on Windows.
    """
    base = Path.cwd() / "pytest-temp-user"
    base.mkdir(parents=True, exist_ok=True)
    path = base / uuid4().hex
    path.mkdir(exist_ok=True)
    try:
        yield path
    finally:
        try:
            shutil.rmtree(path)
        except PermissionError:
            print(f"[cleanup] Locked temp dir, skipping: {path}")
