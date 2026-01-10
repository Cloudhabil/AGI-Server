from pathlib import Path
from datetime import datetime
from inspect import signature
from typing import Any, Callable, Dict
import json

from core.kb import last, ingest_hierarchical_text
from hnet.dynamic_chunker import DynamicChunker, _token_count
from hnet.hierarchical_memory import HierarchicalMemory

# Adjust to your repo root if needed:
REPO_DIR = Path.cwd()
DOCS_DIR = REPO_DIR / "docs"


def agent_generate_ideas(context: dict) -> str:
    """Return a list of high-impact feature ideas.

    Args:
        context: Recent project context. Currently unused but kept for parity with
            other agents that accept contextual data.

    Returns:
        Newline-separated bullet list of suggestions.
    """

    ideas = [
        "- /agent init <persona>: create scoped expert agents (senior backend, DevOps, product).",
        "- Self-healing deps: detect CVEs/deprecations and auto-suggest patches.",
        "- Explain-as-you-code: inline rationale + alternatives while editing.",
        "- HabilModules: snap-in FastAPI/Flask micro-modules (auth, CRUD, billing).",
        "- Mission Loop telemetry: measure suggestion acceptance & cycle time.",
    ]
    return "High-impact ideas:\n" + "\n".join(ideas)


def agent_explain_concepts(topic: str) -> str:
    """Provide a conceptual overview for a given topic.

    Args:
        topic: Subject to explain.

    Returns:
        Multi-line string highlighting key aspects and examples.
    """

    return (
        f"Concept deep-dive on '{topic}':\n"
        "- What / Why / Trade-offs\n"
        "- Modern applications\n"
        "- Example(s) with pros/cons"
    )


def agent_optimize_code(code: str) -> str:
    """Suggest refactors and cleanups for a code snippet.

    Args:
        code: Source code to analyze.

    Returns:
        Bullet list of optimization recommendations.
    """

    # Placeholder for Codex+linting; return a diff-like suggestion
    return (
        "Suggested improvements:\n"
        "- Extract pure functions\n"
        "- Add typing\n"
        "- Reduce nesting\n"
        "- Use logging over prints"
    )


def agent_resolve_problems(symptoms: str) -> str:
    """Outline a debugging plan based on observed symptoms.

    Args:
        symptoms: Description of the issue.

    Returns:
        Ordered steps to track down and fix the problem.
    """

    return (
        "Gold Road (resolution path):\n"
        "1) Reproduce reliably\n"
        "2) Minimize test case\n"
        "3) Inspect logs/metrics\n"
        "4) Add assertions\n"
        "5) Patch + verify\n"
        "6) Regression guard"
    )


def agent_best_practices(scope: str) -> str:
    """List recommended practices for a given domain.

    Args:
        scope: Area to advise on, such as 'backend' or 'DevOps'.

    Returns:
        Multi-line bullet list of best practices.
    """

    return (
        f"Best practices for {scope}:\n"
        "- Clean architecture\n"
        "- Hexagonal boundaries\n"
        "- Observability first\n"
        "- CI as code\n"
        "- Security by default"
    )


def agent_write_docs(title: str, body: str) -> Path:
    """Persist documentation content to the ``docs`` directory.

    Args:
        title: Document title used for the filename and heading.
        body: Markdown content to write.

    Returns:
        Path to the newly created document.
    """

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    path = DOCS_DIR / f"{ts}_{title.replace(' ', '_').lower()}.md"
    path.write_text(f"# {title}\n\n{body}\n", encoding="utf-8")
    return path


def agent_code_review(code: str) -> str:
    """Produce a generic code review checklist for a snippet.

    Args:
        code: Source code to review.

    Returns:
        Multi-line list of review items.
    """

    return (
        "Code Review:\n"
        "- Naming clarity\n"
        "- Single responsibility\n"
        "- Error handling\n"
        "- Test coverage\n"
        "- Performance hotspots"
    )


def agent_prototype(description: str) -> str:
    """Generate a minimal FastAPI prototype scaffold.

    Args:
        description: Placeholder text describing the prototype's goal.

    Returns:
        String containing a ready-to-save Python module.
    """

    return f'''# prototype_app.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

# TODO: {description}
'''


AGENT_FUNCTIONS: Dict[str, Callable] = {
    "generate_ideas": agent_generate_ideas,
    "explain_concepts": agent_explain_concepts,
    "optimize_code": agent_optimize_code,
    "resolve_problems": agent_resolve_problems,
    "best_practices": agent_best_practices,
    "write_docs": agent_write_docs,
    "code_review": agent_code_review,
    "prototype": agent_prototype,
}


def fetch_context(n: int = 5, query: str | None = None) -> str:
    """Return a concatenated summary of recent knowledge base entries.

    Large entries are hierarchically chunked and summarized using H-Net's
    :class:`DynamicChunker`.  Each summary is persisted via
    :func:`kb.ingest_hierarchical_text`.  A lightweight
    :class:`HierarchicalMemory` index is populated so that, when a ``query`` is
    provided, relevant chunks are retrieved to reconstruct context.
    """

    entries = last(n)
    chunker = DynamicChunker()
    memory = HierarchicalMemory(embedding_fn=lambda t: [0.0])

    def summarizer(t: str) -> str:
        return " ".join(t.split()[:40])

    summaries: list[str] = []

    for entry in entries:
        raw = entry.get("data", "")
        try:
            payload = json.loads(raw)
            text = payload.get("text", raw)
        except Exception:
            text = raw

        if _token_count(text) > chunker.max_tokens:
            summary = ingest_hierarchical_text(
                text,
                summarizer,
                max_tokens=chunker.max_tokens,
                overlap_tokens=chunker.overlap_tokens,
            )
        else:
            summary = summarizer(text)
        summaries.append(summary)
        memory.add_segment("kb", text)

    if query:
        summaries.extend(memory.search("kb", query))

    return "\n".join(summaries)


def delegate(task: str, *args: Any, **kwargs: Any) -> Any:
    """Retrieve context from the KB then invoke the requested agent.

    Args:
        task: Key of the agent function to execute.
        *args: Positional arguments forwarded to the agent.
        **kwargs: Keyword arguments forwarded to the agent.

    Returns:
        The result of the underlying agent call.
    """

    context = fetch_context()
    func = AGENT_FUNCTIONS[task]
    if "context" in signature(func).parameters and "context" not in kwargs:
        kwargs["context"] = {"summary": context}
    return func(*args, **kwargs)
