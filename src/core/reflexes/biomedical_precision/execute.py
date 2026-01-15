
from typing import Any, Dict

def run(task: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    """
    Reflex: Biomedical Precision
    Detects bio-queries and enforces domain-specific filters.
    """
    task_lower = task.lower()
    
    # Bio-keywords that trigger the reflex
    triggers = ["nad+", "longevity", "protein", "gene", "enzyme", "metabolism", "cell", "pathway"]
    
    is_bio = any(t in task_lower for t in triggers)
    
    if not is_bio:
        return {"action": "PASS"}

    # Check for ArXiv contamination risk
    # (ArXiv often has 'precursor' in astrophysics contexts)
    sources = context.get("payload", {}).get("sources", [])
    query = context.get("payload", {}).get("query", task)
    
    delta = {}
    modified = False
    
    # 1. Enforce PubMed priority
    if "pubmed" not in sources:
        # We can't easily add it if the user didn't ask, but we can ensure it's there if 'sources' is default
        pass

    # 2. Fix ArXiv Query
    if "arxiv" in sources:
        # If query doesn't already have a category filter, add one
        if "cat:" not in query:
            new_query = f"{query} AND (cat:q-bio.BM OR cat:q-bio.MN OR cat:q-bio.QM)"
            # Update the payload query
            if "payload" not in context:
                delta["payload"] = {}
            
            # We need to construct the delta carefully
            # The context passed to reflex is often the raw input
            # We'll just return a context_delta that overrides the query
            delta["payload"] = context.get("payload", {}).copy()
            delta["payload"]["query"] = new_query
            
            modified = True

    if modified:
        return {
            "action": "MODIFY", # Or PASS with side-effects, but MODIFY signals change
            "context_delta": delta,
            "audit": {
                "decision": "modified_query",
                "reason": "injected_bio_filters"
            }
        }
    
    return {"action": "PASS"}
