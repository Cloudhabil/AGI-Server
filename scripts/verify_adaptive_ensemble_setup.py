#!/usr/bin/env python3
"""
Verification script for RH Adaptive Ensemble setup.

Checks that all components are properly installed and wired before deployment.

Usage:
    python scripts/verify_adaptive_ensemble_setup.py
"""

import sys
import os
from pathlib import Path
import subprocess
import time

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

def check_section(title: str):
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def check_mark(condition: bool, message: str) -> bool:
    """Print check result."""
    status = "✓" if condition else "✗"
    print(f"  [{status}] {message}")
    return condition

def main():
    """Run all verification checks."""
    all_passed = True

    check_section("1. FILE INTEGRITY CHECKS")

    # Check core files exist
    files_to_check = [
        ("scripts/finetune_rh_models.py", "Fine-tuning script"),
        ("core/adaptive_student_scheduler.py", "Adaptive scheduler"),
        ("start_rh_adaptive_ensemble.py", "Ensemble orchestrator"),
        ("RH_ADAPTIVE_ENSEMBLE_GUIDE.md", "User guide"),
        ("ADAPTIVE_ENSEMBLE_IMPLEMENTATION.md", "Implementation doc"),
        ("DEPLOYMENT_CHECKLIST.md", "Deployment guide"),
        ("QUICK_START.md", "Quick start guide"),
    ]

    for file_path, description in files_to_check:
        full_path = REPO_ROOT / file_path
        exists = full_path.exists()
        all_passed &= check_mark(exists, f"{description}: {file_path}")
        if exists:
            size_kb = full_path.stat().st_size / 1024
            print(f"      └─ Size: {size_kb:.1f} KB")

    check_section("2. PYTHON IMPORTS & DEPENDENCIES")

    # Check standard library imports
    try:
        import sqlite3
        import json
        import time
        from pathlib import Path
        from dataclasses import dataclass
        from enum import Enum
        import subprocess
        all_passed &= check_mark(True, "Standard library imports")
    except ImportError as e:
        all_passed &= check_mark(False, f"Standard library imports: {e}")

    # Try importing our modules
    try:
        from core.adaptive_student_scheduler import AdaptiveStudentScheduler, get_adaptive_scheduler
        all_passed &= check_mark(True, "AdaptiveStudentScheduler imports")
    except ImportError as e:
        all_passed &= check_mark(False, f"AdaptiveStudentScheduler: {e}")

    try:
        from core.kernel.budget_service import get_budget_service
        all_passed &= check_mark(True, "BudgetService imports")
    except ImportError as e:
        all_passed &= check_mark(False, f"BudgetService: {e}")

    try:
        from agents.agent_utils import log_event
        all_passed &= check_mark(True, "AgentUtils imports")
    except ImportError as e:
        all_passed &= check_mark(False, f"AgentUtils: {e}")

    check_section("3. OLLAMA & MODELS")

    # Check Ollama is accessible
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            all_passed &= check_mark(True, "Ollama service accessible")

            # Count models
            models = [line for line in result.stdout.split('\n') if line.strip()]
            all_passed &= check_mark(len(models) > 1, f"Models available: {len(models)} models found")

            # Check for gpia- models
            gpia_models = [m for m in result.stdout.split('\n') if 'gpia-' in m.lower()]
            all_passed &= check_mark(
                len(gpia_models) >= 2,
                f"GPIA models available: {len(gpia_models)} found"
            )
            if gpia_models:
                for model in gpia_models[:3]:  # Show first 3
                    print(f"      └─ {model.split()[0] if model else 'unknown'}")

            # Check for fine-tuned RH models
            rh_models = [m for m in result.stdout.split('\n') if 'rh-' in m.lower()]
            if rh_models:
                all_passed &= check_mark(True, f"Fine-tuned RH models found: {len(rh_models)} models")
                for model in rh_models:
                    print(f"      └─ {model.split()[0] if model else 'unknown'}")
            else:
                all_passed &= check_mark(False, "Fine-tuned RH models not found (not yet created)")
                print(f"      └─ Run: python scripts/finetune_rh_models.py")
        else:
            all_passed &= check_mark(False, f"Ollama service error: {result.stderr[:100]}")
    except FileNotFoundError:
        all_passed &= check_mark(False, "Ollama not found in PATH")
        print(f"      └─ Install from: https://ollama.ai")
    except subprocess.TimeoutExpired:
        all_passed &= check_mark(False, "Ollama service timeout (may be starting up)")
    except Exception as e:
        all_passed &= check_mark(False, f"Ollama check failed: {str(e)[:100]}")

    check_section("4. DIRECTORY STRUCTURE")

    dirs_to_check = [
        ("agents/sessions", "Sessions directory"),
        ("scheduler_history", "Scheduler history (will be created on first run)"),
        ("core/kernel", "Kernel services directory"),
    ]

    for dir_path, description in dirs_to_check:
        full_path = REPO_ROOT / dir_path
        exists = full_path.exists()
        if "scheduler_history" in dir_path:
            all_passed &= check_mark(True, f"{description} (will auto-create)")
        else:
            all_passed &= check_mark(exists, f"{description}: {dir_path}")

    check_section("5. CONFIGURATION FILES")

    config_files = [
        ("configs/rh_ensemble_models.yaml", "RH Ensemble configuration"),
        (".env.local", "Environment configuration"),
    ]

    for file_path, description in config_files:
        full_path = REPO_ROOT / file_path
        exists = full_path.exists()
        if ".env.local" in file_path and not exists:
            check_mark(True, f"{description} (optional, will use defaults)")
        else:
            all_passed &= check_mark(exists, f"{description}: {file_path}")

    check_section("6. SYSTEM HARDWARE CHECK")

    try:
        import psutil

        # CPU
        cpu_count = psutil.cpu_count(logical=False)
        cpu_percent = psutil.cpu_percent(interval=0.1)
        check_mark(cpu_count >= 4, f"CPU cores: {cpu_count} cores (needs 4+)")
        check_mark(cpu_percent < 90, f"CPU load: {cpu_percent:.1f}% (should be <90%)")

        # RAM
        ram = psutil.virtual_memory()
        ram_gb = ram.total / (1024**3)
        ram_available_gb = ram.available / (1024**3)
        check_mark(ram_gb >= 16, f"Total RAM: {ram_gb:.1f} GB (needs 16+)")
        check_mark(ram.percent < 90, f"RAM usage: {ram.percent:.1f}% (should be <90%)")

        # Disk
        disk = psutil.disk_usage('/')
        disk_free_gb = disk.free / (1024**3)
        check_mark(disk_free_gb >= 50, f"Disk free: {disk_free_gb:.1f} GB (needs 50+)")

        # GPU (VRAM)
        try:
            result = subprocess.run(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,nounits"],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                vram_mb = int(result.stdout.strip())
                vram_gb = vram_mb / 1024
                check_mark(vram_gb >= 10, f"GPU VRAM: {vram_gb:.1f} GB (needs 10+)")
            else:
                print(f"  [!] GPU check failed (nvidia-smi not available)")
        except Exception as e:
            print(f"  [!] GPU check skipped ({type(e).__name__})")

    except ImportError:
        print(f"  [!] psutil not installed - skipping hardware checks")
        print(f"      Install: pip install psutil")

    check_section("7. ORCHESTRATOR STARTUP TEST")

    # Try importing and initializing the orchestrator
    try:
        # Create a test directory
        test_dir = REPO_ROOT / "agents" / "sessions" / "verify_test"
        test_dir.mkdir(parents=True, exist_ok=True)

        # Try importing key classes
        from start_rh_adaptive_ensemble import RHAdaptiveEnsemble
        from core.adaptive_student_scheduler import get_adaptive_scheduler
        from core.kernel.budget_service import get_budget_service

        # Try initializing components
        scheduler = get_adaptive_scheduler(test_dir)
        check_mark(True, "AdaptiveStudentScheduler initialized")

        budget_service = get_budget_service()
        check_mark(True, "BudgetService initialized")

        # Check scheduler database
        db_path = test_dir / "scheduler_history" / "student_profiles.db"
        check_mark(db_path.exists(), f"Scheduler database created: {db_path.name}")

        # Verify students are recognized
        students = list(scheduler.STUDENTS.keys())
        check_mark(len(students) == 6, f"All 6 students recognized: {', '.join(students)}")

    except Exception as e:
        all_passed &= check_mark(False, f"Orchestrator test: {str(e)[:100]}")
        import traceback
        traceback.print_exc()

    check_section("8. SUMMARY")

    if all_passed:
        print("  ✓ ALL CHECKS PASSED - System ready for deployment!")
        print("\n  Next steps:")
        print("    1. python scripts/finetune_rh_models.py")
        print("    2. python start_rh_adaptive_ensemble.py --duration 5 --session test")
        print("    3. See QUICK_START.md for full deployment steps\n")
        return 0
    else:
        print("  ✗ SOME CHECKS FAILED - Review errors above")
        print("\n  Failed components:")
        print("    - Check file paths are correct")
        print("    - Verify Ollama is running: ollama serve")
        print("    - Check Python imports: python -c 'import core.adaptive_student_scheduler'")
        print("    - See DEPLOYMENT_CHECKLIST.md for troubleshooting\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
