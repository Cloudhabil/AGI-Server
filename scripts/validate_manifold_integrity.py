import json
import os
import sys
import numpy as np
from pathlib import Path

# Setup paths
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from core.npu_utils import get_substrate_embedding, has_npu

def load_manifold():
    """Extracts the JSON vector data from the HTML manifold."""
    html_path = ROOT / "substrate_manifold.html"
    if not html_path.exists():
        raise FileNotFoundError("substrate_manifold.html not found")
        
    content = html_path.read_text(encoding="utf-8")
    
    # Extract JSON between <data> tags
    start_marker = '<data id="singularities" style="display:none;">'
    end_marker = '</data>'
    
    s_idx = content.find(start_marker)
    e_idx = content.find(end_marker, s_idx)
    
    if s_idx == -1 or e_idx == -1:
        raise ValueError("Could not find <data> block in HTML")
        
    json_str = content[s_idx + len(start_marker):e_idx].strip()
    return json.loads(json_str)

def collapse_manifold(intent_vector, singularities):
    """
    Performs the Riemannian metric collapse (Cosine Similarity).
    Returns (best_id, confidence).
    """
    intent = np.array(intent_vector)
    best_score = -1.0
    best_id = None
    
    # Normalize intent once
    norm_intent = np.linalg.norm(intent)
    
    for item in singularities:
        vec = item.get("vector")
        if not vec: 
            continue
            
        vec = np.array(vec)
        # Cosine Similarity: (A . B) / (||A|| * ||B||)
        dot_product = np.dot(intent, vec)
        norm_vec = np.linalg.norm(vec)
        
        score = dot_product / (norm_intent * norm_vec + 1e-9)
        
        if score > best_score:
            best_score = score
            best_id = item["id"]
            
    return best_id, best_score

def main():
    print("=== Substrate Manifold Integrity Check ===\n")
    
    # 1. Load Topology
    print("1. Loading 841-Singularity Topology...", end=" ")
    try:
        singularities = load_manifold()
        print(f"OK ({len(singularities)} nodes loaded)")
    except Exception as e:
        print(f"FAILED: {e}")
        return

    # 2. Define Test Intents (The "User" Simulation)
    test_cases = [
        {
            "intent": "I need to fix broken embedding dimensions in the vector store.",
            "expected_partial": "embedding-repair",
            "desc": "Maintenance Skill"
        },
        {
            "intent": "Show me the slides about the PRISM surveillance program from 2013.",
            "expected_partial": "snowden_prism",
            "desc": "Specific Knowledge Retrieval"
        },
        {
            "intent": "Run a canary test for the TTS voice pipeline.",
            "expected_partial": "tts_canary_runner",
            "desc": "Automation Tool"
        },
        {
            "intent": "Calculate the derived algebraic geometry for gap 6.",
            "expected_partial": "gap6-derived-ag",
            "desc": "Synthesized Math Logic"
        }
    ]

    # 3. NPU Activation
    print("2. Activating NPU for Intent Vectorization...")
    if not has_npu():
        print("   [WARN] NPU not found, falling back to CPU (slower).")
    else:
        os.environ["USE_NPU_EMBEDDINGS"] = "1"
        os.environ["EMBEDDING_DEVICE"] = "NPU"

    print("\n3. Running Topological Collapse Tests:")
    print(f"{ 'Test Case':<25} | { 'Target Logic':<40} | { 'Confidence':<10} | {'Result'}")
    print("-" * 95)

    success_count = 0
    
    for case in test_cases:
        # A. Embed Intent
        intent_vec = get_substrate_embedding(case["intent"])
        
        # B. Collapse Manifold
        match_id, conf = collapse_manifold(intent_vec, singularities)
        
        # C. Verify
        passed = case["expected_partial"] in match_id
        status = "PASS" if passed else "FAIL"
        if passed: success_count += 1
        
        # Format output
        short_id = match_id.split("/")[-1] if match_id else "None"
        if len(short_id) > 38: short_id = "..." + short_id[-35:]
        
        print(f"{case['desc']:<25} | {short_id:<40} | {conf:.4f}     | {status}")
        if not passed:
            print(f"   -> Intent: '{case['intent']}'")
            print(f"   -> Expected: *{case['expected_partial']}*")
            print(f"   -> Got: {match_id}")

    print("-" * 95)
    print(f"Manifold Integrity: {success_count}/{len(test_cases)} Passed")
    
    if success_count == len(test_cases):
        print("\n[CONCLUSION] The Substrate Manifold is structurally sound.")
        print("User Intent successfully collapses onto correct logic singularities via NPU.")
    else:
        print("\n[CONCLUSION] Manifold shows topological fractures. Re-embedding may be required.")

if __name__ == "__main__":
    main()
