"""
Gradient Checkpointing Verification Script
==========================================
EU AI Act Compliance Evidence - Memory Optimization Proof

This script generates verifiable evidence that gradient checkpointing
reduces memory usage during model training as claimed.

Artifact ID: GPAI-CKPT-001
Version: 1.0.0
Date: 2024-12-30
"""

import torch
import torch.nn as nn
from torch.utils.checkpoint import checkpoint
import json
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class MemoryMeasurement:
    """Single memory measurement result."""
    condition: str
    peak_memory_mb: float
    allocated_memory_mb: float
    reserved_memory_mb: float
    forward_time_ms: float
    backward_time_ms: float
    total_time_ms: float


@dataclass
class CheckpointingReport:
    """Complete checkpointing verification report."""
    artifact_id: str
    version: str
    timestamp: str
    device_info: Dict[str, Any]
    model_config: Dict[str, Any]
    test_config: Dict[str, Any]
    measurements: List[Dict[str, Any]]
    comparison: Dict[str, Any]
    conclusion: Dict[str, Any]


class SimpleTransformerBlock(nn.Module):
    """Minimal transformer block for memory testing."""

    def __init__(self, hidden_size: int, num_heads: int = None):
        super().__init__()
        # Auto-select num_heads to be divisible by hidden_size
        if num_heads is None:
            for h in [12, 8, 4, 2, 1]:
                if hidden_size % h == 0:
                    num_heads = h
                    break
        self.attn = nn.MultiheadAttention(hidden_size, num_heads, batch_first=True)
        self.feed_forward = nn.Sequential(
            nn.Linear(hidden_size, hidden_size * 4),
            nn.GELU(),
            nn.Linear(hidden_size * 4, hidden_size)
        )
        self.norm1 = nn.LayerNorm(hidden_size)
        self.norm2 = nn.LayerNorm(hidden_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Self-attention with residual
        normed = self.norm1(x)
        attn_out, _ = self.attn(normed, normed, normed)
        x = x + attn_out
        # Feed-forward with residual
        x = x + self.feed_forward(self.norm2(x))
        return x


class TestModel(nn.Module):
    """Test model with configurable gradient checkpointing."""

    def __init__(
        self,
        num_layers: int = 12,
        hidden_size: int = 768,
        num_heads: int = None,
        use_gradient_checkpointing: bool = True
    ):
        super().__init__()
        self.use_gradient_checkpointing = use_gradient_checkpointing
        self.layers = nn.ModuleList([
            SimpleTransformerBlock(hidden_size, num_heads)
            for _ in range(num_layers)
        ])
        self.final_proj = nn.Linear(hidden_size, hidden_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for layer in self.layers:
            if self.use_gradient_checkpointing and self.training:
                # EVIDENCE: Gradient checkpointing applied here
                x = checkpoint(layer, x, use_reentrant=False)
            else:
                x = layer(x)
        return self.final_proj(x)


def get_device_info() -> Dict[str, Any]:
    """Gather GPU device information."""
    if not torch.cuda.is_available():
        return {"type": "CPU", "name": "N/A", "memory_total_gb": 0}

    device = torch.cuda.current_device()
    props = torch.cuda.get_device_properties(device)

    return {
        "type": "CUDA",
        "name": props.name,
        "compute_capability": f"{props.major}.{props.minor}",
        "memory_total_gb": round(props.total_memory / (1024**3), 2),
        "cuda_version": torch.version.cuda,
        "pytorch_version": torch.__version__,
    }


def measure_memory(
    model: nn.Module,
    input_data: torch.Tensor,
    condition_name: str
) -> MemoryMeasurement:
    """
    Measure peak memory usage during forward + backward pass.

    This is the core evidence-generating function that proves
    gradient checkpointing reduces memory consumption.
    """
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()

    model.train()

    # Forward pass timing
    start_forward = time.perf_counter()
    output = model(input_data)
    loss = output.sum()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    forward_time = (time.perf_counter() - start_forward) * 1000

    # Backward pass timing
    start_backward = time.perf_counter()
    loss.backward()
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    backward_time = (time.perf_counter() - start_backward) * 1000

    # Memory measurements
    if torch.cuda.is_available():
        peak_memory = torch.cuda.max_memory_allocated() / (1024**2)
        allocated = torch.cuda.memory_allocated() / (1024**2)
        reserved = torch.cuda.memory_reserved() / (1024**2)
    else:
        peak_memory = allocated = reserved = 0.0

    # Clear gradients for next measurement
    model.zero_grad()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return MemoryMeasurement(
        condition=condition_name,
        peak_memory_mb=round(peak_memory, 2),
        allocated_memory_mb=round(allocated, 2),
        reserved_memory_mb=round(reserved, 2),
        forward_time_ms=round(forward_time, 2),
        backward_time_ms=round(backward_time, 2),
        total_time_ms=round(forward_time + backward_time, 2),
    )


def run_verification(
    num_layers: int = 12,
    hidden_size: int = 768,
    batch_size: int = 8,
    seq_length: int = 512,
    num_runs: int = 3,
    output_dir: Optional[Path] = None
) -> CheckpointingReport:
    """
    Run complete checkpointing verification and generate report.

    This function:
    1. Creates identical models with/without checkpointing
    2. Runs multiple forward+backward passes
    3. Measures peak memory for each configuration
    4. Computes memory savings percentage
    5. Generates compliance evidence report
    """
    print("=" * 70)
    print("GRADIENT CHECKPOINTING VERIFICATION")
    print("=" * 70)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device_info = get_device_info()

    print(f"\nDevice: {device_info.get('name', 'CPU')}")
    print(f"Total VRAM: {device_info.get('memory_total_gb', 'N/A')} GB")

    # Test configuration
    test_config = {
        "batch_size": batch_size,
        "sequence_length": seq_length,
        "num_runs": num_runs,
        "dtype": "float32",
    }

    model_config = {
        "num_layers": num_layers,
        "hidden_size": hidden_size,
        "num_heads": 12,
        "intermediate_size": hidden_size * 4,
    }

    print(f"\nModel: {num_layers} layers, {hidden_size} hidden dim")
    print(f"Input: batch={batch_size}, seq={seq_length}")
    print(f"Runs per config: {num_runs}")

    measurements = []

    # Create test input
    input_data = torch.randn(batch_size, seq_length, hidden_size, device=device)

    # =========================================================================
    # TEST 1: WITHOUT Gradient Checkpointing (Standard)
    # =========================================================================
    print("\n" + "-" * 50)
    print("Testing WITHOUT gradient checkpointing...")

    model_standard = TestModel(
        num_layers=num_layers,
        hidden_size=hidden_size,
        use_gradient_checkpointing=False
    ).to(device)

    standard_measurements = []
    for run in range(num_runs):
        m = measure_memory(model_standard, input_data, f"standard_run_{run+1}")
        standard_measurements.append(m)
        print(f"  Run {run+1}: Peak={m.peak_memory_mb:.1f}MB, Time={m.total_time_ms:.1f}ms")

    # Average standard results
    avg_standard = MemoryMeasurement(
        condition="WITHOUT_CHECKPOINTING",
        peak_memory_mb=round(sum(m.peak_memory_mb for m in standard_measurements) / num_runs, 2),
        allocated_memory_mb=round(sum(m.allocated_memory_mb for m in standard_measurements) / num_runs, 2),
        reserved_memory_mb=round(sum(m.reserved_memory_mb for m in standard_measurements) / num_runs, 2),
        forward_time_ms=round(sum(m.forward_time_ms for m in standard_measurements) / num_runs, 2),
        backward_time_ms=round(sum(m.backward_time_ms for m in standard_measurements) / num_runs, 2),
        total_time_ms=round(sum(m.total_time_ms for m in standard_measurements) / num_runs, 2),
    )
    measurements.append(asdict(avg_standard))

    # Clean up
    del model_standard
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # =========================================================================
    # TEST 2: WITH Gradient Checkpointing
    # =========================================================================
    print("\n" + "-" * 50)
    print("Testing WITH gradient checkpointing...")

    model_checkpoint = TestModel(
        num_layers=num_layers,
        hidden_size=hidden_size,
        use_gradient_checkpointing=True
    ).to(device)

    checkpoint_measurements = []
    for run in range(num_runs):
        m = measure_memory(model_checkpoint, input_data, f"checkpoint_run_{run+1}")
        checkpoint_measurements.append(m)
        print(f"  Run {run+1}: Peak={m.peak_memory_mb:.1f}MB, Time={m.total_time_ms:.1f}ms")

    # Average checkpoint results
    avg_checkpoint = MemoryMeasurement(
        condition="WITH_CHECKPOINTING",
        peak_memory_mb=round(sum(m.peak_memory_mb for m in checkpoint_measurements) / num_runs, 2),
        allocated_memory_mb=round(sum(m.allocated_memory_mb for m in checkpoint_measurements) / num_runs, 2),
        reserved_memory_mb=round(sum(m.reserved_memory_mb for m in checkpoint_measurements) / num_runs, 2),
        forward_time_ms=round(sum(m.forward_time_ms for m in checkpoint_measurements) / num_runs, 2),
        backward_time_ms=round(sum(m.backward_time_ms for m in checkpoint_measurements) / num_runs, 2),
        total_time_ms=round(sum(m.total_time_ms for m in checkpoint_measurements) / num_runs, 2),
    )
    measurements.append(asdict(avg_checkpoint))

    # Clean up
    del model_checkpoint
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    # =========================================================================
    # COMPUTE COMPARISON
    # =========================================================================
    if avg_standard.peak_memory_mb > 0:
        memory_savings_pct = round(
            100 * (1 - avg_checkpoint.peak_memory_mb / avg_standard.peak_memory_mb), 1
        )
        compute_overhead_pct = round(
            100 * (avg_checkpoint.total_time_ms / avg_standard.total_time_ms - 1), 1
        )
    else:
        memory_savings_pct = 0.0
        compute_overhead_pct = 0.0

    comparison = {
        "standard_peak_memory_mb": avg_standard.peak_memory_mb,
        "checkpoint_peak_memory_mb": avg_checkpoint.peak_memory_mb,
        "memory_savings_mb": round(avg_standard.peak_memory_mb - avg_checkpoint.peak_memory_mb, 2),
        "memory_savings_percent": memory_savings_pct,
        "standard_time_ms": avg_standard.total_time_ms,
        "checkpoint_time_ms": avg_checkpoint.total_time_ms,
        "compute_overhead_percent": compute_overhead_pct,
    }

    # =========================================================================
    # CONCLUSION
    # =========================================================================
    checkpointing_effective = memory_savings_pct >= 30  # At least 30% savings

    conclusion = {
        "checkpointing_effective": checkpointing_effective,
        "memory_reduction_achieved": f"{memory_savings_pct}%",
        "expected_range": "50-70%",
        "compute_tradeoff": f"{compute_overhead_pct}% additional time",
        "recommendation": (
            "PASS - Gradient checkpointing is functioning as expected"
            if checkpointing_effective else
            "REVIEW - Memory savings below expected threshold"
        ),
        "compliance_status": "COMPLIANT" if checkpointing_effective else "REQUIRES_REVIEW",
    }

    # =========================================================================
    # GENERATE REPORT
    # =========================================================================
    report = CheckpointingReport(
        artifact_id="GPAI-CKPT-001",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat() + "Z",
        device_info=device_info,
        model_config=model_config,
        test_config=test_config,
        measurements=measurements,
        comparison=comparison,
        conclusion=conclusion,
    )

    # Print summary
    print("\n" + "=" * 70)
    print("VERIFICATION RESULTS")
    print("=" * 70)
    print(f"\nPeak Memory (Standard):      {avg_standard.peak_memory_mb:>8.1f} MB")
    print(f"Peak Memory (Checkpointing): {avg_checkpoint.peak_memory_mb:>8.1f} MB")
    print(f"Memory Savings:              {memory_savings_pct:>8.1f} %")
    print(f"Compute Overhead:            {compute_overhead_pct:>8.1f} %")
    print(f"\nStatus: {conclusion['compliance_status']}")
    print(f"Recommendation: {conclusion['recommendation']}")

    # Save report
    if output_dir is None:
        output_dir = Path(__file__).parent / "evidence"
    output_dir.mkdir(parents=True, exist_ok=True)

    # JSON report
    report_path = output_dir / "checkpointing_verification.json"
    with open(report_path, "w") as f:
        json.dump(asdict(report), f, indent=2)
    print(f"\nReport saved: {report_path}")

    # Human-readable log
    log_path = output_dir / "checkpointing_verification.log"
    with open(log_path, "w") as f:
        f.write("GRADIENT CHECKPOINTING VERIFICATION LOG\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Timestamp: {report.timestamp}\n")
        f.write(f"Device: {device_info.get('name', 'CPU')}\n")
        f.write(f"VRAM: {device_info.get('memory_total_gb', 'N/A')} GB\n\n")
        f.write(f"Model Configuration:\n")
        f.write(f"  Layers: {num_layers}\n")
        f.write(f"  Hidden Size: {hidden_size}\n")
        f.write(f"  Batch Size: {batch_size}\n")
        f.write(f"  Sequence Length: {seq_length}\n\n")
        f.write("RESULTS:\n")
        f.write("-" * 50 + "\n")
        f.write(f"Peak Memory (Standard):      {avg_standard.peak_memory_mb:>8.1f} MB\n")
        f.write(f"Peak Memory (Checkpointing): {avg_checkpoint.peak_memory_mb:>8.1f} MB\n")
        f.write(f"Memory Savings:              {memory_savings_pct:>8.1f} %\n")
        f.write(f"Compute Overhead:            {compute_overhead_pct:>8.1f} %\n\n")
        f.write(f"CONCLUSION: {conclusion['compliance_status']}\n")
        f.write(f"{conclusion['recommendation']}\n")
    print(f"Log saved: {log_path}")

    return report


if __name__ == "__main__":
    # Run with default parameters suitable for RTX 4070 SUPER (12GB)
    # Adjust batch_size and seq_length based on available VRAM

    import argparse
    parser = argparse.ArgumentParser(description="Verify gradient checkpointing memory savings")
    parser.add_argument("--layers", type=int, default=12, help="Number of transformer layers")
    parser.add_argument("--hidden", type=int, default=768, help="Hidden dimension size")
    parser.add_argument("--batch", type=int, default=8, help="Batch size")
    parser.add_argument("--seq", type=int, default=512, help="Sequence length")
    parser.add_argument("--runs", type=int, default=3, help="Number of runs per config")

    args = parser.parse_args()

    run_verification(
        num_layers=args.layers,
        hidden_size=args.hidden,
        batch_size=args.batch,
        seq_length=args.seq,
        num_runs=args.runs,
    )
