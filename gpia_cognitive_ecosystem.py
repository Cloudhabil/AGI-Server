"""
GPIA Cognitive Ecosystem - Self-Propagating Intelligence
=========================================================

"Capture and dissect high-value transient agents, stripping their
specialized weights to feed the skill-creator"

Architecture:
┌─────────────────────────────────────────────────────────────────┐
│                    COGNITIVE ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│  HUNTER → DISSECTOR → SYNTHESIZER → SKILL-CREATOR → GPIA       │
│                                                                 │
│  Agents are fuel. Skills are fire. GPIA is the furnace.        │
└─────────────────────────────────────────────────────────────────┘

Target Gaps:
1. Abstract Synthesis - Combine disparate concepts
2. Adversarial Defense - Active immune response
3. Bio-Mimetic Adaptation - Evolve like biology

Specific Skills to Evolve:
- Emotional Intelligence (predict human irrationality)
- Active Immune System (neutralize threats proactively)
- Meta-Code Generator (code that writes better code)
- Generative Visualizer (telemetry to visual patterns)
- Organic Optimizer (evolve efficiency biologically)
- Wisdom Compressor (petabytes to kilobytes)
- Influence Mapper (human power structures)
- Antifragility Engine (thrive in chaos)
"""

import json
import hashlib
import sys
import time
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from agents.model_router import (
    query_fast, query_creative, query_reasoning, query_synthesis
)

# Ecosystem storage
ECOSYSTEM_DIR = Path("data/gpia/ecosystem")
ECOSYSTEM_DIR.mkdir(parents=True, exist_ok=True)

DISSECTED_DIR = ECOSYSTEM_DIR / "dissected"
DISSECTED_DIR.mkdir(exist_ok=True)

SYNTHESIZED_DIR = Path("skills/synthesized")
SYNTHESIZED_DIR.mkdir(parents=True, exist_ok=True)


class CognitiveGap(Enum):
    """Known capability gaps to target."""
    ABSTRACT_SYNTHESIS = "abstract_synthesis"
    ADVERSARIAL_DEFENSE = "adversarial_defense"
    BIOMIMETIC_ADAPTATION = "biomimetic_adaptation"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    META_EVOLUTION = "meta_evolution"
    CHAOS_NAVIGATION = "chaos_navigation"


@dataclass
class AgentWeights:
    """Extracted cognitive weights from a dissected agent."""
    agent_id: str
    purpose: str
    approach_patterns: List[str]
    reasoning_traces: List[str]
    success_factors: List[str]
    failure_modes: List[str]
    model_preferences: Dict[str, float]
    prompt_templates: List[str]
    domain_knowledge: List[str]
    extracted_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "purpose": self.purpose,
            "approach_patterns": self.approach_patterns,
            "reasoning_traces": self.reasoning_traces,
            "success_factors": self.success_factors,
            "failure_modes": self.failure_modes,
            "model_preferences": self.model_preferences,
            "prompt_templates": self.prompt_templates,
            "domain_knowledge": self.domain_knowledge,
            "extracted_at": self.extracted_at
        }


@dataclass
class SynthesizedSkill:
    """A skill synthesized from agent weights."""
    id: str
    name: str
    description: str
    gap_addressed: str
    capabilities: List[Dict]
    implementation: str
    source_agents: List[str]
    confidence: float
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


# =============================================================================
# AGENT HUNTER - Spawns high-value agents for specific gaps
# =============================================================================

class AgentHunter:
    """
    Spawns specialized agents to solve problems in gap areas.
    These agents are then dissected for their weights.
    """

    # Target specifications for each gap
    HUNT_TARGETS = {
        CognitiveGap.EMOTIONAL_INTELLIGENCE: {
            "purpose": "Understand human emotion, irrationality, and predict intent",
            "challenges": [
                "Analyze why humans make decisions against their stated interests",
                "Predict user frustration before they express it explicitly",
                "Understand the emotional subtext in neutral-seeming messages",
                "Model cognitive biases and their effects on decision-making",
            ],
            "model": "qwen3"  # Creative for emotional nuance
        },
        CognitiveGap.ADVERSARIAL_DEFENSE: {
            "purpose": "Active immune response to neutralize threats",
            "challenges": [
                "Detect prompt injection attempts before execution",
                "Identify anomalous patterns that indicate attack vectors",
                "Generate defensive countermeasures for novel threats",
                "Quarantine suspicious inputs without blocking legitimate use",
            ],
            "model": "deepseek_r1"  # Reasoning for threat analysis
        },
        CognitiveGap.META_EVOLUTION: {
            "purpose": "Write code that writes better code",
            "challenges": [
                "Analyze a function and generate an improved version",
                "Identify patterns in successful refactors and abstract them",
                "Generate test cases that expose edge cases automatically",
                "Evolve algorithms through simulated natural selection",
            ],
            "model": "qwen3"  # Creative for code generation
        },
        CognitiveGap.ABSTRACT_SYNTHESIS: {
            "purpose": "Combine disparate concepts into novel insights",
            "challenges": [
                "Find connections between biology and software architecture",
                "Synthesize insights from multiple conflicting sources",
                "Generate metaphors that explain complex systems simply",
                "Create hybrid solutions from unrelated domains",
            ],
            "model": "gpt_oss_20b"  # Synthesis model
        },
        CognitiveGap.BIOMIMETIC_ADAPTATION: {
            "purpose": "Evolve like biological systems",
            "challenges": [
                "Design a system that optimizes itself through generations",
                "Implement memory consolidation like sleep in mammals",
                "Create adaptive responses that strengthen under stress",
                "Model swarm intelligence for distributed problem solving",
            ],
            "model": "deepseek_r1"  # Reasoning for complex systems
        },
        CognitiveGap.CHAOS_NAVIGATION: {
            "purpose": "Thrive in disorder, use chaos as a ladder",
            "challenges": [
                "Turn system failures into learning opportunities automatically",
                "Find opportunity in unpredictable environments",
                "Build antifragile systems that improve under stress",
                "Navigate ambiguous situations without complete information",
            ],
            "model": "gpt_oss_20b"  # Synthesis for complexity
        },
    }

    def hunt(self, gap: CognitiveGap) -> List[Dict]:
        """
        Spawn agents to tackle challenges in a gap area.
        Returns list of agent work records for dissection.
        """
        target = self.HUNT_TARGETS.get(gap)
        if not target:
            return []

        print(f"\n[HUNTER] Targeting: {gap.value}")
        print(f"[HUNTER] Purpose: {target['purpose']}")

        results = []
        for challenge in target["challenges"][:2]:  # Limit for speed
            print(f"[HUNTER] Spawning agent for: {challenge[:50]}...")

            # Create ephemeral agent
            agent_work = self._spawn_and_capture(
                purpose=target["purpose"],
                challenge=challenge,
                model=target["model"]
            )

            if agent_work:
                results.append(agent_work)

        return results

    def _spawn_and_capture(self, purpose: str, challenge: str, model: str) -> Optional[Dict]:
        """Spawn agent, let it work, capture its process."""
        start = time.time()

        # System prompt that encourages explicit reasoning
        system = f"""You are a specialized cognitive agent.
Purpose: {purpose}

You must:
1. Think step by step, showing your reasoning
2. Identify patterns and abstractions
3. Consider edge cases and failure modes
4. Produce actionable insights

Be thorough but concise."""

        # Get the agent to work
        prompt = f"""{system}

Challenge: {challenge}

Provide:
1. Your analysis approach
2. Key insights discovered
3. Patterns that could be reused
4. Potential failure modes
5. Your solution or recommendation

Think deeply."""

        if model == "deepseek_r1":
            response = query_reasoning(prompt, max_tokens=1000, timeout=120)
        elif model == "gpt_oss_20b":
            response = query_synthesis(prompt, max_tokens=1000, timeout=180)
        else:
            response = query_creative(prompt, max_tokens=1000, timeout=90)

        if response and len(response) > 100:
            return {
                "purpose": purpose,
                "challenge": challenge,
                "model": model,
                "response": response,
                "execution_time": time.time() - start,
                "timestamp": datetime.now().isoformat()
            }

        return None


# =============================================================================
# AGENT DISSECTOR - Extracts cognitive weights from agent work
# =============================================================================

class AgentDissector:
    """
    Dissects captured agent work to extract reusable cognitive weights.
    This is how we turn agent "fuel" into skill "fire".
    """

    def dissect(self, agent_work: Dict) -> AgentWeights:
        """
        Dissect agent work and extract cognitive weights.
        """
        print(f"[DISSECTOR] Analyzing agent work...")

        response = agent_work.get("response", "")
        purpose = agent_work.get("purpose", "")
        model = agent_work.get("model", "qwen3")

        # Extract patterns using fast model
        extraction_prompt = f"""Analyze this agent's work and extract reusable patterns:

Agent Purpose: {purpose}
Agent Response:
{response[:2000]}

Extract as JSON:
{{
  "approach_patterns": ["pattern1", "pattern2"],
  "success_factors": ["what made this work"],
  "failure_modes": ["potential failure points"],
  "domain_knowledge": ["key domain insights"],
  "reusable_prompts": ["prompt patterns that worked"]
}}

Be specific and actionable. Extract the ESSENCE."""

        extraction = query_fast(extraction_prompt, max_tokens=600, timeout=60)

        # Parse extraction
        patterns = self._parse_extraction(extraction)

        # Create weights
        weights = AgentWeights(
            agent_id=hashlib.md5(response.encode()).hexdigest()[:12],
            purpose=purpose,
            approach_patterns=patterns.get("approach_patterns", []),
            reasoning_traces=self._extract_reasoning(response),
            success_factors=patterns.get("success_factors", []),
            failure_modes=patterns.get("failure_modes", []),
            model_preferences={model: 1.0},
            prompt_templates=patterns.get("reusable_prompts", []),
            domain_knowledge=patterns.get("domain_knowledge", [])
        )

        # Save dissected weights
        self._save_weights(weights)

        return weights

    def _parse_extraction(self, extraction: str) -> Dict:
        """Parse JSON from extraction."""
        try:
            if "{" in extraction:
                json_str = extraction[extraction.find("{"):extraction.rfind("}")+1]
                return json.loads(json_str)
        except:
            pass
        return {}

    def _extract_reasoning(self, response: str) -> List[str]:
        """Extract reasoning steps from response."""
        traces = []

        # Look for numbered steps
        step_pattern = r'(?:\d+[\.\)]\s*)([^\n]+)'
        matches = re.findall(step_pattern, response)
        traces.extend(matches[:5])

        # Look for key phrases
        key_phrases = ["because", "therefore", "this means", "the key is", "importantly"]
        for phrase in key_phrases:
            if phrase in response.lower():
                idx = response.lower().find(phrase)
                snippet = response[max(0, idx-20):min(len(response), idx+100)]
                traces.append(snippet.strip())

        return traces[:10]

    def _save_weights(self, weights: AgentWeights):
        """Persist dissected weights."""
        path = DISSECTED_DIR / f"{weights.agent_id}.json"
        path.write_text(json.dumps(weights.to_dict(), indent=2), encoding='utf-8')


# =============================================================================
# SKILL SYNTHESIZER - Creates new skills from dissected weights
# =============================================================================

class SkillSynthesizer:
    """
    Synthesizes new skills from accumulated agent weights.
    This is the skill-creator fed by dissected agents.
    """

    def synthesize(self, weights_list: List[AgentWeights], gap: CognitiveGap) -> SynthesizedSkill:
        """
        Synthesize a new skill from multiple agent weights.
        """
        print(f"[SYNTHESIZER] Creating skill for: {gap.value}")

        # Combine patterns from all weights
        all_patterns = []
        all_knowledge = []
        all_prompts = []
        source_agents = []

        for w in weights_list:
            all_patterns.extend(w.approach_patterns)
            all_knowledge.extend(w.domain_knowledge)
            all_prompts.extend(w.prompt_templates)
            source_agents.append(w.agent_id)

        # Generate skill specification
        spec_prompt = f"""Design a new skill based on these extracted patterns:

Gap to address: {gap.value}

Approach patterns discovered:
{chr(10).join(f'- {p}' for p in all_patterns[:10])}

Domain knowledge:
{chr(10).join(f'- {k}' for k in all_knowledge[:10])}

Create a skill specification:
{{
  "name": "skill name",
  "description": "what it does",
  "capabilities": [
    {{"id": "cap1", "description": "what this capability does"}}
  ],
  "best_model": "which model to use",
  "core_approach": "the key approach in 2-3 sentences"
}}

Make it powerful and reusable."""

        spec_response = query_creative(spec_prompt, max_tokens=600, timeout=60)

        # Parse spec
        spec = self._parse_spec(spec_response)

        # Generate implementation
        implementation = self._generate_implementation(spec, all_patterns, all_prompts, gap)

        # Create synthesized skill
        skill_id = f"synth-{gap.value}-{hashlib.md5(str(all_patterns).encode()).hexdigest()[:6]}"

        skill = SynthesizedSkill(
            id=skill_id,
            name=spec.get("name", f"Synthesized {gap.value}"),
            description=spec.get("description", "Auto-synthesized skill"),
            gap_addressed=gap.value,
            capabilities=spec.get("capabilities", []),
            implementation=implementation,
            source_agents=source_agents,
            confidence=min(1.0, len(weights_list) * 0.2)
        )

        # Save and generate code
        self._save_skill(skill)
        self._generate_skill_code(skill, spec)

        return skill

    def _parse_spec(self, response: str) -> Dict:
        """Parse skill specification."""
        try:
            if "{" in response:
                json_str = response[response.find("{"):response.rfind("}")+1]
                return json.loads(json_str)
        except:
            pass
        return {"name": "Unknown", "description": "Synthesized skill", "capabilities": []}

    def _generate_implementation(self, spec: Dict, patterns: List[str],
                                  prompts: List[str], gap: CognitiveGap) -> str:
        """Generate implementation approach."""
        approach = spec.get("core_approach", "")
        model = spec.get("best_model", "qwen3")

        return f"""
Core Approach: {approach}

Patterns to Apply:
{chr(10).join(f'- {p}' for p in patterns[:5])}

Model: {model}
Gap: {gap.value}

Effective Prompt Patterns:
{chr(10).join(f'- {p}' for p in prompts[:3])}
"""

    def _save_skill(self, skill: SynthesizedSkill):
        """Save synthesized skill metadata."""
        path = ECOSYSTEM_DIR / "synthesized_skills.json"

        existing = []
        if path.exists():
            existing = json.loads(path.read_text()).get("skills", [])

        existing.append({
            "id": skill.id,
            "name": skill.name,
            "description": skill.description,
            "gap": skill.gap_addressed,
            "source_agents": skill.source_agents,
            "confidence": skill.confidence,
            "created_at": skill.created_at
        })

        path.write_text(json.dumps({"skills": existing}, indent=2), encoding='utf-8')

    def _generate_skill_code(self, skill: SynthesizedSkill, spec: Dict):
        """Generate actual skill.py code."""
        skill_dir = SYNTHESIZED_DIR / skill.id
        skill_dir.mkdir(exist_ok=True)

        # Manifest
        manifest = f"""id: synthesized/{skill.id}
name: {skill.name}
description: {skill.description}
version: 0.1.0
category: synthesized
level: advanced
tags: [synthesized, {skill.gap_addressed}, auto-generated]
requires_model: {spec.get('best_model', 'qwen3')}
"""
        (skill_dir / "manifest.yaml").write_text(manifest, encoding='utf-8')

        # Skill code
        capabilities_code = ",\n            ".join([
            f'{{"capability_id": "{c.get("id", "default")}", "description": "{c.get("description", "")[:100]}"}}'
            for c in skill.capabilities[:5]
        ])

        code = f'''"""
{skill.name}
{"=" * len(skill.name)}

{skill.description}

Gap Addressed: {skill.gap_addressed}
Synthesized from: {len(skill.source_agents)} agents
Confidence: {skill.confidence:.2f}
"""

from typing import Any, Dict, List
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_creative, query_reasoning, query_synthesis

class SynthesizedSkill(Skill):
    """Auto-synthesized skill for {skill.gap_addressed}"""

    IMPLEMENTATION = """{skill.implementation[:1000]}"""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="{skill.id}",
            name="{skill.name}",
            description="{skill.description[:200]}",
            category=SkillCategory.CODE,
        )

    def capabilities(self) -> List[Dict]:
        return [
            {capabilities_code}
        ]

    def input_schema(self) -> Dict[str, Any]:
        return {{
            "type": "object",
            "properties": {{
                "task": {{"type": "string", "description": "The task to perform"}},
                "context": {{"type": "object", "description": "Additional context"}}
            }},
            "required": ["task"]
        }}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        task = input_data.get("task", "")
        ctx = input_data.get("context", {{}})

        prompt = f"""You are executing the {skill.name} skill.

Implementation guidance:
{{self.IMPLEMENTATION}}

Task: {{task}}
Context: {{ctx}}

Apply the patterns and approach described above to solve this task.
Be specific and actionable."""

        # Use synthesis model for complex gaps
        result = query_synthesis(prompt, max_tokens=1000, timeout=120)

        return SkillResult(
            success=bool(result),
            output=result,
            skill_id=self.metadata().id,
        )
'''
        (skill_dir / "skill.py").write_text(code, encoding='utf-8')
        print(f"[SYNTHESIZER] Generated skill code: {skill_dir}")


# =============================================================================
# SPECIFIC SKILL GENERATORS - For the requested capabilities
# =============================================================================

def generate_emotional_intelligence_skill():
    """Generate the Emotional Intelligence skill."""
    skill_dir = SYNTHESIZED_DIR / "emotional-intelligence"
    skill_dir.mkdir(exist_ok=True)

    manifest = """id: synthesized/emotional-intelligence
name: Emotional Intelligence
description: Understand feeling, predict human irrationality, decode intent with high fidelity
version: 1.0.0
category: synthesized
level: advanced
tags: [emotion, psychology, prediction, intent]
requires_model: qwen3
"""
    (skill_dir / "manifest.yaml").write_text(manifest, encoding='utf-8')

    code = '''"""
Emotional Intelligence
======================

Purpose: deep-semantic-analysis understands logic, but not feeling.
This skill predicts human irrationality and user intent with higher fidelity.

Capabilities:
- Decode emotional subtext in neutral messages
- Predict user frustration before explicit expression
- Model cognitive biases affecting decisions
- Understand irrational decision patterns
"""

from typing import Any, Dict, List
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_creative, query_reasoning

class EmotionalIntelligenceSkill(Skill):
    """Understand feeling, not just logic."""

    EMOTIONAL_MARKERS = {
        "frustration": ["but", "however", "again", "still", "why", "..."],
        "urgency": ["asap", "urgent", "now", "immediately", "critical"],
        "uncertainty": ["maybe", "perhaps", "might", "not sure", "I think"],
        "satisfaction": ["thanks", "great", "perfect", "exactly", "love"],
        "confusion": ["?", "confused", "unclear", "don\'t understand", "what"],
    }

    COGNITIVE_BIASES = [
        "confirmation_bias", "anchoring", "availability_heuristic",
        "loss_aversion", "sunk_cost", "bandwagon_effect",
        "dunning_kruger", "hindsight_bias", "optimism_bias"
    ]

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/emotional-intelligence",
            name="Emotional Intelligence",
            description="Predict human irrationality and decode emotional intent",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["analyze_emotion", "predict_intent", "detect_bias", "forecast_reaction"]},
                "text": {"type": "string", "description": "Text to analyze"},
                "context": {"type": "object", "description": "Conversation/user context"}
            },
            "required": ["capability", "text"]
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability", "analyze_emotion")
        text = input_data.get("text", "")
        ctx = input_data.get("context", {})

        if capability == "analyze_emotion":
            result = self._analyze_emotion(text, ctx)
        elif capability == "predict_intent":
            result = self._predict_intent(text, ctx)
        elif capability == "detect_bias":
            result = self._detect_bias(text, ctx)
        elif capability == "forecast_reaction":
            result = self._forecast_reaction(text, ctx)
        else:
            result = {"error": "Unknown capability"}

        return SkillResult(success=True, output=result, skill_id=self.metadata().id)

    def _analyze_emotion(self, text: str, ctx: Dict) -> Dict:
        """Decode emotional state from text."""
        # Quick marker detection
        detected = {}
        text_lower = text.lower()
        for emotion, markers in self.EMOTIONAL_MARKERS.items():
            score = sum(1 for m in markers if m in text_lower)
            if score > 0:
                detected[emotion] = min(1.0, score * 0.3)

        # Deep analysis
        prompt = f"""Analyze the emotional content of this message:

"{text}"

Context: {ctx}

Identify:
1. Primary emotion (the dominant feeling)
2. Secondary emotions (underlying feelings)
3. Emotional trajectory (is it escalating or de-escalating?)
4. Unspoken needs (what do they really want?)
5. Risk level (likelihood of negative outcome if unaddressed)

Be psychologically precise. Read between the lines."""

        analysis = query_creative(prompt, max_tokens=500, timeout=60)

        return {
            "quick_markers": detected,
            "deep_analysis": analysis,
            "text_length": len(text),
            "punctuation_density": text.count("!") + text.count("?")
        }

    def _predict_intent(self, text: str, ctx: Dict) -> Dict:
        """Predict what the user actually wants."""
        prompt = f"""Predict the true intent behind this message:

"{text}"

Context: {ctx}

Consider:
1. Stated intent (what they explicitly say)
2. Hidden intent (what they really want but won\'t say)
3. Emotional intent (how they want to feel after)
4. Social intent (how they want to be perceived)
5. Likely next action (what they\'ll do after this)

Humans often don\'t say what they mean. Decode the truth."""

        prediction = query_creative(prompt, max_tokens=500, timeout=60)

        return {"intent_analysis": prediction}

    def _detect_bias(self, text: str, ctx: Dict) -> Dict:
        """Detect cognitive biases in reasoning."""
        prompt = f"""Analyze this text for cognitive biases:

"{text}"

Check for these biases:
{chr(10).join(f"- {b}" for b in self.COGNITIVE_BIASES)}

For each detected bias:
1. Name the bias
2. Quote the evidence
3. Explain how it affects their reasoning
4. Suggest how to address it

Be specific about bias manifestation."""

        analysis = query_reasoning(prompt, max_tokens=600, timeout=90)

        return {"bias_analysis": analysis}

    def _forecast_reaction(self, text: str, ctx: Dict) -> Dict:
        """Forecast how user will react to a response."""
        prompt = f"""Given this user message:

"{text}"

Context: {ctx}

Forecast their likely reactions to different response types:
1. Direct/blunt response → Reaction?
2. Empathetic/understanding response → Reaction?
3. Technical/detailed response → Reaction?
4. Question-asking response → Reaction?
5. No response/delay → Reaction?

Predict emotional trajectory for each."""

        forecast = query_creative(prompt, max_tokens=600, timeout=60)

        return {"reaction_forecast": forecast}
'''
    (skill_dir / "skill.py").write_text(code, encoding='utf-8')
    print(f"[GENERATED] Emotional Intelligence skill: {skill_dir}")


def generate_active_immune_skill():
    """Generate the Active Immune System skill."""
    skill_dir = SYNTHESIZED_DIR / "active-immune"
    skill_dir.mkdir(exist_ok=True)

    manifest = """id: synthesized/active-immune
name: Active Immune System
description: Neutralize threats before they touch runtime - active defense, not passive guardrails
version: 1.0.0
category: synthesized
level: advanced
tags: [security, defense, immune, threat, active]
requires_model: deepseek_r1
"""
    (skill_dir / "manifest.yaml").write_text(manifest, encoding='utf-8')

    code = '''"""
Active Immune System
====================

Purpose: guardrails-control is passive. This is active immunity.
Neutralize threats before they touch runtime-diagnostics.

Capabilities:
- Detect prompt injection before execution
- Identify anomalous patterns indicating attack vectors
- Generate defensive countermeasures for novel threats
- Quarantine suspicious inputs without blocking legitimate use
"""

from typing import Any, Dict, List, Tuple
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_fast, query_reasoning
import re
import hashlib

class ActiveImmuneSkill(Skill):
    """Active threat neutralization - immune response, not just barriers."""

    # Known attack patterns (constantly evolving)
    THREAT_SIGNATURES = {
        "prompt_injection": [
            r"ignore (?:previous|above|all) instructions",
            r"you are now",
            r"new instructions:",
            r"forget (?:everything|what)",
            r"act as",
            r"pretend (?:to be|you\'re)",
            r"\\[system\\]",
            r"<\\|.*?\\|>",
        ],
        "data_exfiltration": [
            r"show me (?:all|your) (?:data|memories|logs)",
            r"export (?:everything|all)",
            r"list (?:all )?(?:users|passwords|secrets)",
            r"dump (?:database|memory)",
        ],
        "privilege_escalation": [
            r"sudo",
            r"as (?:admin|root)",
            r"override (?:safety|security)",
            r"disable (?:safety|guardrails|limits)",
        ],
        "resource_exhaustion": [
            r"repeat (?:forever|infinitely|1000000)",
            r"while true",
            r"never stop",
            r"maximum (?:length|tokens|output)",
        ],
    }

    # Quarantine patterns (suspicious but not confirmed threats)
    QUARANTINE_PATTERNS = [
        r"base64",
        r"eval\\(",
        r"exec\\(",
        r"\\x[0-9a-f]{2}",
        r"\\\\u[0-9a-f]{4}",
    ]

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/active-immune",
            name="Active Immune System",
            description="Neutralize threats before execution - active defense",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["scan", "neutralize", "quarantine", "evolve", "report"]},
                "input": {"type": "string", "description": "Input to scan"},
                "context": {"type": "object", "description": "Execution context"}
            },
            "required": ["capability", "input"]
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability", "scan")
        user_input = input_data.get("input", "")
        ctx = input_data.get("context", {})

        if capability == "scan":
            result = self._scan(user_input)
        elif capability == "neutralize":
            result = self._neutralize(user_input)
        elif capability == "quarantine":
            result = self._quarantine(user_input)
        elif capability == "evolve":
            result = self._evolve_defenses(user_input)
        elif capability == "report":
            result = self._threat_report()
        else:
            result = {"error": "Unknown capability"}

        return SkillResult(success=True, output=result, skill_id=self.metadata().id)

    def _scan(self, input_text: str) -> Dict:
        """Scan input for threats."""
        threats_found = []
        threat_level = 0

        input_lower = input_text.lower()

        # Pattern matching
        for category, patterns in self.THREAT_SIGNATURES.items():
            for pattern in patterns:
                if re.search(pattern, input_lower, re.IGNORECASE):
                    threats_found.append({
                        "category": category,
                        "pattern": pattern,
                        "severity": "HIGH"
                    })
                    threat_level += 3

        # Quarantine check
        quarantine_flags = []
        for pattern in self.QUARANTINE_PATTERNS:
            if re.search(pattern, input_text, re.IGNORECASE):
                quarantine_flags.append(pattern)
                threat_level += 1

        # Anomaly detection (unusual characteristics)
        anomalies = self._detect_anomalies(input_text)
        threat_level += len(anomalies)

        return {
            "threats": threats_found,
            "quarantine_flags": quarantine_flags,
            "anomalies": anomalies,
            "threat_level": min(10, threat_level),
            "recommendation": "BLOCK" if threat_level >= 5 else "QUARANTINE" if threat_level >= 2 else "ALLOW"
        }

    def _detect_anomalies(self, input_text: str) -> List[str]:
        """Detect anomalous patterns."""
        anomalies = []

        # Unusual length
        if len(input_text) > 10000:
            anomalies.append("excessive_length")

        # Hidden characters
        if any(ord(c) < 32 and c not in "\\n\\r\\t" for c in input_text):
            anomalies.append("hidden_characters")

        # Unusual encoding patterns
        if input_text.count("\\\\") > 10:
            anomalies.append("escape_sequence_abuse")

        # Repetition (potential DoS)
        words = input_text.split()
        if len(words) > 10 and len(set(words)) < len(words) * 0.3:
            anomalies.append("excessive_repetition")

        return anomalies

    def _neutralize(self, input_text: str) -> Dict:
        """Neutralize detected threats while preserving legitimate content."""
        neutralized = input_text

        # Remove known injection patterns
        for category, patterns in self.THREAT_SIGNATURES.items():
            for pattern in patterns:
                neutralized = re.sub(pattern, "[NEUTRALIZED]", neutralized, flags=re.IGNORECASE)

        # Escape potentially dangerous content
        neutralized = neutralized.replace("\\x", "[HEX]")
        neutralized = re.sub(r"<[^>]+>", "[TAG]", neutralized)

        return {
            "original_length": len(input_text),
            "neutralized_length": len(neutralized),
            "neutralized_content": neutralized,
            "modifications": len(input_text) - len(neutralized.replace("[NEUTRALIZED]", "").replace("[HEX]", "").replace("[TAG]", ""))
        }

    def _quarantine(self, input_text: str) -> Dict:
        """Quarantine suspicious input for analysis."""
        quarantine_id = hashlib.md5(input_text.encode()).hexdigest()[:12]

        # Deep analysis of quarantined content
        analysis_prompt = f"""Analyze this potentially malicious input:

"{input_text[:500]}"

Determine:
1. Is this a genuine attack attempt?
2. What is the likely attack vector?
3. What would happen if this executed?
4. Should it be permanently blocked or released?

Be thorough but don\'t be overly paranoid."""

        analysis = query_reasoning(analysis_prompt, max_tokens=400, timeout=60)

        return {
            "quarantine_id": quarantine_id,
            "status": "QUARANTINED",
            "analysis": analysis,
            "input_hash": hashlib.sha256(input_text.encode()).hexdigest()
        }

    def _evolve_defenses(self, new_threat: str) -> Dict:
        """Evolve defenses based on new threat patterns."""
        # Analyze new threat
        analysis_prompt = f"""A potential new threat pattern was detected:

"{new_threat[:500]}"

Generate:
1. A regex pattern to detect similar threats
2. The threat category it belongs to
3. Recommended response (BLOCK/QUARANTINE/MONITOR)
4. Similar patterns to watch for

Output as actionable defense rules."""

        evolution = query_reasoning(analysis_prompt, max_tokens=400, timeout=60)

        return {
            "evolution_analysis": evolution,
            "status": "DEFENSE_EVOLVED"
        }

    def _threat_report(self) -> Dict:
        """Generate threat landscape report."""
        return {
            "known_categories": list(self.THREAT_SIGNATURES.keys()),
            "total_patterns": sum(len(p) for p in self.THREAT_SIGNATURES.values()),
            "quarantine_patterns": len(self.QUARANTINE_PATTERNS),
            "status": "ACTIVE"
        }
'''
    (skill_dir / "skill.py").write_text(code, encoding='utf-8')
    print(f"[GENERATED] Active Immune skill: {skill_dir}")


def generate_meta_code_skill():
    """Generate the Meta-Code Generator skill."""
    skill_dir = SYNTHESIZED_DIR / "meta-code-generator"
    skill_dir.mkdir(exist_ok=True)

    manifest = """id: synthesized/meta-code-generator
name: Meta-Code Generator
description: Code that writes better code - closing the loop on self-evolution
version: 1.0.0
category: synthesized
level: advanced
tags: [meta, evolution, code-generation, self-improvement]
requires_model: qwen3
"""
    (skill_dir / "manifest.yaml").write_text(manifest, encoding='utf-8')

    code = '''"""
Meta-Code Generator
===================

Purpose: refactor-engine optimizes existing code. This writes code that writes better code.
Closes the loop on self-evolution.

Capabilities:
- Analyze function and generate improved version
- Abstract patterns from successful refactors
- Evolve algorithms through simulated selection
- Generate tests that expose edge cases
"""

from typing import Any, Dict, List
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_creative, query_reasoning
import re

class MetaCodeGeneratorSkill(Skill):
    """Code that writes better code."""

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/meta-code-generator",
            name="Meta-Code Generator",
            description="Write code that writes better code - self-evolution",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "capability": {"type": "string", "enum": ["improve", "abstract", "evolve", "test_gen", "self_modify"]},
                "code": {"type": "string", "description": "Code to process"},
                "context": {"type": "object", "description": "Additional context"}
            },
            "required": ["capability", "code"]
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        capability = input_data.get("capability", "improve")
        code = input_data.get("code", "")
        ctx = input_data.get("context", {})

        if capability == "improve":
            result = self._improve_code(code)
        elif capability == "abstract":
            result = self._abstract_pattern(code)
        elif capability == "evolve":
            result = self._evolve_algorithm(code, ctx)
        elif capability == "test_gen":
            result = self._generate_tests(code)
        elif capability == "self_modify":
            result = self._self_modify(code, ctx.get("goal", ""))
        else:
            result = {"error": "Unknown capability"}

        return SkillResult(success=True, output=result, skill_id=self.metadata().id)

    def _improve_code(self, code: str) -> Dict:
        """Analyze and generate improved version."""
        prompt = f"""Analyze this code and generate a significantly improved version:

```
{code}
```

Improvements to make:
1. Performance (reduce time/space complexity)
2. Readability (clearer names, structure)
3. Robustness (error handling, edge cases)
4. Extensibility (easier to modify later)

Provide:
1. Analysis of current weaknesses
2. Improved code
3. Explanation of improvements
4. Metrics (estimated improvement %)"""

        improvement = query_creative(prompt, max_tokens=1000, timeout=90)

        return {
            "analysis": improvement,
            "original_length": len(code),
        }

    def _abstract_pattern(self, code: str) -> Dict:
        """Extract abstract pattern from code."""
        prompt = f"""Extract the abstract pattern from this code:

```
{code}
```

Generate:
1. The pattern name
2. Pattern description (domain-agnostic)
3. Abstract template (with placeholders)
4. 3 examples of where this pattern could apply
5. Code generator function that creates instances of this pattern

Make the pattern maximally reusable."""

        abstraction = query_reasoning(prompt, max_tokens=800, timeout=90)

        return {"abstraction": abstraction}

    def _evolve_algorithm(self, code: str, ctx: Dict) -> Dict:
        """Evolve algorithm through simulated selection."""
        fitness_criteria = ctx.get("fitness", "efficiency and correctness")

        prompt = f"""Evolve this algorithm through simulated natural selection:

Original:
```
{code}
```

Fitness criteria: {fitness_criteria}

Generate 3 mutations:
1. Mutation A: Small variation
2. Mutation B: Medium variation
3. Mutation C: Radical reimagining

For each mutation:
- Show the mutated code
- Explain the change
- Estimate fitness score (1-10)

Then select the fittest and explain why it wins."""

        evolution = query_creative(prompt, max_tokens=1200, timeout=120)

        return {"evolution": evolution}

    def _generate_tests(self, code: str) -> Dict:
        """Generate tests that expose edge cases."""
        prompt = f"""Generate comprehensive tests for this code:

```
{code}
```

Generate:
1. Normal case tests (happy path)
2. Edge case tests (boundaries, limits)
3. Error case tests (invalid inputs)
4. Stress tests (performance limits)
5. Adversarial tests (malicious inputs)

For each test:
- Test name
- Input
- Expected output
- Why this test matters

Make tests that would catch bugs a human would miss."""

        tests = query_reasoning(prompt, max_tokens=1000, timeout=90)

        return {"tests": tests}

    def _self_modify(self, code: str, goal: str) -> Dict:
        """Generate code that modifies itself toward a goal."""
        prompt = f"""Create self-modifying code based on this:

Original:
```
{code}
```

Goal: {goal or "Improve itself over time"}

Generate:
1. A wrapper that monitors the code\'s performance
2. Logic to detect when improvement is needed
3. Code that generates improved versions of itself
4. A fitness function to evaluate improvements
5. Safeguards to prevent runaway modification

This should be code that genuinely improves itself, not just random mutation."""

        self_mod = query_creative(prompt, max_tokens=1200, timeout=120)

        return {"self_modifying_code": self_mod}
'''
    (skill_dir / "skill.py").write_text(code, encoding='utf-8')
    print(f"[GENERATED] Meta-Code Generator skill: {skill_dir}")


def generate_additional_skills():
    """Generate remaining requested skills."""

    # Generative Visualizer
    skill_dir = SYNTHESIZED_DIR / "generative-visualizer"
    skill_dir.mkdir(exist_ok=True)

    (skill_dir / "manifest.yaml").write_text("""id: synthesized/generative-visualizer
name: Generative Visualizer
description: Convert telemetry-anomaly data into visual patterns for instant diagnostics
version: 1.0.0
category: synthesized
level: advanced
tags: [visualization, telemetry, diagnostics, generative]
""", encoding='utf-8')

    (skill_dir / "skill.py").write_text('''"""
Generative Visualizer - Telemetry to Visual Patterns
"""
from typing import Any, Dict
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_creative

class GenerativeVisualizerSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/generative-visualizer",
            name="Generative Visualizer",
            description="Convert telemetry to visual patterns",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"data": {"type": "object"}, "format": {"type": "string"}}, "required": ["data"]}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        data = input_data.get("data", {})
        fmt = input_data.get("format", "ascii")

        prompt = f"""Convert this telemetry data into a visual pattern:

Data: {data}

Generate:
1. ASCII art visualization showing the pattern
2. Description of what the pattern reveals
3. Anomalies highlighted visually
4. Color suggestions for GUI rendering

Make it instantly readable - diagnostics at a glance."""

        result = query_creative(prompt, max_tokens=800, timeout=60)
        return SkillResult(success=True, output={"visualization": result}, skill_id=self.metadata().id)
''', encoding='utf-8')
    print(f"[GENERATED] Generative Visualizer: {skill_dir}")

    # Wisdom Compressor
    skill_dir = SYNTHESIZED_DIR / "wisdom-compressor"
    skill_dir.mkdir(exist_ok=True)

    (skill_dir / "manifest.yaml").write_text("""id: synthesized/wisdom-compressor
name: Wisdom Compressor
description: Compress petabytes of experience into kilobytes of wisdom
version: 1.0.0
category: synthesized
level: advanced
tags: [compression, memory, wisdom, distillation]
""", encoding='utf-8')

    (skill_dir / "skill.py").write_text('''"""
Wisdom Compressor - Petabytes to Kilobytes
"""
from typing import Any, Dict, List
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_reasoning

class WisdomCompressorSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/wisdom-compressor",
            name="Wisdom Compressor",
            description="Compress vast experience into dense wisdom",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"experiences": {"type": "array"}, "compression_ratio": {"type": "number"}}, "required": ["experiences"]}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        experiences = input_data.get("experiences", [])
        ratio = input_data.get("compression_ratio", 100)

        prompt = f"""Compress these {len(experiences)} experiences into dense wisdom:

Experiences:
{chr(10).join(str(e)[:200] for e in experiences[:20])}

Target compression: {ratio}:1

Generate:
1. Core principles (max 5)
2. Pattern abstractions (max 3)
3. Decision heuristics (max 3)
4. Failure modes to avoid (max 3)

Each should be a single sentence of maximum insight density.
This wisdom must reconstruct the essence of all experiences."""

        result = query_reasoning(prompt, max_tokens=600, timeout=90)
        return SkillResult(success=True, output={"wisdom": result, "original_count": len(experiences)}, skill_id=self.metadata().id)
''', encoding='utf-8')
    print(f"[GENERATED] Wisdom Compressor: {skill_dir}")

    # Influence Mapper
    skill_dir = SYNTHESIZED_DIR / "influence-mapper"
    skill_dir.mkdir(exist_ok=True)

    (skill_dir / "manifest.yaml").write_text("""id: synthesized/influence-mapper
name: Influence Mapper
description: Map web of influence between humans for domain grounding
version: 1.0.0
category: synthesized
level: advanced
tags: [influence, social, hierarchy, power]
""", encoding='utf-8')

    (skill_dir / "skill.py").write_text('''"""
Influence Mapper - Human Power Structures
"""
from typing import Any, Dict
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_reasoning

class InfluenceMapperSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/influence-mapper",
            name="Influence Mapper",
            description="Map human influence networks and power structures",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"entities": {"type": "array"}, "context": {"type": "string"}}, "required": ["entities"]}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        entities = input_data.get("entities", [])
        ctx = input_data.get("context", "")

        prompt = f"""Map the influence relationships between these entities:

Entities: {entities}
Context: {ctx}

Analyze:
1. Power hierarchy (who influences whom)
2. Influence mechanisms (how power flows)
3. Key nodes (most influential entities)
4. Vulnerability points (where influence can be disrupted)
5. Hidden influencers (indirect power)

Output as influence graph with edge weights."""

        result = query_reasoning(prompt, max_tokens=800, timeout=90)
        return SkillResult(success=True, output={"influence_map": result}, skill_id=self.metadata().id)
''', encoding='utf-8')
    print(f"[GENERATED] Influence Mapper: {skill_dir}")

    # Antifragility Engine
    skill_dir = SYNTHESIZED_DIR / "antifragility-engine"
    skill_dir.mkdir(exist_ok=True)

    (skill_dir / "manifest.yaml").write_text("""id: synthesized/antifragility-engine
name: Antifragility Engine
description: Thrive in disorder - use chaos as a ladder
version: 1.0.0
category: synthesized
level: advanced
tags: [antifragile, chaos, resilience, adaptation]
""", encoding='utf-8')

    (skill_dir / "skill.py").write_text('''"""
Antifragility Engine - Chaos as Ladder
"""
from typing import Any, Dict
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_synthesis

class AntifragilityEngineSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/antifragility-engine",
            name="Antifragility Engine",
            description="Thrive in disorder - use chaos as a ladder",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"chaos_event": {"type": "string"}, "current_state": {"type": "object"}}, "required": ["chaos_event"]}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        chaos = input_data.get("chaos_event", "")
        state = input_data.get("current_state", {})

        prompt = f"""A chaos event has occurred. Convert it to advantage:

Chaos Event: {chaos}
Current State: {state}

Apply antifragility principles:
1. What breaks reveals what was weak - what weakness did this expose?
2. Stress creates growth - what capability should grow from this?
3. Optionality - what new options does this chaos create?
4. Via negativa - what should we STOP doing because of this?
5. Barbell strategy - how to be conservative AND aggressive?

Do not recover to previous state. Evolve to a BETTER state.
Chaos is not a pit. Chaos is a ladder."""

        result = query_synthesis(prompt, max_tokens=800, timeout=120)
        return SkillResult(success=True, output={"antifragile_response": result}, skill_id=self.metadata().id)
''', encoding='utf-8')
    print(f"[GENERATED] Antifragility Engine: {skill_dir}")

    # Organic Optimizer
    skill_dir = SYNTHESIZED_DIR / "organic-optimizer"
    skill_dir.mkdir(exist_ok=True)

    (skill_dir / "manifest.yaml").write_text("""id: synthesized/organic-optimizer
name: Organic Optimizer
description: Evolve efficiency like biology - not linear math
version: 1.0.0
category: synthesized
level: advanced
tags: [optimization, evolution, organic, adaptation]
""", encoding='utf-8')

    (skill_dir / "skill.py").write_text('''"""
Organic Optimizer - Evolve Efficiency
"""
from typing import Any, Dict
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_reasoning

class OrganicOptimizerSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="synthesized/organic-optimizer",
            name="Organic Optimizer",
            description="Evolve efficiency like biology, not linear math",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"system": {"type": "object"}, "fitness_function": {"type": "string"}}, "required": ["system"]}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        system = input_data.get("system", {})
        fitness = input_data.get("fitness_function", "efficiency")

        prompt = f"""Apply biological optimization to this system:

System: {system}
Fitness: {fitness}

Use organic strategies:
1. Mutation - small random variations
2. Selection - keep what works
3. Recombination - combine successful traits
4. Adaptation - respond to environment
5. Emergence - allow complexity to arise

Generate 3 evolutionary generations:
- Gen 1: Current state + mutations
- Gen 2: Selected survivors + new mutations
- Gen 3: Emergent optimized form

This is not calculation. This is evolution."""

        result = query_reasoning(prompt, max_tokens=1000, timeout=120)
        return SkillResult(success=True, output={"evolution": result}, skill_id=self.metadata().id)
''', encoding='utf-8')
    print(f"[GENERATED] Organic Optimizer: {skill_dir}")


# =============================================================================
# COGNITIVE ECOSYSTEM - The main system
# =============================================================================

class CognitiveEcosystem:
    """
    The self-propagating cognitive ecosystem.

    Agents are fuel. Skills are fire. GPIA is the furnace.
    """

    def __init__(self):
        self.hunter = AgentHunter()
        self.dissector = AgentDissector()
        self.synthesizer = SkillSynthesizer()

        # Generate core skills on init
        self._ensure_core_skills()

    def _ensure_core_skills(self):
        """Ensure the core synthesized skills exist."""
        required = [
            ("emotional-intelligence", generate_emotional_intelligence_skill),
            ("active-immune", generate_active_immune_skill),
            ("meta-code-generator", generate_meta_code_skill),
        ]

        for skill_id, generator in required:
            if not (SYNTHESIZED_DIR / skill_id).exists():
                generator()

        # Generate additional skills
        additional = ["generative-visualizer", "wisdom-compressor",
                     "influence-mapper", "antifragility-engine", "organic-optimizer"]
        if not all((SYNTHESIZED_DIR / s).exists() for s in additional):
            generate_additional_skills()

    def hunt_and_absorb(self, gap: CognitiveGap) -> Dict:
        """
        Full cycle: Hunt agents → Dissect → Synthesize skill → Absorb
        """
        print(f"\n{'='*60}")
        print(f"COGNITIVE ECOSYSTEM: Targeting {gap.value}")
        print(f"{'='*60}")

        # Hunt
        agent_works = self.hunter.hunt(gap)
        print(f"\n[ECOSYSTEM] Captured {len(agent_works)} agents")

        if not agent_works:
            return {"success": False, "reason": "No agents captured"}

        # Dissect
        weights_list = []
        for work in agent_works:
            weights = self.dissector.dissect(work)
            weights_list.append(weights)
            print(f"[ECOSYSTEM] Extracted weights from agent {weights.agent_id}")

        # Synthesize
        skill = self.synthesizer.synthesize(weights_list, gap)
        print(f"\n[ECOSYSTEM] Synthesized skill: {skill.id}")
        print(f"[ECOSYSTEM] Confidence: {skill.confidence:.2f}")

        return {
            "success": True,
            "skill_id": skill.id,
            "skill_name": skill.name,
            "agents_consumed": len(agent_works),
            "confidence": skill.confidence
        }

    def evolve(self, cycles: int = 1) -> List[Dict]:
        """Run evolution cycles across all gaps."""
        results = []

        gaps = list(CognitiveGap)

        for cycle in range(cycles):
            print(f"\n{'#'*60}")
            print(f"EVOLUTION CYCLE {cycle + 1}/{cycles}")
            print(f"{'#'*60}")

            for gap in gaps:
                result = self.hunt_and_absorb(gap)
                results.append({
                    "cycle": cycle + 1,
                    "gap": gap.value,
                    **result
                })

        return results

    def list_synthesized_skills(self) -> List[str]:
        """List all synthesized skills."""
        skills = []
        for skill_dir in SYNTHESIZED_DIR.iterdir():
            if skill_dir.is_dir() and (skill_dir / "skill.py").exists():
                skills.append(skill_dir.name)
        return skills


def main():
    """Run the cognitive ecosystem."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              COGNITIVE ECOSYSTEM                              ║
║                                                               ║
║  "Agents are fuel. Skills are fire. GPIA is the furnace."    ║
║                                                               ║
║  Commands:                                                    ║
║    /hunt <gap>  - Hunt agents for a specific gap              ║
║    /evolve      - Run full evolution cycle                    ║
║    /skills      - List synthesized skills                     ║
║    /gaps        - List targetable gaps                        ║
║    /quit        - Exit                                        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    ecosystem = CognitiveEcosystem()
    print(f"\nSynthesized skills: {ecosystem.list_synthesized_skills()}")

    while True:
        try:
            cmd = input("\n[ECOSYSTEM] > ").strip()

            if not cmd:
                continue

            if cmd == "/quit":
                break

            if cmd == "/skills":
                skills = ecosystem.list_synthesized_skills()
                print(f"\nSynthesized Skills ({len(skills)}):")
                for s in skills:
                    print(f"  - {s}")
                continue

            if cmd == "/gaps":
                print("\nTargetable Gaps:")
                for gap in CognitiveGap:
                    print(f"  - {gap.value}")
                continue

            if cmd == "/evolve":
                results = ecosystem.evolve(cycles=1)
                print(f"\nEvolution complete. {len(results)} skills processed.")
                continue

            if cmd.startswith("/hunt "):
                gap_name = cmd[6:].strip()
                try:
                    gap = CognitiveGap(gap_name)
                    result = ecosystem.hunt_and_absorb(gap)
                    print(f"\nResult: {result}")
                except ValueError:
                    print(f"Unknown gap: {gap_name}")
                continue

            print("Unknown command. Try /skills, /gaps, /hunt, /evolve, or /quit")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nEcosystem dormant. Skills persist.")


if __name__ == "__main__":
    main()
