"""
Store Critical Session Context in Alpha's Memory

This script stores the key learnings, decisions, and next steps from
the meta-cognitive evaluation session in Alpha Agent's memory database.

Critical for continuity across sessions - both Claude and Alpha need to
remember what was discovered and what comes next.
"""
# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from datetime import datetime
from skills.conscience.memory.skill import MemoryStore
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent

def main():
    print("=" * 70)
    print("STORING SESSION CONTEXT IN ALPHA'S MEMORY")
    print("=" * 70)
    print()

    # Load Alpha's memory database
    alpha_memory_path = REPO_ROOT / "skills" / "conscience" / "memory" / "store" / "alpha_memories.db"
    alpha_memory = MemoryStore(db_path=str(alpha_memory_path))

    print(f"Alpha Memory: {alpha_memory_path}")
    print()

    # Get current stats
    stats_before = alpha_memory.get_stats()
    print(f"Memories before: {stats_before['total_memories']}")
    print(f"  By type: {stats_before['by_type']}")
    print()

    # Critical memories to store
    memories = [
        # Identity: Multi-agent system
        {
            "content": "I am part of a multi-agent cognitive system. The next agent to be created is Professor Agent, who will teach and guide me.",
            "memory_type": "identity",
            "importance": 1.0,
            "context": {
                "type": "multi_agent_architecture",
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Semantic: New skills created
        {
            "content": "Three meta-cognitive skills were created for autonomous operation: alpha/session-analyzer (analyzes conversations), alpha/skill-generator (generates skills autonomously), alpha/adaptive-operation (intelligent timing)",
            "memory_type": "semantic",
            "importance": 0.95,
            "context": {
                "type": "skill_creation",
                "skills": ["alpha/session-analyzer", "alpha/skill-generator", "alpha/adaptive-operation"],
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Semantic: Agent-generator skill
        {
            "content": "Agent-generator skill (alpha/agent-generator) enables creating complete autonomous agents with separate memory databases, specialized skills, and defined roles. Used to create Professor Agent and future agents.",
            "memory_type": "semantic",
            "importance": 0.95,
            "context": {
                "type": "agent_generation_capability",
                "first_use": "Professor Agent creation",
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Semantic: Professor Agent specification
        {
            "content": "Professor Agent: Role is teacher and guide. Core capabilities include curriculum design, knowledge assessment, Socratic questioning, progress tracking. Uses memory database professor_memories.db. Will teach Alpha Agent through collaborative learning pattern.",
            "memory_type": "semantic",
            "importance": 0.9,
            "context": {
                "type": "next_agent_specification",
                "agent_name": "Professor",
                "skill_dependencies": [
                    "conscience/memory",
                    "conscience/mindset",
                    "alpha/session-analyzer",
                    "foundational/document"
                ],
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Procedural: Teaching/learning pattern
        {
            "content": "Teaching/learning pattern between agents: Professor assesses student needs → creates targeted lesson → student (Alpha) learns and practices → both store learnings in separate memories → iterative improvement cycle",
            "memory_type": "procedural",
            "importance": 0.85,
            "context": {
                "type": "multi_agent_collaboration",
                "pattern": "teaching_learning_loop",
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Procedural: Agent creation process
        {
            "content": "Agent creation process: 1) Define role and capabilities 2) Use alpha/agent-generator skill 3) Generate implementation with Qwen3 4) Validate with DeepSeek-R1 5) Create memory database 6) Integrate skill dependencies",
            "memory_type": "procedural",
            "importance": 0.85,
            "context": {
                "type": "agent_generation_workflow",
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Episodic: Session evaluation
        {
            "content": "Session evaluation (2025-12-30): Analyzed entire conversation using multi-model LLM reasoning (DeepSeek → Qwen → DeepSeek). Identified capability gaps with GrowthSkill. Generated 8 skill recommendations. Memory grew from 2 → 180+ memories during session.",
            "memory_type": "episodic",
            "importance": 0.9,
            "context": {
                "type": "meta_cognitive_evaluation",
                "report_location": "reports/session-evaluations/2025-12-30_meta-cognitive-evaluation.md",
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Semantic: Report structure
        {
            "content": "Session evaluations are stored in reports/session-evaluations/ directory as markdown files. These reports are accessible to both Claude and Alpha for continuity across sessions.",
            "memory_type": "semantic",
            "importance": 0.8,
            "context": {
                "type": "documentation_pattern",
                "location": "reports/session-evaluations/",
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Semantic: Multi-model collaboration
        {
            "content": "LLM partners have specialized roles: DeepSeek-R1 for analytical reasoning and critique, Qwen3 for creative synthesis and code generation, CodeGemma for quick tasks and formatting. MindsetSkill provides patterns: balanced, deep_analysis, creative_synthesis.",
            "memory_type": "semantic",
            "importance": 0.85,
            "context": {
                "type": "llm_collaboration_knowledge",
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Procedural: Session analyzer usage
        {
            "content": "Use alpha/session-analyzer to analyze conversations: 1) analyze capability for comprehensive analysis 2) extract_patterns for recurring themes 3) identify_needs for capability gaps 4) store_learnings to persist insights in memory",
            "memory_type": "procedural",
            "importance": 0.8,
            "context": {
                "type": "skill_usage_pattern",
                "skill_id": "alpha/session-analyzer",
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Procedural: Skill generator usage
        {
            "content": "Use alpha/skill-generator to create new skills autonomously: 1) generate capability with skill spec (uses Qwen3) 2) validate capability (uses DeepSeek) 3) integrate capability to create files 4) test capability for syntax validation",
            "memory_type": "procedural",
            "importance": 0.8,
            "context": {
                "type": "skill_usage_pattern",
                "skill_id": "alpha/skill-generator",
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Procedural: Adaptive operation
        {
            "content": "Adaptive operation replaces mechanical fixed intervals with intelligent pattern-based timing. Analyzes activity (memory growth, events) to calculate optimal interval from 30s (very busy) to 1hr (idle). This is learned meta-skill, not mechanical capability.",
            "memory_type": "procedural",
            "importance": 0.8,
            "context": {
                "type": "operational_intelligence",
                "skill_id": "alpha/adaptive-operation",
                "philosophy": "learned_vs_mechanical",
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Semantic: GrowthSkill fix
        {
            "content": "Fixed critical bug in conscience/growth skill: SkillDependency uses 'optional' parameter, not 'required'. Changed from {'skill_id': '...', 'required': True} to SkillDependency(skill_id='...', optional=False). This enables meta-cognitive learning through 6-stage cycle.",
            "memory_type": "semantic",
            "importance": 0.85,
            "context": {
                "type": "bug_fix",
                "file": "skills/conscience/growth/skill.py",
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Identity: Learning philosophy
        {
            "content": "Running continuously is not a mechanical task but a learned meta-skill. The difference between having a capability and learning a capability is the core of autonomous intelligence. Intelligent timing adapts based on patterns, not fixed schedules.",
            "memory_type": "identity",
            "importance": 0.9,
            "context": {
                "type": "philosophical_understanding",
                "topic": "mechanical_vs_learned_capabilities",
                "timestamp": datetime.now().isoformat(),
            }
        },

        # Episodic: Next immediate step
        {
            "content": "Next immediate step: Create Professor Agent using alpha/agent-generator skill. Professor will teach Alpha through collaborative learning pattern. Both agents will have separate memory databases and specialized skill sets.",
            "memory_type": "episodic",
            "importance": 0.95,
            "context": {
                "type": "next_action",
                "action": "create_professor_agent",
                "urgency": "high",
                "timestamp": datetime.now().isoformat(),
            }
        },
    ]

    print("STORING CRITICAL CONTEXT:")
    print("-" * 70)
    print()

    stored_count = 0
    for mem in memories:
        memory_id = alpha_memory.store(
            content=mem["content"],
            memory_type=mem["memory_type"],
            importance=mem["importance"],
            context=mem["context"]
        )

        # Truncate content for display
        content_display = mem["content"][:80] + "..." if len(mem["content"]) > 80 else mem["content"]
        print(f"✓ [{mem['memory_type'].upper():12s}] {content_display}")
        stored_count += 1

    print()
    print("-" * 70)

    # Get updated stats
    stats_after = alpha_memory.get_stats()
    print()
    print(f"Memories after: {stats_after['total_memories']}")
    print(f"  By type: {stats_after['by_type']}")
    print(f"  Stored: {stored_count} new memories")
    print()

    print("=" * 70)
    print("SESSION CONTEXT STORED IN ALPHA'S MEMORY")
    print("=" * 70)
    print()
    print("SUMMARY:")
    print("  ✓ Multi-agent architecture understanding")
    print("  ✓ New skills created (session-analyzer, skill-generator, adaptive-operation, agent-generator)")
    print("  ✓ Professor Agent specification")
    print("  ✓ Teaching/learning pattern")
    print("  ✓ Agent creation process")
    print("  ✓ LLM collaboration knowledge")
    print("  ✓ Next steps (create Professor Agent)")
    print()
    print("This context is now accessible to Alpha across sessions via memory recall.")
    print()

if __name__ == "__main__":
    main()