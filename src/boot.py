"""
Unified Runtime Kernel: Single boot point for all operational modes.

Replaces fragmented main.py, run.py, gpia.py entry points.

Architecture:
1. Parse CLI arguments (--mode)
2. Build config with service factories
3. Initialize services exactly once
4. Run sovereignty preflight check
5. Create AgentContext
6. Start CortexSwitchboard for mode orchestration
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any, Dict, Optional

from core.agents.base import AgentContext
from core.kernel.services import init_services
from core.kernel.preflight import sovereignty_preflight_check, SovereigntyPreflightError
from core.kernel.switchboard import CortexSwitchboard, MODE_REGISTRY
from core.runtime.engine_factory import build_capsule_engine

logger = logging.getLogger(__name__)


def build_config() -> Dict[str, Any]:
    """
    Build kernel configuration with service factories.

    Maps to actual implementations in the codebase.
    """
    from core.production_services import (
        make_production_ledger,
        make_production_perception,
        make_production_telemetry
    )

    return {
        "ledger_factory": make_production_ledger,
        "perception_factory": make_production_perception,
        "telemetry_factory": make_production_telemetry,
        # Capsule engine selection ("government" preferred to enable ministers)
        "capsule_engine": "government",
        "legacy_gpia_module": "gpia",
    }


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace with parsed arguments
    """
    # Register modes if not already done
    if not MODE_REGISTRY:
        from core.kernel.switchboard import _register_modes
        _register_modes()

    p = argparse.ArgumentParser(
        prog="boot.py",
        description="Unified Runtime Kernel - Single entry point for all operational modes"
    )
    p.add_argument(
        "--mode",
        default="Sovereign-Loop",
        choices=list(MODE_REGISTRY.keys()),
        help="Operational mode to start in"
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Fail hard on any preflight anomaly"
    )
    p.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    return p.parse_args()


def main() -> int:
    """
    Main kernel boot sequence.

    Steps:
    1. Parse arguments
    2. Configure logging
    3. Build config
    4. Initialize services
    5. Run preflight check
    6. Create context
    7. Start switchboard

    Returns:
        Exit code (0 = clean, 1 = error, 2 = preflight failed)
    """
    args = parse_args()

    # Configure logging
    if args.verbose:
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(name)s] %(levelname)s: %(message)s"
        )
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="[%(levelname)s] %(message)s"
        )

    logger.info(f"Unified Runtime Kernel starting in mode: {args.mode}")

    # Build configuration
    config = build_config()

    # Build capsule engine façade (legacy by default)
    engine = build_capsule_engine(config)

    # Initialize kernel services (Ledger, Perception, Telemetry)
    try:
        services = init_services(config)
        logger.info("Kernel services initialized")
    except Exception as e:
        logger.error(f"Failed to initialize kernel services: {e}")
        return 1

    # Run sovereignty preflight check
    try:
        identity = sovereignty_preflight_check(services)
        logger.info(f"Sovereignty preflight passed for agent: {identity.get('agent_id')}")
    except SovereigntyPreflightError as e:
        services.telemetry.emit(
            "kernel.halt",
            {"reason": "preflight_failed", "error": str(e)}
        )
        if args.strict:
            logger.error(f"Preflight failed (strict mode): {e}")
            raise
        # Non-strict: print message and stop gracefully
        try:
            services.perception.write(f"[KERNEL HALT] {e}\n")
        except Exception:
            pass
        logger.error(f"Preflight failed (non-strict): {e}")
        return 2

    # Create shared agent context
    from core.kernel.substrate import KernelSubstrate
    substrate = KernelSubstrate()

    ctx = AgentContext(
        identity=identity,
        telemetry=services.telemetry,
        ledger=services.ledger,
        perception=services.perception,
        kernel=substrate,
        engine=engine,
        state={
            "boot_mode": args.mode,
            "kernel": "UnifiedRuntimeKernel",
            "kernel_version": "1.0",
        },
    )

    services.telemetry.emit(
        "kernel.boot",
        {
            "mode": args.mode,
            "agent_id": identity.get("agent_id"),
            "strict": args.strict
        }
    )

    # Start mode orchestration
    try:
        switchboard = CortexSwitchboard(ctx=ctx, start_mode=args.mode)
        switchboard.run()
        logger.info("Kernel shutdown cleanly")
        return 0
    except KeyboardInterrupt:
        logger.info("Kernel interrupted by user")
        services.telemetry.emit("kernel.interrupted", {})
        return 0
    except Exception as e:
        logger.exception(f"Kernel error: {e}")
        services.telemetry.emit("kernel.error", {"error": str(e)})
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
