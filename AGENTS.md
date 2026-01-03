# Architecture of the Organism

This document details the different classes of agents and components that constitute the CLI AI ecosystem, based on the current codebase.

---

## 1. Runtime Agents (Behavioral Modes)

The primary "live" agent operates via a mode-based architecture, orchestrated by the `CortexSwitchboard` (`core/kernel/switchboard.py`). These are not separate processes but different behavioral states of the main agent, which is launched via `boot.py`.

### GPIA (General Purpose Intelligent Agent)
- **Implementation**: `core/modes/sovereign_loop.py`
- **Role**: The default interactive mode of the agent. This is the "GPIA" that listens to and processes user commands, utilizing the skill system to perform tasks.

### Teaching Agent
- **Implementation**: `core/modes/teaching.py`
- **Role**: A personality mode where the agent acts as a tutor, demonstrating the system's ability to adopt different functional roles.

### Forensic Debug Agent
- **Implementation**: `core/modes/forensic_debug.py`
- **Role**: A diagnostic mode that allows developers to inspect the agent's internal state and memory, crucial for debugging and maintenance.

---

## 2. Autonomous Learning Agents

This is a standalone, asynchronous learning simulation that runs via `start_autonomous_learning.py` or `docker-compose`. It involves two distinct agent scripts that interact via the file system.

### The Professor (`professor_autonomous.py`)
- **Role**: The Teacher
- **Function**: Autonomously generates lessons on predefined topics using `Qwen3` and `DeepSeek-R1`, saves them to a shared `/lessons` directory, and grades "homework" submitted by the Alpha agent.

### The Alpha (`alpha_autonomous.py`)
- **Role**: The Student
- **Function**: Periodically checks the `/lessons` directory for new material. It "studies" by processing the lesson with `Qwen3`, generates a summary of its understanding, and submits this as "homework" for the Professor to grade. It stores its learnings in a local database.

### The Arbiter (Conceptual Role)
- **Role**: The Judge / Synthesizer
- **Implementation**: This is not a separate agent file but a conceptual role assigned to the `gpt-oss:20b` model within the `agents/model_router.py`. It is invoked for tasks requiring the synthesis of multiple conflicting viewpoints or for making a final judgment call.

---

## 3. The Cognitive Ecosystem (Skill Generation Tool)

This is an offline, interactive tool (`gpia_cognitive_ecosystem.py`) used by a developer to evolve the agent's skillset. Its components are classes, not standalone agents.

### The Hunter (Component)
- **Role**: Identifies a "cognitive gap" and uses an LLM to generate responses to challenges related to that gap.

### The Dissector (Component)
- **Role**: Takes the LLM-generated responses and uses another LLM call to extract reusable patterns and "cognitive weights."

### The Synthesizer (Component)
- **Role**: Takes the extracted weights and uses a final set of LLM prompts to write the Python code for a new, complete skill, saving it as a `.py` file in the `skills/synthesized` directory.

---

## 4. Agent Communication

While the docs mention a "PASS Protocol," the primary communication mechanisms observed in the code are:
- **Mode Transitions:** The live agent switches between behaviors using a `ModeTransition` signal within the `CortexSwitchboard`.
- **File System:** The Alpha and Professor agents communicate asynchronously by reading and writing lesson and homework files to a shared directory.
- **Function Calls:** Components within the same process (like the Cognitive Ecosystem) interact via standard Python class and function calls.