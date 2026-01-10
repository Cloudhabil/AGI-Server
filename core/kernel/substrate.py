"""
KernelSubstrate: The foundational layer connecting all major systems.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from core.kernel.budget_service import get_budget_service
from core.budget_ledger import get_budget_ledger
from core.safety_governor import SafetyGovernor
from core.cognitive_safety_governor import CognitiveSafetyGovernor
from core.dense_state_archiver import DenseStateArchiver
from agents.model_router import get_active_router
from core.evaluation_service import EvaluationService
from core.compliance_service import ComplianceService
from core.skill_assessor import SkillAssessor
from core.millennium_goal import MillenniumGoalAligner

# Integration of previously orphaned systems
from core.temporal_pulse import MasterPulse
from core.standard_refinement_engine import StandardRefinementEngine
try:
    from agents.neuronic_router import NeuronicRouter, get_neuronic_router
except ImportError:
    NeuronicRouter = None
    get_neuronic_router = lambda: None

from professor import ProfessorAgent
try:
    from alpha.agent import AlphaAgent
except ImportError:
    AlphaAgent = None

from rh_dense_state_learner import RHDenseStateLearner
from skills.skill_learning_coordinator import get_skill_learning_coordinator, SkillLearningCoordinator

# Import launcher to register connection (handled carefully)
try:
    import start_autonomous_learning
except ImportError:
    pass

from core.npu_utils import get_npu_info, has_npu
from skills.s2.visual import LLaVaClient

logger = logging.getLogger(__name__)

class KernelSubstrate:
    """
    The substrate that holds all 'orphaned' major systems.
    Provides a unified interface for modes to access services.
    """

    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        
        # 1. Budget & Resource System
        self.budget_service = get_budget_service()
        self.ledger = get_budget_ledger()
        
        # 2. Hardware Safety & Acceleration
        self.safety = SafetyGovernor(self.repo_root)
        self.npu_available = has_npu()
        self.npu_info = get_npu_info() if self.npu_available else {}
        
        # 3. Cognitive Safety
        self.cognitive_safety = CognitiveSafetyGovernor(self.repo_root)
        
        # 4. Model Routing & Vision
        self.router = get_active_router()
        self.neuronic_router = get_neuronic_router()
        self.vision = LLaVaClient() # Visual Cortex (L6 capability)
        
        # 5. Temporal System
        self.pulse = MasterPulse(self.repo_root)
        
        # 6. Refinement Engine
        self.refinement = StandardRefinementEngine()
        
        # 7. Evaluation Service (Self-Test)
        self.evaluator = EvaluationService(self.repo_root)
        
        # 8. Compliance & Oversight (EU AI Act)
        self.compliance = ComplianceService(self.repo_root)
        
        # 9. Skill Assessment (Locker)
        self.assessor = SkillAssessor(self.repo_root)
        
        # Wire Assessor into Router for L6 filtering
        if hasattr(self.neuronic_router, "_assessor"):
            self.neuronic_router._assessor = self.assessor
        
        # 10. Agents & Learning
        self.professor = ProfessorAgent()
        self.alpha = AlphaAgent() if AlphaAgent else None
        
        self.skill_coordinator = get_skill_learning_coordinator()
        self.skill_selector = RHDenseStateLearner(self.repo_root / "agents" / "sessions" / "birth")
        
        # 11. Dense State Archival (Requires session_id, will lazy init)
        self._archiver: Optional[DenseStateArchiver] = None
        
        # 9. Alignment & Ethics
        self.aligner = MillenniumGoalAligner()
        
        # 10. Affect & Mood
        self.affect = None 
        try:
            from core.cognitive_affect import CognitiveAffect
            self.affect = CognitiveAffect()
        except ImportError:
            pass
            
        # 11. Reflex System (Lazy load)
        self.reflexes = None
        try:
            import core.reflexes
            self.reflexes = core.reflexes
        except ImportError:
            pass
        
        # 4. Dense State Archival (Requires session_id, will lazy init)
        self._archiver: Optional[DenseStateArchiver] = None
        
        # 5. Alignment & Ethics
        self.aligner = MillenniumGoalAligner()
        
        # 6. Affect & Mood (Lazy init or add here)
        self.affect = None 
        try:
            from core.cognitive_affect import CognitiveAffect
            self.affect = CognitiveAffect()
        except ImportError:
            pass

    def get_archiver(self, session_id: str) -> DenseStateArchiver:
        """Get or create the archiver for the current session."""
        if self._archiver is None or self._archiver.session_id != session_id:
            self._archiver = DenseStateArchiver(self.repo_root, session_id)
        return self._archiver

    def shutdown(self):
        """Clean shutdown of all services."""
        if self._archiver:
            self._archiver.close()
        logger.info("Kernel substrate shutdown complete")
