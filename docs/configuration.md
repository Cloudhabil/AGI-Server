# Configuration

CLI AI configuration lives in `configs/` and environment variables. GPIA uses a dedicated Ollama host (`127.0.0.1:11435`) with profiled models stored under `models/`.

## Model configuration (`configs/models.yaml`)

`configs/models.yaml` defines the local model profiles and routing rules used by GPIA and the agent stack.

Key sections:
- `models`: model profiles (Ollama endpoints + model names).
- `routing`: task-to-model mapping (e.g., `alpha_response`, `professor_grading`).
- `patterns`: multi-model collaboration sequences.

Example (abridged):

```yaml
models:
  codegemma:
    kind: ollama
    endpoint: http://127.0.0.1:11435/api/generate
    model: gpia-codegemma:latest
    role: fast

  qwen3:
    kind: ollama
    endpoint: http://127.0.0.1:11435/api/generate
    model: gpia-qwen3:latest
    role: creative

routing:
  alpha_response: qwen3
  professor_analysis: deepseek_r1
  final_synthesis: gpt_oss_20b
```

## Agent configuration (`configs/agents.yaml`)

Defines agent ports, prompts, memory databases, and capabilities for Alpha, Professor, and Arbiter.

```yaml
agents:
  professor:
    port: 7001
    primary_model: deepseek_r1
    prompt: prompts/PROFESSOR.md

  alpha:
    port: 7002
    primary_model: qwen3
    prompt: prompts/ALPHA.md
```

## Environment overrides

### Ollama host and models

Use these when running GPIA profiles from the repo-local store:

- `OLLAMA_MODELS`: set to this repo's `models/` directory.
- `OLLAMA_HOST`: set to `127.0.0.1:11435`.

```powershell
setx OLLAMA_MODELS "C:\Users\usuario\Business\CLI_A1_GHR\CLI-main\models"
setx OLLAMA_HOST "127.0.0.1:11435"
```

### Embedding backends

Default order:
- NPU (OpenVINO)
- Ollama embeddings
- sentence-transformers (CPU)

Environment variables:
- `OLLAMA_EMBEDDING_MODEL`: override the default model (`mahonzhan/all-MiniLM-L6-v2`).
- `OLLAMA_URL`: override the Ollama HTTP endpoint for components that use direct URL calls (default `http://127.0.0.1:11434`).
- `MEMORY_EMBEDDINGS`: set to `off` to disable embeddings entirely.

### Runtime guardrails

Telemetry limits (sovereignty wrapper):
- `GPIA_VRAM_LIMIT` (default `0.85`)
- `GPIA_CPU_LIMIT` (default `0.90`)
- `GPIA_RAM_LIMIT` (default `0.90`)
- `GPIA_VRAM_BUFFER` (default `0.10`)
- `GPIA_CPU_BUFFER` (default `0.05`)
- `GPIA_RAM_BUFFER` (default `0.05`)

Control-plane budgets (percent values):
- `GPIA_CONTROL_CPU_GRACE` (default `10`)
- `GPIA_CONTROL_MEM_GRACE` (default `10`)
- `GPIA_CONTROL_CPU_BUFFER` (default `5`)
- `GPIA_CONTROL_MEM_BUFFER` (default `5`)

Baseline floors live in `memory/agent_state_v1/heuristics.json`, and stage/skill budgets live in `configs/control_plane/resources.yaml`.

Resonance gate (Temporal Formalism):
- `GPIA_RESONANCE_STATE_DIM` (default `256`)
- `GPIA_RESONANCE_THRESHOLD` (default `0.95`)
- `GPIA_RESONANCE_PHASE_MOD` (default `1024`)

Rollback gate:
- `GPIA_ROLLBACK_GATE` (default `1`)
- `GPIA_REGRESSION_TIMEOUT` (default `600`, seconds)
- `GPIA_ALLOW_ROLLBACK` (default `0`, must be `1` to permit git reset)
- `GPIA_STABLE_HASH` (optional override for stable commit hash)

### CLI router overrides (legacy CLI tooling)

The task CLI supports external router/providers via environment variables:

- `ROUTER_BASE_URL`, `ROUTER_MODEL`, `ROUTER_API_KEY`
- `QWEN_BASE_URL`, `QWEN_MODEL`, `QWEN_API_KEY`
- `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`, `DEEPSEEK_API_KEY`
- `CH_FORCE_ROUTER_HTTP=1` forces HTTP routing even when a local model path exists.

Example:

```powershell
$env:QWEN_BASE_URL = 'https://api.provider/v1'
$env:QWEN_MODEL = 'qwen2.5-coder'
$env:QWEN_API_KEY = '<token>'
$env:DEEPSEEK_BASE_URL = 'https://api.deepseek/v1'
$env:DEEPSEEK_MODEL = 'deepseek-reasoner'
$env:DEEPSEEK_API_KEY = '<token>'
```
