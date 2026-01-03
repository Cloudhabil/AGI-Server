"""
Session Evaluation: Meta-Cognitive Analysis of Conversation

This script uses Alpha Agent + LLM partners to analyze the entire
conversation session, identify skill gaps, and generate new skills
for autonomous agent capabilities.

Process:
1. Alpha Agent reviews conversation context
2. Multi-model analysis (DeepSeek -> Qwen -> DeepSeek)
3. GrowthSkill identifies capability gaps
4. Generate new skill specifications
5. Store in Alpha's memory for future use
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from datetime import datetime
from skills.loader import SkillLoader
from skills.registry import get_registry
from skills.base import SkillContext

# Conversation context summary
CONVERSATION_SUMMARY = """
# Session Analysis Context

## Topics Covered:
1. AGI Architecture Overview
   - Found 43+ AGI-related components (H-Net, MSHR, Conscience Skills, MindLoop)
   - Identified cognitive architecture with 169 memories, 42 skills
   - Discovered multi-model collaboration (Claude, DeepSeek-R1, Qwen3, CodeGemma)

2. Alpha Agent Deep Dive
   - Found 14 major components of Alpha Agent system
   - OODA loop implementation (Observe -> Orient -> Decide -> Act -> Learn)
   - 3 operational modes (observe, propose, execute)
   - 8 specialized skill dependencies

3. Alpha Agent Enhancement
   - Created separate memory database (alpha_memories.db)
   - Integrated LLM reasoning (3-model chain: DeepSeek -> Qwen -> DeepSeek)
   - Modified alpha.py with intelligent decision-making
   - Successfully ran Alpha with LLM-powered analysis

4. Meta-Cognitive Learning
   - Fixed GrowthSkill (conscience/growth)
   - Demonstrated 6-stage learning cycle
   - Discussed "running continuously" as a learned meta-skill
   - Philosophy: mechanical capabilities vs. intelligent learned skills

5. Current Request
   - Evaluate session for skill gaps
   - Identify skills needed for autonomous agents
   - Use Alpha Agent + LLM partners for analysis
   - Generate new skill specifications

## Key Discoveries:
- Alpha Agent has separate memory (2+ memories stored)
- GrowthSkill enables meta-cognitive learning
- MindsetSkill provides multi-model reasoning
- NPU acceleration (254 texts/sec) operational
- 76 skills in index, 44 registered

## Skills Exercised:
- conscience/memory (MSHR retrieval)
- conscience/mindset (LLM reasoning chains)
- conscience/growth (meta-learning)
- foundational/* (vector mapping, semantic judging, retrieval)
- automation/* (attempted but some missing)

## Patterns Observed:
1. User interested in autonomous cognitive systems
2. Deep questions about learning vs. mechanical execution
3. Focus on meta-cognitive capabilities
4. Interest in self-improving AI systems
5. Preference for hands-on demonstrations
"""

def main():
    print("=" * 70)
    print("META-COGNITIVE SESSION EVALUATION")
    print("Using Alpha Agent + Multi-Model LLM Analysis")
    print("=" * 70)
    print()

    # Load cognitive system
    loader = SkillLoader()
    loader.scan_all(lazy=False)
    registry = get_registry()

    # Get skills
    memory_skill = registry.get_skill('conscience/memory')
    mindset_skill = registry.get_skill('conscience/mindset')
    growth_skill = registry.get_skill('conscience/growth')

    context = SkillContext(agent_role="alpha", session_id="meta_eval")

    print("PHASE 1: MULTI-MODEL ANALYSIS OF CONVERSATION")
    print("-" * 70)
    print()

    # Use MindsetSkill for comprehensive analysis
    print("Consulting LLM Partners (DeepSeek -> Qwen -> DeepSeek)...")
    print()

    analysis_result = mindset_skill.execute({
        'capability': 'analyze',
        'problem': f"""
Analyze this entire conversation session and identify:

{CONVERSATION_SUMMARY}

Questions to answer:
1. What skills were USED in this conversation?
2. What skills were MENTIONED but NOT fully explored?
3. What skills are MISSING that would enable better autonomous operation?
4. What patterns suggest future skill needs?
5. What meta-cognitive capabilities should Alpha develop?

Focus on: Skills for autonomous agents, self-improvement, and cognitive autonomy.
        """,
        'pattern': 'balanced',  # DeepSeek -> Qwen -> DeepSeek
    }, context)

    if analysis_result.success:
        print("✓ Multi-model analysis complete!")
        print()
        print("FINDINGS:")
        print("-" * 70)
        conclusion = analysis_result.output.get('conclusion', '')
        print(conclusion[:2000])
        if len(conclusion) > 2000:
            print(f"\n... ({len(conclusion) - 2000} more characters)")
        print()

        # Store analysis in Alpha's memory
        memory_skill.execute({
            'capability': 'experience',
            'content': f'Session evaluation: {conclusion[:500]}',
            'memory_type': 'semantic',
            'importance': 0.9,
            'context': {
                'type': 'session_analysis',
                'timestamp': datetime.now().isoformat(),
                'pattern': 'balanced'
            }
        }, context)

    print()
    print("PHASE 2: CAPABILITY GAP IDENTIFICATION")
    print("-" * 70)
    print()

    # Use GrowthSkill to identify gaps
    print("Using GrowthSkill to recognize capability gaps...")
    print()

    gap_result = growth_skill.execute({
        'capability': 'recognize',
        'task': 'Enable fully autonomous agent operation with self-improvement',
        'error': 'Current system has manual intervention points, lacks continuous learning loop, missing some automation skills'
    }, context)

    if gap_result.success:
        gap = gap_result.output.get('gap', {})
        print(f"✓ Gap Status: {gap.get('status')}")
        print()
        print("Gap Analysis:")
        print(gap.get('analysis', '')[:1500])
        print()

    print()
    print("PHASE 3: SKILL GENERATION RECOMMENDATIONS")
    print("-" * 70)
    print()

    # Use Qwen3 for creative skill generation
    print("Generating new skill specifications...")
    print()

    skill_gen_result = mindset_skill.execute({
        'capability': 'synthesize',
        'components': [
            'Conversation context and discoveries',
            'Identified capability gaps',
            'Autonomous agent requirements',
            'Meta-cognitive learning needs'
        ],
        'pattern': 'creative_synthesis',  # Emphasize Qwen3
    }, context)

    if skill_gen_result.success:
        print("✓ Skill generation complete!")
        print()
        synthesis = skill_gen_result.output.get('synthesis', '')
        print(synthesis[:1500])
        print()

    print()
    print("PHASE 4: PRIORITY SKILLS FOR AUTONOMOUS AGENTS")
    print("-" * 70)
    print()

    # Create specific recommendations
    recommendations = [
        {
            'skill_id': 'alpha/session-analyzer',
            'name': 'Session Analyzer',
            'description': 'Analyzes conversations to extract learnings, patterns, and skill needs',
            'priority': 'CRITICAL',
            'reason': 'Enables continuous learning from interactions'
        },
        {
            'skill_id': 'alpha/adaptive-operation',
            'name': 'Adaptive Operation',
            'description': 'Intelligent continuous operation with pattern-based timing',
            'priority': 'HIGH',
            'reason': 'Moves from mechanical to intelligent autonomous operation'
        },
        {
            'skill_id': 'alpha/skill-generator',
            'name': 'Skill Generator',
            'description': 'Generates new skill code using Qwen3 based on identified needs',
            'priority': 'CRITICAL',
            'reason': 'Enables true self-expansion of capabilities'
        },
        {
            'skill_id': 'alpha/memory-curator',
            'name': 'Memory Curator',
            'description': 'Manages memory importance, consolidation, and retrieval strategies',
            'priority': 'HIGH',
            'reason': 'Prevents memory bloat, improves recall quality'
        },
        {
            'skill_id': 'alpha/goal-orchestrator',
            'name': 'Goal Orchestrator',
            'description': 'Sets, tracks, and pursues autonomous goals based on observations',
            'priority': 'HIGH',
            'reason': 'Enables proactive vs. reactive behavior'
        },
        {
            'skill_id': 'automation/workflow-validator',
            'name': 'Workflow Validator',
            'description': 'Validates and tests workflow execution before running',
            'priority': 'MEDIUM',
            'reason': 'Safety mechanism for execute mode'
        },
        {
            'skill_id': 'conscience/self-critique',
            'name': 'Self Critique',
            'description': 'Analyzes own decisions and outputs for quality and improvement',
            'priority': 'HIGH',
            'reason': 'Essential for autonomous quality control'
        },
        {
            'skill_id': 'system/capability-mapper',
            'name': 'Capability Mapper',
            'description': 'Maintains dynamic map of what Alpha can/cannot do',
            'priority': 'MEDIUM',
            'reason': 'Self-awareness of capabilities'
        }
    ]

    print("RECOMMENDED NEW SKILLS:")
    print()
    for rec in recommendations:
        print(f"[{rec['priority']}] {rec['skill_id']}")
        print(f"  Name: {rec['name']}")
        print(f"  Purpose: {rec['description']}")
        print(f"  Why: {rec['reason']}")
        print()

    # Store recommendations in Alpha's memory
    memory_skill.execute({
        'capability': 'experience',
        'content': f"Generated {len(recommendations)} new skill recommendations for autonomous agent operation",
        'memory_type': 'procedural',
        'importance': 0.95,
        'context': {
            'type': 'skill_recommendations',
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }
    }, context)

    print()
    print("PHASE 5: MEMORY STORAGE")
    print("-" * 70)
    print()

    # Check Alpha's memory growth
    from skills.conscience.memory.skill import MemoryStore
    alpha_memory = MemoryStore('skills/conscience/memory/store/alpha_memories.db')
    stats = alpha_memory.get_stats()

    print(f"Alpha Memory Database: {stats['total_memories']} memories")
    print(f"  By type: {stats['by_type']}")
    print(f"  Oldest: {stats['oldest']}")
    print(f"  Newest: {stats['newest']}")
    print()

    print("=" * 70)
    print("META-COGNITIVE EVALUATION COMPLETE")
    print("=" * 70)
    print()
    print("SUMMARY:")
    print("  ✓ Analyzed conversation using multi-model LLM reasoning")
    print("  ✓ Identified capability gaps with GrowthSkill")
    print(f"  ✓ Generated {len(recommendations)} new skill specifications")
    print(f"  ✓ Stored findings in Alpha's memory")
    print()
    print("Next Steps:")
    print("  1. Review recommended skills")
    print("  2. Use GrowthSkill to acquire/generate priority skills")
    print("  3. Integrate into Alpha Agent for autonomous operation")
    print("  4. Validate and iterate")
    print()

if __name__ == "__main__":
    main()
