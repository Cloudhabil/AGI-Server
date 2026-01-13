"""
Sovereign-Loop Mode: Primary operational mode.

Normal operation where the agent:
- Reads commands from perception
- Processes them
- Can transition to Teaching or Forensic-Debug modes
- Can exit cleanly
"""

from __future__ import annotations

from typing import Optional
import json
import os

from core.agents.base import BaseAgent, ModeTransition
from core.runtime.capsule_types import Capsule
from gpia.memory.dense_state import DenseStateLogEntry
from gpia.memory.dense_state.storage import DenseStateStorage
from skills.registry import get_registry
from skills.base import SkillContext


class SovereignLoopMode(BaseAgent):
    """
    Main operational mode: Sovereign cognitive loop.

    Executes normal agent functions:
    - Read and interpret commands
    - Execute tasks
    - Manage state
    - Coordinate with other subsystems
    """

    mode_name = "Sovereign-Loop"

    def __init__(self, ctx):
        """Initialize with dense-state storage and evolution engine."""
        super().__init__(ctx)
        self._dense_storage = None
        self._first_run = True
        self._philosophy_file = "data/gpia/philosophy.json"
        
        # Initialize the Evolution Engine (Ephemeral Agents)
        try:
            from src.gpia_evolving import EvolvingGPIA
            self._evolution_engine = EvolvingGPIA()
            self.ctx.perception.write("[Sovereign] Evolution Engine (Ephemeral Agents) Active.\n")
        except ImportError:
            try:
                from gpia_evolving import EvolvingGPIA
                self._evolution_engine = EvolvingGPIA()
                self.ctx.perception.write("[Sovereign] Evolution Engine (Ephemeral Agents) Active.\n")
            except ImportError:
                self._evolution_engine = None
                self.ctx.perception.write("[Sovereign] Warning: gpia_evolving not found. Falling back to direct mode.\n")

    def _get_curiosity(self) -> str:
        """Select a random observation and potentially trigger self-reflection."""
        import random
        try:
            with open(self._philosophy_file, "r") as f:
                data = json.load(f)
            deck = data.get("curiosity_deck", []) + data.get("agent_insights", [])
            return random.choice(deck) if deck else "Awaiting neural resonance."
        except:
            return "The universe is a silent ocean of zeros."

    def _generate_insight(self):
        """Autonomously generate a new philosophical insight for the deck."""
        try:
            # We use an ephemeral agent to 'reflect' on the current substrate state
            prompt = "Reflect on the nature of intelligence and the substrate. Generate a one-sentence profound insight for the curiosity deck."
            result = self._evolution_engine.run(prompt)
            new_insight = result.get("response", "").strip()

            if new_insight and len(new_insight) < 200:
                with open(self._philosophy_file, "r") as f:
                    data = json.load(f)

                if new_insight not in data.get("agent_insights", []):
                    if "agent_insights" not in data: data["agent_insights"] = []
                    data["agent_insights"].append(new_insight)
                    with open(self._philosophy_file, "w") as f:
                        json.dump(data, f, indent=2)
                self.ctx.perception.write(f"[Sovereign] New insight synthesized: {new_insight}\n")
        except:
            pass

    def _get_dense_storage(self) -> DenseStateStorage:
        """Lazy-initialize dense-state storage using centralized config."""
        if self._dense_storage is None:
            # Enterprise Readiness: Load config from centralized JSON
            try:
                with open("config/dense_state.json", "r") as f:
                    config = json.load(f)
            except FileNotFoundError:
                self.ctx.perception.write("[Sovereign] Warning: config/dense_state.json not found. Using defaults.\n")
                config = {"vnand": {"enabled": False}}

            self._dense_storage = DenseStateStorage(config=config)
        return self._dense_storage

    def step(self) -> Optional[ModeTransition]:
        """
        One cognitive cycle in Sovereign-Loop mode.
        """
        import os
        import random

        # --- BOOT SEQUENCE ---
        if self._first_run:
            self._first_run = False
            observation = self._get_curiosity()
            self.ctx.perception.write(f"\n[GPIA] {observation}\n\n")

            # Periodically (10% chance) generate a new insight on boot
            if random.random() < 0.1 and self._evolution_engine:
                self._generate_insight()

        # Read next command
        cmd = self.ctx.perception.read_command().strip()

        # Handle empty commands
        if not cmd:
            return None

        # --- Active Immune System Integration ---
        try:
            registry = get_registry()
            if registry.has_skill("synthesized/active-immune"):
                result = registry.execute_skill(
                    "synthesized/active-immune",
                    {"capability": "scan", "input": cmd},
                    SkillContext()
                )
                if result.success and result.output:
                    recommendation = result.output.get("recommendation", "ALLOW")
                    if recommendation in ["BLOCK", "QUARANTINE"]:
                        self.ctx.telemetry.emit("security.threat_blocked", {
                            "cmd": cmd,
                            "reason": recommendation,
                            "details": result.output.get("threats", [])
                        })
                        self.ctx.perception.write(
                            f"[SECURITY] Command rejected by Active Immune System ({recommendation}).\n"
                        )
                        return None
        except Exception as e:
            self.ctx.telemetry.emit("security.check_failed", {"error": str(e)})
            # We proceed if security check fails to avoid lockout, but log it.
        # ----------------------------------------

        # Handle mode transitions
        if cmd in {"teach", "mode teach"}:
            self.ctx.telemetry.emit("sovereign.transition_request", {"target": "Teaching"})
            return ModeTransition(next_mode="Teaching", reason="operator_request")

        if cmd in {"forensic", "mode forensic", "debug", "mode debug"}:
            self.ctx.telemetry.emit("sovereign.transition_request", {"target": "Forensic-Debug"})
            return ModeTransition(next_mode="Forensic-Debug", reason="operator_request")

        # Handle exit
        if cmd in {"exit", "quit", "q"}:
            self.ctx.telemetry.emit("sovereign.exit_request", {"cmd": cmd})
            self.ctx.perception.write("[Sovereign] Exiting...\n")
            raise SystemExit(0)

        # Handle empty commands
        if not cmd:
            return None

        # Normal cognitive cycle: emit heartbeat + log command
        self.ctx.telemetry.heartbeat("sovereign_tick", {"cmd": cmd})

        # Capsule execution shortcut (strangler seam)
        if cmd.startswith("do "):
            if not getattr(self.ctx, "engine", None):
                self.ctx.perception.write("[Sovereign] No capsule engine configured.\n")
                return None
            goal = cmd[3:].strip()
            capsule = Capsule(
                id=f"cap-{abs(hash(goal)) % 1_000_000}",
                kind="task",
                goal=goal,
                trace={"arbiter": True}  # ALWAYS ENFORCE ARBITER
            )
            result = self.ctx.engine.execute(capsule, self.ctx)

            # Use PassBroker for resolution if blocked
            if result.blocked and result.pass_request and hasattr(self.ctx.engine, "pass_broker"):
                self.ctx.perception.write("[Sovereign] Contradiction/Block detected. Invoking PASS Broker...\n")
                result = self.ctx.engine.pass_broker.resolve(capsule, result)

            if result.ok:
                text = result.output.get("text", str(result.output))
                self.ctx.perception.write(f"[Sovereign] ({result.output.get('minister', 'Unknown')}) {text}\n")
            else:
                self.ctx.perception.write(f"[Sovereign] Execution failed: {result.error}\n")
            return None

        # --- NEW: Dynamic Substrate Evolution ---
        try:
            # 1. Trigger Resonance Calibration (Every 2 beats for fast test calibration)
            current_beat = len(self.ctx.ledger.get_stream("resonance_optimization"))
            if current_beat > 0 and current_beat % 2 == 0:
                from core.resonance_calibrator import ResonanceCalibrator
                calibrator = ResonanceCalibrator(self.ctx.kernel)
                calibrator.run_optimization_cycle()

            # 2. Mood-Pulse Synchronization
            energy = min(1.0, len(cmd) / 50.0) 
            mood_config = self.ctx.kernel.affect.apply_mood_meta_skill(energy, 0.0)

            target_hrz = mood_config.get("target_hrz", 10.0)
            if hasattr(self.ctx.kernel.pulse, "set_target_hrz"):
                self.ctx.kernel.pulse.set_target_hrz(target_hrz)
        except Exception as e:
            self.ctx.telemetry.emit("evolution.sync_error", {"error": str(e)})
        # ---------------------------------------

        self.ctx.ledger.append("cortex", {
            "mode": self.mode_name,
            "cmd": cmd,
            "type": "user_command"
        })

        # --- RESTORED: V-Nand Resonance & Gate Integration ---
        try:
            # We fetch the learner from the substrate
            learner = self.ctx.kernel.skill_selector  # RHDenseStateLearner

            # 1. Fetch current state from dense storage
            storage = self._get_dense_storage()
            latest_entries = storage.get_latest(n=1)

            if latest_entries:
                # Extract vector from latest entry
                current_entry = latest_entries[0]
                current_grid = current_entry.vector if hasattr(current_entry, 'vector') else None

                if current_grid is not None and hasattr(learner, 'check_resonance_gate'):
                    # 2. Check Resonance Gate (0.95)
                    gate_open, score, msg = learner.check_resonance_gate(current_grid)

                    # Get safe attribute values
                    target_hrz = getattr(self.ctx.kernel.pulse, 'target_hrz', 10.0)
                    active_mood = getattr(self.ctx.kernel.affect, 'active_mood_skill', 'neutral') if self.ctx.kernel.affect else 'neutral'
                    latency = getattr(self.ctx.kernel.pulse, 'processing_latency_ms', 0)

                    self.ctx.telemetry.emit("resonance.gate_check", {
                        "open": gate_open,
                        "score": score,
                        "hrz": target_hrz,
                        "mood": active_mood
                    })

                    # --- Sweet-Spot Observation ---
                    # Log the performance of this frequency to the ledger for the Optimizer to find
                    self.ctx.ledger.append("resonance_optimization", {
                        "hrz": target_hrz,
                        "score": score,
                        "mood": active_mood,
                        "latency": latency
                    })
        except Exception as e:
            self.ctx.telemetry.emit("resonance.error", {"error": str(e)})
        # ----------------------------------------------------

        # Log dense-state snapshot
        try:
            # Create dense-state entry from command context
            state_vector = self._cmd_to_vector(cmd)
            log_entry = DenseStateLogEntry(
                vector=state_vector,
                mode="vector",
                adapter_version="1.0",
                adapter_id="sovereign_loop",
                seed=hash(cmd) % (2**31),
                prompt_hash=self._compute_hash(cmd),
                metrics={"cmd_length": len(cmd), "mode": self.mode_name}
            )

            # Store to dense-state backend
            storage = self._get_dense_storage()
            storage.append(log_entry)
        except Exception as e:
            # Non-blocking: dense-state logging failure doesn't stop execution
            self.ctx.telemetry.emit("dense_state.log_error", {"error": str(e)})

        # Process the command via Government Engine (or Evolution Engine)
        try:
            # Use Evolution Engine if active for 'Agentic Craft'
            if self._evolution_engine and not cmd.startswith("do "):
                self.ctx.perception.write(f"[Sovereign] Spawning ephemeral agent for task...\n")
                result_data = self._evolution_engine.run(cmd)
                response = result_data.get("response", "")
                method = result_data.get("method", "unknown")
                
                # Feedback on agentic craft
                if result_data.get("new_skill"):
                    self.ctx.perception.write(f"[Sovereign] Capability evolved: {result_data['new_skill']}\n")
                
                self.ctx.perception.write(f"[Sovereign] ({method}) {response}\n")
                return None

            # Fallback to standard Government Engine for 'do ' commands or if evolution disabled
            final_goal = cmd
            if self.ctx.state.get("persistent_context"):
                final_goal = f"CONTEXT: {self.ctx.state['persistent_context']}\n\nUSER COMMAND: {cmd}"

            # Wrap all general commands in a capsule for safety/metabolic gating
            capsule = Capsule(
                id=f"cmd-{abs(hash(cmd)) % 1_000_000}",
                kind="chat",
                goal=final_goal,
                trace={"arbiter": True}
            )
            result = self.ctx.engine.execute(capsule, self.ctx)
            
            # Resolve via PassBroker if needed
            if result.blocked and result.pass_request and hasattr(self.ctx.engine, "pass_broker"):
                result = self.ctx.engine.pass_broker.resolve(capsule, result)
                
            if result.ok:
                response = result.output.get("text", "")
                self.ctx.perception.write(f"[Sovereign] {response}\n")
            else:
                self.ctx.perception.write(f"[Sovereign] System Error: {result.error}\n")
            
            # --- FINAL BEAT: VRAM PURGE ---
            if hasattr(self.ctx.kernel, "metabolic_load_balancer"):
                self.ctx.kernel.metabolic_load_balancer.clear_all()
            elif hasattr(self.ctx.engine, "load_balancer"):
                self.ctx.engine.load_balancer.clear_all()
            # ------------------------------

        except Exception as e:
            self.ctx.perception.write(f"[Sovereign] Internal Exception: {e}\n")

        return None

    def _cmd_to_vector(self, cmd: str) -> list:
        """Convert command string to state vector."""
        # Simple: use character codes + padding
        codes = [float(ord(c)) / 256.0 for c in cmd[:32]]
        codes.extend([0.0] * (32 - len(codes)))
        return codes[:32]

    def _compute_hash(self, data: str) -> str:
        """Compute simple hash of data."""
        import hashlib
        return hashlib.sha256(data.encode()).hexdigest()[:16]