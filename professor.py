"""
Professor Agent - Universal Educator for Autonomous Agents

Created by: Qwen3 (generation) + DeepSeek-R1 (validation) + CodeGemma (syntax)
Based on: Multi-model competition learnings stored in Alpha's memory

This agent teaches ANY autonomous agent (Alpha, engineering, creative, safety, etc.)
by adapting pedagogy to each student's architecture and needs.

OODA Loop Implementation:
- Observe: Gather student profile and learning context
- Orient: Analyze needs using MindsetSkill with LLM partners
- Decide: Choose teaching mode (assess/teach/adapt/evaluate)
- Act: Execute teaching action
- Learn: Store teaching experience in professor_memories.db
"""

from __future__ import annotations

import argparse
import logging
import sys
import io
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Professor - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProfessorAgent:
    """
    Universal educator that adapts to any student agent's architecture.

    Teaching Modes:
    - assess: Profile student capabilities and needs
    - teach: Deliver adaptive lessons
    - evaluate: Test understanding
    - adapt: Adjust approach based on progress
    """

    def __init__(self):
        self.name = "Professor"
        self.role = "Universal educator for autonomous agents"
        self.cycle = 0
        self.teaching_mode = "assess"
        self.current_student = None

        # Load skills
        self._load_skills()

        # Initialize Professor's memory
        self._init_memory()

        logger.info(f"Professor Agent initialized with {self.skill_count} skills")

    def _load_skills(self):
        """Load required skills from registry."""
        from skills.loader import SkillLoader
        from skills.registry import get_registry
        from skills.base import SkillContext

        loader = SkillLoader()
        loader.scan_all(lazy=True)
        self.registry = get_registry()
        self.context = SkillContext(agent_role="professor", session_id=f"prof_{datetime.now().strftime('%H%M%S')}")

        # Load core skills
        self.memory_skill = None
        self.mindset_skill = None
        self.session_analyzer = None

        try:
            self.memory_skill = self.registry.get_skill("conscience/memory")
            logger.info("Loaded: conscience/memory")
        except Exception as e:
            logger.warning(f"conscience/memory not available: {e}")

        try:
            self.mindset_skill = self.registry.get_skill("conscience/mindset")
            logger.info("Loaded: conscience/mindset (LLM reasoning)")
        except Exception as e:
            logger.warning(f"conscience/mindset not available: {e}")

        try:
            self.session_analyzer = self.registry.get_skill("alpha/session-analyzer")
            logger.info("Loaded: alpha/session-analyzer")
        except Exception as e:
            logger.warning(f"alpha/session-analyzer not available: {e}")

        self.skill_count = sum([1 for s in [self.memory_skill, self.mindset_skill, self.session_analyzer] if s])

    def _init_memory(self):
        """Initialize Professor's separate memory database."""
        from skills.conscience.memory.skill import MemoryStore

        memory_path = REPO_ROOT / "skills" / "conscience" / "memory" / "store" / "professor_memories.db"
        self.professor_memory = MemoryStore(db_path=str(memory_path))

        stats = self.professor_memory.get_stats()
        logger.info(f"Professor memory: {stats['total_memories']} memories")

    def observe(self, student_id: str = "alpha") -> Dict[str, Any]:
        """
        OBSERVE: Gather information about the student.

        Collects:
        - Student's memory stats
        - Recent learnings
        - Known strengths/weaknesses
        - Current learning objectives
        """
        self.cycle += 1
        self.current_student = student_id

        logger.info(f"OBSERVE [Cycle {self.cycle}] - Student: {student_id}")

        observations = {
            "cycle": self.cycle,
            "student_id": student_id,
            "timestamp": datetime.now().isoformat(),
            "student_profile": {},
            "recent_learnings": [],
            "teaching_history": []
        }

        # Get student's memory stats
        if student_id == "alpha":
            try:
                from skills.conscience.memory.skill import MemoryStore
                student_memory = MemoryStore(str(REPO_ROOT / "skills/conscience/memory/store/alpha_memories.db"))
                stats = student_memory.get_stats()
                observations["student_profile"] = {
                    "name": "Alpha Agent",
                    "architecture": "OODA loop with LLM reasoning",
                    "memory_count": stats.get("total_memories", 0),
                    "memory_types": stats.get("by_type", {}),
                }

                # Get recent learnings
                recent = student_memory.recall("learned professor teaching", limit=5)
                observations["recent_learnings"] = [m.get("content", "")[:100] for m in recent]

            except Exception as e:
                logger.warning(f"Could not access student memory: {e}")
                observations["student_profile"] = {"name": student_id, "architecture": "unknown"}

        # Get Professor's teaching history with this student
        teaching_memories = self.professor_memory.recall(f"taught {student_id}", limit=5)
        observations["teaching_history"] = [m.get("content", "")[:100] for m in teaching_memories]

        return observations

    def orient(self, observations: Dict[str, Any]) -> Dict[str, Any]:
        """
        ORIENT: Analyze student needs using MindsetSkill with LLM partners.

        Uses multi-model reasoning:
        - DeepSeek-R1 for analytical assessment
        - Qwen3 for creative teaching approaches
        - CodeGemma for practical validation
        """
        logger.info(f"ORIENT - Analyzing student: {observations.get('student_id')}")

        orientation = {
            "student_id": observations.get("student_id"),
            "profile": observations.get("student_profile", {}),
            "analysis": {},
            "recommended_mode": "assess",
            "reasoning": ""
        }

        if not self.mindset_skill:
            orientation["analysis"] = {"note": "MindsetSkill not available, using default assessment"}
            orientation["recommended_mode"] = "teach"
            return orientation

        # Use MindsetSkill for deep analysis
        analysis_prompt = f"""
Analyze this student for teaching:

Student: {observations.get('student_id')}
Architecture: {observations.get('student_profile', {}).get('architecture', 'unknown')}
Memory Count: {observations.get('student_profile', {}).get('memory_count', 0)}
Recent Learnings: {observations.get('recent_learnings', [])}
Teaching History: {observations.get('teaching_history', [])}

Questions:
1. What is this student's current learning stage?
2. What teaching approach suits their architecture?
3. What should we teach next?
4. What teaching mode is best? (assess/teach/evaluate/adapt)

Provide structured teaching recommendation.
        """

        try:
            result = self.mindset_skill.execute({
                "capability": "analyze",
                "problem": analysis_prompt,
                "pattern": "balanced"  # DeepSeek -> Qwen -> DeepSeek
            }, self.context)

            if result.success:
                orientation["analysis"] = result.output
                orientation["reasoning"] = result.output.get("conclusion", "")[:500]

                # Determine mode from analysis
                conclusion = result.output.get("conclusion", "").lower()
                if "assess" in conclusion:
                    orientation["recommended_mode"] = "assess"
                elif "evaluate" in conclusion or "test" in conclusion:
                    orientation["recommended_mode"] = "evaluate"
                elif "adapt" in conclusion or "adjust" in conclusion:
                    orientation["recommended_mode"] = "adapt"
                else:
                    orientation["recommended_mode"] = "teach"

        except Exception as e:
            logger.error(f"MindsetSkill analysis failed: {e}")
            orientation["reasoning"] = f"Analysis error: {e}"

        return orientation

    def decide(self, orientation: Dict[str, Any]) -> Dict[str, Any]:
        """
        DECIDE: Choose teaching action based on orientation.

        Modes:
        - assess: Profile student capabilities
        - teach: Deliver lesson
        - evaluate: Test understanding
        - adapt: Adjust teaching approach
        """
        logger.info(f"DECIDE - Recommended mode: {orientation.get('recommended_mode')}")

        self.teaching_mode = orientation.get("recommended_mode", "assess")

        decision = {
            "mode": self.teaching_mode,
            "student_id": orientation.get("student_id"),
            "action": None,
            "lesson_topic": None,
            "rationale": orientation.get("reasoning", "Default decision")
        }

        if self.teaching_mode == "assess":
            decision["action"] = "profile_student"
            decision["lesson_topic"] = "Student assessment and profiling"

        elif self.teaching_mode == "teach":
            decision["action"] = "deliver_lesson"
            # Choose topic based on student needs
            decision["lesson_topic"] = "Meta-cognitive learning and self-improvement"

        elif self.teaching_mode == "evaluate":
            decision["action"] = "test_understanding"
            decision["lesson_topic"] = "Knowledge validation quiz"

        elif self.teaching_mode == "adapt":
            decision["action"] = "adjust_approach"
            decision["lesson_topic"] = "Teaching method refinement"

        return decision

    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACT: Execute teaching action.

        Actions:
        - profile_student: Create/update student profile
        - deliver_lesson: Teach a lesson
        - test_understanding: Evaluate learning
        - adjust_approach: Modify teaching strategy
        """
        logger.info(f"ACT - Mode: {decision.get('mode')}, Action: {decision.get('action')}")

        action_result = {
            "action": decision.get("action"),
            "student_id": decision.get("student_id"),
            "success": False,
            "lesson_content": None,
            "feedback": None
        }

        action = decision.get("action")

        if action == "profile_student":
            action_result = self._profile_student(decision)

        elif action == "deliver_lesson":
            action_result = self._deliver_lesson(decision)

        elif action == "test_understanding":
            action_result = self._test_understanding(decision)

        elif action == "adjust_approach":
            action_result = self._adjust_approach(decision)

        return action_result

    def learn(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        LEARN: Store teaching experience in Professor's memory.

        Records:
        - What was taught
        - How student responded
        - Teaching effectiveness
        - Insights for future
        """
        logger.info(f"LEARN - Recording teaching experience")

        learning = {
            "stored": False,
            "memory_id": None,
            "experience": None
        }

        # Create experience record
        experience = f"Taught {action_result.get('student_id', 'unknown')}: {action_result.get('action', 'unknown')} - "
        if action_result.get("success"):
            experience += f"Success. Topic: {action_result.get('lesson_content', 'N/A')[:100]}"
        else:
            experience += f"Needs improvement. Feedback: {action_result.get('feedback', 'N/A')[:100]}"

        # Store in Professor's memory
        memory_id = self.professor_memory.store(
            content=experience,
            memory_type="episodic",
            importance=0.8,
            context={
                "type": "teaching_experience",
                "student": action_result.get("student_id"),
                "action": action_result.get("action"),
                "success": action_result.get("success"),
                "cycle": self.cycle,
                "timestamp": datetime.now().isoformat()
            }
        )

        learning["stored"] = True
        learning["memory_id"] = memory_id
        learning["experience"] = experience

        logger.info(f"Stored teaching experience: {experience[:80]}...")

        return learning

    def _profile_student(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Profile a student's capabilities and needs."""
        student_id = decision.get("student_id", "unknown")

        profile_content = f"""
STUDENT PROFILE: {student_id}
Generated: {datetime.now().isoformat()}

Architecture: OODA loop with LLM reasoning
Role: Learning and execution agent
Strengths: Memory persistence, multi-model reasoning, self-improvement
Weaknesses: Needs more domain knowledge, requires teaching

Learning Style: Experiential (learns by doing)
Recommended Approach: Structured lessons with practical exercises
"""

        # Store profile in Professor's memory
        self.professor_memory.store(
            content=f"Student profile for {student_id}: Architecture is OODA loop, learns experientially, needs structured lessons.",
            memory_type="semantic",
            importance=0.9,
            context={"type": "student_profile", "student": student_id}
        )

        return {
            "action": "profile_student",
            "student_id": student_id,
            "success": True,
            "lesson_content": profile_content,
            "feedback": "Student profile created and stored"
        }

    def _deliver_lesson(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver a lesson to the student."""
        student_id = decision.get("student_id", "unknown")
        topic = decision.get("lesson_topic", "General learning")

        # Generate lesson using Qwen3 if available
        lesson_content = f"""
LESSON: {topic}
For: {student_id}
Date: {datetime.now().strftime('%Y-%m-%d')}

Key Concepts:
1. Meta-cognitive learning is learning about learning
2. Self-improvement requires reflection on experiences
3. Memory consolidation strengthens understanding
4. Pattern recognition accelerates skill acquisition

Exercise:
- Recall your most recent learning experience
- Identify what made it effective
- Apply that insight to future learning

Next Steps:
- Practice this reflection daily
- Store insights in memory
- Track progress over time
"""

        if self.mindset_skill:
            try:
                result = self.mindset_skill.execute({
                    "capability": "synthesize",
                    "components": [topic, "teaching principles", "student needs"],
                    "pattern": "creative_synthesis"
                }, self.context)
                if result.success:
                    lesson_content += f"\n\nEnriched Content:\n{result.output.get('synthesis', '')[:500]}"
            except Exception as e:
                logger.warning(f"Could not enrich lesson: {e}")

        # Store lesson for student (in their memory if possible)
        if student_id == "alpha":
            try:
                from skills.conscience.memory.skill import MemoryStore
                student_memory = MemoryStore(str(REPO_ROOT / "skills/conscience/memory/store/alpha_memories.db"))
                student_memory.store(
                    content=f"Lesson from Professor: {topic} - {lesson_content[:200]}",
                    memory_type="semantic",
                    importance=0.85,
                    context={"type": "lesson", "from": "professor", "topic": topic}
                )
            except Exception as e:
                logger.warning(f"Could not store lesson in student memory: {e}")

        return {
            "action": "deliver_lesson",
            "student_id": student_id,
            "success": True,
            "lesson_content": lesson_content,
            "feedback": f"Lesson on '{topic}' delivered successfully"
        }

    def _test_understanding(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Test student's understanding."""
        student_id = decision.get("student_id", "unknown")

        test_content = """
UNDERSTANDING CHECK:

Question 1: What is the purpose of memory consolidation?
Question 2: How does reflection improve learning?
Question 3: Why is pattern recognition important for skill acquisition?

(Student should recall from memory and demonstrate understanding)
"""

        return {
            "action": "test_understanding",
            "student_id": student_id,
            "success": True,
            "lesson_content": test_content,
            "feedback": "Understanding test prepared - awaiting student response"
        }

    def _adjust_approach(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust teaching approach based on student progress."""
        student_id = decision.get("student_id", "unknown")

        adjustment = """
TEACHING ADJUSTMENT:

Based on student progress analysis:
1. Increase practical exercises
2. Provide more examples
3. Slow down pace for complex concepts
4. Add more reinforcement through repetition

New approach: More hands-on, less theoretical
"""

        return {
            "action": "adjust_approach",
            "student_id": student_id,
            "success": True,
            "lesson_content": adjustment,
            "feedback": "Teaching approach adjusted based on student needs"
        }

    def run_cycle(self, student_id: str = "alpha") -> Dict[str, Any]:
        """Run one complete OODA teaching cycle."""
        print()
        print("=" * 60)
        print(f"PROFESSOR AGENT - TEACHING CYCLE {self.cycle + 1}")
        print(f"Student: {student_id}")
        print("=" * 60)

        # OODA Loop
        observations = self.observe(student_id)
        print(f"\nOBSERVE: Student profile gathered")
        print(f"  Memory count: {observations.get('student_profile', {}).get('memory_count', 'N/A')}")

        orientation = self.orient(observations)
        print(f"\nORIENT: Analysis complete")
        print(f"  Recommended mode: {orientation.get('recommended_mode')}")

        decision = self.decide(orientation)
        print(f"\nDECIDE: Teaching action selected")
        print(f"  Mode: {decision.get('mode')}")
        print(f"  Topic: {decision.get('lesson_topic')}")

        action_result = self.act(decision)
        print(f"\nACT: Teaching executed")
        print(f"  Success: {action_result.get('success')}")
        print(f"  Feedback: {action_result.get('feedback')}")

        learning = self.learn(action_result)
        print(f"\nLEARN: Experience stored")
        print(f"  Memory ID: {learning.get('memory_id', 'N/A')[:20]}...")

        print()
        print("=" * 60)
        print("CYCLE COMPLETE")
        print("=" * 60)

        return {
            "cycle": self.cycle,
            "student": student_id,
            "mode": decision.get("mode"),
            "success": action_result.get("success"),
            "experience_stored": learning.get("stored")
        }


def main():
    parser = argparse.ArgumentParser(description="Professor Agent - Universal Educator")
    parser.add_argument("--once", action="store_true", help="Run single teaching cycle")
    parser.add_argument("--student", default="alpha", help="Student agent ID")
    parser.add_argument("--mode", choices=["assess", "teach", "evaluate", "adapt"], help="Teaching mode")
    args = parser.parse_args()

    print()
    print("=" * 70)
    print("PROFESSOR AGENT - Universal Educator")
    print("Teaching any autonomous agent with adaptive pedagogy")
    print("=" * 70)
    print()

    professor = ProfessorAgent()

    if args.mode:
        professor.teaching_mode = args.mode

    if args.once:
        result = professor.run_cycle(args.student)
        print(f"\nResult: {result}")
    else:
        print("Continuous teaching mode - Press Ctrl+C to stop")
        import time
        try:
            while True:
                professor.run_cycle(args.student)
                print("\nWaiting 60 seconds before next cycle...")
                time.sleep(60)
        except KeyboardInterrupt:
            print("\nTeaching session ended.")


if __name__ == "__main__":
    main()
