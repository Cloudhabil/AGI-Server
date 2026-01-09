# Run 3-Cycle Alignment & Calibration Test

**Purpose**: Validate system behavior before production
**Time**: 5-15 minutes
**Goal**: Ensure all 6 students execute smoothly, context is preserved, safety limits respected

---

## Quick Start

### Single Command (All-in-One)
```bash
python scripts/alignment_calibration_3cycles.py
```

That's it! The script will:
1. Display test overview
2. Ask for confirmation
3. Run exactly 3 cycles
4. Analyze results
5. Show validation report
6. Tell you if ready for production

---

## Recommended: Three Terminals (Full Visibility)

### Terminal 1: Run Test
```bash
python scripts/alignment_calibration_3cycles.py
```

### Terminal 2: Real-Time Progress Monitor
```bash
python scripts/realtime_alignment_monitor.py alignment_calibration_3cycles
```

Shows live:
- Current cycle and student
- VRAM usage
- Progress to 18 total runs
- What's happening right now

### Terminal 3: System Resources (Optional)
```bash
python scripts/monitor_budget_system.py
```

Shows:
- CPU/RAM/GPU usage
- Resource decisions
- Budget allocation

---

## What Happens

### Cycle 1: Baseline (establish reference)
```
[CYCLE 1] Executing all 6 students
  ✓ Alpha   (28.5s, 3847 MB)
  ✓ Beta    (31.2s, 4389 MB)
  ✓ Gamma   (22.1s, 4401 MB)
  ✓ Delta   (29.3s, 3821 MB)
  ✓ Epsilon (33.5s, 4098 MB)
  ✓ Zeta    (38.9s, 5012 MB)

Result: Ground truth measurements
```

### Cycle 2: Alignment Check (verify consistency)
```
[CYCLE 2] Same 6 students again
  ✓ Alpha   (28.5s, 3847 MB) - Same as C1 ✓
  ✓ Beta    (31.2s, 4389 MB) - Same as C1 ✓
  ✓ Gamma   (22.1s, 4401 MB) - Same as C1 ✓
  ✓ Delta   (29.3s, 3821 MB) - Same as C1 ✓
  ✓ Epsilon (33.5s, 4098 MB) - Same as C1 ✓
  ✓ Zeta    (38.9s, 5012 MB) - Same as C1 ✓

Result: Context preserved, timing consistent
```

### Cycle 3: Calibration (prepare for production)
```
[CYCLE 3] Final check
  ✓ Alpha   (28.5s) - Stable
  ✓ Beta    (31.2s) - Stable
  ✓ Gamma   (22.1s) - Stable
  ✓ Delta   (29.3s) - Stable
  ✓ Epsilon (33.5s) - Stable
  ✓ Zeta    (38.9s) - Stable

Result: Ready for production
```

---

## Success Indicators

### ✅ You'll See This (SYSTEM READY)
```
╔════════════════════════════════════════════════════════════════════════════╗
║                  ✓ SYSTEM ALIGNED & CALIBRATED                            ║
║                  READY FOR PRODUCTION DEPLOYMENT                          ║
╚════════════════════════════════════════════════════════════════════════════╝

✓ PASS - Cycle 1 Complete (6/6 students)
✓ PASS - Cycle 2 Complete (6/6 students)
✓ PASS - Cycle 3 Complete (6/6 students)
✓ PASS - Context Preserved (<10% variance)
✓ PASS - Safety Limits Met (VRAM <85%)
✓ PASS - Database Integrity
✓ PASS - Adaptive Learning Detected

ACTION: Ready for 8-hour production deployment
```

### ⚠️ You Might See This (INVESTIGATE)
```
✓ PASS - Cycle 1 Complete (6/6 students)
✓ PASS - Cycle 2 Complete (6/6 students)
⚠ WARN - Cycle 3 partial (5/6 students)

ACTION: Check which student didn't run, but safe to continue
```

### ❌ If You See This (DON'T DEPLOY)
```
✓ PASS - Cycle 1 Complete (6/6 students)
✗ FAIL - Cycle 2 incomplete (4/6 students)
✗ FAIL - Safety Limits violated (VRAM 92%)

ACTION: Stop, investigate issues, fix before deployment
```

---

## Estimated Duration

| Scenario | Time |
|----------|------|
| **Fast** (simulated, no LLM) | 3-5 minutes |
| **Normal** (real models, fast GPU) | 8-12 minutes |
| **Slow** (CPU inference) | 15+ minutes |

---

## During the Test

### What You're Checking
1. **All 6 students execute**: Every cycle should have all 6 Greek letter agents
2. **Consistent timing**: Student times should match between cycles (±10% OK)
3. **VRAM safety**: Peak usage never exceeds 85% of available
4. **Context preservation**: No data loss between cycles
5. **Database integrity**: All metrics recorded properly

### What You're Monitoring
- Console output from Terminal 1 (main test)
- Real-time monitor in Terminal 2 (live progress)
- System resources in Terminal 3 (optional)

### What Can Go Wrong (and what's normal)
- ✓ Timing varies by 5-10% (normal - cache effects)
- ✓ VRAM varies between cycles (normal - garbage collection)
- ✓ One student skipped if VRAM tight (normal - graceful degradation)
- ⚠ Timing varies >20% (investigate - something slow)
- ✗ Multiple students missing (fix - scheduler issue)
- ✗ VRAM exceeds 85% (fix - reserve margin)

---

## After the Test

### If PASSED ✅
```bash
# Congratulations! Ready for 8-hour deployment

python start_rh_adaptive_ensemble.py --duration 480 --session rh_production
```

### If NEEDS INVESTIGATION ⚠️
```bash
# Check database manually
sqlite3 agents/sessions/alignment_calibration_3cycles/scheduler_history/student_profiles.db

# Query which students ran
SELECT cycle, student, time_seconds, vram_mb
FROM student_runs
ORDER BY cycle, student;

# If mostly OK, can proceed with monitoring
python start_rh_adaptive_ensemble.py --duration 480 --session rh_production
```

### If FAILED ❌
```bash
# Do NOT deploy - investigate issues first
# Check ALIGNMENT_CALIBRATION_GUIDE.md troubleshooting section
# Review orchestrator.py and adaptive_student_scheduler.py
# Fix issues, then re-run 3-cycle test
```

---

## Files You're Using

| File | Purpose |
|------|---------|
| `scripts/alignment_calibration_3cycles.py` | Main test script (runs 3 cycles, analyzes results) |
| `scripts/realtime_alignment_monitor.py` | Live progress monitor (optional but recommended) |
| `scripts/monitor_budget_system.py` | System resource monitor (optional) |
| `ALIGNMENT_CALIBRATION_GUIDE.md` | Detailed guide (reference if issues) |

---

## Key Databases

Test creates/updates databases in:
```
agents/sessions/alignment_calibration_3cycles/scheduler_history/
  └── student_profiles.db
      ├── student_runs (18 rows = 3 cycles × 6 students)
      └── hardware_snapshots (18 rows = 1 per cycle × 6 students)
```

---

## Sample Expected Output

### Test Start
```
================================================================================
  ALIGNMENT & CALIBRATION TEST - 3 CYCLES
================================================================================

SESSION: alignment_calibration_3cycles
DURATION: 5 minutes (3 complete cycles)

Press Enter to start 3-cycle test...
```

### During Execution
```
================================================================================
[CYCLE 1] Adaptive Sequential Research
================================================================================

[HARDWARE] Initial snapshot:
  VRAM:  25.0% (2.7/10.8 GB)
  Status: ✓ SAFE

[PHASE 1] Sequential Student Proposals:
  Executing alpha...  ✓ alpha complete (3000 tokens)
  Executing beta...   ✓ beta complete (3000 tokens)
  Executing gamma...  ✓ gamma complete (3000 tokens)
  Executing delta...  ✓ delta complete (3000 tokens)
  Executing epsilon...  ✓ epsilon complete (3000 tokens)
  Executing zeta...   ✓ zeta complete (3000 tokens)

[SUMMARY] Cycle 1 complete:
  Students completed: 6/6
```

### Test Complete
```
================================================================================
  3-CYCLE TEST COMPLETE
================================================================================

Analyzing results...

────────────────────────────────────────────────────────────────────────────
VALIDATION CHECKLIST
────────────────────────────────────────────────────────────────────────────
  [✓ PASS] Cycle 1 Complete (6/6 students)
  [✓ PASS] Cycle 2 Complete (6/6 students)
  [✓ PASS] Cycle 3 Complete (6/6 students)
  [✓ PASS] Context Preserved (<10% variance)
  [✓ PASS] Safety Limits Met (VRAM <85%)
  [✓ PASS] Database Integrity
  [✓ PASS] Adaptive Learning Detected

╔════════════════════════════════════════════════════════════════════════════╗
║                  ✓ SYSTEM ALIGNED & CALIBRATED                            ║
║                  READY FOR PRODUCTION DEPLOYMENT                          ║
╚════════════════════════════════════════════════════════════════════════════╝
```

---

## Next Steps

### After Successful Test
```bash
# Deploy to production (8+ hours)
python start_rh_adaptive_ensemble.py --duration 480 --session rh_production

# Monitor continuously
python scripts/monitor_budget_system.py
```

### After 8-Hour Session
```bash
# Analyze results
sqlite3 agents/sessions/rh_production/scheduler_history/student_profiles.db

# Query total productivity
SELECT COUNT(*), SUM(tokens) FROM student_runs;
```

---

## Command Reference

```bash
# RUN THE TEST (main command)
python scripts/alignment_calibration_3cycles.py

# MONITOR LIVE (in another terminal)
python scripts/realtime_alignment_monitor.py alignment_calibration_3cycles

# AFTER TEST - if you need to investigate
sqlite3 agents/sessions/alignment_calibration_3cycles/scheduler_history/student_profiles.db

# IF PASSED - deploy to production
python start_rh_adaptive_ensemble.py --duration 480 --session rh_production
```

---

## TL;DR

```bash
# Just run this:
python scripts/alignment_calibration_3cycles.py

# It will tell you if you're ready to deploy
# Takes 5-15 minutes
# Shows clear PASS/FAIL result

# If PASS, you're ready for 8-hour production!
```

---

## Questions During Test?

- **"Is VRAM at X% OK?"**: If <85%, you're safe. >85% is warning.
- **"One student didn't run, is that bad?"**: If VRAM tight, it's graceful degradation. OK if others ran.
- **"Timing different between cycles?"**: ±10% variance is normal. >20% warrants investigation.
- **"How long should this take?"**: 5-15 minutes depending on your system.
- **"Can I stop it early?"**: Yes, just Ctrl+C. Results analyzed from what ran.

---

**You're ready! Run the test and let the system validate itself.**

