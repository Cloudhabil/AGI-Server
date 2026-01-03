# S² Skill Tree Evolution

## How Multi-Scale Principles Transform the AGI Skill Architecture

### The S² Insight Applied to Skills

The S² paper proves that **smaller models at multiple scales** outperform larger single-scale models. Applied to CLI AI's skill tree:

> **Current**: 121 skills across mixed scales; decomposition is in progress
> **S² Future**: Multi-scale skill pyramid with compositional execution

---

## Current vs S² Architecture

### Before (Monolithic)
```
┌─────────────────────────────────────┐
│         SKILL (Large)               │
│  - Single execution unit            │
│  - Full context loaded              │
│  - One input → One output           │
└─────────────────────────────────────┘
```

### After (S² Multi-Scale)
```
┌─────────────────────────────────────┐
│           META-SKILL                │  ← Orchestrator (linear transform)
├─────────────────────────────────────┤
│  MACRO   │  MACRO   │  MACRO        │  ← 80-120 token planners
├──────────┼──────────┼───────────────┤
│MESO│MESO │MESO│MESO │MESO│MESO      │  ← 30-50 token composers
├────┼─────┼────┼─────┼────┼──────────┤
│μ│μ│μ│μ│μ│μ│μ│μ│μ│μ│μ│μ│μ│μ│μ│μ│μ│μ  │  ← ≤10 token atoms
└─────────────────────────────────────┘
```

---

## New Skill Scale Hierarchy

| Scale | Name | Token Budget | Role | Example |
|-------|------|--------------|------|---------|
| **L0** | Micro-skill | ≤10 tokens | Atomic action | `fetch-url`, `parse-json`, `read-file` |
| **L1** | Meso-skill | 30-50 tokens | Compose 3-5 micros | `extract-entities`, `validate-schema` |
| **L2** | Macro-skill | 80-120 tokens | Bundle 4-6 mesos + planner | `research-topic`, `refactor-module` |
| **L3** | Meta-skill | Variable | Orchestrate macros via linear transform | `autonomous-devops`, `trust-research` |

---

## Key Transformations

### 1. Skill Decomposition

**Current** (automation/hybrid-orchestrator):
```yaml
id: automation/hybrid-orchestrator
capabilities: [plan, execute, validate, rollback]
# Single monolithic skill
```

**S² Transformed**:
```yaml
id: automation/hybrid-orchestrator
scale: L3-meta
composition:
  - L2: workflow-planner
  - L2: execution-engine
  - L2: validation-suite
  - L2: rollback-handler

# L2 workflow-planner decomposes to:
  - L1: intent-parser
  - L1: dependency-resolver
  - L1: resource-allocator

# L1 intent-parser decomposes to:
  - L0: tokenize
  - L0: classify-action
  - L0: extract-params
```

### 2. Linear Transform Between Scales

The S² paper's key insight: multi-scale features approximate large model capacity via **linear transform**.

```python
class ScaleTransform:
    """Linear projection between skill scales"""

    def __init__(self, dim=384):
        # Shared projection matrices between scales
        self.L0_to_L1 = nn.Linear(dim, dim)
        self.L1_to_L2 = nn.Linear(dim, dim)
        self.L2_to_L3 = nn.Linear(dim, dim)

    def compose(self, micro_outputs: List[Tensor]) -> Tensor:
        """Compose micro-skill outputs into meso-level context"""
        pooled = attention_pool(micro_outputs)
        return self.L0_to_L1(pooled)
```

### 3. Context Stack Architecture

```
┌─────────────────────────────────────┐
│ L3 Meta Context                     │  ← Global state, goals
├─────────────────────────────────────┤
│ L2 Macro Context                    │  ← Task-level state
├─────────────────────────────────────┤
│ L1 Meso Context                     │  ← Subtask state
├─────────────────────────────────────┤
│ L0 Micro Context                    │  ← Immediate action state
└─────────────────────────────────────┘

Each scale reads parent context, writes to its own level.
Child skills inherit but cannot modify parent context.
```

### 4. Memory Integration (MSHR)

Current MSHR stores 384-dim embeddings. With S²:

```python
class S2Memory:
    """Multi-scale memory entries"""

    schema = {
        "id": str,
        "content": str,
        "scale_level": int,        # L0, L1, L2, L3
        "embedding_L0": [384],     # Fine-grained features
        "embedding_L1": [384],     # Composed features
        "embedding_L2": [384],     # Abstract features
        "parent_id": Optional[str], # Hierarchical linking
    }

    def recall(self, query, target_scale=None):
        """Scale-aware retrieval"""
        if target_scale:
            return self.search_at_scale(query, target_scale)
        else:
            # Multi-scale fusion (S² principle)
            results = []
            for scale in [0, 1, 2]:
                results.extend(self.search_at_scale(query, scale))
            return self.linear_fuse(results)
```

---

## Transformed Skill Categories

### Current → S² Mapping

| Current Category | S² Structure |
|------------------|--------------|
| `automation/` (10) | 2 Meta + 8 Macro → 24 Meso → 72 Micro |
| `enterprise/` (7) | 2 Meta + 5 Macro → 15 Meso → 45 Micro |
| `reasoning/` (5) | 1 Meta + 4 Macro → 12 Meso → 36 Micro |
| `conscience/` (3) | 1 Meta + 2 Macro → 6 Meso → 18 Micro |
| `design/` (3) | 1 Meta + 2 Macro → 6 Meso → 18 Micro |

**Total S² Skills**: ~6 Meta + 21 Macro + 63 Meso + 189 Micro = **279 skill units**

But! Most micros are shared across categories (S² reuse principle).

**Deduplicated**: ~6 Meta + 21 Macro + 40 Meso + 50 Micro = **117 unique units**

---

## Progressive Disclosure (S² Enhanced)

Current system has 4 levels. S² adds scale dimension:

```
                    BASIC    INTERMEDIATE    ADVANCED    EXPERT
                   ────────────────────────────────────────────
L3 Meta-skill      │ Hide   │    Hide      │   Show   │  Full  │
L2 Macro-skill     │ Hide   │    Show      │   Full   │  Full  │
L1 Meso-skill      │ Show   │    Full      │   Full   │  Full  │
L0 Micro-skill     │ Full   │    Full      │   Full   │  Full  │
                   ────────────────────────────────────────────
```

Users see micros first, then mesos, then macros, finally metas.

---

## Implementation Roadmap

### Phase 1: Decompose Existing Skills (Week 1-2)
```python
# For each current skill:
def decompose_skill(skill_manifest):
    # Identify atomic operations → L0
    micros = extract_atomic_ops(skill_manifest)
    # Group related micros → L1
    mesos = cluster_by_function(micros)
    # Bundle mesos with planning → L2
    macros = add_planning_layer(mesos)
    return {
        'L0': micros,
        'L1': mesos,
        'L2': macros,
        'L3': skill_manifest  # Original becomes meta
    }
```

### Phase 2: Implement Scale Transforms (Week 2-3)
```python
# Linear projections between scales
class SkillScaleProjector:
    def __init__(self):
        self.projectors = nn.ModuleDict({
            'L0_L1': nn.Linear(384, 384),
            'L1_L2': nn.Linear(384, 384),
            'L2_L3': nn.Linear(384, 384),
        })
```

### Phase 3: Context Stack (Week 3-4)
```python
class S2ContextStack:
    def __init__(self):
        self.stack = [{}] * 4  # L0-L3

    def push(self, scale: int, context: dict):
        self.stack[scale] = {**self.stack[scale], **context}

    def get_context(self, scale: int) -> dict:
        # Inherit from parent scales
        return {**self.stack[scale+1], **self.stack[scale]}
```

### Phase 4: MSHR Multi-Scale (Week 4-5)
```python
# Extend MSHR for scale-aware storage/retrieval
def store_multi_scale(memory_entry):
    embeddings = {}
    for scale in [0, 1, 2]:
        embeddings[f'L{scale}'] = encode_at_scale(
            memory_entry,
            scale,
            projector
        )
    return embeddings
```

---

## Expected Benefits

| Metric | Current | S² Expected | Improvement |
|--------|---------|-------------|-------------|
| Skill reuse | Low | High (shared micros) | 3-5x |
| Context efficiency | 1 scale | 4 scales | 4x density |
| Parallel execution | Sequential | Micro-parallel | 2-3x throughput |
| Memory retrieval | Single embedding | Multi-scale fusion | +20% recall |
| Debugging | Opaque | Scale-traceable | Much easier |

---

## Files to Modify

1. `skills/base.py` - Add scale_level to SkillManifest
2. `skills/loader.py` - Multi-scale lazy loading
3. `skills/INDEX.json` - Add scale metadata
4. `skills/conscience/memory/mshr.py` - Multi-scale embeddings
5. `skills/backends.py` - Scale-aware model routing
6. New: `skills/transforms.py` - Linear scale projectors
7. New: `skills/context_stack.py` - Hierarchical context

---

## Conclusion

S² transforms the skill tree from:
- **121 skills** → **multi-scale units** (in progress)
- **Flat execution** → **Hierarchical composition**
- **Single embeddings** → **Multi-scale memory fusion**
- **Sequential processing** → **Parallel micro-execution**

The key insight: **Small skills at multiple scales, composed via linear transforms, match or exceed large monolithic skills**—just as S² showed for vision models.

---

*Generated: 2025-12-31*
*Based on 5 LLM Partner Synthesis (CodeGemma, LLaVa, Qwen3, DeepSeek-R1, GPT-OSS:20b)*
