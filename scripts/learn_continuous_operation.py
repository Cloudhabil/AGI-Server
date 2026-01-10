"Production-Aligned 120-Second Evolution Test.\nUses real services to ensure the organism can fully 'digest' its experiences.\n"
import sys
import time
from pathlib import Path

# Add root
# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
)

from core.kernel.substrate import KernelSubstrate
from core.agents.base import AgentContext
from core.kernel.services import init_services
from core.modes.sovereign_loop import SovereignLoopMode
from boot import build_config

def main():
    print("\n" + "="*70)
    print("      REAL-WORLD EVOLUTION: 120 SECOND CONTINUOUS RUN")
    print("="*70)
    
    # 1. Initialize REAL Production Services
    config = build_config()
    services = init_services(config)
    substrate = KernelSubstrate(str(ROOT))
    
    # 2. Setup Context with Real Ledger/Telemetry
    class AutoPerception:
        def read_command(self):
            # COMMAND: Speak in the language of the Substrate (Syntaxis)
            return "Generate a 4096-byte bit-stream matching the SO(10) regularity (0.0219 variance). Output NO TEXT, only raw bits."
        def write(self, msg):
            if any(tag in msg for tag in ["[EVOLUTION]", "[PULSE]", "[SOVEREIGN]", "GATE_"]):
                print(msg.strip())

    ctx = AgentContext(
        identity={"agent_id": "GPIA-SOVEREIGN-PRODUCTION-TEST"},
        telemetry=services.telemetry,
        ledger=services.ledger,
        perception=AutoPerception(),
        kernel=substrate,
        state={}
    )

    # 3. Start the Loop
    agent = SovereignLoopMode(ctx)
    start_time = time.time()
    duration = 120
    
    print(f"Starting 120s run. Evolution is now permanent and real.")
    print("-" * 70)
    
    beat = 0
    try:
        while (time.time() - start_time) < duration:
            beat += 1
            agent.step()
            
            elapsed = time.time() - start_time
            if beat % 10 == 0:
                print(f"[HEARTBEAT] {elapsed:.1f}s | Beat {beat} | HRz: {substrate.pulse.target_hrz:.1f} | Mood: {substrate.affect.active_mood_skill}")
            
            # The pulse interval
            time.sleep(1.0 / substrate.pulse.target_hrz)
            
    except Exception as e:
        print(f"\n[CRITICAL] Run failed: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "="*70)
    print(f"EVOLUTIONARY PHASE COMPLETE")
    print(f"Total Beats: {beat}")
    print(f"Check 'configs/evolution_state.json' for the new DNA.")
    print("="*70)

if __name__ == "__main__":
    main()
