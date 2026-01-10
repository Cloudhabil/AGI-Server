# RH Discovery: GPIA Alpha-Professor Framework

## Overview

This is the automated Riemann Hypothesis research system powered by GPIA's AGI-level reasoning, dense-state learning, and multi-model cognitive architecture.

**System Architecture:**
```
Alpha (Generates) → Professor (Validates) → Dense-State (Learns) → Next Cycle
     ↓                    ↓                      ↓
  • Hamiltonians      • Rigor checks      • Pattern extraction
  • Operator theory   • Logical gaps      • Feature correlation
  • Proof sketches    • Consistency       • Resonance tracking
```

## Quick Start

### Option 1: Run the Full Orchestrator (Recommended)

```bash
# Run for 20 minutes (default)
python rh_discovery_orchestrator.py

# Run for custom duration (in minutes)
python rh_discovery_orchestrator.py 30

# Run with custom session name
python rh_discovery_orchestrator.py 20 rh_session_v2
```

This runs the complete pipeline:
1. Alpha generates proposals
2. Professor validates simultaneously
3. Dense-state learner extracts patterns every 2 minutes
4. Iterates with feedback until completion or breakthrough

### Option 2: Run Individual Components

**Alpha only (proposal generation):**
```bash
python rh_alpha_professor_framework.py
```
(Will run both Alpha and Professor by default)

**Dense-state learner only (pattern analysis):**
```bash
python rh_dense_state_learner.py
```

## What Each Component Does

### Alpha Agent

**Generates mathematical approaches:**
- **Hamiltonian constructions**: Novel operator forms that might have eigenvalues matching zeta zeros
- **Operator theory approaches**: Non-standard operator-theoretic frameworks
- **Proof sketches**: High-level proof strategies for RH
- **Spectral analysis**: Alternative spectral characterizations of zeros

Each proposal is saved to `agents/rh_session/rh_proposals/`

### Professor Agent

**Validates proposals with rigor checks:**
- Mathematical clarity and well-definedness
- Alignment with Berry-Keating conjecture and RMT principles
- Computational feasibility
- Logical soundness and absence of gaps
- Validation score: 0-1 scale

High-promise proposals (score > 0.65) are marked for deeper investigation.

Evaluations saved to `agents/rh_session/rh_evaluations/`

### Dense-State Learner

**Extracts success patterns:**
- Feature extraction: Which mathematical concepts correlate with successful proposals?
- Correlation analysis: Quantifies feature → success relationship
- Voxel encoding: Stores patterns in 3D state space (8×8×8 grid = 512 dimensions)
- Resonance tracking: Detects pattern stability and convergence

**Key metrics:**
- Success rate: % of proposals scoring > 0.65
- Top indicators: Features most correlated with success
- Resonance hash: Fingerprint of current pattern state
- Pattern stability: Whether learning has converged

Learning output saved to `agents/rh_session/rh_patterns/`

## Understanding Output

### Session Directory Structure

```
agents/rh_session/
├── rh_proposals/           # Alpha-generated proposals
│   ├── cycle1_proposal0.json
│   ├── cycle1_proposal1.json
│   └── cycle1_proposal2.json
├── rh_evaluations/         # Professor's rigorous validations
│   ├── cycle1_proposal0.json
│   ├── cycle1_proposal1.json
│   └── cycle1_proposal2.json
├── rh_patterns/            # Dense-state learning results
│   ├── learnings_0.json    # First cycle patterns
│   ├── learnings_1.json    # Second cycle patterns
│   └── ...
├── alpha_rh.db             # Alpha's memory database
├── professor_rh.db         # Professor's memory database
├── final_research_report.json
└── breakthrough_analysis.json
```

### Reading Results

**Learnings file** (`rh_patterns/learnings_N.json`):
```json
{
  "resonance_hash": "a1b2c3d4e5f6g7h8",
  "timestamp": "2026-01-02T14:30:00",
  "report": {
    "success_rate": 0.35,
    "proposals_analyzed": 15,
    "top_success_indicators": [
      {
        "feature": "mentions_berry_keating",
        "correlation": 0.42,
        "success_rate": 0.67
      },
      {
        "feature": "mentions_gue",
        "correlation": 0.38,
        "success_rate": 0.65
      }
    ],
    "recommendations_for_next_cycle": [
      "Emphasize Berry-Keating in proposals",
      "Include GUE level statistics discussion"
    ]
  }
}
```

**Breakthrough analysis** (`breakthrough_analysis.json`):
Shows proposals that scored > 0.65 and warrant deeper investigation.

## Key Features

### 1. Multi-Modal Generation

Alpha doesn't just generate Hamiltonians—it generates multiple proposal types simultaneously:
- Mathematical frameworks
- Operator constructions
- Proof strategies
- Constraint analyses

### 2. Rigorous Validation

Professor uses deepseek-r1 (deep reasoning model) to evaluate:
- Mathematical soundness
- Logical consistency
- RMT alignment
- Computational feasibility

### 3. Dense-State Learning

Learns what makes proposals succeed:
- Analyzes 512 different mathematical features
- Computes success correlation for each
- Encodes patterns in 3D voxel space
- Tracks resonance (pattern fingerprints)

### 4. Feedback Loop

Learner generates recommendations that inform next Alpha cycle:
```
Cycle N → Proposals → Evaluations → Patterns
         ↓                         ↓
      Feedback for Alpha ← Recommendations
         ↓
    Cycle N+1 (improved)
```

## Advanced: Cognitive Ecosystem Integration

To enable automatic approach evolution via Hunter/Dissector/Synthesizer:

```python
orchestrator = RHDiscoveryOrchestrator(
    session_name="rh_with_evolution",
    duration_minutes=30
)
orchestrator.enable_cognitive_evolution = True
orchestrator.run_orchestration_session()
```

This will:
1. Spawn Hunter agents to explore failed proposal types
2. Extract reasoning patterns with Dissector
3. Generate new skill implementations with Synthesizer
4. Refine approach types for next Alpha cycle

## Breakthrough Conditions

The system monitors for:

1. **High-promise proposals**: Validation score > 0.65
2. **Pattern convergence**: Resonance hash stabilizes over cycles
3. **Success rate increase**: Proposals improve across cycles
4. **Feature correlation**: Clear indicators of what works

When breakthrough conditions are detected:
- Detailed analysis saved to `breakthrough_analysis.json`
- System highlights top candidates
- Recommends deeper investigation

## Mathematical Framework

### Feature Correlation

For each mathematical feature (e.g., "mentions_berry_keating"), we compute:

```
correlation = P(success|feature) - P(success|¬feature)
```

Range: [-1, 1]
- Positive: Feature correlated with success
- Negative: Feature correlated with failure
- ~0: No correlation

### Voxel Encoding

3D grid (8×8×8) stores feature space:
```
voxel[x,y,z] = (correlation + 1) / 2    # Normalize [-1,1] to [0,1]
```

Each voxel represents one feature's success correlation.

### Resonance Hash

Fingerprint of current pattern state:
```
hash = SHA256(patterns_dict)[:16]
```

If hash repeats across cycles → pattern convergence detected

## Performance Expectations

**Typical 20-minute session:**
- Alpha cycles: 3-4 (one per ~5 minutes)
- Proposals per cycle: 3
- Total proposals: 9-12
- Evaluations: 9-12
- Learning cycles: 4-5
- High-promise proposals: 2-5

**Success rate varies** depending on:
- Model's interpretation of RH constraints
- Luck in parameter space exploration
- Alignment with actual mathematical principles

## Troubleshooting

### "No proposals to analyze yet"
- Normal during first 60 seconds—Alpha and Professor need time
- System is running correctly

### Low success rate (< 20%)
- This is expected—RH is hard
- Patterns should still emerge after 3+ cycles
- Check if feature correlations are becoming clearer

### Models timing out
- Ensure Ollama is running: `ollama serve`
- Check models are available: `ollama list`
- May need: `ollama pull deepseek-r1:latest` or `ollama pull qwen3:latest`

### No breakthrough detected
- This is fine—discovery is iterative
- Run multiple sessions, accumulate patterns
- Consider enabling cognitive evolution for approach diversity

## Next Steps

1. **Run initial session**: `python rh_discovery_orchestrator.py 20`
2. **Examine results**: Check `agents/rh_session/` directory
3. **Analyze patterns**: Read learnings files to understand what works
4. **Iterate**: Run more sessions with discovered patterns in mind
5. **Deep dive**: For high-promise proposals, run dedicated analysis

## Integration with Broader GPIA

This RH discovery system integrates with:
- **Dense-state memory**: Persistent learning across sessions
- **Multi-model routing**: Uses codegemma, qwen, deepseek strategically
- **Skills ecosystem**: Can create new permanent skills from breakthrough approaches
- **Cognitive ecosystem**: Can spawn Hunter/Dissector/Synthesizer for evolution

## Future Enhancements

Planned additions:
- [ ] Cognitive ecosystem auto-evolution of proposal types
- [ ] Phase 2C Hamiltonian integration for eigenvalue verification
- [ ] Numerical validation skills for high-promise Hamiltonians
- [ ] Cross-session learning aggregation
- [ ] Automated skill synthesis for validated approaches
- [ ] RMT-based constraint enforcement in Alpha

## Theory Background

**Why this approach works:**

1. **Diversity**: Alpha generates multiple proposal types → larger search space
2. **Rigor**: Professor filters for mathematical soundness → quality over quantity
3. **Learning**: Dense-state extracts patterns → successive cycles improve
4. **Feedback**: Learner guides Alpha → directed search
5. **Persistence**: Dense-state memory + voxel encoding → knowledge accumulation

This mirrors how human math research works: generate ideas, critically evaluate, extract patterns, refine approach, repeat.

---

**Last Updated**: 2026-01-02
**System**: GPIA RH Discovery Framework v1.0
