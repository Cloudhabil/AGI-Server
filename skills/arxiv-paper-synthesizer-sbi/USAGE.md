# ArXiv Paper Synthesizer - Usage Guide

## Overview

The ArXiv Paper Synthesizer (SBI) enables GPIA to autonomously synthesize, validate, and iteratively improve academic papers through a three-phase cognitive ecosystem:

1. **Hunter** - Identifies unargued claims and rigor gaps
2. **Dissector** - Extracts evidence chains and reasoning patterns
3. **Synthesizer** - Generates improved LaTeX with formal definitions and citations

The system runs N passes with convergence detection, measuring rigor improvement at each step and learning which synthesis strategies are most effective.

---

## How GPIA Uses It

### 1. Initialize and Run Full Synthesis Cycle

```python
from skills.registry import get_registry
from skills.base import SkillContext

registry = get_registry()

# Load papers from arxiv_submission directory
papers = [
    {
        "id": "gpia_sovereign_logic_v1",
        "title": "The Genesis of Sovereign Synthetic Cognition",
        "content": open("arxiv_submission/gpia_sovereign_logic_v1.tex").read(),
        "claims": [
            {
                "claim": "39.13% inference latency improvement",
                "evidence_level": "preliminary"
            },
            {
                "claim": "σ²=1.348 sub-Poissonian distribution",
                "evidence_level": "unargued"
            }
        ]
    },
    # ... more papers
]

# Run synthesis with 3 passes, targeting 0.85 rigor
result = registry.execute_skill(
    "arxiv-paper-synthesizer-sbi",
    {
        "capability": "iterate_n_passes",
        "papers": papers,
        "n_passes": 3,
        "rigor_target": 0.85,
        "convergence_threshold": 0.02,
        "arxiv_field": "cs.AI",
        "focus_areas": ["mathematical_rigor", "citations", "empirical_validation"]
    },
    SkillContext()
)

# Check results
if result.success:
    print(f"✓ Synthesis complete: {result.output['total_passes']} passes")
    print(f"✓ Final rigor score: {result.output['final_rigor_score']:.3f}")
    print(f"✓ ArXiv ready: {result.output['arxiv_ready']}")
    print("\nIteration history:")
    for pass_data in result.output["iteration_history"]:
        print(f"  Pass {pass_data['pass_number']}: "
              f"rigor={pass_data['rigor_score']:.3f}, "
              f"improvement={pass_data['improvement']:+.4f}")
```

### 2. Run Individual Phases

```python
# Just Hunter phase - identify gaps
hunter_result = registry.execute_skill(
    "arxiv-paper-synthesizer-sbi",
    {
        "capability": "run_hunter_pass",
        "papers": papers
    },
    SkillContext()
)

print(f"Found {hunter_result.output['total_unargued_claims']} unargued claims")

# Just Dissector phase - extract evidence chains
dissector_result = registry.execute_skill(
    "arxiv-paper-synthesizer-sbi",
    {
        "capability": "run_dissector_pass",
        "papers": papers
    },
    SkillContext()
)

# Just Synthesizer phase - generate improved LaTeX
synthesizer_result = registry.execute_skill(
    "arxiv-paper-synthesizer-sbi",
    {
        "capability": "run_synthesizer_pass",
        "papers": papers,
        "pass_number": 1
    },
    SkillContext()
)

# Generate improved papers
for paper in synthesizer_result.output["improved_papers"]:
    print(f"Paper {paper['paper_id']}: +{paper['content_delta']} chars")
```

### 3. Evaluate and Get Learning Report

```python
# Evaluate rigor
eval_result = registry.execute_skill(
    "arxiv-paper-synthesizer-sbi",
    {
        "capability": "evaluate_rigor",
        "papers": papers,
        "rigor_target": 0.85
    },
    SkillContext()
)

for assessment in eval_result.output["rigor_assessments"]:
    print(f"{assessment['paper_id']}: {assessment['rigor_score']:.3f} "
          f"(ready={assessment['arxiv_ready']})")
    print(f"  Definition completeness: {assessment['components']['definition_completeness']:.3f}")
    print(f"  Citation coverage: {assessment['components']['citation_coverage']:.3f}")
    print(f"  Methodology: {assessment['components']['methodology_rigor']:.3f}")
    print(f"  Coherence: {assessment['components']['logical_coherence']:.3f}")

# Get learning report
learning_result = registry.execute_skill(
    "arxiv-paper-synthesizer-sbi",
    {
        "capability": "generate_learning_report",
        "papers": papers,
        "iteration_history": result.output["iteration_history"]
    },
    SkillContext()
)

print("\nGPIA learned:")
for pattern in learning_result.output["patterns_discovered"]:
    print(f"  • {pattern}")

print("\nEffectiveness metrics:")
print(f"  Avg improvement/pass: {learning_result.output['effectiveness_metrics']['average_rigor_improvement_per_pass']:.4f}")
print(f"  Convergence passes: {learning_result.output['effectiveness_metrics']['convergence_speed']}")
```

---

## What Each Phase Does

### Hunter - Identify Gaps

**Looks for**:
- Quantitative claims without methodology (39.13% improvement)
- Undefined metrics (AGI Score 100, Resonance Gate 0.95)
- Vague causality statements ("results in", "ensures that")
- Missing empirical evidence for claims

**Output**:
```json
{
  "claims_found": [
    {
      "type": "quantitative",
      "value": "39.13%",
      "context": "...",
      "requires_evidence": true
    }
  ],
  "gap_severity": {
    "critical": ["Metric not formally defined: AGI Score 100"],
    "major": ["Quantitative claim lacks methodology"],
    "minor": []
  },
  "recommendations": [
    "Add formal definitions before submission",
    "Include empirical methodology section"
  ]
}
```

### Dissector - Extract Evidence Chains

**Builds**:
- Evidence chains linking claims to supporting statements
- Theoretical grounding (citations to established theory)
- Empirical evidence (experiments, data, validation)
- Gaps where evidence is weak

**Output**:
```json
{
  "claim": "39.13% inference latency improvement",
  "supporting_statements": [...],
  "theoretical_grounding": ["codegemma", "dense-state memory"],
  "empirical_evidence": ["77.66s", "39.13%", "benchmark"],
  "gaps": ["Lacks baseline architecture specification"],
  "strength_score": 0.65
}
```

### Synthesizer - Generate Improved LaTeX

**Performs**:
- **Pass 1**: Fix LaTeX syntax errors (corrupted characters, unmatched braces)
- **Pass 2**: Inject formal definitions, strengthen citations
- **Pass 3**: Restructure claims with evidence levels, add methodology sections

**Output**:
- Improved `.tex` content with:
  - `\section{Notation and Terminology}` with formal definitions
  - Expanded `\thebibliography` with proper citations
  - Structured claims marked with evidence level
  - Added methodology section with subsections for:
    - Experimental design
    - Evaluation metrics
    - Reproducibility

---

## Convergence and Iteration

The system runs up to N passes (default 3) and stops early if:
```
improvement_between_passes < convergence_threshold
```

Example trajectory:
```
Pass 1: rigor=0.45, improvement=+0.45 (baseline)
Pass 2: rigor=0.72, improvement=+0.27 ← Hunter + Dissector improve significantly
Pass 3: rigor=0.78, improvement=+0.06 ← Synthesizer adds polish
→ Continue if +0.06 > 0.02 threshold, else CONVERGED
```

---

## Rigor Scoring

Each paper receives a composite rigor score (0-1) based on:

| Component | Weight | Measurement |
|-----------|--------|------------|
| Definition Completeness | 25% | % of required metrics formally defined |
| Citation Coverage | 25% | Count of unique citations (target 15+) |
| Methodology Rigor | 25% | Coverage of method/baseline/evaluation/metric |
| Logical Coherence | 25% | Sections with cross-references |

**ArXiv Ready**: score ≥ rigor_target (default 0.85)

---

## Learning Loop

After synthesis completes, GPIA extracts learning:

```python
learning = {
    "passes_to_convergence": 3,
    "total_rigor_improvement": 0.33,
    "best_improvement_pass": 2,  # Dissector was most effective
    "patterns_discovered": [
        "Most unargued claims appear in quantitative sections",
        "Evidence chains strengthen fastest in pass 2",
        "Methodology gaps close before citation gaps"
    ],
    "recommendations": [
        "Focus synthesis on definition completeness (highest ROI)",
        "Prioritize citations in early passes",
        "Reserve methodology restructuring for late passes"
    ]
}
```

**GPIA applies this learning** to:
- Prioritize which synthesis strategies to apply in future cycles
- Allocate token budget more efficiently (focus on high-ROI phases)
- Identify patterns in which claims are hardest to validate

---

## Example: Run on Your Papers

```bash
# From CLI
python -c "
from skills.registry import get_registry
from skills.base import SkillContext
from pathlib import Path

registry = get_registry()

# Load your papers
papers = [
    {
        'id': 'gpia_sovereign_logic_v1',
        'title': 'The Genesis of Sovereign Synthetic Cognition',
        'content': Path('arxiv_submission/gpia_sovereign_logic_v1.tex').read_text(),
    },
    {
        'id': 'foundations_of_temporal_formalism',
        'title': 'Foundations of Temporal Formalism',
        'content': Path('arxiv_submission/foundations_of_temporal_formalism.tex').read_text(),
    },
    # ... add all 5 papers
]

# Synthesize
result = registry.execute_skill(
    'arxiv-paper-synthesizer-sbi',
    {
        'capability': 'iterate_n_passes',
        'papers': papers,
        'n_passes': 3,
        'rigor_target': 0.85,
    },
    SkillContext()
)

# Report
print('SYNTHESIS COMPLETE')
print(f'Passes: {result.output[\"total_passes\"]}')
print(f'Final rigor: {result.output[\"final_rigor_score\"]:.3f}')
print(f'ArXiv ready: {result.output[\"arxiv_ready\"]}')

# Save improved papers
for pass_data in result.output['iteration_history']:
    print(f'  Pass {pass_data[\"pass_number\"]}: {pass_data[\"rigor_score\"]:.3f}')
"
```

---

## Key Design Principles

1. **Progressive Rigor**: Each pass tightens academic standards
2. **Evidence-Grounded**: Claims linked to supporting evidence chains
3. **Self-Learning**: GPIA discovers what synthesis strategies work best
4. **Convergence-Aware**: Stops when diminishing returns appear
5. **ArXiv-Focused**: Optimizes for actual ArXiv submission standards

---

## Architecture Notes

- **Hunter**: Pattern-based gap detection (regex + heuristics)
- **Dissector**: Evidence chain extraction with strength scoring
- **Synthesizer**: LaTeX generation with progressive passes
- **Evaluator**: Composite rigor scoring across 4 dimensions
- **Learning**: Pattern discovery and recommendation generation

The skill is stateless (no persistent learning yet) but designed to:
- Log all synthesis decisions for future analysis
- Build a corpus of what works for arXiv papers
- Enable GPIA to improve her own synthesis heuristics over time
