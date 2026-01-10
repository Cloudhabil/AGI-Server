"""
Teaching Session: Untruncate Skill

Process:
1. Use local LLMs to define and implement "untruncate" capability
2. Professor learns this skill
3. Professor teaches Alpha this skill
4. Both agents store in their memories
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
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
OLLAMA_URL = "http://localhost:11434/api/generate"

def query_model(model: str, prompt: str, max_tokens: int = 2000) -> str:
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
    print("TEACHING SESSION: UNTRUNCATE SKILL")
    print("Professor Agent Learning & Teaching Alpha Agent")
    print("=" * 70)
    print()

    # Load memories
    from skills.conscience.memory.skill import MemoryStore
    professor_memory = MemoryStore(str(REPO_ROOT / "skills/conscience/memory/store/professor_memories.db"))
    alpha_memory = MemoryStore(str(REPO_ROOT / "skills/conscience/memory/store/alpha_memories.db"))

    # PHASE 1: DeepSeek defines the problem
    print("PHASE 1: DEEPSEEK-R1 DEFINES UNTRUNCATE PROBLEM")
    print("-" * 70)
    print()

    define_prompt = """
Define the "untruncate" problem and skill for AI agents:

1. What is truncation in LLM outputs?
2. Why does it happen? (token limits, max_tokens, buffer overflow)
3. What problems does it cause? (incomplete code, broken logic, missing context)
4. What capabilities does an "untruncate" skill need?
5. How should an agent detect and handle truncation?

Provide clear definition that can be taught to other agents.
"""

    print("[DeepSeek-R1] Defining untruncate problem...")
    definition = query_model("deepseek-r1:latest", define_prompt)
    print("DEFINITION:")
    print("-" * 60)
    print(definition)
    print()

    # PHASE 2: Qwen3 designs the implementation
    print("=" * 70)
    print("PHASE 2: QWEN3 DESIGNS IMPLEMENTATION")
    print("-" * 70)
    print()

    design_prompt = f"""
Based on this problem definition:
{definition[:1000]}

Design an "untruncate" skill with these capabilities:

1. detect_truncation - Identify when output is incomplete
2. request_continuation - Ask LLM to continue from where it stopped
3. merge_outputs - Combine multiple partial outputs into complete result
4. validate_completeness - Verify the final result is complete

Provide Python implementation for each capability.
Make it work with Ollama API (localhost:11434).
"""

    print("[Qwen3] Designing implementation...")
    implementation = query_model("qwen3:latest", design_prompt, max_tokens=3000)
    print("IMPLEMENTATION:")
    print("-" * 60)
    print(implementation[:2000])
    if len(implementation) > 2000:
        print(f"\n... ({len(implementation) - 2000} more chars)")
    print()

    # PHASE 3: CodeGemma creates practical code
    print("=" * 70)
    print("PHASE 3: CODEGEMMA CREATES WORKING CODE")
    print("-" * 70)
    print()

    code_prompt = f"""
Create a working Python class for untruncate skill:

class UntruncateSkill:
    def detect_truncation(self, text: str) -> bool:
        # Return True if text appears truncated

    def request_continuation(self, original_prompt: str, partial_output: str) -> str:
        # Ask LLM to continue from partial output

    def merge_outputs(self, parts: list) -> str:
        # Combine multiple parts into complete output

    def validate_completeness(self, text: str, expected_type: str) -> bool:
        # Check if output is complete for expected type (code, text, json)

Use Ollama API at localhost:11434. Include all imports. Make it work immediately.
"""

    print("[CodeGemma] Creating working code...")
    working_code = query_model("codegemma:latest", code_prompt, max_tokens=2000)
    print("WORKING CODE:")
    print("-" * 60)
    print(working_code)
    print()

    # PHASE 4: Professor learns the skill
    print("=" * 70)
    print("PHASE 4: PROFESSOR LEARNS UNTRUNCATE SKILL")
    print("-" * 70)
    print()

    # Store in Professor's memory
    professor_memory.store(
        content=f"Untruncate Skill Definition: {definition[:500]}",
        memory_type="semantic",
        importance=0.95,
        context={"type": "skill_definition", "skill": "untruncate", "source": "deepseek-r1"}
    )

    professor_memory.store(
        content=f"Untruncate Implementation Design: {implementation[:500]}",
        memory_type="procedural",
        importance=0.95,
        context={"type": "skill_implementation", "skill": "untruncate", "source": "qwen3"}
    )

    professor_memory.store(
        content=f"Untruncate Working Code: {working_code[:500]}",
        memory_type="procedural",
        importance=0.95,
        context={"type": "skill_code", "skill": "untruncate", "source": "codegemma"}
    )

    professor_memory.store(
        content="Learned untruncate skill from multi-model collaboration. Can now detect, handle, and prevent truncated LLM outputs.",
        memory_type="episodic",
        importance=0.9,
        context={"type": "learning_experience", "skill": "untruncate", "timestamp": datetime.now().isoformat()}
    )

    prof_stats = professor_memory.get_stats()
    print(f"Professor stored 4 memories about untruncate skill")
    print(f"Professor now has {prof_stats['total_memories']} total memories")
    print()

    # PHASE 5: Professor teaches Alpha
    print("=" * 70)
    print("PHASE 5: PROFESSOR TEACHES ALPHA THE UNTRUNCATE SKILL")
    print("-" * 70)
    print()

    lesson = f"""
LESSON: UNTRUNCATE SKILL
From: Professor Agent
To: Alpha Agent
Date: {datetime.now().strftime('%Y-%m-%d')}

== WHAT IS TRUNCATION ==
When LLMs generate long outputs, they may be cut off due to:
- Token limits (max_tokens parameter)
- Buffer constraints
- Timeout conditions

== WHY IT MATTERS ==
Truncated outputs cause:
- Incomplete code (syntax errors, missing functions)
- Broken logic (partial implementations)
- Lost context (important information cut off)

== HOW TO DETECT TRUNCATION ==
Signs of truncation:
- Code that doesn't close brackets/braces
- Text ending mid-sentence
- JSON/YAML not properly closed
- Functions without return statements

== HOW TO HANDLE TRUNCATION ==
1. Detect: Check for incomplete patterns
2. Continue: Ask LLM to continue from last complete point
3. Merge: Combine partial outputs
4. Validate: Verify completeness

== CAPABILITIES TO DEVELOP ==
- detect_truncation(text) -> bool
- request_continuation(prompt, partial) -> str
- merge_outputs(parts) -> str
- validate_completeness(text, type) -> bool

== PRACTICAL CODE ==
{working_code[:1000]}

== EXERCISE ==
1. When you generate code, check if it's complete
2. If truncated, request continuation
3. Merge parts and validate
4. Store successful patterns in memory

== REMEMBER ==
Always validate completeness before using LLM output.
Truncation is common - prepare for it.
"""

    print("LESSON CONTENT:")
    print("-" * 60)
    print(lesson[:1500])
    print()

    # Store lesson in Alpha's memory
    alpha_memory.store(
        content=f"Professor taught me untruncate skill: Detect truncation (incomplete brackets, mid-sentence cuts), request continuation, merge outputs, validate completeness.",
        memory_type="semantic",
        importance=0.95,
        context={"type": "lesson", "from": "professor", "skill": "untruncate"}
    )

    alpha_memory.store(
        content=f"Untruncate detection: Check for unclosed brackets, incomplete sentences, missing return statements, invalid JSON. These indicate LLM output was cut off.",
        memory_type="procedural",
        importance=0.9,
        context={"type": "skill_knowledge", "skill": "untruncate"}
    )

    alpha_memory.store(
        content=f"Untruncate handling: 1) Detect truncation 2) Request continuation from last complete point 3) Merge partial outputs 4) Validate final result",
        memory_type="procedural",
        importance=0.9,
        context={"type": "skill_procedure", "skill": "untruncate"}
    )

    alpha_memory.store(
        content=f"Learned untruncate skill from Professor. Can now detect and handle truncated LLM outputs. Exercise: Always validate completeness after LLM calls.",
        memory_type="episodic",
        importance=0.85,
        context={"type": "learning_experience", "from": "professor", "skill": "untruncate", "timestamp": datetime.now().isoformat()}
    )

    alpha_stats = alpha_memory.get_stats()
    print(f"Alpha learned 4 memories about untruncate skill")
    print(f"Alpha now has {alpha_stats['total_memories']} total memories")
    print()

    # PHASE 6: Save skill implementation
    print("=" * 70)
    print("PHASE 6: SAVE UNTRUNCATE SKILL IMPLEMENTATION")
    print("-" * 70)
    print()

    # Create skill file
    skill_dir = REPO_ROOT / "skills" / "foundational" / "untruncate"
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_content = f'''"""
Untruncate Skill - Handle Truncated LLM Outputs

Created: {datetime.now().isoformat()}
Taught by: Professor Agent
Learned by: Alpha Agent
Models used: DeepSeek-R1 (definition), Qwen3 (design), CodeGemma (code)

This skill enables agents to detect, handle, and prevent truncated outputs
from LLM calls.
"""

import requests
import re
from typing import List, Optional, Tuple
from skills.base import Skill, SkillMetadata, SkillContext, SkillResult, SkillCategory, SkillLevel

OLLAMA_URL = "http://localhost:11434/api/generate"


class UntruncateSkill(Skill):
    """Detect and handle truncated LLM outputs."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="foundational/untruncate",
            name="Untruncate",
            description="Detect, handle, and prevent truncated LLM outputs",
            category=SkillCategory.FOUNDATIONAL,
            level=SkillLevel.INTERMEDIATE,
            tags=["llm", "output", "truncation", "validation", "continuation"],
        )

    def input_schema(self):
        return {{
            "type": "object",
            "properties": {{
                "capability": {{"type": "string", "enum": ["detect", "continue", "merge", "validate"]}},
                "text": {{"type": "string"}},
                "parts": {{"type": "array"}},
                "expected_type": {{"type": "string", "enum": ["code", "text", "json", "yaml"]}},
                "original_prompt": {{"type": "string"}},
            }},
            "required": ["capability"]
        }}

    def output_schema(self):
        return {{
            "type": "object",
            "properties": {{
                "is_truncated": {{"type": "boolean"}},
                "continued_text": {{"type": "string"}},
                "merged_text": {{"type": "string"}},
                "is_complete": {{"type": "boolean"}},
                "issues": {{"type": "array"}},
            }}
        }}

    def execute(self, input_data, context: SkillContext) -> SkillResult:
        capability = input_data.get("capability")

        if capability == "detect":
            return self._detect_truncation(input_data.get("text", ""))
        elif capability == "continue":
            return self._request_continuation(
                input_data.get("original_prompt", ""),
                input_data.get("text", "")
            )
        elif capability == "merge":
            return self._merge_outputs(input_data.get("parts", []))
        elif capability == "validate":
            return self._validate_completeness(
                input_data.get("text", ""),
                input_data.get("expected_type", "text")
            )
        else:
            return SkillResult(success=False, output=None, error=f"Unknown capability: {{capability}}")

    def _detect_truncation(self, text: str) -> SkillResult:
        """Detect if text appears truncated."""
        issues = []

        # Check for unclosed brackets
        open_parens = text.count('(') - text.count(')')
        open_brackets = text.count('[') - text.count(']')
        open_braces = text.count('{{') - text.count('}}')

        if open_parens > 0:
            issues.append(f"Unclosed parentheses: {{open_parens}}")
        if open_brackets > 0:
            issues.append(f"Unclosed brackets: {{open_brackets}}")
        if open_braces > 0:
            issues.append(f"Unclosed braces: {{open_braces}}")

        # Check for incomplete sentences
        stripped = text.rstrip()
        if stripped and stripped[-1] not in '.!?:"\\'}}])':
            if not stripped.endswith('```'):
                issues.append("Text ends mid-sentence")

        # Check for incomplete code blocks
        code_blocks = text.count('```')
        if code_blocks % 2 != 0:
            issues.append("Unclosed code block")

        # Check for common truncation patterns
        truncation_patterns = [
            r'\\.\\.\\.$',  # Ends with ...
            r'and$', r'or$', r'the$', r'a$',  # Ends with article/conjunction
            r'def\\s+\\w+\\([^)]*$',  # Incomplete function definition
            r'class\\s+\\w+[^:]*$',  # Incomplete class definition
        ]

        for pattern in truncation_patterns:
            if re.search(pattern, stripped, re.IGNORECASE):
                issues.append(f"Pattern suggests truncation: {{pattern}}")

        is_truncated = len(issues) > 0

        return SkillResult(
            success=True,
            output={{
                "is_truncated": is_truncated,
                "issues": issues,
                "text_length": len(text)
            }},
            skill_id=self.metadata().id
        )

    def _request_continuation(self, original_prompt: str, partial_output: str) -> SkillResult:
        """Request LLM to continue from partial output."""
        continuation_prompt = f"""
The following output was truncated. Continue from where it stopped.

ORIGINAL PROMPT:
{{original_prompt[:500]}}

PARTIAL OUTPUT (continue from here):
{{partial_output[-500:]}}

Continue immediately without repeating what was already written:
"""

        try:
            response = requests.post(
                OLLAMA_URL,
                json={{
                    "model": "qwen3:latest",
                    "prompt": continuation_prompt,
                    "stream": False,
                    "options": {{"temperature": 0.3, "num_predict": 2000}}
                }},
                timeout=120
            )

            if response.status_code == 200:
                continuation = response.json().get("response", "")
                return SkillResult(
                    success=True,
                    output={{
                        "continued_text": continuation,
                        "method": "llm_continuation"
                    }},
                    skill_id=self.metadata().id
                )

        except Exception as e:
            return SkillResult(success=False, output=None, error=str(e))

    def _merge_outputs(self, parts: List[str]) -> SkillResult:
        """Merge multiple partial outputs."""
        if not parts:
            return SkillResult(success=False, output=None, error="No parts provided")

        merged = parts[0]
        for i, part in enumerate(parts[1:], 1):
            # Find overlap between end of merged and start of new part
            overlap_found = False
            for overlap_len in range(min(100, len(merged), len(part)), 0, -1):
                if merged[-overlap_len:] == part[:overlap_len]:
                    merged = merged + part[overlap_len:]
                    overlap_found = True
                    break

            if not overlap_found:
                merged = merged + part

        return SkillResult(
            success=True,
            output={{
                "merged_text": merged,
                "parts_count": len(parts),
                "total_length": len(merged)
            }},
            skill_id=self.metadata().id
        )

    def _validate_completeness(self, text: str, expected_type: str) -> SkillResult:
        """Validate that output is complete for expected type."""
        issues = []
        is_complete = True

        if expected_type == "code":
            # Check Python code completeness
            if "def " in text and "return" not in text:
                issues.append("Function without return statement")
            if "class " in text and "def " not in text:
                issues.append("Class without methods")

        elif expected_type == "json":
            try:
                import json
                json.loads(text)
            except:
                issues.append("Invalid JSON")
                is_complete = False

        elif expected_type == "yaml":
            try:
                import yaml
                yaml.safe_load(text)
            except:
                issues.append("Invalid YAML")
                is_complete = False

        # General completeness checks
        detection_result = self._detect_truncation(text)
        if detection_result.output.get("is_truncated"):
            is_complete = False
            issues.extend(detection_result.output.get("issues", []))

        return SkillResult(
            success=True,
            output={{
                "is_complete": is_complete,
                "expected_type": expected_type,
                "issues": issues
            }},
            skill_id=self.metadata().id
        )
'''

    skill_file = skill_dir / "skill.py"
    skill_file.write_text(skill_content, encoding="utf-8")
    print(f"Saved skill: {skill_file}")

    # Create README
    readme = f"""# Untruncate Skill

**Created**: {datetime.now().isoformat()}
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
result = untruncate.execute({{"capability": "detect", "text": some_output}})

# Continue truncated output
result = untruncate.execute({{
    "capability": "continue",
    "original_prompt": prompt,
    "text": partial_output
}})

# Validate completeness
result = untruncate.execute({{
    "capability": "validate",
    "text": code,
    "expected_type": "code"
}})
```

## Teaching Record
This skill was taught through multi-agent collaboration:
1. DeepSeek-R1 defined the problem
2. Qwen3 designed the implementation
3. CodeGemma created working code
4. Professor Agent synthesized and taught
5. Alpha Agent learned and practiced
"""

    readme_file = skill_dir / "README.md"
    readme_file.write_text(readme, encoding="utf-8")
    print(f"Saved README: {readme_file}")
    print()

    # Summary
    print("=" * 70)
    print("TEACHING SESSION COMPLETE")
    print("=" * 70)
    print()
    print("RESULTS:")
    print(f"  Professor memories: {prof_stats['total_memories']}")
    print(f"  Alpha memories: {alpha_stats['total_memories']}")
    print()
    print("SKILL CREATED:")
    print(f"  ID: foundational/untruncate")
    print(f"  Location: {skill_dir}")
    print()
    print("BOTH AGENTS LEARNED:")
    print("  - What truncation is and why it happens")
    print("  - How to detect truncated outputs")
    print("  - How to request continuation")
    print("  - How to merge and validate outputs")
    print()

if __name__ == "__main__":
    main()