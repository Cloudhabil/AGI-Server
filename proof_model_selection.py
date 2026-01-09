"""
Proof of Neural Model Selection Logic
=====================================

Executes a battery of tasks through the NeuronicRouter to verify
that the 'Intuition' pass correctly aligns task complexity with
the specific local model substrates.
"""

import json
import logging
from agents.neuronic_router import get_neuronic_router

# Configure logging to show the intuition selections
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("Proof")

TEST_TASKS = [
    {
        "id": "MATH_01",
        "prompt": "Prove that the sum of two even integers is always even.",
        "expected_role": "REASONING",
        "target": "qwen2_math"
    },
    {
        "id": "VISION_01",
        "prompt": "Describe the contents of the attached image showing a hardware rack.",
        "expected_role": "VISION",
        "target": "llava"
    },
    {
        "id": "CODE_01",
        "prompt": "Extract the API keys from this json block: {'key': '12345'}",
        "expected_role": "FAST",
        "target": "codegemma"
    },
    {
        "id": "DEEP_01",
        "prompt": "Analyze the philosophical implications of a 78C thermal limit on machine consciousness.",
        "expected_role": "REASONING",
        "target": "deepseek_r1"
    }
]

def run_proof():
    router = get_neuronic_router()
    results = []

    print(f"{'TASK_ID':<10} | {'SELECTED_MODEL':<20} | {'ALIGNMENT'}")
    print("-" * 60)

    for task in TEST_TASKS:
        # We use a mocked context or limited tokens for the proof
        # In a real run, this would trigger the full query
        # Here we just want to verify the 'Intuition' phase selection
        
        intuition = router.intuition.execute({
            "capability": "align_model",
            "task_query": task["prompt"]
        }, None).output
        
        selected = intuition.get("selected_id")
        rationale = intuition.get("rationale")
        
        status = "MATCH" if selected == task["target"] else "DIVERGENT"
        
        print(f"{task['id']:<10} | {selected:<20} | {status}")
        print(f"  > Rationale: {rationale}\n")
        
        results.append({
            "task_id": task["id"],
            "selected": selected,
            "status": status,
            "rationale": rationale
        })

    with open("model_selection_proof.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_proof()
