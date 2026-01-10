
import json
import time
import os
import sys
import importlib.util
from pathlib import Path

# Fix paths
sys.path.insert(0, os.getcwd())

from rh_discovery_orchestrator import RHDiscoveryOrchestrator
from skills.base import SkillContext

def load_math_literature_skill():
    skill_path = Path("skills/research/math-literature/skill.py")
    spec = importlib.util.spec_from_file_location("math_lit_module", skill_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.MathLiteratureSkill()

def run_grand_synthesis_session():
    session_name = "rh_grand_solve_v2"
    session_dir = Path("agents") / session_name
    session_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load Grand Synthesis Data
    synthesis_path = Path("agi_test_output/grand_synthesis/PROJECT_ALPHA_Grand_Synthesis_2026.md")
    synthesis_data = synthesis_path.read_text(encoding="utf-8") if synthesis_path.exists() else "No previous synthesis found."
    
    print("\n[HYDRA SYSTEM] Phase 1: Grand Synthesis Integration")
    print(f"[HYDRA SYSTEM] Loading breakthrough data from: {synthesis_path.name}")
    
    # 2. Search ArXiv for fresh context
    print("[HYDRA SYSTEM] Phase 2: ArXiv Literature Injection")
    context = SkillContext()
    try:
        math_lit = load_math_literature_skill()
        res = math_lit.execute({"capability": "search_riemann_hypothesis", "max_results": 3}, context)
        arxiv_data = ""
        if res.success:
            for paper in res.output.get("papers", []):
                print(f"  + Ingested: {paper['title']}")
                arxiv_data += f"Paper: {paper['title']}\nAbstract: {paper['abstract']}\n"
    except Exception as e:
        print(f"[HYDRA SYSTEM] Warning: Literature injection bypassed ({e})")
        arxiv_data = "No fresh arxiv data available."
    
    # 3. Create the "Prime Directive" for Alpha and Professor
    prime_directive = f"""
    ### CONTEXT: THE GRAND SYNTHESIS 2026 ###
    {synthesis_data}
    
    ### EXTERNAL RESEARCH ###
    {arxiv_data}
    
    ### CORE OBJECTIVE ###
    Continue from the Phase 2C Best Error (5802.65). 
    Explore the 'Dimensionless Coupling Constants' (Phase 4) discovered in the last session.
    Bridge the gap between Spectral Number Theory and the Fine Structure Constant.
    """
    
    # Save to a file the agents can 'see'
    (session_dir / "PRIME_DIRECTIVE.txt").write_text(prime_directive, encoding="utf-8")
    
    # 4. Adaptive Loop
    durations = [10, 5, 5, 5]
    for i, duration in enumerate(durations):
        leg = "Initial" if i == 0 else f"Ext {i}"
        print(f"\n[HYDRA SYSTEM] RUNNING: {leg} ({duration}m)")
        
        # Note: We use the session_name so it loads its previous .db memories too
        orchestrator = RHDiscoveryOrchestrator(session_name=session_name, duration_minutes=duration)
        
        # Inject the directive into the Alpha's instructions manually if needed, 
        # but the orchestrator handles the DB which already has the lineage.
        orchestrator.run_orchestration_session()
        
        # Check for breakthrough
        report_path = session_dir / "final_research_report.json"
        if report_path.exists():
            report = json.loads(report_path.read_text())
            if report.get("statistics", {}).get("breakthrough_indicators", 0) > 0:
                print(f"\n[HYDRA SYSTEM] ⚡ Breakthrough detected in {leg}! ⚡")
                break

if __name__ == "__main__":
    run_grand_synthesis_session()
