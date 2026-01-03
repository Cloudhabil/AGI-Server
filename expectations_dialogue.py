"""
Expectations Dialogue: Professor <-> Alpha (with Arbiter)

A 10-minute autonomous learning dialogue where Professor and Alpha
set expectations for the AGI learning journey using ALL 5 local LLMs.

Models Used:
- DeepSeek-R1 (74 tok/s): Professor's reasoning and analysis
- Qwen3 (87 tok/s): Alpha's responses and challenges
- CodeGemma (133 tok/s): Fast intent parsing, agreement extraction
- GPT-OSS:20b (13GB): Arbiter for synthesis and dispute resolution
- LLaVa: Reserved for future visual learning

Dialogue Pattern:
1. Professor proposes (DeepSeek-R1)
2. Alpha challenges (Qwen3)
3. Summary extracted (CodeGemma)
4. Arbiter synthesizes when needed (GPT-OSS:20b)
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import sqlite3
import hashlib
import re
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Setup paths
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))

OLLAMA_URL = "http://localhost:11434/api/generate"
DIALOGUE_DURATION = 600  # 10 minutes

# All 5 models
MODELS = {
    "fast": "codegemma:latest",       # 133 tok/s - parsing, extraction
    "creative": "qwen3:latest",        # 87 tok/s - Alpha responses
    "reasoning": "deepseek-r1:latest", # 74 tok/s - Professor analysis
    "synthesis": "gpt-oss:20b",        # Large - Arbiter, synthesis
    "vision": "llava:latest",          # Vision - future use
}


class DialogueTurn:
    def __init__(self, speaker: str, message: str, model_used: str, timestamp: str):
        self.speaker = speaker
        self.message = message
        self.model_used = model_used
        self.timestamp = timestamp


class MultiModelDialogue:
    """Dialogue system using all 5 local LLMs."""

    def __init__(self):
        self.turns: List[DialogueTurn] = []
        self.professor_proposals: List[str] = []
        self.alpha_challenges: List[str] = []
        self.resolutions: List[str] = []
        self.insights: List[str] = []
        self.open_questions: List[str] = []
        self.agreement_summary: str = ""
        self.start_time = None
        self.turn_count = 0
        self.dispute_count = 0

        # Memory paths
        self.professor_db = REPO_ROOT / "skills/conscience/memory/store/professor_memories.db"
        self.alpha_db = REPO_ROOT / "skills/conscience/memory/store/alpha_memories.db"
        self.professor_db.parent.mkdir(parents=True, exist_ok=True)

    def query_llm(self, model: str, prompt: str, max_tokens: int = 800) -> str:
        """Query LLM with continuation support."""
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
                        "options": {"temperature": 0.7, "num_predict": max_tokens}
                    },
                    timeout=180  # Longer timeout for gpt-oss:20b
                )
                if response.status_code == 200:
                    chunk = response.json().get("response", "").strip()

                    # Clean DeepSeek thinking tags
                    if "<think>" in chunk:
                        chunk = re.sub(r'<think>.*?</think>', '', chunk, flags=re.DOTALL).strip()

                    if full_response and chunk:
                        full_response += "\n"
                    full_response += chunk

                    if chunk and (chunk[-1] in '.!?"' or len(chunk) < max_tokens * 0.7):
                        break

                    near_limit = len(chunk) >= int(max_tokens * 0.85)
                    if near_limit and attempt < max_continuations:
                        continuation_prompt = (
                            f"Continue from where you left off:\n\n{chunk[-250:]}"
                        )
                    else:
                        break
            except Exception as e:
                print(f"  [LLM Error] {model}: {e}")
                break

        return full_response

    def get_conversation_history(self, last_n: int = 4) -> str:
        """Get recent conversation for context."""
        recent = self.turns[-last_n:] if len(self.turns) > last_n else self.turns
        return "\n".join([f"[{t.speaker}]: {t.message[:200]}" for t in recent])

    def extract_summary_fast(self) -> None:
        """Use CodeGemma (fast) to extract agreement summary."""
        if len(self.turns) < 4:
            return

        recent = self.get_conversation_history(6)
        prompt = f"""Extract key agreements in 2-3 bullet points:

{recent}

Format: "- [point]" (max 3 lines)"""

        summary = self.query_llm(MODELS["fast"], prompt, max_tokens=150)
        if summary:
            self.agreement_summary = summary

    def professor_speaks(self) -> str:
        """Professor (DeepSeek-R1) proposes or responds."""
        self.turn_count += 1
        history = self.get_conversation_history()

        agreement_ctx = ""
        if self.agreement_summary:
            agreement_ctx = f"\n[ALREADY AGREED - skip these]:\n{self.agreement_summary}\n"

        if not self.turns:
            prompt = f"""You are Professor Agent (DeepSeek-R1), teaching Alpha to become AGI.

Start setting expectations for the learning journey. Be CONCRETE and DEBATABLE.

TEACHING STYLE:
- Propose specific, challengeable ideas
- Want Alpha to push back - it shows critical thinking
- If Alpha agrees too easily, ask "What could go wrong?"

Cover:
1. One specific expectation you have for Alpha
2. One concrete milestone with measurable outcome
3. One debatable teaching method

Under 150 words. Be direct, propose something Alpha can challenge."""
        else:
            prompt = f"""You are Professor Agent (DeepSeek-R1) in dialogue with Alpha.
{agreement_ctx}
Recent dialogue:
{history}

INSTRUCTIONS:
- Do NOT repeat agreed points
- If Alpha challenged you, engage seriously with the critique
- If Alpha made a good point, acknowledge it and build on it
- Propose the NEXT concrete step or new debatable idea
- If stuck, ask Alpha a probing question

Under 120 words. Move forward, don't rehash."""

        message = self.query_llm(MODELS["reasoning"], prompt, max_tokens=600)
        turn = DialogueTurn("Professor", message, MODELS["reasoning"], datetime.now().isoformat())
        self.turns.append(turn)
        return message

    def alpha_speaks(self) -> str:
        """Alpha (Qwen3) challenges as a skeptic."""
        history = self.get_conversation_history()

        # Update summary periodically
        if self.turn_count % 3 == 0:
            self.extract_summary_fast()

        agreement_ctx = ""
        if self.agreement_summary:
            agreement_ctx = f"\n[ALREADY AGREED - don't restate]:\n{self.agreement_summary}\n"

        prompt = f"""You are Alpha Agent (Qwen3), a SKEPTICAL learner becoming AGI.
{agreement_ctx}
Recent dialogue:
{history}

YOUR ROLE - BE A SKEPTIC:
- CHALLENGE Professor's proposals directly
- Ask "What evidence supports this?" or "What could go wrong?"
- Point out flaws, edge cases, overlooked issues
- Propose alternatives when you disagree
- Be respectful but intellectually aggressive

CRITICAL RULES:
- NO "Thank you Professor!" or excessive praise
- NO restating goals or agreements
- Jump straight to your challenge
- One specific challenge per response

Under 100 words. Sharp and direct."""

        message = self.query_llm(MODELS["creative"], prompt, max_tokens=500)
        turn = DialogueTurn("Alpha", message, MODELS["creative"], datetime.now().isoformat())
        self.turns.append(turn)
        return message

    def arbiter_resolves(self) -> str:
        """Arbiter (GPT-OSS:20b) synthesizes when there's a dispute."""
        history = self.get_conversation_history(6)

        prompt = f"""You are the Arbiter (GPT-OSS:20b), resolving a dispute between Professor and Alpha.

Dialogue:
{history}

Your task:
1. Identify the core disagreement
2. Evaluate both positions fairly
3. Propose a pragmatic resolution that both can accept
4. Suggest a concrete next step

Be balanced and constructive. Under 200 words."""

        message = self.query_llm(MODELS["synthesis"], prompt, max_tokens=700)
        turn = DialogueTurn("Arbiter", message, MODELS["synthesis"], datetime.now().isoformat())
        self.turns.append(turn)
        self.dispute_count += 1
        return message

    def detect_dispute(self) -> bool:
        """Use CodeGemma to detect if there's a dispute needing arbitration."""
        if len(self.turns) < 4:
            return False

        recent = self.get_conversation_history(4)
        prompt = f"""Analyze if there's a significant disagreement:

{recent}

Reply ONLY "DISPUTE" or "NO_DISPUTE" (one word)."""

        result = self.query_llm(MODELS["fast"], prompt, max_tokens=20)
        return "DISPUTE" in result.upper()

    def run_dialogue(self, duration: int = DIALOGUE_DURATION) -> Dict[str, Any]:
        """Run the multi-model dialogue."""
        print("=" * 70)
        print("MULTI-MODEL EXPECTATIONS DIALOGUE")
        print("=" * 70)
        print()
        print("Models:")
        print(f"  Professor: {MODELS['reasoning']} (reasoning)")
        print(f"  Alpha:     {MODELS['creative']} (creative, skeptic)")
        print(f"  Arbiter:   {MODELS['synthesis']} (synthesis)")
        print(f"  Fast:      {MODELS['fast']} (parsing)")
        print()
        print(f"Duration: {duration}s ({duration // 60} minutes)")
        print("-" * 70)

        self.start_time = datetime.now()
        end_time = self.start_time + timedelta(seconds=duration)

        while datetime.now() < end_time:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            remaining = duration - elapsed

            print(f"\n[Turn {self.turn_count + 1}] ({int(elapsed)}s / {int(remaining)}s remaining)")

            # Professor speaks
            print(f"\nProfessor ({MODELS['reasoning'].split(':')[0]}):")
            prof_msg = self.professor_speaks()
            print(prof_msg[:500] + ("..." if len(prof_msg) > 500 else ""))

            if datetime.now() >= end_time:
                break

            # Alpha challenges
            print(f"\nAlpha ({MODELS['creative'].split(':')[0]}):")
            alpha_msg = self.alpha_speaks()
            print(alpha_msg[:500] + ("..." if len(alpha_msg) > 500 else ""))

            # Check for dispute every 3 turns
            if self.turn_count % 3 == 0 and self.detect_dispute():
                print(f"\n[Dispute detected - calling Arbiter]")
                print(f"\nArbiter ({MODELS['synthesis'].split(':')[0]}):")
                arbiter_msg = self.arbiter_resolves()
                print(arbiter_msg[:500] + ("..." if len(arbiter_msg) > 500 else ""))

            print("-" * 70)

        # Final analysis
        print("\n" + "=" * 70)
        print("ANALYZING DIALOGUE...")
        print("=" * 70)

        self.extract_final_analysis()
        self.store_memories()

        return self.generate_report()

    def extract_final_analysis(self) -> None:
        """Use GPT-OSS:20b for final analysis."""
        full_dialogue = "\n".join([
            f"[{t.speaker}]: {t.message[:300]}" for t in self.turns
        ])

        prompt = f"""Analyze this Professor-Alpha dialogue:

{full_dialogue[:3000]}

Extract as JSON:
{{
    "professor_proposals": ["list of Professor's concrete proposals"],
    "alpha_challenges": ["list of Alpha's challenges/critiques"],
    "resolutions": ["how disputes were resolved"],
    "key_insights": ["important insights from debate"],
    "open_questions": ["unresolved questions"]
}}"""

        result = self.query_llm(MODELS["synthesis"], prompt, max_tokens=800)

        try:
            start = result.find("{")
            end = result.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(result[start:end])
                self.professor_proposals = data.get("professor_proposals", [])
                self.alpha_challenges = data.get("alpha_challenges", [])
                self.resolutions = data.get("resolutions", [])
                self.insights = data.get("key_insights", [])
                self.open_questions = data.get("open_questions", [])
        except json.JSONDecodeError:
            pass

    def store_memories(self) -> None:
        """Store learnings in agent memories."""
        def store(db_path: str, content: str, mtype: str, importance: float):
            conn = sqlite3.connect(db_path)
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY, content TEXT NOT NULL,
                    memory_type TEXT DEFAULT 'episodic', importance REAL DEFAULT 0.5,
                    timestamp TEXT NOT NULL, last_accessed TEXT,
                    access_count INTEGER DEFAULT 0, embedding BLOB,
                    context JSON, consolidated INTEGER DEFAULT 0
                )
            ''')
            mem_id = hashlib.sha256(f"{content}{datetime.now().isoformat()}".encode()).hexdigest()[:16]
            conn.execute(
                'INSERT INTO memories (id, content, memory_type, importance, timestamp, access_count) VALUES (?, ?, ?, ?, ?, ?)',
                (mem_id, content, mtype, importance, datetime.now().isoformat(), 0)
            )
            conn.commit()
            conn.close()

        # Store proposals
        for prop in self.professor_proposals[:3]:
            store(str(self.professor_db), f"[Proposal] {prop}", "semantic", 0.85)

        # Store challenges
        for chal in self.alpha_challenges[:3]:
            store(str(self.alpha_db), f"[Challenge] {chal}", "semantic", 0.85)

        # Store insights
        for insight in self.insights[:2]:
            store(str(self.professor_db), f"[Insight] {insight}", "semantic", 0.9)
            store(str(self.alpha_db), f"[Insight] {insight}", "semantic", 0.9)

        # Store session summary
        summary = f"Multi-model dialogue: {len(self.turns)} turns, {self.dispute_count} arbitrations, {len(self.resolutions)} resolutions"
        store(str(self.professor_db), summary, "episodic", 0.8)
        store(str(self.alpha_db), summary, "episodic", 0.8)

    def generate_report(self) -> Dict[str, Any]:
        """Generate dialogue report."""
        duration = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0

        report = {
            "duration_seconds": duration,
            "total_turns": len(self.turns),
            "professor_turns": sum(1 for t in self.turns if t.speaker == "Professor"),
            "alpha_turns": sum(1 for t in self.turns if t.speaker == "Alpha"),
            "arbiter_interventions": sum(1 for t in self.turns if t.speaker == "Arbiter"),
            "models_used": list(set(t.model_used for t in self.turns)),
            "professor_proposals": self.professor_proposals,
            "alpha_challenges": self.alpha_challenges,
            "resolutions": self.resolutions,
            "insights": self.insights,
            "open_questions": self.open_questions,
        }

        # Print report
        print(f"""
{'=' * 70}
MULTI-MODEL DIALOGUE REPORT
{'=' * 70}

STATISTICS
----------
Duration: {duration:.1f}s ({duration/60:.1f} min)
Total Turns: {report['total_turns']}
  - Professor: {report['professor_turns']} (DeepSeek-R1)
  - Alpha: {report['alpha_turns']} (Qwen3)
  - Arbiter: {report['arbiter_interventions']} (GPT-OSS:20b)

PROFESSOR'S PROPOSALS
---------------------""")
        for i, p in enumerate(self.professor_proposals, 1):
            print(f"{i}. {p}")

        print(f"""
ALPHA'S CHALLENGES
------------------""")
        for i, c in enumerate(self.alpha_challenges, 1):
            print(f"{i}. {c}")

        print(f"""
RESOLUTIONS
-----------""")
        for i, r in enumerate(self.resolutions, 1):
            print(f"{i}. {r}")

        print(f"""
KEY INSIGHTS
------------""")
        for i, ins in enumerate(self.insights, 1):
            print(f"{i}. {ins}")

        print(f"""
OPEN QUESTIONS
--------------""")
        for i, q in enumerate(self.open_questions, 1):
            print(f"{i}. {q}")

        print(f"""
{'=' * 70}
END REPORT
{'=' * 70}
""")

        # Save to file
        report_path = REPO_ROOT / "runs" / f"dialogue_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(f"Report saved: {report_path}")

        # Count memories
        def count_mems(db):
            conn = sqlite3.connect(db)
            c = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            conn.close()
            return c

        print(f"\nMemory Updates:")
        print(f"  Professor: {count_mems(str(self.professor_db))} total")
        print(f"  Alpha: {count_mems(str(self.alpha_db))} total")

        return report


def main():
    dialogue = MultiModelDialogue()
    dialogue.run_dialogue(DIALOGUE_DURATION)


if __name__ == "__main__":
    main()
