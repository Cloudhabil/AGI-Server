# Pre-Installation Information

**CLI AI - Multi-Agent Command-Line Interface**

Please read this document carefully before installing CLI AI.

## What is CLI AI?

CLI AI is an intelligent, multi-agent command-line interface that orchestrates specialized AI agents through a message bus architecture. It features H-Net hierarchical memory management with dynamic chunking to maintain long-term context while staying within token budgets.

## System Requirements

### Minimum Requirements

- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+, Fedora, Arch), macOS 11+
- **Python**: Version 3.11 or higher
- **RAM**: 8 GB minimum (16 GB recommended)
- **Disk Space**: 5 GB minimum (10 GB recommended for models)
- **Internet Connection**: Required for initial setup and model downloads

### Required Software

Before installation, ensure you have:

1. **Python 3.11+** - [Download from python.org](https://www.python.org/downloads/)
2. **Git** - [Download from git-scm.com](https://git-scm.com/downloads/)
3. **Redis** (optional but recommended) - [Download from redis.io](https://redis.io/download)
4. **PostgreSQL** (optional, for full backend features) - [Download from postgresql.org](https://www.postgresql.org/download/)

### Local LLM Runtime

CLI AI requires a local LLM runtime. We recommend:

- **Ollama** - [Download from ollama.ai](https://ollama.ai/) (recommended)
- Or any OpenAI-compatible API endpoint

## What Will Be Installed?

The installation process will:

1. Install Python dependencies including:
   - FastAPI (web framework)
   - Redis client (message bus)
   - NumPy (numerical computing)
   - SQLite support (knowledge base)
   - Optional: FAISS, OpenVINO, asyncpg

2. Create the following directory structure:
   ```
   data/          # Knowledge base and memory storage
   configs/       # Configuration files
   prompts/       # Agent system prompts
   logs/          # Application logs
   ```

3. Set up configuration files from templates

## Optional Components

### OpenVINO Runtime (Advanced Users)

For optimized embedding generation on Intel hardware:
- Additional 2-3 GB disk space required
- Requires model export and configuration
- See documentation for setup instructions

### Frontend (Web Interface)

For the web-based interface:
- Node.js 18+ and npm required
- Additional 500 MB disk space for dependencies
- Separate installation steps required

## Important Notes

### Before You Install

- **Backup**: If upgrading from a previous version, backup your `data/` directory
- **Firewall**: The system uses ports 7001-7009 and 7088 by default
- **Antivirus**: Some antivirus software may flag the installation; you may need to add exceptions
- **Model Downloads**: Plan to download 2-10 GB of language models after installation

### Security Considerations

- All agents communicate via local message bus with bearer token authentication
- No data is sent to external servers by default
- Review `.env.example` for security-related configuration options
- Use strong passwords for database credentials

### Known Limitations

- Windows users may experience slower performance with WSL recommended
- FAISS library may not be available on all platforms (fallback to NumPy)
- Full orchestrator requires Redis running locally or accessible endpoint

## Getting Help

If you encounter issues during installation:

- Check [docs/troubleshooting.md](docs/troubleshooting.md)
- Review [docs/installation.md](docs/installation.md) for detailed steps
- Report issues at: [GitHub Issues](https://github.com/your-repo/issues)

## License

This software is distributed under the MIT License. See [LICENSE](LICENSE) for details.

## Ready to Install?

Once you've reviewed this information and met all prerequisites, proceed to:

**[Installation Guide](docs/installation.md)**

---

*Last updated: 2025-12-29*
