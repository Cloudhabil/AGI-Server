# Filesystem Gardener - Quick Start

## Installation (1 minute)

```bash
# Install the only external dependency
pip install watchdog
```

## Running the Gardener (Choose One)

### Option A: Integrated with Main Agent (Recommended)

```bash
python boot.py --mode Gardener
```

**Advantages:**
- Full GPIA intelligence for classification
- Bidirectional communication
- Integrated with main agent kernel
- Unified logging and telemetry

### Option B: Standalone Daemon

```bash
# Monitor filesystem only
python filesystem_gardener_daemon.py

# Scan existing files on startup
python filesystem_gardener_daemon.py --scan
```

**Advantages:**
- Independent operation
- Simpler deployment
- Can run on different root directory

## What Happens?

1. **Filesystem Monitoring Starts**: Watches for new files
2. **Existing Chaos**: Your ~400 untracked files are classified
3. **Auto-Organization**: Files moved to logical locations
4. **Audit Trail**: Every move recorded in `data/ledger/gardener.jsonl`
5. **Stats Reporting**: Every 60 seconds, see progress

## Example Session

```
==========================================
GARDENER MODE - Autonomous File Organization
==========================================

Initializing Filesystem Gardener...
Gardener active. Monitoring filesystem...

[Gardener] execute_final_victory.py → EXPERIMENT_ACTIVE (0.85)
[Gardener] snowden_skill_1.py → SKILL_SYNTHESIZED (0.95)
[Gardener] benchmark_test.py → EVAL_BENCHMARK (0.90)

----------------------------------------
[Stats] Uptime: 60s | Processed: 42 | Organized: 38 | Queue: 2
[Stats] Classifications:
        SKILL_SYNTHESIZED: 300
        EXPERIMENT_ACTIVE: 15
        EVAL_BENCHMARK: 5
        CONFIG: 3
        UNKNOWN: 2
----------------------------------------
```

## Result: Organized Structure

**Before:**
```
CLI-main/
├── execute_final_victory.py
├── snowden_skill_1.py
├── benchmark_test.py
├── ... (400+ files)
```

**After:**
```
CLI-main/
├── skills/
│   └── synthesized/
│       ├── snowden_skill_1.py
│       ├── snowden_skill_2.py
│       └── ... (300+ files)
├── experiments/
│   └── active/
│       ├── execute_final_victory.py
│       └── ... (15+ files)
├── evals/
│   └── benchmarks/
│       └── benchmark_test.py
├── data/
│   └── ledger/
│       └── gardener.jsonl  # Complete audit trail
```

## Verification

Check the audit trail:

```bash
# View recent organization actions
tail -n 20 data/ledger/gardener.jsonl

# Count organized files
grep -c "artifact_path" data/ledger/gardener.jsonl

# Find specific file's history
grep "snowden_skill" data/ledger/gardener.jsonl
```

## Stopping the Gardener

**Integrated Mode:**
```
Press Ctrl+C in the terminal
```

**Standalone Daemon:**
```
Press Ctrl+C in the terminal
```

The Gardener performs a clean shutdown, reporting final statistics.

## Next Steps

1. **Review Classifications**: Check `inbox/unclassified/` for low-confidence items
2. **Adjust Taxonomy**: Edit `core/filesystem_gardener.py` to customize structure
3. **Monitor Ledger**: Track all movements in `data/ledger/gardener.jsonl`
4. **GPIA Commands**: Send commands via the bridge (see GARDENER_README.md)

## Troubleshooting

**Problem**: "watchdog not installed"
```bash
pip install watchdog
```

**Problem**: "Running without GPIA intelligence"
- This is normal - Gardener will use heuristics
- Or force heuristic mode: `python filesystem_gardener_daemon.py --no-gpia`

**Problem**: Files not organizing
- Check confidence threshold (default: 0.7)
- Review ledger: `tail -f data/ledger/gardener.jsonl`
- Low-confidence items go to `inbox/unclassified/`

## Safety Guarantee

**The Gardener NEVER deletes files.**

Every operation is:
- A file move (rename)
- Fully logged
- Reversible

You can always find where a file went by checking the ledger.
