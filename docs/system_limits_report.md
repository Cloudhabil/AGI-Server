# System Limits and Capability Analysis

Date: 2025-12-29
Updated: 2026-01-01

## Summary
This system is configured for local-first AI operation with a hybrid compute stack (GPU + CPU + NPU), Ollama-backed local LLMs, a skill framework with progressive disclosure, and a persistent memory store. The primary limits are model availability on the local Ollama endpoint, NPU embeddings setup, and I/O scope constraints enforced by the safety skill.

## Hardware and Runtime Baseline
- CPU: Intel(R) Core(TM) Ultra 5 245KF, 14 cores / 14 threads @ 4.2 GHz max
- GPU: NVIDIA GeForce RTX 4070 SUPER (approx 4.0 GB reported by WMI; model spec is 12 GB VRAM in CLAUDE.md)
- NPU: Intel AI Boost (per CLAUDE.md) used for embeddings/classification

## Model Configuration
- `configs/models.yaml` defines:
  - `gpia-codegemma:latest` via Ollama (`127.0.0.1:11435`)
  - `gpia-qwen3:latest` via Ollama (`127.0.0.1:11435`)
  - `gpia-deepseek-r1:latest` via Ollama (`127.0.0.1:11435`)
  - `gpia-master` via Ollama (`127.0.0.1:11435`)
  - `claude-3-5-sonnet-latest` via Anthropic (optional)
- `skills/backends.py` defines local backends:
  - `local_qwen` -> `qwen3:latest`
  - `local_deepseek` -> `deepseek-r1:latest`
  - `local_codegemma` -> `codegemma:latest`

## Skills Framework Capacity
- Skills are loaded lazily; manifest + schema are used for discovery.
- Skills can invoke local models via backends router.
- Conscience stack:
  - `conscience/self`: introspection and alignment
  - `conscience/memory`: persistence + goals table
  - `conscience/awareness`: protoself/core/extended layering
  - `conscience/safety`: boundary enforcement for sensitive actions

## Memory and Goals State
- Memory store stats:
  - total memories: 10
  - by type: episodic 4, procedural 3, semantic 3
  - last_consolidated: null
- Goals table: available and writable via `conscience/memory`.

## Benchmark Results (local Ollama)
Prompt: "Summarize the key differences between CPU, GPU, and NPU in one paragraph."
Runs: 3, max_tokens: 256

- `gpia-qwen3:latest`: avg_latency_ms ~ 4018, runs 3
- `gpia-deepseek-r1:latest`: avg_latency_ms ~ 4146, runs 3
- `gpia-codegemma:latest`: avg_latency_ms ~ 2576, runs 3

Observations:
- All three local backends are available and respond consistently.
- CodeGemma is the fastest of the three in this prompt profile.

## System Limits and Risks
1. **Local model availability**
   - If Ollama is not running or the model is missing, local inference fails.
2. **NPU embeddings dependency**
   - Embedding generation requires OpenVINO/NPU setup; failures are non-fatal but reduce recall quality.
3. **Memory consolidation**
   - Consolidation is configured but no consolidated memories exist yet (`last_consolidated` is null).
4. **Write boundaries**
   - `conscience/safety` halts writes outside repo without explicit approval.
5. **UI/loop separation**
   - Mind loop runs indefinitely; UI server is separate. Foreground launch can block if run with short timeouts.

## Recommendations
- Ensure Ollama service is running at `http://127.0.0.1:11435` with required GPIA models pulled.
- Set `OLLAMA_MODELS` to the repo `models/` directory for GPIA profiles.
- Initialize NPU embeddings in `core/npu_utils.py` if semantic recall quality becomes important.
- Schedule periodic memory consolidation (e.g., daily) to manage memory growth.
- Keep safety skill as the gatekeeper for any writes outside repo.
- Use the `MindLoop` class for background execution and `interface.py` for UI.

## Evidence Sources
- `CLAUDE.md`: hardware, local model guidance, NPU usage
- `configs/models.yaml`: model endpoints
- `skills/backends.py`: local backend definitions
- `skills/conscience/*`: self, memory, awareness, safety
- Benchmark run via `system/benchmark` skill
