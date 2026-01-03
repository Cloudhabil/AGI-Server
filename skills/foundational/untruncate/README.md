# Untruncate Skill

**Created**: 2025-12-30T12:00:59.866319
**Taught by**: Professor Agent
**Learned by**: Alpha Agent
**Models used**: DeepSeek-R1 (definition), Qwen3 (design), CodeGemma (code)

## Purpose
Detect, handle, and prevent truncated outputs from LLM calls.

## Capabilities
- **detect**: Check if text appears truncated
- **continue**: Request LLM to continue from partial output
- **merge**: Combine multiple partial outputs
- **validate**: Verify completeness for expected type (code/json/yaml)

## Truncation Signs
- Unclosed brackets, braces, parentheses
- Text ending mid-sentence
- Incomplete function/class definitions
- Invalid JSON/YAML structure

## Usage
```python
from skills.registry import get_registry

untruncate = get_registry().get_skill("foundational/untruncate")

# Detect truncation
result = untruncate.execute({"capability": "detect", "text": some_output})

# Continue truncated output
result = untruncate.execute({
    "capability": "continue",
    "original_prompt": prompt,
    "text": partial_output
})

# Validate completeness
result = untruncate.execute({
    "capability": "validate",
    "text": code,
    "expected_type": "code"
})
```

## Teaching Record
This skill was taught through multi-agent collaboration:
1. DeepSeek-R1 defined the problem
2. Qwen3 designed the implementation
3. CodeGemma created working code
4. Professor Agent synthesized and taught
5. Alpha Agent learned and practiced
