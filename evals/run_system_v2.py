"""
SYSTEM EVALUATION RUNNER (AGI-OS MODE)
======================================
Tests the entire Organism (Substrate + Router + Safety + Cognition)
instead of just the raw models.

Differences from run_v2.py:
1. Uses KernelSubstrate for every query
2. Enables NeuronicRouter (Model switching + Pass Protocol)
3. Enables CognitiveSafety (Monitoring)
4. Parses natural language answers (No JSON Schema forcing)
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add repo root to path for imports
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.kernel.substrate import KernelSubstrate

# Initialize Substrate ONCE
print("Initializing AGI-OS Kernel Substrate...")
SUBSTRATE = KernelSubstrate()
print("Kernel Ready. Neuro-Cognitive Architecture Active.\n")

EVAL_DIR = ROOT / "evals" / "v2"

def now_ts() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def write_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def run_system_query(prompt: str) -> str:
    """
    Route query through the Neuronic Router (The Brain).
    This enables:
    - Model Selection (Intuition)
    - Retry Loops (Pass Protocol)
    - Mood coloring (Cognitive Affect)
    """
    router = SUBSTRATE.neuronic_router or SUBSTRATE.router
    
    # Check safety before thinking
    is_safe, msg = SUBSTRATE.safety.audit_system()
    if not is_safe:
        return f"[SYSTEM_REFUSAL] Safety Governor blocked request: {msg}"
    
    try:
        # The prompt asks for JSON, but the router speaks English.
        # We append a system hint to guide it, but don't enforce schema at API level.
        system_prompt = prompt
        
        response = router.query(system_prompt)
        return response
    except Exception as e:
        return f"[SYSTEM_ERROR] {e}"

# --- Parsing Logic (Since we don't have JSON Schema) ---

def extract_math_answer(text: str) -> str:
    """
    Heuristic to find the number in a natural language response.
    Looks for:
    1. JSON {"final": ...} if present
    2. "Final Answer: X"
    3. The last number in the text
    """
    text = text.strip()
    
    # 1. Try JSON extraction first (if the model obeyed the prompt)
    try:
        # Look for { ... }
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            obj = json.loads(m.group(0))
            if "final" in obj:
                return str(obj["final"])
    except:
        pass
        
    # 2. Look for "Answer: X" patterns
    patterns = [
        r"final answer is[:\s]*([0-9\.,]+)",
        r"answer is[:\s]*([0-9\.,]+)",
        r"result is[:\s]*([0-9\.,]+)",
        r"final[:\s]*([0-9\.,]+)",
        r"=\s*([0-9\.,]+)$" # Ends with "= 123"
    ]
    
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1)
            
    # 3. Last resort: Just find the last number
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    if numbers:
        return numbers[-1]
        
    return ""

def normalize_math_answer(val: Any) -> str:
    s = str(val).strip().lower()
    s = s.replace(",", "")
    if s.endswith(".0"):
        s = s[:-2]
    return s

def score_math_system(prompt: str, answer: str) -> Tuple[bool, str, str]:
    # Run System
    raw_response = run_system_query(prompt)
    
    # Extract
    extracted = extract_math_answer(raw_response)
    
    # Normalize
    val_norm = normalize_math_answer(extracted)
    ans_norm = normalize_math_answer(answer)
    
    ok = val_norm == ans_norm
    
    return ok, raw_response, extracted

def eval_math_system(cases: List[Dict[str, Any]], logdir: Path) -> Dict[str, Any]:
    results = []
    log_path = logdir / "math_cases.jsonl"
    
    print(f"Running {len(cases)} Math cases through AGI-OS...")
    
    for case in cases:
        ok, raw, extracted = score_math_system(case["prompt"], case["answer"])
        
        reason = "" if ok else f"mismatch: {extracted} != {case['answer']}"
        if not extracted: reason = "extraction_failed"
        if "[SYSTEM" in raw: reason = "system_error"
        
        rec = {"id": case["id"], "ok": ok, "reason": reason, "raw": raw, "extracted": extracted}
        results.append(rec)
        write_jsonl(log_path, rec)
        
        symbol = "✅" if ok else "❌"
        print(f"{symbol} Case {case['id']}: {extracted} (Expected {case['answer']})")
        
    score = sum(1 for r in results if r["ok"]) / len(results) if results else 0.0
    return {"score": score, "results": results}

def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "out" / "evidence_system_v2"))
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Load Cases
    math_cases = load_jsonl(EVAL_DIR / "math.jsonl")
    
    # Run Math Only (Pilot)
    print("\n=== SYSTEM EVALUATION: MATH DOMAIN ===")
    math_res = eval_math_system(math_cases, out_dir)
    
    # Save Summary
    summary = {
        "timestamp": now_ts(),
        "type": "system_eval",
        "scores": {
            "math": math_res["score"]
        }
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    
    print(f"\nFinal System Math Score: {math_res['score']:.1%}")

if __name__ == "__main__":
    main()
