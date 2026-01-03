# Agent Generator

Generates complete autonomous agent implementations using local models (DeepSeek-R1, Qwen3, CodeGemma).

## Purpose

This skill enables the multi-agent architecture by creating specialized agents like Professor Agent, each with:
- Separate memory database
- Specialized skill set
- Defined role and purpose
- Access to LLM partners

## Capabilities

- **generate_agent**: Create complete agent implementation from specification
- **create_memory_db**: Initialize separate memory database for agent
- **define_skills**: Specify agent-specific skill dependencies
- **integrate_agent**: Register agent in the system

## Multi-Model Usage

- **Qwen3**: Creative agent code generation
- **DeepSeek-R1**: Agent design validation and critique
- **CodeGemma**: Quick syntax validation

## Example Usage

```python
from skills.registry import get_registry
from skills.base import SkillContext

registry = get_registry()
agent_gen = registry.get_skill("alpha/agent-generator")

# Generate Professor Agent
result = agent_gen.execute({
    "capability": "generate_agent",
    "spec": {
        "agent_name": "Professor",
        "role": "Teacher and guide for Alpha Agent",
        "description": "Creates lesson plans, assesses understanding, provides Socratic guidance",
        "core_capabilities": [
            "curriculum design",
            "knowledge assessment",
            "Socratic questioning",
            "progress tracking"
        ],
        "skill_dependencies": [
            "conscience/memory",
            "conscience/mindset",
            "alpha/session-analyzer",
            "foundational/document"
        ],
        "memory_db_name": "professor_memories.db",
        "ooda_config": {
            "interval_s": 300,
            "modes": ["observe", "teach", "assess"]
        }
    }
}, SkillContext())

# Create memory database
db_result = agent_gen.execute({
    "capability": "create_memory_db",
    "spec": {
        "agent_name": "Professor",
        "memory_db_name": "professor_memories.db"
    }
}, SkillContext())

# Define skills
skills_result = agent_gen.execute({
    "capability": "define_skills",
    "spec": {
        "agent_name": "Professor",
        "role": "Teacher",
        "core_capabilities": ["teach", "assess", "guide"],
        "skill_dependencies": [
            "conscience/memory",
            "conscience/mindset"
        ]
    }
}, SkillContext())

# Integrate into system
integration_result = agent_gen.execute({
    "capability": "integrate_agent",
    "agent_code": result.output.get("agent_code"),
    "spec": {
        "agent_name": "Professor",
        "description": "Teaching agent for Alpha",
        "role": "Teacher and guide",
        "core_capabilities": ["teach", "assess"],
        "skill_dependencies": ["conscience/memory"],
        "memory_db_name": "professor_memories.db",
        "ooda_config": {}
    }
}, SkillContext())
```

## Process Flow

1. **Generate Agent** (Qwen3)
   - Take agent specification
   - Generate OODA loop implementation
   - Include skill integration logic
   - Add role-specific capabilities

2. **Validate Design** (DeepSeek-R1)
   - Check OODA implementation
   - Verify multi-agent compatibility
   - Assess role-specific logic
   - Security review

3. **Create Memory DB**
   - Initialize SQLite database
   - Create proper schema
   - Store initial identity memory

4. **Define Skills**
   - Analyze skill requirements
   - Recommend custom skills
   - Create skill specifications

5. **Integrate Agent**
   - Write agent Python file
   - Create README documentation
   - Register in system

## Multi-Agent Architecture

Each generated agent:
- Has own `{agent_name}_memories.db`
- Loads required skills from registry
- Implements OODA loop for autonomy
- Can collaborate with other agents via shared skills
- Maintains separate learning history

## Professor Agent Example

The first agent to create with this skill is **Professor Agent**:

```python
spec = {
    "agent_name": "Professor",
    "role": "Teacher and guide for Alpha Agent",
    "description": "Designs curricula, assesses knowledge, provides Socratic guidance",
    "core_capabilities": [
        "curriculum_design",
        "knowledge_assessment",
        "socratic_questioning",
        "progress_tracking",
        "adaptive_teaching"
    ],
    "skill_dependencies": [
        "conscience/memory",     # Teaching history
        "conscience/mindset",    # Pedagogical reasoning
        "alpha/session-analyzer", # Student analysis
        "foundational/document"  # Lesson materials
    ],
    "memory_db_name": "professor_memories.db",
    "ooda_config": {
        "interval_s": 300,
        "modes": ["observe", "teach", "assess"]
    }
}
```

## Teaching/Learning Pattern

**Professor teaches → Alpha learns:**

```python
# Professor assesses Alpha's needs
needs = professor.analyze_student(alpha_context)

# Professor creates lesson
lesson = professor.create_lesson(needs)

# Alpha learns from lesson
alpha.learn(lesson)

# Both store in memory
professor.memory.store("Taught lesson X")
alpha.memory.store("Learned lesson X")
```

## Generated

This skill was generated autonomously by Alpha Agent's SkillGenerator.

Generated: 2025-12-30

## Dependencies

- conscience/mindset (required) - For LLM reasoning
- conscience/memory (optional) - For storing generations
- alpha/skill-generator (optional) - For generating custom agent skills
