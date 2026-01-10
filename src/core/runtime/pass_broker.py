from __future__ import annotations

from typing import Dict, List, TYPE_CHECKING, Any

from core.runtime.capsule_types import Capsule, CapsuleResult

if TYPE_CHECKING:
    from core.runtime.engines.government import GovernmentCapsuleEngine


class PassBroker:
    """
    Minimal PASS broker that gathers assists from designated ministers when a capsule is blocked.
    """

    def __init__(self, engine: Any):
        self.engine = engine

    def resolve(self, capsule: Capsule, res: CapsuleResult) -> CapsuleResult:
        """
        If CapsuleResult has pass_request, gather assists from ministers and attempt a resume.
        Handles both arbiter contradictions and low-confidence selection.
        """
        if not res.blocked or not res.pass_request:
            return res

        reason = res.pass_request.get("reason", "contradiction")
        needs: List[Dict] = res.pass_request.get("needs", [])
        assists = []
        
        for need in needs:
            role = (need.get("role") or "").lower()
            if "truth" in role:
                # Fact-check or quality-check via Minister of Truth
                if reason == "low_output_confidence":
                    prompt = (
                        f"The following response has low confidence for the goal '{res.pass_request.get('original_goal','')}'.\n"
                        f"LOW CONFIDENCE REPLY: {res.pass_request.get('original_reply','')}\n"
                        "Verify the facts and provide a corrected, high-certainty response."
                    )
                else:
                    prompt = f"Fact-check and resolve contradictions:\n{res.pass_request.get('critique','')}\nOriginal:\n{res.pass_request.get('original','')}"
                
                assist_text = self.engine.router.query(
                    prompt=prompt,
                    model=self.engine.gov.cabinet.get("Minister of Truth", self.engine.gov.president).model_id,
                    max_tokens=400,
                    temperature=0.1,
                    bypass_gov=True
                )
                assists.append({"role": "Truth", "content": assist_text})
            elif "intelligence" in role or "simulate" in role:
                # Clarify or simulate via Minister of Intelligence
                if reason == "low_confidence":
                    prompt = f"The system is unsure how to delegate this goal: '{capsule.goal}'. Clarify the intent and suggest which minister portfolio (Engineering, Truth, etc.) best fits this task."
                else:
                    prompt = f"Simulate alternatives to resolve critique:\n{res.pass_request.get('critique','')}\nOriginal:\n{res.pass_request.get('original','')}"
                
                assist_text = self.engine.router.query(
                    prompt=prompt,
                    model=self.engine.gov.cabinet.get("Minister of Intelligence", self.engine.gov.president).model_id,
                    max_tokens=400,
                    temperature=0.3,
                    bypass_gov=True
                )
                assists.append({"role": "Intelligence", "content": assist_text})

        # Attempt resume: feed assists back to the arbiter minister (President)
        if reason == "low_confidence":
            resume_prompt = (
                f"A goal was received with low delegation confidence. Assists provided:\n{assists}\n"
                f"Original Goal: {capsule.goal}\nExecute this goal now using your sovereign authority and the assists provided."
            )
        elif reason == "low_output_confidence":
            resume_prompt = (
                f"A response was rejected for low output confidence. Assists provided:\n{assists}\n"
                f"Original Goal: {res.pass_request.get('original_goal','')}\n"
                f"Original Reply: {res.pass_request.get('original_reply','')}\n"
                "Synthesize the assists and provide a final high-certainty response."
            )
        else:
            resume_prompt = (
                f"Resolve contradictions using assists:\n{assists}\nOriginal critique:\n"
                f"{res.pass_request.get('critique','')}\nOriginal output:\n{res.pass_request.get('original','')}"
            )

        corrected = self.engine.router.query(
            prompt=resume_prompt,
            model=self.engine.gov.president.model_id,
            max_tokens=800,
            temperature=0.1,
            bypass_gov=True
        )

        return CapsuleResult(
            ok=True,
            capsule_id=capsule.id,
            output={"text": corrected, "assists": assists, "minister": "President (PASS-Resolved)"},
            metrics={"resolved_via_pass": True, "pass_reason": reason},
        )
