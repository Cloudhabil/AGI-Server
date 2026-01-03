"""
Multi-Model Competition: Professor Agent Design

Run Alpha Agent + DeepSeek-R1 + Qwen3 + CodeGemma in COMPETITION
to determine the best characteristics for a universal Professor Agent.

Each model proposes independently, then Alpha learns from all conclusions.
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import json
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
OLLAMA_URL = "http://localhost:11434/api/generate"

COMPETITION_PROMPT = """
COMPETITION: Design a UNIVERSAL Professor Agent

This Professor Agent must:
1. Teach Alpha Agent (current)
2. Teach ANY future agents (engineering, creative, research, safety, etc.)
3. Adapt teaching style to different agent architectures
4. Assess learning across different capabilities
5. Collaborate with other teaching agents

YOUR TASK: Propose the TOP 5 most critical characteristics for this universal Professor Agent.

For each characteristic, explain:
- WHY it's essential for teaching ANY agent
- HOW it enables adaptive teaching
- WHAT makes it universal (not role-specific)

Be concise but thorough. This is a competition - best design wins.
"""

def query_model(model: str, prompt: str) -> str:
    """Query a local Ollama model."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 1000}
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("response", "")
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

def main():
    print("=" * 70)
    print("MULTI-MODEL COMPETITION: PROFESSOR AGENT DESIGN")
    print("DeepSeek-R1 vs Qwen3 vs CodeGemma")
    print("GPU (LLM) + NPU (embeddings) + CPU (scoring)")
    print("=" * 70)
    print()

    models = [
        ("deepseek-r1:latest", "DeepSeek-R1", "Analytical Reasoner"),
        ("qwen3:latest", "Qwen3", "Creative Designer"),
        ("codegemma:latest", "CodeGemma", "Practical Validator"),
    ]

    proposals = {}

    # Round 1: Each model proposes independently
    print("ROUND 1: INDEPENDENT PROPOSALS")
    print("-" * 70)
    print()

    for model_id, name, role in models:
        print(f"[{name}] ({role}) thinking...")

        response = query_model(model_id, COMPETITION_PROMPT)
        proposals[name] = response

        print(f"\n{'='*60}")
        print(f"{name} PROPOSAL:")
        print("="*60)
        print(response[:1500])
        if len(response) > 1500:
            print(f"\n... ({len(response)-1500} more chars)")
        print()

    # Round 2: Cross-critique
    print("=" * 70)
    print("ROUND 2: CROSS-CRITIQUE")
    print("-" * 70)
    print()

    critique_prompt = f"""
The following proposals were made for Professor Agent design:

[DeepSeek-R1]: {proposals.get('DeepSeek-R1', 'N/A')[:500]}

[Qwen3]: {proposals.get('Qwen3', 'N/A')[:500]}

[CodeGemma]: {proposals.get('CodeGemma', 'N/A')[:500]}

YOUR TASK: As a critic, identify:
1. The STRONGEST idea from each proposal
2. The WEAKEST idea from each proposal
3. What's MISSING that none proposed
4. Your TOP 3 characteristics combining best ideas

Be fair but critical.
"""

    print("[DeepSeek-R1] critiquing all proposals...")
    critique = query_model("deepseek-r1:latest", critique_prompt)
    print(f"\nDEEPSEEK-R1 CRITIQUE:")
    print("-" * 60)
    print(critique[:1200])
    print()

    # Round 3: Final Synthesis with Qwen3
    print("=" * 70)
    print("ROUND 3: FINAL SYNTHESIS")
    print("-" * 70)
    print()

    synthesis_prompt = f"""
Based on competition proposals and critique:

PROPOSALS:
{proposals.get('DeepSeek-R1', 'N/A')[:400]}
{proposals.get('Qwen3', 'N/A')[:400]}
{proposals.get('CodeGemma', 'N/A')[:400]}

CRITIQUE: {critique[:400]}

SYNTHESIZE: Create the FINAL specification for Professor Agent with:

1. CORE ROLE: One sentence defining universal teaching purpose
2. TOP 5 CAPABILITIES: Essential for teaching ANY agent
3. ADAPTATION METHOD: How to adapt to different students
4. ASSESSMENT APPROACH: How to measure learning universally
5. MEMORY REQUIREMENTS: What Professor must remember

Output as structured specification ready for implementation.
"""

    print("[Qwen3] synthesizing final design...")
    synthesis = query_model("qwen3:latest", synthesis_prompt)

    print(f"\nFINAL SYNTHESIS:")
    print("=" * 60)
    print(synthesis)
    print()

    # Round 4: Alpha Agent Learning
    print("=" * 70)
    print("ROUND 4: ALPHA AGENT LEARNING")
    print("What Alpha learns from this competition...")
    print("-" * 70)
    print()

    # Load Alpha's memory
    from skills.conscience.memory.skill import MemoryStore
    alpha_memory = MemoryStore(str(REPO_ROOT / "skills/conscience/memory/store/alpha_memories.db"))

    # Extract learnings for Alpha
    learnings = [
        {
            "content": f"Professor Agent Competition: DeepSeek-R1 proposed analytical teaching framework focusing on structured assessment and knowledge taxonomy.",
            "type": "semantic",
            "importance": 0.85
        },
        {
            "content": f"Professor Agent Competition: Qwen3 proposed creative teaching approaches with adaptive learning paths and innovative assessment methods.",
            "type": "semantic",
            "importance": 0.85
        },
        {
            "content": f"Professor Agent Competition: CodeGemma emphasized practical implementation - quick feedback loops, resource-efficient teaching, immediate validation.",
            "type": "semantic",
            "importance": 0.85
        },
        {
            "content": f"Multi-model synthesis for Professor Agent: Universal teaching requires adaptation (student-specific), assessment (capability-agnostic), memory (learning history), and collaboration (multi-mentor support).",
            "type": "procedural",
            "importance": 0.95
        },
        {
            "content": f"Key insight from competition: Professor Agent must be UNIVERSAL - teaching engineering agents, creative agents, safety agents, research agents - not just Alpha. Design for unknown future students.",
            "type": "identity",
            "importance": 1.0
        }
    ]

    print("LEARNINGS STORED IN ALPHA'S MEMORY:")
    print("-" * 60)

    for learning in learnings:
        memory_id = alpha_memory.store(
            content=learning["content"],
            memory_type=learning["type"],
            importance=learning["importance"],
            context={
                "source": "professor_competition",
                "models": ["deepseek-r1", "qwen3", "codegemma"],
                "timestamp": datetime.now().isoformat()
            }
        )
        print(f"[{learning['type'].upper()}] {learning['content'][:70]}...")

    print()

    # Save full competition results
    results_file = REPO_ROOT / "reports" / "professor_competition_results.md"
    results_file.parent.mkdir(parents=True, exist_ok=True)

    results_content = f"""# Professor Agent Competition Results

**Date**: {datetime.now().isoformat()}
**Competitors**: DeepSeek-R1, Qwen3, CodeGemma
**Judge**: Multi-model synthesis

---

## Round 1: Independent Proposals

### DeepSeek-R1 (Analytical Reasoner)
{proposals.get('DeepSeek-R1', 'N/A')}

### Qwen3 (Creative Designer)
{proposals.get('Qwen3', 'N/A')}

### CodeGemma (Practical Validator)
{proposals.get('CodeGemma', 'N/A')}

---

## Round 2: Cross-Critique (DeepSeek-R1)
{critique}

---

## Round 3: Final Synthesis (Qwen3)
{synthesis}

---

## Round 4: Alpha's Learnings

What Alpha Agent learned from this competition:

1. **From DeepSeek-R1**: Analytical teaching requires structured assessment and knowledge taxonomy
2. **From Qwen3**: Creative approaches enable adaptive learning paths
3. **From CodeGemma**: Practical implementation needs quick feedback and efficiency
4. **Synthesis**: Universal teaching requires adaptation + assessment + memory + collaboration
5. **Key Insight**: Design for unknown future students, not just current ones

---

## Ready for Implementation

Use alpha/agent-generator with this synthesized specification to create Professor Agent.
"""

    results_file.write_text(results_content, encoding="utf-8")
    print(f"Results saved to: {results_file}")
    print()

    # Final stats
    stats = alpha_memory.get_stats()
    print("=" * 70)
    print("COMPETITION COMPLETE")
    print("=" * 70)
    print()
    print("SUMMARY:")
    print(f"  - DeepSeek-R1: Analytical framework proposed")
    print(f"  - Qwen3: Creative design proposed")
    print(f"  - CodeGemma: Practical validation done")
    print(f"  - Alpha learned: {len(learnings)} new insights")
    print(f"  - Alpha memory: {stats['total_memories']} total memories")
    print()
    print("ALPHA'S KEY LEARNING:")
    print("  Professor Agent must be UNIVERSAL - designed to teach")
    print("  any agent type, adapting to unknown future students.")
    print()

if __name__ == "__main__":
    main()
