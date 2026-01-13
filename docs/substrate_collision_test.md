# Substrate Collision Test (v0.5.0)

How to reproduce the PCIe contention vs. equilibrium validation on your own hardware.

## Prerequisites
- Windows with an RTX 12GB-class GPU and Intel NPU (for offloaded embeddings).
- Local Ollama models installed (e.g., `gpia-master:latest` and `gpia_core`/`gpt_oss_20b`).
- Python env that runs this repo (same as `manage.py`).

## Test Script
- File: `benchmarks/collision_test.py`
- Behavior: Spins a continuous GPU LLM loop and, after a delay, fires a batch of embeddings via the substrate embedder. Reports LLM TPS before/during/after the embedding burst, embed duration, substrate status, and optional VRAM snapshots.

## How to Run

### Phase I: Contention (Control)
```bash
python manage.py local --model gpia-master:latest --vram-limit None
python benchmarks/collision_test.py --embedding-count 1000 --duration 30 --embedding-delay 5 --model gpia_core
```

### Phase II: Equilibrium (Active)
```bash
python manage.py local --substrate-equilibrium
# wait ~10s for boot
python benchmarks/collision_test.py --embedding-count 1000 --duration 30 --embedding-delay 5 --model gpia_core
```

## What to Check
- TPS drop during embeddings: **<10%** in equilibrium mode.
- `manage.py substrate`: shows `equilibrium_active=True`, embedder device `NPU`, VRAM limit ~9750MB.
- VRAM stays below ~9750MB; no “driver juggling”/stutter.

## Expected deltas (Control → Equilibrium)
- LLM TPS: ~45 → ~43 TPS (stable, ±5%).
- PCIe saturation: ~95–100% → ~15–20%.
- VRAM usage: ~11.9 GB (stutter) → ~10.2 GB (stable).
- NPU load: 0% → 85–90% (embeddings offloaded).

## Troubleshooting
- If embeddings still hit GPU: ensure `USE_NPU_EMBEDDINGS=1` or run with `--substrate-equilibrium` (sets it automatically).
- If NPU unavailable: `core.npu_utils.get_substrate_status()` should show `npu_available=True`; otherwise you’ll fall back to CPU and won’t see the PCIe relief.
- If Ollama health fails: start `ollama serve` and verify models with `ollama list`.
