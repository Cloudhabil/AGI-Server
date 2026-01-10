"""
Filesystem Gardener Daemon: Autonomous File Organization Service

This daemon runs continuously in the background, organizing the chaos
of the codebase into a coherent structure without deleting anything.

Features:
- Real-time filesystem monitoring
- Intelligent classification using GPIA
- Automatic organization into taxonomy
- Bidirectional communication with main agent
- Comprehensive audit logging
- Zero deletion policy

Usage:
    # Run as standalone daemon
    python filesystem_gardener_daemon.py

    # Run with initial scan
    python filesystem_gardener_daemon.py --scan

    # Run with custom root
    python filesystem_gardener_daemon.py --root /path/to/project
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add root to path
# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
)

from core.filesystem_gardener import get_gardener
from core.gpia_bridge import GPIABridge, MessageType
from core.gpia_bridge import notify_gpia_artifact_discovered, notify_gpia_artifact_organized, send_gardener_stats
from core.kernel.substrate import KernelSubstrate


class GardenerDaemon:
    """
    Orchestrates the Filesystem Gardener with GPIA integration.
    """

    def __init__(self, root: Path, enable_gpia: bool = True):
        self.root = root
        self.enable_gpia = enable_gpia

        print("=" * 80)
        print("     FILESYSTEM GARDENER DAEMON")
        print("     Autonomous File Organization Service")
        print("=" * 80)
        print(f"Root: {self.root}")
        print(f"GPIA Integration: {'Enabled' if enable_gpia else 'Disabled'}")
        print()

        # Initialize kernel (optional, for GPIA intelligence)
        self.kernel = None
        if enable_gpia:
            try:
                print("[INIT] Initializing Kernel Substrate...")
                self.kernel = KernelSubstrate(str(self.root))
                print("[INIT] Kernel initialized successfully")
            except Exception as e:
                print(f"[INIT] Warning: Kernel initialization failed: {e}")
                print("[INIT] Running without GPIA intelligence (heuristics only)")

        # Initialize GPIA bridge
        self.bridge = None
        if enable_gpia:
            try:
                print("[INIT] Initializing GPIA Bridge...")
                self.bridge = GPIABridge(self.root, sender="gardener")
                self._setup_bridge_handlers()
                print("[INIT] GPIA Bridge ready")
            except Exception as e:
                print(f"[INIT] Warning: Bridge initialization failed: {e}")

        # Initialize gardener
        print("[INIT] Initializing Filesystem Gardener...")
        self.gardener = get_gardener(
            root=self.root,
            kernel=self.kernel,
            gpia_callback=self._gpia_callback if self.bridge else None
        )
        print("[INIT] Gardener ready")
        print()

        # Stats reporting
        self.last_stats_report = time.time()
        self.stats_interval = 60  # Report every 60 seconds

    def _setup_bridge_handlers(self):
        """Setup handlers for messages from GPIA"""

        def handle_scan_command(message):
            directory = message.payload.get('directory', '.')
            print(f"[GPIA CMD] Scan directory: {directory}")
            self.gardener.scan_existing(directory)

        def handle_organize_command(message):
            artifact = message.payload.get('artifact_path')
            classification = message.payload.get('classification')
            print(f"[GPIA CMD] Organize {artifact} as {classification}")
            # TODO: Implement manual organization override

        def handle_update_config(message):
            config = message.payload.get('config', {})
            print(f"[GPIA CMD] Update config: {config}")
            # TODO: Implement dynamic config update

        def handle_shutdown(message):
            print(f"[GPIA CMD] Shutdown requested")
            self.shutdown()

        # Register handlers
        self.bridge.register_callback(MessageType.SCAN_DIRECTORY, handle_scan_command)
        self.bridge.register_callback(MessageType.ORGANIZE_COMMAND, handle_organize_command)
        self.bridge.register_callback(MessageType.UPDATE_CONFIG, handle_update_config)
        self.bridge.register_callback(MessageType.SHUTDOWN, handle_shutdown)

        # Start listening
        self.bridge.listen_from_gpia(poll_interval=2.0)

    def _gpia_callback(self, event: dict):
        """Callback for Gardener events to notify GPIA"""
        if not self.bridge:
            return

        try:
            event_type = event.get('event')

            if event_type == 'artifact_processed':
                artifact = event['artifact']
                notify_gpia_artifact_discovered(
                    self.bridge,
                    artifact['path'],
                    event['classification']
                )

        except Exception as e:
            print(f"[BRIDGE] Callback error: {e}")

    def run(self, scan_on_start: bool = False):
        """
        Run the daemon.

        Args:
            scan_on_start: If True, scan existing files before monitoring
        """
        try:
            # Start gardener
            self.gardener.start()

            # Optional initial scan
            if scan_on_start:
                print("[DAEMON] Performing initial scan...")
                self.gardener.scan_existing(".")
                print("[DAEMON] Initial scan complete")

            print("\n" + "=" * 80)
            print("DAEMON ACTIVE - Monitoring filesystem for changes")
            print("Press Ctrl+C to stop")
            print("=" * 80 + "\n")

            # Main loop
            while True:
                time.sleep(5)

                # Periodic stats reporting to GPIA
                if time.time() - self.last_stats_report >= self.stats_interval:
                    self._report_stats()

        except KeyboardInterrupt:
            print("\n[DAEMON] Shutdown requested by user")
            self.shutdown()

    def shutdown(self):
        """Clean shutdown"""
        print("\n[DAEMON] Shutting down...")

        # Send final stats
        self._report_stats()

        # Stop gardener
        if self.gardener:
            self.gardener.stop()

        # Stop bridge
        if self.bridge:
            self.bridge.stop_listening()

        print("[DAEMON] Shutdown complete")
        sys.exit(0)

    def _report_stats(self):
        """Report statistics to console and GPIA"""
        stats = self.gardener.get_stats()

        # Console report
        print("\n" + "-" * 80)
        print(f"[STATS] Uptime: {stats['uptime']:.0f}s | "
              f"Processed: {stats['artifacts_processed']} | "
              f"Organized: {stats['artifacts_organized']} | "
              f"Queue: {stats['queue_size']}")

        if stats['classifications']:
            print("[STATS] Classifications:")
            for classification, count in sorted(stats['classifications'].items()):
                print(f"        {classification}: {count}")

        print("-" * 80 + "\n")

        # Send to GPIA
        if self.bridge:
            send_gardener_stats(self.bridge, stats)

        self.last_stats_report = time.time()


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Filesystem Gardener Daemon - Autonomous File Organization"
    )
    parser.add_argument(
        '--root',
        type=str,
        default='.',
        help='Root directory to organize (default: current directory)'
    )
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Scan existing files on startup'
    )
    parser.add_argument(
        '--no-gpia',
        action='store_true',
        help='Disable GPIA integration (heuristics only)'
    )
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Error: Root directory does not exist: {root}")
        sys.exit(1)

    daemon = GardenerDaemon(
        root=root,
        enable_gpia=not args.no_gpia
    )

    daemon.run(scan_on_start=args.scan)


if __name__ == "__main__":
    main()
