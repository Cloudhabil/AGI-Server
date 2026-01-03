# Development

## Setup

Install dependencies:

```bash
pip install -e .[dev]
# or
uv pip install -e .[dev]
```

### Optional OpenVINO/NPU setup

```bash
pip install "openvino>=2024.2" "optimum[openvino]" openvino-tokenizers
optimum-cli export openvino \
    --model sentence-transformers/all-MiniLM-L6-v2 \
    --task feature-extraction \
    --output_dir models/ov-emb
export OPENVINO_EMBEDDING_MODEL=$PWD/models/ov-emb/model.xml
export OPENVINO_TOKENIZER=sentence-transformers/all-MiniLM-L6-v2
export USE_OPENVINO=1
```

## Run checks before committing

```bash
ruff .
mypy
pytest -q
```

The `Makefile` provides a helper:

```bash
make check
```

## Run CI jobs locally

The GitHub Actions workflow defines separate jobs for linting, type checking, and tests.
You can replicate them individually:

- **Lint:** `ruff .`
- **Type:** `mypy`
- **Test:** `SKIP_OPENVINO=true SKIP_DB=true pytest --maxfail=1 --cov=. --cov-fail-under=80`

## FastAPI lifespan

Both `server/main.py` and `bus_server.py` use FastAPI's `lifespan` to manage startup/shutdown
resources (DB pool, Redis). If you embed the app programmatically or mount it into another
ASGI app, the lifespan context ensures resources are acquired and released properly.

Example:

```python
from fastapi import FastAPI
from server.main import app as backend_app
from bus_server import app as bus_app

root = FastAPI()
root.mount("/api", backend_app)
root.mount("/bus", bus_app)

# uvicorn root:app
```

If you need to add your own startup/shutdown logic, define a `lifespan` contextmanager
and pass it to `FastAPI(lifespan=...)` or wrap/mount the provided apps.
