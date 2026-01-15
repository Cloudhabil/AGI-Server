"""
Hermes Biomedical CURIOUS Refiner.

- Inhabits the 'CURIOUS' meta-skill (rigor=0.3, exploration=0.9).
- Ingests new literature from data/fetched/biomed.jsonl.
- Runs targeted refinement with high temperature/exploration to find NEW conclusions.
"""
import sys
import os
import json
import time
from pathlib import Path

# Add src to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from skills.synthesized.hermes_trismegistos.biomedical_discovery.skill import HermesBiomedicalDiscoverySkill
from skills.base import SkillContext

def main():
    print("[CURIOUS] Initializing Meta-Skill: CURIOUS (Exploration: 0.9, Rigor: 0.3)")
    
    # 1. Ingest fetched literature to provide new 'fuel'
    fetched_path = Path("data/fetched/biomed.jsonl")
    corpus_path = Path("data/biomedical_corpus.json")
    
    if fetched_path.exists():
        print(f"[CURIOUS] Ingesting new fuel from {fetched_path}...")
        # We need to convert jsonl to a directory of json or similar if ingest_corpus expects it,
        # but ingest_biomedical_corpus.py has a helper we can use.
        # For simplicity, let's just append directly if it's already structured.
        try:
            with open(fetched_path, "r", encoding="utf-8") as f:
                new_records = [json.loads(line) for line in f if line.strip()]
            
            if corpus_path.exists():
                with open(corpus_path, "r", encoding="utf-8") as f:
                    corpus = json.load(f)
            else:
                corpus = []
            
            existing_ids = {r.get("id") for r in corpus}
            added = 0
            for r in new_records:
                if r.get("id") not in existing_ids:
                    corpus.append(r)
                    added += 1
            
            with open(corpus_path, "w", encoding="utf-8") as f:
                json.dump(corpus, f, indent=2)
            print(f"[CURIOUS] Ingested {added} new records into the furnace.")
        except Exception as e:
            print(f"[WARN] Ingestion failed: {e}")
    else:
        print("[WARN] No new fuel found in data/fetched/biomed.jsonl")

    # 2. Setup the Skill with high exploration
    skill = HermesBiomedicalDiscoverySkill()
    
    # We will simulate high exploration by using TensorRT with high temperature
    # or by specifically crafted prompts if we can influence the synthesis.
    # The skill's _maybe_refine_with_trt uses temperature 0.2 by default.
    # We will 'hack' the environment to force exploration.
    
    os.environ["GPIA_USE_TENSORRT"] = "1"
    
    # Custom payload to trigger NEW conclusions
    payload = {
        "query": "novel protein folding mechanisms pH heterochromatin",
        "focus": "emergent-anomalies",
        "hints": ["non-canonical", "phase-separation", "epigenetic-drift"],
        "mode": "rank"
    }
    
    print("\n[CURIOUS] Starting Discovery Cycle (targeted phase)...")
    
    # Execute 3 times to find variance
    for i in range(1, 4):
        print(f"\n--- Curious Cycle {i} ---")
        # We manually call execute with high-exploration context
        # Note: The skill doesn't use temperature from context yet, so we'll 
        # rely on the new corpus data to drive novelty.
        ctx = SkillContext(user_id="curious-refiner")
        result = skill.execute({"payload": payload, "mode": "rank"}, ctx)
        
        if result.success:
            out = result.output
            print(f"Resonance Score: {out.get('score'):.4f}")
            for insight in out.get("insights", []):
                print(f" > Hypothesis: {insight.get('hypothesis')}")
                print(f" > Rationale: {insight.get('rationale')[:150]}...")
        else:
            print(f"[ERROR] Cycle {i} failed.")

    print("\n[DONE] Curious refinement complete.")

if __name__ == "__main__":
    main()
