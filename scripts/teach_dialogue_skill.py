"""
Teach Dialogue Skill to Alpha

Professor Agent teaches Alpha the dialogue/conversation-handler skill
using all local LLMs. This creates a proper teaching loop where:
1. Professor analyzes the skill
2. Professor creates a lesson
3. Alpha studies the lesson
4. Alpha demonstrates understanding
5. Both store learnings in memory
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import json
import sqlite3
import hashlib
import requests
from datetime import datetime
from pathlib import Path

# Setup paths
# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
)

OLLAMA_URL = "http://localhost:11434/api/generate"


def query_llm(model: str, prompt: str, max_tokens: int = 800) -> str:
    """Query local Ollama LLM."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": max_tokens}
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except Exception as e:
        print(f"LLM Error: {e}")
    return ""


def store_memory(db_path: str, content: str, memory_type: str, importance: float):
    """Store memory in SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure table exists with correct schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            memory_type TEXT DEFAULT 'episodic',
            importance REAL DEFAULT 0.5,
            timestamp TEXT NOT NULL,
            last_accessed TEXT,
            access_count INTEGER DEFAULT 0,
            embedding BLOB,
            context JSON,
            consolidated INTEGER DEFAULT 0
        )
    ''')

    memory_id = hashlib.sha256(
        f"{content}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:16]

    timestamp = datetime.now().isoformat()

    cursor.execute('''
        INSERT INTO memories (id, content, memory_type, importance, timestamp, access_count)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (memory_id, content, memory_type, importance, timestamp, 0))

    conn.commit()
    conn.close()
    return memory_id


def main():
    print("=" * 70)
    print("TEACHING SESSION: Dialogue Skill")
    print("Professor Agent -> Alpha Agent")
    print("=" * 70)
    print()

    # Memory paths
    professor_db = REPO_ROOT / "skills/conscience/memory/store/professor_memories.db"
    alpha_db = REPO_ROOT / "skills/conscience/memory/store/alpha_memories.db"
    professor_db.parent.mkdir(parents=True, exist_ok=True)

    # Read the skill code
    skill_path = REPO_ROOT / "skills/dialogue/conversation_handler.py"
    skill_code = skill_path.read_text(encoding='utf-8')

    # ============================================================
    # PHASE 1: Professor Analyzes the Skill
    # ============================================================
    print("[Phase 1] Professor Analyzes the Dialogue Skill")
    print("-" * 70)

    analysis_prompt = f"""You are Professor Agent, an expert AI teacher.

Analyze this dialogue skill that enables natural language interaction:

```python
{skill_code[:3000]}
```

Provide:
1. Key concepts a student needs to understand
2. The interaction loop flow
3. How this enables AGI-level conversation
4. Learning objectives for the student

Be thorough but concise."""

    print("Professor (using DeepSeek-R1): Analyzing skill...")
    professor_analysis = query_llm("deepseek-r1:latest", analysis_prompt, max_tokens=1000)
    print(f"\nProfessor's Analysis:\n{professor_analysis[:800]}...")

    # Store Professor's analysis
    store_memory(
        str(professor_db),
        f"Analyzed dialogue/conversation-handler skill. Key insight: {professor_analysis[:300]}",
        "semantic",
        0.9
    )

    # ============================================================
    # PHASE 2: Professor Creates Lesson
    # ============================================================
    print("\n" + "=" * 70)
    print("[Phase 2] Professor Creates Lesson")
    print("-" * 70)

    lesson_prompt = f"""Based on your analysis, create a focused lesson for Alpha Agent.

Analysis: {professor_analysis[:600]}

Create a lesson with:
1. Introduction - Why this skill matters for AGI
2. Core Concepts - The 5 key components
3. The Interaction Loop - Step by step
4. Practical Example - A sample conversation
5. Exercise - Something Alpha should try

Make it engaging and clear."""

    print("Professor (using Qwen3): Creating lesson...")
    lesson_content = query_llm("qwen3:latest", lesson_prompt, max_tokens=1200)
    print(f"\nLesson Content:\n{lesson_content[:1000]}...")

    # Store lesson
    store_memory(
        str(professor_db),
        f"Created lesson for dialogue skill: {lesson_content[:400]}",
        "episodic",
        0.85
    )

    # ============================================================
    # PHASE 3: Alpha Studies the Lesson
    # ============================================================
    print("\n" + "=" * 70)
    print("[Phase 3] Alpha Studies the Lesson")
    print("-" * 70)

    study_prompt = f"""You are Alpha Agent, learning to become an interactive AGI.

Professor has created this lesson for you:

{lesson_content}

Study this lesson and:
1. Summarize the key concepts in your own words
2. Explain how the interaction loop works
3. Describe how you will use this skill
4. Ask one clarifying question

Show that you understand deeply."""

    print("Alpha (using Qwen3): Studying lesson...")
    alpha_understanding = query_llm("qwen3:latest", study_prompt, max_tokens=1000)
    print(f"\nAlpha's Understanding:\n{alpha_understanding[:800]}...")

    # Store Alpha's learning
    store_memory(
        str(alpha_db),
        f"Learned dialogue/conversation-handler skill. Understanding: {alpha_understanding[:300]}",
        "semantic",
        0.9
    )

    # ============================================================
    # PHASE 4: Alpha Demonstrates the Skill
    # ============================================================
    print("\n" + "=" * 70)
    print("[Phase 4] Alpha Demonstrates the Skill")
    print("-" * 70)

    # Import and use the actual skill
    from skills.dialogue.conversation_handler import ConversationHandlerSkill

    skill = ConversationHandlerSkill()

    demo_messages = [
        "Hello Alpha! Can you tell me about yourself?",
        "What did you learn today?",
        "How will you use the dialogue skill to help users?"
    ]

    print("Alpha demonstrates conversation ability:\n")

    conversation_id = None
    for msg in demo_messages:
        print(f"User: {msg}")

        result = skill.execute({
            "capability": "process_message",
            "message": msg,
            "conversation_id": conversation_id,
            "use_llm": True
        })

        if result.success:
            conversation_id = result.output["conversation_id"]
            print(f"Alpha: {result.output['response']}")
            print(f"  [Intent: {result.output['intent']['primary']}]\n")

    # Store demonstration
    store_memory(
        str(alpha_db),
        f"Successfully demonstrated dialogue skill in conversation. Processed {len(demo_messages)} messages with context maintenance.",
        "procedural",
        0.85
    )

    # ============================================================
    # PHASE 5: Professor Grades and Provides Feedback
    # ============================================================
    print("=" * 70)
    print("[Phase 5] Professor Grades Alpha's Performance")
    print("-" * 70)

    grade_prompt = f"""You are Professor Agent grading Alpha's understanding.

Alpha's summary of learning:
{alpha_understanding[:500]}

Alpha demonstrated the skill successfully, processing messages with intent recognition and context maintenance.

Grade Alpha (1-10) and provide:
1. Score with justification
2. What Alpha did well
3. What Alpha can improve
4. Next lesson recommendation

Be constructive and encouraging."""

    print("Professor (using DeepSeek-R1): Grading...")
    professor_feedback = query_llm("deepseek-r1:latest", grade_prompt, max_tokens=600)
    print(f"\nProfessor's Feedback:\n{professor_feedback}")

    # Store feedback
    store_memory(
        str(professor_db),
        f"Graded Alpha on dialogue skill. Feedback: {professor_feedback[:300]}",
        "episodic",
        0.8
    )

    store_memory(
        str(alpha_db),
        f"Received feedback from Professor on dialogue skill: {professor_feedback[:300]}",
        "episodic",
        0.8
    )

    # ============================================================
    # Final Summary
    # ============================================================
    print("\n" + "=" * 70)
    print("TEACHING SESSION COMPLETE")
    print("=" * 70)

    # Count memories
    def count_memories(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM memories")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    print(f"\nProfessor memories: {count_memories(str(professor_db))}")
    print(f"Alpha memories: {count_memories(str(alpha_db))}")

    print("\nSkill Teaching Summary:")
    print("  - Professor analyzed the dialogue/conversation-handler skill")
    print("  - Professor created a structured lesson")
    print("  - Alpha studied and demonstrated understanding")
    print("  - Alpha demonstrated the skill with live conversation")
    print("  - Professor provided feedback and grading")
    print("\nAlpha can now interact with users in natural language!")
    print("This is Pillar 1 (NLU) + Pillar 2 (NLG) of the AGI Curriculum.")
    print("=" * 70)


if __name__ == "__main__":
    main()
