"""
Substrate Collision Test
========================

Stresses Tier 1 (GPU LLM) and Tier 3 (NPU embeddings) at the same time to
check for PCIe contention. Run twice: once in legacy mode and once with
--substrate-equilibrium enabled.
"""

import argparse
import os
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from agents.model_router import ModelRouter  # type: ignore
from core.npu_utils import (  # type: ignore
    get_substrate_embeddings_batch,
    get_substrate_status,
)

try:  # Optional GPU stats
    import torch
except Exception:  # pragma: no cover - optional
    torch = None


def _now() -> float:
    return time.perf_counter()


def _mean(values: List[float]) -> float:
    return statistics.mean(values) if values else 0.0


def vram_snapshot() -> Optional[Dict[str, float]]:
    if not torch or not torch.cuda.is_available():
        return None
    device = torch.device("cuda")
    torch.cuda.synchronize()
    props = torch.cuda.get_device_properties(device)
    return {
        "total_mb": props.total_memory / 1_000_000,
        "allocated_mb": torch.cuda.memory_allocated(device) / 1_000_000,
        "reserved_mb": torch.cuda.memory_reserved(device) / 1_000_000,
    }


def llm_worker(
    router: ModelRouter,
    prompt: str,
    model: Optional[str],
    max_tokens: int,
    temperature: float,
    stop_at: float,
    stop_event: threading.Event,
    sink: List[Dict[str, float]],
) -> None:
    while not stop_event.is_set() and _now() < stop_at:
        start = _now()
        try:
            response = router.query(
                prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=120,
                bypass_gov=True,
            )
        except Exception as exc:  # pragma: no cover - runtime diagnostic
            sink.append({"start": start, "duration": 0.0, "tokens": 0.0, "error": str(exc)})
            stop_event.set()
            break

        duration = max(_now() - start, 1e-6)
        tokens = float(len(response.split())) or 1.0
        sink.append({"start": start, "duration": duration, "tokens": tokens})


def embeddings_worker(texts: List[str], record: Dict[str, float]) -> None:
    record["start"] = _now()
    try:
        get_substrate_embeddings_batch(texts)
        record["success"] = 1
    except Exception as exc:  # pragma: no cover - runtime diagnostic
        record["error"] = str(exc)
    finally:
        record["end"] = _now()


def aggregate_tps(samples: List[Dict[str, float]]) -> float:
    tps = [s["tokens"] / s["duration"] for s in samples if s.get("duration", 0) > 0]
    return _mean(tps)


def bucketize(samples: List[Dict[str, float]], start: float, end: float) -> Dict[str, List[Dict[str, float]]]:
    before = [s for s in samples if s.get("start", 0) < start]
    during = [s for s in samples if start <= s.get("start", 0) <= end]
    after = [s for s in samples if s.get("start", 0) > end]
    return {"before": before, "during": during, "after": after}


def main() -> None:
    parser = argparse.ArgumentParser(description="Substrate Collision Test")
    parser.add_argument("--model", default="gpia_core", help="Model id for the GPU task (router names, e.g., gpia_core or gpt_oss_20b)")
    parser.add_argument("--max-tokens", type=int, default=256, help="Max new tokens per LLM call")
    parser.add_argument("--temperature", type=float, default=0.2, help="LLM temperature")
    parser.add_argument("--duration", type=int, default=30, help="Total run duration (seconds)")
    parser.add_argument("--embedding-count", type=int, default=1000, help="Number of texts to embed in the collision batch")
    parser.add_argument("--embedding-delay", type=int, default=5, help="Seconds to wait before launching embeddings")
    parser.add_argument("--prompt", default="Generate a detailed analysis of substrate equilibrium and PCIe contention mitigation techniques.", help="Prompt for the GPU task")
    args = parser.parse_args()

    print("=== Substrate Collision Test ===")
    print(f"Repo: {REPO_ROOT}")
    print(f"Mode: model={args.model}, duration={args.duration}s, embeddings={args.embedding_count}, delay={args.embedding_delay}s")

    print("\n[Status] Substrate configuration")
    status = get_substrate_status()
    for k, v in status.items():
        print(f"- {k}: {v}")

    baseline_vram = vram_snapshot()
    if baseline_vram:
        print("\n[Status] GPU VRAM snapshot (MB)")
        for k, v in baseline_vram.items():
            print(f"- {k}: {v:.1f}")

    router = ModelRouter()

    # Warm-up to ensure model load is accounted for outside the measurement window
    try:
        _ = router.query(args.prompt, model=args.model, max_tokens=64, temperature=args.temperature, timeout=60, bypass_gov=True)
    except Exception as exc:  # pragma: no cover - runtime diagnostic
        print(f"[Warmup] Failed: {exc}")

    llm_samples: List[Dict[str, float]] = []
    llm_stop_event = threading.Event()
    stop_at = _now() + args.duration

    llm_thread = threading.Thread(
        target=llm_worker,
        kwargs={
            "router": router,
            "prompt": args.prompt,
            "model": args.model,
            "max_tokens": args.max_tokens,
            "temperature": args.temperature,
            "stop_at": stop_at,
            "stop_event": llm_stop_event,
            "sink": llm_samples,
        },
        daemon=True,
    )
    llm_thread.start()

    time.sleep(max(args.embedding_delay, 0))

    texts = [f"embedding payload {i}: substrate equilibrium collision test" for i in range(args.embedding_count)]
    embedding_record: Dict[str, float] = {}
    embed_thread = threading.Thread(target=embeddings_worker, args=(texts, embedding_record), daemon=True)
    embed_thread.start()

    embed_thread.join()
    llm_stop_event.set()
    llm_thread.join()

    embed_start = embedding_record.get("start", _now())
    embed_end = embedding_record.get("end", embed_start)
    buckets = bucketize(llm_samples, embed_start, embed_end)

    before_tps = aggregate_tps(buckets["before"])
    during_tps = aggregate_tps(buckets["during"])
    after_tps = aggregate_tps(buckets["after"])

    print("\n=== Results ===")
    print(f"Embeddings batch: {args.embedding_count} items")
    print(f"Embeddings duration: {embed_end - embed_start:.2f}s")
    if "error" in embedding_record:
        print(f"Embeddings error: {embedding_record['error']}")

    print("\nLLM throughput (tokens/sec)")
    print(f"- Before embeddings: {before_tps:.2f}")
    print(f"- During embeddings: {during_tps:.2f}")
    print(f"- After embeddings:  {after_tps:.2f}")

    if before_tps:
        drop = ((before_tps - during_tps) / before_tps) * 100
        print(f"Drop during collision: {drop:.1f}%")

    final_vram = vram_snapshot()
    if final_vram:
        print("\n[Status] GPU VRAM snapshot after test (MB)")
        for k, v in final_vram.items():
            print(f"- {k}: {v:.1f}")


if __name__ == "__main__":
    main()
