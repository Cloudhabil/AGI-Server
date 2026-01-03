#!/usr/bin/env python3
"""
Minimal training runner for a dense-state-aware LLaMA (Option B: control vector).
- Streams JSONL logs (prompt/text, dense_state vector, resonance score).
- Auto-detects keys (text/state/resonance) from the first valid record.
- Uses a gated adapter to produce a q_proj bias and a resonance head for regression.
- Supports locked normalization stats; computes and saves them if missing.

Assumptions:
- Logs are JSONL with one record per line.
- Fields include: text (str), dense_state (list[float]), resonance/score (float).
- Requires transformers installed and a LLaMA-style model path/name.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, IterableDataset, get_worker_info
from transformers import AutoModelForCausalLM, AutoTokenizer

from scripts.dense_state_patch import enable_dense_state_injection


# ---------- JSONL reader ----------
def iter_jsonl(path: Path) -> Iterator[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"Invalid JSON at {path}:{line_no}: {exc}") from exc


# ---------- Key detection ----------
def detect_keys(rec: Dict[str, Any]) -> Tuple[str, str, str]:
    text_candidates = ["text", "prompt", "input", "instruction", "content"]
    state_candidates = ["state", "dense_state", "vector", "ds"]
    res_candidates = ["resonance", "score", "target_res", "y"]

    state_key = next((k for k in state_candidates if k in rec and isinstance(rec[k], list)), None)
    if state_key is None:
        list_fields = [k for k, v in rec.items() if isinstance(v, list)]
        if len(list_fields) == 1:
            state_key = list_fields[0]
        else:
            raise RuntimeError(f"Cannot detect state key. List fields: {list_fields}")

    res_key = next((k for k in res_candidates if k in rec and isinstance(rec[k], (int, float))), None)
    if res_key is None:
        num_fields = [k for k, v in rec.items() if isinstance(v, (int, float))]
        if len(num_fields) == 1:
            res_key = num_fields[0]
        else:
            raise RuntimeError(f"Cannot detect resonance key. Numeric fields: {num_fields}")

    text_key = next((k for k in text_candidates if k in rec and isinstance(rec[k], str)), None)
    if text_key is None:
        str_fields = [k for k, v in rec.items() if isinstance(v, str)]
        if len(str_fields) == 1:
            text_key = str_fields[0]
        else:
            raise RuntimeError(f"Cannot detect text key. String fields: {str_fields}")

    return text_key, state_key, res_key


# ---------- Streaming dataset ----------
class DenseStateIterableDataset(IterableDataset):
    def __init__(self, logs_path: Path, tokenizer, max_length: int, text_key: str, state_key: str, res_key: str):
        super().__init__()
        self.logs_path = logs_path
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.text_key = text_key
        self.state_key = state_key
        self.res_key = res_key

    def _sharded_iter(self) -> Iterable[Dict[str, Any]]:
        worker = get_worker_info()
        if worker is None:
            yield from iter_jsonl(self.logs_path)
            return
        wid = worker.id
        nw = worker.num_workers
        for i, rec in enumerate(iter_jsonl(self.logs_path)):
            if (i % nw) == wid:
                yield rec

    def __iter__(self):
        tok = self.tokenizer
        for rec in self._sharded_iter():
            text = rec.get(self.text_key)
            state = rec.get(self.state_key)
            res = rec.get(self.res_key)
            if not isinstance(text, str):
                continue
            if not isinstance(state, list) or len(state) == 0:
                continue
            if not isinstance(res, (int, float)):
                continue
            enc = tok(
                text,
                truncation=True,
                max_length=self.max_length,
                padding="max_length",
                return_tensors="pt",
            )
            input_ids = enc["input_ids"].squeeze(0)
            attention_mask = enc["attention_mask"].squeeze(0)
            labels = input_ids.clone()
            labels[attention_mask == 0] = -100
            yield {
                "input_ids": input_ids,
                "attention_mask": attention_mask,
                "labels": labels,
                "dense_state": torch.tensor(state, dtype=torch.float32),
                "target_res": torch.tensor([float(res)], dtype=torch.float32),
            }


def collate_dense_state(batch: List[Dict[str, torch.Tensor]]) -> Dict[str, torch.Tensor]:
    out: Dict[str, torch.Tensor] = {}
    for k in batch[0].keys():
        out[k] = torch.stack([b[k] for b in batch], dim=0)
    return out


# ---------- Adapter + resonance head ----------
class DenseStateAdapter(nn.Module):
    def __init__(self, state_dim: int, model_dim: int, bottleneck: int = 128):
        super().__init__()
        self.norm = nn.LayerNorm(state_dim)
        self.fc1 = nn.Linear(state_dim, bottleneck)
        self.act = nn.SiLU()
        self.fc2 = nn.Linear(bottleneck, model_dim)
        self.gate = nn.Parameter(torch.tensor(-4.0))  # sigmoid(-4) ~ 0.018
        nn.init.zeros_(self.fc2.weight)
        nn.init.zeros_(self.fc2.bias)

    def forward(self, dense_state: torch.Tensor) -> torch.Tensor:
        x = self.norm(dense_state)
        x = self.act(self.fc1(x))
        bias = self.fc2(x)
        return torch.sigmoid(self.gate) * bias


class ResonanceHead(nn.Module):
    def __init__(self, model_dim: int, res_dim: int = 1, pooling: str = "masked_mean"):
        super().__init__()
        self.norm = nn.LayerNorm(model_dim)
        self.fc = nn.Linear(model_dim, res_dim)
        self.pooling = pooling

    def forward(self, hidden_states: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        if self.pooling == "masked_mean":
            mask = attention_mask.unsqueeze(-1).to(hidden_states.dtype)
            summed = (hidden_states * mask).sum(dim=1)
            denom = mask.sum(dim=1).clamp_min(1.0)
            pooled = summed / denom
        elif self.pooling == "last_token":
            idx = attention_mask.sum(dim=1).clamp_min(1).long() - 1
            pooled = hidden_states[torch.arange(hidden_states.size(0), device=hidden_states.device), idx]
        else:
            raise ValueError(f"Unknown pooling: {self.pooling}")
        return self.fc(self.norm(pooled))


def compute_golden_loss(logits: torch.Tensor, labels: torch.Tensor, pred_res: torch.Tensor, target_res: torch.Tensor, lambda_res: float = 0.05) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    loss_lm = F.cross_entropy(
        logits.view(-1, logits.size(-1)),
        labels.view(-1),
        ignore_index=-100,
    )
    loss_res = F.smooth_l1_loss(pred_res, target_res)
    return loss_lm + (lambda_res * loss_res), loss_lm.detach(), loss_res.detach()


# ---------- Stats (mean/std) ----------
def compute_stats(logs_path: Path, state_key: str) -> Dict[str, Any]:
    count = 0
    mean = None
    m2 = None
    state_dim = None
    for rec in iter_jsonl(logs_path):
        state = rec.get(state_key)
        if not isinstance(state, list) or len(state) == 0:
            continue
        vec = torch.tensor(state, dtype=torch.float64)
        if state_dim is None:
            state_dim = vec.numel()
            mean = torch.zeros(state_dim, dtype=torch.float64)
            m2 = torch.zeros(state_dim, dtype=torch.float64)
        if vec.numel() != state_dim:
            raise RuntimeError(f"State dim mismatch: expected {state_dim}, got {vec.numel()}")
        count += 1
        delta = vec - mean
        mean = mean + delta / count
        delta2 = vec - mean
        m2 = m2 + delta * delta2
    if count == 0 or state_dim is None:
        raise RuntimeError("No valid dense_state vectors found to compute stats.")
    var = m2 / max(count - 1, 1)
    std = torch.sqrt(var + 1e-9)
    return {"mean_ref": mean.float(), "std_ref": std.float(), "state_dim": state_dim, "count": count}


def save_stats(stats: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(stats, path)


# ---------- Main ----------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="HF model name or path")
    ap.add_argument("--logs", required=True, help="Path to JSONL logs with text/state/resonance")
    ap.add_argument("--stats", required=True, help="Path to mean/std artifact (will be created if missing)")
    ap.add_argument("--max_length", type=int, default=512)
    ap.add_argument("--batch_size", type=int, default=4)
    ap.add_argument("--num_workers", type=int, default=2)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--steps", type=int, default=200)
    ap.add_argument("--lambda_res", type=float, default=0.05)
    ap.add_argument("--pooling", type=str, default="masked_mean", choices=["masked_mean", "last_token"])
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logs_path = Path(args.logs)
    stats_path = Path(args.stats)

    # Detect keys from the first suitable record.
    first = None
    for rec in iter_jsonl(logs_path):
        if any(isinstance(v, str) for v in rec.values()) and any(isinstance(v, list) for v in rec.values()) and any(isinstance(v, (int, float)) for v in rec.values()):
            first = rec
            break
    if first is None:
        raise RuntimeError("Cannot find a record suitable for key detection in logs.")
    text_key, state_key, res_key = detect_keys(first)
    print(f"[keys] text={text_key} state={state_key} res={res_key}")

    # Load or compute stats.
    if stats_path.exists():
        stats = torch.load(stats_path, map_location="cpu")
        print(f"[stats] loaded {stats_path} count={stats.get('count')}")
    else:
        stats = compute_stats(logs_path, state_key)
        save_stats(stats, stats_path)
        print(f"[stats] computed and saved to {stats_path} count={stats['count']}")
    mean_ref = stats["mean_ref"].to(device)
    std_ref = stats["std_ref"].to(device)
    state_dim = int(stats["state_dim"])

    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16 if device == "cuda" else None,
        device_map="auto" if device == "cuda" else None,
    )
    model.eval()

    # Enable dense-state injection (q_proj bias).
    enable_dense_state_injection(model, verbose=True)

    ds = DenseStateIterableDataset(
        logs_path,
        tokenizer,
        args.max_length,
        text_key=text_key,
        state_key=state_key,
        res_key=res_key,
    )
    dl = DataLoader(
        ds,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        pin_memory=(device == "cuda"),
        collate_fn=collate_dense_state,
    )

    model_dim = model.config.hidden_size
    adapter = DenseStateAdapter(state_dim=state_dim, model_dim=model_dim).to(device)
    res_head = ResonanceHead(model_dim=model_dim, pooling=args.pooling).to(device)

    # Freeze base model for adapter-only training.
    for p in model.parameters():
        p.requires_grad = False

    params = list(adapter.parameters()) + list(res_head.parameters())
    opt = torch.optim.AdamW(params, lr=args.lr, betas=(0.9, 0.95), weight_decay=0.01)

    model.train(False)
    adapter.train(True)
    res_head.train(True)

    iterator = iter(dl)
    for step in range(1, args.steps + 1):
        try:
            batch = next(iterator)
        except StopIteration:
            iterator = iter(dl)
            batch = next(iterator)

        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        raw_state = batch["dense_state"].to(device)
        target_res = batch["target_res"].to(device)

        norm_state = (raw_state - mean_ref) / (std_ref + 1e-6)
        state_bias = adapter(norm_state)  # float32

        out = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            output_hidden_states=True,
            return_dict=True,
            dense_state_bias=state_bias,
        )
        logits = out.logits
        last_hidden = out.hidden_states[-1]
        pred_res = res_head(last_hidden, attention_mask)

        loss, loss_lm, loss_res = compute_golden_loss(
            logits, labels, pred_res, target_res, lambda_res=args.lambda_res
        )

        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        opt.step()

        if step % 25 == 0:
            gate = torch.sigmoid(adapter.gate).item()
            print(
                f"step={step} loss={loss.item():.4f} lm={loss_lm.item():.4f} "
                f"res={loss_res.item():.4f} gate={gate:.4f}"
            )

    print("[ok] training run complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
