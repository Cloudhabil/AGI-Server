"""
Protocol Selector - PHI-bandwidth adaptation

Selects communication protocol based on the ratio of available bandwidth
to required bandwidth. Uses PHI-harmonic thresholds for protocol selection.

Protocol Selection Tiers (based on available_bw / required_bw ratio):
- ratio >= PHI^3 (~4.236): ULTRA - Maximum throughput protocol
- ratio >= PHI^2 (~2.618): HIGH - High-bandwidth protocol
- ratio >= PHI   (~1.618): STANDARD - Normal operation protocol
- ratio >= 1.0:            EFFICIENT - Bandwidth-conserving protocol
- ratio >= 1/PHI (~0.618): MINIMAL - Minimal bandwidth protocol
- ratio < 1/PHI:           EMERGENCY - Emergency fallback protocol
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum, auto
import time

PHI = 1.618033988749895
SUM_CONSTANT = 214
D5_CAPACITY = 11
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]

# PHI-harmonic thresholds
PHI_CUBED = PHI ** 3      # ~4.236
PHI_SQUARED = PHI ** 2    # ~2.618
PHI_INVERSE = 1 / PHI     # ~0.618


class Protocol(Enum):
    """Communication protocols ordered by bandwidth requirements."""
    EMERGENCY = auto()    # Minimal survival mode
    MINIMAL = auto()      # Low bandwidth operation
    EFFICIENT = auto()    # Optimized for limited bandwidth
    STANDARD = auto()     # Normal operation
    HIGH = auto()         # High throughput
    ULTRA = auto()        # Maximum performance


@dataclass
class ProtocolSpec:
    """Specification for a communication protocol."""
    protocol: Protocol
    min_ratio: float
    compression_level: int  # 0-11 (D5 capacity)
    packet_size: int        # bytes
    retry_limit: int
    timeout_ms: int
    features: List[str] = field(default_factory=list)

    @property
    def efficiency_score(self) -> float:
        """Calculate efficiency based on compression and packet size."""
        return (self.compression_level / D5_CAPACITY) * PHI


@dataclass
class BandwidthState:
    """Current bandwidth state for protocol selection."""
    available_bw: float  # Mbps
    required_bw: float   # Mbps
    latency_ms: float = 0.0
    packet_loss: float = 0.0  # 0-1
    timestamp: float = field(default_factory=time.time)

    @property
    def ratio(self) -> float:
        """Calculate bandwidth ratio."""
        if self.required_bw <= 0:
            return float('inf')
        return self.available_bw / self.required_bw

    @property
    def phi_normalized_ratio(self) -> float:
        """Normalize ratio to PHI scale."""
        return self.ratio / PHI


class ProtocolSelector:
    """
    Selects optimal communication protocol based on PHI-bandwidth adaptation.

    The selector uses golden ratio thresholds to determine protocol tiers,
    ensuring harmonic transitions between bandwidth states.
    """

    def __init__(self):
        self.protocols: Dict[Protocol, ProtocolSpec] = {}
        self._initialize_protocols()
        self.selection_history: List[tuple] = []
        self.current_protocol: Optional[Protocol] = None

    def _initialize_protocols(self):
        """Initialize protocol specifications with PHI-harmonic parameters."""
        self.protocols = {
            Protocol.ULTRA: ProtocolSpec(
                protocol=Protocol.ULTRA,
                min_ratio=PHI_CUBED,
                compression_level=0,  # No compression needed
                packet_size=65536,    # Large packets
                retry_limit=1,
                timeout_ms=100,
                features=["parallel_streams", "predictive_cache", "zero_copy"]
            ),
            Protocol.HIGH: ProtocolSpec(
                protocol=Protocol.HIGH,
                min_ratio=PHI_SQUARED,
                compression_level=3,
                packet_size=32768,
                retry_limit=2,
                timeout_ms=250,
                features=["multi_channel", "adaptive_buffer"]
            ),
            Protocol.STANDARD: ProtocolSpec(
                protocol=Protocol.STANDARD,
                min_ratio=PHI,
                compression_level=5,
                packet_size=16384,
                retry_limit=3,
                timeout_ms=500,
                features=["flow_control", "error_correction"]
            ),
            Protocol.EFFICIENT: ProtocolSpec(
                protocol=Protocol.EFFICIENT,
                min_ratio=1.0,
                compression_level=8,
                packet_size=8192,
                retry_limit=4,
                timeout_ms=1000,
                features=["aggressive_compression", "dedup"]
            ),
            Protocol.MINIMAL: ProtocolSpec(
                protocol=Protocol.MINIMAL,
                min_ratio=PHI_INVERSE,
                compression_level=10,
                packet_size=2048,
                retry_limit=5,
                timeout_ms=2000,
                features=["priority_queue", "drop_non_essential"]
            ),
            Protocol.EMERGENCY: ProtocolSpec(
                protocol=Protocol.EMERGENCY,
                min_ratio=0.0,
                compression_level=11,  # Maximum compression (D5_CAPACITY)
                packet_size=512,
                retry_limit=10,
                timeout_ms=5000,
                features=["survival_mode", "essential_only", "store_forward"]
            ),
        }

    def select(self, state: BandwidthState) -> ProtocolSpec:
        """
        Select optimal protocol based on bandwidth state.

        Uses PHI-harmonic thresholds with hysteresis to prevent oscillation.
        """
        ratio = state.ratio

        # Apply packet loss penalty to ratio
        effective_ratio = ratio * (1 - state.packet_loss)

        # Select protocol based on effective ratio
        selected = Protocol.EMERGENCY
        for protocol in [Protocol.ULTRA, Protocol.HIGH, Protocol.STANDARD,
                         Protocol.EFFICIENT, Protocol.MINIMAL, Protocol.EMERGENCY]:
            spec = self.protocols[protocol]
            if effective_ratio >= spec.min_ratio:
                selected = protocol
                break

        # Apply hysteresis if already have a protocol
        if self.current_protocol:
            current_idx = list(Protocol).index(self.current_protocol)
            selected_idx = list(Protocol).index(selected)

            # Require stronger signal to upgrade (PHI-scaled hysteresis)
            if selected_idx < current_idx:  # Upgrading
                upgrade_threshold = self.protocols[selected].min_ratio * (1 + PHI_INVERSE/10)
                if effective_ratio < upgrade_threshold:
                    selected = self.current_protocol

        # Record selection
        self.current_protocol = selected
        self.selection_history.append((time.time(), state, selected))

        return self.protocols[selected]

    def select_from_bandwidth(self, available_bw: float, required_bw: float,
                               latency_ms: float = 0.0,
                               packet_loss: float = 0.0) -> ProtocolSpec:
        """Convenience method to select protocol from raw bandwidth values."""
        state = BandwidthState(
            available_bw=available_bw,
            required_bw=required_bw,
            latency_ms=latency_ms,
            packet_loss=packet_loss
        )
        return self.select(state)

    def get_threshold_info(self) -> Dict[str, Any]:
        """Get information about PHI-harmonic thresholds."""
        return {
            "phi": PHI,
            "phi_squared": PHI_SQUARED,
            "phi_cubed": PHI_CUBED,
            "phi_inverse": PHI_INVERSE,
            "thresholds": {
                p.name: self.protocols[p].min_ratio
                for p in Protocol
            }
        }

    def get_protocol_for_ratio(self, ratio: float) -> Protocol:
        """Get protocol name for a given ratio without state tracking."""
        for protocol in [Protocol.ULTRA, Protocol.HIGH, Protocol.STANDARD,
                         Protocol.EFFICIENT, Protocol.MINIMAL, Protocol.EMERGENCY]:
            if ratio >= self.protocols[protocol].min_ratio:
                return protocol
        return Protocol.EMERGENCY

    def estimate_throughput(self, spec: ProtocolSpec,
                            available_bw: float) -> float:
        """Estimate actual throughput for a protocol given available bandwidth."""
        # Compression boost factor based on D5 capacity
        compression_factor = 1 + (spec.compression_level / D5_CAPACITY) * PHI_INVERSE

        # Overhead reduction based on packet size
        overhead_factor = 1 - (512 / spec.packet_size) * 0.1

        return available_bw * compression_factor * overhead_factor


if __name__ == "__main__":
    print("=" * 60)
    print("ProtocolSelector - PHI-bandwidth Adaptation Test")
    print("=" * 60)

    selector = ProtocolSelector()

    # Display PHI thresholds
    print("\n[PHI-Harmonic Thresholds]")
    thresholds = selector.get_threshold_info()
    print(f"  PHI = {thresholds['phi']:.6f}")
    print(f"  PHI^2 = {thresholds['phi_squared']:.6f}")
    print(f"  PHI^3 = {thresholds['phi_cubed']:.6f}")
    print(f"  1/PHI = {thresholds['phi_inverse']:.6f}")

    print("\n[Protocol Thresholds]")
    for name, threshold in thresholds['thresholds'].items():
        print(f"  {name}: ratio >= {threshold:.3f}")

    # Test protocol selection
    print("\n[Protocol Selection Tests]")
    test_cases = [
        (100.0, 20.0, "Abundant bandwidth (5.0x)"),
        (50.0, 20.0, "Good bandwidth (2.5x)"),
        (35.0, 20.0, "Adequate bandwidth (1.75x)"),
        (20.0, 20.0, "Matched bandwidth (1.0x)"),
        (15.0, 20.0, "Limited bandwidth (0.75x)"),
        (10.0, 20.0, "Constrained bandwidth (0.5x)"),
        (5.0, 20.0, "Critical bandwidth (0.25x)"),
    ]

    for available, required, desc in test_cases:
        spec = selector.select_from_bandwidth(available, required)
        throughput = selector.estimate_throughput(spec, available)
        print(f"\n  {desc}")
        print(f"    Available: {available} Mbps, Required: {required} Mbps")
        print(f"    Ratio: {available/required:.3f}")
        print(f"    Selected: {spec.protocol.name}")
        print(f"    Compression: {spec.compression_level}/{D5_CAPACITY}")
        print(f"    Packet size: {spec.packet_size} bytes")
        print(f"    Est. throughput: {throughput:.2f} Mbps")

    # Test with packet loss
    print("\n[Packet Loss Impact Test]")
    for loss in [0.0, 0.1, 0.2, 0.3]:
        spec = selector.select_from_bandwidth(50.0, 20.0, packet_loss=loss)
        print(f"  Packet loss {loss:.0%}: {spec.protocol.name}")

    print("\n[Protocol Specifications]")
    for protocol, spec in selector.protocols.items():
        print(f"\n  {protocol.name}:")
        print(f"    Min ratio: {spec.min_ratio:.3f}")
        print(f"    Compression: {spec.compression_level}")
        print(f"    Packet size: {spec.packet_size}")
        print(f"    Features: {', '.join(spec.features)}")

    print("\n[Test Complete]")
