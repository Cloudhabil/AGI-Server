"""
run.py: MindLoop heartbeat entry point (shim).

This file now delegates to the unified runtime kernel (boot.py).
The legacy MindLoop behavior is preserved by running in Sovereign-Loop mode,
which can be customized to match the original MindLoop semantics.
"""

from __future__ import annotations

import sys

from boot import main

if __name__ == "__main__":
    # Preserve legacy behavior: default to Sovereign-Loop mode
    if "--mode" not in sys.argv:
        sys.argv += ["--mode", "Sovereign-Loop"]
    raise SystemExit(main())
