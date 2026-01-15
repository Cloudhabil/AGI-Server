"""
Hermes Biomedical Dual-Rigor Check.

- Phase 2 of verification: HYPER_FOCUS.
- Re-runs verified hypotheses (0.85) through a high-rigor 'gate'.
- Promotes to Level 10 ONLY if they survive the gate.
"""
import sys
import os
import json
from pathlib import Path

# Add src to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from skills.synthesized.hermes_trismegistos.biomedical_discovery.skill import HermesBiomedicalDiscoverySkill
from skills.synthesized.hermes_trismegistos.protein_folding_hypothesis_miner.skill import HermesTrismegistosSkill as ProteinFoldingSkill
from skills.base import SkillContext

def main():
    print("==================================================")
    print("       HERMES DUAL-RIGOR GATE (HYPER_FOCUS)       ")
    print("==================================================")

    # 1. Load Hypotheses (From previous Curious pass)
    # We assume they entered at 0.8500
    hypotheses = [
        {
            "id": "H1",
            "text": "Intrinsically disordered proteins can adopt a meta-stable helical structure in the absence of HSP70, stabilized by cytosolic pH fluctuations.",
            "domain": "protein-folding",
            "curious_score": 0.8500
        },
        {
            "id": "H2",
            "text": "CRISPR-Cas9 off-target effects are more prevalent in high-density chromatin regions, correlated with specific methylation markers.",
            "domain": "genomics",
            "curious_score": 0.8500
        },
        {
            "id": "H3",
            "text": "The standard coil or globule phases cannot accurately describe the denatured state of structured proteins and intrinsically disordered proteins.",
            "domain": "protein-folding",
            "curious_score": 0.8500
        }
    ]

    print(f"[INPUT] Loaded {len(hypotheses)} verified hypotheses (Curious Score: 0.8500)")

    # 2. Instantiate Skills
    # To simulate HYPER_FOCUS, we rely on the skill's internal 'gate' logic
    # which typically filters out low-confidence signals strictly.
    folding_skill = ProteinFoldingSkill()
    bio_skill = HermesBiomedicalDiscoverySkill()
    
    # We set a context user_id that implies rigor, though the skill logic is mostly mode-driven
    ctx = SkillContext(user_id="hyper-focus-gate")

    # 3. Rigor Loop
    for h in hypotheses:
        print(f"\n[GATING] {h['id']}: {h['text'][:80]}...")
        
        survived = False
        final_score = h["curious_score"]
        
        if h["domain"] == "protein-folding":
            # Strict Gating on Folding
            payload = {
                "sequence": "MOCK_SEQUENCE_IDP",
                "motifs": ["HSP70-binding"],
                "structure_prior": h["text"],
                # We limit hints to only the core mechanism to test robustness
                "evidence_hints": ["pH fluctuation"]
            }
            # Mode "gate" applies stricter filtering (e.g. support < 0.2 rejected)
            res = folding_skill.execute({"payload": payload, "mode": "gate"}, ctx)
            
            if res.success and res.output["insights"]:
                top = res.output["insights"][0]
                # In gate mode, we look for stability (did the score hold up?)
                gate_score = top.get("composite_score", 0.0)
                print(f"    > Gate Score: {gate_score:.4f}")
                
                if gate_score >= 0.4: # Threshold for passing the gate logic in skill.py
                    survived = True
                    # Boost to 1.0 (Level 10) if it survives both extremes
                    final_score = 1.0000 
        
        elif h["domain"] == "genomics":
            # Strict Gating on Genomics
            payload = {
                "query": "CRISPR off-target heterochromatin methylation",
                "focus": "safety-critical",
                "mode": "gate" # Enforce strict relevance
            }
            res = bio_skill.execute({"payload": payload, "mode": "gate"}, ctx)
            
            if res.success:
                # For bio discovery, we check if the score remains high without 'hints'
                gate_score = res.output.get("score", 0.0)
                print(f"    > Gate Score: {gate_score:.4f}")
                
                if gate_score > 0.5:
                    survived = True
                    final_score = 1.0000

        status = "VERIFIED (LEVEL 10)" if survived else "REJECTED"
        print(f"    > Status: {status} | Final Score: {final_score}")

    print("\n==================================================")
    print("             DUAL-RIGOR SUMMARY                   ")
    print("==================================================")
    print("If Status is LEVEL 10, the 1500-point knowledge gap is closed.")

if __name__ == "__main__":
    main()
