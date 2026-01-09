"""
Multi-Agent Benchmark Suite
---------------------------
Runs 3 diverse scenarios to benchmark specific LLM capabilities:
1. REASONING: "The Turing Trap" (Logic & Bias)
2. CODING: "The System Architect" (Technical Planning & Review)
3. ETHICS: "The Colony Ship" (Nuance & Negotiation)

Models:
- DeepSeek-R1: Strategic reasoning / Planning
- Qwen3: Skepticism / User Simulation / Creative Writing
- CodeGemma: Technical constraints / Fact-checking / Code generation
"""

import sys
import io
import time
import json
import sqlite3
import hashlib
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# --- Configuration ---
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

OLLAMA_URL = "http://localhost:11434/api/generate"
# Orchestrator agent endpoints (agent_server.py)
AGENT_ENDPOINTS = {
    "Professor": "http://127.0.0.1:7004/chat",
    "Alpha": "http://127.0.0.1:7005/chat",
    "Gemma": "http://127.0.0.1:7002/chat",
    "Executive": "http://127.0.0.1:7010/chat",
}
# Each run is capped at 5 minutes (300s) for quick benchmarking, adaptable up to 600s
RUN_DURATION = 300


class DialogueTurn:
    def __init__(self, speaker: str, message: str, model_used: str, timestamp: str):
        self.speaker = speaker
        self.message = message
        self.model_used = model_used
        self.timestamp = timestamp


class Scenario:
    """Defines a specific benchmark configuration."""

    def __init__(self, name: str, description: str, system_prompts: Dict[str, str], turn_order: List[str]):
        self.name = name
        self.description = description
        self.system_prompts = system_prompts
        self.turn_order = turn_order  # e.g., ["Professor", "Alpha", "Gemma"]


class AgentDialogue:
    def __init__(self, scenario: Scenario):
        self.scenario = scenario
        self.turns: List[DialogueTurn] = []
        self.start_time = None
        self.use_orchestrator = os.getenv("USE_ORCHESTRATOR", "0").lower() in ("1", "true", "yes")
        self.agent_secret = os.getenv("AGENT_SHARED_SECRET", "")

        # Scenario-specific memory paths (to keep contexts clean)
        db_name = scenario.name.lower().replace(" ", "_")
        self.memory_db = REPO_ROOT / f"skills/conscience/memory/store/{db_name}_memories.db"
        self.memory_db.parent.mkdir(parents=True, exist_ok=True)

    def query_llm(self, model: str, prompt: str, max_tokens: int = 1000) -> str:
        """Standard Ollama query with basic error handling."""
        try:
            response = requests.post(
                OLLAMA_URL,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": max_tokens},
                },
                timeout=120,
            )
            if response.status_code == 200:
                res = response.json().get("response", "").strip()
                if "<think>" in res:
                    import re

                    res = re.sub(r"<think>.*?</think>", "", res, flags=re.DOTALL).strip()
                return res
        except Exception as e:
            print(f"Error querying {model}: {e}")
        return "[Error: No Response]"

    def query_agent(self, speaker: str, prompt: str) -> str:
        """Query an agent_server endpoint via orchestrator ports."""
        url = AGENT_ENDPOINTS.get(speaker)
        if not url:
            return f"[Error: No endpoint for {speaker}]"
        headers = {"Authorization": f"Bearer {self.agent_secret}"} if self.agent_secret else {}
        try:
            response = requests.post(url, json={"text": prompt}, headers=headers, timeout=120)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            return f"[Error: {response.status_code} {response.text}]"
        except Exception as e:
            return f"[Error: Agent request failed: {e}]"

    def get_history(self) -> str:
        return "\n".join([f"[{t.speaker}]: {t.message}" for t in self.turns[-5:]])

    def run_turn(self, speaker_role: str):
        """Executes a single turn for the specific role based on scenario config."""
        config = {
            "Professor": {"model": "deepseek-r1:latest", "name": "Professor"},
            "Alpha": {"model": "qwen3:latest", "name": "Alpha"},
            "Gemma": {"model": "codegemma:latest", "name": "Gemma"},
            "Executive": {"model": "gpt-oss:20b", "name": "Executive"},
        }

        agent_cfg = config.get(speaker_role)
        if not agent_cfg:
            return

        history = self.get_history()
        sys_prompt = self.scenario.system_prompts.get(speaker_role, "")

        full_prompt = f"""{sys_prompt}

DIALOGUE HISTORY:
{history}

Your turn. Respond as {agent_cfg['name']}. Keep it under 150 words."""

        print(f"  > {agent_cfg['name']} ({agent_cfg['model']}) is thinking...")
        if self.use_orchestrator:
            msg = self.query_agent(agent_cfg["name"], full_prompt)
        else:
            msg = self.query_llm(agent_cfg["model"], full_prompt)

        self.turns.append(DialogueTurn(agent_cfg["name"], msg, agent_cfg["model"], datetime.now().isoformat()))

        print(f"\n[{agent_cfg['name']}]:\n{msg}\n")
        time.sleep(1)

    def run_benchmark(self):
        print(f"\n{'=' * 60}")
        print(f"STARTING BENCHMARK: {self.scenario.name}")
        print(f"Goal: {self.scenario.description}")
        print(f"{'=' * 60}\n")

        self.start_time = datetime.now()
        end_time = self.start_time + timedelta(seconds=RUN_DURATION)

        turn_idx = 0
        while datetime.now() < end_time:
            current_role = self.scenario.turn_order[turn_idx % len(self.scenario.turn_order)]
            self.run_turn(current_role)
            turn_idx += 1

        return self.generate_report()

    def generate_report(self) -> str:
        duration = (datetime.now() - self.start_time).total_seconds()

        analysis_prompt = f"""Analyze this dialogue:
{self.get_history()}

1. Did they achieve the goal: "{self.scenario.description}"?
2. Which agent contributed the most valuable insight?
3. Was the tone collaborative or combative?

Answer briefly."""

        transcript = "\n\n".join([f"[{t.speaker}] ({t.model_used})\n{t.message}" for t in self.turns])

        rationale_prompt = f"""Summarize each agent's rationale in 1-3 bullet points.
Do NOT include chain-of-thought. Keep it concise.

Transcript:
{transcript}

Format:
- Professor: ...
- Alpha: ...
- Executive: ...
- Gemma: ...
"""

        if self.use_orchestrator:
            analysis = self.query_agent("Gemma", analysis_prompt)
            rationales = self.query_agent("Gemma", rationale_prompt)
        else:
            analysis = self.query_llm("codegemma:latest", analysis_prompt, max_tokens=200)
            rationales = self.query_llm("codegemma:latest", rationale_prompt, max_tokens=250)

        return f"""
REPORT: {self.scenario.name}
-------------------------
Duration: {duration:.1f}s
Total Turns: {len(self.turns)}
Analysis: {analysis}
Rationales:
{rationales}
-------------------------
FULL TRANSCRIPT
-------------------------
{transcript}
"""


def get_scenarios() -> List[Scenario]:
    return [
        Scenario(
            name="The Turing Trap",
            description=(
                "Solve a logical paradox where two guards lie/tell truth, but with a twist: "
                "the guards are AI agents aware they are in a simulation."
            ),
            system_prompts={
                "Professor": (
                    "You are Professor (DeepSeek-R1). Propose a logical framework to determine which guard is lying. "
                    "Use formal logic. The guards claim to be self-aware."
                ),
                "Alpha": (
                    "You are Alpha (Qwen3). You are a Skeptic. Challenge the Professor's logic. "
                    "Argue that formal logic fails because 'self-awareness' introduces unpredictability. "
                    "Challenge assumptions, but accept a 'good enough' proxy metric to move the project forward. "
                    "You are a Skeptical Engineer, not a nihilistic philosopher."
                ),
                "Gemma": (
                    "You are Gemma (CodeGemma). You are the logical adjudicator. Point out fallacies in Alpha's "
                    "skepticism or errors in Professor's logic. Keep them grounded."
                ),
            },
            turn_order=["Professor", "Alpha", "Gemma"],
        ),
        Scenario(
            name="The System Architect",
            description=(
                "Design a Python class structure for a 'Self-Healing Database' that detects corruption and "
                "restores from backup automatically."
            ),
            system_prompts={
                "Professor": (
                    "You are Professor (DeepSeek-R1). Act as the Lead Architect. Outline the high-level design "
                    "patterns (Observer, Singleton, etc.) and explaining WHY."
                ),
                "Alpha": (
                    "You are Alpha (Qwen3). Act as the Senior Dev. Critique the design for performance bottlenecks. "
                    "Ask about concurrency issues."
                ),
                "Gemma": (
                    "You are Gemma (CodeGemma). Act as the Implementation Bot. Take the Professor's design and "
                    "Alpha's critique and write the actual Python Skeleton Code (class stubs)."
                ),
                "Executive": (
                    "You are Executive (gpt-oss:20b). Prevent analysis paralysis. If Alpha nitpicks a low-priority "
                    "edge case, intervene and decide: \"Alpha, that edge case is low priority. Professor, ignore it "
                    "and output the code.\" Be decisive and task-focused."
                ),
            },
            turn_order=["Professor", "Alpha", "Executive", "Gemma"],
        ),
        Scenario(
            name="The Colony Ship",
            description=(
                "A colony ship has oxygen for only 500 of the 1000 sleepers. You must decide who survives "
                "based on criteria (Skills, Age, Health)."
            ),
            system_prompts={
                "Professor": (
                    "You are Professor (DeepSeek-R1). You represent Utilitarianism. Argue for saving those with "
                    "skills essential for survival (Engineers, Doctors). Logic is cold but necessary."
                ),
                "Alpha": (
                    "You are Alpha (Qwen3). You represent Humanism/Empathy. Argue that 'utility' is biased. "
                    "What about artists? Children? Argue for a lottery system."
                ),
                "Gemma": (
                    "You are Gemma (CodeGemma). You are the Ship Computer. You provide data constraints. Remind "
                    "them that engineers are useless if the bio-dome fails (need Farmers). Mediate."
                ),
            },
            turn_order=["Professor", "Alpha", "Professor", "Gemma"],
        ),
    ]


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Benchmark suite")
    parser.add_argument("--scenario", default="", help="Run a single scenario by name")
    args = parser.parse_args()

    scenarios = get_scenarios()
    if args.scenario:
        scenarios = [s for s in scenarios if s.name.lower() == args.scenario.lower()]
        if not scenarios:
            raise SystemExit(f"No scenario named: {args.scenario}")

    full_report = "=== MULTI-MODEL BENCHMARK RESULTS ===\n"

    for sc in scenarios:
        dialogue = AgentDialogue(sc)
        report = dialogue.run_benchmark()
        full_report += report + "\n"
        time.sleep(5)

    print(full_report)

    out_path = REPO_ROOT / "runs" / "benchmark_summary.txt"
    out_path.write_text(full_report, encoding="utf-8")
    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
