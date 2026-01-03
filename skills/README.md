# CLI AI Skills Framework

A modular skills system that provides domain expertise and procedural knowledge to AI agents. Skills are organized as self-contained packages with code, scripts, and instructions that enable **progressive disclosure** - agents only access complex information when necessary to save context space.

## Overview

Skills provide a universal interface for agents to interact with the digital world more consistently and efficiently than traditional prompting alone. This modular approach enables:

- **Progressive Disclosure**: Skills are lazy-loaded; agents only see detailed information when needed
- **Domain Expertise**: Package specialized knowledge into reusable units
- **Collaborative Ecosystem**: Both technical and non-technical users can create and share skills
- **Agent Integration**: Seamless integration with CLI AI's message bus and agent architecture

## Quick Start

### Using a Skill

```python
from skills import load_skill, SkillContext

# Load a skill
python_skill = load_skill("code/python")

# Create execution context
context = SkillContext(
    user_id="user123",
    agent_role="CTO",
)

# Execute the skill
result = python_skill.execute(
    input_data={
        "task": "debug",
        "code": "def foo(): return bar",
        "error": "NameError: name 'bar' is not defined",
    },
    context=context,
)

if result.success:
    print(result.output)
else:
    print(f"Error: {result.error}")
```

### Discovering Skills

```python
from skills.discovery import discover_skills, recommend_skills

# Natural language discovery
matches = discover_skills("help me analyze my CSV data")
for match in matches:
    print(f"{match.skill_id}: {match.score:.2f} - {match.metadata.description}")

# Task-based recommendations
recommendations = recommend_skills(
    task="refactor this Python function for better performance",
    context={"file_extension": ".py"}
)
```

### Agent Integration

```python
from skills.agent_integration import AgentSkillBridge

# Create bridge for an agent role
bridge = AgentSkillBridge("CTO")

# Get available skills for this role
available = bridge.get_available_skills()
print(f"CTO has access to {len(available)} skills")

# Execute a skill with role-based context
result = bridge.execute_skill(
    "code/review",
    {"code": "...", "checks": ["security", "quality"]}
)
```

## Architecture

### Directory Structure

```
skills/
  INDEX.json              # Master registry (121 skills)
  base.py                 # Core interfaces
  registry.py             # Skill registry
  loader.py               # Lazy loader
  discovery.py            # Natural language discovery
  agent_integration.py    # Agent bridge
  automation/             # Orchestration & guardrails
  conscience/             # Memory, mindset, self, safety
  enterprise/             # Business + compliance
  operations/             # Reliability + service ops
  reasoning/              # Analysis + grounding
  research/               # Evidence + verification
  synthesis/              # Output crafting
  synthesized/            # Auto-generated skills
  system/                 # System-level skills
  ...                     # See INDEX.json for full list
```

### Core Components

#### Skill Base Class

Every skill extends the `Skill` base class:

```python
from skills.base import Skill, SkillMetadata, SkillContext, SkillResult

class MySkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="category/my-skill",
            name="My Skill",
            description="What this skill does",
            category=SkillCategory.CODE,
            level=SkillLevel.INTERMEDIATE,
            tags=["tag1", "tag2"],
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "input_field": {"type": "string"},
            },
            "required": ["input_field"],
        }

    def execute(self, input_data: Dict, context: SkillContext) -> SkillResult:
        # Skill logic here
        return SkillResult(
            success=True,
            output={"result": "..."},
            skill_id=self.metadata().id,
        )
```

#### Skill Levels

Skills have complexity levels that affect when they're disclosed:

| Level | Description | Behavior |
|-------|-------------|----------|
| `BASIC` | Always available | Auto-loaded, low token cost |
| `INTERMEDIATE` | Available on relevant tasks | Loaded on demand |
| `ADVANCED` | Loaded when explicitly needed | Higher token cost |
| `EXPERT` | Requires confirmation | May require user approval |

#### Skill Categories

Skills are organized into categories:

- **CODE**: Programming, debugging, refactoring
- **DATA**: Analysis, transformation, queries
- **WRITING**: Content creation, editing, docs
- **RESEARCH**: Information gathering
- **AUTOMATION**: Workflows, scripts
- **INTEGRATION**: External services
- **REASONING**: Logic, problem-solving
- **CREATIVE**: Generative tasks

## Creating a Skill

### Using the Template Generator

```python
from skills.loader import SkillLoader
from skills.base import SkillCategory
from pathlib import Path

loader = SkillLoader()
loader.create_skill_template(
    directory=Path("skills/custom/my-skill"),
    skill_id="custom/my-skill",
    name="My Custom Skill",
    description="Description of what it does",
    category=SkillCategory.CODE,
)
```

### Manual Creation

1. **Create directory structure**:
   ```
   skills/category/my-skill/
   ├── manifest.yaml
   ├── skill.py
   └── README.md
   ```

2. **Define manifest.yaml**:
   ```yaml
   id: category/my-skill
   name: My Skill
   description: Brief description
   version: "0.1.0"
   category: code
   level: intermediate
   tags: [tag1, tag2]
   dependencies: []
   estimated_tokens: 500
   ```

3. **Implement skill.py**:
   ```python
   from skills.base import Skill, SkillMetadata, SkillContext, SkillResult

   class MySkill(Skill):
       def metadata(self) -> SkillMetadata:
           # Load from manifest or define inline
           ...

       def execute(self, input_data, context) -> SkillResult:
           # Your skill logic
           ...
   ```

## Configuration

Skills are configured in `configs/skills.yaml`:

```yaml
settings:
  enabled: true
  lazy_loading: true
  auto_scan: true

role_mappings:
  CTO:
    categories: [code, reasoning]
    max_level: expert
    specific_skills:
      - code/python
      - code/review

discovery:
  min_relevance_score: 0.3
  max_suggestions: 5
```

## Built-in Skills

### Code Skills

| Skill ID | Description |
|----------|-------------|
| `code/python` | Python development assistance |
| `code/review` | Automated code review |
| `code/refactor` | Code refactoring suggestions |

### Data Skills

| Skill ID | Description |
|----------|-------------|
| `data/analysis` | Exploratory data analysis |
| `data/transform` | Data cleaning and transformation |

### Writing Skills

| Skill ID | Description |
|----------|-------------|
| `writing/draft` | Content drafting |
| `writing/edit` | Content editing and proofreading |

## Integration Points

### Message Bus

Skills can be invoked via bus messages:

```python
# Bus message format
{
    "topic": "skill_request",
    "data": {
        "skill_id": "code/python",
        "input": {"task": "debug", "code": "..."},
        "context": {"agent_role": "CTO"},
    }
}

# Response format
{
    "topic": "skill_result",
    "data": {
        "skill_id": "code/python",
        "success": true,
        "output": {...},
    }
}
```

### Knowledge Base

Skill executions can be logged to the KB:

```python
# Entry format
{
    "kind": "skill_execution",
    "meta": {
        "skill_id": "code/python",
        "agent_role": "CTO",
        "success": true,
        "execution_time_ms": 150,
    },
    "text": "Skill output summary...",
}
```

## Best Practices

### Skill Design

1. **Single Responsibility**: Each skill should do one thing well
2. **Clear Schemas**: Define precise input/output schemas
3. **Graceful Degradation**: Handle missing dependencies
4. **Meaningful Errors**: Return helpful error messages
5. **Token Efficiency**: Minimize token usage in prompts

### Performance

1. **Lazy Loading**: Use `lazy=True` when scanning
2. **Cache Results**: Enable caching for deterministic skills
3. **Batch Operations**: Process multiple items together
4. **Async Where Possible**: Use async for I/O operations

### Security

1. **Input Validation**: Validate all inputs against schema
2. **Safe Defaults**: Never execute arbitrary code
3. **Sandboxing**: Run untrusted operations in isolation
4. **Audit Logging**: Log sensitive operations

## API Reference

### Core Classes

- `Skill` - Base class for all skills
- `SkillMetadata` - Skill description and requirements
- `SkillContext` - Runtime execution context
- `SkillResult` - Execution result with output and metadata

### Registry Functions

- `get_registry()` - Get global skill registry
- `load_skill(skill_id)` - Load and return a skill
- `scan_builtin_skills()` - Scan and register built-in skills

### Discovery Functions

- `discover_skills(query)` - Natural language discovery
- `recommend_skills(task, context)` - Task-based recommendations
- `get_discovery()` - Get global discovery instance

### Agent Integration

- `AgentSkillBridge` - Bridge between agents and skills
- `create_skill_delegate(role)` - Create delegation function
- `inject_skills_into_prompt(prompt, role)` - Enhance prompts with skills

## Contributing

### Adding a New Skill

1. Fork the repository
2. Create skill directory under appropriate category
3. Implement `manifest.yaml` and `skill.py`
4. Add tests in `tests/skills/`
5. Submit pull request

### Guidelines

- Follow existing code style
- Include comprehensive tests
- Document all public APIs
- Provide example usage in manifest

## License

MIT License - see LICENSE file for details.
