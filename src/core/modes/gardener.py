"""
Gardener Mode: Autonomous File Organization

An operational mode that runs the Filesystem Gardener daemon
integrated with the main GPIA agent for bidirectional communication.

Usage:
    python boot.py --mode Gardener

Features:
- Real-time filesystem monitoring
- Intelligent classification via GPIA
- Auto-organization with zero deletion
- Audit logging
- Interactive controls
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from core.agents.base import BaseAgent, AgentContext
from core.filesystem_gardener import get_gardener, FilesystemGardener
from core.gpia_bridge import GPIABridge, MessageType
from core.gpia_bridge import notify_gpia_artifact_discovered, send_gardener_stats


class GardenerMode(BaseAgent):
    """
    Operational mode for autonomous file organization.

    Integrates Filesystem Gardener with the main agent's kernel.
    """

    def __init__(self, ctx: AgentContext):
        super().__init__(ctx)
        self.root = Path.cwd()

        # Initialize GPIA bridge
        self.bridge = GPIABridge(self.root, sender="gardener")
        self._setup_bridge()

        # Initialize gardener with kernel integration
        self.gardener: Optional[FilesystemGardener] = None

        # Stats
        self.last_stats_time = time.time()
        self.stats_interval = 60  # seconds

    def _setup_bridge(self):
        """Setup bidirectional communication handlers"""

        def handle_scan_command(message):
            directory = message.payload.get('directory', '.')
            self.ctx.perception.write(f"[GPIA] Scanning directory: {directory}\n")
            if self.gardener:
                self.gardener.scan_existing(directory)

        def handle_shutdown(message):
            self.ctx.perception.write("[GPIA] Shutdown command received\n")
            self.shutdown()

        # Register handlers
        self.bridge.register_callback(MessageType.SCAN_DIRECTORY, handle_scan_command)
        self.bridge.register_callback(MessageType.SHUTDOWN, handle_shutdown)

        # Start listening
        self.bridge.listen_from_gpia(poll_interval=2.0)

    def _gpia_callback(self, event: dict):
        """Forward Gardener events to GPIA via bridge"""
        try:
            event_type = event.get('event')

            if event_type == 'artifact_processed':
                artifact = event['artifact']
                classification = event['classification']
                confidence = event['confidence']

                # Log to perception
                self.ctx.perception.write(
                    f"[Gardener] {artifact['path']} → {classification} ({confidence:.2f})\n"
                )

                # Notify GPIA
                notify_gpia_artifact_discovered(
                    self.bridge,
                    artifact['path'],
                    classification
                )

        except Exception as e:
            self.ctx.perception.write(f"[Gardener] Callback error: {e}\n")

    def initialize(self) -> None:
        """Initialize the Gardener mode"""
        self.ctx.perception.write("=" * 80 + "\n")
        self.ctx.perception.write("GARDENER MODE - Autonomous File Organization\n")
        self.ctx.perception.write("=" * 80 + "\n\n")

        # Create gardener with kernel integration
        self.ctx.perception.write("Initializing Filesystem Gardener...\n")
        self.gardener = get_gardener(
            root=self.root,
            kernel=self.ctx.kernel,
            gpia_callback=self._gpia_callback
        )

        # Start autonomous operation
        self.gardener.start()
        self.ctx.perception.write("Gardener active. Monitoring filesystem...\n\n")

        # Emit telemetry
        self.ctx.telemetry.emit(
            "gardener.started",
            {
                "root": str(self.root),
                "agent_id": self.ctx.identity.get("agent_id")
            }
        )

    def step(self) -> None:
        """Single step of Gardener operation"""

        # Periodic stats reporting
        if time.time() - self.last_stats_time >= self.stats_interval:
            self._report_stats()

        # Allow some idle time
        time.sleep(5)

    def shutdown(self) -> None:
        """Clean shutdown of Gardener"""
        self.ctx.perception.write("\n[Gardener] Shutting down...\n")

        # Final stats
        self._report_stats()

        # Stop gardener
        if self.gardener:
            self.gardener.stop()

        # Stop bridge
        self.bridge.stop_listening()

        self.ctx.telemetry.emit("gardener.stopped", {})
        self.ctx.perception.write("[Gardener] Shutdown complete\n")

    def _report_stats(self):
        """Report gardener statistics"""
        if not self.gardener:
            return

        stats = self.gardener.get_stats()

        # Console output
        self.ctx.perception.write("\n" + "-" * 80 + "\n")
        self.ctx.perception.write(
            f"[Stats] Uptime: {stats['uptime']:.0f}s | "
            f"Processed: {stats['artifacts_processed']} | "
            f"Organized: {stats['artifacts_organized']} | "
            f"Queue: {stats['queue_size']}\n"
        )

        if stats['classifications']:
            self.ctx.perception.write("[Stats] Classifications:\n")
            for classification, count in sorted(stats['classifications'].items()):
                self.ctx.perception.write(f"        {classification}: {count}\n")

        self.ctx.perception.write("-" * 80 + "\n\n")

        # Send to GPIA via bridge
        send_gardener_stats(self.bridge, stats)

        # Emit telemetry
        self.ctx.telemetry.emit("gardener.stats", stats)

        self.last_stats_time = time.time()
