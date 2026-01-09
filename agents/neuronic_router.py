"""
Neuronic Router: PASS-Integrated Model Orchestrator
===================================================

Implements the "Neuronic" gap-closure by integrating the PASS Protocol
directly into the Model Routing layer. 

Features:
1. Mood-Aware Hyperparameters: Modulates temperature/top_p based on CognitiveAffect.
2. Epistemic Gating: Uses EpistemicCalibration to trigger PASS on low-confidence.
3. Recursive Resolution: Automates the Capsule/Assist loop for blocked tasks.
"""

import logging
import json
import uuid
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from agents.model_router import get_router, ModelRouter, Model
from core.pass_protocol import (
    PassOrchestrator, 
    Capsule,
    CapsuleState,
    ProtocolParser,
    PassResponse,
    SuccessResponse
)
from core.cognitive_affect import CognitiveAffect
from skills.base import SkillContext

logger = logging.getLogger("NeuronicRouter")

# Optional cognition skills with fallbacks
try:
    from skills.cognition.epistemic_calibration.skill import EpistemicCalibrationSkill, CertaintyLevel
except Exception as e:
    logger.warning(f"EpistemicCalibration missing, using no-op stub: {e}")
    class CertaintyLevel:
        HIGH = "HIGH"
    class EpistemicCalibrationSkill:
        def execute(self, *args, **kwargs):
            return type("R", (), {"output": {"confidence_score": 1.0, "reasoning": "stub high confidence"}})()

try:
    from skills.cognition.neuro_intuition import NeuroIntuitionSkill
except Exception as e:
    logger.warning(f"NeuroIntuition missing, using no-op stub: {e}")
    class NeuroIntuitionSkill:
        def execute(self, params, ctx):
            return type("R", (), {"output": {"selected_id": None, "intuition_score": 0.0, "rationale": "stub"}})()

class NeuronicRouter:
    def __init__(self):
        self.base_router = get_router()
        self.orchestrator = PassOrchestrator()
        self.affect = CognitiveAffect()
        self.epistemic = EpistemicCalibrationSkill()
        self.intuition = NeuroIntuitionSkill()
        self.confidence_threshold = 0.65

    def query(
        self, 
        prompt: str, 
        task: str = None, 
        context: Dict = None,
        depth: int = 0
    ) -> str:
        """
        Agentic query loop with PASS and Intuition integration.
        """
        if depth > 3:
            return "[Error: Max PASS Recursion Depth Exceeded]"

        # 1. Intuition Pass: Select the model dynamically
        intuition_result = self.intuition.execute({
            "capability": "align_model",
            "task_query": prompt
        }, SkillContext()).output
        
        selected_model = intuition_result.get("selected_id", task)
        logger.info(f"Neural Intuition selected: {selected_model} (Score: {intuition_result.get('intuition_score')})")

        mood_params = self._get_mood_adjustments()
        
        # 2. Execute Query with Intuition-Selected Model
        raw_output = self.base_router.query(
            prompt=prompt,
            model=selected_model,
            temperature=mood_params["temperature"],
            max_tokens=mood_params["max_tokens"]
        )
        
        if not raw_output:
            raw_output = ""

        # 2. Protocol Parsing (Check if model self-identified a PASS)
        protocol_msg = ProtocolParser.parse(raw_output)

        # 3. Epistemic Calibration (Force PASS on hidden low confidence)
        if isinstance(protocol_msg, SuccessResponse):
            calibration = self.epistemic.execute({
                "capability": "assess_confidence",
                "draft_response": str(protocol_msg.output),
                "query": prompt
            }, SkillContext()).output
            
            conf_score = calibration.get("confidence_score", 1.0)
            if conf_score < self.confidence_threshold:
                logger.warning(f"Epistemic Gate Triggered: Confidence {conf_score:.2f} < {self.confidence_threshold}")
                # Convert success to a forced PASS
                protocol_msg = ProtocolParser._prose_to_pass(
                    f"Low confidence response detected. Reasoning: {calibration.get('reasoning')}"
                )

        # 4. Handle PASS Protocol
        if isinstance(protocol_msg, PassResponse):
            logger.info(f"Initiating PASS Protocol resolution...")
            
            # Create Task Capsule
            capsule = self.orchestrator.create_capsule(
                task=prompt,
                agent_id="gpia_neuronic_router",
                context=context or {}
            )
            
            # Record the PASS
            capsule = self.orchestrator.handle_pass(capsule, protocol_msg)
            
            # Recursive Assist Resolution
            for need in protocol_msg.needs:
                resolver = self.orchestrator.get_resolver_for_need(need)        
                logger.info(f"Resolving Need: {need.id} via {resolver}")        

                # Simulate Assist via Model Router (Arbiter Mode)
                assist_prompt = f"Provide assistance for: {need.description}. Context: {raw_output}"
                # Let router pick the best model for this need (no hard-coded arbiter)
                assist_content = self.base_router.query(assist_prompt, task=None, model=None)
                
                from core.pass_protocol import AssistResponse
                assist_resp = AssistResponse(
                    need_id=need.id,
                    content=assist_content,
                    success=True
                )
                capsule = self.orchestrator.provide_assist(capsule, assist_resp, resolver)

            # Resume Task with Enriched Context
            if capsule.state == CapsuleState.ASSISTED:
                self.orchestrator.resume(capsule)
                resumed_prompt = f"{prompt}\n\n## ADDED CONTEXT FROM ASSISTANTS ##\n{self.orchestrator.build_assist_context(capsule)}"
                return self.query(resumed_prompt, task=task, context=capsule.context, depth=depth+1)

        # 5. Return Validated Result
        return str(protocol_msg.output if isinstance(protocol_msg, SuccessResponse) else raw_output)

    def _get_mood_adjustments(self) -> Dict[str, Any]:
        """Convert current mood to LLM hyperparameters."""
        # Get current config from affect system
        mood_config = self.affect.MOOD_SKILLS.get(self.affect.active_mood_skill, {})
        
        exploration = mood_config.get("exploration", 0.5)
        rigor = mood_config.get("rigor", 0.5)
        safety = mood_config.get("safety", 0.0)
        
        # Calculate Temperature
        if safety > 0.8:
            # Reflex Mode: Deterministic
            temp = 0.0
        else:
            # Base 0.5 + (Exp * 0.6) - (Rigor * 0.4)
            temp = 0.5 + (exploration * 0.6) - (rigor * 0.4)
            temp = max(0.1, min(1.0, temp)) # Keep strictly positive
        
        return {
            "temperature": round(temp, 2),
            "max_tokens": 1024 if rigor > 0.6 else 800
        }


# Singleton instance
_neuronic_router = None

def get_neuronic_router() -> NeuronicRouter:
    global _neuronic_router
    if _neuronic_router is None:
        _neuronic_router = NeuronicRouter()
    return _neuronic_router
