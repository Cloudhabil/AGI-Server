"""
GPIA Multi-Agent Mission: Learn LoRA Self-Modification (Enhanced)
==================================================================

Goal: Use all available LLMs to research, understand, and acquire
all skills needed for LoRA self-modification capabilities.

ENHANCEMENTS:
1. PASS Protocol - If any agent is blocked, PASS to get assists
2. Parallel Execution - Run independent phases simultaneously
3. Skill Auto-Registration - Learned skills added to GPIA registry
4. Memory Persistence - Store learnings in MSHR memory system

Agents:
- CodeGemma (Fast): Intent parsing, quick lookups
- Qwen3 (Creative): Code generation, solution design
- DeepSeek-R1 (Reasoning): Deep analysis, architecture decisions
- GPT-OSS:20b (Synthesis): Multi-perspective integration
- LLaVa (Vision): Diagram understanding (if needed)
"""
# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


import json
import sys
import time
import threading
import concurrent.futures
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import traceback

# Ensure UTF-8
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from agents.model_router import (
    query_fast, query_creative, query_reasoning, query_synthesis
)
from core.pass_protocol import (
    Capsule, CapsuleState, Need, NeedType,
    PassResponse, SuccessResponse, AssistResponse,
    PassOrchestrator, CapsuleStore, ProtocolParser
)


# =============================================================================
# ENUMS & DATA CLASSES
# =============================================================================

class PhaseStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"      # Waiting for assist
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRole(str, Enum):
    FAST = "codegemma"
    CREATIVE = "qwen3"
    REASONING = "deepseek-r1"
    SYNTHESIS = "gpt-oss:20b"
    VISION = "llava"


@dataclass
class PhaseResult:
    """Result of a mission phase."""
    phase_name: str
    status: PhaseStatus
    agent: AgentRole
    output: Any
    duration_seconds: float
    pass_count: int = 0
    assist_count: int = 0
    error: Optional[str] = None


@dataclass
class MissionState:
    """Current state of the mission."""
    mission_id: str
    goal: str
    phases: Dict[str, PhaseResult] = field(default_factory=dict)
    knowledge: Dict[str, Any] = field(default_factory=dict)
    skills_registered: List[str] = field(default_factory=list)
    memories_stored: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None


# =============================================================================
# PASS-ENABLED AGENT
# =============================================================================

class PassEnabledAgent:
    """
    An agent that uses PASS protocol when blocked.

    If the primary query fails or returns "I don't know",
    it PASSes to get assists from other agents.
    """

    def __init__(self, orchestrator: PassOrchestrator, verbose: bool = True):
        self.orchestrator = orchestrator
        self.verbose = verbose
        self.query_functions = {
            AgentRole.FAST: query_fast,
            AgentRole.CREATIVE: query_creative,
            AgentRole.REASONING: query_reasoning,
            AgentRole.SYNTHESIS: query_synthesis,
        }

    def log(self, message: str):
        if self.verbose:
            print(f"    [Agent] {message}")

    def execute_with_pass(
        self,
        task: str,
        primary_agent: AgentRole,
        context: Dict = None,
        max_passes: int = 3,
        timeout: int = 180
    ) -> tuple[Any, int, int]:
        """
        Execute a task with PASS protocol support.

        Returns: (result, pass_count, assist_count)
        """
        # Create capsule for this task
        capsule = self.orchestrator.create_capsule(
            task=task,
            agent_id=primary_agent.value,
            context=context or {}
        )

        pass_count = 0
        assist_count = 0
        query_fn = self.query_functions.get(primary_agent, query_creative)

        while capsule.state not in [CapsuleState.COMPLETED, CapsuleState.FAILED]:
            if pass_count > max_passes:
                self.log(f"Max passes ({max_passes}) exceeded, failing")
                capsule.state = CapsuleState.FAILED
                break

            # Build prompt with PASS protocol rules
            assist_context = self.orchestrator.build_assist_context(capsule)

            prompt = f"""TASK: {task}

CONTEXT: {json.dumps(capsule.context, default=str)[:1500]}
{assist_context}

INSTRUCTIONS:
- If you can complete this task, provide a comprehensive response.
- If you need information you don't have, clearly state what you need.
- Be thorough and technical.

RESPONSE:"""

            try:
                # Query the agent
                response = query_fn(prompt, max_tokens=2000, timeout=timeout)

                # Check if response indicates being blocked
                if self._is_blocked_response(response):
                    pass_count += 1
                    self.log(f"PASS #{pass_count} - Agent needs assistance")

                    # Extract what's needed and get assists
                    needs = self._extract_needs(response, task)
                    pass_response = PassResponse(
                        needs=needs,
                        partial_work=response[:500],
                        resume_hint="Continue with the additional information"
                    )

                    capsule = self.orchestrator.handle_pass(capsule, pass_response)

                    # Get assists from other agents
                    for need in needs:
                        assist = self._get_assist(need, capsule.context)
                        capsule = self.orchestrator.provide_assist(
                            capsule, assist, assist.notes
                        )
                        assist_count += 1

                    # Resume
                    if capsule.state == CapsuleState.ASSISTED:
                        capsule = self.orchestrator.resume(capsule)
                        capsule.state = CapsuleState.ACTIVE
                else:
                    # Success!
                    capsule = self.orchestrator.complete(capsule, response)

            except Exception as e:
                self.log(f"Error: {e}")
                pass_count += 1
                if pass_count > max_passes:
                    capsule.state = CapsuleState.FAILED
                    capsule.context["error"] = str(e)

        result = capsule.context.get("final_output", capsule.context.get("error", "Failed"))
        return result, pass_count, assist_count

    def _is_blocked_response(self, response: str) -> bool:
        """Check if response indicates the agent is blocked."""
        blocked_patterns = [
            "i don't know",
            "i cannot",
            "i can't",
            "i'm not sure",
            "i need more information",
            "i would need",
            "unable to determine",
            "insufficient information",
            "cannot provide",
            "don't have access",
        ]
        response_lower = response.lower()
        return any(pattern in response_lower for pattern in blocked_patterns)

    def _extract_needs(self, response: str, task: str) -> List[Need]:
        """Extract needs from a blocked response."""
        needs = []

        # Use fast model to extract needs
        extract_prompt = f"""The following response indicates the agent needs help.
Extract what specific information or capabilities are needed.

Response: {response[:1000]}

Original task: {task}

Output JSON array of needs:
[{{"type": "knowledge|file|capability", "id": "identifier", "description": "what is needed"}}]
"""
        try:
            extract_response = query_fast(extract_prompt, max_tokens=300, timeout=30)
            if "[" in extract_response:
                json_str = extract_response[extract_response.find("["):extract_response.rfind("]")+1]
                needs_data = json.loads(json_str)
                for n in needs_data:
                    needs.append(Need(
                        type=NeedType(n.get("type", "knowledge")),
                        id=n.get("id", "unknown"),
                        description=n.get("description", "")
                    ))
        except:
            # Fallback: create generic knowledge need
            needs.append(Need(
                type=NeedType.KNOWLEDGE,
                id="task_assistance",
                description=f"Help completing: {task[:200]}"
            ))

        return needs

    def _get_assist(self, need: Need, context: Dict) -> AssistResponse:
        """Get assistance for a need from another agent."""
        # Route to appropriate agent based on need type
        if need.type == NeedType.KNOWLEDGE:
            # Use reasoning model for knowledge
            prompt = f"""Provide information about: {need.id}

Description: {need.description}

Context: {json.dumps(context, default=str)[:500]}

Be comprehensive and technical."""

            response = query_reasoning(prompt, max_tokens=1000, timeout=90)
            return AssistResponse(
                need_id=need.id,
                content=response,
                success=True,
                notes="DeepSeek-R1"
            )

        elif need.type == NeedType.CAPABILITY:
            # Use creative model for capability suggestions
            prompt = f"""Suggest how to implement: {need.id}

Description: {need.description}

Provide practical code or approach."""

            response = query_creative(prompt, max_tokens=800, timeout=60)
            return AssistResponse(
                need_id=need.id,
                content=response,
                success=True,
                notes="Qwen3"
            )

        else:
            # Generic assist via synthesis
            prompt = f"""Help with: {need.description}"""
            response = query_creative(prompt, max_tokens=500, timeout=45)
            return AssistResponse(
                need_id=need.id,
                content=response,
                success=True,
                notes="Generic"
            )


# =============================================================================
# MEMORY PERSISTENCE
# =============================================================================

class MemoryPersistence:
    """Store learnings in MSHR memory system."""

    def __init__(self):
        self.memory_skill = None
        self._init_memory()

    def _init_memory(self):
        """Initialize memory skill."""
        try:
            from skills.conscience.memory.skill import MemorySkill
            from skills.base import SkillContext
            self.memory_skill = MemorySkill(use_mshr=True)
            self.context = SkillContext(agent_role="mission_learner")
        except Exception as e:
            print(f"[Memory] Could not initialize: {e}")
            self.memory_skill = None

    def store_learning(
        self,
        content: str,
        memory_type: str = "semantic",
        importance: float = 0.8,
        tags: List[str] = None
    ) -> Optional[str]:
        """Store a learning in memory."""
        if not self.memory_skill:
            return None

        try:
            result = self.memory_skill.execute({
                "capability": "experience",
                "content": content,
                "memory_type": memory_type,
                "importance": importance,
                "metadata": {"tags": tags or [], "source": "lora_learning_mission"}
            }, self.context)

            memory_id = result.output.get("memory_id") if result.output else None
            return memory_id
        except Exception as e:
            print(f"[Memory] Store failed: {e}")
            return None

    def store_phase_result(self, phase_name: str, result: PhaseResult) -> List[str]:
        """Store phase results as memories."""
        stored = []

        # Store main result
        if isinstance(result.output, str) and len(result.output) > 100:
            # Chunk large outputs
            chunks = self._chunk_text(result.output, max_size=2000)
            for i, chunk in enumerate(chunks):
                memory_id = self.store_learning(
                    content=f"[{phase_name} Part {i+1}] {chunk}",
                    memory_type="semantic",
                    importance=0.8,
                    tags=["lora", "self-modification", phase_name.lower()]
                )
                if memory_id:
                    stored.append(memory_id)
        elif isinstance(result.output, dict):
            memory_id = self.store_learning(
                content=f"[{phase_name}] {json.dumps(result.output, default=str)[:2000]}",
                memory_type="semantic",
                importance=0.8,
                tags=["lora", "self-modification", phase_name.lower()]
            )
            if memory_id:
                stored.append(memory_id)

        return stored

    def _chunk_text(self, text: str, max_size: int = 2000) -> List[str]:
        """Split text into chunks."""
        chunks = []
        for i in range(0, len(text), max_size):
            chunks.append(text[i:i+max_size])
        return chunks


# =============================================================================
# SKILL AUTO-REGISTRATION
# =============================================================================

class SkillAutoRegistration:
    """Automatically register learned skills with GPIA."""

    def __init__(self, skills_dir: str = "skills/learned"):
        self.skills_dir = Path(skills_dir)
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def register_skill(
        self,
        skill_id: str,
        name: str,
        description: str,
        code: str,
        capabilities: List[Dict]
    ) -> Optional[str]:
        """Register a new skill from learned code."""
        skill_path = self.skills_dir / skill_id
        skill_path.mkdir(parents=True, exist_ok=True)

        # Create manifest
        manifest = {
            "id": f"learned/{skill_id}",
            "name": name,
            "description": description,
            "version": "1.0.0",
            "level": "advanced",
            "category": "learned",
            "capabilities": capabilities,
            "auto_generated": True,
            "generated_at": datetime.now().isoformat(),
            "source": "lora_learning_mission"
        }

        # Write manifest
        manifest_path = skill_path / "manifest.yaml"
        import yaml
        try:
            with open(manifest_path, 'w', encoding='utf-8') as f:
                yaml.dump(manifest, f, default_flow_style=False)
        except ImportError:
            # Fallback to JSON if yaml not available
            manifest_path = skill_path / "manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)

        # Write skill code
        skill_file = skill_path / "skill.py"
        with open(skill_file, 'w', encoding='utf-8') as f:
            f.write(code)

        # Update skill index
        self._update_index(skill_id, manifest)

        return str(skill_path)

    def _update_index(self, skill_id: str, manifest: Dict):
        """Update the skills INDEX.json."""
        index_path = Path("skills/INDEX.json")
        try:
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {"skills": [], "updated_at": None}

            # Add or update skill
            existing = [s for s in index["skills"] if s.get("id") != manifest["id"]]
            existing.append({
                "id": manifest["id"],
                "name": manifest["name"],
                "description": manifest["description"],
                "category": manifest["category"],
                "level": manifest["level"]
            })

            index["skills"] = existing
            index["updated_at"] = datetime.now().isoformat()

            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2)

        except Exception as e:
            print(f"[SkillReg] Index update failed: {e}")


# =============================================================================
# PARALLEL PHASE EXECUTOR
# =============================================================================

class ParallelPhaseExecutor:
    """Execute independent phases in parallel."""

    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def execute_parallel(
        self,
        phases: List[tuple[str, Callable, Dict]],  # (name, func, kwargs)
        timeout: int = 300
    ) -> Dict[str, PhaseResult]:
        """Execute phases in parallel, return results."""
        results = {}
        futures = {}

        for phase_name, func, kwargs in phases:
            future = self.executor.submit(func, **kwargs)
            futures[future] = phase_name

        # Wait for completion
        done, not_done = concurrent.futures.wait(
            futures.keys(),
            timeout=timeout,
            return_when=concurrent.futures.ALL_COMPLETED
        )

        for future in done:
            phase_name = futures[future]
            try:
                results[phase_name] = future.result()
            except Exception as e:
                results[phase_name] = PhaseResult(
                    phase_name=phase_name,
                    status=PhaseStatus.FAILED,
                    agent=AgentRole.FAST,
                    output=None,
                    duration_seconds=0,
                    error=str(e)
                )

        for future in not_done:
            phase_name = futures[future]
            future.cancel()
            results[phase_name] = PhaseResult(
                phase_name=phase_name,
                status=PhaseStatus.FAILED,
                agent=AgentRole.FAST,
                output=None,
                duration_seconds=timeout,
                error="Timeout"
            )

        return results

    def shutdown(self):
        self.executor.shutdown(wait=False)


# =============================================================================
# ENHANCED MISSION ORCHESTRATOR
# =============================================================================

class EnhancedMissionOrchestrator:
    """
    Orchestrates a multi-agent learning mission with:
    1. PASS Protocol - Automatic assist when blocked
    2. Parallel Execution - Independent phases run concurrently
    3. Skill Registration - Learned skills added to GPIA
    4. Memory Persistence - Learnings stored in MSHR
    """

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

        # Core components
        self.store = CapsuleStore("data/missions")
        self.orchestrator = PassOrchestrator(self.store)
        self.agent = PassEnabledAgent(self.orchestrator, verbose)

        # Enhancement components
        self.memory = MemoryPersistence()
        self.skill_registry = SkillAutoRegistration()
        self.parallel_executor = ParallelPhaseExecutor(max_workers=3)

        # State
        self.mission_state: Optional[MissionState] = None
        self.mission_log: List[Dict] = []

    def log(self, phase: str, message: str, model: str = None):
        """Log mission progress."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "message": message,
            "model": model
        }
        self.mission_log.append(entry)
        if self.verbose:
            model_tag = f"[{model}]" if model else ""
            print(f"[{phase}] {model_tag} {message}")

    def run_mission(self) -> Dict[str, Any]:
        """Execute the full LoRA learning mission with all enhancements."""

        print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║       GPIA ENHANCED MULTI-AGENT MISSION: LEARN LoRA SELF-MODIFICATION         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  ENHANCEMENTS ACTIVE:                                                         ║
║    ✓ PASS Protocol    - Auto-assist when agents are blocked                   ║
║    ✓ Parallel Exec    - Independent phases run concurrently                   ║
║    ✓ Skill Registry   - Learned skills auto-registered                        ║
║    ✓ Memory Persist   - Learnings stored in MSHR                              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  PHASES:                                                                      ║
║    1. SCOPE        [CodeGemma]     Define objectives                          ║
║    2. RESEARCH     [DeepSeek-R1]   Deep dive (parallel: concepts + tools)     ║
║    3. ARCHITECTURE [DeepSeek-R1]   Design implementation                      ║
║    4. IMPLEMENT    [Qwen3]         Generate code (parallel: components)       ║
║    5. SYNTHESIZE   [GPT-OSS:20b]   Integrate learnings                        ║
║    6. REGISTER     [System]        Register skills & store memories           ║
║    7. VALIDATE     [DeepSeek-R1]   Verify completeness                        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
""")

        start_time = time.time()

        # Initialize mission state
        import uuid
        self.mission_state = MissionState(
            mission_id=str(uuid.uuid4())[:12],
            goal="Learn and acquire all skills related to LoRA Self-Modification"
        )

        self.log("INIT", f"Mission ID: {self.mission_state.mission_id}")

        try:
            # Phase 1: SCOPE (sequential - needed for other phases)
            scope_result = self._phase_scope()
            self.mission_state.phases["scope"] = scope_result
            self.mission_state.knowledge["scope"] = scope_result.output

            # Phase 2: RESEARCH (parallel - concepts and tools)
            research_results = self._phase_research_parallel(scope_result.output)
            self.mission_state.phases["research"] = research_results["combined"]
            self.mission_state.knowledge["research"] = research_results

            # Phase 3: ARCHITECTURE (sequential - depends on research)
            arch_result = self._phase_architecture()
            self.mission_state.phases["architecture"] = arch_result
            self.mission_state.knowledge["architecture"] = arch_result.output

            # Phase 4: IMPLEMENTATION (parallel - multiple components)
            impl_results = self._phase_implementation_parallel(arch_result.output)
            self.mission_state.phases["implementation"] = impl_results["combined"]
            self.mission_state.knowledge["implementation"] = impl_results

            # Phase 5: SYNTHESIS
            synth_result = self._phase_synthesis()
            self.mission_state.phases["synthesis"] = synth_result
            self.mission_state.knowledge["synthesis"] = synth_result.output

            # Phase 6: REGISTER (skills + memory)
            reg_result = self._phase_register()
            self.mission_state.phases["registration"] = reg_result

            # Phase 7: VALIDATE
            val_result = self._phase_validation()
            self.mission_state.phases["validation"] = val_result
            self.mission_state.knowledge["validation"] = val_result.output

        except Exception as e:
            self.log("ERROR", f"Mission failed: {e}")
            traceback.print_exc()

        # Finalize
        self.mission_state.end_time = datetime.now()
        elapsed = time.time() - start_time

        # Calculate totals
        total_passes = sum(p.pass_count for p in self.mission_state.phases.values() if hasattr(p, 'pass_count'))
        total_assists = sum(p.assist_count for p in self.mission_state.phases.values() if hasattr(p, 'assist_count'))

        # Save report
        report = {
            "mission_id": self.mission_state.mission_id,
            "goal": self.mission_state.goal,
            "status": "COMPLETED",
            "elapsed_seconds": elapsed,
            "total_passes": total_passes,
            "total_assists": total_assists,
            "skills_registered": self.mission_state.skills_registered,
            "memories_stored": len(self.mission_state.memories_stored),
            "phases": {
                name: {
                    "status": p.status.value if hasattr(p, 'status') else "unknown",
                    "agent": p.agent.value if hasattr(p, 'agent') else "unknown",
                    "duration": p.duration_seconds if hasattr(p, 'duration_seconds') else 0,
                    "pass_count": p.pass_count if hasattr(p, 'pass_count') else 0,
                }
                for name, p in self.mission_state.phases.items()
            },
            "knowledge_summary": {
                k: str(v)[:500] + "..." if len(str(v)) > 500 else str(v)
                for k, v in self.mission_state.knowledge.items()
            },
            "mission_log": self.mission_log,
        }

        report_path = Path(f"runs/mission_{self.mission_state.mission_id}.json")
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, default=str))

        # Cleanup
        self.parallel_executor.shutdown()

        # Print summary
        self._print_summary(report, elapsed)

        return report

    def _phase_scope(self) -> PhaseResult:
        """Phase 1: Define learning objectives."""
        print(f"\n{'─'*70}")
        self.log("SCOPE", "Defining learning objectives...", "CodeGemma")
        start = time.time()

        task = """Define comprehensive learning objectives for mastering LoRA Self-Modification.

Output JSON:
{
  "core_concepts": ["fundamental concepts to learn"],
  "technical_skills": ["specific skills needed"],
  "tools_libraries": ["tools to master: peft, transformers, bitsandbytes, trl"],
  "implementation_steps": ["high-level implementation steps"],
  "success_criteria": ["how to verify mastery"],
  "sub_topics": {
    "lora_fundamentals": ["low-rank matrices", "adapter injection", "weight merging"],
    "training": ["QLoRA", "gradient checkpointing", "DPO/RLHF"],
    "deployment": ["adapter hot-swap", "Ollama integration", "validation"]
  }
}

Be comprehensive. This guides the entire learning mission."""

        result, passes, assists = self.agent.execute_with_pass(
            task=task,
            primary_agent=AgentRole.FAST,
            timeout=90
        )

        # Parse result
        try:
            if isinstance(result, str) and "{" in result:
                json_str = result[result.find("{"):result.rfind("}")+1]
                output = json.loads(json_str)
            else:
                output = {"raw": result}
        except:
            output = {"raw": result}

        duration = time.time() - start
        self.log("SCOPE", f"Complete in {duration:.1f}s (passes: {passes}, assists: {assists})")

        return PhaseResult(
            phase_name="scope",
            status=PhaseStatus.COMPLETED,
            agent=AgentRole.FAST,
            output=output,
            duration_seconds=duration,
            pass_count=passes,
            assist_count=assists
        )

    def _phase_research_parallel(self, scope: Dict) -> Dict:
        """Phase 2: Research in parallel streams."""
        print(f"\n{'─'*70}")
        self.log("RESEARCH", "Starting parallel research streams...", "DeepSeek-R1")

        def research_concepts():
            start = time.time()
            task = f"""Research LoRA (Low-Rank Adaptation) core concepts:

Scope: {json.dumps(scope, default=str)[:1000]}

Cover in depth:
1. Mathematical foundation of LoRA (low-rank decomposition, r and alpha)
2. How LoRA modifies attention layers (Q, K, V, O projections)
3. Memory efficiency (why LoRA uses less VRAM than full fine-tuning)
4. QLoRA: 4-bit quantization + LoRA
5. Adapter merging strategies (linear interpolation, task arithmetic)

Be thorough and technical. Include formulas where helpful."""

            result, passes, assists = self.agent.execute_with_pass(
                task=task,
                primary_agent=AgentRole.REASONING,
                timeout=180
            )
            return PhaseResult(
                phase_name="research_concepts",
                status=PhaseStatus.COMPLETED,
                agent=AgentRole.REASONING,
                output=result,
                duration_seconds=time.time() - start,
                pass_count=passes,
                assist_count=assists
            )

        def research_training():
            start = time.time()
            task = """Research LoRA training techniques:

Cover in depth:
1. DPO (Direct Preference Optimization) for preference learning
2. RLHF alternatives (RLAIF, Constitutional AI)
3. Catastrophic forgetting prevention
4. Online/continual learning approaches
5. Training hyperparameters for 7B models on 12GB VRAM

Include practical configurations and code snippets."""

            result, passes, assists = self.agent.execute_with_pass(
                task=task,
                primary_agent=AgentRole.REASONING,
                timeout=180
            )
            return PhaseResult(
                phase_name="research_training",
                status=PhaseStatus.COMPLETED,
                agent=AgentRole.REASONING,
                output=result,
                duration_seconds=time.time() - start,
                pass_count=passes,
                assist_count=assists
            )

        def research_deployment():
            start = time.time()
            task = """Research LoRA deployment and hot-swapping:

Cover:
1. Adapter storage formats (safetensors, GGUF, GGML)
2. Ollama Modelfile creation with adapters
3. Runtime adapter loading/unloading
4. Validation and benchmarking strategies
5. Rollback mechanisms

Focus on practical implementation with Ollama."""

            result, passes, assists = self.agent.execute_with_pass(
                task=task,
                primary_agent=AgentRole.REASONING,
                timeout=180
            )
            return PhaseResult(
                phase_name="research_deployment",
                status=PhaseStatus.COMPLETED,
                agent=AgentRole.REASONING,
                output=result,
                duration_seconds=time.time() - start,
                pass_count=passes,
                assist_count=assists
            )

        # Execute in parallel
        self.log("RESEARCH", "Launching 3 parallel research streams...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_concepts = executor.submit(research_concepts)
            future_training = executor.submit(research_training)
            future_deployment = executor.submit(research_deployment)

            results = {
                "concepts": future_concepts.result(),
                "training": future_training.result(),
                "deployment": future_deployment.result(),
            }

        # Combine results
        total_duration = max(r.duration_seconds for r in results.values())
        total_passes = sum(r.pass_count for r in results.values())
        total_assists = sum(r.assist_count for r in results.values())

        results["combined"] = PhaseResult(
            phase_name="research",
            status=PhaseStatus.COMPLETED,
            agent=AgentRole.REASONING,
            output={k: v.output for k, v in results.items() if k != "combined"},
            duration_seconds=total_duration,
            pass_count=total_passes,
            assist_count=total_assists
        )

        self.log("RESEARCH", f"All streams complete in {total_duration:.1f}s (parallel)")
        return results

    def _phase_architecture(self) -> PhaseResult:
        """Phase 3: Design architecture."""
        print(f"\n{'─'*70}")
        self.log("ARCHITECTURE", "Designing implementation architecture...", "DeepSeek-R1")
        start = time.time()

        research = self.mission_state.knowledge.get("research", {})

        task = f"""Design the complete architecture for LoRA Self-Modification in GPIA.

Research findings:
{json.dumps(research, default=str)[:3000]}

Hardware constraints:
- RTX 4070 SUPER (12GB VRAM)
- Ollama for model serving
- Models: qwen3, deepseek-r1, codegemma (all ~7B)

Design these components with clear interfaces:

1. PREFERENCE COLLECTOR
   - Data model for preference pairs
   - Storage schema (SQLite)
   - Export formats for training

2. TRAINING PIPELINE
   - QLoRA configuration for 12GB
   - Background training manager
   - Progress tracking

3. VALIDATION SYSTEM
   - Benchmark suite design
   - Regression detection
   - Pass/fail criteria

4. DEPLOYMENT MANAGER
   - Adapter file management
   - Ollama Modelfile generation
   - Hot-swap protocol

5. GPIA INTEGRATION
   - Skill interface
   - PASS protocol integration
   - Multi-agent coordination

Output as detailed JSON with component specifications."""

        result, passes, assists = self.agent.execute_with_pass(
            task=task,
            primary_agent=AgentRole.REASONING,
            timeout=180
        )

        # Parse
        try:
            if isinstance(result, str) and "{" in result:
                json_str = result[result.find("{"):result.rfind("}")+1]
                output = json.loads(json_str)
            else:
                output = {"design": result}
        except:
            output = {"design": result}

        duration = time.time() - start
        self.log("ARCHITECTURE", f"Complete in {duration:.1f}s")

        return PhaseResult(
            phase_name="architecture",
            status=PhaseStatus.COMPLETED,
            agent=AgentRole.REASONING,
            output=output,
            duration_seconds=duration,
            pass_count=passes,
            assist_count=assists
        )

    def _phase_implementation_parallel(self, architecture: Dict) -> Dict:
        """Phase 4: Implementation in parallel."""
        print(f"\n{'─'*70}")
        self.log("IMPLEMENT", "Starting parallel implementation...", "Qwen3")

        def implement_preference_collector():
            start = time.time()
            task = f"""Implement PreferenceCollector class for LoRA training data.

Architecture spec:
{json.dumps(architecture, default=str)[:1000]}

Requirements:
- SQLite storage with FTS
- collect(prompt, rejected, preferred, model, importance)
- export_for_training() -> JSONL in DPO format
- statistics() -> count by domain, model, etc.

Generate complete, production-ready Python code with:
- Type hints
- Docstrings
- Error handling
- Example usage"""

            result, passes, assists = self.agent.execute_with_pass(
                task=task,
                primary_agent=AgentRole.CREATIVE,
                timeout=180
            )
            return PhaseResult(
                phase_name="impl_preference_collector",
                status=PhaseStatus.COMPLETED,
                agent=AgentRole.CREATIVE,
                output=result,
                duration_seconds=time.time() - start,
                pass_count=passes,
                assist_count=assists
            )

        def implement_trainer():
            start = time.time()
            task = """Implement LoRATrainer class for QLoRA fine-tuning.

Requirements:
- QLoRA config for 12GB VRAM (4-bit, rank=16)
- train(preferences, base_model, output_path)
- Background training with threading
- Progress callbacks
- Uses: peft, transformers, bitsandbytes, trl

Generate complete Python code optimized for RTX 4070."""

            result, passes, assists = self.agent.execute_with_pass(
                task=task,
                primary_agent=AgentRole.CREATIVE,
                timeout=180
            )
            return PhaseResult(
                phase_name="impl_trainer",
                status=PhaseStatus.COMPLETED,
                agent=AgentRole.CREATIVE,
                output=result,
                duration_seconds=time.time() - start,
                pass_count=passes,
                assist_count=assists
            )

        def implement_adapter_manager():
            start = time.time()
            task = """Implement AdapterManager class for Ollama integration.

Requirements:
- save_adapter(adapter_path, metadata)
- load_adapter(adapter_id) -> path
- create_modelfile(base_model, adapter_path) -> Modelfile content
- register_with_ollama(modelfile_path, model_name)
- swap_active_adapter(adapter_id)
- rollback()

Generate complete Python code with Ollama CLI integration."""

            result, passes, assists = self.agent.execute_with_pass(
                task=task,
                primary_agent=AgentRole.CREATIVE,
                timeout=180
            )
            return PhaseResult(
                phase_name="impl_adapter_manager",
                status=PhaseStatus.COMPLETED,
                agent=AgentRole.CREATIVE,
                output=result,
                duration_seconds=time.time() - start,
                pass_count=passes,
                assist_count=assists
            )

        # Execute in parallel
        self.log("IMPLEMENT", "Launching 3 parallel implementation tasks...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                "preference_collector": executor.submit(implement_preference_collector),
                "trainer": executor.submit(implement_trainer),
                "adapter_manager": executor.submit(implement_adapter_manager),
            }

            results = {k: f.result() for k, f in futures.items()}

        # Combine
        total_duration = max(r.duration_seconds for r in results.values())
        total_passes = sum(r.pass_count for r in results.values())
        total_assists = sum(r.assist_count for r in results.values())

        results["combined"] = PhaseResult(
            phase_name="implementation",
            status=PhaseStatus.COMPLETED,
            agent=AgentRole.CREATIVE,
            output={k: v.output for k, v in results.items() if k != "combined"},
            duration_seconds=total_duration,
            pass_count=total_passes,
            assist_count=total_assists
        )

        self.log("IMPLEMENT", f"All implementations complete in {total_duration:.1f}s (parallel)")
        return results

    def _phase_synthesis(self) -> PhaseResult:
        """Phase 5: Synthesize all learnings."""
        print(f"\n{'─'*70}")
        self.log("SYNTHESIZE", "Integrating all learnings...", "GPT-OSS:20b")
        start = time.time()

        task = f"""Synthesize all learnings about LoRA Self-Modification.

KNOWLEDGE ACQUIRED:

1. SCOPE:
{json.dumps(self.mission_state.knowledge.get('scope', {}), default=str)[:800]}

2. RESEARCH (Concepts):
{str(self.mission_state.knowledge.get('research', {}).get('concepts', {}).output if hasattr(self.mission_state.knowledge.get('research', {}).get('concepts', {}), 'output') else '')[:800]}

3. ARCHITECTURE:
{json.dumps(self.mission_state.knowledge.get('architecture', {}), default=str)[:800]}

4. IMPLEMENTATION:
Components built: preference_collector, trainer, adapter_manager

Create a comprehensive synthesis:

1. EXECUTIVE SUMMARY (what we learned, what we can do)
2. KEY TECHNICAL INSIGHTS (top 10)
3. IMPLEMENTATION CHECKLIST (what's ready vs needs work)
4. CAPABILITY MATRIX (can do / cannot do / needs research)
5. INTEGRATION GUIDE (how to use with GPIA)
6. NEXT STEPS (prioritized)

Make this actionable and complete."""

        result, passes, assists = self.agent.execute_with_pass(
            task=task,
            primary_agent=AgentRole.SYNTHESIS,
            timeout=240
        )

        duration = time.time() - start
        self.log("SYNTHESIZE", f"Complete in {duration:.1f}s")

        return PhaseResult(
            phase_name="synthesis",
            status=PhaseStatus.COMPLETED,
            agent=AgentRole.SYNTHESIS,
            output=result,
            duration_seconds=duration,
            pass_count=passes,
            assist_count=assists
        )

    def _phase_register(self) -> PhaseResult:
        """Phase 6: Register skills and persist memories."""
        print(f"\n{'─'*70}")
        self.log("REGISTER", "Registering skills and storing memories...", "System")
        start = time.time()

        # Store each phase's learnings in memory
        for phase_name, phase_result in self.mission_state.phases.items():
            if hasattr(phase_result, 'output') and phase_result.output:
                memory_ids = self.memory.store_phase_result(phase_name, phase_result)
                self.mission_state.memories_stored.extend(memory_ids)
                self.log("REGISTER", f"Stored {len(memory_ids)} memories from {phase_name}")

        # Register implementation as skills
        impl = self.mission_state.knowledge.get("implementation", {})
        if impl:
            for component_name, component_result in impl.items():
                if component_name == "combined":
                    continue

                if hasattr(component_result, 'output') and component_result.output:
                    code = component_result.output if isinstance(component_result.output, str) else str(component_result.output)

                    # Only register if it looks like actual code
                    if "class " in code or "def " in code:
                        skill_path = self.skill_registry.register_skill(
                            skill_id=f"lora_{component_name}",
                            name=f"LoRA {component_name.replace('_', ' ').title()}",
                            description=f"Auto-generated {component_name} for LoRA self-modification",
                            code=code,
                            capabilities=[{"name": component_name, "description": f"LoRA {component_name}"}]
                        )
                        if skill_path:
                            self.mission_state.skills_registered.append(skill_path)
                            self.log("REGISTER", f"Registered skill: {component_name}")

        duration = time.time() - start

        return PhaseResult(
            phase_name="registration",
            status=PhaseStatus.COMPLETED,
            agent=AgentRole.FAST,
            output={
                "memories_stored": len(self.mission_state.memories_stored),
                "skills_registered": self.mission_state.skills_registered
            },
            duration_seconds=duration,
            pass_count=0,
            assist_count=0
        )

    def _phase_validation(self) -> PhaseResult:
        """Phase 7: Validate mission completeness."""
        print(f"\n{'─'*70}")
        self.log("VALIDATE", "Validating mission completeness...", "DeepSeek-R1")
        start = time.time()

        scope = self.mission_state.knowledge.get("scope", {})

        task = f"""Validate the LoRA Self-Modification learning mission.

ORIGINAL OBJECTIVES:
{json.dumps(scope, default=str)[:1000]}

WHAT WAS ACCOMPLISHED:
- Research: 3 parallel streams (concepts, training, deployment)
- Architecture: Complete system design
- Implementation: 3 components (preference_collector, trainer, adapter_manager)
- Synthesis: Integrated knowledge base
- Registration: {len(self.mission_state.skills_registered)} skills, {len(self.mission_state.memories_stored)} memories

Validate each objective:
1. Was it addressed? (fully/partially/not)
2. Evidence
3. Gaps remaining

Output JSON:
{{
  "overall_completion_percent": 0-100,
  "objectives_fully_met": ["list"],
  "objectives_partially_met": ["list"],
  "objectives_not_met": ["list"],
  "critical_gaps": ["list"],
  "recommendations": ["prioritized list"],
  "mission_success": true/false,
  "confidence": 0.0-1.0
}}"""

        result, passes, assists = self.agent.execute_with_pass(
            task=task,
            primary_agent=AgentRole.REASONING,
            timeout=120
        )

        # Parse
        try:
            if isinstance(result, str) and "{" in result:
                json_str = result[result.find("{"):result.rfind("}")+1]
                output = json.loads(json_str)
            else:
                output = {"assessment": result}
        except:
            output = {"assessment": result}

        duration = time.time() - start
        self.log("VALIDATE", f"Complete in {duration:.1f}s")

        return PhaseResult(
            phase_name="validation",
            status=PhaseStatus.COMPLETED,
            agent=AgentRole.REASONING,
            output=output,
            duration_seconds=duration,
            pass_count=passes,
            assist_count=assists
        )

    def _print_summary(self, report: Dict, elapsed: float):
        """Print mission summary."""
        print(f"\n{'='*70}")
        print("MISSION COMPLETE")
        print(f"{'='*70}")

        print(f"\nMission ID: {report['mission_id']}")
        print(f"Duration: {elapsed:.1f}s")
        print(f"Total PASS events: {report['total_passes']}")
        print(f"Total assists: {report['total_assists']}")

        print(f"\nSkills Registered: {len(report['skills_registered'])}")
        for skill in report['skills_registered']:
            print(f"  → {skill}")

        print(f"\nMemories Stored: {report['memories_stored']}")

        val = self.mission_state.knowledge.get("validation", {})
        if isinstance(val, dict):
            print(f"\nValidation:")
            print(f"  Completion: {val.get('overall_completion_percent', 'N/A')}%")
            print(f"  Success: {val.get('mission_success', 'Unknown')}")
            print(f"  Confidence: {val.get('confidence', 'N/A')}")

            if val.get("critical_gaps"):
                print(f"\n  Critical Gaps:")
                for gap in val["critical_gaps"][:3]:
                    print(f"    • {gap}")

            if val.get("recommendations"):
                print(f"\n  Recommendations:")
                for rec in val["recommendations"][:3]:
                    print(f"    → {rec}")

        print(f"\nReport saved to: runs/mission_{report['mission_id']}.json")
        print(f"{'='*70}")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run the enhanced LoRA learning mission."""
    print("\n" + "="*70)
    print("GPIA ENHANCED MULTI-AGENT LEARNING MISSION")
    print("="*70)
    print("\nThis mission will:")
    print("  1. Use ALL available LLMs (CodeGemma, Qwen3, DeepSeek-R1, GPT-OSS:20b)")
    print("  2. Apply PASS protocol when agents are blocked")
    print("  3. Run independent phases in PARALLEL")
    print("  4. AUTO-REGISTER learned skills")
    print("  5. PERSIST learnings in MSHR memory")
    print("\nEstimated time: 5-15 minutes (with parallel execution)")
    print("="*70 + "\n")

    orchestrator = EnhancedMissionOrchestrator(verbose=True)

    try:
        report = orchestrator.run_mission()
        return report
    except KeyboardInterrupt:
        print("\n\nMission interrupted by user.")
    except Exception as e:
        print(f"\nMission failed: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()