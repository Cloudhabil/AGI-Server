#!/usr/bin/env python3
"""
Build BSI as a standalone executable.

Requirements:
    pip install pyinstaller

Usage:
    python build_executable.py

Output:
    dist/bsi_app.exe (Windows)
    dist/bsi_app (Linux/Mac)
"""

import subprocess
import sys
import os

def main():
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "bsi_app.py")

    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Single executable
        "--name", "BrahimSecureIntelligence",
        "--clean",                      # Clean cache
        "--noconfirm",                  # Overwrite output
        app_path
    ]

    print("Building executable...")
    print(f"Command: {' '.join(cmd)}")

    result = subprocess.run(cmd, cwd=script_dir)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("=" * 60)
        print(f"\nExecutable location: {os.path.join(script_dir, 'dist')}")
        print("\nRun with:")
        if sys.platform == "win32":
            print("  dist\\BrahimSecureIntelligence.exe")
            print("  dist\\BrahimSecureIntelligence.exe --verify")
            print("  dist\\BrahimSecureIntelligence.exe --chat")
        else:
            print("  dist/BrahimSecureIntelligence")
            print("  dist/BrahimSecureIntelligence --verify")
            print("  dist/BrahimSecureIntelligence --chat")
    else:
        print("\nBuild failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
