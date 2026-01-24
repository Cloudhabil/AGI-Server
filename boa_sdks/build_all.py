#!/usr/bin/env python3
"""
BOA SDKs - Build All APKs
Builds all 4 Brahim Onion Agent SDKs as standalone executables
"""

import os
import subprocess
import sys
import shutil

SDKS = [
    ("egyptian_fractions", "boa-egyptian-fractions", 5001),
    ("sat_solver", "boa-sat-solver", 5002),
    ("fluid_dynamics", "boa-fluid-dynamics", 5003),
    ("titan_explorer", "boa-titan-explorer", 5004),
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")


def build_sdk(sdk_dir: str, output_name: str, port: int) -> bool:
    """Build a single SDK."""
    print(f"\n{'='*60}")
    print(f"Building: {output_name}")
    print(f"{'='*60}")

    sdk_path = os.path.join(BASE_DIR, sdk_dir)
    main_path = os.path.join(sdk_path, "main.py")

    if not os.path.exists(main_path):
        print(f"ERROR: {main_path} not found")
        return False

    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", output_name,
        "--distpath", DIST_DIR,
        "--workpath", os.path.join(BASE_DIR, "build", sdk_dir),
        "--specpath", os.path.join(BASE_DIR, "build"),
        "--add-data", f"{os.path.join(sdk_path, 'src')}:src",
        "--hidden-import", "flask",
        "--hidden-import", "numpy",
        main_path
    ]

    try:
        subprocess.run(cmd, check=True, cwd=sdk_path)
        print(f"SUCCESS: {output_name} built")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Build failed - {e}")
        return False


def main():
    print("="*60)
    print("BOA SDKs - Build All")
    print("="*60)
    print(f"\nBase directory: {BASE_DIR}")
    print(f"Output directory: {DIST_DIR}")

    # Create dist directory
    os.makedirs(DIST_DIR, exist_ok=True)

    # Build each SDK
    results = []
    for sdk_dir, output_name, port in SDKS:
        success = build_sdk(sdk_dir, output_name, port)
        results.append((output_name, success, port))

    # Summary
    print("\n" + "="*60)
    print("BUILD SUMMARY")
    print("="*60)

    for name, success, port in results:
        status = "OK" if success else "FAILED"
        print(f"  {name}: {status} (port {port})")

    # List output files
    print(f"\nOutput files in {DIST_DIR}:")
    if os.path.exists(DIST_DIR):
        for f in os.listdir(DIST_DIR):
            path = os.path.join(DIST_DIR, f)
            size = os.path.getsize(path) / (1024*1024)
            print(f"  {f}: {size:.1f} MB")


if __name__ == "__main__":
    main()
