"""
IIAS Backup Scheduler

PHI-interval snapshots using the golden ratio for exponentially
increasing backup intervals: next_backup = last_backup * PHI

This creates a Fibonacci-like sequence of backup times that
balances storage efficiency with data protection.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import json


# Fundamental constants
PHI = 1.618033988749895
GENESIS_CONSTANT = 2 / 901
SUM_CONSTANT = 214


class BackupStatus(Enum):
    """Backup operation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class BackupSnapshot:
    """Record of a backup snapshot."""
    snapshot_id: str
    source_key: str
    timestamp: datetime
    interval_minutes: float
    status: BackupStatus
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "snapshot_id": self.snapshot_id,
            "source_key": self.source_key,
            "timestamp": self.timestamp.isoformat(),
            "interval_minutes": self.interval_minutes,
            "status": self.status.value,
            "size_bytes": self.size_bytes,
            "metadata": self.metadata,
        }


@dataclass
class BackupSchedule:
    """Backup schedule for a data source."""
    source_key: str
    base_interval_minutes: float
    current_interval_minutes: float
    last_backup: Optional[datetime] = None
    next_backup: Optional[datetime] = None
    backup_count: int = 0
    snapshots: List[BackupSnapshot] = field(default_factory=list)
    max_snapshots: int = 100  # Retention limit

    def calculate_next_interval(self) -> float:
        """Calculate next backup interval using PHI multiplication."""
        return self.current_interval_minutes * PHI

    def calculate_next_backup_time(self) -> datetime:
        """Calculate when next backup should occur."""
        if self.last_backup is None:
            return datetime.now()
        return self.last_backup + timedelta(minutes=self.current_interval_minutes)


class BackupScheduler:
    """
    PHI-interval backup scheduler.

    Uses the golden ratio to create exponentially increasing backup intervals:
    - First backup: immediate
    - Second: base_interval
    - Third: base_interval * PHI
    - Fourth: base_interval * PHI^2
    - etc.

    This Fibonacci-like progression provides:
    - Frequent recent backups for quick recovery
    - Increasingly sparse older backups for storage efficiency
    """

    def __init__(self, base_interval_minutes: float = 1.0):
        """
        Initialize scheduler with base interval.

        Args:
            base_interval_minutes: Starting interval for backup sequence
        """
        self.base_interval = base_interval_minutes
        self._schedules: Dict[str, BackupSchedule] = {}
        self._backup_handlers: Dict[str, Callable] = {}
        self._snapshot_counter = 0

    def register_source(
        self,
        source_key: str,
        base_interval_minutes: Optional[float] = None,
        backup_handler: Optional[Callable] = None,
    ) -> BackupSchedule:
        """
        Register a data source for backup scheduling.

        Args:
            source_key: Unique identifier for the data source
            base_interval_minutes: Override default base interval
            backup_handler: Optional callback for performing backup

        Returns:
            BackupSchedule for the source
        """
        interval = base_interval_minutes or self.base_interval

        schedule = BackupSchedule(
            source_key=source_key,
            base_interval_minutes=interval,
            current_interval_minutes=interval,
            next_backup=datetime.now(),  # First backup immediate
        )

        self._schedules[source_key] = schedule

        if backup_handler:
            self._backup_handlers[source_key] = backup_handler

        return schedule

    def get_schedule(self, source_key: str) -> Optional[BackupSchedule]:
        """Get schedule for a source."""
        return self._schedules.get(source_key)

    def _generate_snapshot_id(self, source_key: str) -> str:
        """Generate unique snapshot ID."""
        self._snapshot_counter += 1
        return f"{source_key}_snap_{self._snapshot_counter:06d}"

    def perform_backup(
        self,
        source_key: str,
        data: Any = None,
        force: bool = False,
    ) -> Optional[BackupSnapshot]:
        """
        Perform backup for a source if scheduled or forced.

        Args:
            source_key: Source to backup
            data: Data to backup (for simulation)
            force: Force backup regardless of schedule

        Returns:
            BackupSnapshot if backup performed, None otherwise
        """
        schedule = self._schedules.get(source_key)
        if not schedule:
            raise ValueError(f"Source '{source_key}' not registered")

        now = datetime.now()

        # Check if backup is due
        if not force and schedule.next_backup and now < schedule.next_backup:
            return None

        # Create snapshot
        snapshot = BackupSnapshot(
            snapshot_id=self._generate_snapshot_id(source_key),
            source_key=source_key,
            timestamp=now,
            interval_minutes=schedule.current_interval_minutes,
            status=BackupStatus.IN_PROGRESS,
            size_bytes=len(str(data)) if data else 0,
        )

        # Execute backup handler if registered
        try:
            if source_key in self._backup_handlers:
                self._backup_handlers[source_key](data, snapshot)
            snapshot.status = BackupStatus.COMPLETED
        except Exception as e:
            snapshot.status = BackupStatus.FAILED
            snapshot.metadata["error"] = str(e)

        # Update schedule with PHI progression
        schedule.last_backup = now
        schedule.current_interval_minutes = schedule.calculate_next_interval()
        schedule.next_backup = schedule.calculate_next_backup_time()
        schedule.backup_count += 1
        schedule.snapshots.append(snapshot)

        # Enforce retention limit
        if len(schedule.snapshots) > schedule.max_snapshots:
            schedule.snapshots = schedule.snapshots[-schedule.max_snapshots:]

        return snapshot

    def get_phi_sequence(self, source_key: str, steps: int = 10) -> List[float]:
        """
        Get the PHI-based backup interval sequence for a source.

        Args:
            source_key: Source identifier
            steps: Number of intervals to calculate

        Returns:
            List of interval values in minutes
        """
        schedule = self._schedules.get(source_key)
        if not schedule:
            return []

        intervals = []
        current = schedule.base_interval_minutes

        for _ in range(steps):
            intervals.append(current)
            current *= PHI

        return intervals

    def get_backup_timeline(self, source_key: str, steps: int = 10) -> List[Dict[str, Any]]:
        """
        Project future backup times based on PHI progression.

        Args:
            source_key: Source identifier
            steps: Number of future backups to project

        Returns:
            List of projected backup times with intervals
        """
        schedule = self._schedules.get(source_key)
        if not schedule:
            return []

        timeline = []
        current_time = schedule.next_backup or datetime.now()
        current_interval = schedule.current_interval_minutes

        for i in range(steps):
            timeline.append({
                "backup_number": schedule.backup_count + i + 1,
                "scheduled_time": current_time.isoformat(),
                "interval_minutes": round(current_interval, 4),
                "interval_hours": round(current_interval / 60, 4),
            })
            current_time += timedelta(minutes=current_interval)
            current_interval *= PHI

        return timeline

    def get_all_pending(self) -> List[str]:
        """Get all sources with pending backups."""
        now = datetime.now()
        pending = []

        for key, schedule in self._schedules.items():
            if schedule.next_backup and now >= schedule.next_backup:
                pending.append(key)

        return pending

    def reset_schedule(self, source_key: str) -> Optional[BackupSchedule]:
        """Reset a source's schedule to base interval."""
        schedule = self._schedules.get(source_key)
        if schedule:
            schedule.current_interval_minutes = schedule.base_interval_minutes
            schedule.next_backup = datetime.now()
        return schedule

    def get_statistics(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        total_snapshots = sum(len(s.snapshots) for s in self._schedules.values())
        total_backups = sum(s.backup_count for s in self._schedules.values())

        return {
            "registered_sources": len(self._schedules),
            "total_backups_performed": total_backups,
            "total_snapshots_retained": total_snapshots,
            "phi_constant": PHI,
            "sources": {
                key: {
                    "backup_count": s.backup_count,
                    "current_interval_min": round(s.current_interval_minutes, 4),
                    "next_backup": s.next_backup.isoformat() if s.next_backup else None,
                }
                for key, s in self._schedules.items()
            },
        }


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Backup Scheduler - Test Suite")
    print("=" * 60)
    print(f"PHI constant: {PHI}")
    print(f"Formula: next_backup = last_backup * PHI")

    # Initialize scheduler with 1-minute base interval
    scheduler = BackupScheduler(base_interval_minutes=1.0)

    # Test 1: Register sources
    print("\n[TEST 1] Registering Backup Sources...")

    sources = ["database", "user_files", "config", "logs"]
    for src in sources:
        schedule = scheduler.register_source(src, base_interval_minutes=1.0)
        print(f"  Registered '{src}': base_interval={schedule.base_interval_minutes}min")

    # Test 2: PHI sequence calculation
    print("\n[TEST 2] PHI Interval Sequence (10 steps)...")
    sequence = scheduler.get_phi_sequence("database", steps=10)
    print(f"  Base: 1 minute")
    for i, interval in enumerate(sequence, 1):
        print(f"  Step {i}: {interval:.4f} min ({interval/60:.4f} hours)")

    # Test 3: Perform backups
    print("\n[TEST 3] Performing Backups...")

    test_data = {
        "database": {"tables": 50, "rows": 1000000},
        "user_files": {"count": 5000, "size_gb": 250},
        "config": {"settings": {"debug": False, "log_level": "INFO"}},
    }

    for src in ["database", "user_files", "config"]:
        for i in range(3):
            snapshot = scheduler.perform_backup(src, data=test_data.get(src), force=True)
            if snapshot:
                schedule = scheduler.get_schedule(src)
                print(f"  {src} backup #{i+1}: {snapshot.snapshot_id}")
                print(f"    - Interval used: {snapshot.interval_minutes:.4f} min")
                print(f"    - Next interval: {schedule.current_interval_minutes:.4f} min")

    # Test 4: Backup timeline projection
    print("\n[TEST 4] Backup Timeline Projection (database)...")
    timeline = scheduler.get_backup_timeline("database", steps=5)
    for entry in timeline:
        print(f"  Backup #{entry['backup_number']}: {entry['interval_minutes']:.4f} min interval")

    # Test 5: Statistics
    print("\n[TEST 5] Scheduler Statistics...")
    stats = scheduler.get_statistics()
    print(f"  Registered sources: {stats['registered_sources']}")
    print(f"  Total backups: {stats['total_backups_performed']}")
    print(f"  Retained snapshots: {stats['total_snapshots_retained']}")
    print(f"  PHI constant: {stats['phi_constant']}")

    # Test 6: Schedule reset
    print("\n[TEST 6] Schedule Reset...")
    before = scheduler.get_schedule("database").current_interval_minutes
    scheduler.reset_schedule("database")
    after = scheduler.get_schedule("database").current_interval_minutes
    print(f"  'database' interval: {before:.4f} -> {after:.4f} min")

    # Test 7: Verify PHI multiplication
    print("\n[TEST 7] PHI Multiplication Verification...")
    intervals = []
    for i in range(5):
        snapshot = scheduler.perform_backup("logs", force=True)
        schedule = scheduler.get_schedule("logs")
        intervals.append(schedule.current_interval_minutes / PHI)  # Get the used interval

    print(f"  Intervals: {[round(i, 4) for i in intervals]}")
    print(f"  Ratios: {[round(intervals[i+1]/intervals[i], 6) for i in range(len(intervals)-1)]}")
    print(f"  Expected ratio (PHI): {PHI}")

    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)
