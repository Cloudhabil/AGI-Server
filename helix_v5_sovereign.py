import os
import json
import logging
import httpx
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [HELIX] - %(message)s')
logger = logging.getLogger("HelixEngine")

OLLAMA_URL = "http://localhost:11434"
MODEL_ANALYZE = "gpia-deepseek-r1:latest"
MODEL_MANIFEST = "gpia-master:latest"

SETS = [
    {
        "name": "IDENTITY",
        "artifact": "arxiv_submission/genesis_sovereign_manifesto.tex",
        "focus": "Temporal Formalism, Heartbeat (5-22Hz), Golden Ratio Gate."
    },
    {
        "name": "MORTALITY",
        "artifact": "core/safety_governor.py",
        "focus": "78C Thermal Law, 85% VRAM Limit, Physical Grounding."
    },
    {
        "name": "TRUTH",
        "artifact": "research/Riemann_Hypothesis/RIEMANN_PROOF_FINAL_MANUSCRIPT.tex",
        "focus": "Berry-Keating Hamiltonian, Variational Principle, Sub-Poissonian Spacing."
    }
]

def query_ollama(model: str, prompt: str, num_predict: int = 2048):
    try:
        response = httpx.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.6, "num_predict": num_predict, "num_ctx": 8192},
            },
            timeout=600.0
        )
        return response.json().get("response", "")
    except Exception as e:
        return f"ERROR: {str(e)}"

def run_set(set_data: dict):
    logger.info(f"SET: {set_data['name']}")
    artifact_path = Path(set_data['artifact'])
    if not artifact_path.exists():
        return f"MISSING ARTIFACT: {set_data['artifact']}"
    
    content = artifact_path.read_text(encoding='utf-8')[:8000]
    insights = []

    # Phase 1: 25 Analysis Beats
    for i in range(1, 26):
        logger.info(f"  Beat {i}/25 (Analyze)")
        prompt = f"<SYSTEM>Phase: DIVERGENCE (Cycle {i}/25). Target: {set_data['name']}. Focus: {set_data['focus']}.</SYSTEM>\nArtifact:\n{content}\n\nExisting Insights:\n{chr(10).join(insights[-3:])}\n\nTask: Generate one unique technical/philosophical insight."
        insight = query_ollama(MODEL_ANALYZE, prompt, num_predict=512)
        insights.append(insight)

    # Phase 2: 5 Manifestation Beats
    draft = ""
    for i in range(26, 31):
        logger.info(f"  Beat {i}/30 (Manifest)")
        if i == 26:
            prompt = f"<SYSTEM>Phase: CONVERGENCE (Cycle 26/30). Synthesis of 25 insights.</SYSTEM>\nInsights:\n{json.dumps(insights)}\n\nTask: Write the definitive Chapter for {set_data['name']}."
        else:
            prompt = f"<SYSTEM>Phase: CONVERGENCE (Cycle {i}/30). Refinement Step.</SYSTEM>\nDraft:\n{draft}\n\nTask: Enhance technical density and sovereign tone."
        
        draft = query_ollama(MODEL_MANIFEST, prompt)
    
    return draft

def main():
    codex_path = Path("THE_GENESIS_CODEX_HELIX_V5.md")
    full_text = ["# THE_GENESIS_CODEX_HELIX_V5\n**Protocol:** 3x(25+5) Full Sovereign Refinement\n\n"]
    
    for s in SETS:
        chapter_content = run_set(s)
        full_text.append(f"## {s['name']}\n")
        full_text.append(chapter_content)
        full_text.append("\n---\n")
    
    codex_path.write_text("\n".join(full_text), encoding='utf-8')
    print(f"COMPLETE: {codex_path}")

if __name__ == "__main__":
    main()
