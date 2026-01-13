"""Utilities for running text embedding models via OpenVINO.

This module provides a light wrapper around the OpenVINO runtime to obtain
vector embeddings from text inputs. The heavy OpenVINO dependencies are only
imported when ``get_embeddings`` is first invoked so importing this module has
minimal side‑effects.

SUBSTRATE EQUILIBRIUM (v0.5.0):
When USE_NPU_EMBEDDINGS=1 or SUBSTRATE_EQUILIBRIUM=1, this module routes
embeddings through the Intel NPU's direct memory path, freeing the PCIe bus
for GPU LLM inference. This prevents the "traffic jam" when GPU spills into
shared memory.

Device Priority:
1. NPU (Intel AI Boost) - when equilibrium mode enabled (bypasses PCIe)
2. CPU - default fallback (preserves VRAM for LLM)
3. GPU - only if explicitly requested (consumes VRAM)
"""

from __future__ import annotations

import os
from typing import List, Any, Optional

import numpy as np

# Defer importing settings until first use
_settings = None

# Defer importing OpenVINO until first use so tests can mock it easily
Core: Any | None = None  # set in _lazy_init when available

# Lazy loaded globals
_core = None
_compiled_model = None
_output = None
_tokenizer = None
_core_ctor: Any | None = None
_npu_embedder = None  # Substrate equilibrium NPU embedder
_use_npu_backend = False


def _get_settings():
    """Lazy load settings to avoid circular imports."""
    global _settings
    if _settings is None:
        from core.settings import settings
        _settings = settings
    return _settings


def _check_npu_equilibrium() -> bool:
    """
    Check if NPU substrate equilibrium mode should be used.

    Returns True if:
    - USE_NPU_EMBEDDINGS=1, or
    - SUBSTRATE_EQUILIBRIUM=1, or
    - EMBEDDING_DEVICE=NPU
    """
    return (
        os.getenv("USE_NPU_EMBEDDINGS", "0") == "1" or
        os.getenv("SUBSTRATE_EQUILIBRIUM", "0") == "1" or
        os.getenv("EMBEDDING_DEVICE", "").upper() == "NPU"
    )


def _init_npu_backend() -> bool:
    """
    Initialize NPU backend for substrate equilibrium mode.

    Returns True if NPU backend is ready.
    """
    global _npu_embedder, _use_npu_backend

    if _npu_embedder is not None:
        return _use_npu_backend

    try:
        from core.npu_utils import NPUEmbedder, has_npu

        if not has_npu():
            print("[EMBEDDER] NPU not available, falling back to CPU")
            _use_npu_backend = False
            return False

        _npu_embedder = NPUEmbedder(device="NPU")
        if _npu_embedder.load_model():
            _use_npu_backend = True
            print(f"[EMBEDDER] NPU ACTIVATED: {_npu_embedder.backend_info}")
            print("[EMBEDDER] Embeddings now bypass PCIe bus (direct RAM path)")
            return True
        else:
            print("[EMBEDDER] NPU model load failed, falling back to CPU")
            _use_npu_backend = False
            return False

    except Exception as e:
        print(f"[EMBEDDER] NPU init failed: {e}, falling back to CPU")
        _use_npu_backend = False
        return False


def _lazy_init() -> None:
    global Core, _core_ctor
    """Initialise OpenVINO runtime and tokenizer on first use."""
    global _core, _compiled_model, _output, _tokenizer

    # SUBSTRATE EQUILIBRIUM: Check for NPU mode first
    if _check_npu_equilibrium():
        if _init_npu_backend():
            return  # NPU backend active, skip OpenVINO init

    if _compiled_model is not None and _core_ctor is Core:
        return

    settings = _get_settings()
    model_path = settings.OPENVINO_EMBEDDING_MODEL
    if not model_path:
        raise RuntimeError("OPENVINO_EMBEDDING_MODEL is not configured")

    # Import Core lazily so tests can patch sys.modules or oe.Core
    if Core is None:
        try:  # Prefer modern import path first
            from openvino import Core as OVCore  # type: ignore
        except Exception:
            try:  # Fallback to legacy path; may emit deprecation warning
                from openvino.runtime import Core as OVCore  # type: ignore
            except Exception:
                raise RuntimeError(
                    "OpenVINO runtime not available. Set it up locally to run models."
                )
        Core = OVCore

    from transformers import AutoTokenizer

    _core_ctor = Core
    _core = Core()

    # HARDWARE SOVEREIGNTY: Device selection
    # Default to CPU to preserve VRAM for LLM inference
    # NPU is handled by separate backend above
    device = "CPU"

    if settings.OPENVINO_EMBEDDING_MODEL_CPU:
        model_path = settings.OPENVINO_EMBEDDING_MODEL_CPU

    print(f"[EMBEDDER] Compiling model for {device}...")
    model = _core.read_model(model_path)
    _compiled_model = _core.compile_model(model, device_name=device)
    _output = _compiled_model.output(0)

    tokenizer_name = settings.OPENVINO_TOKENIZER or "sentence-transformers/all-MiniLM-L6-v2"
    _tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

    # Warm-up inference to avoid initial latency spikes
    warm_tokens = _tokenizer("warmup", return_tensors="np", padding=True, truncation=True)
    warm_inputs = {inp.any_name: warm_tokens.get(inp.any_name) for inp in _compiled_model.inputs}
    _compiled_model(warm_inputs)
    print(f"[EMBEDDER] Ready on {device}")


def get_embeddings(text: str) -> List[float]:
    """Return the embedding vector for ``text``.

    The vector is returned as a simple list of floats for ease of storage and
    transmission. The underlying OpenVINO runtime and tokenizer are initialised
    on first call and reused for subsequent invocations.

    SUBSTRATE EQUILIBRIUM (v0.5.0):
    When NPU mode is active, embeddings are routed through the Intel NPU's
    direct memory path, bypassing the PCIe bus used by GPU.
    """
    _lazy_init()

    # SUBSTRATE EQUILIBRIUM: Use NPU backend if active
    if _use_npu_backend and _npu_embedder is not None:
        embeddings = _npu_embedder.embed([text])
        return embeddings[0].tolist()

    # Standard OpenVINO path (CPU)
    assert _compiled_model is not None and _output is not None and _tokenizer is not None

    tokens = _tokenizer(text, return_tensors="np", padding=True, truncation=True)
    # OpenVINO models expect a dict of numpy arrays keyed by input tensor name.
    # ``_compiled_model.inputs`` provides the ordered inputs; we map them to the
    # tokeniser output.
    inputs = {inp.any_name: tokens.get(inp.any_name) for inp in _compiled_model.inputs}
    result = _compiled_model(inputs)[_output]
    array = np.array(result).squeeze(0)
    return array.tolist()


def get_embedder_status() -> dict:
    """
    Get current embedder status for diagnostics.

    Returns information about which backend is active.
    """
    _lazy_init()

    return {
        "npu_active": _use_npu_backend,
        "npu_embedder": _npu_embedder.backend_info if _npu_embedder else None,
        "openvino_compiled": _compiled_model is not None,
        "equilibrium_mode": _check_npu_equilibrium(),
    }
