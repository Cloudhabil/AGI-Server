"""
main.py: Unified kernel entry point (shim).

This file now delegates to the unified runtime kernel (boot.py).
The legacy behavior is preserved by defaulting to Sovereign-Loop mode.
"""

from boot import main

if __name__ == "__main__":
    raise SystemExit(main())
