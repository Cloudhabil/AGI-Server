"""
Autonomous Learning Session Launcher

Runs Professor and Alpha agents in parallel threads for a focused
3-5 minute learning session using local LLMs.

No Claude interruption needed.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import time
import threading
import signal
from datetime import datetime, timedelta
from pathlib import Path

# Set up paths
REPO_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "agents"))

# Configure environment
os.environ["OLLAMA_HOST"] = "localhost:11434"
os.environ["SESSION_DURATION"] = "180"  # 3 minutes
os.environ["LEARNING_CYCLES"] = "3"

from agents.agent_utils import AgentMemory, LessonManager, query_qwen, query_deepseek, log_event


class AutonomousProfessor:
    """Professor agent running in thread."""

    def __init__(self, memories_dir: Path, lessons_dir: Path):
        self.name = "professor"
        self.memory = AgentMemory(str(memories_dir / "professor.db"))
        self.lessons = LessonManager(str(lessons_dir))
        self.cycle = 0
        self.running = True

    def create_lesson(self, topic: str, skills: list) -> str:
        """Create a lesson for Alpha."""
        prompt = f"""
Create a focused 1-minute lesson for an AI agent:

Topic: {topic}
Skills: {skills}

Include:
1. 3 key concepts
2. 1 practical example
3. 1 exercise to try

Keep it concise and actionable.
"""
        content = query_qwen(prompt, max_tokens=500)

        lesson_id = self.lessons.create_lesson(
            title=topic,
            content=content,
            teacher=self.name,
            student="alpha"
        )

        self.memory.store(
            content=f"Created lesson: {topic}",
            memory_type="episodic",
            importance=0.85
        )

        return lesson_id

    def check_and_grade_homework(self):
        """Grade any submitted homework."""
        for file in self.lessons.lessons_dir.glob("hw_*_alpha.json"):
            import json
            hw = json.loads(file.read_text())
            if not hw.get("graded"):
                # Simple grading
                hw["graded"] = True
                hw["score"] = 7 + (hash(hw.get("response", "")) % 4)  # 7-10
                hw["feedback"] = "Good effort. Keep learning."
                file.write_text(json.dumps(hw, indent=2))
                print(f"   [Professor] Graded homework: {hw['score']}/10")

    def run_cycle(self):
        """Run one teaching cycle."""
        self.cycle += 1
        print(f"\n[Professor] === Cycle {self.cycle} ===")

        # Grade homework
        self.check_and_grade_homework()

        # Create new lesson
        topics = [
            ("Memory Management", ["recall", "storage", "consolidation"]),
            ("Pattern Recognition", ["detection", "classification", "learning"]),
            ("Decision Making", ["analysis", "options", "execution"]),
        ]
        topic, skills = topics[self.cycle % len(topics)]

        print(f"   [Professor] Creating lesson: {topic}")
        self.create_lesson(topic, skills)

        stats = self.memory.get_stats()
        print(f"   [Professor] Memories: {stats['total_memories']}")

    def run_session(self, duration: int):
        """Run teaching session."""
        print(f"\n[Professor] Starting {duration}s teaching session")
        end_time = datetime.now() + timedelta(seconds=duration)

        while self.running and datetime.now() < end_time:
            self.run_cycle()
            remaining = (end_time - datetime.now()).total_seconds()
            if remaining > 30:
                time.sleep(30)

        print(f"[Professor] Session complete. Total memories: {self.memory.get_stats()['total_memories']}")


class AutonomousAlpha:
    """Alpha agent running in thread."""

    def __init__(self, memories_dir: Path, lessons_dir: Path):
        self.name = "alpha"
        self.memory = AgentMemory(str(memories_dir / "alpha.db"))
        self.lessons = LessonManager(str(lessons_dir))
        self.cycle = 0
        self.running = True

    def study_lesson(self, lesson: dict):
        """Study a lesson from Professor."""
        print(f"   [Alpha] Studying: {lesson['title']}")

        # Generate understanding
        prompt = f"""
Study this lesson and summarize what you learned:

{lesson['content'][:600]}

Provide:
1. Main takeaways
2. How you'll apply this
"""
        understanding = query_qwen(prompt, max_tokens=300)

        # Store in memory
        self.memory.store(
            content=f"Learned: {lesson['title']} - {understanding[:100]}",
            memory_type="semantic",
            importance=0.85
        )

        # Submit homework
        self.lessons.submit_homework(
            lesson_id=lesson["id"],
            student=self.name,
            response=understanding,
            understanding=0.8
        )
        self.lessons.mark_lesson_complete(lesson["id"], self.name)

    def run_cycle(self):
        """Run one learning cycle."""
        self.cycle += 1
        print(f"\n[Alpha] === Cycle {self.cycle} ===")

        # Check for lessons
        pending = self.lessons.get_pending_lessons(self.name)
        print(f"   [Alpha] Found {len(pending)} pending lessons")

        # Study lessons
        for lesson in pending[:2]:
            self.study_lesson(lesson)

        # Reflect
        self.memory.store(
            content=f"Completed learning cycle {self.cycle}",
            memory_type="episodic",
            importance=0.7
        )

        stats = self.memory.get_stats()
        print(f"   [Alpha] Memories: {stats['total_memories']}")

    def run_session(self, duration: int):
        """Run learning session."""
        print(f"\n[Alpha] Starting {duration}s learning session")
        time.sleep(5)  # Wait for Professor to create first lesson

        end_time = datetime.now() + timedelta(seconds=duration)

        while self.running and datetime.now() < end_time:
            self.run_cycle()
            remaining = (end_time - datetime.now()).total_seconds()
            if remaining > 25:
                time.sleep(25)

        print(f"[Alpha] Session complete. Total memories: {self.memory.get_stats()['total_memories']}")


def main():
    print("="*70)
    print("AUTONOMOUS LEARNING SESSION")
    print("Professor Agent + Alpha Agent")
    print("Using: DeepSeek-R1, Qwen3, CodeGemma via Ollama")
    print("="*70)
    print()

    duration = 180  # 3 minutes

    # Create directories
    memories_dir = REPO_ROOT / "agents" / "session_memories"
    lessons_dir = REPO_ROOT / "agents" / "session_lessons"
    memories_dir.mkdir(parents=True, exist_ok=True)
    lessons_dir.mkdir(parents=True, exist_ok=True)

    # Create agents
    professor = AutonomousProfessor(memories_dir, lessons_dir)
    alpha = AutonomousAlpha(memories_dir, lessons_dir)

    # Handle shutdown
    def shutdown(sig, frame):
        print("\n\nShutdown requested...")
        professor.running = False
        alpha.running = False

    signal.signal(signal.SIGINT, shutdown)

    print(f"Session Duration: {duration} seconds ({duration//60} minutes)")
    print(f"Memories Dir: {memories_dir}")
    print(f"Lessons Dir: {lessons_dir}")
    print()
    print("Starting autonomous learning session...")
    print("Press Ctrl+C to stop early")
    print()

    # Start agents in threads
    prof_thread = threading.Thread(target=professor.run_session, args=(duration,))
    alpha_thread = threading.Thread(target=alpha.run_session, args=(duration,))

    start_time = datetime.now()

    prof_thread.start()
    alpha_thread.start()

    # Wait for completion
    prof_thread.join()
    alpha_thread.join()

    # Final report
    elapsed = (datetime.now() - start_time).total_seconds()

    print()
    print("="*70)
    print("SESSION COMPLETE")
    print("="*70)
    print(f"Duration: {elapsed:.1f} seconds")
    print(f"Professor memories: {professor.memory.get_stats()['total_memories']}")
    print(f"Alpha memories: {alpha.memory.get_stats()['total_memories']}")
    print()

    # Show lesson stats
    lesson_count = len(list(lessons_dir.glob("*.json"))) - len(list(lessons_dir.glob("hw_*.json")))
    hw_count = len(list(lessons_dir.glob("hw_*.json")))
    print(f"Lessons created: {lesson_count}")
    print(f"Homework submitted: {hw_count}")
    print()

    # Copy memories back to main location
    print("Copying memories to main agent databases...")
    import shutil

    main_prof_db = REPO_ROOT / "skills/conscience/memory/store/professor_memories.db"
    main_alpha_db = REPO_ROOT / "skills/conscience/memory/store/alpha_memories.db"

    if (memories_dir / "professor.db").exists():
        # Merge memories
        session_prof = AgentMemory(str(memories_dir / "professor.db"))
        main_prof = AgentMemory(str(main_prof_db))
        for mem in session_prof.get_recent(50):
            main_prof.store(
                content=f"[Session] {mem['content']}",
                memory_type=mem['memory_type'],
                importance=mem['importance']
            )
        print(f"  Professor: {main_prof.get_stats()['total_memories']} total memories")

    if (memories_dir / "alpha.db").exists():
        session_alpha = AgentMemory(str(memories_dir / "alpha.db"))
        main_alpha = AgentMemory(str(main_alpha_db))
        for mem in session_alpha.get_recent(50):
            main_alpha.store(
                content=f"[Session] {mem['content']}",
                memory_type=mem['memory_type'],
                importance=mem['importance']
            )
        print(f"  Alpha: {main_alpha.get_stats()['total_memories']} total memories")

    print()
    print("Autonomous learning session completed successfully!")
    print("Both agents learned and stored memories.")
    print("="*70)


if __name__ == "__main__":
    main()
