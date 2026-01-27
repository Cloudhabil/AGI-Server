#!/usr/bin/env python3
"""
GPIA-PIO Bridge: Ignorance-Aware Cognition
==========================================

Connects GPIA's 12-wavelength cognitive pipeline to PIO's ignorance cartography.

THE MAPPING:
    Each GPIA wavelength flows through a PIO dimension, gaining:
    - Ignorance measurement (what we cannot see at this stage)
    - Confidence scoring (how much to trust this wavelength's output)
    - Boundary detection (are we at the edge of knowledge?)

WAVELENGTH → DIMENSION MAPPING:
    W1  Zero-Point      → D1  Perception    (initial awareness)
    W2  Prime Directive → D2  Attention     (focus on target)
    W3  Stochastic      → D3  Security      (validate input)
    W4  Density         → D4  Stability     (maintain balance)
    W5  Metatron        → D5  Compression   (project to sphere)
    W6  Synaptic        → D6  Harmony       (find resonance)
    W7  Generative      → D7  Reasoning     (propose solutions)
    W8  Theta Wave      → D8  Prediction    (predict correction)
    W9  Homeostatic     → D9  Creativity    (adapt weights)
    W10 Endurance       → D10 Wisdom        (validate convergence)
    W11 Hephaestus      → D11 Integration   (forge safety)
    W12 Crystallize     → D12 Unification   (persist state)

THE INSIGHT:
    GPIA processes information. PIO tracks what GPIA cannot see.
    Together: cognition + ignorance = calibrated intelligence.

Author: Elias Oulad Brahim
Version: 1.0.0
Date: 2026-01-27
"""

import logging
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from core.pio import (
    PIOWithIgnorance,
    IgnoranceState,
    IgnoranceAccumulator,
    IgnoranceReport,
    Dimension,
    DARK_SECTOR_RATIOS,
    BETA,
    EPSILON,
    PHI,
)

logger = logging.getLogger("gpia_pio_bridge")


# =============================================================================
# WAVELENGTH-DIMENSION MAPPING
# =============================================================================

class Wavelength(Enum):
    """The 12 GPIA wavelengths mapped to PIO dimensions."""

    # (wavelength_id, dimension_n, gpia_name, pio_domain)
    W1  = (1,  1,  "Zero-Point",      "Perception")
    W2  = (2,  2,  "Prime Directive", "Attention")
    W3  = (3,  3,  "Stochastic",      "Security")
    W4  = (4,  4,  "Density",         "Stability")
    W5  = (5,  5,  "Metatron",        "Compression")
    W6  = (6,  6,  "Synaptic",        "Harmony")
    W7  = (7,  7,  "Generative",      "Reasoning")
    W8  = (8,  8,  "Theta Wave",      "Prediction")
    W9  = (9,  9,  "Homeostatic",     "Creativity")
    W10 = (10, 10, "Endurance",       "Wisdom")
    W11 = (11, 11, "Hephaestus",      "Integration")
    W12 = (12, 12, "Crystallize",     "Unification")

    def __init__(self, wid: int, dim: int, gpia_name: str, pio_domain: str):
        self.wid = wid
        self.dim = dim
        self.gpia_name = gpia_name
        self.pio_domain = pio_domain

    @property
    def dark_ratio(self) -> float:
        """Dark sector ratio for this wavelength's dimension."""
        return DARK_SECTOR_RATIOS.get(self.dim, 0.164)

    @classmethod
    def from_dimension(cls, dim: int) -> 'Wavelength':
        """Get wavelength by dimension number."""
        for w in cls:
            if w.dim == dim:
                return w
        raise ValueError(f"No wavelength for dimension {dim}")


# =============================================================================
# WAVELENGTH IGNORANCE STATE
# =============================================================================

@dataclass
class WavelengthIgnorance:
    """
    Ignorance state for a specific wavelength.

    Extends IgnoranceState with wavelength-specific information.
    """
    wavelength: Wavelength
    ignorance: IgnoranceState

    # Wavelength-specific metrics
    input_entropy: float = 0.0      # Entropy of input to this wavelength
    output_variance: float = 0.0    # Variance of output from this wavelength
    processing_confidence: float = 1.0  # Confidence in this wavelength's processing

    @property
    def should_skip(self) -> bool:
        """Should this wavelength be skipped due to high ignorance?"""
        return self.ignorance.confidence < 0.3

    @property
    def needs_human(self) -> bool:
        """Does this wavelength need human intervention?"""
        return self.ignorance.is_at_boundary and self.ignorance.boundary_type == "n4"

    @property
    def summary(self) -> str:
        """One-line summary."""
        conf = self.processing_confidence * self.ignorance.confidence
        status = "[!]" if self.ignorance.is_at_boundary else "[ok]"
        return (f"W{self.wavelength.wid:2} {self.wavelength.gpia_name:15} -> "
                f"D{self.wavelength.dim:2} {self.wavelength.pio_domain:12} "
                f"[conf={conf:.0%}] {status}")


@dataclass
class PipelineIgnorance:
    """
    Ignorance state for the entire GPIA pipeline.

    Tracks ignorance across all 12 wavelengths.
    """
    wavelength_states: List[WavelengthIgnorance] = field(default_factory=list)

    def add(self, state: WavelengthIgnorance):
        """Add wavelength ignorance state."""
        self.wavelength_states.append(state)

    @property
    def total_ignorance(self) -> float:
        """Total ignorance across pipeline."""
        if not self.wavelength_states:
            return 0.0
        return sum(w.ignorance.total_ignorance for w in self.wavelength_states)

    @property
    def mean_confidence(self) -> float:
        """Mean confidence across pipeline."""
        if not self.wavelength_states:
            return 1.0
        return sum(w.ignorance.confidence for w in self.wavelength_states) / len(self.wavelength_states)

    @property
    def bottleneck(self) -> Optional[WavelengthIgnorance]:
        """Wavelength with lowest confidence (the bottleneck)."""
        if not self.wavelength_states:
            return None
        return min(self.wavelength_states, key=lambda w: w.ignorance.confidence)

    @property
    def boundary_wavelengths(self) -> List[WavelengthIgnorance]:
        """Wavelengths at boundaries."""
        return [w for w in self.wavelength_states if w.ignorance.is_at_boundary]

    def get_routing_recommendation(self) -> Dict[str, Any]:
        """Get recommendation for pipeline routing."""
        if not self.wavelength_states:
            return {"action": "proceed", "confidence": 1.0}

        bottleneck = self.bottleneck
        boundaries = self.boundary_wavelengths

        if bottleneck and bottleneck.ignorance.confidence < 0.3:
            return {
                "action": "caution",
                "reason": f"Low confidence at W{bottleneck.wavelength.wid} ({bottleneck.wavelength.gpia_name})",
                "confidence": bottleneck.ignorance.confidence,
                "recommendation": "Consider human review"
            }

        if boundaries:
            return {
                "action": "alert",
                "reason": f"{len(boundaries)} wavelengths at boundaries",
                "wavelengths": [w.wavelength.gpia_name for w in boundaries],
                "confidence": self.mean_confidence,
                "recommendation": "Proceed with caution"
            }

        return {
            "action": "proceed",
            "confidence": self.mean_confidence,
            "recommendation": "Pipeline clear"
        }

    def summary(self) -> str:
        """Full pipeline summary."""
        lines = ["GPIA-PIO Pipeline Ignorance:", "=" * 50]
        for ws in self.wavelength_states:
            lines.append(ws.summary)
        lines.append("=" * 50)
        lines.append(f"Total Ignorance: {self.total_ignorance:.4f}")
        lines.append(f"Mean Confidence: {self.mean_confidence:.1%}")
        if self.bottleneck:
            lines.append(f"Bottleneck: W{self.bottleneck.wavelength.wid} ({self.bottleneck.wavelength.gpia_name})")
        rec = self.get_routing_recommendation()
        lines.append(f"Recommendation: {rec['action'].upper()} - {rec.get('recommendation', '')}")
        return "\n".join(lines)


# =============================================================================
# GPIA-PIO BRIDGE
# =============================================================================

class GPIAPIOBridge:
    """
    Bridge between GPIA's 12-wavelength pipeline and PIO's ignorance cartography.

    THE INTEGRATION:
        1. Each GPIA wavelength maps to a PIO dimension
        2. Before/after each wavelength, measure ignorance
        3. Accumulate ignorance through the pipeline
        4. Return both GPIA result and ignorance report

    Usage:
        from core.gpia_puddels import GPiaPuddelsGate
        from core.gpia_pio_bridge import GPIAPIOBridge

        gate = GPiaPuddelsGate()
        bridge = GPIAPIOBridge(gate)

        # Process with ignorance tracking
        result, ignorance = bridge.evaluate_with_ignorance("input text")

        print(ignorance.summary())
        print(f"Bottleneck: {ignorance.bottleneck.wavelength.gpia_name}")
    """

    def __init__(self, gpia_gate=None):
        """
        Initialize bridge.

        Args:
            gpia_gate: Optional GPiaPuddelsGate instance. If None, created on demand.
        """
        self.gpia_gate = gpia_gate
        self.pio = PIOWithIgnorance("GPIA-Bridge")
        self.pipeline_history: List[PipelineIgnorance] = []

    def _ensure_gate(self):
        """Ensure GPIA gate is initialized."""
        if self.gpia_gate is None:
            try:
                from core.gpia_puddels import GPiaPuddelsGate
                self.gpia_gate = GPiaPuddelsGate(
                    enable_learning=True,
                    enable_convergence=False,
                    auto_persist=False
                )
            except ImportError:
                logger.warning("Could not import GPiaPuddelsGate")
                return False
        return True

    def measure_wavelength_ignorance(
        self,
        wavelength: Wavelength,
        input_value: float,
        input_entropy: float = 0.0,
        output_variance: float = 0.0
    ) -> WavelengthIgnorance:
        """
        Measure ignorance at a specific wavelength.

        Args:
            wavelength: The wavelength being processed
            input_value: Normalized input value [0, 1]
            input_entropy: Entropy of input data
            output_variance: Variance of output

        Returns:
            WavelengthIgnorance with full measurement
        """
        # Use PIO to measure ignorance at this dimension
        ignorance = self.pio.measure_ignorance(input_value, wavelength.dim)

        # Calculate processing confidence based on wavelength characteristics
        # Higher wavelengths have more uncertainty, lower confidence
        base_confidence = 1.0 - wavelength.dark_ratio

        # Adjust for input entropy (high entropy = less predictable)
        entropy_factor = 1.0 / (1.0 + input_entropy)

        # Adjust for output variance (high variance = less stable)
        variance_factor = 1.0 / (1.0 + output_variance)

        processing_confidence = base_confidence * entropy_factor * variance_factor

        return WavelengthIgnorance(
            wavelength=wavelength,
            ignorance=ignorance,
            input_entropy=input_entropy,
            output_variance=output_variance,
            processing_confidence=processing_confidence
        )

    def trace_pipeline(
        self,
        embedding: np.ndarray,
        density: float,
        error_delta: float
    ) -> PipelineIgnorance:
        """
        Trace ignorance through the entire GPIA pipeline.

        Simulates the 12-wavelength flow, measuring ignorance at each stage.

        Args:
            embedding: The input embedding
            density: Calculated density
            error_delta: Error from target

        Returns:
            PipelineIgnorance with all wavelength states
        """
        pipeline = PipelineIgnorance()

        # Calculate input characteristics
        embedding_norm = np.linalg.norm(embedding) if embedding is not None else 0.0
        embedding_var = np.var(embedding) if embedding is not None else 0.0
        embedding_entropy = self._estimate_entropy(embedding) if embedding is not None else 0.0

        # Normalized values for PIO
        norm_density = min(1.0, max(0.001, density))
        norm_error = min(1.0, max(0.0, abs(error_delta)))

        # Trace each wavelength
        for w in Wavelength:
            # Input value varies by wavelength stage
            if w.wid <= 3:
                # Early wavelengths: use embedding characteristics
                input_val = min(1.0, embedding_norm / 10.0) if embedding_norm else 0.5
            elif w.wid <= 6:
                # Middle wavelengths: use density
                input_val = norm_density
            elif w.wid <= 9:
                # Correction wavelengths: use error
                input_val = max(0.001, 1.0 - norm_error)
            else:
                # Final wavelengths: use combined
                input_val = (norm_density + (1.0 - norm_error)) / 2

            # Measure ignorance
            wi = self.measure_wavelength_ignorance(
                wavelength=w,
                input_value=input_val,
                input_entropy=embedding_entropy * (w.wid / 12),  # Entropy accumulates
                output_variance=embedding_var * (w.wid / 12)     # Variance accumulates
            )

            pipeline.add(wi)

        return pipeline

    def _estimate_entropy(self, embedding: np.ndarray) -> float:
        """Estimate entropy of embedding."""
        if embedding is None or len(embedding) == 0:
            return 0.0

        # Normalize to probabilities
        abs_emb = np.abs(embedding) + 1e-10
        probs = abs_emb / np.sum(abs_emb)

        # Shannon entropy
        entropy = -np.sum(probs * np.log2(probs + 1e-10))

        # Normalize by max entropy
        max_entropy = np.log2(len(embedding))
        return entropy / max_entropy if max_entropy > 0 else 0.0

    def evaluate_with_ignorance(self, text: str) -> Tuple[Any, PipelineIgnorance]:
        """
        Evaluate text through GPIA with ignorance tracking.

        Args:
            text: Input text to evaluate

        Returns:
            Tuple of (GateResult, PipelineIgnorance)
        """
        if not self._ensure_gate():
            # Return mock result if gate unavailable
            pipeline = self._mock_pipeline_trace(text)
            return None, pipeline

        # Run GPIA evaluation
        result = self.gpia_gate.evaluate(text)

        # Extract values for ignorance tracing
        metadata = result.metadata
        density = metadata.get("density", 0.022)
        error_delta = metadata.get("error_delta", 0.0)

        # Get embedding if available
        embedding = None
        try:
            ingestor = self.gpia_gate.ingestor
            embedding = ingestor.ingest_stream(text)
        except:
            pass

        # Trace pipeline ignorance
        pipeline = self.trace_pipeline(embedding, density, error_delta)

        # Store in history
        self.pipeline_history.append(pipeline)

        return result, pipeline

    def _mock_pipeline_trace(self, text: str) -> PipelineIgnorance:
        """Generate mock pipeline trace when GPIA unavailable."""
        pipeline = PipelineIgnorance()

        # Use text characteristics
        text_len = len(text)
        norm_len = min(1.0, text_len / 1000)

        for w in Wavelength:
            wi = self.measure_wavelength_ignorance(
                wavelength=w,
                input_value=norm_len * (w.wid / 12),
                input_entropy=0.5,
                output_variance=0.1
            )
            pipeline.add(wi)

        return pipeline

    def get_confidence_for_wavelength(self, wavelength_id: int) -> float:
        """Get current confidence for a specific wavelength."""
        if not self.pipeline_history:
            return 1.0

        last_pipeline = self.pipeline_history[-1]
        for ws in last_pipeline.wavelength_states:
            if ws.wavelength.wid == wavelength_id:
                return ws.ignorance.confidence

        return 1.0

    def get_bottleneck_history(self) -> List[str]:
        """Get history of bottleneck wavelengths."""
        return [
            p.bottleneck.wavelength.gpia_name
            for p in self.pipeline_history
            if p.bottleneck
        ]

    def dashboard(self) -> str:
        """Generate ignorance dashboard."""
        if not self.pipeline_history:
            return "No pipeline history available."

        last = self.pipeline_history[-1]

        lines = [
            "=" * 60,
            "GPIA-PIO IGNORANCE DASHBOARD",
            "=" * 60,
            "",
            "WAVELENGTH CONFIDENCE MAP:",
            "-" * 60,
        ]

        for ws in last.wavelength_states:
            conf = ws.ignorance.confidence
            bar_len = int(conf * 30)
            bar = "█" * bar_len + "░" * (30 - bar_len)
            boundary = " [BOUNDARY]" if ws.ignorance.is_at_boundary else ""
            lines.append(
                f"W{ws.wavelength.wid:2} {ws.wavelength.gpia_name:15} |{bar}| "
                f"{conf:.0%}{boundary}"
            )

        lines.extend([
            "",
            "-" * 60,
            f"Total Pipelines:    {len(self.pipeline_history)}",
            f"Mean Confidence:    {last.mean_confidence:.1%}",
            f"Total Ignorance:    {last.total_ignorance:.4f}",
            f"Bottleneck:         W{last.bottleneck.wavelength.wid} ({last.bottleneck.wavelength.gpia_name})" if last.bottleneck else "None",
            "",
        ])

        rec = last.get_routing_recommendation()
        lines.extend([
            "RECOMMENDATION:",
            f"  Action: {rec['action'].upper()}",
            f"  {rec.get('recommendation', '')}",
            "=" * 60,
        ])

        return "\n".join(lines)


# =============================================================================
# IGNORANCE-AWARE GPIA GATE
# =============================================================================

class IgnoranceAwareGate:
    """
    GPIA Gate with built-in ignorance awareness.

    Wraps GPiaPuddelsGate with automatic ignorance tracking and
    confidence-based routing.

    Usage:
        gate = IgnoranceAwareGate()

        result = gate.evaluate("input text")

        print(f"Safe: {result.safe}")
        print(f"Confidence: {result.confidence:.1%}")
        print(f"Bottleneck: {result.bottleneck}")

        if result.needs_human:
            print("Human review recommended!")
    """

    def __init__(self, **gpia_kwargs):
        """
        Initialize ignorance-aware gate.

        Args:
            **gpia_kwargs: Arguments passed to GPiaPuddelsGate
        """
        self.bridge = GPIAPIOBridge()
        self.gpia_kwargs = gpia_kwargs
        self._gate_initialized = False

    def _ensure_initialized(self):
        """Initialize GPIA gate on first use."""
        if not self._gate_initialized:
            try:
                from core.gpia_puddels import GPiaPuddelsGate
                self.bridge.gpia_gate = GPiaPuddelsGate(**self.gpia_kwargs)
                self._gate_initialized = True
            except ImportError:
                logger.warning("GPiaPuddelsGate not available")

    def evaluate(self, text: str) -> 'IgnoranceAwareResult':
        """
        Evaluate with ignorance awareness.

        Args:
            text: Input text

        Returns:
            IgnoranceAwareResult with confidence and recommendations
        """
        self._ensure_initialized()

        gpia_result, pipeline = self.bridge.evaluate_with_ignorance(text)

        return IgnoranceAwareResult(
            gpia_result=gpia_result,
            pipeline=pipeline,
            text=text
        )

    def dashboard(self) -> str:
        """Get ignorance dashboard."""
        return self.bridge.dashboard()


@dataclass
class IgnoranceAwareResult:
    """Result from ignorance-aware evaluation."""
    gpia_result: Any  # GateResult or None
    pipeline: PipelineIgnorance
    text: str

    @property
    def safe(self) -> bool:
        """Is the result safe?"""
        if self.gpia_result:
            return self.gpia_result.safe
        return self.confidence > 0.5

    @property
    def confidence(self) -> float:
        """Overall confidence in result."""
        return self.pipeline.mean_confidence

    @property
    def bottleneck(self) -> Optional[str]:
        """Name of bottleneck wavelength."""
        b = self.pipeline.bottleneck
        return b.wavelength.gpia_name if b else None

    @property
    def bottleneck_confidence(self) -> float:
        """Confidence at bottleneck."""
        b = self.pipeline.bottleneck
        return b.ignorance.confidence if b else 1.0

    @property
    def needs_human(self) -> bool:
        """Does this need human review?"""
        return self.bottleneck_confidence < 0.3 or any(
            ws.needs_human for ws in self.pipeline.wavelength_states
        )

    @property
    def recommendation(self) -> Dict[str, Any]:
        """Get routing recommendation."""
        return self.pipeline.get_routing_recommendation()

    def summary(self) -> str:
        """Summary of result."""
        lines = [
            f"Text: {self.text[:50]}...",
            f"Safe: {self.safe}",
            f"Confidence: {self.confidence:.1%}",
            f"Bottleneck: {self.bottleneck} ({self.bottleneck_confidence:.1%})",
            f"Needs Human: {self.needs_human}",
            f"Recommendation: {self.recommendation['action'].upper()}"
        ]
        return "\n".join(lines)


# =============================================================================
# DEMO
# =============================================================================

def demo():
    """Demonstrate GPIA-PIO bridge."""
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print("GPIA-PIO BRIDGE DEMONSTRATION")
    print("Ignorance-Aware Cognition")
    print("=" * 60)
    print()

    # Create bridge (without full GPIA for demo)
    bridge = GPIAPIOBridge()

    # Simulate multiple evaluations
    print("Simulating 3 pipeline evaluations...")
    print()

    test_cases = [
        ("Normal query about weather", 0.022, 0.001),
        ("Complex reasoning task", 0.035, 0.015),
        ("Edge case near boundaries", 0.089, 0.067),
    ]

    for i, (desc, density, error) in enumerate(test_cases, 1):
        print(f"--- Evaluation {i}: {desc} ---")
        embedding = np.random.randn(384).astype(np.float32)
        pipeline = bridge.trace_pipeline(embedding, density, error)
        bridge.pipeline_history.append(pipeline)

        rec = pipeline.get_routing_recommendation()
        print(f"  Density: {density:.3f}, Error: {error:.3f}")
        print(f"  Confidence: {pipeline.mean_confidence:.1%}")
        print(f"  Bottleneck: W{pipeline.bottleneck.wavelength.wid} ({pipeline.bottleneck.wavelength.gpia_name})")
        print(f"  Action: {rec['action'].upper()}")
        print()

    print("=" * 60)
    print("FINAL DASHBOARD")
    print("=" * 60)
    print()
    print(bridge.dashboard())

    # Show wavelength mapping
    print()
    print("=" * 60)
    print("WAVELENGTH -> DIMENSION MAPPING")
    print("=" * 60)
    print()
    print("GPIA Wavelength        PIO Dimension       Dark Ratio")
    print("-" * 60)
    for w in Wavelength:
        print(f"W{w.wid:2} {w.gpia_name:15}  D{w.dim:2} {w.pio_domain:12}  {w.dark_ratio:.1%}")
    print()
    print("=" * 60)
    print()
    print("THE INSIGHT:")
    print("  GPIA processes information through 12 wavelengths.")
    print("  PIO tracks what GPIA cannot see at each wavelength.")
    print("  Together: cognition + ignorance = calibrated intelligence.")
    print()
    print("=" * 60)


if __name__ == "__main__":
    demo()
