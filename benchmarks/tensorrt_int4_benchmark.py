"""
TensorRT-LLM INT4 Mistral benchmark helper.

Runs fixed decoding trials against the local TensorRT engine and reports
per-trial latency/throughput plus GPU VRAM usage sampled from nvidia-smi.

Notes:
- Uses the embedded Python 3.10 environment under models/nuke_eater/python_310
  so DLL paths are added explicitly.
- Contexts that exceed the engine's max_input_len are skipped.
"""

import json
import os
import random
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np


BASE_DIR = Path(__file__).resolve().parents[1] / "models" / "nuke_eater" / "python_310"
SITE_PACKAGES = BASE_DIR / "Lib" / "site-packages"
sys.path.insert(0, str(SITE_PACKAGES))


def _add_dll_path(subpath: Path) -> None:
    full = SITE_PACKAGES / subpath
    if full.exists():
        try:
            os.add_dll_directory(str(full))
        except Exception as exc:  # pragma: no cover - best-effort hook
            print(f"[dll] warning: {full} -> {exc}")
        os.environ["PATH"] = str(full) + os.pathsep + os.environ.get("PATH", "")


_add_dll_path(Path("tensorrt_libs"))
_add_dll_path(Path("tensorrt_bindings"))
_add_dll_path(Path("torch") / "lib")
os.add_dll_directory(str(BASE_DIR))

import torch  # noqa: E402
from tensorrt_llm.runtime import ModelRunner, SamplingConfig  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402


ENGINE_DIR = BASE_DIR.parent / "mistral_int4_awq" / "engine"
TOKENIZER_DIR = BASE_DIR.parent / "mistral_int4_awq" / "tokenizer"

TRIALS = 5
TARGET_CONTEXTS = [1024, 2048, 8000, 16000, 32000]
GEN_TOKENS = 256
SEED = 42


def _read_engine_limits() -> dict:
    with open(ENGINE_DIR / "config.json", "r", encoding="utf-8") as fh:
        cfg = json.load(fh)
    build = cfg.get("build_config", {})
    return {
        "max_input_len": int(build.get("max_input_len", 0)),
        "max_output_len": int(build.get("max_output_len", 0)),
    }


LIMITS = _read_engine_limits()


def _make_prompt(tokenizer, target_tokens: int) -> tuple[str, list[int]]:
    """Construct a deterministic prompt near the requested token length."""

    base_chunk = (
        "Safety audit: map out a 4-stage mitigation plan for a supply chain "
        "disruption while citing assumptions."
    )

    text = base_chunk
    # Grow until we meet or exceed the target.
    while len(tokenizer.encode(text, add_special_tokens=True)) < target_tokens:
        text += " " + base_chunk

    # If we overshoot, trim by decoding a truncated token list; accept approximate size.
    token_ids = tokenizer.encode(text, add_special_tokens=True)
    if len(token_ids) > target_tokens:
        text = tokenizer.decode(token_ids[:target_tokens], skip_special_tokens=True)
        token_ids = tokenizer.encode(text, add_special_tokens=True)

    return text, token_ids


def _read_gpu_mem_mb() -> int | None:
    try:
        res = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        line = res.stdout.strip().splitlines()[0]
        return int(line.split(" ")[0])
    except Exception:
        return None


def _run_single_trial(runner, tokenizer, prompt_ids: list[int]) -> dict:
    torch.manual_seed(SEED)
    random.seed(SEED)
    np.random.seed(SEED)

    scfg = SamplingConfig(
        end_id=tokenizer.eos_token_id,
        pad_id=tokenizer.pad_token_id,
        max_new_tokens=GEN_TOKENS,
        temperature=0.0,
        top_k=1,
        top_p=0.0,
        output_sequence_lengths=True,
        return_dict=True,
    )
    scfg.random_seed = SEED

    prompt_len = len(prompt_ids)
    input_tensor = torch.tensor(prompt_ids, dtype=torch.int32)

    mem_samples: list[tuple[float, int]] = []
    stop_evt = threading.Event()

    def poll_vram() -> None:
        while not stop_evt.is_set():
            mem = _read_gpu_mem_mb()
            if mem is not None:
                mem_samples.append((time.perf_counter(), mem))
            time.sleep(0.2)

    poll_thread = threading.Thread(target=poll_vram, daemon=True)
    poll_thread.start()

    torch.cuda.synchronize()
    start = time.perf_counter()

    gen = runner.generate(
        batch_input_ids=[input_tensor],
        sampling_config=scfg,
        streaming=True,
    )

    first_ts = None
    step_records: list[tuple[int, float]] = []

    for out in gen:
        torch.cuda.synchronize()
        now = time.perf_counter()
        seq_len = int(out["sequence_lengths"][0][0])
        new_tokens = seq_len - prompt_len
        if first_ts is None and new_tokens > 0:
            first_ts = now
        step_records.append((new_tokens, now))

    torch.cuda.synchronize()
    end = time.perf_counter()

    stop_evt.set()
    poll_thread.join(timeout=2)

    per_token_tps = []
    prev_tokens = 0
    prev_time = start
    for tokens_generated, ts in step_records:
        delta_tokens = tokens_generated - prev_tokens
        delta_time = ts - prev_time
        if delta_tokens > 0 and delta_time > 0:
            per_token_tps.append(delta_tokens / delta_time)
        prev_tokens = tokens_generated
        prev_time = ts

    total_new_tokens = step_records[-1][0] if step_records else 0
    total_time = end - start
    avg_tps = total_new_tokens / total_time if total_time > 0 else 0.0
    p95_tps = float(np.percentile(per_token_tps, 95)) if per_token_tps else 0.0

    mem_peak = max((m for _, m in mem_samples), default=None)
    mem_steady = mem_samples[-1][1] if mem_samples else None

    return {
        "prompt_tokens": prompt_len,
        "new_tokens": total_new_tokens,
        "ttfb_s": (first_ts - start) if first_ts else None,
        "wall_time_s": total_time,
        "avg_tokens_per_s": avg_tps,
        "p95_tokens_per_s": p95_tps,
        "peak_vram_mb": mem_peak,
        "steady_vram_mb": mem_steady,
    }


def main() -> None:
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_DIR)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    runner = ModelRunner.from_dir(
        str(ENGINE_DIR),
        rank=0,
        debug_mode=False,
        lora_ckpt_source="hf",
    )

    # Warmup to avoid including one-time setup overheads.
    warm_prompt_ids = tokenizer.encode("warmup", add_special_tokens=True)
    _run_single_trial(runner, tokenizer, warm_prompt_ids)

    results = {}
    skipped = []

    for target in TARGET_CONTEXTS:
        if target > LIMITS["max_input_len"]:
            skipped.append({"target_tokens": target, "reason": "exceeds_max_input_len"})
            continue

        prompt_text, prompt_ids = _make_prompt(tokenizer, target)
        trials = []
        for i in range(TRIALS):
            metrics = _run_single_trial(runner, tokenizer, prompt_ids)
            metrics["trial"] = i + 1
            metrics["target_prompt_tokens"] = target
            metrics["actual_prompt_tokens"] = metrics.get("prompt_tokens")
            trials.append(metrics)

        results[str(target)] = {
            "prompt": prompt_text,
            "trials": trials,
        }

    output = {
        "limits": LIMITS,
        "gen_tokens": GEN_TOKENS,
        "seed": SEED,
        "results": results,
        "skipped": skipped,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

