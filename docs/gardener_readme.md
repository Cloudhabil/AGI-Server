# Filesystem Gardener - Autonomous File Organization

## Overview

The Filesystem Gardener is an autonomous agent that transforms chaos into order by intelligently organizing files without ever deleting anything. It operates continuously in the background, monitoring for new files and classifying them into a logical taxonomy.

## Philosophy

**"From Chaos to Order, Without Loss"**

- **Zero Deletion Policy**: The Gardener NEVER deletes files, only organizes them
- **Intelligent Classification**: Uses GPIA intelligence + heuristics to categorize artifacts
- **Real-time Operation**: Monitors filesystem and reacts immediately to changes
- **Bidirectional Communication**: Integrates with main GPIA agent for coordination
- **Complete Auditability**: Every file movement is logged in an append-only ledger

## Architecture

```
┌─────────────────────────────────────────┐
│   Filesystem Watcher (watchdog)         │
│   Monitors: *.py, *.json, *.md, etc.   │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   Classification Engine                  │
│   - GPIA-powered (intelligent)          │
│   - Heuristic fallback (pattern-based)  │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   Taxonomy Builder                       │
│   Organizes into logical structure      │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│   Movement Ledger                        │
│   data/ledger/gardener.jsonl            │
└─────────────────────────────────────────┘
```

## Taxonomy Structure

The Gardener organizes files into this hierarchy:

```
skills/
  ├── synthesized/       # Auto-generated skills (e.g., Snowden corpus)
  ├── auto_learned/      # Skills learned through agent training
  ├── ops/               # Operational utility skills
  └── conscience/        # Ethical/oversight skills

evals/
  ├── benchmarks/        # Performance benchmarks
  └── tests/             # Test suites

experiments/
  ├── active/            # Current experiments
  └── archive/           # Completed experiments

scripts/
  ├── executables/       # Standalone scripts
  └── utilities/         # Helper scripts

data/
  ├── ledger/            # Persistent ledger data
  ├── vnand/             # VNAND storage
  └── cache/             # Temporary cache

configs/                 # Configuration files
docs/                    # Documentation
inbox/
  └── unclassified/      # Items with low confidence
```

## Installation

### Dependencies

```bash
pip install watchdog
```

The Gardener uses the `watchdog` library for filesystem monitoring. All other dependencies are standard library.

## Usage

### Option 1: Integrated Mode (via boot.py)

Run the Gardener as an operational mode within the main agent:

```bash
# Start in Gardener mode
python boot.py --mode Gardener

# With verbose logging
python boot.py --mode Gardener --verbose
```

This approach provides full GPIA integration and bidirectional communication.

### Option 2: Standalone Daemon

Run the Gardener as an independent daemon:

```bash
# Start daemon (monitoring only)
python filesystem_gardener_daemon.py

# Start with initial scan of existing files
python filesystem_gardener_daemon.py --scan

# Run without GPIA integration (heuristics only)
python filesystem_gardener_daemon.py --no-gpia

# Custom root directory
python filesystem_gardener_daemon.py --root /path/to/project
```

### Option 3: Programmatic Usage

Integrate the Gardener into your own code:

```python
from pathlib import Path
from core.filesystem_gardener import get_gardener
from core.kernel.substrate import KernelSubstrate

# Initialize with kernel for GPIA intelligence
kernel = KernelSubstrate()
gardener = get_gardener(root=Path.cwd(), kernel=kernel)

# Start autonomous operation
gardener.start()

# Scan existing files
gardener.scan_existing(".")

# Get statistics
stats = gardener.get_stats()
print(f"Processed: {stats['artifacts_processed']}")
```

## Communication Protocol

### Gardener → GPIA Messages

1. **ARTIFACT_DISCOVERED**: New file detected
   ```json
   {
     "artifact_path": "new_skill.py",
     "classification": "SKILL_SYNTHESIZED",
     "timestamp": "2025-01-10T12:00:00"
   }
   ```

2. **ARTIFACT_ORGANIZED**: File moved
   ```json
   {
     "source": "new_skill.py",
     "destination": "skills/synthesized/new_skill.py",
     "classification": "SKILL_SYNTHESIZED"
   }
   ```

3. **STATS_UPDATE**: Periodic statistics
   ```json
   {
     "artifacts_processed": 100,
     "artifacts_organized": 85,
     "queue_size": 5
   }
   ```

### GPIA → Gardener Commands

1. **SCAN_DIRECTORY**: Request scan
   ```json
   {
     "directory": "experiments/"
   }
   ```

2. **ORGANIZE_COMMAND**: Manual organization
   ```json
   {
     "artifact_path": "test.py",
     "classification": "SKILL_OPS"
   }
   ```

3. **SHUTDOWN**: Stop daemon
   ```json
   {}
   ```

## Audit Trail

Every file movement is recorded in the ledger:

**Location**: `data/ledger/gardener.jsonl`

**Format**: JSONL (one JSON object per line)

**Example Entry**:
```json
{
  "timestamp": "2025-01-10T12:00:00",
  "artifact_path": "snowden_skill.py",
  "source_path": "/root/snowden_skill.py",
  "destination_path": "/root/skills/synthesized/snowden_skill.py",
  "classification": "SKILL_SYNTHESIZED",
  "confidence": 0.95,
  "reason": "Snowden skill pattern"
}
```

## Classification Rules

### GPIA-Powered (High Accuracy)

When the kernel is available, the Gardener uses the model router to classify files intelligently.

### Heuristic Fallback (Pattern-Based)

When GPIA is unavailable, heuristics are used:

- **Snowden Skills**: Files matching `snowden_*.py` → `skills/synthesized/`
- **Evaluations**: Files with `eval`, `benchmark`, `test_` → `evals/`
- **Experiments**: Files with `execute_`, `hunt_`, `probe_` → `experiments/active/`
- **Configs**: JSON/YAML/TOML files with "config" → `configs/`
- **Data**: Files in vnand/ledger directories → `data/`

## Confidence Thresholds

- **≥ 0.7**: Auto-organize immediately
- **< 0.7**: Record classification but keep in place (manual review)

## Safety Features

1. **No Deletion**: Files are only moved, never deleted
2. **Conflict Resolution**: Timestamp appended if destination exists
3. **Atomic Moves**: Uses OS-level atomic rename
4. **Full Audit Trail**: Every action logged
5. **Graceful Degradation**: Works without GPIA in heuristic mode

## Monitoring

### Real-time Stats

When running, the Gardener reports statistics every 60 seconds:

```
[STATS] Uptime: 300s | Processed: 42 | Organized: 38 | Queue: 2
[STATS] Classifications:
        SKILL_SYNTHESIZED: 20
        EXPERIMENT_ACTIVE: 10
        EVAL_BENCHMARK: 5
        CONFIG: 3
```

### Querying Stats Programmatically

```python
stats = gardener.get_stats()
print(stats['artifacts_processed'])
print(stats['classifications'])
print(stats['queue_size'])
```

## Troubleshooting

### "watchdog not installed"

```bash
pip install watchdog
```

### "Running without GPIA intelligence"

This is normal if the kernel fails to initialize. The Gardener will use heuristics instead. To force heuristic-only mode:

```bash
python filesystem_gardener_daemon.py --no-gpia
```

### Files not being organized

Check the confidence threshold. Low-confidence classifications (< 0.7) are logged but not auto-organized. Review:

```bash
tail -f data/ledger/gardener.jsonl
```

### Queue backing up

If the queue size keeps growing, the Gardener may be processing slower than files are arriving. This is normal during initial scans.

## Advanced Configuration

### Custom Taxonomy

Edit `core/filesystem_gardener.py` to modify the `ArtifactType` enum:

```python
class ArtifactType(Enum):
    MY_CUSTOM_CATEGORY = "my_directory/subdirectory"
```

### Custom Classification Rules

Add heuristics in `ClassificationEngine._build_heuristics()`:

```python
def _build_heuristics(self):
    return {
        'my_rule': lambda p: 'pattern' in p.name,
        # ... existing rules
    }
```

## Performance

- **Filesystem Monitoring**: Near-zero overhead (watchdog is event-driven)
- **Classification**: ~100ms per file (GPIA) or ~1ms (heuristics)
- **Organization**: ~10ms per file (single atomic rename)
- **Memory**: ~50MB baseline + ~1KB per queued file

## Future Enhancements

- [ ] Interactive CLI for manual classification
- [ ] Machine learning from user corrections
- [ ] Conflict resolution strategies
- [ ] Multi-repository coordination
- [ ] Git integration (organize by commit history)
- [ ] Semantic analysis for unknown file types

## Questions?

See the main `CLAUDE.md` for overall project architecture or inspect the source:

- `core/filesystem_gardener.py` - Main gardener logic
- `core/gpia_bridge.py` - Communication protocol
- `core/modes/gardener.py` - Boot.py integration
- `filesystem_gardener_daemon.py` - Standalone daemon
