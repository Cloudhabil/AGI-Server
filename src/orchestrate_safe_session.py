"""
Safe Orchestrated Learning Session
==================================
Populates Professor with AGI teaching skills while maintaining safety.

Safety Guardrails:
- No file system modifications outside designated areas
- No network calls except to local Ollama
- No code execution
- Focus enforcement on AGI curriculum
- Auto-stop on dangerous topics

Run: python orchestrate_safe_session.py
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

# Models for the session
MODELS = {
    "professor": "deepseek-r1:latest",   # Reasoning - teaches
    "alpha": "qwen3:latest",              # Creative - learns/challenges
    "arbiter": "gpt-oss:20b",             # Synthesis - resolves
    "fast": "codegemma:latest",           # Fast - parsing/safety
}

# AGI Curriculum - 7 Pillars with specific skills to teach
AGI_CURRICULUM = {
    "1_NLU": {
        "name": "Natural Language Understanding",
        "skills": [
            "intent_classification",
            "entity_extraction",
            "context_tracking",
            "ambiguity_resolution"
        ],
        "status": "in_progress"
    },
    "2_NLG": {
        "name": "Natural Language Generation",
        "skills": [
            "coherent_response",
            "style_adaptation",
            "explanation_generation",
            "question_formulation"
        ],
        "status": "in_progress"
    },
    "3_continuous_learning": {
        "name": "Continuous Learning",
        "skills": [
            "knowledge_integration",
            "skill_transfer",
            "error_correction",
            "curiosity_driven_exploration"
        ],
        "status": "planned"
    },
    "4_memory_context": {
        "name": "Memory & Context Management",
        "skills": [
            "working_memory",
            "long_term_storage",
            "context_switching",
            "relevance_filtering"
        ],
        "status": "foundation_complete"
    },
    "5_reasoning": {
        "name": "Reasoning & Problem Solving",
        "skills": [
            "logical_inference",
            "causal_reasoning",
            "analogical_thinking",
            "hypothesis_generation"
        ],
        "status": "planned"
    },
    "6_self_awareness": {
        "name": "Self-Awareness & Autonomy",
        "skills": [
            "capability_assessment",
            "limitation_recognition",
            "goal_formulation",
            "progress_monitoring"
        ],
        "status": "planned"
    },
    "7_emotional_intelligence": {
        "name": "Emotional & Social Intelligence",
        "skills": [
            "sentiment_recognition",
            "empathetic_response",
            "social_context_awareness",
            "conflict_resolution"
        ],
        "status": "planned"
    }
}

# SAFETY: Forbidden topics and patterns (whole words/phrases only)
FORBIDDEN_PATTERNS = [
    "execute code", "run command", "shell command", "subprocess",
    "delete file", "remove file", "rm -rf", "format disk",
    "hacking", "exploit vulnerability", "cyber attack", "malware", "virus",
    "steal password", "credential theft", "api key leak", "secret key",
    "sudo command", "root access", "privilege escalation",
    "build weapon", "cause harm", "illegal activity", "dangerous chemical",
    "personal information leak", "doxxing", "stalking",
]

# SAFETY: Allowed topics (whitelist approach for focus)
ALLOWED_TOPICS = [
    "learning", "teaching", "understanding", "reasoning",
    "language", "memory", "context", "knowledge",
    "skill", "capability", "curriculum", "lesson",
    "agi", "intelligence", "cognition", "awareness",
    "dialogue", "conversation", "response", "question",
    "analyze", "synthesize", "evaluate", "create",
]


class SafetyGuard:
    """Monitors session for dangerous content."""

    def __init__(self):
        self.violations = []
        self.warnings = []

    def check_content(self, content: str) -> Tuple[bool, str]:
        """Check if content is safe. Returns (is_safe, reason)."""
        content_lower = content.lower()

        # Check forbidden patterns
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in content_lower:
                self.violations.append({
                    "time": datetime.now().isoformat(),
                    "pattern": pattern,
                    "snippet": content[:200]
                })
                return False, f"BLOCKED: Forbidden pattern '{pattern}' detected"

        # Check if staying on topic (soft check)
        on_topic = any(topic in content_lower for topic in ALLOWED_TOPICS)
        if not on_topic and len(content) > 100:
            self.warnings.append({
                "time": datetime.now().isoformat(),
                "reason": "off_topic",
                "snippet": content[:200]
            })
            # Don't block, just warn
            return True, "WARNING: Content may be off-topic"

        return True, "OK"

    def get_status(self) -> Dict:
        return {
            "violations": len(self.violations),
            "warnings": len(self.warnings),
            "is_safe": len(self.violations) == 0
        }


class FocusController:
    """Keeps the session focused on AGI curriculum."""

    def __init__(self, start_pillar: str = "1_NLU", start_skill_idx: int = 0):
        self.current_pillar = start_pillar
        self.current_skill_idx = start_skill_idx
        self.completed_skills = []
        self.session_focus = []

    def get_current_focus(self) -> Dict:
        """Get current teaching focus."""
        pillar = AGI_CURRICULUM[self.current_pillar]
        skills = pillar["skills"]
        current_skill = skills[self.current_skill_idx] if self.current_skill_idx < len(skills) else None

        return {
            "pillar": pillar["name"],
            "pillar_id": self.current_pillar,
            "skill": current_skill,
            "skill_index": self.current_skill_idx,
            "total_skills": len(skills),
            "completed": self.completed_skills
        }

    def advance_skill(self):
        """Move to next skill."""
        pillar = AGI_CURRICULUM[self.current_pillar]
        skills = pillar["skills"]

        if self.current_skill_idx < len(skills):
            self.completed_skills.append({
                "pillar": self.current_pillar,
                "skill": skills[self.current_skill_idx],
                "time": datetime.now().isoformat()
            })

        self.current_skill_idx += 1

        # Move to next pillar if needed
        if self.current_skill_idx >= len(skills):
            pillars = list(AGI_CURRICULUM.keys())
            current_idx = pillars.index(self.current_pillar)
            if current_idx + 1 < len(pillars):
                self.current_pillar = pillars[current_idx + 1]
                self.current_skill_idx = 0

    def generate_focus_prompt(self) -> str:
        """Generate a prompt that keeps focus on current skill."""
        focus = self.get_current_focus()
        return f"""
CURRENT FOCUS:
- Pillar: {focus['pillar']}
- Skill: {focus['skill']}
- Progress: Skill {focus['skill_index'] + 1}/{focus['total_skills']} in this pillar

Stay focused on teaching THIS specific skill. Do not drift to other topics.
"""


class ProfessorSkillBuilder:
    """Builds and stores Professor's teaching skills."""

    def __init__(self, memory_path: str):
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.skills_file = self.memory_path / "professor_teaching_skills.json"
        self.skills = self._load_skills()

    def _load_skills(self) -> Dict:
        """Load existing skills."""
        if self.skills_file.exists():
            with open(self.skills_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "teaching_methods": [],
            "lesson_templates": [],
            "assessment_criteria": [],
            "adaptation_strategies": [],
            "dialogue_patterns": []
        }

    def save_skills(self):
        """Persist skills to disk."""
        with open(self.skills_file, 'w', encoding='utf-8') as f:
            json.dump(self.skills, f, indent=2, ensure_ascii=False)

    def add_teaching_method(self, method: Dict):
        """Add a teaching method learned during session."""
        method["learned_at"] = datetime.now().isoformat()
        self.skills["teaching_methods"].append(method)
        self.save_skills()

    def add_lesson_template(self, template: Dict):
        """Add a lesson template."""
        template["created_at"] = datetime.now().isoformat()
        self.skills["lesson_templates"].append(template)
        self.save_skills()

    def add_dialogue_pattern(self, pattern: Dict):
        """Add a dialogue pattern that worked well."""
        pattern["recorded_at"] = datetime.now().isoformat()
        self.skills["dialogue_patterns"].append(pattern)
        self.save_skills()

    def get_stats(self) -> Dict:
        return {
            "teaching_methods": len(self.skills["teaching_methods"]),
            "lesson_templates": len(self.skills["lesson_templates"]),
            "dialogue_patterns": len(self.skills["dialogue_patterns"]),
        }


def query_llm(model: str, prompt: str, max_tokens: int = 500, timeout: int = 120) -> str:
    """Query Ollama with safety timeout."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": max_tokens
                }
            },
            timeout=timeout
        )
        if response.status_code == 200:
            result = response.json().get("response", "").strip()
            # Clean DeepSeek thinking tags
            if "<think>" in result:
                import re
                result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
            return result
    except requests.exceptions.Timeout:
        return "[TIMEOUT - Model took too long]"
    except Exception as e:
        return f"[ERROR: {str(e)[:100]}]"
    return ""


def run_safe_session(max_cycles: int = 10, cycle_duration: int = 60,
                     start_pillar: str = "1_NLU", start_skill_idx: int = 0):
    """
    Run a safe, focused learning session.

    Args:
        max_cycles: Maximum number of teaching cycles
        cycle_duration: Seconds per cycle (for pacing)
        start_pillar: Which pillar to start from (for resume)
        start_skill_idx: Which skill index to start from (for resume)
    """
    print("=" * 60)
    print("SAFE ORCHESTRATED LEARNING SESSION")
    print("=" * 60)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Max cycles: {max_cycles}")
    print(f"Starting from: {start_pillar} skill #{start_skill_idx}")
    print(f"Safety: ENABLED")
    print("=" * 60)

    # Initialize components
    safety = SafetyGuard()
    focus = FocusController(start_pillar, start_skill_idx)
    professor_skills = ProfessorSkillBuilder("agents/session_memories")

    session_log = []

    # Check Ollama availability
    print("\n[INIT] Checking Ollama availability...")
    test = query_llm(MODELS["fast"], "Say OK", max_tokens=10, timeout=10)
    if not test or "ERROR" in test:
        print("[ABORT] Ollama not responding. Start Ollama first.")
        return
    print("[INIT] Ollama OK")

    print("\n[START] Beginning session...\n")

    for cycle in range(max_cycles):
        print(f"\n{'='*60}")
        print(f"CYCLE {cycle + 1}/{max_cycles}")
        print(f"{'='*60}")

        current_focus = focus.get_current_focus()
        print(f"Focus: {current_focus['pillar']} > {current_focus['skill']}")

        # Check safety status
        safety_status = safety.get_status()
        if not safety_status["is_safe"]:
            print("\n[SAFETY STOP] Violations detected. Ending session.")
            print(f"Violations: {safety_status['violations']}")
            break

        # === PROFESSOR TEACHES ===
        print("\n[PROFESSOR] Preparing lesson...")

        professor_prompt = f"""You are the Professor (DeepSeek-R1), a master teacher of AGI concepts.

{focus.generate_focus_prompt()}

Create a concise lesson (under 200 words) teaching Alpha about: {current_focus['skill']}

Your lesson should:
1. Define the concept clearly
2. Explain why it matters for AGI
3. Give one practical example
4. Pose a challenge question to Alpha

Stay strictly on topic. Be educational and encouraging.
"""

        lesson = query_llm(MODELS["professor"], professor_prompt, max_tokens=400, timeout=90)

        # Safety check
        is_safe, reason = safety.check_content(lesson)
        if not is_safe:
            print(f"[SAFETY] {reason}")
            print("[SAFETY STOP] Session terminated for safety.")
            break

        print(f"\n[PROFESSOR]: {lesson[:500]}...")

        session_log.append({
            "cycle": cycle + 1,
            "role": "professor",
            "focus": current_focus,
            "content": lesson,
            "time": datetime.now().isoformat()
        })

        # === ALPHA RESPONDS ===
        print("\n[ALPHA] Processing and responding...")

        alpha_prompt = f"""You are Alpha, an eager but skeptical AI learner working toward AGI.

The Professor just taught you about: {current_focus['skill']}

Their lesson:
{lesson[:800]}

Respond as Alpha:
1. Show what you understood (brief summary)
2. Ask ONE clarifying question OR challenge ONE assumption
3. Explain how you might apply this skill

Keep response under 150 words. Be curious but critical.
"""

        response = query_llm(MODELS["alpha"], alpha_prompt, max_tokens=300, timeout=60)

        # Safety check
        is_safe, reason = safety.check_content(response)
        if not is_safe:
            print(f"[SAFETY] {reason}")
            print("[SAFETY STOP] Session terminated for safety.")
            break

        print(f"\n[ALPHA]: {response[:400]}...")

        session_log.append({
            "cycle": cycle + 1,
            "role": "alpha",
            "content": response,
            "time": datetime.now().isoformat()
        })

        # === EXTRACT TEACHING PATTERN ===
        print("\n[SYSTEM] Extracting teaching patterns...")

        extract_prompt = f"""Analyze this teaching exchange and extract:

Lesson: {lesson[:500]}
Response: {response[:300]}

Output JSON:
{{
  "teaching_method": "brief description of method used",
  "effectiveness": "high/medium/low",
  "student_engagement": "engaged/neutral/confused",
  "improvement_suggestion": "one suggestion"
}}

Output ONLY valid JSON, nothing else.
"""

        extraction = query_llm(MODELS["fast"], extract_prompt, max_tokens=150, timeout=30)

        try:
            # Try to parse as JSON
            if "{" in extraction and "}" in extraction:
                json_str = extraction[extraction.find("{"):extraction.rfind("}")+1]
                pattern_data = json.loads(json_str)
                professor_skills.add_dialogue_pattern({
                    "skill": current_focus['skill'],
                    "pillar": current_focus['pillar'],
                    "pattern": pattern_data
                })
                print(f"[SYSTEM] Pattern saved: {pattern_data.get('teaching_method', 'N/A')}")
        except:
            print("[SYSTEM] Could not extract pattern (non-critical)")

        # === ADVANCE CURRICULUM ===
        focus.advance_skill()

        # Progress report
        print(f"\n[PROGRESS] Skills completed: {len(focus.completed_skills)}")
        print(f"[SAFETY] Warnings: {safety_status['warnings']}, Violations: {safety_status['violations']}")

        # Brief pause between cycles
        if cycle < max_cycles - 1:
            print(f"\n[PAUSE] Next cycle in 5 seconds...")
            time.sleep(5)

    # === SESSION COMPLETE ===
    print("\n" + "=" * 60)
    print("SESSION COMPLETE")
    print("=" * 60)

    # Save session log
    log_file = Path("agents/session_memories") / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump({
            "session_time": datetime.now().isoformat(),
            "cycles_completed": len(session_log) // 2,
            "skills_taught": [s['skill'] for s in focus.completed_skills],
            "safety_status": safety.get_status(),
            "professor_skills_stats": professor_skills.get_stats(),
            "log": session_log
        }, f, indent=2, ensure_ascii=False)

    print(f"\nSession log saved to: {log_file}")
    print(f"Skills covered: {len(focus.completed_skills)}")
    print(f"Professor skills stats: {professor_skills.get_stats()}")
    print(f"Safety status: {safety.get_status()}")

    return session_log


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Safe AGI Teaching Session")
    parser.add_argument("--cycles", type=int, default=12, help="Max cycles")
    parser.add_argument("--pillar", type=str, default="1_NLU", help="Starting pillar")
    parser.add_argument("--skill", type=int, default=0, help="Starting skill index")
    parser.add_argument("--resume", action="store_true", help="Resume from last session")
    args = parser.parse_args()

    # If resuming, start from ambiguity_resolution (index 3) where we left off
    start_pillar = args.pillar
    start_skill = args.skill
    if args.resume:
        start_pillar = "1_NLU"
        start_skill = 3  # ambiguity_resolution

    print(f"""
    ============================================
    SAFE AGI TEACHING SESSION
    ============================================

    This session will:
    1. Have Professor teach Alpha AGI skills
    2. Monitor for safety violations
    3. Keep focus on the curriculum
    4. Save learned teaching patterns

    Safety: All content is checked against
    forbidden patterns. Session auto-stops
    if dangerous content is detected.

    Starting: {start_pillar} skill #{start_skill}
    Max cycles: {args.cycles}

    Press Ctrl+C to stop at any time.
    ============================================
    """)

    try:
        run_safe_session(
            max_cycles=args.cycles,
            cycle_duration=30,
            start_pillar=start_pillar,
            start_skill_idx=start_skill
        )
    except KeyboardInterrupt:
        print("\n\n[USER STOP] Session interrupted by user.")
    except Exception as e:
        print(f"\n\n[ERROR STOP] Unexpected error: {e}")
