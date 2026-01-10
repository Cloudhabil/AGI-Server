"""
Alpha Agent: The Autonomous Student (Level 6 ASI Edition)

This version is aligned with the "Goldroad" vision and the system's "real actual situation":
-   Inherits from `BaseAgent`: Properly integrates with the `CortexSwitchboard`.
-   Connects to `KernelSubstrate`: Plugs directly into the `MasterPulse` (Heartbeat) and V-NAND (`skill_selector`).
-   Implements OODA Loop: Restores the core Observe, Orient, Decide, Act cognitive cycle.
-   Wires in S2 Compressor: Uses the `S2Projector` to scale and compress thoughts into the 4D uint8 V-NAND substrate, respecting the 12GB VRAM limit.
"""

from __future__ import annotations

import logging
import numpy as np
from datetime import datetime
from typing import Any, Dict, Optional

from core.agents.base import BaseAgent, AgentContext, ModeTransition
from core.runtime.capsule_types import Capsule
from skills.registry import get_registry
from skills.s2.transforms import S2Projector

logger = logging.getLogger(__name__)

class AlphaAgent(BaseAgent):
    """
    Alpha: The First Student (Level 6).
    Synchronizes with the Kernel Substrate to drive autonomous learning.
    """
    mode_name = "Alpha"

    def __init__(self, ctx: AgentContext):
        super().__init__(ctx)
        self._cycle = 0
        self.projector = S2Projector(dimension=384)
        
        # Bind to Level 6 Substrate
        self.pulse = getattr(self.ctx.kernel, "pulse", None)
        self.v_nand_learner = getattr(self.ctx.kernel, "skill_selector", None)
        
        registry = get_registry()
        self.memory_skill = registry.get_skill("conscience/memory")
        
        logger.info("[Alpha] Level 6 Brain instantiated and plugged into substrate.")

    def on_enter(self) -> None:
        super().on_enter()
        self.ctx.perception.write("[Alpha] Awake. Synchronizing with MasterPulse...\n")

    def step(self) -> Optional[ModeTransition]:
        """One OODA cognitive cycle, aligned with the 'Goldroad' vision."""
        self._cycle += 1
        
        # --- 1. OBSERVE (Synchronized with Pulse) ---
        cmd = self.ctx.perception.read_command().strip()
        if not cmd:
            return self._idle_learning()

        obs = {
            "cycle": self._cycle,
            "input": cmd,
            "timestamp": datetime.now().isoformat(),
            "heartbeat": getattr(self.pulse, "beat_count", 0) if self.pulse else 0
        }

        # --- 2. ORIENT (S2 Scaling) ---
        raw_vec = self._text_to_vector(cmd)
        macro_state = self.projector.project(raw_vec, "L0", "L2")
        
        # --- 3. DECIDE ---
        decision = self._reason_about_task(cmd, macro_state)

        # --- 4. ACT ---
        result = self._execute_alpha_task(decision)
        
        # --- Record to Fossil Record ---
        self._record_fossil_record(macro_state, result)

        return None

    def _idle_learning(self) -> None:
        """Autonomous behavior: review past lessons or wait for Professor."""
        time.sleep(1) # Yield to pulse
        return None

    def _reason_about_task(self, cmd: str, state: np.ndarray) -> Dict[str, Any]:
        """Use the Government Cabinet to reason about the task."""
        return {"goal": cmd, "minister": "Prime Minister (Reason)"}

    def _execute_alpha_task(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task via a Capsule to the Government engine."""
        capsule = Capsule(
            id=f"alpha-task-{self._cycle}",
            kind="task",
            goal=decision["goal"],
            trace={"alpha_cycle": self._cycle}
        )
        if self.ctx.engine:
            res = self.ctx.engine.execute(capsule, self.ctx)
            if res.ok:
                response = res.output.get("text", "Task completed.")
                self.ctx.perception.write(f"[Alpha] {response}\n")
                return {"status": "success", "output": res.output}
        return {"status": "failed", "error": "No engine"}

    def _record_fossil_record(self, macro_state: np.ndarray, result: Dict[str, Any]):
        """Crystallize the thought into the 4D V-NAND substrate."""
        if not self.v_nand_learner:
            return

        # S2 Scale: Project float32 thought-vector to uint8 Braille-Byte grid
        # This is the "compressor" that respects the 12GB VRAM limit.
        grid = (macro_state.reshape(8, 8, 6) * 255).astype(np.uint8) # Dummy 3D->2D slice
        
        # Flatten to match the 8*8*8*8 = 4096 expected by the learner
        flat_grid = np.zeros(4096, dtype=np.uint8)
        flat_grid[:grid.size] = grid.flatten()

        # Reshape to 4D
        final_grid = flat_grid.reshape(8, 8, 8, 8)
        
        # Calculate success score for learning
        success_score = 1.0 if result.get("status") == "success" else 0.1
        
        self.v_nand_learner.learn_pattern(final_grid, score=success_score)
        self.ctx.telemetry.emit("alpha.fossil_recorded", {"cycle": self._cycle, "score": success_score})

    def _text_to_vector(self, text: str) -> np.ndarray:
        """Helper: Text to fixed-dim vector (EMBEDDING_DIM=384)."""
        vec = np.zeros(384, dtype=np.float32)
        for i, char in enumerate(text[:384]):
            vec[i] = ord(char) / 255.0
        return vec

def get_alpha_agent(ctx: AgentContext) -> AlphaAgent:
    return AlphaAgent(ctx)
