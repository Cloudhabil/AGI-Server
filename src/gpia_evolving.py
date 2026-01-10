"""
Evolving GPIA - Agents are Ephemeral, Skills are Permanent
==========================================================

Philosophy:
- Agents are temporary workers that solve problems
- Successful solutions become permanent skills
- GPIA absorbs skills and grows
- No persistent sub-agents - only GPIA remains

The Transmutation Loop:
1. GPIA faces unknown problem
2. Spawns ephemeral agent to solve it
3. Agent solves problem (or fails)
4. If success: Extract skill from agent's approach
5. Skill is added to GPIA's skillbox
6. Agent is destroyed
7. Next time: GPIA handles it directly (no agent needed)

This is how GPIA evolves: temporary help → permanent capability
"""

import json
import hashlib
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from agents.model_router import (
    query_fast, query_creative, query_reasoning, query_synthesis
)

# Where extracted skills are stored
EVOLVED_SKILLS_DIR = Path("skills/evolved")
EVOLVED_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

EVOLUTION_LOG = Path("data/gpia/evolution.json")
EVOLUTION_LOG.parent.mkdir(parents=True, exist_ok=True)


@dataclass
class SkillExtract:
    """A skill extracted from successful agent work."""
    id: str
    name: str
    description: str
    trigger: str  # When to use this skill
    approach: str  # How to solve it
    model: str  # Which model works best
    prompt_template: str  # The prompt that worked
    examples: List[Dict] = field(default_factory=list)
    success_rate: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentWork:
    """Record of ephemeral agent's work."""
    task: str
    approach: str
    reasoning: List[str]
    result: Any
    success: bool
    model_used: str
    prompt_used: str
    execution_time: float


class EphemeralAgent:
    """
    A temporary agent that exists only to solve one problem.

    After solving (or failing), it provides:
    - The solution
    - Its approach (for skill extraction)
    - Then it's destroyed
    """

    def __init__(self, purpose: str, model: str = "qwen3"):
        self.purpose = purpose
        self.model = model
        self.work: Optional[AgentWork] = None
        self._alive = True

    def solve(self, task: str, context: Dict = None) -> AgentWork:
        """
        Attempt to solve a task. This is the agent's only job.
        After this, the agent should be destroyed.
        """
        if not self._alive:
            raise RuntimeError("Agent already terminated")

        start = time.time()
        reasoning = []

        # Step 1: Understand the task
        understand_prompt = f"""You are a specialized agent for: {self.purpose}

Task: {task}

Context: {json.dumps(context or {})[:500]}

First, analyze:
1. What exactly needs to be done?
2. What approach should work?
3. What could go wrong?

Be concise."""

        understanding = self._think(understand_prompt)
        reasoning.append(f"Understanding: {understanding[:200]}")

        # Step 2: Solve it
        solve_prompt = f"""You are solving: {task}

Your analysis: {understanding}

Now provide a complete solution. Be specific and actionable.
If code is needed, write working code.
If steps are needed, list them clearly."""

        solution = self._think(solve_prompt)
        reasoning.append(f"Solution: {solution[:200]}")

        # Record the work
        # Determine success - any meaningful response
        is_success = bool(solution and len(solution.strip()) > 20)

        self.work = AgentWork(
            task=task,
            approach=understanding,
            reasoning=reasoning,
            result=solution if is_success else f"Approach: {understanding}\n\nAttempt: {solution}",
            success=is_success or bool(understanding and len(understanding) > 50),
            model_used=self.model,
            prompt_used=solve_prompt,
            execution_time=time.time() - start
        )

        return self.work

    def _think(self, prompt: str) -> str:
        """Use assigned model."""
        if self.model == "deepseek_r1":
            return query_reasoning(prompt, max_tokens=800, timeout=90)
        elif self.model == "gpt_oss_20b":
            return query_synthesis(prompt, max_tokens=800, timeout=120)
        elif self.model == "codegemma":
            return query_fast(prompt, max_tokens=400, timeout=30)
        else:
            return query_creative(prompt, max_tokens=800, timeout=60)

    def get_extractable_skill(self) -> Optional[SkillExtract]:
        """
        If work was successful, extract a reusable skill.
        This is how the agent's knowledge transfers to GPIA.
        """
        if not self.work or not self.work.success:
            return None

        # Generate skill from successful work
        skill_id = f"evolved-{hashlib.md5(self.work.task.encode()).hexdigest()[:8]}"

        return SkillExtract(
            id=skill_id,
            name=f"Evolved: {self.purpose[:30]}",
            description=f"Skill evolved from solving: {self.work.task[:100]}",
            trigger=self.work.task,
            approach=self.work.approach,
            model=self.model,
            prompt_template=self.work.prompt_used,
            examples=[{
                "input": self.work.task,
                "output": str(self.work.result)[:500]
            }]
        )

    def terminate(self):
        """Destroy the agent. It should not be used after this."""
        self._alive = False
        self.work = None


class SkillEvolver:
    """
    Manages skill evolution - converting agent work into permanent skills.
    """

    def __init__(self):
        self.evolved_skills: Dict[str, SkillExtract] = {}
        self._load_evolved()

    def _load_evolved(self):
        """Load previously evolved skills."""
        for skill_file in EVOLVED_SKILLS_DIR.glob("*.json"):
            try:
                data = json.loads(skill_file.read_text())
                skill = SkillExtract(**data)
                self.evolved_skills[skill.id] = skill
            except Exception as e:
                print(f"Failed to load evolved skill {skill_file}: {e}")

        print(f"[Evolver] Loaded {len(self.evolved_skills)} evolved skills")

    def absorb(self, skill: SkillExtract) -> bool:
        """
        Absorb a skill into GPIA's permanent skillbox.
        """
        # Check if similar skill exists
        for existing in self.evolved_skills.values():
            if self._is_similar(skill.trigger, existing.trigger):
                # Merge: update existing skill
                existing.examples.extend(skill.examples)
                existing.success_rate = (existing.success_rate + 1) / 2
                self._save_skill(existing)
                print(f"[Evolver] Merged into existing skill: {existing.id}")
                return True

        # New skill
        self.evolved_skills[skill.id] = skill
        self._save_skill(skill)
        self._generate_skill_code(skill)
        print(f"[Evolver] New skill absorbed: {skill.id}")
        return True

    def _is_similar(self, trigger1: str, trigger2: str) -> bool:
        """Check if two triggers are similar (would use same skill)."""
        # Extract meaningful words (remove common words)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'what', 'how', 'why', 'in', 'of', 'to', 'and', 'or', 'between'}

        words1 = set(w.lower() for w in trigger1.split() if w.lower() not in stop_words and len(w) > 2)
        words2 = set(w.lower() for w in trigger2.split() if w.lower() not in stop_words and len(w) > 2)

        if not words1 or not words2:
            return False

        overlap = len(words1 & words2)
        # If at least 2 meaningful words overlap, consider similar
        return overlap >= 2 or (overlap >= 1 and len(words1) <= 3)

    def _save_skill(self, skill: SkillExtract):
        """Persist skill to disk."""
        skill_file = EVOLVED_SKILLS_DIR / f"{skill.id}.json"
        skill_file.write_text(json.dumps({
            "id": skill.id,
            "name": skill.name,
            "description": skill.description,
            "trigger": skill.trigger,
            "approach": skill.approach,
            "model": skill.model,
            "prompt_template": skill.prompt_template,
            "examples": skill.examples,
            "success_rate": skill.success_rate,
            "created_at": skill.created_at
        }, indent=2))

    def _generate_skill_code(self, skill: SkillExtract):
        """Generate actual skill.py for the evolved skill."""
        skill_dir = EVOLVED_SKILLS_DIR / skill.id
        skill_dir.mkdir(exist_ok=True)

        # Generate manifest
        manifest = {
            "id": f"evolved/{skill.id}",
            "name": skill.name,
            "description": skill.description,
            "version": "0.1.0",
            "category": "evolved",
            "level": "intermediate",
            "tags": ["evolved", "auto-generated"],
            "requires_model": skill.model,
        }
        (skill_dir / "manifest.yaml").write_text(
            "\n".join(f"{k}: {json.dumps(v)}" for k, v in manifest.items())
        )

        # Generate skill code
        code = f'''"""
{skill.name}
Auto-evolved skill from successful agent work.
"""

from typing import Any, Dict
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext, SkillCategory
from agents.model_router import query_creative, query_reasoning

class EvolvedSkill(Skill):
    """Auto-evolved skill: {skill.description[:100]}"""

    APPROACH = """{skill.approach[:500]}"""
    MODEL = "{skill.model}"

    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="{skill.id}",
            name="{skill.name}",
            description="{skill.description[:200]}",
            category=SkillCategory.CODE,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {{
            "type": "object",
            "properties": {{
                "task": {{"type": "string", "description": "The task to perform"}}
            }},
            "required": ["task"]
        }}

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        task = input_data.get("task", "")

        prompt = f"""Based on this approach: {{self.APPROACH}}

Solve this task: {{task}}

Provide a complete solution."""

        if self.MODEL == "deepseek_r1":
            result = query_reasoning(prompt, max_tokens=800)
        else:
            result = query_creative(prompt, max_tokens=800)

        return SkillResult(
            success=bool(result),
            output=result,
            skill_id=self.metadata().id,
        )
'''
        (skill_dir / "skill.py").write_text(code)

    def find_skill_for(self, task: str) -> Optional[SkillExtract]:
        """Find an evolved skill that can handle this task."""
        for skill in self.evolved_skills.values():
            if self._is_similar(task, skill.trigger):
                return skill
        return None


class EvolvingGPIA:
    """
    GPIA that evolves by absorbing successful agent work.

    Flow:
    1. Task arrives
    2. Check if evolved skill exists → use it
    3. If not, spawn ephemeral agent
    4. Agent solves task
    5. If success, extract skill and absorb
    6. Destroy agent
    7. Next time, use the skill directly
    """

    def __init__(self):
        from gpia import GPIA
        self.core = GPIA(verbose=False)
        self.evolver = SkillEvolver()
        self.evolution_count = 0

        print(f"[EvolvingGPIA] Core skills: {self.core.state.skills_loaded}")
        print(f"[EvolvingGPIA] Evolved skills: {len(self.evolver.evolved_skills)}")

    def run(self, task: str) -> Dict:
        """
        Execute a task, evolving if needed.
        """
        print(f"\n[GPIA] Task: {task[:60]}...")

        # Step 1: Check for evolved skill
        evolved_skill = self.evolver.find_skill_for(task)
        if evolved_skill:
            print(f"[GPIA] Using evolved skill: {evolved_skill.id}")
            return self._use_evolved_skill(evolved_skill, task)

        # Step 2: Check if core GPIA can handle it
        complexity = self._assess_complexity(task)

        if complexity == "simple":
            print("[GPIA] Simple task - direct execution")
            result = self.core.run(task)
            return {
                "response": result.response,
                "method": "direct",
                "evolved": False
            }

        # Step 3: Spawn ephemeral agent
        print("[GPIA] Complex task - spawning ephemeral agent...")
        return self._solve_with_agent(task, complexity)

    def _assess_complexity(self, task: str) -> str:
        """Quick complexity assessment."""
        result = query_fast(
            f"Rate complexity: simple, medium, or complex\nTask: {task}\nAnswer:",
            max_tokens=10
        )
        if "complex" in result.lower():
            return "complex"
        elif "medium" in result.lower():
            return "medium"
        return "simple"

    def _use_evolved_skill(self, skill: SkillExtract, task: str) -> Dict:
        """Use a previously evolved skill."""
        prompt = f"""Based on this proven approach:
{skill.approach}

Solve: {task}"""

        if skill.model == "deepseek_r1":
            result = query_reasoning(prompt, max_tokens=800, timeout=90)
        else:
            result = query_creative(prompt, max_tokens=800, timeout=60)

        return {
            "response": result,
            "method": "evolved_skill",
            "skill_id": skill.id,
            "evolved": True
        }

    def _solve_with_agent(self, task: str, complexity: str) -> Dict:
        """
        Spawn agent, solve, extract skill, destroy agent.
        """
        # Choose model based on complexity
        model = "deepseek_r1" if complexity == "complex" else "qwen3"

        # Create ephemeral agent
        agent = EphemeralAgent(
            purpose=f"Solve: {task[:50]}",
            model=model
        )

        try:
            # Agent does the work
            work = agent.solve(task)

            if work.success:
                # Extract and absorb skill
                skill = agent.get_extractable_skill()
                if skill:
                    self.evolver.absorb(skill)
                    self.evolution_count += 1
                    print(f"[GPIA] Evolved! New skill: {skill.id}")

                return {
                    "response": work.result,
                    "method": "ephemeral_agent",
                    "model": model,
                    "evolved": True,
                    "new_skill": skill.id if skill else None,
                    "execution_time": work.execution_time
                }
            else:
                return {
                    "response": "Agent failed to solve task",
                    "method": "ephemeral_agent",
                    "evolved": False,
                    "error": "No solution found"
                }

        finally:
            # Always destroy the agent
            agent.terminate()
            print("[GPIA] Agent terminated")

    def status(self) -> Dict:
        """Get evolution status."""
        return {
            "core_skills": self.core.state.skills_loaded,
            "evolved_skills": len(self.evolver.evolved_skills),
            "evolution_count": self.evolution_count,
            "evolved_skill_ids": list(self.evolver.evolved_skills.keys())
        }

    def list_evolved(self):
        """List all evolved skills."""
        print("\nEvolved Skills:")
        print("-" * 50)
        for skill in self.evolver.evolved_skills.values():
            print(f"  {skill.id}")
            print(f"    Trigger: {skill.trigger[:60]}...")
            print(f"    Model: {skill.model}")
            print()


def main():
    """Interactive evolving GPIA."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                    EVOLVING GPIA                              ║
║                                                               ║
║  Agents are ephemeral. Skills are permanent.                  ║
║  Every solved problem becomes a new capability.               ║
║                                                               ║
║  Commands:                                                    ║
║    /status   - Show evolution status                          ║
║    /evolved  - List evolved skills                            ║
║    /quit     - Exit                                           ║
╚═══════════════════════════════════════════════════════════════╝
""")

    gpia = EvolvingGPIA()

    while True:
        try:
            task = input("\n[You] > ").strip()

            if not task:
                continue

            if task == "/quit":
                break

            if task == "/status":
                status = gpia.status()
                print(f"\nCore skills: {status['core_skills']}")
                print(f"Evolved skills: {status['evolved_skills']}")
                print(f"Evolutions this session: {status['evolution_count']}")
                continue

            if task == "/evolved":
                gpia.list_evolved()
                continue

            # Run task
            result = gpia.run(task)

            print(f"\n[GPIA] {result['response']}")
            print(f"\n(Method: {result['method']}", end="")
            if result.get('new_skill'):
                print(f", New skill: {result['new_skill']}", end="")
            print(")")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print(f"\nSession stats: {gpia.evolution_count} evolutions")
    print("Goodbye!")


if __name__ == "__main__":
    main()
