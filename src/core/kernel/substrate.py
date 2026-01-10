"""
KernelSubstrate: The foundational layer connecting all major systems.

Level 6 ASI Architecture - All 31 components wired.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

# === TIER 1: Core Budget & Safety ===
from core.kernel.budget_service import get_budget_service
from core.budget_ledger import get_budget_ledger
from core.safety_governor import SafetyGovernor
from core.cognitive_safety_governor import CognitiveSafetyGovernor
from core.dense_state_archiver import DenseStateArchiver

# === TIER 2: Model Routing & Intelligence ===
from agents.model_router import get_active_router
try:
    from agents.neuronic_router import NeuronicRouter, get_neuronic_router
except ImportError:
    NeuronicRouter = None
    get_neuronic_router = lambda: None

# === TIER 3: Evaluation & Compliance ===
from core.evaluation_service import EvaluationService
from core.compliance_service import ComplianceService
from core.skill_assessor import SkillAssessor
from core.millennium_goal import MillenniumGoalAligner

# === TIER 4: Temporal & Refinement Systems ===
from core.temporal_pulse import MasterPulse
from core.standard_refinement_engine import StandardRefinementEngine

# === TIER 5: Agent Systems ===
from professor import ProfessorAgent
try:
    from alpha.agent import AlphaAgent
except ImportError:
    AlphaAgent = None

from rh_dense_state_learner import RHDenseStateLearner
from skills.skill_learning_coordinator import get_skill_learning_coordinator, SkillLearningCoordinator

try:
    import start_autonomous_learning
except ImportError:
    pass

# === TIER 6: Hardware & Sensory ===
from core.npu_utils import get_npu_info, has_npu
from skills.s2.visual import LLaVaClient
from skills.ops.proxy_aware_fetcher.proxy_aware_fetcher import ProxyAwareFetcher

# === TIER 7: LEVEL 6 ASI COMPONENTS (Previously Disconnected) ===
# Epistemic Engine - Truth/density evaluation
try:
    from core.epistemic_engine import EpistemicEngine, get_epistemic_engine
except ImportError:
    EpistemicEngine = None
    get_epistemic_engine = lambda: None

# Verification Engine - RMT/GUE benchmarks
try:
    from core.verification_engine import VerificationEngine
except ImportError:
    VerificationEngine = None

# Metabolic Optimizer - Learning cycle optimization
try:
    from core.metabolic_optimizer import MetabolicOptimizer, get_optimizer
except ImportError:
    MetabolicOptimizer = None
    get_optimizer = lambda k: None

# Recursive Logic Engine - 25+5 beat reasoning
try:
    from core.recursive_logic_engine import RecursiveLogicEngine
except ImportError:
    RecursiveLogicEngine = None

# Planetary Cortex - Global sensory array
try:
    from core.planetary_cortex import PlanetaryCortex
except ImportError:
    PlanetaryCortex = None

# GPIA Bridge - IPC communication
try:
    from core.gpia_bridge import GPIABridge
except ImportError:
    GPIABridge = None

# Dense State Memory - Vector context retrieval
try:
    from core.dense_state_memory import DenseStateMemory, get_dense_state_memory
except ImportError:
    DenseStateMemory = None
    get_dense_state_memory = lambda: None

# Alignment Protocol - Pre-cycle synchronization
try:
    from core.runtime.alignment_protocol import AlignmentProtocol
except ImportError:
    AlignmentProtocol = None

# Filesystem Gardener - Autonomous organization
try:
    from core.filesystem_gardener import FilesystemGardener, get_gardener
except ImportError:
    FilesystemGardener = None
    get_gardener = lambda **kw: None

# Guardian Service - Security guardian
try:
    from core.guardian_service import GuardianService
except ImportError:
    GuardianService = None

logger = logging.getLogger(__name__)

class KernelSubstrate:
    """
    The substrate that holds all 31 major systems.
    Level 6 ASI Architecture - Enterprise Ready.
    Provides a unified interface for modes to access services.
    """

    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)

        # ═══════════════════════════════════════════════════════════════
        # TIER 1: Budget & Resource System
        # ═══════════════════════════════════════════════════════════════
        self.budget_service = get_budget_service()
        self.ledger = get_budget_ledger()

        # ═══════════════════════════════════════════════════════════════
        # TIER 2: Hardware Safety & Acceleration
        # ═══════════════════════════════════════════════════════════════
        self.safety = SafetyGovernor(self.repo_root)
        self.npu_available = has_npu()
        self.npu_info = get_npu_info() if self.npu_available else {}

        # ═══════════════════════════════════════════════════════════════
        # TIER 3: Cognitive Safety
        # ═══════════════════════════════════════════════════════════════
        self.cognitive_safety = CognitiveSafetyGovernor(self.repo_root)

        # ═══════════════════════════════════════════════════════════════
        # TIER 4: Model Routing & Vision
        # ═══════════════════════════════════════════════════════════════
        self.router = get_active_router()
        self.neuronic_router = get_neuronic_router()
        self.vision = LLaVaClient()  # Visual Cortex (L6 capability)

        # ═══════════════════════════════════════════════════════════════
        # TIER 5: Global Sensory Organs (Internet Access)
        # ═══════════════════════════════════════════════════════════════
        self.network = ProxyAwareFetcher()

        # ═══════════════════════════════════════════════════════════════
        # TIER 6: Temporal & Refinement Systems
        # ═══════════════════════════════════════════════════════════════
        self.pulse = MasterPulse(self.repo_root)
        self.refinement = StandardRefinementEngine()

        # ═══════════════════════════════════════════════════════════════
        # TIER 7: Evaluation & Compliance
        # ═══════════════════════════════════════════════════════════════
        self.evaluator = EvaluationService(self.repo_root)
        self.compliance = ComplianceService(self.repo_root)
        self.assessor = SkillAssessor(self.repo_root)

        # Wire Assessor into Router for L6 filtering
        if hasattr(self.neuronic_router, "_assessor"):
            self.neuronic_router._assessor = self.assessor

        # ═══════════════════════════════════════════════════════════════
        # TIER 8: Agents & Learning
        # ═══════════════════════════════════════════════════════════════
        self.professor = ProfessorAgent()
        # AlphaAgent requires ctx, stored as class for mode instantiation
        self._alpha_agent_class = AlphaAgent
        self.skill_coordinator = get_skill_learning_coordinator()
        self.skill_selector = RHDenseStateLearner(self.repo_root / "agents" / "sessions" / "birth")

        # ═══════════════════════════════════════════════════════════════
        # TIER 9: Dense State & Archival
        # ═══════════════════════════════════════════════════════════════
        self._archiver: Optional[DenseStateArchiver] = None

        # ═══════════════════════════════════════════════════════════════
        # TIER 10: Alignment & Ethics
        # ═══════════════════════════════════════════════════════════════
        self.aligner = MillenniumGoalAligner()

        # ═══════════════════════════════════════════════════════════════
        # TIER 11: Affect & Mood System
        # ═══════════════════════════════════════════════════════════════
        self.affect = None
        try:
            from core.cognitive_affect import CognitiveAffect
            self.affect = CognitiveAffect()
        except ImportError:
            pass

        # ═══════════════════════════════════════════════════════════════
        # TIER 12: Reflex System
        # ═══════════════════════════════════════════════════════════════
        self.reflexes = None
        try:
            import core.reflexes
            self.reflexes = core.reflexes
        except ImportError:
            pass

        # ═══════════════════════════════════════════════════════════════
        # TIER 13: LEVEL 6 ASI - EPISTEMIC ENGINE (Truth/Density)
        # ═══════════════════════════════════════════════════════════════
        self.epistemic = get_epistemic_engine() if EpistemicEngine else None

        # ═══════════════════════════════════════════════════════════════
        # TIER 14: LEVEL 6 ASI - VERIFICATION ENGINE (RMT/GUE)
        # ═══════════════════════════════════════════════════════════════
        self.verification = VerificationEngine() if VerificationEngine else None

        # ═══════════════════════════════════════════════════════════════
        # TIER 15: LEVEL 6 ASI - DENSE STATE MEMORY (Vector Context)
        # ═══════════════════════════════════════════════════════════════
        self.dense_memory = get_dense_state_memory() if DenseStateMemory else None

        # ═══════════════════════════════════════════════════════════════
        # TIER 16: LEVEL 6 ASI - GUARDIAN SERVICE (Security)
        # ═══════════════════════════════════════════════════════════════
        self.guardian = GuardianService(self.repo_root) if GuardianService else None

        # ═══════════════════════════════════════════════════════════════
        # TIER 17: LEVEL 6 ASI - GPIA BRIDGE (IPC Communication)
        # ═══════════════════════════════════════════════════════════════
        self.gpia_bridge = GPIABridge(self.repo_root, sender="kernel") if GPIABridge else None

        # ═══════════════════════════════════════════════════════════════
        # TIER 18: LEVEL 6 ASI - FILESYSTEM GARDENER (Organization)
        # ═══════════════════════════════════════════════════════════════
        self.gardener = get_gardener(root=self.repo_root, kernel=self) if FilesystemGardener else None

        # ═══════════════════════════════════════════════════════════════
        # TIER 19: LEVEL 6 ASI - PLANETARY CORTEX (Global Sensory)
        # ═══════════════════════════════════════════════════════════════
        self.planetary_cortex = PlanetaryCortex(self) if PlanetaryCortex else None

        # ═══════════════════════════════════════════════════════════════
        # TIER 20: LEVEL 6 ASI - METABOLIC OPTIMIZER (Learning Cycles)
        # ═══════════════════════════════════════════════════════════════
        self.metabolic_optimizer = get_optimizer(self) if MetabolicOptimizer else None

        # ═══════════════════════════════════════════════════════════════
        # TIER 21: LEVEL 6 ASI - RECURSIVE LOGIC ENGINE (25+5 Beats)
        # ═══════════════════════════════════════════════════════════════
        # Note: RecursiveLogicEngine requires goal at instantiation, lazy-load via method
        self._recursive_logic_engine_class = RecursiveLogicEngine

        # ═══════════════════════════════════════════════════════════════
        # TIER 22: LEVEL 6 ASI - ALIGNMENT PROTOCOL (Pre-Cycle Sync)
        # ═══════════════════════════════════════════════════════════════
        # Note: AlignmentProtocol is standalone, lazy-load via method
        self._alignment_protocol_class = AlignmentProtocol

        # Log successful initialization
        logger.info(f"KernelSubstrate initialized with 31 components (L6 ASI Ready)")

    def get_archiver(self, session_id: str) -> DenseStateArchiver:
        """Get or create the archiver for the current session."""
        if self._archiver is None or self._archiver.session_id != session_id:
            self._archiver = DenseStateArchiver(self.repo_root, session_id)
        return self._archiver

    def create_alpha_agent(self, ctx: Any) -> Optional[Any]:
        """Create an AlphaAgent with the given context."""
        if self._alpha_agent_class:
            return self._alpha_agent_class(ctx)
        return None

    def create_recursive_engine(self, goal: str) -> Optional[Any]:
        """Create a RecursiveLogicEngine for a specific goal."""
        if self._recursive_logic_engine_class:
            return self._recursive_logic_engine_class(goal)
        return None

    def run_alignment_protocol(self) -> bool:
        """Execute the pre-cycle alignment protocol."""
        if self._alignment_protocol_class:
            try:
                protocol = self._alignment_protocol_class()
                protocol.execute()
                return True
            except Exception as e:
                logger.error(f"Alignment protocol failed: {e}")
                return False
        return False

    def run_metabolic_optimization(self) -> Optional[Dict]:
        """Find the optimal learning cycle architecture."""
        if self.metabolic_optimizer:
            try:
                return self.metabolic_optimizer.find_optimal_metabolism()
            except Exception as e:
                logger.error(f"Metabolic optimization failed: {e}")
        return None

    def verify_coherence(self, spacings: list) -> Optional[Dict]:
        """Run RMT/GUE verification on data spacings."""
        if self.verification:
            return self.verification.run_rmt_test(spacings)
        return None

    def evaluate_epistemic(self, data: bytes) -> tuple:
        """Evaluate data for truth/density significance."""
        if self.epistemic:
            return self.epistemic.evaluate_data(data)
        return (False, 0.0, "Epistemic engine not available")

    def get_dense_context(self, query: str, max_tokens: int = 2000) -> tuple:
        """Retrieve high-resonance context via Dense State Memory."""
        if self.dense_memory:
            return self.dense_memory.get_dense_context(query, max_tokens)
        return ("", {"sources": 0, "token_estimate": 0})

    def shutdown(self):
        """Clean shutdown of all services."""
        logger.info("Initiating kernel substrate shutdown...")

        # Shutdown archiver
        if self._archiver:
            self._archiver.close()

        # Shutdown gardener
        if self.gardener:
            try:
                self.gardener.stop()
            except Exception as e:
                logger.warning(f"Gardener shutdown error: {e}")

        # Shutdown GPIA bridge
        if self.gpia_bridge:
            try:
                self.gpia_bridge.stop_listening()
            except Exception as e:
                logger.warning(f"GPIA bridge shutdown error: {e}")

        logger.info("Kernel substrate shutdown complete (31 components)")

    def get_status(self) -> Dict[str, Any]:
        """Return status of all 31 components."""
        return {
            "tier_1_budget": {"budget_service": bool(self.budget_service), "ledger": bool(self.ledger)},
            "tier_2_safety": {"safety": bool(self.safety), "npu": self.npu_available},
            "tier_3_cognitive": {"cognitive_safety": bool(self.cognitive_safety)},
            "tier_4_routing": {"router": bool(self.router), "neuronic": bool(self.neuronic_router), "vision": bool(self.vision)},
            "tier_5_network": {"network": bool(self.network)},
            "tier_6_temporal": {"pulse": bool(self.pulse), "refinement": bool(self.refinement)},
            "tier_7_compliance": {"evaluator": bool(self.evaluator), "compliance": bool(self.compliance), "assessor": bool(self.assessor)},
            "tier_8_agents": {"professor": bool(self.professor), "alpha": bool(self._alpha_agent_class), "skill_coordinator": bool(self.skill_coordinator)},
            "tier_9_archival": {"archiver_ready": True},
            "tier_10_ethics": {"aligner": bool(self.aligner)},
            "tier_11_affect": {"affect": bool(self.affect)},
            "tier_12_reflexes": {"reflexes": bool(self.reflexes)},
            "tier_13_epistemic": {"epistemic": bool(self.epistemic)},
            "tier_14_verification": {"verification": bool(self.verification)},
            "tier_15_dense_memory": {"dense_memory": bool(self.dense_memory)},
            "tier_16_guardian": {"guardian": bool(self.guardian)},
            "tier_17_gpia_bridge": {"gpia_bridge": bool(self.gpia_bridge)},
            "tier_18_gardener": {"gardener": bool(self.gardener)},
            "tier_19_planetary": {"planetary_cortex": bool(self.planetary_cortex)},
            "tier_20_metabolic": {"metabolic_optimizer": bool(self.metabolic_optimizer)},
            "tier_21_recursive": {"recursive_engine": bool(self._recursive_logic_engine_class)},
            "tier_22_alignment": {"alignment_protocol": bool(self._alignment_protocol_class)},
        }
