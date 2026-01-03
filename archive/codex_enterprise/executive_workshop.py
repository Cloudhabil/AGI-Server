"""
Executive Agent Workshop
------------------------
Professor + Alpha collaborate to draft Executive Agent documentation.
Outputs:
- runs/executive_agent_spec.md
- prompts/EXECUTIVE.md
- runs/executive_agent_transcript.txt
"""

import argparse
import io
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import requests
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent
OLLAMA_URL = "http://localhost:11434/api/generate"

DEFAULT_MODELS = {
    "professor": "deepseek-r1:latest",
    "alpha": "qwen3:latest",
    "synth": "gpt-oss:20b",
}


class DialogueTurn:
    def __init__(self, speaker: str, message: str, model_used: str, timestamp: str):
        self.speaker = speaker
        self.message = message
        self.model_used = model_used
        self.timestamp = timestamp


def load_skill_catalog(limit: int = 60) -> List[str]:
    index_path = REPO_ROOT / "skills" / "INDEX.json"
    if not index_path.exists():
        return []
    try:
        payload = json.loads(index_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    items = []
    for entry in payload.get("skills", []):
        skill_id = entry.get("id") or ""
        description = entry.get("description") or ""
        if skill_id:
            items.append(f"- {skill_id}: {description}")
        if len(items) >= limit:
            break
    return items


def query_llm(model: str, prompt: str, max_tokens: int = 900) -> str:
    full_response = ""
    continuation_prompt = prompt
    max_continuations = 2

    for attempt in range(max_continuations + 1):
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": model,
                    "prompt": continuation_prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": max_tokens},
                },
                timeout=120,
            )
            if response.status_code == 200:
                chunk = response.json().get("response", "").strip()
                if full_response and chunk:
                    full_response += "\n"
                full_response += chunk

                if chunk and (chunk[-1] in ".!?\""):
                    break

                near_limit = len(chunk) >= int(max_tokens * 0.9)
                if near_limit and attempt < max_continuations:
                    continuation_prompt = (
                        "Continue your previous response. You were saying:\n\n"
                        f"{chunk[-300:]}\n\nContinue from where you left off:"
                    )
                else:
                    break
        except Exception as exc:
            print(f"LLM Error ({model}): {exc}")
            break

    return full_response


def format_history(turns: List[DialogueTurn], last_n: int = 6) -> str:
    recent = turns[-last_n:] if len(turns) > last_n else turns
    return "\n".join([f"[{t.speaker}]: {t.message}" for t in recent])


def run_workshop(models: Dict[str, str], max_turns: int, skill_catalog: List[str]) -> List[DialogueTurn]:
    turns: List[DialogueTurn] = []
    skill_block = "\n".join(skill_catalog) if skill_catalog else "- (skills index not available)"

    phases = [
        {
            "title": "Role Definition & Outcomes",
            "professor": (
                "Draft the Executive Agent role: mission, key responsibilities, decision authority, and outputs. "
                "Include 3-5 concrete deliverables. Cite at least 3 skills from the catalog and how Executive will use them."
            ),
            "alpha": (
                "Critique gaps, overreach, or vague outputs. Propose a pragmatic proxy metric for success and "
                "name at least 2 skills the Executive should rely on to close the gaps."
            ),
        },
        {
            "title": "Operating Workflow & Guardrails",
            "professor": (
                "Define the Executive workflow (intake -> plan -> delegate -> review -> finalize). "
                "Add guardrails, escalation criteria, and quality gates. Map each step to skills."
            ),
            "alpha": (
                "Challenge the workflow for deadlocks or missing checks. Suggest a 'good enough' acceptance criterion "
                "to prevent analysis paralysis."
            ),
        },
        {
            "title": "Integration Contract",
            "professor": (
                "Produce a compact Executive Agent system prompt outline (sections + bullet points). "
                "Specify interfaces with Professor and Alpha, and how Executive resolves disputes."
            ),
            "alpha": (
                "Challenge the dispute resolution and propose a pragmatic decision rule to ensure task completion."
            ),
        },
    ]

    for phase in phases:
        history = format_history(turns)
        professor_prompt = f"""You are Professor (DeepSeek-R1). You are collaborating with Alpha to design an Executive Agent.

PHASE: {phase['title']}
SKILL CATALOG (use these explicitly):
{skill_block}

RECENT DIALOGUE:
{history}

TASK:
{phase['professor']}

Constraints:
- Be concrete and specific.
- No fluff. Under 180 words.
"""
        professor_msg = query_llm(models["professor"], professor_prompt, max_tokens=900)
        turns.append(DialogueTurn("Professor", professor_msg, models["professor"], datetime.now().isoformat()))

        history = format_history(turns)
        alpha_prompt = f"""You are Alpha (Qwen3). You are the critical reviewer for the Executive Agent.

PHASE: {phase['title']}
SKILL CATALOG (use these explicitly):
{skill_block}

RECENT DIALOGUE:
{history}

TASK:
{phase['alpha']}

PRAGMATISM CONSTRAINT:
- Challenge assumptions, but accept a "good enough" proxy metric to move forward.
- You are a Skeptical Engineer, not a nihilistic philosopher.

Constraints:
- Provide 1-2 concrete fixes.
- Under 150 words.
"""
        alpha_msg = query_llm(models["alpha"], alpha_prompt, max_tokens=700)
        turns.append(DialogueTurn("Alpha", alpha_msg, models["alpha"], datetime.now().isoformat()))

        if len(turns) >= max_turns:
            break

    return turns


def synthesize_document(turns: List[DialogueTurn], models: Dict[str, str]) -> str:
    transcript = "\n".join([f"[{t.speaker}] {t.message}" for t in turns])
    prompt = f"""You are the synthesis agent. Convert the dialogue into a final Executive Agent spec.

Transcript:
{transcript}

Output a Markdown document with these sections:
1) Executive Agent Summary
2) Mission & Success Metrics (include a "good enough" proxy metric)
3) Responsibilities & Deliverables
4) Decision Workflow (intake -> plan -> delegate -> review -> finalize)
5) Skills Usage Map (list skill ids and how they are used)
6) Interfaces with Professor and Alpha (handoff + dispute resolution)
7) Guardrails & Quality Gates
8) Prompt Template (system prompt text)

Keep it concise but complete. Use bullet points where appropriate.
"""
    return query_llm(models["synth"], prompt, max_tokens=1200)


def sanitize_spec(spec: str) -> str:
    cleaned = spec.replace("\uFFFD", "").replace("\u001A", "-")
    cleaned = cleaned.replace("\r\n", "\n")
    cleaned = cleaned.replace("\t", " ")
    cleaned = re.sub(r"=\?(\d+)\?%", r"\1%", cleaned)
    cleaned = re.sub(r"=\?(\d+)\?", r"\1", cleaned)
    cleaned = cleaned.replace("?", "?")
    cleaned = cleaned.replace("�", "")
    cleaned = cleaned.replace("", "-")
    cleaned = cleaned.encode("ascii", "ignore").decode("ascii")
    return cleaned


def write_outputs(spec: str, turns: List[DialogueTurn], out_dir: Path, prompt_path: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    spec_path = out_dir / "executive_agent_spec.md"
    transcript_path = out_dir / "executive_agent_transcript.txt"

    cleaned_spec = sanitize_spec(spec)
    spec_path.write_text(cleaned_spec, encoding="utf-8")
    transcript_path.write_text(
        "\n\n".join([f"[{t.speaker}] ({t.model_used})\n{t.message}" for t in turns]),
        encoding="utf-8",
    )

    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(cleaned_spec, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Executive Agent Workshop")
    parser.add_argument("--max-turns", type=int, default=6)
    parser.add_argument("--professor-model", default=DEFAULT_MODELS["professor"])
    parser.add_argument("--alpha-model", default=DEFAULT_MODELS["alpha"])
    parser.add_argument("--synth-model", default=DEFAULT_MODELS["synth"])
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "runs"))
    parser.add_argument("--prompt-path", default=str(REPO_ROOT / "prompts" / "EXECUTIVE.md"))
    args = parser.parse_args()

    models = {
        "professor": args.professor_model,
        "alpha": args.alpha_model,
        "synth": args.synth_model,
    }

    skills = load_skill_catalog()
    turns = run_workshop(models, args.max_turns, skills)
    spec = synthesize_document(turns, models)

    write_outputs(spec, turns, Path(args.out_dir), Path(args.prompt_path))

    print("Executive Agent spec generated.")
    print(f"Spec: {Path(args.out_dir) / 'executive_agent_spec.md'}")
    print(f"Prompt: {Path(args.prompt_path)}")


if __name__ == "__main__":
    main()
