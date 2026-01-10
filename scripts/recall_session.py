"""
Session Recall - Restore Context from Previous Sessions

Run this at the start of any conversation with Claude to restore
memory of what we've built together.

Usage: python recall_session.py
"""

import sqlite3
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent


def recall_memories():
    """Recall key memories from both agents."""
    print("=" * 70)
    print("SESSION RECALL: Restoring Context")
    print("=" * 70)
    print()

    # Alpha memories
    alpha_db = REPO_ROOT / "skills/conscience/memory/store/alpha_memories.db"
    prof_db = REPO_ROOT / "skills/conscience/memory/store/professor_memories.db"

    memories = {"alpha": [], "professor": []}

    if alpha_db.exists():
        conn = sqlite3.connect(str(alpha_db))

        # Identity memories (most important)
        cursor = conn.execute(
            "SELECT content FROM memories WHERE memory_type='identity' ORDER BY importance DESC LIMIT 5"
        )
        for row in cursor:
            memories["alpha"].append(("identity", row[0]))

        # Recent semantic (knowledge)
        cursor = conn.execute(
            "SELECT content FROM memories WHERE memory_type='semantic' ORDER BY timestamp DESC LIMIT 10"
        )
        for row in cursor:
            memories["alpha"].append(("semantic", row[0]))

        # Recent episodic (experiences)
        cursor = conn.execute(
            "SELECT content FROM memories WHERE memory_type='episodic' ORDER BY timestamp DESC LIMIT 5"
        )
        for row in cursor:
            memories["alpha"].append(("episodic", row[0]))

        total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        conn.close()

        print(f"[ALPHA AGENT] - {total} total memories")
        print("-" * 50)
        for mtype, content in memories["alpha"][:10]:
            short = content[:80] + "..." if len(content) > 80 else content
            print(f"  [{mtype}] {short}")
        print()

    if prof_db.exists():
        conn = sqlite3.connect(str(prof_db))

        cursor = conn.execute(
            "SELECT content FROM memories WHERE memory_type='semantic' ORDER BY timestamp DESC LIMIT 10"
        )
        for row in cursor:
            memories["professor"].append(("semantic", row[0]))

        total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        conn.close()

        print(f"[PROFESSOR AGENT] - {total} total memories")
        print("-" * 50)
        for mtype, content in memories["professor"][:8]:
            short = content[:80] + "..." if len(content) > 80 else content
            print(f"  [{mtype}] {short}")
        print()

    return memories


def recall_recent_work():
    """Show recently modified files."""
    print("=" * 70)
    print("RECENT WORK")
    print("=" * 70)
    print()

    key_files = [
        "expectations_dialogue.py",
        "teach_dialogue_skill.py",
        "skills/dialogue/conversation_handler.py",
        "curriculum/AGI_CURRICULUM.md",
        "professor.py",
        "start_autonomous_learning.py",
        "agents/agent_utils.py",
    ]

    for f in key_files:
        path = REPO_ROOT / f
        if path.exists():
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            print(f"  {f:<45} - Modified: {mtime.strftime('%Y-%m-%d %H:%M')}")

    print()


def recall_journey():
    """Print the journey summary."""
    print("=" * 70)
    print("OUR JOURNEY TOGETHER")
    print("=" * 70)
    print("""
PHASE 1: Foundation
  - Reconnected with H-Net cognitive system
  - Explored AGI components in codebase (43+ found)
  - Enhanced Alpha Agent with separate memory

PHASE 2: Teaching Infrastructure
  - Created Professor Agent (universal teacher)
  - Multi-model competition: DeepSeek vs Qwen vs CodeGemma
  - Established teaching loop: Professor -> Alpha -> Feedback

PHASE 3: Autonomous Learning
  - Docker/Kubernetes containerized agents
  - 3-5 minute focused learning sessions
  - No Claude interruption needed

PHASE 4: AGI Curriculum
  - Defined 7 Pillars of Interactive AGI
  - Created 20 skills Professor must teach
  - Implementation phases (12 weeks)

PHASE 5: First AGI Capability
  - Built dialogue/conversation-handler skill
  - NLU + NLG (Pillars 1 & 2)
  - Alpha can now converse in natural language

PHASE 6: Skeptical Learning (Current)
  - Professor-Alpha expectations dialogue
  - Fixed: Alpha now challenges assumptions
  - Fixed: Agreement summary prevents repetition
  - Fixed: Continue loop for truncated messages

NEXT STEPS:
  - Run improved skeptical dialogue
  - Build remaining AGI skills (18 more)
  - Test autonomous learning with new prompts
""")


def main():
    print()
    print("*" * 70)
    print("*  WELCOME BACK - Restoring Session Context")
    print("*" * 70)
    print()

    recall_memories()
    recall_recent_work()
    recall_journey()

    print("=" * 70)
    print("Context restored. Ready to continue building AGI.")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
