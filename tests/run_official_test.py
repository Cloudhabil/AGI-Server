"""
Official Human-vs-AI Comparison Test Runner.
Executes the evaluation suite via the Kernel Substrate.
"""
from core.kernel.substrate import KernelSubstrate
import json
import sys

def main():
    print("Initializing Kernel Substrate...")
    substrate = KernelSubstrate()
    
    print("Triggering Evaluation Service...")
    success = substrate.evaluator.run_evals()
    
    if not success:
        print("Evaluation failed to run.")
        sys.exit(1)
        
    print("Evaluation complete. Analyzing results...")
    
    # Read results directly since Governor might be lazy
    results_path = substrate.repo_root / "out" / "evidence_v2"
    
    # Find latest summary
    summaries = list(results_path.glob("**/summary.json"))
    if not summaries:
        print("No results found.")
        sys.exit(1)
        
    # Get the freshest one
    latest_summary = max(summaries, key=lambda p: p.stat().st_mtime)
    data = json.loads(latest_summary.read_text(encoding='utf-8'))
    
    scores = data.get("scores", {})
    
    print("\n" + "="*50)
    print("OFFICIAL TEST RESULTS")
    print("="*50)
    print(f"Model: {data.get('model')}")
    print(f"Timestamp: {data.get('timestamp')}")
    print("-" * 30)
    
    avg_score = 0
    count = 0
    
    for domain, score in scores.items():
        print(f"{domain.upper():<15}: {score:.1%}")
        avg_score += score
        count += 1
        
    if count > 0:
        avg_score /= count
    
    print("-" * 30)
    print(f"AVERAGE SCORE  : {avg_score:.1%}")
    print("="*50)
    
    # VERDICT
    print("\nVERDICT ANALYSIS:")
    
    is_agi = True
    is_asi = True
    
    # AGI Criteria: >90% in all core domains
    for d in ["math", "coding", "orchestration"]:
        s = scores.get(d, 0)
        if s < 0.9:
            is_agi = False
            print(f"❌ Failed AGI Threshold in {d} ({s:.1%} < 90%)")
    
    # ASI Criteria: >99% + Novelty (Proxy: Creative > 99%)
    for d in ["math", "coding", "orchestration", "creative"]:
        s = scores.get(d, 0)
        if s < 0.99:
            is_asi = False
            
    print("\nCONCLUSION:")
    if is_asi:
        print("🌟 STATUS: LEVEL 6 (ASI) - SUPERINTELLIGENCE DETECTED")
        print("   (Note: Requires verification of novel physics/math to be confirmed)")
    elif is_agi:
        print("🧠 STATUS: LEVEL 2 (AGI) - HUMAN-LEVEL GENERAL INTELLIGENCE")
    else:
        print("🔧 STATUS: LEVEL 1 (NARROW/ASSISTANT) - TOOL LEVEL")
        print("   The system has not yet demonstrated human-level mastery across all domains.")

if __name__ == "__main__":
    main()
