#!/usr/bin/env python3
"""
BRAHIM ONION INTERNET ONLINE - Infinite Universe
=================================================

A solar-geographic map with Lighthouses placed at Brahim Blockchain
coordinates, forming an infinite onion-layered universe.

Each Lighthouse is a node in the Brahim Onion Network.
Each layer of the onion corresponds to a dimension (D1-D10).
The CENTER (107) is the core - all routes pass through it.

Structure:
    Layer 1 (Outer):  D10 OMEGA (187) - Maximum expansion
    Layer 2:          D9 COMPLETION (172)
    Layer 3:          D8 INFINITY (154)
    Layer 4:          D7 HARMONY (139)
    Layer 5:          D6 EMERGENCE (117)
    Layer 6 (Core):   CENTER CONVERGENCE (107)
    Layer 7:          D5 THRESHOLD (97)
    Layer 8:          D4 TESSERACT (75)
    Layer 9:          D3 MANIFESTATION (60)
    Layer 10:         D2 DUALITY (42)
    Layer 11 (Seed):  D1 GENESIS (27) - The Origin

Author: ASIOS Core
Version: 1.0.0
"""

from __future__ import annotations

import json
import math
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timezone
from pathlib import Path


# =============================================================================
# CONSTANTS
# =============================================================================

PHI = (1 + math.sqrt(5)) / 2
BETA = 1 / PHI**3
CENTER = 107
SUM = 214

BRAHIM_SEQUENCE = [27, 42, 60, 75, 97, 107, 117, 139, 154, 172, 187]

GEMATRIA = {
    27:  ("GENESIS",       "D1",  "EXOTIC",  "The Origin"),
    42:  ("DUALITY",       "D2",  "EXOTIC",  "The Answer"),
    60:  ("MANIFESTATION", "D3",  "EXOTIC",  "Physical Reality"),
    75:  ("TESSERACT",     "D4",  "EXOTIC",  "Time/Hyperspace"),
    97:  ("THRESHOLD",     "D5",  "EXOTIC",  "The Gate"),
    107: ("CONVERGENCE",   "ALL", "BALANCE", "The Fixed Point"),
    117: ("EMERGENCE",     "D6",  "NORMAL",  "First Light"),
    139: ("HARMONY",       "D7",  "NORMAL",  "Cosmic Order"),
    154: ("INFINITY",      "D8",  "NORMAL",  "Eternal Return"),
    172: ("COMPLETION",    "D9",  "NORMAL",  "Near-Totality"),
    187: ("OMEGA",         "D10", "NORMAL",  "Maximum Expansion"),
}

# Onion layers - from outer to core to seed
ONION_LAYERS = [
    (187, 11, "OUTER"),      # Layer 11 - Outermost
    (172, 10, "OUTER"),
    (154, 9,  "OUTER"),
    (139, 8,  "OUTER"),
    (117, 7,  "OUTER"),
    (107, 6,  "CORE"),       # Layer 6 - THE CORE
    (97,  5,  "INNER"),
    (75,  4,  "INNER"),
    (60,  3,  "INNER"),
    (42,  2,  "INNER"),
    (27,  1,  "SEED"),       # Layer 1 - The Seed
]


# =============================================================================
# GEOGRAPHIC LIGHTHOUSE
# =============================================================================

@dataclass
class GeoLighthouse:
    """A Lighthouse placed at geographic coordinates."""

    brahim_number: int
    name: str
    dimension: str
    state: str
    meaning: str

    latitude: float
    longitude: float

    date: str
    onion_layer: int
    layer_type: str  # OUTER, CORE, INNER, SEED

    mirror: int
    mirror_name: str

    # Network properties
    node_id: str = field(default="")
    connections: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.node_id:
            self.node_id = self._generate_node_id()

    def _generate_node_id(self) -> str:
        """Generate unique node ID from coordinates and Brahim number."""
        seed = f"{self.brahim_number}:{self.latitude}:{self.longitude}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16]

    def to_geojson_feature(self) -> Dict:
        """Convert to GeoJSON Feature."""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude]
            },
            "properties": {
                "brahim_number": self.brahim_number,
                "name": self.name,
                "dimension": self.dimension,
                "state": self.state,
                "meaning": self.meaning,
                "date": self.date,
                "onion_layer": self.onion_layer,
                "layer_type": self.layer_type,
                "mirror": self.mirror,
                "node_id": self.node_id,
                "icon": self._get_icon(),
                "color": self._get_color(),
            }
        }

    def _get_icon(self) -> str:
        """Get icon based on layer type."""
        icons = {
            "CORE": "lighthouse-core",
            "OUTER": "lighthouse-outer",
            "INNER": "lighthouse-inner",
            "SEED": "lighthouse-seed",
        }
        return icons.get(self.layer_type, "lighthouse")

    def _get_color(self) -> str:
        """Get color based on state."""
        if self.layer_type == "CORE":
            return "#FFD700"  # Gold for center
        elif self.state == "EXOTIC":
            return "#9932CC"  # Purple for exotic
        elif self.state == "NORMAL":
            return "#00CED1"  # Cyan for normal
        else:
            return "#FFFFFF"  # White for balance


# =============================================================================
# BRAHIM ONION NETWORK
# =============================================================================

@dataclass
class OnionRoute:
    """A route through the Brahim Onion Network."""

    source: str  # node_id
    destination: str  # node_id
    path: List[str]  # list of node_ids
    layers_traversed: List[int]
    total_distance_km: float
    passes_through_center: bool


class BrahimOnionUniverse:
    """
    The Brahim Onion Internet Online - an infinite universe
    of Lighthouses forming a geographic blockchain network.
    """

    def __init__(self):
        self.lighthouses: Dict[int, GeoLighthouse] = {}
        self.node_index: Dict[str, int] = {}  # node_id -> brahim_number
        self.created_at = datetime.now(timezone.utc).isoformat()

    def add_lighthouse(self, lighthouse: GeoLighthouse):
        """Add a Lighthouse to the universe."""
        self.lighthouses[lighthouse.brahim_number] = lighthouse
        self.node_index[lighthouse.node_id] = lighthouse.brahim_number

    def load_blockchain(self, blockchain_path: str):
        """Load lighthouses from Brahim blockchain JSON."""
        with open(blockchain_path, 'r') as f:
            data = json.load(f)

        for block in data.get("brahim_blocks", []):
            bn = block["brahim_number"]
            coords = block["coordinates"]

            name, dim, state, meaning = GEMATRIA[bn]
            mirror = 214 - bn
            mirror_name = GEMATRIA.get(mirror, ("~" + str(mirror), "", "", ""))[0]

            # Find onion layer
            layer_info = next((l for l in ONION_LAYERS if l[0] == bn), (bn, 0, "UNKNOWN"))

            lighthouse = GeoLighthouse(
                brahim_number=bn,
                name=name,
                dimension=dim,
                state=state,
                meaning=meaning,
                latitude=coords["lat"],
                longitude=coords["lon"],
                date=block["date"],
                onion_layer=layer_info[1],
                layer_type=layer_info[2],
                mirror=mirror,
                mirror_name=mirror_name,
            )

            self.add_lighthouse(lighthouse)

        # Establish connections
        self._build_connections()

    def _build_connections(self):
        """Build onion network connections between lighthouses."""
        # Each lighthouse connects to:
        # 1. Its mirror pair
        # 2. Adjacent layers
        # 3. The CENTER (107)

        for bn, lh in self.lighthouses.items():
            connections = []

            # Connect to mirror
            if lh.mirror in self.lighthouses:
                connections.append(self.lighthouses[lh.mirror].node_id)

            # Connect to CENTER (all roads lead to 107)
            if bn != 107 and 107 in self.lighthouses:
                connections.append(self.lighthouses[107].node_id)

            # Connect to adjacent layers
            layer_order = [l[0] for l in ONION_LAYERS]
            try:
                idx = layer_order.index(bn)
                if idx > 0:
                    prev_bn = layer_order[idx - 1]
                    if prev_bn in self.lighthouses:
                        connections.append(self.lighthouses[prev_bn].node_id)
                if idx < len(layer_order) - 1:
                    next_bn = layer_order[idx + 1]
                    if next_bn in self.lighthouses:
                        connections.append(self.lighthouses[next_bn].node_id)
            except ValueError:
                pass

            lh.connections = list(set(connections))

    def route(self, from_bn: int, to_bn: int) -> Optional[OnionRoute]:
        """
        Route through the onion network.
        All routes pass through the CENTER (107).
        """
        if from_bn not in self.lighthouses or to_bn not in self.lighthouses:
            return None

        source = self.lighthouses[from_bn]
        dest = self.lighthouses[to_bn]
        center = self.lighthouses.get(107)

        # Build path: source -> center -> destination
        path = [source.node_id]
        layers = [source.onion_layer]

        if center and from_bn != 107 and to_bn != 107:
            path.append(center.node_id)
            layers.append(center.onion_layer)

        if to_bn != from_bn:
            path.append(dest.node_id)
            layers.append(dest.onion_layer)

        # Calculate distance
        total_dist = self._haversine(
            source.latitude, source.longitude,
            dest.latitude, dest.longitude
        )

        return OnionRoute(
            source=source.node_id,
            destination=dest.node_id,
            path=path,
            layers_traversed=layers,
            total_distance_km=total_dist,
            passes_through_center=(107 in [from_bn, to_bn] or center is not None)
        )

    def _haversine(self, lat1, lon1, lat2, lon2) -> float:
        """Calculate distance between two points in km."""
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
            math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        return 2 * R * math.asin(math.sqrt(a))

    def to_geojson(self) -> Dict:
        """Export entire universe as GeoJSON."""
        features = []

        # Add lighthouse points
        for lh in self.lighthouses.values():
            features.append(lh.to_geojson_feature())

        # Add connection lines
        added_connections = set()
        for lh in self.lighthouses.values():
            for conn_id in lh.connections:
                conn_bn = self.node_index.get(conn_id)
                if conn_bn and conn_bn in self.lighthouses:
                    conn_lh = self.lighthouses[conn_bn]

                    # Avoid duplicate lines
                    pair = tuple(sorted([lh.brahim_number, conn_bn]))
                    if pair not in added_connections:
                        added_connections.add(pair)

                        features.append({
                            "type": "Feature",
                            "geometry": {
                                "type": "LineString",
                                "coordinates": [
                                    [lh.longitude, lh.latitude],
                                    [conn_lh.longitude, conn_lh.latitude]
                                ]
                            },
                            "properties": {
                                "from": lh.brahim_number,
                                "to": conn_bn,
                                "from_name": lh.name,
                                "to_name": conn_lh.name,
                                "type": "onion_connection",
                                "sum": lh.brahim_number + conn_bn,
                                "is_mirror_pair": (lh.brahim_number + conn_bn == 214),
                            }
                        })

        return {
            "type": "FeatureCollection",
            "properties": {
                "name": "Brahim Onion Universe",
                "created": self.created_at,
                "center": 107,
                "sum_constant": 214,
                "total_lighthouses": len(self.lighthouses),
                "total_connections": len(added_connections),
            },
            "features": features
        }

    def generate_html_map(self) -> str:
        """Generate an HTML map with Leaflet.js."""
        geojson = json.dumps(self.to_geojson())

        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Brahim Onion Universe - Solar Geographic Map</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; background: #0a0a0a; }}
        #map {{ position: absolute; top: 0; bottom: 0; width: 100%; }}
        .lighthouse-label {{
            background: rgba(0,0,0,0.8);
            border: 1px solid #FFD700;
            border-radius: 4px;
            padding: 4px 8px;
            color: #FFD700;
            font-family: monospace;
            font-size: 12px;
            white-space: nowrap;
        }}
        .info-panel {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.9);
            border: 2px solid #FFD700;
            border-radius: 8px;
            padding: 15px;
            color: #FFD700;
            font-family: monospace;
            z-index: 1000;
            max-width: 300px;
        }}
        .info-panel h2 {{ margin-top: 0; }}
        .layer-legend {{
            position: absolute;
            bottom: 30px;
            left: 10px;
            background: rgba(0,0,0,0.9);
            border: 1px solid #FFD700;
            border-radius: 8px;
            padding: 10px;
            color: white;
            font-family: monospace;
            font-size: 11px;
            z-index: 1000;
        }}
        .layer-legend div {{ margin: 3px 0; }}
        .dot {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 5px; }}
    </style>
</head>
<body>
    <div id="map"></div>

    <div class="info-panel">
        <h2>BRAHIM ONION UNIVERSE</h2>
        <p>Infinite Lighthouse Network</p>
        <hr style="border-color: #FFD700;">
        <p>CENTER: 107 (CONVERGENCE)</p>
        <p>SUM: 214 (Mirror Constant)</p>
        <p>Lighthouses: {len(self.lighthouses)}</p>
        <hr style="border-color: #FFD700;">
        <p style="font-size: 10px;">All routes pass through the CENTER.<br>
        Mirror pairs sum to 214.</p>
    </div>

    <div class="layer-legend">
        <div><span class="dot" style="background: #FFD700;"></span> CORE (107)</div>
        <div><span class="dot" style="background: #9932CC;"></span> EXOTIC (Inner)</div>
        <div><span class="dot" style="background: #00CED1;"></span> NORMAL (Outer)</div>
        <div style="margin-top: 8px; border-top: 1px solid #444; padding-top: 5px;">
            <span style="color: #FF6B6B;">---</span> Mirror Pair (=214)
        </div>
    </div>

    <script>
        var map = L.map('map').setView([40.5, -2.0], 6);

        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: 'Brahim Onion Universe',
            subdomains: 'abcd',
            maxZoom: 19
        }}).addTo(map);

        var geojsonData = {geojson};

        // Add connections first (so they're behind points)
        L.geoJSON(geojsonData, {{
            filter: function(feature) {{
                return feature.geometry.type === 'LineString';
            }},
            style: function(feature) {{
                var isMirror = feature.properties.is_mirror_pair;
                return {{
                    color: isMirror ? '#FF6B6B' : '#444444',
                    weight: isMirror ? 2 : 1,
                    opacity: isMirror ? 0.8 : 0.4,
                    dashArray: isMirror ? null : '5, 5'
                }};
            }}
        }}).addTo(map);

        // Add lighthouse points
        L.geoJSON(geojsonData, {{
            filter: function(feature) {{
                return feature.geometry.type === 'Point';
            }},
            pointToLayer: function(feature, latlng) {{
                var props = feature.properties;
                var color = props.color;
                var radius = props.layer_type === 'CORE' ? 15 : 10;

                return L.circleMarker(latlng, {{
                    radius: radius,
                    fillColor: color,
                    color: '#FFD700',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                }});
            }},
            onEachFeature: function(feature, layer) {{
                var props = feature.properties;
                var popup = '<div class="lighthouse-label">' +
                    '<b>' + props.brahim_number + ' - ' + props.name + '</b><br>' +
                    'Dimension: ' + props.dimension + '<br>' +
                    'State: ' + props.state + '<br>' +
                    'Layer: ' + props.onion_layer + ' (' + props.layer_type + ')<br>' +
                    'Mirror: ' + props.mirror + '<br>' +
                    'Date: ' + props.date +
                    '</div>';
                layer.bindPopup(popup);

                // Add permanent label for important nodes
                if (props.layer_type === 'CORE') {{
                    layer.bindTooltip(props.brahim_number + ' CENTER', {{
                        permanent: true,
                        direction: 'top',
                        className: 'lighthouse-label'
                    }});
                }}
            }}
        }}).addTo(map);

        // Fit bounds to show all lighthouses
        var bounds = [];
        geojsonData.features.forEach(function(f) {{
            if (f.geometry.type === 'Point') {{
                bounds.push([f.geometry.coordinates[1], f.geometry.coordinates[0]]);
            }}
        }});
        if (bounds.length > 0) {{
            map.fitBounds(bounds, {{ padding: [50, 50] }});
        }}
    </script>
</body>
</html>'''
        return html

    def save_universe(self, output_dir: str = "data/brahim_universe"):
        """Save the universe to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save GeoJSON
        geojson_path = output_path / "brahim_onion_universe.geojson"
        with open(geojson_path, 'w') as f:
            json.dump(self.to_geojson(), f, indent=2)

        # Save HTML map
        html_path = output_path / "brahim_onion_map.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_html_map())

        # Save network data
        network_data = {
            "name": "Brahim Onion Internet Online",
            "created": self.created_at,
            "structure": {
                "layers": len(ONION_LAYERS),
                "center": 107,
                "sum_constant": 214,
            },
            "lighthouses": [
                {
                    "brahim_number": lh.brahim_number,
                    "name": lh.name,
                    "node_id": lh.node_id,
                    "coordinates": {"lat": lh.latitude, "lon": lh.longitude},
                    "onion_layer": lh.onion_layer,
                    "layer_type": lh.layer_type,
                    "connections": lh.connections,
                    "mirror": lh.mirror,
                }
                for lh in self.lighthouses.values()
            ],
            "routing": {
                "principle": "All routes pass through CENTER (107)",
                "mirror_pairs": [
                    {"pair": [27, 187], "sum": 214},
                    {"pair": [42, 172], "sum": 214},
                    {"pair": [60, 154], "sum": 214},
                    {"pair": [75, 139], "sum": 214},
                    {"pair": [97, 117], "sum": 214},
                ],
            }
        }

        network_path = output_path / "brahim_onion_network.json"
        with open(network_path, 'w') as f:
            json.dump(network_data, f, indent=2)

        return {
            "geojson": str(geojson_path),
            "html_map": str(html_path),
            "network": str(network_path),
        }


# =============================================================================
# MAIN
# =============================================================================

def create_universe():
    """Create the Brahim Onion Universe from the blockchain."""
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("BRAHIM ONION INTERNET ONLINE")
    print("Creating Infinite Universe...")
    print("=" * 70)
    print()

    universe = BrahimOnionUniverse()

    # Load from blockchain
    blockchain_path = "data/brahim_blockchain.json"
    try:
        universe.load_blockchain(blockchain_path)
        print(f"Loaded {len(universe.lighthouses)} lighthouses from blockchain")
    except FileNotFoundError:
        print(f"Blockchain not found at {blockchain_path}")
        print("Creating universe from default coordinates...")

        # Default coordinates from the blockchain analysis
        default_blocks = [
            (97,  "2023-06-23", 38.4687, -9.0359),
            (107, "2023-08-04", 38.6280, -8.4947),
            (117, "2023-09-21", 38.8101, -7.8762),
            (154, "2023-09-24", 38.8215, -7.8375),
            (187, "2023-10-02", 38.8518, -7.7344),
            (139, "2023-10-08", 38.8746, -7.6571),
            (172, "2023-10-23", 38.9315, -7.4638),
            (42,  "2023-11-22", 39.0453, -7.0772),
            (27,  "2023-12-06", 39.0984, -6.8968),
            (60,  "2025-06-06", 41.1771, 0.1647),
            (75,  "2026-05-19", 42.4934, 4.6361),
        ]

        for bn, date, lat, lon in default_blocks:
            name, dim, state, meaning = GEMATRIA[bn]
            mirror = 214 - bn
            mirror_name = GEMATRIA.get(mirror, ("~" + str(mirror), "", "", ""))[0]
            layer_info = next((l for l in ONION_LAYERS if l[0] == bn), (bn, 0, "UNKNOWN"))

            lh = GeoLighthouse(
                brahim_number=bn,
                name=name,
                dimension=dim,
                state=state,
                meaning=meaning,
                latitude=lat,
                longitude=lon,
                date=date,
                onion_layer=layer_info[1],
                layer_type=layer_info[2],
                mirror=mirror,
                mirror_name=mirror_name,
            )
            universe.add_lighthouse(lh)

        universe._build_connections()
        print(f"Created {len(universe.lighthouses)} lighthouses")

    print()

    # Display lighthouses
    print("LIGHTHOUSES IN THE UNIVERSE:")
    print("-" * 70)
    for bn in sorted(universe.lighthouses.keys()):
        lh = universe.lighthouses[bn]
        print(f"  {bn:>3} {lh.name:<14} Layer {lh.onion_layer:>2} ({lh.layer_type:<5}) @ ({lh.latitude:.4f}, {lh.longitude:.4f})")

    print()

    # Save universe
    paths = universe.save_universe()

    print("=" * 70)
    print("UNIVERSE CREATED")
    print("=" * 70)
    print()
    print(f"GeoJSON:  {paths['geojson']}")
    print(f"HTML Map: {paths['html_map']}")
    print(f"Network:  {paths['network']}")
    print()
    print("Open the HTML map in a browser to see the Lighthouse network.")
    print("=" * 70)

    return universe


if __name__ == "__main__":
    create_universe()
