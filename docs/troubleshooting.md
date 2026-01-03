# Troubleshooting

## OpenVINO
- `ov.Core().available_devices` missing `NPU`: install latest drivers and ensure user belongs to `video`/`render` groups.
- Tokenizer not found: verify `openvino-tokenizers` is installed and `OPENVINO_TOKENIZER` points to a valid repo.
- `CLDNN`/`Level Zero` errors: upgrade runtime or set `OPENVINO_EMBEDDING_MODEL_CPU` for CPU fallback.

## Bus Authentication
- `401 Unauthorized`: confirm `BUS_TOKEN` environment variable matches server configuration.
- Connection refused: ensure `bus_server.py` is running and listening on expected port.

## Environment Variables
- Missing `OPENVINO_EMBEDDING_MODEL`: export path to `model.xml`.
- Undefined model paths: check `.env` or shell config files.

## Embedding Backends
- Default order: NPU (OpenVINO) -> Ollama embeddings -> sentence-transformers (CPU).
- If you see sentence-transformers warnings, confirm Ollama is running and the model exists:
  - `ollama list`
  - `OLLAMA_EMBEDDING_MODEL=mahonzhan/all-MiniLM-L6-v2`
- For non-default Ollama servers, set `OLLAMA_URL` (or `OLLAMA_HOST` for the GPIA profile host).
- To disable embeddings entirely, set `MEMORY_EMBEDDINGS=off`.

## Model Downloading
- `model not found`: run `ollama pull <model>` before starting the CLI.
- Corrupted cache: remove `~/.ollama` entries and retry download.

## GPIA Ollama Profiles
- If `gpia-*` models are missing, ensure `OLLAMA_MODELS` points to the repo and `OLLAMA_HOST` is set to `127.0.0.1:11435`.
- If the host is up but models are absent, rebuild from the registry:
  ```powershell
  python .\models\archive_v1\ollama_bridge.py --model gpia-master --create --host http://127.0.0.1:11435
  ```
- If Ollama is not persistent on Windows, install the Startup launcher:
  ```powershell
  .\skills\operations\ollama-service-persistence\scripts\ollama_service_manager.ps1 -Action Install -Mode Startup -ModelsDir "C:\Users\usuario\Business\CLI_A1_GHR\CLI-main\models" -OllamaHost "127.0.0.1:11435"
  ```

## Benchmark Guardrails
- Prefer segmented runs: `python gpia_benchmark_suite.py --sections model,s2,memory --guardrails on`
- Safer memory runs: `python gpia_benchmark_suite.py --sections memory --memory-mode safe --guardrails on`
