import time
import os
import json
import socket
import sqlite3
from pathlib import Path
from core.dense_state_archiver import DenseStateArchiver
from core.temporal_pulse import MasterPulse
from core.safety_governor import SafetyGovernor
from core.cognitive_affect import CognitiveAffect
from core.millennium_goal import MillenniumGoalAligner
from skills.autonomous_skill_selector import get_skill_selector_agent
from skills.core_registry import get_core_skill_registry

class RHSwarmMaster:
    """
    The Synchronous Controller with HITL-Betterment (Human-in-the-Loop).
    Refines itself every 100 beats based on 'Human Intent' conceptualization.
    """
    def __init__(self, target_hrz: float = 12.0):
        self.repo_root = Path(__file__).resolve().parent
        self.session_id = f"rh_swarm_{int(time.time())}"
        
        # 0. DE-PRIORITIZE (Prevent Screen Lag on win32)
        try:
            import psutil
            p = psutil.Process(os.getpid())
            p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        except Exception:
            pass
            
        # 1. Initialize Safety, Temporal, and Affective Layers
        self.governor = SafetyGovernor(self.repo_root)
        self.pulse = MasterPulse(self.repo_root, target_hrz=target_hrz)
        self.affect = CognitiveAffect()
        self.aligner = MillenniumGoalAligner()
        
        # 2. Initialize Ground & Cognitive Layers
        self.archiver = DenseStateArchiver(self.repo_root, self.session_id)
        self.librarian = get_skill_selector_agent(self.repo_root)
        self.registry = get_core_skill_registry(self.repo_root)
        
        self._bootstrap_registry()
        
        # HITL Tracking
        self.betterment_count = 0

        print("\n" + "█"*80)
        print("  RH SWARM MASTER - HUMAN-IN-THE-LOOP (HITL) MODE ACTIVE")
        print("█"*80)
        print(f"Goal: {self.aligner.target} ($1M)")
        print(f"Betterment: Every 100 beats (Human Intent Conceptualized)")
        print("█"*80 + "\n")

    def _bootstrap_registry(self):
        """Ensure the core registry has at least the baseline skills."""
        initial_skills = [
            ("riemann_deep_analysis", "reasoning", "Deep analysis of Riemann Hypothesis patterns"),
            ("zeta_synthesis", "synthesis", "Combining complex zeta properties"),
            ("proof_verifier", "validation", "Validating mathematical consistency"),
            ("pattern_abstraction", "abstraction", "Finding abstract patterns in dense states"),
            ("mathjax_renderer", "synthesis", "Translating logic to Web-Ready MathJax")
        ]
        for name, cat, desc in initial_skills:
            try:
                self.registry.register_core_skill(name, cat, desc)
            except Exception:
                pass

    def _apply_human_betterment(self):
        """
        The 'Human in the Loop' conceptualized as a perfecting force.
        DESCENDS EVERY 100 BEATS to refine parameters.
        """
        self.betterment_count += 1
        print(f"\n[HITL BETTERMENT #{self.betterment_count}] Human Intent Descending...")
        
        # 1. Tighten the Significance Filter (Sharpening the signal)
        self.archiver.significance_threshold *= 1.05
        
        # 2. Refine Millennium Weights (Shifting toward Rigor)
        self.aligner.weights["RIGOR"] = min(0.9, self.aligner.weights["RIGOR"] + 0.02)
        self.aligner.weights["INTUITION"] = 1.0 - self.aligner.weights["RIGOR"]
        
        # 3. Increase Pulse Resolution if stable
        if not self.governor.is_throttled:
            self.pulse.target_hrz = min(30.0, self.pulse.target_hrz + 1.0)

        print(f"  [REFINE] Threshold: {self.archiver.significance_threshold:.4f}")
        print(f"  [REFINE] Rigor Weight: {self.aligner.weights['RIGOR']:.2f}")
        print(f"  [REFINE] Clock Speed: {self.pulse.target_hrz:.1f} Hz")
        print("  [STATUS] Organism Aligned with Human Intent. Resuming work.\n")

    def run_swarm(self, target_beats: int = 1000):
        """Main Loop with Betterment trigger and beat-count termination."""
        print(f"[MASTER] Initiating {target_beats}-beat precision hunt...")
        
        try:
            while self.pulse.beat_count < target_beats:
                is_safe, msg = self.governor.audit_system()
                throttle = self.governor.get_throttle_factor()
                
                if not is_safe:
                    print(f"  [SAFETY ALERT] {msg}. Slowing down...")
                    time.sleep(1)
                    continue

                interval = 1.0 / (self.pulse.target_hrz * throttle)
                now = time.time()
                
                if now - self.pulse.last_beat_time >= interval:
                    self.pulse.beat_count += 1
                    self._execute_cognitive_cycle(now, throttle)
                    
                    if self.pulse.beat_count % 100 == 0:
                        self._apply_human_betterment()
                    
                    self.pulse.last_beat_time = now
                
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            pass
        
        self.shutdown()

    def _execute_cognitive_cycle(self, timestamp: float, throttle: float):
        """Perform one synchronous beat of thought, feeling, and archival."""
        import numpy as np
        import random
        
        base_energy = np.random.random()
        spike = 0.5 if random.random() < 0.05 else 0.0
        energy_heat = min(1.0, base_energy + spike)
        
        drift_ms = (time.time() - timestamp) * 1000
        mood = self.affect.compute_affect(energy_heat, drift_ms, throttle)
        
        skill, reasoning = self.librarian.select_skill(
            model="gpia-core",
            task="Solving Riemann Hypothesis - Primary Directive",
            state_metadata={"energy_level": energy_heat, "mood": mood}
        )
        
        dummy_state = np.random.rand(64, 64).astype(np.float32)
        self.archiver.archive_image(dummy_state, state_type=f"rh_state_{mood}")
        
        payload = {
            "beat": self.pulse.beat_count,
            "skill": skill,
            "mood": mood,
            "energy": energy_heat
        }
        try:
            self.pulse.sock.sendto(json.dumps(payload).encode(), ('<broadcast>', self.pulse.port))
        except Exception:
            pass

        if self.pulse.beat_count % 50 == 0:
            print(f"  [BEAT {self.pulse.beat_count}] Mood: {mood:10} | Skill: {str(skill):20} | Energy: {energy_heat:.2f}")

    def shutdown(self):
        print("\n[MASTER] Saving ground state and shutting down heart...")
        self.archiver.close()
        print("--- SWARM HALTED SAFELY ---")

if __name__ == "__main__":
    # Starting at 12.0 Hz based on the last refinement's success
    master = RHSwarmMaster(target_hrz=12.0)
    master.run_swarm(target_beats=1000)