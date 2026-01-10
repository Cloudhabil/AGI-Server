# Post-Installation Guide

**Congratulations!** You have successfully installed CLI AI.

## Installation Verification

Verify your installation is working correctly:

### 1. Check Python Installation

```bash
python --version
# Should display Python 3.11 or higher
```

### 2. Verify CLI AI Installation

```bash
python scripts/ch_cli.py --help
# Should display CLI AI help information
```

### 3. Check Dependencies

```bash
pip list | grep -E "(fastapi|redis|pydantic)"
# Should show installed packages
```

## Initial Configuration

### 1. Create Environment File

If not already done during installation:

```bash
cp .env.example .env
```

Edit `.env` with your preferred text editor and configure:

```env
# Required: Bus authentication token
BUS_TOKEN=your-secure-token-here

# Redis connection (if using Redis)
REDIS_URL=redis://localhost:6379/0

# Database (if using PostgreSQL)
POSTGRES_USER=orch
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=orch

# Model configuration (optional, defaults to Ollama)
QWEN_BASE_URL=http://localhost:11434/v1
ROUTER_BASE_URL=http://localhost:11434/v1
```

### 2. Download Required Models

If using Ollama (recommended):

```bash
ollama pull qwen2
ollama pull codegemma
```

Verify models are available:

```bash
ollama list
```

### 3. Initialize Knowledge Base

The knowledge base is automatically created on first run, but you can verify:

```bash
# This will create data/kb.db if it doesn't exist
python scripts/ch_cli.py new --name "test" --task "Hello world"
```

## Quick Start

### Basic CLI Workflow

Run your first task:

```bash
python scripts/ch_cli.py new --name "my-first-task" --task "Explain what you can do"
```

### Full Orchestrator Mode

Start the complete multi-agent system:

```bash
# Ensure Redis is running first
redis-server

# In another terminal, boot the orchestrator
python orchestrator.py boot
```

### Interactive Shell

For interactive agent communication:

```bash
python orchestrator.py shell
```

## Next Steps

### 1. Explore Documentation

- **[Usage Guide](docs/usage.md)** - Learn how to use CLI AI effectively
- **[Architecture](docs/architecture.md)** - Understand the system design
- **[Configuration](docs/configuration.md)** - Advanced configuration options
- **[API Reference](docs/api.md)** - API documentation

### 2. Optional: Set Up Frontend

If you want the web interface:

```bash
cd frontend
npm install
npm run dev
# Frontend will be available at http://localhost:5173
```

### 3. Optional: Configure OpenVINO (Advanced)

For optimized embeddings on Intel hardware:

```bash
pip install "openvino>=2024.2" "optimum[openvino]" openvino-tokenizers

optimum-cli export openvino \
    --model sentence-transformers/all-MiniLM-L6-v2 \
    --task feature-extraction \
    --output_dir models/ov-emb

# Set environment variables
export OPENVINO_EMBEDDING_MODEL=$PWD/models/ov-emb/model.xml
export OPENVINO_TOKENIZER=sentence-transformers/all-MiniLM-L6-v2
export USE_OPENVINO=1
```

### 4. Development Mode (Optional)

If you plan to contribute or develop:

```bash
# Install development dependencies
pip install .[dev]

# Run tests
pytest

# Run code quality checks
make check
```

## Verification Checklist

Ensure everything is working:

- [ ] Python 3.11+ installed and accessible
- [ ] CLI AI responds to `python scripts/ch_cli.py --help`
- [ ] Environment file (`.env`) configured
- [ ] Required LLM models downloaded (via Ollama or other)
- [ ] Redis running (if using full orchestrator)
- [ ] Successfully ran first test task
- [ ] Knowledge base created in `data/kb.db`

## Common Post-Installation Issues

### Issue: "Module not found" errors

**Solution**: Ensure you installed all dependencies:
```bash
pip install .[dev]
```

### Issue: "Connection refused" to Redis

**Solution**: Start Redis server:
```bash
redis-server
```

Or update `REDIS_URL` in `.env` to point to your Redis instance.

### Issue: "Model not found" errors

**Solution**: Download required models:
```bash
ollama pull qwen2
ollama pull codegemma
```

### Issue: Port conflicts (7088, 7001-7009)

**Solution**: Check for processes using these ports:
```bash
# Windows
netstat -ano | findstr :7088

# Linux/macOS
lsof -i :7088
```

Update port configuration in `configs/agents.yaml` if needed.

## Getting Help

If you encounter issues:

1. Check **[Troubleshooting Guide](docs/troubleshooting.md)**
2. Review **[FAQ](docs/README.md)**
3. Search existing **[GitHub Issues](https://github.com/your-repo/issues)**
4. Open a new issue with:
   - Your OS and Python version
   - Installation method used
   - Full error message
   - Steps to reproduce

## Community and Contributing

- **Documentation**: [docs/](docs/README.md)
- **Contributing**: [docs/contributing.md](docs/contributing.md)
- **Development**: [docs/development.md](docs/development.md)

## What's Next?

You're all set! Here are some suggestions:

1. **Learn the basics**: Read the [Usage Guide](docs/usage.md)
2. **Experiment**: Try different tasks with `ch_cli.py`
3. **Explore agents**: Review `configs/agents.yaml` to see available agents
4. **Customize**: Modify agent prompts in `prompts/` directory
5. **Integrate**: Set up social hooks in `integrations/` (optional)

## Thank You

Thank you for installing CLI AI! We hope you find it useful.

---

*Last updated: 2025-12-29*
