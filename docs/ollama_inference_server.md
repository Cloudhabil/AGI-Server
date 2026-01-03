# Ollama-like Inference Server Architecture

This document captures the technical architecture, components, and data flow for a local, stateful inference daemon that mirrors an Ollama-style runtime. It focuses strictly on implementation concerns and avoids product or marketing storytelling.

## 1. System Role

The server is a local model runtime and orchestration daemon. Its responsibilities include:

- Loading quantized transformer weights from disk.
- Managing model lifecycles across RAM, VRAM, and device backends.
- Hosting an HTTP (or gRPC) inference API compatible with OpenAI-style requests.
- Scheduling and executing inference loops on available hardware.
- Streaming tokens back to clients while handling batching, caching, and concurrency.
- Persisting stateful components such as KV caches and sessions, but explicitly not performing training or gradient updates.

## 2. High-Level Architecture

```
Client (CLI / API / App)
        │
        ▼
 HTTP API Layer (REST / OpenAI-compatible)
        │
        ▼
Request Router / Scheduler
        │
        ├── Session Manager
        ├── Context Window Manager
        ├── KV Cache Manager
        │
        ▼
Model Runtime Layer
        │
        ├── Weight Loader
        ├── Tensor Engine
        ├── Tokenizer
        ├── Sampler
        │
        ▼
Hardware Abstraction Layer (CPU / CUDA / Metal / ROCm)
        │
        ▼
Execution Device
```

Stateful elements (sessions, KV cache, token buffers) live inside the inference host. The daemon is not a training service; it runs forward-only passes and streams outputs.

## 3. Core Components

### 3.1. API Layer

- Implemented in a systems language (Rust / Go / C++).
- Exposes `/v1/chat/completions`, `/v1/completions`, `/models`, `/pull`.
- Parses JSON payloads, converts them into job structures, and hands them to the scheduler.
- Handles streaming via server-sent events (SSE) or chunked transfer encoding.

### 3.2. Request Scheduler

- Manages concurrency and queues.
- Picks available model instances based on GPU memory limits.
- Tracks token generation state and cancellation flags.
- Coordinates batching when multiple requests target the same model.

### 3.3. Model Registry

- Maps logical model names to artifact metadata (GGUF, safetensors, quantization, context size, required backend).
- Supports lazy loading and cache eviction (LRU by usage timestamp).
- Provides version tracking so clients can request specific revisions.

### 3.4. Weight Loader

- Memory-maps model files and loads tensors into RAM/VRAM.
- Performs layout conversion, alignment, and optional dequantization steps.
- Integrates with the runtime layer to provide pointers for the tensor engine.

### 3.5. Tokenizer

- Maintains vocab tables (BPE, unigram, SentencePiece) in memory for reuse.
- Converts input text to token IDs and token IDs back to text.

### 3.6. Inference Engine

- Runs transformer forward passes (attention + MLP + LayerNorm).
- Efficiently manages KV cache per session.
- Supports rotary embeddings or ALiBi.
- Optimized for cached attention reuse during autoregressive decoding.

### 3.7. KV Cache Manager

- Stores keys/values per layer and token position for every session.
- Enables context reuse and long conversation handling.
- Synchronized with the scheduler so multiple requests can share caches safely.

### 3.8. Sampler

- Applies decoding hyperparameters (temperature, top-k, top-p, repetition penalty, stop sequences).
- Operates on logits to select the next token.
- Notifies the HTTP layer so tokens can stream immediately.

### 3.9. Hardware Abstraction Layer

- Routes tensor ops to CPU (BLAS/AVX/NEON), CUDA, Metal, or ROCm backends.
- Manages kernel dispatch, memory transfers, and device synchronization.
- Keeps device utilization traces for telemetry.

## 4. Data Flow

1. Client issues prompt.
2. API parses request and passes to the scheduler.
3. Scheduler binds the request to a session, context window state, and model instance.
4. Tokenizer encodes text into IDs.
5. Inference engine produces logits and uses KV cache manager for context.
6. Sampler picks the next token and pushes it to the streaming queue.
7. KV cache updates with the new token’s keys/values.
8. Token streams back to the client.
9. Loop repeats until stop conditions are met.

## 5. Memory Model

| Memory Type | Usage |
|-------------|-------|
| RAM         | Model weights (CPU mode), token buffers, scheduler metadata |
| VRAM        | Model weights (GPU mode), KV caches, sampler state |
| Disk        | Model artifacts, logs, cache indexes |
| Cache       | Recently used models, tokenizer tables, session metadata |

## 6. Concurrency Model

- Each inference request runs an independent decode loop.
- Scheduler supports time slicing, optional batching, and per-session isolation.
- GPU scheduling enforces context isolation so KV caches cannot leak across requests.

## 7. Persistence

- Models persist on disk; sessions remain in-memory unless explicitly checkpointed.
- No training state, gradients, or optimizer states are stored.

## 8. Security Boundary

- Default binding is localhost.
- Prevents remote command execution unless explicitly configured.
- Treats model binaries as untrusted inputs.

## 9. Summary

An Ollama-like server is a local, stateful LLM inference daemon that loads quantized transformer models from disk, schedules concurrent token-generation loops, manages KV caches and memory placement across CPU/GPU backends, and exposes a streaming HTTP API for client applications.
