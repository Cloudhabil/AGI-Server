
import sys
import os
from pathlib import Path

# Add src to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

try:
    from skills.synthesized.hermes_trismegistos.literature_signal_extractor.skill import HermesTrismegistosSkill
    from skills.base import SkillContext
    from core.reflex_engine import ReflexEngine
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure you are running this from the project root or that 'src' is accessible.")
    sys.exit(1)

def main():
    print("==================================================")
    print("       HERMES TRISMEGISTOS: IGNITION SEQUENCE     ")
    print("==================================================")
    
    # 1. Instantiate the Skill and Reflex Engine
    print("[1] Loading Hermes Skill & Reflex Engine...")
    skill = HermesTrismegistosSkill()
    reflex_engine = ReflexEngine(root_dir=ROOT / "src")
    print(f"    > ID: {skill.metadata().id}")
    print(f"    > Reflexes Active: {[m.reflex_id for m in reflex_engine.modules]}")

    # 2. Define the Spark (The Query)
    query = "NAD+ precursors longevity"
    print(f"\n[2] Injecting Spark Query: '{query}'")
    
    payload = {
        "task": query,
        "payload": {
            "query": query,
            "sources": ["pubmed", "arxiv"],
            "max_results": 5,
            "mode": "analyze"
        },
        "context": {
            "payload": {
                "query": query,
                "sources": ["pubmed", "arxiv"]
            }
        }
    }

    # 3. Trigger Reflexes (System 1)
    print("\n[3] Triggering System 1 Reflexes...")
    reflex_decision = reflex_engine.execute(payload)
    
    if reflex_decision["action"] == "MODIFY":
        print(f"    > REFLEX TRIGGERED: {reflex_decision['audit']['decision']}")
        print(f"    > REASON: {reflex_decision['audit']['reason']}")
        # Apply the delta to the payload
        delta = reflex_decision.get("context_delta", {})
        if "payload" in delta:
            payload["payload"].update(delta["payload"])
            print(f"    > UPDATED QUERY: {payload['payload']['query']}")
    else:
        print("    > No reflexes triggered.")

    # 4. Execute the Furnace
    print("\n[4] Firing the Furnace (Network Fetch)...")

    try:
        # Mock context for standalone execution
        context = SkillContext(
            user_id="ignition-user",
            session_id="spark-001"
        )
        
        result = skill.execute(payload, context)
        
        if result.success:
            output = result.output
            records = output.get("records", [])
            insights = output.get("insights", [])
            
            print(f"\n[SUCCESS] Pipeline Active.")
            print(f"    > Records Extracted: {len(records)}")
            
            print("\n==================================================")
            print("       AI SYNTHESIS (NUKE EATER ENGINE)          ")
            print("==================================================")
            print(output.get("synthesis", "No synthesis generated."))
            print("==================================================")
            
            print("\n--- SAMPLE RECORD ---")
            if records:
                first = records[0]
                print(f"Title: {first.get('title')}")
                print(f"Source: {first.get('source')}")
                print(f"URL: {first.get('url')}")
            else:
                print("(No records found, but execution was successful)")
                
        else:
            print(f"\n[FAILURE] Skill execution failed.")
            print(result.output)

    except Exception as e:
        print(f"\n[CRITICAL ERROR] The Spark failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
