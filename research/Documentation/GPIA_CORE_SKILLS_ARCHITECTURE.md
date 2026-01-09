# GPIA-Core Specialized Skill Registry

## Why Separate Skills for GPIA-Core?

Yes, it makes excellent sense. Here's why:

### 1. **Different Reasoning Patterns**

GPIA-core is built for:
- Deep logical reasoning
- Complex synthesis
- Multi-step problem solving
- Mathematical proof validation

Student models (7B) are optimized for:
- Quick responses
- Practical applications
- Single-step inference
- Pattern recognition

**Example:**
```
Task: "Analyze Riemann Hypothesis proof structure"

GPIA-core approach:
  [Decompose] → [Recursive analysis] → [Pattern recognition] → [Synthesis]
  Uses: reasoning, decomposition, recursive_thinking, synthesis
  Time: More (deep analysis)
  Quality: High (comprehensive)

Student approach:
  [Quick analysis] → [Output]
  Uses: quick_synthesis, pattern_matching
  Time: Less (fast response)
  Quality: Good (practical answer)
```

### 2. **Performance Optimization**

Skills can be tuned per-model:

```
Core Skills:
  - reasoning/deep_zeta_analysis.py
    └─ Optimized for GPIA-core token budget
    └─ Uses advanced math notation
    └─ Multi-step reasoning

Student Skills:
  - synthesis/quick_summary.py
    └─ Optimized for 7B model VRAM
    └─ Simplified language
    └─ Single-pass synthesis
```

### 3. **Safety & Curation**

Core model gets curated skills:

```
GPIA-Core Skills:
  ✓ Proof validation (mathematically rigorous)
  ✓ Constraint solving (complex logic)
  ✓ Recursive thinking (deep analysis)
  ✓ Pattern abstraction (generalization)

Student Skills:
  ✓ Practical synthesis (actionable)
  ✓ Quick optimization (efficient)
  ✓ Pattern matching (recognition)
  ✓ Explanation simplification (clarity)
```

### 4. **Evolution & Learning**

Each can evolve independently:

```
GPIA-Core Evolution:
  [Skill v1.0] → [Skill v1.1] → [Skill v2.0]
  Focus: Deeper reasoning, better proofs

Student Evolution:
  [Skill v1.0] → [Skill v1.1] → [Skill v2.0]
  Focus: Faster inference, better explanations
```

### 5. **Synergy Tracking**

Core skills can be tracked for which combinations work best:

```
Database tracks:
  primary_skill: "riemann_deep_analysis"
  supporting_skill: "zeta_function_synthesis"
  synergy_score: 0.94  ← These work GREAT together!
  use_count: 247

Then system learns: "When using deep analysis,
                    always consider synergy with synthesis"
```

---

## Architecture Overview

### Current Structure (Before)
```
skills/
├── synthesized/
├── auto_learned/
├── evolved/
├── registry.py  ← All models share this
└── base.py
```

**Problem**: One-size-fits-all approach

### New Structure (After)
```
skills/
├── core/                    ← NEW: GPIA-core exclusive
│   ├── reasoning/           (e.g., riemann_deep_analysis.py)
│   ├── synthesis/           (e.g., zeta_function_synthesis.py)
│   ├── validation/          (e.g., proof_validator.py)
│   ├── abstraction/         (e.g., pattern_abstractor.py)
│   ├── decomposition/       (e.g., problem_decomposer.py)
│   ├── recursive_thinking/  (e.g., recursive_analyzer.py)
│   ├── constraint_solving/  (e.g., constraint_solver.py)
│   ├── pattern_recognition/ (e.g., pattern_detector.py)
│   ├── core_registry.py     (NEW: Core-specific database)
│   └── core_skill_metrics.db
│
├── student/                 ← Can add student-specific skills
│   ├── synthesis/
│   ├── optimization/
│   └── student_registry.py  (optional)
│
├── general/                 ← Shared fallback skills
│   ├── synthesized/
│   ├── auto_learned/
│   └── ...
│
├── unified_skill_router.py  (NEW: Routes to right registry)
├── core_registry.py         (NEW: Core skill tracking)
├── registry.py              (Existing general registry)
└── base.py
```

**Benefits**: Specialized + hierarchical + fallback

---

## Routing Logic

### Unified Skill Router Decision Tree

```
Model Request: "I need a skill for task X"
    ↓
router.get_best_skill(model="gpia-core", task_type="reasoning")
    ↓
[DETERMINE TIER]
    model = "gpia-core" → tier = CORE
    ↓
[ROUTE TO APPROPRIATE REGISTRY]
    if tier == CORE:
        query core_registry
    elif tier == STUDENT:
        query general_registry (or student_registry if exists)
    else:
        query general_registry
    ↓
[TRY PRIMARY]
    Does core_registry have a skill for "reasoning"?
    Yes → Return it
    No → Check fallback
    ↓
[TRY FALLBACK]
    fallback_to_general=True?
    Yes → Try general_registry
    No → Return None
    ↓
[RECORD USAGE]
    Record to core_registry if CORE tier
    Record to general_registry if STUDENT tier
```

---

## Database Schema

### Core Skills Registry

```sql
-- Available core skills
CREATE TABLE core_skills (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,              -- "riemann_deep_analysis"
    category TEXT,                 -- "reasoning"
    description TEXT,              -- "What it does"
    version TEXT,                  -- "1.0"
    created_at REAL,
    updated_at REAL
);

-- Performance tracking per skill
CREATE TABLE skill_performance (
    id INTEGER PRIMARY KEY,
    skill_name TEXT,
    task TEXT,                     -- "Analyze proof structure"
    success BOOLEAN,
    quality_score FLOAT,           -- 0.0-1.0
    execution_time_ms FLOAT,
    tokens_used INTEGER,
    timestamp REAL
);

-- Which skills work best together
CREATE TABLE skill_compositions (
    id INTEGER PRIMARY KEY,
    primary_skill TEXT,            -- "riemann_deep_analysis"
    supporting_skill TEXT,         -- "zeta_function_synthesis"
    synergy_score FLOAT,           -- 0.94 (they work great together!)
    use_count INTEGER,
    timestamp REAL
);
```

### Queries

```python
# Get best skill for task
SELECT name FROM core_skills
WHERE category = "reasoning"
ORDER BY (avg quality) DESC
LIMIT 1

# Get skills that work with primary skill
SELECT supporting_skill, synergy_score
FROM skill_compositions
WHERE primary_skill = "riemann_deep_analysis"
ORDER BY synergy_score DESC

# Top performers
SELECT name, avg(quality_score), count(*)
FROM core_skills
JOIN skill_performance ON core_skills.name = skill_performance.skill_name
GROUP BY name
ORDER BY avg(quality_score) DESC
```

---

## Usage Example

### Before (All models same skills):
```python
from skills.registry import get_registry

registry = get_registry()
skill = registry.execute_skill("synthesized/active-immune", {...})
# ^ Everyone uses same skills
```

### After (Model-specific skills):
```python
from skills.unified_skill_router import get_unified_router

router = get_unified_router()

# GPIA-core gets specialized skill
if model == "gpia-core":
    skill = router.get_best_skill("gpia-core", "reasoning")
    # Returns: "riemann_deep_analysis" (from core registry)

# Student gets general skill
elif model == "alpha":
    skill = router.get_best_skill("alpha", "synthesis")
    # Returns: "quick_summary" (from general registry)

# Record performance
router.record_skill_usage(
    model="gpia-core",
    skill_name="riemann_deep_analysis",
    task="Analyze hypothesis",
    success=True,
    quality_score=0.92,
    execution_time_ms=3500,
    tokens_used=2847
)
```

---

## Core-Specific Skill Categories

### 1. **Reasoning** (deep_logical_analysis)
- Deep analysis of problems
- Multi-step reasoning chains
- Logical proof construction

**Skills:**
- `riemann_deep_analysis` - First principles analysis
- `zeta_function_properties` - Complex property reasoning
- `numerical_methods_reasoning` - Computational strategy

### 2. **Synthesis** (combining_insights)
- Combining multiple perspectives
- Creating coherent output from fragments
- Bridging different domains

**Skills:**
- `zeta_function_synthesis` - Combining zeta properties
- `cross_domain_bridge` - Connecting RH to other fields
- `insight_composition` - Merging insights

### 3. **Validation** (proof_checking)
- Checking logical consistency
- Validating mathematical proofs
- Error detection

**Skills:**
- `proof_validator` - Validates proof structure
- `consistency_checker` - Checks logical consistency
- `error_detector` - Finds logical gaps

### 4. **Abstraction** (finding_patterns)
- Finding abstract patterns
- Generalizing specific cases
- Creating conceptual models

**Skills:**
- `pattern_abstractor` - Finds general patterns
- `generalizer` - Creates abstract models
- `meta_analyzer` - High-level analysis

### 5. **Decomposition** (breaking_down)
- Breaking complex problems down
- Identifying sub-problems
- Creating problem hierarchies

**Skills:**
- `problem_decomposer` - Breaks down RH
- `hierarchical_analyzer` - Creates problem trees
- `sub_problem_identifier` - Finds sub-tasks

### 6. **Recursive Thinking** (self_referential_analysis)
- Applying recursion to problems
- Self-referential reasoning
- Iterative refinement

**Skills:**
- `recursive_analyzer` - Applies recursion
- `self_referential_reasoner` - Self-referential logic
- `iterative_refiner` - Iterative improvement

### 7. **Constraint Solving** (bounded_problem_solving)
- Solving with constraints
- Optimization problems
- Finding valid solutions within bounds

**Skills:**
- `constraint_solver` - Solves constrained problems
- `optimizer` - Optimization strategies
- `bounded_search` - Search within constraints

### 8. **Pattern Recognition** (identifying_structures)
- Identifying patterns
- Recognizing structures
- Classifying patterns

**Skills:**
- `pattern_detector` - Detects patterns
- `structure_recognizer` - Recognizes structures
- `pattern_classifier` - Classifies patterns

---

## Performance Tracking Example

### Scenario: Riemann Analysis Skill

```
Day 1:
  Use: riemann_deep_analysis
  Task: "Analyze proof structure"
  Result: quality=0.88, time=2100ms, tokens=1800

Day 2:
  Use: riemann_deep_analysis
  Task: "Explain critical line"
  Result: quality=0.91, time=2300ms, tokens=1950

Day 3:
  Use: riemann_deep_analysis + zeta_function_synthesis
  Task: "Synthesize analysis with zeta properties"
  Result: quality=0.94, time=3200ms, tokens=3100
  → System records synergy_score=0.94 for this combo!

Statistics:
  Success rate: 100%
  Avg quality: 0.91
  Avg time: 2533ms
  Avg tokens: 2283
  Most effective combo: riemann_deep_analysis + zeta_function_synthesis
```

---

## Integration with Existing Systems

### With Orchestrator
```python
from orchestrator_predictive_sequential import PredictiveSequentialOrchestrator
from skills.unified_skill_router import get_unified_router

orchestrator = PredictiveSequentialOrchestrator()
router = get_unified_router()

# When GPIA-core needs to solve a problem:
skill_name = router.get_best_skill("gpia-core", "reasoning")
# → Gets "riemann_deep_analysis" (core registry)

# Record how well it performed:
router.record_skill_usage(
    model="gpia-core",
    skill_name=skill_name,
    task="Analyze RH",
    success=True,
    quality_score=0.92,
    execution_time_ms=3500,
    tokens_used=2847
)
```

### With Adaptive Ensemble
```python
from start_rh_adaptive_ensemble import RHAdaptiveEnsemble
from skills.unified_skill_router import get_unified_router

ensemble = RHAdaptiveEnsemble()
router = get_unified_router()

# When Student Alpha runs:
skill_name = router.get_best_skill("alpha", "synthesis")
# → Gets from general registry (not core skills)

# Skills are optimized for 7B models, not deep reasoning
```

---

## Migration Path

### Phase 1: Foundation (Week 1)
- Create `skills/core/` directory structure
- Implement `core_registry.py` (this file ✓)
- Implement `unified_skill_router.py` (this file ✓)
- Create core_skill_metrics.db

### Phase 2: Core Skills (Week 2)
- Implement 8 core skill categories
- Port relevant skills from general registry
- Create core-specific optimizations
- Populate skill database

### Phase 3: Integration (Week 3)
- Update GPIA-core to use unified router
- Track performance for all core skills
- Analyze skill synergies
- Optimize combinations

### Phase 4: Student Skills (Week 4)
- Optional: Create student-specific skills
- Optimize 7B model execution
- Track student skill performance
- Separate student evolution

---

## Key Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Skill selection** | One registry for all | Model-specific routing |
| **Performance tuning** | Generic for all | Optimized per-model |
| **Reasoning depth** | Same for all | Deep for core, practical for students |
| **Synergy tracking** | N/A | Tracks which skills work together |
| **Evolution** | All models evolve same way | Independent evolution paths |
| **Safety/Curation** | All skills available | Core gets curated set |
| **Learning** | Monolithic | Modular learning per tier |

---

## Files Created

1. **`skills/core_registry.py`** (350 lines)
   - GPIA-core specific skill database
   - Performance tracking
   - Synergy analysis
   - Categories: reasoning, synthesis, validation, abstraction, decomposition, recursive_thinking, constraint_solving, pattern_recognition

2. **`skills/unified_skill_router.py`** (290 lines)
   - Routes requests to appropriate registry
   - Model tier classification
   - Fallback chain handling
   - Performance recording

3. **`GPIA_CORE_SKILLS_ARCHITECTURE.md`** (This file)
   - Complete architecture documentation
   - Usage examples
   - Migration path
   - Integration guide

---

## Testing

```bash
# Initialize and show core registry
python skills/core_registry.py

# Show routing table
python skills/unified_skill_router.py

# Check metrics database
sqlite3 agents/sessions/*/core_skill_metrics.db ".schema"
```

---

## Next Steps

1. Create core skill implementations in `skills/core/*/`
2. Integrate unified router into orchestrators
3. Update GPIA-core to use core registry
4. Track performance and synergies
5. Optional: Create student-specific skills
6. Optimize skill combinations based on data

