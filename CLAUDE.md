# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Overview: A Dual-Architecture Cognitive Organism

**CLI AI** is a complex system with two main parts:
1.  A **Runtime Kernel** (`boot.py`) that runs the live, interactive agent.
2.  A **Cognitive Ecosystem** (`gpia_cognitive_ecosystem.py`) that is an offline tool for generating new skills.

- **Philosophy**: "Agents are fuel. Skills are fire. GPIA is the furnace."
- **Evolution**: The Cognitive Ecosystem tool uses an LLM-driven pipeline (Hunter -> Dissector -> Synthesizer) to create new, permanent skills as Python files.
- **Immunity**: The `active-immune` skill neutralizes threats before execution.

## Core Directives for Claude

1.  **Respect the Architecture**: Understand the difference between the live agent (`boot.py` and its modes) and the offline skill generator (`gpia_cognitive_ecosystem.py`). Do not try to run evolution commands in the live agent.
2.  **Bio-Mimetic Design**: When refactoring, think in terms of "organs" (specialized agent modes or skills) and "DNA" (the permanent skills in the `skills/` directory).
3.  **Model Routing**: The system uses standard Ollama model tags (e.g., `codegemma:latest`, `deepseek-r1:latest`). Do not use or assume custom `gpia-*` aliases. See `agents/model_router.py` for the definitive mapping.
4.  **Token Ecology**: Be mindful of token consumption. Use `codegemma` for reflexes and `deepseek-r1` for deep thought, as configured in the model router.

## System Architecture

### The Runtime Kernel (`boot.py`)
- **Entry Point**: `python boot.py --mode <mode_name>`
- **Orchestration**: `core/kernel/switchboard.py` manages transitions between different behavioral modes.
- **Default Mode**: `Sovereign-Loop` is the main interactive CLI for the agent.

### The Cognitive Ecosystem (`gpia_cognitive_ecosystem.py`)
This is a standalone tool for developers.
- **Hunter**: A class that prompts LLMs to solve challenges.
- **Dissector**: A class that extracts reasoning patterns ("weights") from the results.
- **Synthesizer**: A class that uses the weights to write the final Python code for a new skill.

### Core Agent Concepts
- **Alpha & Professor**: A teacher-student simulation for autonomous learning, run via `start_autonomous_learning.py`. They interact via files in `agents/session_lessons/`.
- **Arbiter**: A conceptual role, not a file. The `gpt-oss:20b` model is used for this synthesis task.

## Developer Quick Start

```bash
# Launch the main agent's interactive CLI
python boot.py --mode Sovereign-Loop

# Run the interactive tool to evolve new skills
python gpia_cognitive_ecosystem.py

# Run a standalone learning simulation
python start_autonomous_learning.py

# Run tests
pytest --maxfail=1
```

## Skills Framework

The system possesses a growing library of skills found in the `skills/` directory, organized into subdirectories like `synthesized`, `auto_learned`, and `conscience`. The `SkillRegistry` handles lazy-loading them.

### Using Skills in Code

```python
from skills.registry import get_registry
from skills.base import SkillContext

# The registry handles loading and execution
result = get_registry().execute_skill(
    "synthesized/active-immune",
    {"capability": "scan", "input": user_input},
    SkillContext()
)
```