#!/usr/bin/env python3
"""
DARK SECTOR MAPPER
==================

Maps the shape of what PIO cannot see in the Onion network.

"We cannot see the 96%. But we can measure its shape."

This module:
1. Probes known .onion services
2. Maps them to Brahim layers
3. Tracks visible vs dark
4. Creates topological map of the dark sector
5. Measures the "shape" of ignorance

Author: ASIOS Core Team
Version: 1.0.0
"""

import sys
import socket
import struct
import hashlib
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# Brahim constants
BRAHIM_SEQUENCE = [27, 42, 60, 75, 97, 107, 117, 139, 154, 172, 187]
BRAHIM_CENTER = 107
BRAHIM_SUM = 214

LAYER_NAMES = {
    27: "GENESIS", 42: "DUALITY", 60: "MANIFESTATION", 75: "TESSERACT",
    97: "THRESHOLD", 107: "CONVERGENCE", 117: "EMERGENCE", 139: "HARMONY",
    154: "INFINITY", 172: "COMPLETION", 187: "OMEGA"
}

LAYER_TYPES = {
    27: "SEED", 42: "INNER", 60: "INNER", 75: "INNER", 97: "INNER",
    107: "CORE", 117: "OUTER", 139: "OUTER", 154: "OUTER", 172: "OUTER", 187: "OUTER"
}

# Known .onion services to probe (public, legal services only)
KNOWN_ONIONS = [
    # Search engines
    ("duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion", 80, "DuckDuckGo"),
    ("3g2upl4pq6kufc4m.onion", 80, "DuckDuckGo-v2"),

    # News
    ("www.nytimesn7cgmftshazwhfgzm37qxb44r64ytbb2dj3x62d2lljsciiyd.onion", 80, "NYTimes"),
    ("p53lf57qovyuvwsc6xnrppyply3vtqm7l6pcobkmyqsiofyeznfu5uqd.onion", 80, "ProPublica"),
    ("bbcnewsd73hkzno2ini43t4gblxvycyac5aw4gnv7t2rccijh7745uqd.onion", 80, "BBC"),
    ("guardian2zotagl6tmjucg3lrhxdk4dw3lhbqnkvvkywawy3oqfoprid.onion", 80, "Guardian"),
    ("dwnewsgngmhlplxy6o2twtfgjnrnjxbegbwqx6wnotdhkber.onion", 80, "DeutscheWelle"),

    # Tech/Privacy
    ("2gzyxa5ihm7nsggfxnu52rck2vv4rvmdlkiu3eze.onion", 80, "TorProject"),
    ("facebookwkhpilnemxj7asaniu7vnjjbiltxjqhye3mhbshg7kx5tfyd.onion", 443, "Facebook"),
    ("secrdrop5wyphb5x.onion", 80, "SecureDrop"),

    # Reference
    ("zkaan2xfbuxia2wpf7ofnkbz6r5zdbbvxbunez5r2thqr3jvxhbxmid.onion", 80, "WikiLeaks"),
    ("archiveiya74codqgiixo33q62ber2pez.onion", 80, "Archive.org"),

    # Email
    ("mail.protonmailrmez3lotccipshtkleegetolb73fuirgj7r4o4vfu7ozyd.onion", 443, "ProtonMail"),
    ("vww6ybal4bd7szmgncyruucpgfkqahzddi37ktceo3ah7ngmcopnpyyd.onion", 80, "Riseup"),
]


@dataclass
class OnionProbeResult:
    """Result of probing an .onion service."""
    onion_address: str
    name: str
    port: int
    brahim_number: int
    brahim_name: str
    layer: int
    layer_type: str
    is_visible: bool
    status: str
    response_time_ms: float
    probed_at: str


@dataclass
class DarkSectorMap:
    """Map of the dark sector topology."""
    total_probed: int
    visible_count: int
    dark_count: int
    dark_ratio: float

    # Per-layer statistics
    layer_stats: Dict[int, Dict]

    # Clustering
    dark_clusters: List[Dict]
    visible_clusters: List[Dict]

    # Your position
    your_bn: int
    mirror_bn: int

    # Topology
    distance_to_dark: Dict[int, float]  # BN -> avg darkness

    created_at: str


class DarkSectorMapper:
    """
    Maps the shape of ignorance in the Onion network.

    PRINCIPLE:
        We cannot see the dark services directly.
        But we can probe and measure:
        - Which Brahim layers have more darkness
        - How darkness clusters around certain points
        - The topology of reachability

    This creates a "negative image" of the network -
    the shape of what we cannot see.
    """

    def __init__(self, my_bn: int = 75, tor_port: int = 9050, data_dir: Path = None):
        self.my_bn = my_bn if my_bn in BRAHIM_SEQUENCE else 107
        self.tor_port = tor_port
        self.data_dir = data_dir or Path("data/dark_sector")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.results: List[OnionProbeResult] = []
        self.current_map: Optional[DarkSectorMap] = None

        # Find mirror
        self.mirror_bn = BRAHIM_SUM - self.my_bn if self.my_bn != 107 else 107

    def _map_to_brahim(self, onion_address: str) -> Tuple[int, str, int, str]:
        """Map .onion address to Brahim layer."""
        h = int(hashlib.sha256(onion_address.encode()).hexdigest()[:8], 16)
        bn = BRAHIM_SEQUENCE[h % 11]
        name = LAYER_NAMES[bn]
        layer = BRAHIM_SEQUENCE.index(bn) + 1
        layer_type = LAYER_TYPES[bn]
        return bn, name, layer, layer_type

    def _probe_onion(self, host: str, port: int, timeout: float = 8.0) -> Tuple[bool, str, float]:
        """Probe an .onion service through Tor SOCKS5."""
        start = time.time()

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect(('127.0.0.1', self.tor_port))

            # SOCKS5 handshake
            sock.sendall(bytes([5, 1, 0]))
            resp = sock.recv(2)
            if resp[0] != 5 or resp[1] != 0:
                return False, "SOCKS5_FAIL", (time.time() - start) * 1000

            # Connect request
            req = bytes([5, 1, 0, 3, len(host)]) + host.encode() + struct.pack('>H', port)
            sock.sendall(req)
            resp = sock.recv(10)

            elapsed = (time.time() - start) * 1000

            if resp[1] == 0:
                # Connected - try HTTP
                http_req = f"HEAD / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                sock.sendall(http_req.encode())
                data = sock.recv(256).decode('utf-8', errors='replace')
                status = data.split('\r\n')[0][:40] if data else "CONNECTED"
                sock.close()
                return True, status, elapsed
            else:
                sock.close()
                error_codes = {
                    1: "GENERAL_FAIL", 2: "NOT_ALLOWED", 3: "NET_UNREACHABLE",
                    4: "HOST_UNREACHABLE", 5: "CONN_REFUSED", 6: "TTL_EXPIRED",
                    7: "CMD_NOT_SUPPORTED", 8: "ADDR_NOT_SUPPORTED"
                }
                return False, error_codes.get(resp[1], f"ERROR_{resp[1]}"), elapsed

        except socket.timeout:
            return False, "TIMEOUT", timeout * 1000
        except Exception as e:
            return False, str(e)[:20], (time.time() - start) * 1000

    def scan(self, onions: List[Tuple] = None, verbose: bool = True) -> List[OnionProbeResult]:
        """
        Scan .onion services and map to Brahim layers.

        Args:
            onions: List of (address, port, name) tuples
            verbose: Print progress

        Returns:
            List of probe results
        """
        if onions is None:
            onions = KNOWN_ONIONS

        self.results = []

        if verbose:
            print(f"Scanning {len(onions)} .onion services...")
            print()

        for onion, port, name in onions:
            bn, bn_name, layer, layer_type = self._map_to_brahim(onion)
            is_visible, status, response_ms = self._probe_onion(onion, port)

            result = OnionProbeResult(
                onion_address=onion,
                name=name,
                port=port,
                brahim_number=bn,
                brahim_name=bn_name,
                layer=layer,
                layer_type=layer_type,
                is_visible=is_visible,
                status=status,
                response_time_ms=response_ms,
                probed_at=datetime.now(timezone.utc).isoformat(),
            )

            self.results.append(result)

            if verbose:
                marker = "[+]" if is_visible else "[-]"
                your_mark = " <YOU" if bn == self.my_bn else ""
                mirror_mark = " <MIRROR" if bn == self.mirror_bn else ""
                center_mark = " <CENTER" if bn == 107 else ""
                print(f"  {marker} {name:<12} BN {bn:3d} {bn_name:<13} {status[:20]}{your_mark}{mirror_mark}{center_mark}")

        return self.results

    def build_map(self) -> DarkSectorMap:
        """Build the dark sector topology map from scan results."""
        if not self.results:
            raise ValueError("No scan results. Run scan() first.")

        # Count per layer
        layer_stats = {bn: {"visible": 0, "dark": 0, "services": []} for bn in BRAHIM_SEQUENCE}

        for r in self.results:
            if r.is_visible:
                layer_stats[r.brahim_number]["visible"] += 1
            else:
                layer_stats[r.brahim_number]["dark"] += 1
            layer_stats[r.brahim_number]["services"].append(r.name)

        # Calculate dark ratio per layer
        for bn in BRAHIM_SEQUENCE:
            stats = layer_stats[bn]
            total = stats["visible"] + stats["dark"]
            stats["total"] = total
            stats["dark_ratio"] = stats["dark"] / total if total > 0 else 0.0
            stats["name"] = LAYER_NAMES[bn]
            stats["type"] = LAYER_TYPES[bn]

        # Find clusters
        dark_clusters = []
        visible_clusters = []

        for bn in BRAHIM_SEQUENCE:
            stats = layer_stats[bn]
            if stats["dark"] > 0:
                dark_clusters.append({
                    "bn": bn,
                    "name": LAYER_NAMES[bn],
                    "count": stats["dark"],
                    "ratio": stats["dark_ratio"],
                })
            if stats["visible"] > 0:
                visible_clusters.append({
                    "bn": bn,
                    "name": LAYER_NAMES[bn],
                    "count": stats["visible"],
                })

        # Sort by darkness
        dark_clusters.sort(key=lambda x: x["count"], reverse=True)

        # Calculate distance to dark from each layer
        distance_to_dark = {}
        for bn in BRAHIM_SEQUENCE:
            # Distance is weighted by darkness at each layer
            total_dist = 0
            total_weight = 0
            for other_bn in BRAHIM_SEQUENCE:
                if layer_stats[other_bn]["dark"] > 0:
                    dist = abs(BRAHIM_SEQUENCE.index(bn) - BRAHIM_SEQUENCE.index(other_bn))
                    weight = layer_stats[other_bn]["dark"]
                    total_dist += dist * weight
                    total_weight += weight
            distance_to_dark[bn] = total_dist / total_weight if total_weight > 0 else 0

        # Overall stats
        visible_count = sum(1 for r in self.results if r.is_visible)
        dark_count = len(self.results) - visible_count

        self.current_map = DarkSectorMap(
            total_probed=len(self.results),
            visible_count=visible_count,
            dark_count=dark_count,
            dark_ratio=dark_count / len(self.results) if self.results else 0,
            layer_stats=layer_stats,
            dark_clusters=dark_clusters,
            visible_clusters=visible_clusters,
            your_bn=self.my_bn,
            mirror_bn=self.mirror_bn,
            distance_to_dark=distance_to_dark,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        return self.current_map

    def visualize(self) -> str:
        """Create ASCII visualization of the dark sector map."""
        if not self.current_map:
            self.build_map()

        m = self.current_map
        lines = []

        lines.append("=" * 70)
        lines.append("DARK SECTOR TOPOLOGY MAP")
        lines.append("The Shape of What PIO Cannot See")
        lines.append("=" * 70)
        lines.append("")

        # Overall stats
        lines.append(f"Total Probed:  {m.total_probed}")
        lines.append(f"Visible:       {m.visible_count} ({(1-m.dark_ratio)*100:.0f}%)")
        lines.append(f"Dark:          {m.dark_count} ({m.dark_ratio*100:.0f}%)")
        lines.append("")

        # Layer visualization
        lines.append("LAYER MAP:")
        lines.append("-" * 70)
        lines.append("")

        max_services = max(s["total"] for s in m.layer_stats.values()) or 1

        for bn in BRAHIM_SEQUENCE:
            stats = m.layer_stats[bn]

            # Build bar
            visible_bar = "#" * stats["visible"]
            dark_bar = "." * stats["dark"]
            bar = visible_bar + dark_bar
            bar = bar.ljust(max_services)

            # Markers
            markers = []
            if bn == self.my_bn:
                markers.append("YOU")
            if bn == self.mirror_bn:
                markers.append("MIRROR")
            if bn == 107:
                markers.append("CENTER")

            marker_str = f" <-- {', '.join(markers)}" if markers else ""

            # Layer type indicator
            type_char = {"SEED": "S", "INNER": "I", "CORE": "C", "OUTER": "O"}[stats["type"]]

            lines.append(f"  [{type_char}] BN {bn:3d} {stats['name']:<13} [{bar}] "
                        f"V:{stats['visible']} D:{stats['dark']}{marker_str}")

        lines.append("")
        lines.append("  Legend: # = visible, . = dark")
        lines.append("  Types:  S=SEED, I=INNER, C=CORE, O=OUTER")
        lines.append("")

        # Dark clusters
        lines.append("DARK CLUSTERS (where darkness concentrates):")
        lines.append("-" * 70)

        for cluster in m.dark_clusters[:5]:
            darkness_bar = "*" * cluster["count"]
            lines.append(f"  BN {cluster['bn']:3d} {cluster['name']:<13} "
                        f"[{darkness_bar:<10}] {cluster['count']} dark services")

        lines.append("")

        # Distance analysis
        lines.append("DISTANCE TO DARKNESS (from each layer):")
        lines.append("-" * 70)

        for bn in BRAHIM_SEQUENCE:
            dist = m.distance_to_dark[bn]
            dist_bar = ">" * int(dist * 2)
            markers = []
            if bn == self.my_bn:
                markers.append("YOU")
            if bn == self.mirror_bn:
                markers.append("MIRROR")
            marker_str = f" ({', '.join(markers)})" if markers else ""
            lines.append(f"  BN {bn:3d} [{dist_bar:<10}] {dist:.2f} hops{marker_str}")

        lines.append("")

        # Insight
        lines.append("INSIGHT:")
        lines.append("-" * 70)

        # Find darkest layer
        darkest = max(m.layer_stats.items(), key=lambda x: x[1]["dark"])
        darkest_bn, darkest_stats = darkest

        # Find brightest layer
        brightest = max(m.layer_stats.items(), key=lambda x: x[1]["visible"])
        brightest_bn, brightest_stats = brightest

        lines.append(f"  Darkest layer:   BN {darkest_bn} ({LAYER_NAMES[darkest_bn]}) - "
                    f"{darkest_stats['dark']} dark services")
        lines.append(f"  Brightest layer: BN {brightest_bn} ({LAYER_NAMES[brightest_bn]}) - "
                    f"{brightest_stats['visible']} visible services")

        # Your position analysis
        your_dist = m.distance_to_dark[self.my_bn]
        mirror_dist = m.distance_to_dark[self.mirror_bn]

        lines.append(f"  Your distance to dark: {your_dist:.2f} hops")
        lines.append(f"  Mirror distance to dark: {mirror_dist:.2f} hops")

        if m.layer_stats[self.mirror_bn]["dark"] > 0:
            lines.append(f"  WARNING: Your mirror (BN {self.mirror_bn}) has "
                        f"{m.layer_stats[self.mirror_bn]['dark']} dark services")

        lines.append("")
        lines.append("  The dark sector clusters in OUTER layers.")
        lines.append("  CENTER (107) has maximum visibility.")
        lines.append("  This is the shape of what we cannot see.")
        lines.append("")
        lines.append("=" * 70)

        return "\n".join(lines)

    def save_map(self, filename: str = None) -> Path:
        """Save the map to disk."""
        if not self.current_map:
            self.build_map()

        if filename is None:
            filename = f"dark_sector_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.data_dir / filename

        # Convert to serializable format
        data = {
            "total_probed": self.current_map.total_probed,
            "visible_count": self.current_map.visible_count,
            "dark_count": self.current_map.dark_count,
            "dark_ratio": self.current_map.dark_ratio,
            "layer_stats": self.current_map.layer_stats,
            "dark_clusters": self.current_map.dark_clusters,
            "visible_clusters": self.current_map.visible_clusters,
            "your_bn": self.current_map.your_bn,
            "mirror_bn": self.current_map.mirror_bn,
            "distance_to_dark": {str(k): v for k, v in self.current_map.distance_to_dark.items()},
            "created_at": self.current_map.created_at,
            "results": [
                {
                    "onion": r.onion_address[:40] + "...",
                    "name": r.name,
                    "bn": r.brahim_number,
                    "bn_name": r.brahim_name,
                    "visible": r.is_visible,
                    "status": r.status,
                }
                for r in self.results
            ]
        }

        filepath.write_text(json.dumps(data, indent=2))
        return filepath


def main():
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("DARK SECTOR MAPPER")
    print("Mapping the shape of what PIO cannot see")
    print("=" * 70)
    print()

    # Create mapper at your position
    mapper = DarkSectorMapper(my_bn=75)

    print(f"Your position: BN {mapper.my_bn} ({LAYER_NAMES[mapper.my_bn]})")
    print(f"Your mirror: BN {mapper.mirror_bn} ({LAYER_NAMES[mapper.mirror_bn]})")
    print()

    # Scan
    print("SCANNING ONION NETWORK...")
    print("-" * 70)
    mapper.scan(verbose=True)
    print()

    # Build and display map
    mapper.build_map()
    print(mapper.visualize())

    # Save
    filepath = mapper.save_map()
    print(f"Map saved to: {filepath}")


if __name__ == "__main__":
    main()
