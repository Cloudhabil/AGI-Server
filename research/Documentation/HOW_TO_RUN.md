# How to Run: Autonomous Skill Selector Integration

## Quick Start (Choose Your Path)

### Path 1: Quick Verification (5 minutes)
**Goal:** Verify the system works before committing to long run

```bash
python scripts/test_skill_learning_integration.py
```

**Output:**
- ✓ Skill selector available
- ✓ Orchestrator initialized
- ✓ Skill selection logic working
- ✓ Learning outcomes recorded
- ✓ Quick 1-minute orchestration test

**Next:** If all tests pass, proceed to Path 3

---

### Path 2: See Learning in Action (10-15 minutes)
**Goal:** Watch the agent select skills and record learning

```bash
python orchestrator_predictive_sequential.py --duration 10 --session test_learning
```

**What You'll See:**
```
[CYCLE 1] Predictive Sequential Execution

[STUDENT ALPHA]
  [PREDICT] Predict: 0GB used + 4GB model = 4GB (33%) -> OK
  [BOOT UP] Loading nous-hermes:7b into VRAM... [OK] 3.2s
  [SOFT WARMUP] Warming cache... [OK] 10 tokens, 42.3 tok/s

  [SKILL SELECT] riemann_deep_analysis           ← AGENT CHOSE THIS
    Pattern: reasoning | Confidence: 0% | Method: exploration

  [EXECUTE] Running inference... [OK] 287 tokens, 35.4 tok/s
  [CONTEXT SAVE] 3 insights extracted

  [LEARNING] Recorded outcome: riemann_deep_analysis -> Q=0.88  ← AGENT LEARNED

[STUDENT BETA]
  [PREDICT] Predict: 4GB used + 4GB model = 8GB (65%) -> OK
  ...
```

**At End:** Final report showing:
```
Skill Selection Learning:
  Skills selected: 6
  Unique skills learned: 3
  Average confidence: 0.15
  Average quality: 0.87

AUTONOMOUS SKILL SELECTOR - LEARNING SUMMARY:
Learned patterns: 2
Average confidence: 0.15/1.00
Average success rate: 100%
```

**Next:** Satisfied? Move to Path 3 for long production run

---

### Path 3: Production Learning (2+ weeks)
**Goal:** Accumulate real learning data, reach high confidence

```bash
python orchestrator_predictive_sequential.py --duration 20160 --session rh_production_v1
```

**Duration Notes:**
- `--duration 10` = 10 minutes (1 cycle)
- `--duration 60` = 1 hour (4-5 cycles)
- `--duration 1440` = 1 day (60+ cycles)
- `--duration 10080` = 1 week (300+ cycles)
- `--duration 20160` = 2 weeks (600+ cycles) ← RECOMMENDED

**What Happens:**
```
[MINUTE 1-30] Early exploration
  Agent selecting skills randomly
  Confidence: 0.07-0.13
  Building initial observations

[HOUR 1-4] Learning phase
  Agent sees patterns emerging
  Confidence: 0.20-0.40
  Preferences becoming visible

[DAY 1] Clear patterns
  Agent has strong preferences
  Confidence: 0.40-0.60
  System operating smoothly

[WEEK 1] High confidence
  Agent mostly exploiting
  Confidence: 0.60-0.80
  Excellent consistency

[WEEK 2+] Optimized
  Agent fully confident
  Confidence: 0.90-1.0
  Discovering synergies
```

**Let it run:**
- In background: `nohup python orchestrator_... &`
- In separate terminal: Monitor progress
- Don't interrupt (learning is continuous)

---

## Monitoring Progress

### Option 1: Watch Real-Time Metrics (Every 60 seconds)

```bash
watch -n 60 'sqlite3 agents/sessions/rh_production_v1/metrics.db "SELECT COUNT(*), COUNT(DISTINCT skill_selected), ROUND(AVG(skill_confidence),2), ROUND(AVG(throughput),1) FROM executions WHERE skill_selected IS NOT NULL;"'
```

**Output Format:**
```
count | unique_skills | avg_confidence | avg_throughput
24    | 3             | 0.25           | 35.4
48    | 3             | 0.42           | 36.1
72    | 3             | 0.58           | 36.8
```

**What to Look For:**
- count: Increases over time (executions accumulating)
- unique_skills: Should stabilize to 1-3
- avg_confidence: Should increase 0.07 → 0.70+
- avg_throughput: Should be consistent (30-40 tok/s)

### Option 2: Skill Preference per Student

```bash
sqlite3 agents/sessions/rh_production_v1/metrics.db "
SELECT student, skill_selected, COUNT(*),
       ROUND(AVG(quality_score),2) as avg_quality,
       ROUND(MAX(skill_confidence),2) as max_confidence
FROM executions
WHERE skill_selected IS NOT NULL
GROUP BY student, skill_selected
ORDER BY student, COUNT(*) DESC;"
```

**Output Example:**
```
student | skill_selected    | count | avg_quality | max_confidence
alpha   | riemann_analysis  | 8     | 0.88        | 0.27
alpha   | synthesis         | 2     | 0.85        | 0.13
beta    | synthesis         | 6     | 0.86        | 0.20
beta    | summary           | 4     | 0.80        | 0.13
```

### Option 3: Agent's Internal Knowledge

```bash
python -c "
from skills.autonomous_skill_selector import get_skill_selector_agent
agent = get_skill_selector_agent()
print('\n=== AGENT STATUS ===')
agent.print_agent_status()
print('\n=== LEARNED PATTERNS ===')
agent.print_learned_knowledge()
"
```

**Output Example:**
```
=== AGENT STATUS ===
AUTONOMOUS SKILL SELECTOR AGENT - STATUS
Learning Progress:
  Learned patterns: 4
  Average confidence: 0.42/1.00
  Average success rate: 95%
  Exploration rate: 15%

=== LEARNED PATTERNS ===
Model: alpha
  reasoning
    riemann_deep_analysis SR=100.0% Q=0.88 C=0.27 n=4
    zeta_function_synthesis SR=80.0% Q=0.82 C=0.07 n=2
```

---

## Understanding the Output

### Key Lines to Watch

#### Skill Selection Happening
```
[SKILL SELECT] riemann_deep_analysis
  Pattern: reasoning | Confidence: 75% | Method: exploitation
```

✓ **GOOD**: Agent selected a skill based on learned confidence
- If confidence >= 70% → "exploitation" (using proven skill)
- If confidence < 70% → "exploration" (trying alternatives)

#### Learning Being Recorded
```
[LEARNING] Recorded outcome: riemann_deep_analysis -> Q=0.88
```

✓ **GOOD**: Agent recorded the outcome for learning
- Q (quality) should be 0.80-0.95
- If Q is consistently high, skill is working well

#### Final Report
```
Skill Selection Learning:
  Skills selected: 24
  Unique skills learned: 3
  Average confidence: 0.65
  Average quality: 0.88
```

✓ **GOOD**: Metrics show learning progress
- Average confidence increasing over time
- Average quality stable and high (0.85+)
- Unique skills stabilizing (not exploring too much)

---

## Troubleshooting During Run

### Problem: Skill selector says "Error"
```
[SKILL SELECT] Error: ...
```

**Solution:** Check skill selector memory
```bash
sqlite3 skills/core/selector_memory.db ".tables"
```

**Fix:** Ensure database exists and has tables

---

### Problem: No skills being selected
```
[SKILL SELECT] Error: No learned patterns yet
```

**This is NORMAL** on first run. It means:
- Agent doesn't have data yet
- Let it run to accumulate observations
- After ~5 cycles, confidence will appear

---

### Problem: Confidence not increasing
```
Average confidence: 0.07 (stuck)
```

**Cause:** Not enough observations
**Solution:** Run longer
- Need 5+ observations per pattern for confidence to increase
- After 15 observations, confidence reaches 1.0
- Quick test won't show learning (run 1+ day minimum)

---

### Problem: Throughput varying wildly
```
Cycle 1: 16 tok/s
Cycle 2: 38 tok/s
Cycle 3: 41 tok/s
```

**This is NORMAL:**
- First run shows cold model (soft warmup works)
- Second+ runs show warm model
- After soft warmup, should stabilize around 35-40 tok/s

---

## Expected Timeline

### First 5 Minutes
- ✓ Skills selected: YES (might be random)
- ✓ Outcomes recorded: YES
- ✓ Confidence values: 0.07-0.13 (emerging)

### First Hour (4-5 cycles)
- ✓ Skills selected: YES (patterns emerging)
- ✓ Outcomes recorded: YES
- ✓ Confidence values: 0.13-0.35 (growing)
- ✓ Preferences visible: YES (which skill used most)

### Day 1 (60-80 cycles)
- ✓ Clear skill preferences: YES
- ✓ Average confidence: 0.40-0.60
- ✓ Quality consistent: YES (0.85-0.95)
- ✓ VRAM under 85%: YES (should be < 70%)

### Week 1 (300+ cycles)
- ✓ High confidence patterns: YES (0.60-0.80)
- ✓ Mostly exploitation: YES (80%+ of decisions)
- ✓ Excellent consistency: YES (quality variance < 5%)
- ✓ System optimized: YES (for your workload)

### Week 2+ (600+ cycles)
- ✓ Full confidence: YES (0.90-1.0)
- ✓ Optimal skill selection: YES
- ✓ Discovering synergies: YES
- ✓ Production ready: YES (can use results)

---

## Advanced: Analyzing Results After Run

### After 1 Week: Identify Best Skills

```bash
sqlite3 agents/sessions/rh_production_v1/metrics.db "
SELECT skill_selected, COUNT(*) as uses,
       ROUND(AVG(quality_score),3) as avg_quality,
       ROUND(AVG(skill_confidence),3) as avg_confidence
FROM executions
WHERE skill_selected IS NOT NULL
GROUP BY skill_selected
ORDER BY avg_quality DESC;"
```

**Output Example:**
```
skill_selected         | uses | avg_quality | avg_confidence
riemann_deep_analysis  | 52   | 0.903       | 0.563
zeta_function_synthesis| 34   | 0.877       | 0.412
synthesis_core         | 18   | 0.842       | 0.287
```

### After 2 Weeks: Identify Skill Synergies

Which skills appeared together successfully?

```bash
sqlite3 agents/sessions/rh_production_v1/metrics.db "
SELECT student, skill_selected, COUNT(*) as uses,
       ROUND(AVG(quality_score),3) as quality,
       ROUND(AVG(skill_confidence),3) as confidence
FROM executions
WHERE skill_selected IS NOT NULL
GROUP BY student, skill_selected
ORDER BY student, quality DESC;"
```

### Export Learning for Later Reference

```bash
sqlite3 agents/sessions/rh_production_v1/metrics.db ".mode csv" ".headers on" "
SELECT * FROM skill_selections
WHERE success = 1 AND quality_score > 0.85
ORDER BY confidence DESC;" > learned_patterns.csv
```

---

## Best Practices

### 1. Let It Run Uninterrupted
- Don't stop and restart
- Continuous operation is best
- Stopping loses momentum

### 2. Monitor But Don't Obsess
- Check progress once per day
- Watch for anomalies, not noise
- Short-term variance is normal

### 3. Document Starting Point
```bash
echo "Started: $(date)" > agents/sessions/rh_production_v1/START.txt
```

### 4. Save Results
```bash
# After run completes
cp -r agents/sessions/rh_production_v1 agents/sessions/rh_production_v1_backup
```

### 5. Share Learning
```bash
# Export readable report
sqlite3 agents/sessions/rh_production_v1/metrics.db \
  ".mode list" ".separator '\n'" ".width 20 20 20" \
  "SELECT 'LEARNING RESULTS' AS header;
   SELECT skill_selected, COUNT(*), ROUND(AVG(quality_score),2)
   FROM executions WHERE skill_selected IS NOT NULL
   GROUP BY skill_selected;"
```

---

## Summary

### Quick Path (5 min)
```bash
python scripts/test_skill_learning_integration.py
```

### Learning Path (10-15 min)
```bash
python orchestrator_predictive_sequential.py --duration 10 --session test_learning
```

### Production Path (2+ weeks)
```bash
python orchestrator_predictive_sequential.py --duration 20160 --session rh_production_v1
```

**Then monitor, let it run, analyze results.**

The system will learn autonomously. No intervention needed.

✓ System is ready. Start whenever you're ready.

