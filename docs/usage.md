# Usage

## Creating a Task

```bash
python ch_cli.py new --name "my-first-task" --task "Refactor auth logic"
```

You can optionally provide initial context and constraints:

```bash
python ch_cli.py new \
  --name "my-first-task" \
  --context "Repo X, branch main" \
  --task "Refactor auth logic" \
  --constraints "No API changes; keep tests green"
```

This creates `tasks/my-first-task/inputs/` with `context.md`, `tarea.md`, and `restricciones.md`.

## Running a Task

Generate a solution using routing (auto) or a specific model:

```bash
python ch_cli.py run --name "my-first-task" --model auto
# or force a model
python ch_cli.py run --name "my-first-task" --model qwen3
python ch_cli.py run --name "my-first-task" --model deepseek_r1
```

If `inputs/` files exist for the task, they are used; otherwise you may pass `--task` and `--constraints` inline. Outputs are written under `tasks/<slug>/outputs/` with a timestamp. If the model returns a fenced ```diff block, a `.patch` file is also saved.

## Review and Apply

Review the latest output with the QA assistant and save a refined suggestion:

```bash
python ch_cli.py qa --slug my-first-task
```

If a `.patch` was extracted, you can apply it in your target repo:

```bash
python ch_cli.py apply --slug my-first-task
# prints: git apply ".../tasks/my-first-task/outputs/<timestamp>.patch"
```

## Diagnostics

Check router/subserver availability and configuration hints:

```bash
python ch_cli.py doctor
```

## Benchmark Guardrails

Use segmented benchmark runs to reduce resource spikes:

```bash
python gpia_benchmark_suite.py --sections model,s2,memory --guardrails on
```

Use safe memory mode when hardware risk is detected:

```bash
python gpia_benchmark_suite.py --sections memory --memory-mode safe --guardrails on
```

## Launch the Orchestrator

```bash
python orchestrator.py boot
```

## Orbital Orchestrator UI

Backend (Unix):
```bash
scripts/dev_backend.sh
```
Frontend (Unix):
```bash
scripts/dev_frontend.sh
```
Windows equivalents:

```powershell
scripts\dev_backend.ps1
scripts\dev_frontend.ps1
```
Visit <http://localhost:5173> to interact with the 3D orbit interface.

For a full run guide (env vars, ports), see the repository-level `RUN.md`.

## Docker

Bring up the full stack with Redis and Postgres:
```bash
docker-compose up --build
```

## Agent Server Authentication

The FastAPI agent server protects its endpoints with a bearer token.

1. Set a secret token:
   ```bash
   export AGENT_SHARED_SECRET="supersecret"
   ```
2. Include the token in requests:
   ```bash
   curl http://127.0.0.1:8000/health -H "Authorization: Bearer $AGENT_SHARED_SECRET"
   ```

Tokens are compared using a constant-time algorithm to mitigate timing attacks.

## GPIA Ollama Host

If you are using the GPIA model profiles, ensure the host and model store are set:

```powershell
setx OLLAMA_MODELS "C:\Users\usuario\Business\CLI_A1_GHR\CLI-main\models"
setx OLLAMA_HOST "127.0.0.1:11435"
```
