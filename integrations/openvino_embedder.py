"""Utilities for running text embedding models via OpenVINO.

This module provides a light wrapper around the OpenVINO runtime to obtain
vector embeddings from text inputs. The heavy OpenVINO dependencies are only
imported when ``get_embeddings`` is first invoked so importing this module has
minimal side‑effects.
"""

from __future__ import annotations

from typing import List, Any

import numpy as np
from core.settings import settings

# Defer importing OpenVINO until first use so tests can mock it easily
Core: Any | None = None  # set in _lazy_init when available

# Lazy loaded globals
_core = None
_compiled_model = None
_output = None
_tokenizer = None
_core_ctor: Any | None = None


def _lazy_init() -> None:
    global Core, _core_ctor
    """Initialise OpenVINO runtime and tokenizer on first use."""
    global _core, _compiled_model, _output, _tokenizer
    if _compiled_model is not None and _core_ctor is Core:
        return

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
    # Force CPU execution to preserve VRAM for reasoning models (ASI-Father Substrate Optimization)
    device = "CPU"
    
    if settings.OPENVINO_EMBEDDING_MODEL_CPU:
        model_path = settings.OPENVINO_EMBEDDING_MODEL_CPU

    model = _core.read_model(model_path)
    _compiled_model = _core.compile_model(model, device_name=device)
    _output = _compiled_model.output(0)

    tokenizer_name = settings.OPENVINO_TOKENIZER or "sentence-transformers/all-MiniLM-L6-v2"
    _tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)

    # Warm-up inference to avoid initial latency spikes
    warm_tokens = _tokenizer("warmup", return_tensors="np", padding=True, truncation=True)
    warm_inputs = {inp.any_name: warm_tokens.get(inp.any_name) for inp in _compiled_model.inputs}
    _compiled_model(warm_inputs)


def get_embeddings(text: str) -> List[float]:
    """Return the embedding vector for ``text``.

    The vector is returned as a simple list of floats for ease of storage and
    transmission. The underlying OpenVINO runtime and tokenizer are initialised
    on first call and reused for subsequent invocations.
    """
    _lazy_init()
    assert _compiled_model is not None and _output is not None and _tokenizer is not None

    tokens = _tokenizer(text, return_tensors="np", padding=True, truncation=True)
    # OpenVINO models expect a dict of numpy arrays keyed by input tensor name.
    # ``_compiled_model.inputs`` provides the ordered inputs; we map them to the
    # tokeniser output.
    inputs = {inp.any_name: tokens.get(inp.any_name) for inp in _compiled_model.inputs}
    result = _compiled_model(inputs)[_output]
    array = np.array(result).squeeze(0)
    return array.tolist()
