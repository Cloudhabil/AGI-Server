import logging
import requests
from typing import Any, Dict, Tuple, Optional

from agents.model_router import get_router
from core.agents.base import AgentContext
from core.runtime.capsule_engine import CapsuleEngine
from core.runtime.capsule_types import Capsule, CapsuleResult
from core.runtime.government import Government, Minister
from core.safety_governor import SafetyGovernor
from core.runtime.pass_broker import PassBroker
from core.runtime.metabolic_load_balancer import MetabolicLoadBalancer
from core.runtime.infrastructure_minister import InfrastructureMinister

logger = logging.getLogger(__name__)


class GovernmentCapsuleEngine(CapsuleEngine):
    """
    Cabinet-based routing. Selects a Minister (role) and executes via router.
    Backend IDs stay internal; logs show only titles/roles.
    """

    name = "government"

    def __init__(self) -> None:
        self.gov = Government.form_cabinet()
        self.router = get_router()
        self.governor = SafetyGovernor()
        self.pass_broker = PassBroker(self)
        self.load_balancer = MetabolicLoadBalancer(self.governor)
        self.infra = InfrastructureMinister()
        self.output_confidence_threshold = 0.7

    def _evaluate_output_confidence(self, capsule: Capsule, minister: Minister, reply: str) -> float:
        """
        Evaluate the confidence of a minister's output using the President.
        Returns a score between 0.0 and 1.0.
        """
        try:
            score_prompt = (
                f"AUDIT OBJECTIVE: Rate the following response from the {minister.title} on a scale of 0.0 to 1.0.\n"
                "CRITERIA: Clarity, logic, completeness, and adherence to the goal.\n"
                f"GOAL: {capsule.goal}\n"
                f"RESPONSE: {reply}\n\n"
                "Reply ONLY with the numerical score (e.g., '0.85')."
            )
            raw_score = self.router.query(
                prompt=score_prompt,
                model=self.gov.president.model_id,
                max_tokens=10,
                temperature=0.0,
                bypass_gov=True # Avoid recursion
            ).strip()
            
            # Extract float from response
            import re
            match = re.search(r"([0-1]\.\d+)", raw_score)
            if match:
                return float(match.group(1))
            return 0.5 # Default middle-ground if parsing fails
        except Exception:
            return 0.5

    def _select_minister(self, capsule: Capsule) -> Minister:
        minister, _ = self.gov.convene(capsule.goal or "")
        return minister

    def _arbiter_check(self, capsule: Capsule, minister: Minister, reply: str, ctx: AgentContext) -> CapsuleResult:
        """
        Run an arbiter (President) critique when requested via capsule.trace['arbiter'].
        """
        try:
            arbiter = self.gov.president
            critique_prompt = (
                "AUDIT OBJECTIVE: Find contradictions, circular logic, or physical impossibilities.\n"
                f"PROPOSAL:\n{reply}\n\nIf clear, reply 'VERDICT: CLEAR'."
            )
            critique = self.router.query(
                prompt=critique_prompt,
                model=arbiter.model_id,
                max_tokens=400,
                temperature=0.1,
                bypass_gov=True
            )
            if "VERDICT: CLEAR" in critique.upper():
                return CapsuleResult(
                    ok=True,
                    capsule_id=capsule.id,
                    output={"text": reply, "minister": minister.title},
                    metrics={"metabolic_cost": minister.metabolic_cost, "arbiter": "clear"},
                )
            # Contradiction -> request PASS assists
            return CapsuleResult(
                ok=False,
                capsule_id=capsule.id,
                error="arbiter_detected_contradiction",
                blocked=True,
                pass_request={
                    "needs": [
                        {"role": "Truth", "description": "Fact-check contradictions"},
                        {"role": "Intelligence", "description": "Simulate alternatives"},
                    ],
                    "critique": critique,
                    "original": reply,
                },
                metrics={"metabolic_cost": minister.metabolic_cost, "arbiter": "contradiction"},
            )
        except Exception as e:
            return CapsuleResult(
                ok=False,
                capsule_id=capsule.id,
                error=f"arbiter_failed: {e}",
                blocked=False,
            )

    def _query_with_url(self, prompt: str, model_id: str, url: str, **kwargs) -> str:
        """Direct query to a specific Ollama URL (bypassing the default router endpoint)."""
        try:
            payload = {
                "model": model_id,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.1),
                    "num_predict": kwargs.get("max_tokens", 800),
                },
            }
            # Append /api/generate if not present
            endpoint = f"{url.rstrip('/')}/api/generate"
            resp = requests.post(endpoint, json=payload, timeout=kwargs.get("timeout", 120))
            if resp.status_code == 200:
                return resp.json().get("response", "").strip()
        except Exception as e:
            logger.error(f"[GOVERNMENT] Direct query to {url} failed: {e}")
        return ""

    def _skill_reflex(self, capsule: Capsule, ctx: AgentContext) -> Optional[CapsuleResult]:
        """
        Reflex Layer: Check if a local skill can solve the goal before asking a Minister.
        """
        from skills.registry import get_registry
        from skills.base import SkillContext
        registry = get_registry()
        
        # 1. Direct Skill ID match (if provided in payload)
        skill_id = capsule.payload.get("skill_id")
        if skill_id and registry.has_skill(skill_id):
            print(f"[REFLEX] Executing identified skill: {skill_id}")
            res = registry.execute_skill(skill_id, capsule.payload, SkillContext())
            return CapsuleResult(
                ok=res.success,
                capsule_id=capsule.id,
                output={"text": res.output if isinstance(res.output, str) else str(res.output), "skill": skill_id},
                metrics={"reflex": True}
            )

        # 2. Semantic Skill Search (Asking the Archivist)
        print(f"[REFLEX] Scanning 819+ skills for matches to: '{capsule.goal}'...")
        # (This uses the Archivist minister internally via the router)
        search_prompt = f"Find the ID of a Python skill that can solve: '{capsule.goal}'. Reply ONLY with the skill ID or 'NONE'."
        matched_id = self.router.query(
            prompt=search_prompt, 
            model=self.gov.cabinet.get("The Archivist", self.gov.president).model_id,
            max_tokens=20,
            temperature=0.0,
            bypass_gov=True
        ).strip()

        if matched_id != "NONE" and registry.has_skill(matched_id):
            print(f"[REFLEX] Found matching skill: {matched_id}. Executing...")
            res = registry.execute_skill(matched_id, capsule.payload, SkillContext())
            if res.success:
                return CapsuleResult(
                    ok=True,
                    capsule_id=capsule.id,
                    output={"text": str(res.output), "skill": matched_id},
                    metrics={"reflex": True, "semantic_match": True}
                )

        return None

    def execute(self, capsule: Capsule, ctx: AgentContext) -> CapsuleResult:
        # 0. Substrate Self-Healing
        if not self.infra.heal_substrate():
            return CapsuleResult(ok=False, capsule_id=capsule.id, error="Substrate Down", blocked=True)

        # 1. SKILL REFLEX: Check if we already know how to do this
        reflex_res = self._skill_reflex(capsule, ctx)
        if reflex_res:
            ctx.telemetry.emit("government.reflex_hit", {"capsule_id": capsule.id, "skill": reflex_res.output.get("skill")})
            return reflex_res

        # VRAM mapping per metabolic cost label (MB)
        METABOLIC_VRAM_MAP = {
            "micro": 500,      # Small scripts/embedders
            "low": 4700,       # llava, mistral, president
            "medium": 5500,    # deepseek-r1, llama3:8b, qwen2-math
            "high": 8000,      # heavy reasoning
            "extreme": 13000   # gpt-oss:20b
        }

        try:
            # 2. Semantic Minister Selection
            minister, confidence = self.gov.convene(capsule.goal or "")
            required_vram = METABOLIC_VRAM_MAP.get(minister.metabolic_cost, 5000)
            
            # 3. Metabolic Load Balancing: Ensure model fits or REDIRECT TO STUDENT
            is_cleared, target_url = self.load_balancer.request_load(minister.model_id, required_vram)
            
            if not is_cleared:
                # METABOLIC DOWNGRADE
                ctx.telemetry.emit("government.metabolic_downgrade", {
                    "minister": minister.title, 
                    "reason": "VRAM_EXHAUSTED_ALL_NODES"
                })
                
                # Attempt to find a 'low' cost alternative (usually President)
                if minister.metabolic_cost not in ["micro", "low"]:
                    low_cost_minister = self.gov.president
                    safe_fallback, _ = self.governor.audit_system(required_vram_mb=METABOLIC_VRAM_MAP["low"])
                    
                    if safe_fallback:
                        res = CapsuleResult(
                            ok=False,
                            capsule_id=capsule.id,
                            error=f"Resource constraint. Downgrading to President.",
                            blocked=True,
                            pass_request={
                                "reason": "resource_downgrade",
                                "needs": [{"role": "Intelligence", "description": "Simplify task"}],
                                "original": capsule.goal,
                                "target_minister": minister.title
                            }
                        )
                        return self.pass_broker.resolve(capsule, res)

                return CapsuleResult(ok=False, capsule_id=capsule.id, error="Substrate Exhausted", blocked=True)

            # Emit state with target URL
            ctx.telemetry.emit(
                "capsule.execute.start",
                {
                    "engine": self.name, 
                    "capsule_id": capsule.id, 
                    "minister": minister.title, 
                    "node": target_url,
                    "confidence": float(confidence)
                },
            )

            # 4. Primary Execution
            temp = 0.1 if any(c in minister.capabilities for c in ["logic", "arbiter", "code"]) else 0.3
            
            if target_url == self.router.ollama_url:
                reply = self.router.query(
                    prompt=capsule.goal,
                    model=minister.model_id,
                    max_tokens=800,
                    temperature=temp,
                    bypass_gov=True
                )
            else:
                # REDIRECTED to Docker Student
                reply = self._query_with_url(
                    prompt=capsule.goal, 
                    model_id=minister.model_id, 
                    url=target_url, 
                    temperature=temp
                )

            # 5. Output Confidence Audit
            out_confidence = self._evaluate_output_confidence(capsule, minister, reply)
            if out_confidence < self.output_confidence_threshold:
                res = CapsuleResult(
                    ok=False,
                    capsule_id=capsule.id,
                    error=f"Low output confidence ({out_confidence:.2f})",
                    blocked=True,
                    pass_request={
                        "reason": "low_output_confidence",
                        "confidence": out_confidence,
                        "needs": [{"role": "Truth", "description": "Verify quality"}],
                        "original_reply": reply,
                        "original_goal": capsule.goal
                    }
                )
                return self.pass_broker.resolve(capsule, res)

            # 6. Mandatory Arbiter Path
            enforce_arbiter = capsule.trace.get("arbiter", False) or capsule.kind == "task"
            if enforce_arbiter:
                self.load_balancer.request_load(self.gov.president.model_id, 4700)
                arbiter_res = self._arbiter_check(capsule, minister, reply, ctx)
                if arbiter_res.blocked:
                    return self.pass_broker.resolve(capsule, arbiter_res)
                return arbiter_res

            return CapsuleResult(
                ok=True,
                capsule_id=capsule.id,
                output={"text": reply, "minister": minister.title, "confidence": out_confidence},
                metrics={"delegation_confidence": float(confidence), "output_confidence": out_confidence},
            )

        except Exception as e:
            ctx.telemetry.emit("capsule.execute.error", {"engine": self.name, "capsule_id": capsule.id, "error": str(e)})
            return CapsuleResult(ok=False, capsule_id=capsule.id, error=str(e))
