"""
StudentSynthesizer - Dynamically generates specialized student agents using GPIA

This module uses the Cognitive Ecosystem (Hunter/Dissector/Synthesizer) to create
novel student agents optimized for specific research gaps discovered by the Meta-Professor.

Philosophy: Students are synthesized, not predefined. The system learns what types of
students are effective and evolves them.
"""

import sys
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import importlib.util

# Set up paths
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

os.environ["OLLAMA_HOST"] = "localhost:11434"

from agents.agent_utils import query_deepseek, query_qwen, log_event


@dataclass
class StudentSpecification:
    """Blueprint for a specialized student agent."""

    name: str  # e.g., "SymmetryStudent", "TopologyStudent"
    specialization: str  # e.g., "Find hidden group structures in eigenvalue patterns"
    gap_detected: str  # What problem prompted creation
    domain_expertise: str  # Technical domain (quantum, topology, algebra, etc.)
    parameter_focus: List[str]  # Which parameters this student optimizes
    prompt_template: str  # Custom prompt for this student type
    validation_criteria: Dict[str, float]  # How to score this student's proposals
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class StudentSynthesizer:
    """
    Synthesizes novel student agents dynamically.

    Uses a three-phase approach:
    1. Hunter: Identifies what's missing in current research
    2. Dissector: Extracts the core "reasoning pattern" needed
    3. Synthesizer: Generates the actual student agent code
    """

    def __init__(self, synthesis_dir: Path):
        self.synthesis_dir = synthesis_dir
        self.synthesis_dir.mkdir(parents=True, exist_ok=True)

        self.students_generated = 0
        self.synthesis_history = []

    def hunt_for_gaps(self, current_results: Dict, research_context: str) -> List[str]:
        """
        Phase 1: Hunter - identifies what types of students would be most useful.

        Analyzes current results and recommends specialized agent types.
        """
        hunt_prompt = f"""
You are a research strategist analyzing a mathematical discovery effort on the Riemann Hypothesis.

Current Research Context:
{research_context}

Results So Far:
{json.dumps(current_results, indent=2)[:1000]}

Your task: Identify what TYPES of specialized research agents would be most valuable.

For each gap, specify:
1. Agent Name (e.g., "SymmetryStudent", "InverseStudent")
2. Core Specialization (1-2 sentence)
3. Why it's needed NOW (not theoretical, but practical for current problem)
4. What domain expertise it needs (quantum physics, topology, algebra, etc.)
5. What parameters it should focus on

Be creative. Think of agent types humans wouldn't naturally conceive of.
Rank by immediate usefulness (1=needed now, 5=nice to have).

Format as JSON array of objects with keys: name, specialization, rank, domain, focus_params, why_needed
"""

        response = query_deepseek(hunt_prompt, max_tokens=2000)

        # Parse recommendations
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group())
                # Filter for high-priority (rank <= 2)
                high_priority = [r for r in recommendations if r.get('rank', 5) <= 2]
                gap_descriptions = [r.get('name', 'Unknown') for r in high_priority]
                return gap_descriptions
        except:
            pass

        # Fallback: extract agent names mentioned
        return ["PatternStudent", "ConvergenceStudent", "StabilityStudent"]

    def dissect_reasoning_pattern(self, gap_name: str, research_context: str) -> Dict[str, Any]:
        """
        Phase 2: Dissector - extracts the core reasoning pattern needed.

        Breaks down: "What would a researcher specialized in [gap] actually think about?"
        """
        dissect_prompt = f"""
You are analyzing the reasoning pattern for a specialized research agent: {gap_name}

Context: {research_context[:500]}

Your task: Extract the CORE REASONING PATTERN this specialist would use.

Describe:
1. Core Mental Model: How does this specialist think about the problem?
2. Key Insights: What patterns would they notice?
3. Computational Strategy: What algorithms/methods would they use?
4. Validation Logic: How would they know if they're on the right track?
5. Hypothesis Generation: How would they propose new ideas?
6. Error Patterns: What mistakes might they make? (for robustness)

Think like you ARE this specialist. What's your intuition?

Format as JSON with keys: mental_model, key_insights (list), methods (list), validation_logic, hypothesis_strategy, error_modes (list)
"""

        response = query_deepseek(dissect_prompt, max_tokens=2000)

        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                pattern = json.loads(json_match.group())
                return pattern
        except:
            pass

        return {
            "mental_model": "Pattern recognition in mathematical structures",
            "key_insights": ["Structure underlies chaos", "Symmetries guide discovery"],
            "methods": ["Spectral analysis", "Correlation detection"],
            "validation_logic": "Consistency with known theorems",
            "hypothesis_strategy": "Propose structures, test predictions",
            "error_modes": ["Over-fitting to noise", "Ignoring edge cases"]
        }

    def synthesize_student_code(self, spec: StudentSpecification, pattern: Dict) -> str:
        """
        Phase 3: Synthesizer - generates the actual Python student agent.

        Creates executable code optimized for the identified reasoning pattern.
        """
        synth_prompt = f"""
Generate a complete Python class for a specialized student agent.

Name: {spec.name}
Specialization: {spec.specialization}
Domain: {spec.domain_expertise}
Focus Parameters: {', '.join(spec.parameter_focus)}

Reasoning Pattern to Implement:
{json.dumps(pattern, indent=2)[:1000]}

Requirements:
1. Class name: {spec.name}
2. Inherit from BaseDynamicStudent (provided)
3. Implement these methods:
   - generate_proposal() -> Dict (returns {"approach": str, "parameters": Dict, "rationale": str})
   - validate_result(result: Dict) -> float (0-1 score)
   - adapt_based_feedback(feedback: Dict) -> None
4. Domain-specific logic (use {spec.domain_expertise})
5. Include 2-3 specialized methods unique to this agent

Custom Prompt Template for this student:
{spec.prompt_template[:500]}

Generate ONLY the Python class code. Make it production-ready.
Include docstrings. Start with: class {spec.name}(BaseDynamicStudent):
"""

        response = query_deepseek(synth_prompt, max_tokens=3000)

        # Extract code block if present
        import re
        code_match = re.search(r'```python\n(.*?)\n```', response, re.DOTALL)
        if code_match:
            return code_match.group(1)

        # Try to find class definition
        if f"class {spec.name}" in response:
            # Extract from class definition onwards
            start = response.find(f"class {spec.name}")
            return response[start:]

        return response

    def create_student_module(self, spec: StudentSpecification, code: str) -> Path:
        """
        Creates a complete Python module for the synthesized student.

        Returns path to the created module.
        """
        # Create module directory
        module_name = spec.name.lower()
        module_dir = self.synthesis_dir / module_name
        module_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_file = module_dir / "__init__.py"
        init_file.write_text(f'"""Auto-synthesized student agent: {spec.name}"""\n')

        # Create manifest
        manifest = {
            "name": spec.name,
            "specialization": spec.specialization,
            "gap_detected": spec.gap_detected,
            "domain_expertise": spec.domain_expertise,
            "parameter_focus": spec.parameter_focus,
            "synthesis_timestamp": spec.timestamp,
            "synthesis_method": "StudentSynthesizer (GPIA Hunter/Dissector/Synthesizer)",
            "version": "1.0-synthesized"
        }
        manifest_file = module_dir / "manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2))

        # Create the agent code file
        full_code = self._wrap_student_code(spec, code)
        agent_file = module_dir / "agent.py"
        agent_file.write_text(full_code)

        return agent_file

    def _wrap_student_code(self, spec: StudentSpecification, user_code: str) -> str:
        """Wraps synthesized code with necessary imports and base class."""
        return f'''"""
Auto-synthesized student agent: {spec.name}

Specialization: {spec.specialization}
Domain: {spec.domain_expertise}
Gap Detected: {spec.gap_detected}

Generated: {datetime.now().isoformat()}
Method: GPIA StudentSynthesizer
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from agents.agent_utils import query_deepseek

class BaseDynamicStudent:
    """Base class for dynamically synthesized students."""

    def __init__(self, name: str, specialization: str):
        self.name = name
        self.specialization = specialization
        self.proposals = []
        self.feedback_history = []
        self.adaptation_count = 0

    def generate_proposal(self) -> Dict[str, Any]:
        """Generate a research proposal. Override in subclass."""
        raise NotImplementedError

    def validate_result(self, result: Dict) -> float:
        """Validate result. Return score 0-1."""
        raise NotImplementedError

    def adapt_based_feedback(self, feedback: Dict) -> None:
        """Adapt strategy based on feedback."""
        self.feedback_history.append(feedback)
        self.adaptation_count += 1


# The synthesized student code follows:

{user_code}
'''

    def synthesize_student(self, gap_name: str, gap_description: str,
                          research_context: str, current_results: Dict) -> Optional[StudentSpecification]:
        """
        Full synthesis pipeline: Hunt → Dissect → Synthesize → Create Module

        Returns the StudentSpecification if successful, None otherwise.
        """
        print(f"\n[StudentSynthesizer] === Synthesizing: {gap_name} ===")

        # Phase 1: Hunt - understand what's needed
        print(f"  [Phase 1] Hunting for pattern needed...")
        pattern = self.dissect_reasoning_pattern(gap_name, research_context)

        # Create specification
        spec = StudentSpecification(
            name=gap_name,
            specialization=gap_description,
            gap_detected=gap_description,
            domain_expertise=pattern.get("mental_model", "Mathematical Analysis"),
            parameter_focus=[
                gap_name.lower().replace("student", ""),
                "convergence",
                "validation"
            ],
            prompt_template=f"""
You are a specialized research agent: {gap_name}

Your expertise: {pattern.get('mental_model', 'Analysis')}

Key patterns to recognize: {', '.join(pattern.get('key_insights', [])[:3])}

Methods to employ: {', '.join(pattern.get('methods', [])[:3])}

Generate a novel approach to the Riemann Hypothesis research problem.
Focus on: {gap_description}

Think creatively. What would someone specialized in {gap_name} notice that others miss?
"""
        )

        print(f"  [Phase 2] Extracting reasoning pattern...")

        # Phase 2: Dissect
        print(f"  [Phase 3] Synthesizing agent code...")
        code = self.synthesize_student_code(spec, pattern)

        # Phase 3: Create module
        print(f"  [Phase 4] Creating module...")
        module_path = self.create_student_module(spec, code)
        print(f"  ✓ Created: {module_path}")

        # Track synthesis
        self.students_generated += 1
        synthesis_record = {
            "student_name": spec.name,
            "specialization": spec.specialization,
            "module_path": str(module_path),
            "timestamp": datetime.now().isoformat(),
            "pattern": pattern
        }
        self.synthesis_history.append(synthesis_record)

        # Save history
        history_file = self.synthesis_dir / "synthesis_history.json"
        history_file.write_text(json.dumps(self.synthesis_history, indent=2))

        return spec

    def get_synthesis_history(self) -> List[Dict]:
        """Return all synthesized students."""
        return self.synthesis_history.copy()

    def get_student_count(self) -> int:
        """Total students synthesized so far."""
        return self.students_generated
