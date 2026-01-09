# RH Adaptive Ensemble - 5-Minute Quick Start

Ready to deploy? Follow these 4 simple steps:

---

## Step 1: Create Fine-Tuned Models (2 min)

```bash
python scripts/finetune_rh_models.py
```

Wait for completion. Should see:
```
[OK] Created rh-alpha:latest
[OK] Created rh-beta:latest
[OK] Created rh-gamma:latest
[OK] Created rh-delta:latest
[OK] Created rh-epsilon:latest
[OK] Created rh-zeta:latest
```

**Verify**:
```bash
ollama list | grep rh-
```

---

## Step 2: Test with 5 Minutes (5 min)

**Terminal 1** - Start test run:
```bash
python start_rh_adaptive_ensemble.py --duration 5 --session test
```

**Terminal 2** - Monitor in real-time (start before or after):
```bash
python scripts/monitor_budget_system.py
```

Watch for:
- ✓ Students executing sequentially
- ✓ VRAM stays below 85%
- ✓ Database being populated
- ✓ Proposals completing

---

## Step 3: Verify Database (1 min)

```bash
sqlite3 agents/sessions/test/scheduler_history/student_profiles.db

# View summary
SELECT student, COUNT(*), AVG(vram_mb) FROM student_runs GROUP BY student;

# Exit
.exit
```

See all 6 students with VRAM/time/tokens recorded ✓

---

## Step 4: Run Production (8+ hours)

```bash
python start_rh_adaptive_ensemble.py --duration 480 --session rh_production
```

Keep `monitor_budget_system.py` running in another terminal for real-time monitoring.

**Expected Output After 8 Hours**:
- 32+ cycles completed
- 100,000+ tokens generated
- All 6 students scheduled regularly
- VRAM never exceeded safety limits
- Database with full history

---

## Key Commands Reference

| Task | Command |
|------|---------|
| **Create fine-tuned models** | `python scripts/finetune_rh_models.py` |
| **Test 5 minutes** | `python start_rh_adaptive_ensemble.py --duration 5 --session test` |
| **Run 8 hours** | `python start_rh_adaptive_ensemble.py --duration 480 --session rh_production` |
| **Monitor real-time** | `python scripts/monitor_budget_system.py` |
| **Query database** | `sqlite3 agents/sessions/rh_production/scheduler_history/student_profiles.db` |
| **List fine-tuned models** | `ollama list \| grep rh-` |
| **Check Ollama status** | `ollama list` |

---

## That's It!

Your RH Adaptive Ensemble is ready to generate 100,000+ tokens of research in 8 hours with intelligent resource management.

For detailed info, see:
- `DEPLOYMENT_CHECKLIST.md` - Full deployment guide
- `RH_ADAPTIVE_ENSEMBLE_GUIDE.md` - Architecture & concepts
- `ADAPTIVE_ENSEMBLE_IMPLEMENTATION.md` - Technical details

