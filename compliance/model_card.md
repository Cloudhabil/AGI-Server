# Model Card (Draft)

Status: owner-filled for policy; update if deployment differs.

## Model
- Name: GPIA (General Purpose Intelligent Agent) — GPAI/LLM
- Architecture: decoder-only transformer with RoPE, RMSNorm (pre), SwiGLU, causal MHA; weight tying.
- Optimizations: gradient checkpointing; optional LoRA/QLoRA (rank 8, QLoRA NF4).
- Inference endpoints: Ollama-compatible (see `models/backend.py`).

## Data
- Training data: not shipped in repo; assume use of locally hosted, license-compliant open-weight models (e.g., Ollama-provided models: CodeGemma, Qwen3, DeepSeek-R1, GPT-OSS, LLaVa). If custom training occurs, record datasets, licenses, and PII handling in `compliance/data_sources.md`.
- Fine-tuning/adapters: if used, document datasets and licenses in `compliance/data_sources.md`.

## Capabilities / Intended Use
- General-purpose research, planning, code, and tooling orchestration through MCP.
- Works with multiple local models (CodeGemma, Qwen3, DeepSeek-R1, GPT-OSS, LLaVa) via routing.
- Not intended for Annex III high-risk functions unless explicitly authorized and assessed.

## Limitations / Known Risks
- May hallucinate or produce insecure tool plans if policy/verification disabled.
- No bias/fairness evaluations shipped; treat bias risk as unknown.
- Training data provenance not included; treat copyright/PII risk as unknown unless filled in `compliance/data_sources.md`.

## Safety / Controls
- MCP orchestrator enforces policy, schema validation, retry budgets, audit trace, and manual gates for risky ops.
- Active-immune skill exists but should not be sole defense.
- Manual approval token required for high-risk operations (policy gate).

## Evaluations
- Available: `compliance/generate_validation_metrics.py` with outputs in `compliance/evidence/validation_metrics*.json`.
- Missing: bias/fairness tests; domain-specific robustness.

## Logging / Audit
- MCP orchestration audit: `memory/agent_state_v1/mcp_orchestrator_audit.jsonl`.
- MCP skill audit: `memory/agent_state_v1/mcp_audit.jsonl`.
- Additional logs: agent/bus/server logs (outside scope of this card).

## Deployment Notes
- Requires Python 3.11+; uses local Ollama endpoints for models.
- Ensure `OLLAMA_MODELS` and `OLLAMA_HOST` are set if using local models.

## Owner Actions Needed
- If custom training/finetuning is performed, add data sources/licensing to `compliance/data_sources.md` and update this card.
- Add bias/fairness evaluation results if applicable.
- If an Annex III high-risk use emerges, add specific controls and documentation. 
