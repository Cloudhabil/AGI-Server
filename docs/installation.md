# Installation

## Prerequisites

- Python 3.11+
- Git
- Local LLM runtime: [Ollama](https://ollama.ai/)

## Clone and Setup

```bash
git clone <your-fork-url>
cd CLI-main
pip install -e .[dev]
```

For a fully pinned environment:

```bash
pip install -r requirements.lock
```

## Ollama models (base)

Pull the base models once (default Ollama store, `xxx.0.0.1:11434`):

```bash
ollama pull llama3:8b
ollama pull codegemma:latest
ollama pull qwen3:latest
ollama pull deepseek-r1:latest
ollama pull llava:latest
ollama pull gpt-oss:20b
ollama pull mahonzhan/all-MiniLM-L6-v2:latest
```

## GPIA model profiles (repo-local)

GPIA uses profiled copies stored under `models/` and served on `xxx.0.0.1:11435`.

Set the repo-local model store:

```powershell
setx OLLAMA_MODELS "C:\Users\usuario\Business\CLI_A1_GHR\CLI-main\models"
setx OLLAMA_HOST "127.0.0.1:11435"
```

Optional: start Ollama in persistent mode (Windows Startup launcher):

```powershell
.\skills\operations\ollama-service-persistence\scripts\ollama_service_manager.ps1 -Action Install -Mode Startup -ModelsDir "C:\Users\usuario\Business\CLI_A1_GHR\CLI-main\models" -OllamaHost "xxx.0.0.1:11435"
```

To build GPIA model profiles:

```powershell
python .\models\archive_v1\ollama_bridge.py --model gpia-master --create --host http://xxx.0.0.1:11435
python .\models\archive_v1\ollama_bridge.py --model gpia-codegemma --create --host http://xxx.0.0.1:11435
```

## OpenVINO Runtime (optional)

```bash
pip install "openvino>=2024.2" "optimum[openvino]" openvino-tokenizers
optimum-cli export openvino \
    --model sentence-transformers/all-MiniLM-L6-v2 \
    --task feature-extraction \
    --output_dir models/ov-emb
```

Set environment variables so the CLI can locate the exported model:

```bash
export OPENVINO_EMBEDDING_MODEL=$PWD/models/ov-emb/model.xml
export OPENVINO_TOKENIZER=sentence-transformers/all-MiniLM-L6-v2
export USE_OPENVINO=1
```

Refer to [Troubleshooting](troubleshooting.md) for common setup issues.
