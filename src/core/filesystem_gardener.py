"""
Filesystem Gardener: Autonomous File Organization Agent

Purpose: Transform chaos into order through intelligent classification and organization.
Philosophy: Preserve everything, organize relentlessly, communicate continuously.

Architecture:
1. Filesystem Watcher: Monitors for new files/folders in real-time
2. Classification Engine: Uses GPIA intelligence to categorize artifacts
3. Taxonomy Builder: Creates logical structure from chaos
4. Movement Ledger: Tracks every file relocation for auditability
5. GPIA Bridge: Bidirectional communication channel with main agent

Zero Deletion Policy: This agent NEVER deletes. Only organizes.
"""

import sys
import time
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue

# Filesystem watching
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileCreatedEvent, DirCreatedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("[GARDENER] Warning: watchdog not installed. Run: pip install watchdog")


class ArtifactType(Enum):
    """Classification taxonomy for discovered artifacts"""
    SKILL_SYNTHESIZED = "skills/synthesized"
    SKILL_LEARNED = "skills/auto_learned"
    SKILL_CONSCIENCE = "skills/conscience"
    SKILL_OPS = "skills/ops"

    EVAL_BENCHMARK = "evals/benchmarks"
    EVAL_TEST = "evals/tests"

    EXPERIMENT_ACTIVE = "experiments/active"
    EXPERIMENT_ARCHIVE = "experiments/archive"

    SCRIPT_EXECUTABLE = "scripts/executables"
    SCRIPT_UTILITY = "scripts/utilities"

    DATA_LEDGER = "data/ledger"
    DATA_VNAND = "data/vnand"
    DATA_CACHE = "data/cache"

    CONFIG = "configs"
    DOCS = "docs"

    UNKNOWN = "inbox/unclassified"


@dataclass
class FileArtifact:
    """Represents a discovered file artifact"""
    path: str
    size: int
    created: float
    signature: str  # sha256 hash
    classification: Optional[ArtifactType] = None
    metadata: Dict = None

    def to_dict(self):
        return {
            **asdict(self),
            'classification': self.classification.value if self.classification else None
        }


@dataclass
class OrganizationAction:
    """Records a file organization action"""
    timestamp: str
    artifact_path: str
    source_path: str
    destination_path: str
    classification: str
    confidence: float
    reason: str

    def to_ledger_entry(self) -> str:
        """Convert to JSONL ledger format"""
        return json.dumps(asdict(self))


class ClassificationEngine:
    """
    Intelligent file classifier using GPIA model.
    Falls back to heuristics when GPIA unavailable.
    """

    def __init__(self, kernel=None):
        self.kernel = kernel
        self.heuristics = self._build_heuristics()

    def _build_heuristics(self) -> Dict[str, Callable]:
        """Build pattern-based classification rules"""
        return {
            'snowden_skill': lambda p: 'snowden_' in p.name and p.suffix == '.py',
            'skill_general': lambda p: p.parent.name in ['synthesized', 'ops', 'auto_learned', 'conscience'],
            'eval': lambda p: 'eval' in p.name or 'benchmark' in p.name or 'test_' in p.name,
            'experiment': lambda p: any(x in p.name.lower() for x in ['execute_', 'hunt_', 'probe_', 'scan_', 'diagnose_']),
            'config': lambda p: p.suffix in ['.json', '.yaml', '.yml', '.toml'] and 'config' in p.name.lower(),
            'data_vnand': lambda p: 'vnand' in str(p.parent),
            'data_ledger': lambda p: 'ledger' in str(p.parent),
        }

    def classify(self, artifact: FileArtifact) -> tuple[ArtifactType, float, str]:
        """
        Classify an artifact.

        Returns:
            (classification, confidence, reason)
        """
        path = Path(artifact.path)

        # Try GPIA-powered classification first
        if self.kernel:
            gpia_result = self._classify_via_gpia(artifact)
            if gpia_result:
                return gpia_result

        # Fallback to heuristics
        return self._classify_via_heuristics(path)

    def _classify_via_gpia(self, artifact: FileArtifact) -> Optional[tuple]:
        """Ask GPIA to classify the artifact"""
        try:
            router = self.kernel.router
            prompt = f"""Classify this file artifact into a category:

File: {artifact.path}
Size: {artifact.size} bytes
Signature: {artifact.signature[:16]}...

Categories:
- SKILL_SYNTHESIZED: Auto-generated skills from external intelligence
- SKILL_LEARNED: Skills learned through agent training
- SKILL_OPS: Operational utility skills
- EVAL_BENCHMARK: Performance benchmarks and tests
- EXPERIMENT_ACTIVE: Active experimental code
- SCRIPT_EXECUTABLE: Standalone executable scripts
- CONFIG: Configuration files
- DATA_LEDGER: Persistent ledger data
- UNKNOWN: Cannot classify

Respond in JSON: {{"category": "...", "confidence": 0.0-1.0, "reason": "..."}}"""

            response = router.query(prompt, task="intent_parsing", max_tokens=200)
            result = json.loads(response)

            category_name = result.get('category', 'UNKNOWN')
            category = ArtifactType[category_name]
            confidence = float(result.get('confidence', 0.5))
            reason = result.get('reason', 'GPIA classification')

            return (category, confidence, reason)

        except Exception as e:
            print(f"[GARDENER] GPIA classification failed: {e}")
            return None

    def _classify_via_heuristics(self, path: Path) -> tuple[ArtifactType, float, str]:
        """Pattern-based classification"""

        # Snowden synthesized skills
        if self.heuristics['snowden_skill'](path):
            return (ArtifactType.SKILL_SYNTHESIZED, 0.95, "Snowden skill pattern")

        # General skills
        if self.heuristics['skill_general'](path):
            if 'synthesized' in str(path):
                return (ArtifactType.SKILL_SYNTHESIZED, 0.9, "In synthesized directory")
            elif 'ops' in str(path):
                return (ArtifactType.SKILL_OPS, 0.9, "In ops directory")
            elif 'auto_learned' in str(path):
                return (ArtifactType.SKILL_LEARNED, 0.9, "In auto_learned directory")

        # Evals
        if self.heuristics['eval'](path):
            return (ArtifactType.EVAL_BENCHMARK, 0.85, "Evaluation pattern")

        # Experiments
        if self.heuristics['experiment'](path):
            return (ArtifactType.EXPERIMENT_ACTIVE, 0.8, "Experimental script pattern")

        # Config
        if self.heuristics['config'](path):
            return (ArtifactType.CONFIG, 0.9, "Configuration file")

        # Data
        if self.heuristics['data_vnand'](path):
            return (ArtifactType.DATA_VNAND, 0.95, "VNAND data")
        if self.heuristics['data_ledger'](path):
            return (ArtifactType.DATA_LEDGER, 0.95, "Ledger data")

        # Unknown
        return (ArtifactType.UNKNOWN, 0.3, "No matching pattern")


class MovementLedger:
    """
    Tracks all file movements for auditability.
    Implements append-only JSONL log.
    """

    def __init__(self, ledger_path: Path):
        self.ledger_path = ledger_path
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, action: OrganizationAction):
        """Append action to ledger"""
        with open(self.ledger_path, 'a', encoding='utf-8') as f:
            f.write(action.to_ledger_entry() + '\n')

    def get_history(self, artifact_path: str = None) -> List[OrganizationAction]:
        """Retrieve movement history"""
        if not self.ledger_path.exists():
            return []

        history = []
        with open(self.ledger_path, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line)
                action = OrganizationAction(**entry)
                if artifact_path is None or action.artifact_path == artifact_path:
                    history.append(action)

        return history


class TaxonomyBuilder:
    """
    Creates and maintains the logical directory structure.
    """

    def __init__(self, root: Path):
        self.root = root
        self._ensure_structure()

    def _ensure_structure(self):
        """Create base taxonomy directories"""
        base_dirs = [
            "skills/synthesized",
            "skills/auto_learned",
            "skills/ops",
            "skills/conscience",
            "evals/benchmarks",
            "evals/tests",
            "experiments/active",
            "experiments/archive",
            "scripts/executables",
            "scripts/utilities",
            "data/ledger",
            "data/vnand",
            "data/cache",
            "configs",
            "docs",
            "inbox/unclassified"
        ]

        for dir_path in base_dirs:
            (self.root / dir_path).mkdir(parents=True, exist_ok=True)

    def get_destination(self, classification: ArtifactType, filename: str) -> Path:
        """Get destination path for classified artifact"""
        return self.root / classification.value / filename


class FilesystemWatcher(FileSystemEventHandler):
    """
    Monitors filesystem for new artifacts.
    Feeds discovery queue for classification.
    """

    def __init__(self, discovery_queue: queue.Queue, root: Path):
        self.queue = discovery_queue
        self.root = root

    def on_created(self, event):
        """Handle new file/folder creation"""
        if event.is_directory:
            return

        # Ignore hidden files and system files
        path = Path(event.src_path)
        if path.name.startswith('.') or path.name.startswith('__'):
            return

        # Create artifact record
        try:
            artifact = FileArtifact(
                path=str(path.relative_to(self.root)),
                size=path.stat().st_size,
                created=time.time(),
                signature=self._compute_signature(path),
                metadata={'absolute_path': str(path)}
            )
            self.queue.put(artifact)
        except Exception as e:
            print(f"[WATCHER] Error processing {path}: {e}")

    def _compute_signature(self, path: Path) -> str:
        """Compute SHA256 hash of file"""
        try:
            hasher = hashlib.sha256()
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return "00" * 32  # Fallback hash


class FilesystemGardener:
    """
    Main orchestrator for autonomous file organization.

    Lifecycle:
    1. Watch filesystem for new artifacts
    2. Classify using GPIA + heuristics
    3. Organize into taxonomy
    4. Record in ledger
    5. Notify GPIA of changes
    """

    def __init__(self, root: Path, kernel=None, gpia_callback: Callable = None):
        self.root = Path(root)
        self.kernel = kernel
        self.gpia_callback = gpia_callback

        # Core components
        self.classifier = ClassificationEngine(kernel)
        self.ledger = MovementLedger(self.root / "data" / "ledger" / "gardener.jsonl")
        self.taxonomy = TaxonomyBuilder(self.root)

        # Processing queue
        self.discovery_queue = queue.Queue()

        # Statistics
        self.stats = {
            'artifacts_processed': 0,
            'artifacts_organized': 0,
            'classifications': {},
            'started_at': datetime.now().isoformat()
        }

        # Watchdog setup
        if WATCHDOG_AVAILABLE:
            self.observer = Observer()
            self.watcher = FilesystemWatcher(self.discovery_queue, self.root)
        else:
            self.observer = None
            self.watcher = None

    def start(self):
        """Start autonomous operation"""
        print(f"[GARDENER] Starting Filesystem Gardener at {self.root}")

        # Start filesystem watcher
        if self.observer:
            self.observer.schedule(self.watcher, str(self.root), recursive=True)
            self.observer.start()
            print("[GARDENER] Filesystem watcher active")
        else:
            print("[GARDENER] WARNING: Running without filesystem watcher")

        # Start processing loop in background
        self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
        self.processing_thread.start()

        print("[GARDENER] Processing loop active")

    def stop(self):
        """Stop autonomous operation"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        print("[GARDENER] Filesystem Gardener stopped")

    def _processing_loop(self):
        """Background processing of discovered artifacts"""
        while True:
            try:
                # Get artifact from queue (blocking with timeout)
                artifact = self.discovery_queue.get(timeout=1.0)
                self._process_artifact(artifact)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[GARDENER] Processing error: {e}")

    def _process_artifact(self, artifact: FileArtifact):
        """
        Process a single artifact:
        1. Classify
        2. Organize
        3. Record
        4. Notify GPIA
        """
        print(f"[GARDENER] Processing: {artifact.path}")

        # Classify
        classification, confidence, reason = self.classifier.classify(artifact)
        artifact.classification = classification

        # Update stats
        self.stats['artifacts_processed'] += 1
        self.stats['classifications'][classification.value] = \
            self.stats['classifications'].get(classification.value, 0) + 1

        # Only organize if confidence is high enough
        if confidence >= 0.7:
            self._organize_artifact(artifact, confidence, reason)
        else:
            print(f"[GARDENER] Low confidence ({confidence:.2f}), keeping in place: {artifact.path}")
            # Still record for future manual review
            self._record_classification(artifact, confidence, reason, organized=False)

        # Notify GPIA if callback provided
        if self.gpia_callback:
            try:
                self.gpia_callback({
                    'event': 'artifact_processed',
                    'artifact': artifact.to_dict(),
                    'classification': classification.value,
                    'confidence': confidence
                })
            except Exception as e:
                print(f"[GARDENER] GPIA notification failed: {e}")

    def _organize_artifact(self, artifact: FileArtifact, confidence: float, reason: str):
        """Move artifact to its classified location"""
        source = Path(artifact.metadata['absolute_path'])
        destination = self.taxonomy.get_destination(artifact.classification, source.name)

        # Prevent organizing artifacts already in correct location
        try:
            if source.resolve().parent == destination.parent:
                print(f"[GARDENER] Already organized: {artifact.path}")
                return
        except Exception:
            pass

        # Handle filename conflicts
        if destination.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = destination.stem
            suffix = destination.suffix
            destination = destination.parent / f"{stem}_{timestamp}{suffix}"

        # Move file
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            source.rename(destination)

            # Record action
            action = OrganizationAction(
                timestamp=datetime.now().isoformat(),
                artifact_path=artifact.path,
                source_path=str(source),
                destination_path=str(destination),
                classification=artifact.classification.value,
                confidence=confidence,
                reason=reason
            )
            self.ledger.record(action)

            self.stats['artifacts_organized'] += 1
            print(f"[GARDENER] Organized: {source.name} → {artifact.classification.value} (confidence: {confidence:.2f})")

        except Exception as e:
            print(f"[GARDENER] Failed to organize {artifact.path}: {e}")

    def _record_classification(self, artifact: FileArtifact, confidence: float, reason: str, organized: bool):
        """Record classification without moving file"""
        action = OrganizationAction(
            timestamp=datetime.now().isoformat(),
            artifact_path=artifact.path,
            source_path=artifact.metadata['absolute_path'],
            destination_path=artifact.metadata['absolute_path'],  # Same location
            classification=artifact.classification.value,
            confidence=confidence,
            reason=f"Not organized (confidence {confidence:.2f}): {reason}"
        )
        self.ledger.record(action)

    def scan_existing(self, directory: str = "."):
        """Scan existing files and organize them"""
        scan_path = self.root / directory
        print(f"[GARDENER] Scanning existing files in {scan_path}...")

        # Exclusion list for metabolic efficiency
        # (venv, models, build artifacts consume descriptors without value)
        EXCLUDED_DIRS = {
            'venv', 'env', '.venv',  # Virtual environments
            'models', 'runs',  # ML model storage (71G + 3.8G)
            'node_modules', 'bower_components',  # JS dependencies
            '__pycache__', '.pytest_cache', '.mypy_cache',  # Python cache
            '.git', '.svn', '.hg',  # Version control
            'build', 'dist', '*.egg-info',  # Build artifacts
            'snowden_archive', 'snowden-archive-master',  # Already archived
            'data/archives',  # ZIP substrates (separate loading path)
        }

        count = 0
        skipped = 0
        for path in scan_path.rglob("*"):
            # Check if path contains any excluded directory
            path_parts = set(path.relative_to(self.root).parts)
            if any(excluded in path_parts or any(part.startswith(excluded.rstrip('*')) for part in path_parts)
                   for excluded in EXCLUDED_DIRS):
                skipped += 1
                continue

            if path.is_file() and not path.name.startswith('.'):
                try:
                    artifact = FileArtifact(
                        path=str(path.relative_to(self.root)),
                        size=path.stat().st_size,
                        created=path.stat().st_ctime,
                        signature=self.watcher._compute_signature(path) if self.watcher else "00"*32,
                        metadata={'absolute_path': str(path)}
                    )
                    self.discovery_queue.put(artifact)
                    count += 1
                except Exception as e:
                    print(f"[GARDENER] Error scanning {path}: {e}")

        print(f"[GARDENER] Queued {count} existing files for processing")
        print(f"[GARDENER] Skipped {skipped} files in excluded directories (venv, models, build artifacts)")

    def get_stats(self) -> Dict:
        """Get current statistics"""
        return {
            **self.stats,
            'queue_size': self.discovery_queue.qsize(),
            'uptime': (datetime.now() - datetime.fromisoformat(self.stats['started_at'])).total_seconds()
        }


def get_gardener(root: Path = None, kernel=None, gpia_callback: Callable = None) -> FilesystemGardener:
    """Factory function to create gardener instance"""
    if root is None:
        root = Path.cwd()
    return FilesystemGardener(root, kernel, gpia_callback)


if __name__ == "__main__":
    # Standalone test mode
    print("Filesystem Gardener - Standalone Mode")

    root = Path(__file__).parent.parent
    gardener = get_gardener(root)

    try:
        gardener.start()
        print("\nGardener running. Press Ctrl+C to stop.\n")

        # Report stats every 30 seconds
        while True:
            time.sleep(30)
            stats = gardener.get_stats()
            print(f"\n[STATS] Processed: {stats['artifacts_processed']} | "
                  f"Organized: {stats['artifacts_organized']} | "
                  f"Queue: {stats['queue_size']}")

    except KeyboardInterrupt:
        print("\nStopping...")
        gardener.stop()
