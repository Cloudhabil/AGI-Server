#!/usr/bin/env python3
"""
Lightweight hook-based dense-state injection for HF LLaMA-style models.
- Adds a per-batch bias to q_proj outputs (Option B: control vector).
- Avoids touching prompts; injection is gated upstream by the caller.

Usage:
    from dense_state_patch import enable_dense_state_injection
    model = AutoModelForCausalLM.from_pretrained(...)
    enable_dense_state_injection(model, verbose=True)
    ...
    with model.dense_state_context(state_bias):
        out = model(input_ids=..., dense_state_bias=state_bias, ...)
"""
from __future__ import annotations

import threading
from contextlib import contextmanager
from typing import Any, Callable, List, Optional, Tuple

import torch
import torch.nn as nn

# Thread-local storage keeps bias scoped to a single forward, even with workers.
_DENSE_STATE_CTX = threading.local()


def _get_dense_state_bias() -> Optional[torch.Tensor]:
    return getattr(_DENSE_STATE_CTX, "dense_state_bias", None)


@contextmanager
def dense_state_context(bias: Optional[torch.Tensor]):
    prev = _get_dense_state_bias()
    _DENSE_STATE_CTX.dense_state_bias = bias
    try:
        yield
    finally:
        _DENSE_STATE_CTX.dense_state_bias = prev


def _qproj_hook(_module: nn.Module, _inputs: Tuple[torch.Tensor, ...], output: torch.Tensor):
    """
    Forward hook on q_proj: adds dense_state_bias to q_proj output.
    output: [B, T, model_dim]; bias: [B, model_dim]
    """
    bias = _get_dense_state_bias()
    if bias is None:
        return output

    if bias.device != output.device:
        raise RuntimeError(
            f"dense_state_bias device {bias.device} != q_proj output device {output.device}"
        )
    # Allow fp32 bias with bf16/fp16 model; cast to match output dtype.
    if bias.dtype != output.dtype:
        bias = bias.to(dtype=output.dtype)

    if bias.dim() != 2 or output.dim() != 3:
        raise RuntimeError(
            f"Expected bias [B, model_dim] and q_proj output [B, T, model_dim], "
            f"got bias {tuple(bias.shape)} and output {tuple(output.shape)}"
        )
    if bias.size(0) != output.size(0) or bias.size(1) != output.size(2):
        raise RuntimeError(
            f"Shape mismatch: bias {tuple(bias.shape)} vs q {tuple(output.shape)} "
            f"(expected bias [B={output.size(0)}, model_dim={output.size(2)}])"
        )

    return output + bias.unsqueeze(1)  # broadcast bias over tokens


def _wrap_forward(model: nn.Module, verbose: bool = False) -> None:
    """
    Patch model.forward to accept dense_state_bias and route it to the hook context.
    """
    if getattr(model, "_dense_state_forward_wrapped", False):
        return

    orig_forward: Callable[..., Any] = model.forward

    def patched_forward(*args: Any, dense_state_bias: Optional[torch.Tensor] = None, **kwargs: Any):
        with dense_state_context(dense_state_bias):
            return orig_forward(*args, **kwargs)

    model.forward = patched_forward  # type: ignore[assignment]
    model._dense_state_forward_wrapped = True  # type: ignore[attr-defined]
    if verbose:
        print("[dense-state] patched model.forward to accept dense_state_bias")


def enable_dense_state_injection(model: nn.Module, verbose: bool = False) -> List[Any]:
    """
    Attach q_proj hooks across the model and wrap forward for dense_state_bias.
    Returns the list of hook handles for optional cleanup.
    """
    handles: List[Any] = []
    for name, module in model.named_modules():
        if hasattr(module, "q_proj") and isinstance(module.q_proj, nn.Module):
            handle = module.q_proj.register_forward_hook(_qproj_hook)
            handles.append(handle)
            if verbose:
                print(f"[dense-state] hooked q_proj at {name}")

    _wrap_forward(model, verbose=verbose)
    model.dense_state_context = dense_state_context  # type: ignore[attr-defined]
    model._dense_state_hooks = handles  # type: ignore[attr-defined]
    return handles


def disable_dense_state_injection(model: nn.Module) -> None:
    """
    Remove hooks and clear forward patch marker.
    """
    handles: List[Any] = getattr(model, "_dense_state_hooks", [])
    for h in handles:
        try:
            h.remove()
        except Exception:
            pass
    if hasattr(model, "_dense_state_hooks"):
        delattr(model, "_dense_state_hooks")
    if hasattr(model, "_dense_state_forward_wrapped"):
        delattr(model, "_dense_state_forward_wrapped")
