
import time
import json
import socket
from pathlib import Path
from core.safety_governor import SafetyGovernor

class MasterPulse:
    """
    The Master Oscillator for the AGI Organism.
    Generates the synchronous HRz heartbeat.
    """
    def __init__(self, repo_root: Path, target_hrz: float = 10.0):
        self.repo_root = repo_root
        self.target_hrz = target_hrz
        self.max_hrz = 22.0 # The Genesis Hard Ceiling
        self.governor = SafetyGovernor(repo_root)
        
        # Latency-Aware Recalibration
        self.processing_latency_ms = 0.0
        self.dynamic_ceiling = 22.0
        
        # Internal Clock State
        self.beat_count = 0
        self.start_time = time.time()
        self.last_beat_time = time.time()
        
        # Communication (UDP Broadcast for zero-latency)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.port = 50005 # Synchronous Pulse Port

    def set_target_hrz(self, hrz: float):
        """Update the target heartbeat frequency."""
        self.target_hrz = max(1.0, min(self.max_hrz, hrz))
        print(f"  [PULSE] Heartbeat shifted to {self.target_hrz:.1f}Hz")

    def recalibrate_ceiling(self, measured_latency_ms: float):
        """
        Adjust the Max HRz based on actual processing time of the 8^4 state.
        Ensures the 'Thoughts' don't outrun the 'Nervous System'.
        """
        self.processing_latency_ms = measured_latency_ms
        # Safety buffer: 20% headroom
        safe_interval_ms = measured_latency_ms * 1.2
        if safe_interval_ms > 0:
            potential_hrz = 1000.0 / safe_interval_ms
            self.dynamic_ceiling = min(self.max_hrz, potential_hrz)
            
        if measured_latency_ms > 40: # Approaching the 22Hz limit (45ms)
            print(f"  [RECALIBRATION] High Density Detected. Throttling Ceiling to {self.dynamic_ceiling:.1f}Hz")

    def emit_pulse(self, current_latency_ms: float = 0.0):
        """Broadcasts the beat and manages alignment."""
        if current_latency_ms > 0:
            self.recalibrate_ceiling(current_latency_ms)

        while True:
            # 1. SAFETY CHECK (The Governor)
            is_safe, msg = self.governor.audit_system()
            throttle = self.governor.get_throttle_factor()
            
            if not is_safe:
                print(f"  [PULSE] Emergency Slowdown: {msg}")
                time.sleep(2) # Cooldown pause
                continue
                
            # 2. CALCULATE DYNAMIC FREQUENCY
            # Use the lower of Target or Dynamic Ceiling (based on 8^4 density)
            actual_target = min(self.target_hrz, self.dynamic_ceiling)
            actual_hrz = actual_target * throttle
            interval = 1.0 / actual_hrz
            
            # 3. THE BEAT
            now = time.time()
            if now - self.last_beat_time >= interval:
                self.beat_count += 1
                payload = {
                    "beat": self.beat_count,
                    "timestamp": now,
                    "hrz": actual_hrz,
                    "ceiling": self.dynamic_ceiling,
                    "throttle": throttle,
                    "latency": self.processing_latency_ms
                }
                
                # Broadcast to the Swarm
                self.sock.sendto(json.dumps(payload).encode(), ('<broadcast>', self.port))
                
                # Feedback loop (Feeling Time)
                drift = (now - self.last_beat_time) - interval
                if drift > 0.05: # If lagging by more than 50ms
                    print(f"  [PULSE] Jitter Detected! Drift: {drift*1000:.1f}ms | Current HRz: {actual_hrz:.1f}")
                
                self.last_beat_time = now
                
                if self.beat_count % 100 == 0:
                    print(f"[PULSE] Beat {self.beat_count} | HRz: {actual_hrz:.1f}/{self.dynamic_ceiling:.1f} | Temp Safe")

            # Yield to OS
            time.sleep(0.001)

if __name__ == "__main__":
    pulse = MasterPulse(Path("."), target_hrz=10.0) # Start at 10Hz
    print("--- GENESIS PULSE INITIALIZED ---")
    print("Broadcasting to the 2TB Swarm...")
    try:
        pulse.emit_pulse()
    except KeyboardInterrupt:
        print("\n[PULSE] Heartbeat stopped safely.")
