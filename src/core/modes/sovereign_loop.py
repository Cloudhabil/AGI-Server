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
        """Initialize with dense-state storage."""
        super().__init__(ctx)
        self._dense_storage = None

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

        Reads a command from perception and processes it.
        Can transition to Teaching, Forensic-Debug, or exit.

        Returns:
            ModeTransition to change modes, or None to continue
        """
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

        # Process the command via Government Engine (Gated & Audited)
        try:
            # Wrap all general commands in a capsule for safety/metabolic gating
            capsule = Capsule(
                id=f"cmd-{abs(hash(cmd)) % 1_000_000}",
                kind="chat",
                goal=cmd,
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
