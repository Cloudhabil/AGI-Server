"Production implementations of kernel services."

from __future__ import annotations

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, List

from core.agents.base import SupportsLedger, SupportsPerception, SupportsTelemetry
from core.kernel.budget_service import get_budget_service

logger = logging.getLogger(__name__)


class ProductionLedger(SupportsLedger):
    """
    Production ledger implementation.
    Stores records in JSONL files and maintains agent identity.
    """

    def __init__(self, ledger_dir: str = "data/ledger"):
        self.ledger_dir = Path(ledger_dir)
        self.ledger_dir.mkdir(parents=True, exist_ok=True)
        self.main_log = self.ledger_dir / "kernel.jsonl"
        self.identity_file = self.ledger_dir / "identity.json"
        self._identity: Optional[Dict[str, Any]] = None

    def append(self, stream: str, record: Dict[str, Any]) -> None:
        """Append record to a named stream in the JSONL log."""
        entry = {
            "timestamp": time.time(),
            "stream": stream,
            "record": record
        }
        with open(self.main_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        logger.debug(f"[Ledger] {stream}: {record}")

    def get_identity_record(self) -> Optional[Dict[str, Any]]:
        """Retrieve or create the agent identity record."""
        if self._identity:
            return self._identity

        if self.identity_file.exists():
            try:
                self._identity = json.loads(self.identity_file.read_text(encoding="utf-8"))
                return self._identity
            except Exception as e:
                logger.error(f"Failed to load identity: {e}")

        # Default identity if not found
        self._identity = {
            "agent_id": "gpia-sovereign",
            "kernel_signature": "unified_kernel_v1",
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "hardware_id": self._get_hw_id()
        }
        self.identity_file.write_text(json.dumps(self._identity, indent=2), encoding="utf-8")
        return self._identity

    def _get_hw_id(self) -> str:
        """Simple hardware identifier."""
        import platform
        import uuid
        return f"{platform.node()}-{uuid.getnode()}"


class ProductionPerception(SupportsPerception):
    """
    Production perception implementation (CLI).
    Handles standard I/O with basic formatting.
    """

    def read_command(self) -> str:
        """Read command from stdin with a prompt."""
        try:
            # Use color if available or requested
            prompt = "\033[1;34m[GPIA]>\033[0m " if sys.stdout.isatty() else "> "
            return input(prompt).strip()
        except EOFError:
            return "exit"
        except KeyboardInterrupt:
            return "exit"

    def write(self, msg: str) -> None:
        """Write message to stdout."""
        print(msg, end="", flush=True)


class ProductionTelemetry(SupportsTelemetry):
    """
    Production telemetry implementation.
    Integrates BudgetService for hardware vitals and logs events.
    """

    def __init__(self, telemetry_dir: str = "logs/telemetry"):
        self.telemetry_dir = Path(telemetry_dir)
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)
        self.event_log = self.telemetry_dir / f"telemetry_{int(time.time())}.jsonl"
        self.budget_service = get_budget_service()
        
        # Start background heartbeat if needed, but for now we'll do it synchronously
        self._last_heartbeat = 0.0

    def emit(self, event: str, payload: Dict[str, Any]) -> None:
        """Emit a telemetry event with system context."""
        # Enrich payload with basic vitals if it's a critical event
        if event.startswith("kernel.") or event.startswith("security."):
            try:
                snapshot = self.budget_service.get_resource_snapshot()
                payload["vitals"] = {
                    "cpu": snapshot.cpu_percent,
                    "vram_util": snapshot.vram_util,
                    "ram_util": snapshot.ram_util
                }
            except:
                pass

        entry = {
            "timestamp": time.time(),
            "event": event,
            "payload": payload
        }
        
        with open(self.event_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
            
        if event == "kernel.error" or event.startswith("security.threat"):
            logger.error(f"[TELEMETRY] {event}: {payload}")
        else:
            logger.debug(f"[TELEMETRY] {event}: {payload}")

    def heartbeat(self, name: str, payload: Dict[str, Any]) -> None:
        """Emit a heartbeat signal, including full resource snapshot."""
        now = time.time()
        # Rate limit heartbeat logging to disk but always update status
        if now - self._last_heartbeat >= 5.0:
            try:
                snapshot = self.budget_service.get_resource_snapshot()
                payload["resources"] = {
                    "cpu_pct": snapshot.cpu_percent,
                    "vram_used_mb": snapshot.vram_used_mb,
                    "vram_total_mb": snapshot.vram_total_mb,
                    "ram_used_mb": snapshot.ram_used_mb,
                    "disk_write_mbps": snapshot.disk_write_mbps
                }
                
                # Check safety
                is_safe, reason = self.budget_service.check_safety(snapshot)
                payload["safety"] = {"is_safe": is_safe, "reason": reason}
                
                if not is_safe:
                    self.emit("security.safety_breach", {"reason": reason, "snapshot": payload["resources"]})
            except Exception as e:
                payload["resource_error"] = str(e)

            self.emit(f"heartbeat.{name}", payload)
            self._last_heartbeat = now


def make_production_ledger() -> ProductionLedger:
    """Factory for production ledger service."""
    return ProductionLedger()


def make_production_perception() -> ProductionPerception:
    """Factory for production perception service."""
    return ProductionPerception()


def make_production_telemetry() -> ProductionTelemetry:
    """Factory for production telemetry service."""
    return ProductionTelemetry()
