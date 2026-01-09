
import json
import time
from pathlib import Path
from rh_discovery_orchestrator import RHDiscoveryOrchestrator

def run_adaptive_rh_session():
    session_name = "rh_adaptive_solve_session"
    # Logic: 10 mins initially, then 5, 5, 5 (total 3 extensions)
    durations = [10, 5, 5, 5]
    
    print(f"[HYDRA SYSTEM] Initializing Adaptive RH Solver...")
    print(f"[HYDRA SYSTEM] Strategy: {durations[0]}m + " + " + ".join([f"{d}m" for d in durations[1:]]))
    
    for i, duration in enumerate(durations):
        leg_name = "Initial" if i == 0 else f"Extension {i}"
        print(f"\n{'#'*60}")
        print(f"[HYDRA SYSTEM] STARTING {leg_name.upper()} RUN ({duration} minutes)")
        print(f"{'{#'*60}\n")
        
        orchestrator = RHDiscoveryOrchestrator(
            session_name=session_name, 
            duration_minutes=duration
        )
        
        # Run the research session
        orchestrator.run_orchestration_session()
        
        # Post-run check
        report_path = Path("agents") / session_name / "final_research_report.json"
        
        if report_path.exists():
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            stats = report.get("statistics", {})
            breakthroughs = stats.get("breakthrough_indicators", 0)
            high_promise = stats.get("high_promise_proposals", 0)
            
            print(f"\n[HYDRA SYSTEM] Leg Summary:")
            print(f"  > Breakthroughs: {breakthroughs}")
            print(f"  > High Promise: {high_promise}")
            
            if breakthroughs > 0 or high_promise >= 2:
                print(f"\n[HYDRA SYSTEM] ⚡ SOLUTION/BREAKTHROUGH DETECTED IN {leg_name.upper()} ⚡")
                print(f"[HYDRA SYSTEM] Stopping adaptive loop as goal conditions are met.")
                return
            
            if i < len(durations) - 1:
                print(f"\n[HYDRA SYSTEM] No definitive solution found in {leg_name}. Triggering extension...")
            else:
                print(f"\n[HYDRA SYSTEM] Final extension complete. No automated breakthrough reached.")
        else:
            print(f"[HYDRA SYSTEM] Error: Could not find report at {report_path}")

if __name__ == "__main__":
    run_adaptive_rh_session()
