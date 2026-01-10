"""
Recursive Logic Engine (25+5) using GovernmentCapsuleEngine and Arbiter self-audit.
- Expansion: 25 beats (reasoning minister)
- Crystallization: 5 beats (crystallization minister + arbiter audit)
- Regularity filter (0.0219) and SafetyGovernor throttling
- PASS handoff: contradictions trigger a pass_request for assists
"""
from __future__ import annotations

import sys
import time
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.runtime.capsule_types import Capsule
from core.runtime.engines.government import GovernmentCapsuleEngine
from core.safety_governor import SafetyGovernor


class RecursiveLogicEngine:
    def __init__(self, goal: str):
        self.goal = goal
        self.engine = GovernmentCapsuleEngine()
        self.governor = SafetyGovernor(ROOT)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_path = ROOT / "logs" / "recursive_engine" / f"logic_strip_{self.session_id}.json"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        self.logic_strip = []
        self.regularity_threshold = 0.0219
        self.expansion_count = 25
        self.crystallization_count = 5

    def _throttle(self):
        """Phase 4: Hardware-Coupled Throttling"""
        safe, msg = self.governor.audit_system()
        if not safe:
            print(f"[ENGINE] Safety Governor Triggered: {msg}. Throttling...")
            factor = self.governor.get_throttle_factor()
            time.sleep(10 / factor)  # Mandatory wait

    def _verify_regularity(self, data: List[float]) -> bool:
        """Phase 3: 0.0219 Statistical Filter"""
        if len(data) < 5:
            return True
        variance = np.var(data)
        ratio = variance / np.mean(data) if np.mean(data) != 0 else 1.0

        is_coherent = ratio <= self.regularity_threshold
        if not is_coherent:
            print(f"[ENGINE] Regularity check FAILED (Ratio: {ratio:.4f} > {self.regularity_threshold})")
        return is_coherent

    def _fake_ctx(self):
        # Minimal adapter since GovernmentCapsuleEngine executes without full ctx needs
        class FakeTelemetry:
            def emit(self, *args, **kwargs):
                pass

        class FakeLedger:
            def append(self, *args, **kwargs):
                pass

        class FakePerception:
            def write(self, *args, **kwargs):
                pass

        from core.agents.base import AgentContext

        return AgentContext(
            identity={},
            telemetry=FakeTelemetry(),
            ledger=FakeLedger(),
            perception=FakePerception(),
            kernel=None,
            engine=self.engine,
            state={},
        )

    def _run_governed_capsule(self, goal: str, kind: str = "task", trace: Dict = None) -> str:
        """Executes a capsule via the government engine with PASS broker resilience."""
        capsule = Capsule(
            id=f"cap-{abs(hash(goal)) % 1_000_000}",
            kind=kind,
            goal=goal,
            trace=trace or {}
        )
        
        res = self.engine.execute(capsule, ctx=self._fake_ctx())
        
        # If blocked (VRAM, Confidence, or Arbiter), resolve via PASS
        if res.blocked and res.pass_request:
            print(f"[ENGINE] Blocked ({res.error}). Invoking PASS Broker for resilience...")
            res = self.engine.pass_broker.resolve(capsule, res)
            
        if not res.ok:
            raise RuntimeError(res.error or "Capsule execution failed")
            
        return res.output.get("text", "")

    def run_expansion(self):
        """Phase 2: Baseline Expansion (25 Beats) via Reasoning minister"""
        print(f"### STARTING EXPANSION PHASE (Goal: {self.goal})")
        for beat in range(1, self.expansion_count + 1):
            self._throttle()
            print(f"[BEAT {beat}/25] Expanding context...")

            prompt = f"Beat {beat} of 25. Current objective: {self.goal}. Provide a detailed analytical step."
            # Expansion uses reasoning minister (via trace hint) and enforces arbiter
            response = self._run_governed_capsule(prompt, trace={"minister_hint": "Prime Minister", "arbiter": True})

            entry = {
                "beat": beat,
                "type": "expansion",
                "content": response,
                "timestamp": datetime.now().isoformat()
            }
            self.logic_strip.append(entry)
            self._save_log()

    def run_crystallization(self):
        """Phase 2: Forensic Crystallization (5 Beats) with Resonant Bridge"""
        print("### STARTING CRYSTALLIZATION PHASE (Self-Correction Active)")
        for beat in range(1, self.crystallization_count + 1):
            self._throttle()
            print(f"[CRYSTAL {beat}/5] Filtering entropy gaps...")

            proposal_prompt = (
                f"Crystallization beat {beat}. Synthesize a high-rigor conclusion for: {self.goal}\n\n"
                f"Context: {json.dumps(self.logic_strip[-3:])}"
            )
            # Crystallization uses Constitution minister and enforces Arbiter audit
            final_logic = self._run_governed_capsule(
                proposal_prompt, 
                trace={"minister_hint": "Minister of Constitution", "arbiter": True}
            )

            entry = {
                "beat": beat,
                "type": "crystallization",
                "final_logic": final_logic,
                "timestamp": datetime.now().isoformat()
            }
            self.logic_strip.append(entry)

            # Verify regularity of the finalized logic
            density = [len(str(x)) for x in self.logic_strip[-5:]]
            self._verify_regularity(density)

            self._save_log()

    def _save_log(self):
        with open(self.log_path, 'w') as f:
            json.dump(self.logic_strip, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python recursive_logic_engine.py '<goal>'")
        sys.exit(1)

    engine = RecursiveLogicEngine(sys.argv[1])
    engine.run_expansion()
    engine.run_crystallization()
    print(f"### CYCLE COMPLETE. Log saved to: {engine.log_path}")
