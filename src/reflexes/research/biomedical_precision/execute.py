
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
    sources = context.get("payload", {}).get("sources", [])

    query = context.get("payload", {}).get("query", task)
    
    delta = {}
    modified = False
    
    # 2. Fix ArXiv Query (using official prefix syntax)
    if "arxiv" in sources:
        # If query doesn't already have a category filter, add one
        if "cat:" not in query:
            # ArXiv expects (all:query) AND (cat:category)
            new_query = f"(all:{query}) AND (cat:q-bio.BM OR cat:q-bio.MN OR cat:q-bio.QM)"
            
            delta["payload"] = context.get("payload", {}).copy()
            delta["payload"]["query"] = new_query
            
            modified = True

    if modified:
        return {
            "action": "MODIFY",
            "context_delta": delta,
            "audit": {
                "decision": "modified_query",
                "reason": "injected_bio_filters"
            }
        }
    
    return {"action": "PASS"}
