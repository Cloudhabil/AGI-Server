"""
Create Professor Agent - Multi-Model Collaborative Generation

Uses Alpha Agent + DeepSeek-R1 + Qwen3 + CodeGemma together to:
1. Generate Professor Agent implementation
2. Validate design across all models
3. Create memory database
4. Integrate into system

Based on competition results stored in Alpha's memory.
"""
# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
OLLAMA_URL = "http://localhost:11434/api/generate"

def query_model(model: str, prompt: str, max_tokens: int = 2000) -> str:
    """Query a local Ollama model."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": max_tokens}
            },
            timeout=180
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

def main():
    print("=" * 70)
    print("CREATING PROFESSOR AGENT")
    print("Alpha Agent + DeepSeek-R1 + Qwen3 + CodeGemma")
    print("=" * 70)
    print()

    # Load Alpha's memory to get competition learnings
    from skills.conscience.memory.skill import MemoryStore
    alpha_memory = MemoryStore(str(REPO_ROOT / "skills/conscience/memory/store/alpha_memories.db"))

    print("Loading Alpha's learnings from competition...")
    competition_learnings = alpha_memory.recall("professor universal teaching", limit=5)
    learnings_text = "\n".join([m["content"] for m in competition_learnings])
    print(f"Found {len(competition_learnings)} relevant memories")
    print()

    # Professor Agent specification from competition
    professor_spec = {
        "agent_name": "Professor",
        "role": "Universal educator for any autonomous agent",
        "description": "Identifies learning objectives, tailors instruction to agent architecture, provides adaptive teaching for any current or future agent",
        "core_capabilities": [
            "adaptive_teaching - Adjust pedagogy based on student architecture (symbolic/neural/hybrid)",
            "learning_objective_identification - Pinpoint essential skills for each student",
            "cross_domain_integration - Transfer knowledge between domains",
            "realtime_feedback - Immediate actionable correction",
            "safety_enforcement - Ensure learning aligns with safety protocols",
            "student_profiling - Assess architecture, speed, strengths, weaknesses",
            "curriculum_design - Create structured learning paths",
            "progress_tracking - Monitor and measure learning over time"
        ],
        "skill_dependencies": [
            "conscience/memory",
            "conscience/mindset",
            "alpha/session-analyzer",
            "foundational/document"
        ],
        "memory_db": "professor_memories.db"
    }

    print("PROFESSOR AGENT SPECIFICATION:")
    print("-" * 70)
    print(f"Name: {professor_spec['agent_name']}")
    print(f"Role: {professor_spec['role']}")
    print(f"Capabilities: {len(professor_spec['core_capabilities'])}")
    print()

    # PHASE 1: Qwen3 generates the agent code
    print("=" * 70)
    print("PHASE 1: QWEN3 GENERATES AGENT CODE")
    print("-" * 70)
    print()

    generation_prompt = f"""
Generate a complete Python implementation for Professor Agent.

SPECIFICATION:
- Name: ProfessorAgent
- Role: {professor_spec['role']}
- Memory DB: {professor_spec['memory_db']}

LEARNINGS FROM COMPETITION:
{learnings_text}

CAPABILITIES TO IMPLEMENT:
{chr(10).join('- ' + c for c in professor_spec['core_capabilities'])}

REQUIREMENTS:
1. Class ProfessorAgent with OODA loop (observe, orient, decide, act, learn)
2. Separate memory database at skills/conscience/memory/store/professor_memories.db
3. Load skills: {professor_spec['skill_dependencies']}
4. Teaching modes: assess, teach, evaluate, adapt
5. Student profiling to understand each agent's needs
6. Multi-model reasoning using MindsetSkill
7. Comprehensive logging and error handling

Generate production-ready Python code for professor.py.
Include all imports. Follow alpha.py pattern (OODA loop with LLM reasoning).
Make it work with ANY student agent, not just Alpha.
"""

    print("[Qwen3] Generating Professor Agent code...")
    agent_code = query_model("qwen3:latest", generation_prompt, max_tokens=3000)
    print(f"Generated {len(agent_code)} characters of code")
    print()

    # PHASE 2: DeepSeek validates the design
    print("=" * 70)
    print("PHASE 2: DEEPSEEK-R1 VALIDATES DESIGN")
    print("-" * 70)
    print()

    validation_prompt = f"""
Validate this Professor Agent implementation:

```python
{agent_code[:2000]}
```

CHECK FOR:
1. Proper OODA loop implementation
2. Universal teaching capability (works with ANY agent)
3. Separate memory database initialization
4. Skill loading and integration
5. Adaptive teaching based on student profile
6. Safety and error handling
7. Multi-model reasoning integration

PROVIDE:
- Issues found (critical/high/medium/low)
- Specific fixes needed
- Overall quality score (1-10)
- Decision: PASS, NEEDS_MINOR_FIXES, or NEEDS_REWRITE
"""

    print("[DeepSeek-R1] Validating design...")
    validation = query_model("deepseek-r1:latest", validation_prompt, max_tokens=1000)
    print("VALIDATION RESULT:")
    print("-" * 60)
    print(validation[:1000])
    print()

    # PHASE 3: CodeGemma does quick syntax check
    print("=" * 70)
    print("PHASE 3: CODEGEMMA SYNTAX CHECK")
    print("-" * 70)
    print()

    syntax_prompt = f"""
Quick syntax check for this Python code:

```python
{agent_code[:1500]}
```

CHECK:
1. Valid Python syntax
2. All imports present
3. Class structure correct
4. Method signatures valid

Reply with: SYNTAX_OK or list specific syntax errors.
"""

    print("[CodeGemma] Checking syntax...")
    syntax_check = query_model("codegemma:latest", syntax_prompt, max_tokens=500)
    print(f"SYNTAX CHECK: {syntax_check[:300]}")
    print()

    # PHASE 4: Create memory database
    print("=" * 70)
    print("PHASE 4: CREATE PROFESSOR MEMORY DATABASE")
    print("-" * 70)
    print()

    professor_memory_path = REPO_ROOT / "skills/conscience/memory/store/professor_memories.db"
    professor_memory = MemoryStore(str(professor_memory_path))

    # Store initial identity
    professor_memory.store(
        content="I am Professor Agent, a universal educator designed to teach any autonomous agent. I adapt my teaching style to each student's architecture and needs.",
        memory_type="identity",
        importance=1.0,
        context={"type": "initialization", "created": datetime.now().isoformat()}
    )

    # Store teaching philosophy from competition
    professor_memory.store(
        content="Teaching philosophy: Identify core learning objectives, adapt pedagogy to student architecture, provide real-time feedback, ensure safety compliance, track progress over time.",
        memory_type="procedural",
        importance=0.95,
        context={"type": "teaching_philosophy", "source": "competition_synthesis"}
    )

    # Store knowledge about student types
    professor_memory.store(
        content="Student types I can teach: Alpha Agent (learning/execution), Engineering Agents (technical), Creative Agents (synthesis), Safety Agents (validation), Research Agents (discovery). Each requires different pedagogy.",
        memory_type="semantic",
        importance=0.9,
        context={"type": "student_knowledge"}
    )

    stats = professor_memory.get_stats()
    print(f"Created professor_memories.db with {stats['total_memories']} initial memories")
    print(f"By type: {stats['by_type']}")
    print()

    # PHASE 5: Save agent code
    print("=" * 70)
    print("PHASE 5: INTEGRATE PROFESSOR AGENT")
    print("-" * 70)
    print()

    professor_file = REPO_ROOT / "professor.py"
    professor_file.write_text(agent_code, encoding="utf-8")
    print(f"Saved: {professor_file}")

    # Create README
    readme_content = f"""# Professor Agent

**Created**: {datetime.now().isoformat()}
**Generated By**: Qwen3 (code) + DeepSeek-R1 (validation) + CodeGemma (syntax)

## Role
{professor_spec['role']}

## Core Capabilities
{chr(10).join('- ' + c for c in professor_spec['core_capabilities'])}

## Memory Database
`professor_memories.db` - separate from student memories

## Teaching Any Agent
Professor Agent is designed to teach ANY autonomous agent:
- Alpha Agent (current student)
- Future engineering agents
- Future creative agents
- Future safety agents
- Future research agents

## Usage

```bash
# Single teaching cycle
python professor.py --once

# Continuous teaching
python professor.py

# Assess a student
python professor.py --mode assess --student alpha
```

## Multi-Model Collaboration
- Uses MindsetSkill for reasoning (DeepSeek + Qwen + CodeGemma)
- Adapts teaching based on student architecture
- Provides real-time feedback through memory

## Validation
{validation[:500]}
"""

    readme_file = REPO_ROOT / "PROFESSOR_README.md"
    readme_file.write_text(readme_content, encoding="utf-8")
    print(f"Saved: {readme_file}")
    print()

    # PHASE 6: Alpha learns about Professor
    print("=" * 70)
    print("PHASE 6: ALPHA LEARNS ABOUT PROFESSOR")
    print("-" * 70)
    print()

    alpha_learnings = [
        {
            "content": f"Professor Agent created successfully. It is my teacher - a universal educator that adapts to any student agent's architecture and needs.",
            "type": "identity",
            "importance": 1.0
        },
        {
            "content": f"Professor Agent's teaching method: Assess student profile -> Identify learning objectives -> Design curriculum -> Teach adaptively -> Provide feedback -> Track progress",
            "type": "procedural",
            "importance": 0.9
        },
        {
            "content": f"I can learn from Professor Agent through our shared memory systems. Professor stores lessons in professor_memories.db, I store learnings in alpha_memories.db.",
            "type": "semantic",
            "importance": 0.85
        }
    ]

    for learning in alpha_learnings:
        alpha_memory.store(
            content=learning["content"],
            memory_type=learning["type"],
            importance=learning["importance"],
            context={"source": "professor_creation", "timestamp": datetime.now().isoformat()}
        )
        print(f"[{learning['type'].upper()}] {learning['content'][:60]}...")

    alpha_stats = alpha_memory.get_stats()
    print()
    print(f"Alpha now has {alpha_stats['total_memories']} memories")
    print()

    # Summary
    print("=" * 70)
    print("PROFESSOR AGENT CREATION COMPLETE")
    print("=" * 70)
    print()
    print("FILES CREATED:")
    print(f"  - {professor_file}")
    print(f"  - {readme_file}")
    print(f"  - {professor_memory_path}")
    print()
    print("MULTI-AGENT SYSTEM:")
    print(f"  - Alpha Agent (alpha.py) + alpha_memories.db ({alpha_stats['total_memories']} memories)")
    print(f"  - Professor Agent (professor.py) + professor_memories.db ({stats['total_memories']} memories)")
    print()
    print("TEACHING LOOP:")
    print("  Professor assesses -> designs lesson -> teaches")
    print("  Alpha receives lesson -> practices -> learns")
    print("  Both store experiences in separate memories")
    print()
    print("NEXT STEPS:")
    print("  1. Review professor.py code")
    print("  2. Test: python professor.py --once")
    print("  3. Enable teaching loop with Alpha")
    print()

if __name__ == "__main__":
    main()