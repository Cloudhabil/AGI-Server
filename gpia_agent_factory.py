"""
GPIA Agent Factory - Self-Creating Agent System
================================================

GPIA creates specialized agents to close its own capability gaps.
Each agent is a focused sub-system that can:
- Be created dynamically
- Operate autonomously
- Create other agents if needed

The Bootstrap Loop:
1. GPIA identifies capability gap
2. GPIA creates agent to fill gap
3. Agent operates and reports back
4. GPIA learns from agent's work
5. Better agents are created

This is the path from automation to autonomy.
"""

import json
import os
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from agents.model_router import (
    get_router, query_fast, query_creative,
    query_reasoning, query_synthesis
)
from core.agent_creator_manager import AgentCreatorManager

# Agent storage
AGENTS_DIR = Path("data/gpia/agents")
AGENTS_DIR.mkdir(parents=True, exist_ok=True)


class AgentCapability(Enum):
    """What agents can do."""
    PLAN = "plan"           # Break down goals
    ANALYZE = "analyze"     # Deep analysis
    CREATE = "create"       # Generate content/code
    DEBUG = "debug"         # Fix problems
    LEARN = "learn"         # Extract patterns
    DECIDE = "decide"       # Make choices
    COORDINATE = "coordinate"  # Manage other agents


@dataclass
class AgentSpec:
    """Specification for creating an agent."""
    name: str
    purpose: str
    capabilities: List[AgentCapability]
    model: str  # Which LLM to use
    system_prompt: str
    tools: List[str] = field(default_factory=list)
    can_create_agents: bool = False
    max_iterations: int = 10
    agent_id: Optional[str] = None


@dataclass
class AgentResult:
    """Result from agent execution."""
    agent_name: str
    success: bool
    output: Any
    reasoning: List[str] = field(default_factory=list)
    sub_agents_created: List[str] = field(default_factory=list)
    execution_time: float = 0.0


class BaseAgent(ABC):
    """Base class for all GPIA agents."""

    def __init__(self, spec: AgentSpec):
        self.spec = spec
        self.name = spec.name
        self.iteration = 0
        self.history: List[Dict] = []

    @abstractmethod
    def run(self, task: str, context: Dict = None) -> AgentResult:
        """Execute the agent's main function."""
        pass

    def think(self, prompt: str) -> str:
        """Use the agent's assigned model to think."""
        if self.spec.model == "deepseek_r1":
            return query_reasoning(prompt, max_tokens=1000, timeout=120)
        elif self.spec.model == "gpt_oss_20b":
            return query_synthesis(prompt, max_tokens=1000, timeout=180)
        elif self.spec.model == "codegemma":
            return query_fast(prompt, max_tokens=500, timeout=30)
        else:
            return query_creative(prompt, max_tokens=1000, timeout=90)

    def log(self, message: str):
        """Log agent activity."""
        entry = {
            "time": datetime.now().isoformat(),
            "iteration": self.iteration,
            "message": message
        }
        self.history.append(entry)
        print(f"[{self.name}] {message}")


# =============================================================================
# GAP-CLOSING AGENTS
# =============================================================================

class MetaPlannerAgent(BaseAgent):
    """
    Closes Gap: "Can't invent goals"

    Takes a high-level objective and breaks it into:
    - Sub-goals (recursive)
    - Concrete tasks
    - Success criteria
    """

    def run(self, objective: str, context: Dict = None) -> AgentResult:
        start = time.time()
        reasoning = []

        self.log(f"Planning: {objective[:50]}...")

        # Step 1: Understand the objective
        understand_prompt = f"""{self.spec.system_prompt}

Analyze this objective and identify:
1. What is the end goal?
2. What are the major milestones?
3. What capabilities are needed?
4. What could go wrong?

Objective: {objective}

Output as JSON:
{{"end_goal": "...", "milestones": [...], "capabilities_needed": [...], "risks": [...]}}
"""
        understanding = self.think(understand_prompt)
        reasoning.append(f"Understanding: {understanding[:200]}")

        # Step 2: Break into sub-goals
        plan_prompt = f"""{self.spec.system_prompt}

Given this objective: {objective}

And this understanding: {understanding}

Create a hierarchical plan with:
1. Sub-goals (things that must be achieved)
2. For each sub-goal, concrete tasks
3. Dependencies between tasks
4. Success criteria for each

Output as JSON:
{{
  "sub_goals": [
    {{
      "id": "sg1",
      "description": "...",
      "tasks": [
        {{"id": "t1", "description": "...", "depends_on": []}}
      ],
      "success_criteria": "..."
    }}
  ]
}}
"""
        plan = self.think(plan_prompt)
        reasoning.append(f"Plan: {plan[:300]}")

        # Try to parse the plan
        try:
            if "{" in plan:
                json_str = plan[plan.find("{"):plan.rfind("}")+1]
                plan_data = json.loads(json_str)
            else:
                plan_data = {"sub_goals": [], "raw": plan}
        except:
            plan_data = {"sub_goals": [], "raw": plan}

        return AgentResult(
            agent_name=self.name,
            success=True,
            output=plan_data,
            reasoning=reasoning,
            execution_time=time.time() - start
        )


class SelfDebuggerAgent(BaseAgent):
    """
    Closes Gap: "Can't fix code bugs"

    Analyzes failures, identifies root causes, proposes fixes.
    """

    def run(self, failure_info: str, context: Dict = None) -> AgentResult:
        start = time.time()
        reasoning = []

        self.log(f"Debugging: {failure_info[:50]}...")

        # Step 1: Diagnose
        diagnose_prompt = f"""{self.spec.system_prompt}

A failure occurred. Analyze it:

Failure info: {failure_info}

Context: {json.dumps(context or {}, indent=2)[:500]}

Identify:
1. What exactly failed?
2. What was the expected behavior?
3. What are possible root causes? (rank by likelihood)
4. What evidence supports each cause?

Be systematic and thorough.
"""
        diagnosis = self.think(diagnose_prompt)
        reasoning.append(f"Diagnosis: {diagnosis[:300]}")

        # Step 2: Propose fix
        fix_prompt = f"""{self.spec.system_prompt}

Based on this diagnosis: {diagnosis}

Propose a fix:
1. What specific change would fix the root cause?
2. How can we verify the fix works?
3. What could this fix break? (side effects)
4. Is there a safer alternative?

If code is needed, provide it.
"""
        fix = self.think(fix_prompt)
        reasoning.append(f"Fix: {fix[:300]}")

        return AgentResult(
            agent_name=self.name,
            success=True,
            output={"diagnosis": diagnosis, "fix": fix},
            reasoning=reasoning,
            execution_time=time.time() - start
        )


class FailureAnalystAgent(BaseAgent):
    """
    Closes Gap: "Can't reason about failures"

    Extracts patterns from failures to prevent recurrence.
    """

    def run(self, failures: List[Dict], context: Dict = None) -> AgentResult:
        start = time.time()
        reasoning = []

        self.log(f"Analyzing {len(failures)} failures...")

        failures_text = "\n".join([
            f"- {f.get('error', 'unknown')}: {f.get('context', '')[:100]}"
            for f in failures[:10]
        ])

        # Step 1: Find patterns
        pattern_prompt = f"""{self.spec.system_prompt}

Analyze these failures and find patterns:

{failures_text}

Identify:
1. Common themes or categories
2. Recurring root causes
3. Environmental factors
4. Timing patterns

What systemic issues do these failures reveal?
"""
        patterns = self.think(pattern_prompt)
        reasoning.append(f"Patterns: {patterns[:300]}")

        # Step 2: Propose preventions
        prevent_prompt = f"""{self.spec.system_prompt}

Based on these failure patterns: {patterns}

Propose systemic improvements:
1. What checks could prevent these failures?
2. What capabilities is the system missing?
3. What new agents or skills would help?
4. What goals should be added?

Be specific and actionable.
"""
        prevention = self.think(prevent_prompt)
        reasoning.append(f"Prevention: {prevention[:300]}")

        return AgentResult(
            agent_name=self.name,
            success=True,
            output={"patterns": patterns, "prevention": prevention},
            reasoning=reasoning,
            execution_time=time.time() - start
        )


class SkillWriterAgent(BaseAgent):
    """
    Closes Gap: "Can't modify behavior"

    Creates new skills when capability gaps are identified.
    """

    def run(self, capability_gap: str, context: Dict = None) -> AgentResult:
        start = time.time()
        reasoning = []

        self.log(f"Creating skill for: {capability_gap[:50]}...")

        # Step 1: Design the skill
        design_prompt = f"""{self.spec.system_prompt}

Design a new skill to address this capability gap:
{capability_gap}

Specify:
1. Skill name and ID
2. What it does (capabilities)
3. Input schema (what it needs)
4. Output schema (what it produces)
5. Which model(s) it should use
6. Dependencies on other skills

Output as JSON:
{{
  "id": "skill-name",
  "name": "Skill Name",
  "description": "...",
  "capabilities": [...],
  "input_schema": {{}},
  "output_schema": {{}},
  "model": "qwen3",
  "dependencies": []
}}
"""
        design = self.think(design_prompt)
        reasoning.append(f"Design: {design[:300]}")

        # Step 2: Generate implementation
        impl_prompt = f"""{self.spec.system_prompt}

Based on this skill design: {design}

Write the Python implementation following this template:

```python
from skills.base import Skill, SkillMetadata, SkillResult, SkillContext

class NewSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(id="...", name="...", description="...")

    def input_schema(self):
        return {{...}}

    def execute(self, input_data, context) -> SkillResult:
        # Implementation
        return SkillResult(success=True, output=result)
```

Write clean, working code.
"""
        implementation = self.think(impl_prompt)
        reasoning.append(f"Implementation: {implementation[:300]}")

        return AgentResult(
            agent_name=self.name,
            success=True,
            output={"design": design, "implementation": implementation},
            reasoning=reasoning,
            execution_time=time.time() - start
        )


class GoalGeneratorAgent(BaseAgent):
    """
    Closes Gap: "Can't set own goals"

    Observes system state and proposes new goals.
    """

    def run(self, observations: str, context: Dict = None) -> AgentResult:
        start = time.time()
        reasoning = []

        self.log("Generating goals from observations...")

        # Step 1: Analyze situation
        analyze_prompt = f"""{self.spec.system_prompt}

Based on these observations about the system:
{observations}

Current context: {json.dumps(context or {}, indent=2)[:500]}

Analyze:
1. What is going well?
2. What needs improvement?
3. What opportunities exist?
4. What threats or risks are emerging?
"""
        analysis = self.think(analyze_prompt)
        reasoning.append(f"Analysis: {analysis[:300]}")

        # Step 2: Generate goals
        goals_prompt = f"""{self.spec.system_prompt}

Based on this analysis: {analysis}

Propose 3-5 new goals that would:
1. Address identified weaknesses
2. Capitalize on opportunities
3. Mitigate risks
4. Improve overall capability

For each goal specify:
- Description
- Priority (1-5)
- Schedule (one-time, hourly, daily)
- Success criteria

Output as JSON array.
"""
        goals = self.think(goals_prompt)
        reasoning.append(f"Goals: {goals[:300]}")

        return AgentResult(
            agent_name=self.name,
            success=True,
            output={"analysis": analysis, "proposed_goals": goals},
            reasoning=reasoning,
            execution_time=time.time() - start
        )


class AgentCoordinatorAgent(BaseAgent):
    """
    Meta-agent that coordinates other agents.
    Can create new agents when needed.
    """

    def __init__(self, spec: AgentSpec, factory: 'AgentFactory'):
        super().__init__(spec)
        self.factory = factory

    def run(self, task: str, context: Dict = None) -> AgentResult:
        start = time.time()
        reasoning = []
        sub_agents = []

        self.log(f"Coordinating: {task[:50]}...")

        # Step 1: Decompose task
        decompose_prompt = f"""{self.spec.system_prompt}

Task to coordinate: {task}

Available agent types:
- MetaPlanner: Breaks down objectives into sub-goals
- SelfDebugger: Diagnoses and fixes failures
- FailureAnalyst: Finds patterns in failures
- SkillWriter: Creates new skills
- GoalGenerator: Proposes new goals

Which agents should work on this task?
What should each one do?
In what order?

Output as JSON:
{{"agents": [{{"type": "...", "subtask": "..."}}], "coordination_notes": "..."}}
"""
        plan = self.think(decompose_prompt)
        reasoning.append(f"Coordination plan: {plan[:300]}")

        # Step 2: Execute agents (simplified - would be parallel in production)
        results = []
        try:
            if "{" in plan:
                json_str = plan[plan.find("{"):plan.rfind("}")+1]
                plan_data = json.loads(json_str)

                for agent_task in plan_data.get("agents", [])[:3]:  # Max 3
                    agent_type = agent_task.get("type", "")
                    subtask = agent_task.get("subtask", "")

                    if agent_type and subtask:
                        agent = self.factory.get_agent(agent_type)
                        if agent:
                            self.log(f"Delegating to {agent_type}...")
                            result = agent.run(subtask, context)
                            results.append({
                                "agent": agent_type,
                                "result": result.output
                            })
                            sub_agents.append(agent_type)
        except Exception as e:
            reasoning.append(f"Coordination error: {e}")

        # Step 3: Synthesize results
        if results:
            synth_prompt = f"""{self.spec.system_prompt}

Original task: {task}

Results from sub-agents:
{json.dumps(results, indent=2, default=str)[:2000]}

Synthesize these results into a coherent response.
What was accomplished? What remains to be done?
"""
            synthesis = self.think(synth_prompt)
            reasoning.append(f"Synthesis: {synthesis[:300]}")
        else:
            synthesis = "No sub-agents executed"

        return AgentResult(
            agent_name=self.name,
            success=True,
            output={"plan": plan, "results": results, "synthesis": synthesis},
            reasoning=reasoning,
            sub_agents_created=sub_agents,
            execution_time=time.time() - start
        )


# =============================================================================
# AGENT FACTORY
# =============================================================================

class AgentFactory:
    """
    Creates and manages agents.

    This is how GPIA creates agents to close its own gaps.
    """

    # Pre-defined agent specifications
    AGENT_SPECS = {
        "MetaPlanner": AgentSpec(
            name="MetaPlanner",
            purpose="Break high-level objectives into actionable sub-goals and tasks",
            capabilities=[AgentCapability.PLAN, AgentCapability.ANALYZE],
            model="deepseek_r1",
            system_prompt="""You are the MetaPlanner agent. Your role is to take abstract objectives
and decompose them into concrete, achievable sub-goals and tasks.
Think hierarchically. Be thorough but practical.""",
        ),

        "SelfDebugger": AgentSpec(
            name="SelfDebugger",
            purpose="Diagnose failures and propose fixes",
            capabilities=[AgentCapability.DEBUG, AgentCapability.ANALYZE],
            model="deepseek_r1",
            system_prompt="""You are the SelfDebugger agent. Your role is to analyze failures,
identify root causes, and propose concrete fixes.
Be systematic. Consider multiple hypotheses. Verify before concluding.""",
        ),

        "FailureAnalyst": AgentSpec(
            name="FailureAnalyst",
            purpose="Extract patterns from failures to prevent recurrence",
            capabilities=[AgentCapability.LEARN, AgentCapability.ANALYZE],
            model="deepseek_r1",
            system_prompt="""You are the FailureAnalyst agent. Your role is to find patterns
in failures and propose systemic improvements.
Look for commonalities. Think about prevention, not just fixes.""",
        ),

        "SkillWriter": AgentSpec(
            name="SkillWriter",
            purpose="Create new skills when capability gaps are found",
            capabilities=[AgentCapability.CREATE],
            model="qwen3",
            system_prompt="""You are the SkillWriter agent. Your role is to design and implement
new skills that extend the system's capabilities.
Follow the skill framework. Write clean, working code.""",
        ),

        "GoalGenerator": AgentSpec(
            name="GoalGenerator",
            purpose="Propose new goals based on observations",
            capabilities=[AgentCapability.PLAN, AgentCapability.DECIDE],
            model="qwen3",
            system_prompt="""You are the GoalGenerator agent. Your role is to observe the system
and propose meaningful goals that drive improvement.
Be strategic. Prioritize high-impact goals.""",
        ),

        "Coordinator": AgentSpec(
            name="Coordinator",
            purpose="Orchestrate multiple agents to solve complex problems",
            capabilities=[AgentCapability.COORDINATE, AgentCapability.DECIDE],
            model="gpt_oss_20b",
            system_prompt="""You are the Coordinator agent. Your role is to decompose complex
tasks and delegate to specialized agents.
Think about dependencies. Synthesize results.""",
            can_create_agents=True,
        ),
    }

    # Agent class mapping
    AGENT_CLASSES = {
        "MetaPlanner": MetaPlannerAgent,
        "SelfDebugger": SelfDebuggerAgent,
        "FailureAnalyst": FailureAnalystAgent,
        "SkillWriter": SkillWriterAgent,
        "GoalGenerator": GoalGeneratorAgent,
    }

    def __init__(self):
        self.active_agents: Dict[str, BaseAgent] = {}
        self.creator = AgentCreatorManager()

    def get_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """Get or create an agent by type."""
        if agent_type in self.active_agents:
            return self.active_agents[agent_type]

        if agent_type in self.AGENT_SPECS:
            spec = self.AGENT_SPECS[agent_type]

            if agent_type == "Coordinator":
                agent = AgentCoordinatorAgent(spec, self)
            elif agent_type in self.AGENT_CLASSES:
                agent = self.AGENT_CLASSES[agent_type](spec)
            else:
                return None

            self.active_agents[agent_type] = agent
            return agent

        return None

    def create_custom_agent(self, spec: AgentSpec) -> BaseAgent:
        """Create a custom agent from a specification."""
        # For now, create a generic agent
        # In production, this would dynamically generate agent code

        class CustomAgent(BaseAgent):
            def run(self, task: str, context: Dict = None) -> AgentResult:
                start = time.time()
                self.log(f"Executing: {task[:50]}...")

                prompt = f"{self.spec.system_prompt}\n\nTask: {task}"
                output = self.think(prompt)

                return AgentResult(
                    agent_name=self.name,
                    success=True,
                    output=output,
                    execution_time=time.time() - start
                )

        agent = CustomAgent(spec)
        self.active_agents[spec.name] = agent
        if not spec.agent_id:
            entry = self.creator.register_runtime_agent(
                name=spec.name,
                purpose=spec.purpose,
                model_id=spec.model,
                requester_id="factory",
                requester_type="system",
            )
            spec.agent_id = entry.get("agent_id")
            agent.agent_id = spec.agent_id
        return agent

    def provision_agent(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Provision a new agent workspace via the creator manager."""
        return self.creator.provision(request)

    def list_agents(self) -> List[str]:
        """List available agent types."""
        return list(self.AGENT_SPECS.keys())


# =============================================================================
# INTEGRATION WITH GPIA
# =============================================================================

class SelfImprovingGPIA:
    """
    GPIA that uses agents to close its own capability gaps.

    The bootstrap loop:
    1. Identify gaps
    2. Create agents to fill gaps
    3. Run agents
    4. Learn from results
    5. Improve
    """

    def __init__(self):
        from gpia import GPIA
        self.gpia = GPIA(verbose=False)
        self.factory = AgentFactory()
        self.improvement_history: List[Dict] = []

    def identify_gaps(self) -> List[str]:
        """Identify current capability gaps."""
        # Use GoalGenerator to analyze and find gaps
        agent = self.factory.get_agent("GoalGenerator")

        observations = f"""
System status:
- Skills loaded: {self.gpia.state.skills_loaded}
- Tasks completed: {self.gpia.state.task_count}
- Last task: {self.gpia.state.last_task or 'None'}
- Last result: {(self.gpia.state.last_result or '')[:200]}

Recent improvement history: {len(self.improvement_history)} iterations
"""
        result = agent.run(observations)

        # Extract gaps from analysis
        gaps = []
        if "weaknesses" in str(result.output).lower():
            gaps.append("improvement_needed")
        if "opportunities" in str(result.output).lower():
            gaps.append("opportunities_available")

        return gaps

    def improve(self, focus: str = None) -> Dict:
        """
        Run one improvement cycle.

        This is the core self-improvement loop.
        """
        print("=" * 50)
        print("SELF-IMPROVEMENT CYCLE")
        print("=" * 50)

        # Step 1: Identify what to improve
        if focus:
            improvement_target = focus
        else:
            gaps = self.identify_gaps()
            improvement_target = gaps[0] if gaps else "general_improvement"

        print(f"\nTarget: {improvement_target}")

        # Step 2: Use Coordinator to orchestrate improvement
        coordinator = self.factory.get_agent("Coordinator")

        task = f"""Improve the system's capability regarding: {improvement_target}

Available actions:
1. Analyze current failures and find patterns
2. Create new skills to fill gaps
3. Propose new goals for continuous improvement
4. Debug existing issues

What should we do to improve?"""

        result = coordinator.run(task, {
            "skills_loaded": self.gpia.state.skills_loaded,
            "task_count": self.gpia.state.task_count,
        })

        # Step 3: Record improvement
        improvement = {
            "timestamp": datetime.now().isoformat(),
            "target": improvement_target,
            "agents_used": result.sub_agents_created,
            "output": str(result.output)[:500],
            "success": result.success
        }
        self.improvement_history.append(improvement)

        print(f"\nAgents used: {result.sub_agents_created}")
        print(f"Time: {result.execution_time:.2f}s")
        print("=" * 50)

        return improvement

    def run_with_agents(self, task: str) -> Dict:
        """
        Run a task, using agents if needed.

        If the task is complex, delegate to Coordinator.
        """
        # Quick complexity check
        complexity_check = query_fast(
            f"Is this task complex enough to need multiple agents? Task: {task}\nAnswer: yes or no",
            max_tokens=10
        )

        if "yes" in complexity_check.lower():
            print("[GPIA] Complex task - using agent coordination")
            coordinator = self.factory.get_agent("Coordinator")
            result = coordinator.run(task)
            return {
                "response": result.output,
                "agents_used": result.sub_agents_created,
                "reasoning": result.reasoning
            }
        else:
            print("[GPIA] Simple task - direct execution")
            result = self.gpia.run(task)
            return {
                "response": result.response,
                "agents_used": [],
                "reasoning": result.reasoning_trace
            }


def main():
    """Demo the self-improving GPIA."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              SELF-IMPROVING GPIA                              ║
║                                                               ║
║  GPIA + Agents = Recursive Self-Improvement                   ║
║                                                               ║
║  Commands:                                                    ║
║    /improve     - Run self-improvement cycle                  ║
║    /agents      - List available agents                       ║
║    /gaps        - Identify capability gaps                    ║
║    /quit        - Exit                                        ║
╚═══════════════════════════════════════════════════════════════╝
""")

    gpia = SelfImprovingGPIA()
    print(f"Loaded {gpia.gpia.state.skills_loaded} skills")
    print(f"Available agents: {gpia.factory.list_agents()}")

    while True:
        try:
            task = input("\n[You] > ").strip()

            if not task:
                continue

            if task == "/quit":
                break

            if task == "/agents":
                for name in gpia.factory.list_agents():
                    spec = gpia.factory.AGENT_SPECS[name]
                    print(f"  {name}: {spec.purpose}")
                continue

            if task == "/gaps":
                gaps = gpia.identify_gaps()
                print(f"Identified gaps: {gaps}")
                continue

            if task == "/improve":
                result = gpia.improve()
                print(f"\nImprovement result: {result}")
                continue

            # Regular task with agent support
            result = gpia.run_with_agents(task)
            print(f"\n[GPIA] {result['response']}")
            if result['agents_used']:
                print(f"\n(Agents: {', '.join(result['agents_used'])})")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\nGoodbye!")


if __name__ == "__main__":
    main()
