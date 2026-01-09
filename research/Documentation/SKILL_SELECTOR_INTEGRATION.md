# Autonomous Skill Selector Integration Guide

## Overview

The **Autonomous Skill Selector Agent** is now fully integrated into the **Predictive Sequential Orchestrator**. This creates a complete end-to-end system that:

1. **Predicts resource requirements** before loading models
2. **Selects skills intelligently** based on learned patterns
3. **Executes efficiently** with soft warm-up
4. **Records outcomes** for continuous learning
5. **Improves over time** as confidence builds

---

## Architecture: Three-Layer System

### Layer 1: Core Skill Registry (`skills/core_registry.py`)
**Database of available skills organized by category:**
```
Reasoning, Synthesis, Validation, Abstraction, Decomposition,
Recursive Thinking, Constraint Solving, Pattern Recognition
```

### Layer 2: Autonomous Skill Selector Agent (`skills/autonomous_skill_selector.py`)
**Meta-learning agent that:**
- Observes outcomes of skill usage
- Extracts patterns (model + task_type → best_skill)
- Builds confidence from observations
- Balances exploration (15% try new) vs exploitation (use proven)
- Updates continuously as new data arrives

### Layer 3: Predictive Sequential Orchestrator (`orchestrator_predictive_sequential.py`)
**Orchestrates execution with intelligence:**
- Resource prediction before loading
- Autonomous skill selection before execution
- Real model execution with warm-up
- Outcome recording for agent learning
- Context transfer between models

---

## Integration Points

### 1. Skill Selection in Orchestrator

**Before Execution (STEP 4.5):**
```python
# Select skill autonomously
if self.skill_selector:
    skill_name, reasoning = self.skill_selector.select_skill(
        student_name,           # "alpha", "beta", etc.
        config["prompt"]        # The task description
    )

    # Returns:
    # skill_name = "riemann_deep_analysis"
    # reasoning = {
    #     "pattern": "reasoning",
    #     "confidence": 0.75,
    #     "selection_method": "exploitation"  # or "exploration"
    # }
```

### 2. Recording Learning Outcomes

**After Execution (STEP 8):**
```python
# Calculate quality based on throughput
quality_score = min(1.0, throughput / 40.0)  # 40 tok/s = perfect

# Record for learning
self.skill_selector.record_outcome(
    model=student_name,
    task=config["prompt"],
    skill=skill_name,
    success=True,
    quality=quality_score
)

# Agent updates internally:
# - success_rate for this (model, pattern, skill) combo
# - avg_quality score
# - confidence = min(1.0, observations / 15)
# - marks for future exploitation or exploration
```

### 3. Database Tracking

**Two tables in metrics.db:**

**executions table:**
```sql
SELECT cycle, student, skill_selected, skill_confidence,
       selection_method, throughput, tokens
FROM executions
```

**skill_selections table:**
```sql
SELECT cycle, student, task_pattern, skill_selected,
       confidence, selection_method, quality_score
FROM skill_selections
```

---

## Learning Progression Example

### Day 1: No Knowledge
```
Cycle 1:
  Alpha + "Analyze RH..."
    -> No learned patterns yet
    -> Select randomly: "riemann_deep_analysis"
    -> Execute: throughput=35 tok/s, quality=0.88
    -> Record: riemann_deep_analysis SR=100% Q=0.88 Conf=0.07 (n=1)

Cycle 2:
  Alpha + "Analyze RH..."
    -> Found pattern! Conf=0.07 < threshold (0.70)
    -> Still exploring: random selection
    -> Selected: "riemann_deep_analysis" (again)
    -> Execute: throughput=38 tok/s, quality=0.95
    -> Record: riemann_deep_analysis SR=100% Q=0.91 Conf=0.13 (n=2)
```

### Week 1: Building Confidence
```
After 5+ observations:
  Confidence = min(1.0, 5 / 15) = 0.33
  Success Rate = 100%
  Avg Quality = 0.92
  -> Still under 70% threshold, mix exploitation/exploration

After 10 observations:
  Confidence = min(1.0, 10 / 15) = 0.67
  -> Getting close to exploitation threshold
  -> 85% of time use best-known, 15% explore alternatives
```

### Week 2+: Exploitation Phase
```
After 15+ observations:
  Confidence = min(1.0, 15 / 15) = 1.0 (full confidence)
  Success Rate = 99%
  Avg Quality = 0.93
  -> EXPLOIT: Use riemann_deep_analysis for reasoning tasks
  -> Still explore 15% of time to find better combinations
```

---

## Running the Integrated System

### Quick Test (10 minutes, 1-2 cycles)
```bash
python orchestrator_predictive_sequential.py --duration 10 --session test_skill_learning
```

### Production Run (2+ weeks for real learning)
```bash
python orchestrator_predictive_sequential.py --duration 20160 --session rh_production
# Runs for 2 weeks continuously
# Accumulates enough observations for high-confidence patterns
```

### View Learning Progress During Run
```bash
# In another terminal, monitor the database:
sqlite3 agents/sessions/rh_production/metrics.db "SELECT student, skill_selected, COUNT(*), AVG(quality_score) FROM executions WHERE skill_selected IS NOT NULL GROUP BY student, skill_selected;"
```

### Analyze Results After Run
```bash
# Final report is printed at end of run, includes:
# - Cycles completed
# - Skills selected
# - Unique skills learned
# - Average confidence
# - Average quality
# - Learned patterns from autonomous selector
```

---

## Key Metrics to Monitor

### 1. Skill Selection Metrics
```
Average Confidence: Should trend upward over time
  - Day 1: 0.07 (just started)
  - Week 1: 0.40-0.60 (learning)
  - Week 2: 0.70+ (exploiting)

Skills Per Student: How many different skills discovered
  - Ideally stabilizes to 1-3 per student
  - Higher = more exploration needed
  - Lower = might be over-specializing

Selection Method Distribution:
  - Exploitation %: Should increase over time
  - Exploration %: Should decrease (but stay at ~15%)
```

### 2. Quality Metrics
```
Average Quality Score: 0.0-1.0, higher is better
  - Based on throughput (40 tok/s = 1.0)
  - Should be consistent (< 10% variance)

Quality Per Skill: Which skills produce best results
  - riemann_deep_analysis: 0.92 avg
  - zeta_function_synthesis: 0.88 avg
  - etc.
```

### 3. Resource Metrics
```
Throughput (tokens/second): Should be homogeneous
  - Soft warm-up should eliminate cold-start spikes
  - Target: 30-40 tok/s with <5% variance

VRAM Usage: Should stay under 85%
  - Resource predictor enforces this
  - If violations occur, resource rule failed
```

---

## What Happens Behind the Scenes

### Full Request Flow

```
1. Orchestrator._run_cycle()
   ↓
2. For each student (alpha, beta, gamma, ...):
   ↓
3. [PREDICT] Check if safe to load model
   safe, reason = predictor.predict_model_load(model)
   ↓
4. [BOOT UP] Load model to VRAM
   lifecycle.boot_up(model)
   ↓
5. [SOFT WARMUP] Warm GPU cache (10 tokens)
   lifecycle.soft_warmup(model)
   ↓
6. [SKILL SELECT] Autonomously choose skill
   skill, reasoning = skill_selector.select_skill(student_name, prompt)
   ↓
   Agent internally:
   - abstract_task_pattern(prompt) -> "reasoning" | "synthesis" | etc.
   - query memory: patterns for (student="alpha", pattern="reasoning")
   - if confidence >= 70% -> EXPLOIT (use best known)
   - else -> EXPLORE (try alternative)
   ↓
7. [EXECUTE] Run full inference with warm model
   response, tokens, throughput = lifecycle.execute(model, prompt)
   ↓
8. [TRANSFER] Extract context/insights
   context = context_manager.extract_context(student, response)
   ↓
9. [BOOT DOWN] Unload model
   lifecycle.boot_down(model)
   ↓
10. [RECORD LEARNING] Update agent's knowledge
    quality_score = throughput / 40.0
    skill_selector.record_outcome(student_name, prompt, skill_name,
                                  success=True, quality=quality_score)
    ↓
    Agent internally:
    - record to recommendations table
    - recalculate success_rate, avg_quality, confidence
    - update learned_patterns table
    - logging: "[LEARNING] alpha/reasoning/riemann: SR=100% Q=0.92 Conf=0.20 (n=3)"
    ↓
11. [DATABASE RECORD] Save to metrics.db
    INSERT INTO executions (...)
    INSERT INTO skill_selections (...)
```

---

## Design Philosophy

### Not a Static Router
**Before:** Hardcoded rules in code
```python
if model == "gpia-core" and pattern == "reasoning":
    use "riemann_deep_analysis"  # Fixed in code
```

**After:** Autonomous Learning Agent
```python
agent.select_skill("alpha", "Analyze RH...")
# Returns best skill based on 50+ observations
# Automatically improves as more data comes in
```

### Benefits of Autonomous Selection

| Aspect | Static Router | Autonomous Agent |
|--------|---|---|
| **Adaptation** | Requires code change | Automatic, continuous |
| **Learning** | No learning from data | Learns from every outcome |
| **Exploration** | Fixed rules only | 15% exploration + 85% exploitation |
| **Synergy** | Can't detect | Tracks skill combinations |
| **Confidence** | N/A | Quantified confidence per pattern |
| **Evolution** | Manual updates | Improves autonomously |

---

## Confidence Thresholds

### Decision Rules
```
Confidence < 50%:
  -> Mostly EXPLORE (try new skills)
  -> Weak pattern, needs more data

50% <= Confidence < 70%:
  -> Mix exploitation/exploration (70/30 split)
  -> Pattern emerging, building confidence

Confidence >= 70%:
  -> Mostly EXPLOIT (use proven skill)
  -> But still 15% EXPLORE (discover better combinations)
  -> High confidence, pattern established

Confidence = 100% (15+ observations):
  -> Full exploitation with structured exploration
  -> Pattern fully trusted, optimize and innovate
```

---

## Files Modified/Created

### Modified Files
1. **`orchestrator_predictive_sequential.py`**
   - Added skill selector import and initialization
   - Added STEP 4.5: Autonomous skill selection
   - Added STEP 8: Record learning outcomes
   - Updated database schema with skill columns
   - Enhanced reporting with learning statistics

### New Features Added
1. **Skill Selection Logging**
   ```
   [SKILL SELECT] riemann_deep_analysis
     Pattern: reasoning | Confidence: 75% | Method: exploitation
   ```

2. **Learning Outcome Recording**
   ```
   [LEARNING] Recorded outcome: riemann_deep_analysis -> Q=0.88
   ```

3. **Final Learning Summary**
   ```
   AUTONOMOUS SKILL SELECTOR - LEARNING SUMMARY
   Learned patterns: 3
   Average confidence: 0.65
   Average success rate: 96%
   Average quality: 0.90

   DETAILED LEARNED PATTERNS:
   Model: alpha
     reasoning: riemann_deep_analysis (SR=100% Q=0.91 C=0.27 n=4)
     synthesis: zeta_function_synthesis (SR=100% Q=0.86 C=0.13 n=2)
   ```

---

## Expected Outcomes

### After 1 Hour (3-4 cycles)
- ✓ Skill selector working, selecting skills
- ✓ Basic patterns emerging (confidence 0.07-0.20)
- ✓ Learning recorded in database
- ✗ Not enough data for real confidence (need 5+ observations)

### After 1 Day (12-16 cycles)
- ✓ Clear patterns established per student
- ✓ Confidence values: 0.40-0.70 range
- ✓ Can see preference for certain skills
- ✓ Learning dynamics visible

### After 1 Week (100+ cycles)
- ✓ High confidence patterns (0.70+)
- ✓ Agent consistently selecting best skills
- ✓ Occasional exploration discovering new combinations
- ✓ Quality metrics improving

### After 2+ Weeks (200+ cycles)
- ✓ Full exploitation mode for proven patterns
- ✓ Multiple synergies discovered (skill combinations)
- ✓ System operating at optimized efficiency
- ✓ New patterns still emerging from exploration

---

## Troubleshooting

### Skill Selector Not Initializing
```
[WARN] Autonomous skill selector not available
```
**Fix:** Check that `skills/autonomous_skill_selector.py` exists
```bash
ls -la skills/autonomous_skill_selector.py
```

### No Skills Being Selected
```
[SKILL SELECT] Error: ...
```
**Fix:** Check skill selector memory database
```bash
sqlite3 skills/core/selector_memory.db ".schema"
```

### Confidence Not Increasing
**Cause:** Not enough observations accumulated
**Fix:** Run longer session (need 5+ observations per pattern)
```bash
python orchestrator_predictive_sequential.py --duration 60
```

### Learning Outcomes Not Recorded
**Check:** Verify database has skill_selections table
```bash
sqlite3 agents/sessions/rh_production/metrics.db ".tables"
```

---

## Next Steps

1. **Run production session:**
   ```bash
   python orchestrator_predictive_sequential.py --duration 20160 --session rh_learning
   ```

2. **Monitor learning progress:**
   ```bash
   watch -n 60 'sqlite3 agents/sessions/rh_learning/metrics.db "SELECT COUNT(*), COUNT(DISTINCT skill_selected) FROM executions WHERE skill_selected IS NOT NULL;"'
   ```

3. **Analyze results after 1-2 weeks:**
   - Extract most-used skills per student
   - Identify skill synergies
   - Calculate confidence improvements over time
   - Optimize skill parameters based on learned patterns

4. **Optional: Integrate with multi-student containers:**
   ```bash
   docker-compose -f docker-compose.rh-ensemble.yml up
   # Then run orchestrator against containerized students
   ```

---

## Summary

The **Autonomous Skill Selector Agent** transforms the orchestrator from a static resource manager into an **intelligent, self-improving system** that:

- ✓ Learns which skills work best for each student
- ✓ Builds confidence from real outcomes
- ✓ Balances exploration and exploitation
- ✓ Continuously optimizes recommendations
- ✓ Operates completely autonomously

After 2+ weeks of operation, the system will have learned optimal skill selections for your specific workload, with high confidence and measurable improvements in quality and efficiency.

