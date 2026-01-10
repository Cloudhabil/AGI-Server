"""
Autonomous GPIA - Self-Sustaining Agent
========================================

Runs without human intervention in a container environment.
Designed for Kubernetes with persistent volumes.

Requirements for autonomy:
1. Goal persistence - Survives restarts
2. Task generation - Creates own work
3. Self-monitoring - Detects failures
4. Self-healing - Recovers from errors
5. External triggers - Reacts to events
6. Resource awareness - Manages limits
7. Escalation - Knows when to alert humans

Usage:
    # In container
    python gpia_autonomous.py --mode daemon

    # With goals
    python gpia_autonomous.py --goal "Monitor system health every hour"
"""

import json
import logging
import os
import signal
import sys
import time
import threading
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from enum import Enum

# Ensure UTF-8
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Persistent storage path (mount as volume in K8s)
DATA_DIR = Path(os.getenv("GPIA_DATA_DIR", "data/gpia"))
GOALS_FILE = DATA_DIR / "goals.json"
STATE_FILE = DATA_DIR / "state.json"
TASKS_FILE = DATA_DIR / "task_queue.json"
HEALTH_FILE = DATA_DIR / "health.json"
LOG_FILE = DATA_DIR / "autonomous.log"


class GoalPriority(Enum):
    CRITICAL = 1  # Must always run
    HIGH = 2      # Important
    NORMAL = 3    # Regular
    LOW = 4       # Nice to have


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Goal:
    """A persistent goal that survives restarts."""
    id: str
    description: str
    priority: int = GoalPriority.NORMAL.value
    schedule: Optional[str] = None  # cron-like or interval
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    enabled: bool = True
    success_count: int = 0
    failure_count: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Goal':
        return cls(**data)


@dataclass
class Task:
    """A task in the queue."""
    id: str
    goal_id: Optional[str]
    description: str
    status: str = TaskStatus.PENDING.value
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(**data)


@dataclass
class HealthStatus:
    """Agent health metrics."""
    alive: bool = True
    last_heartbeat: str = field(default_factory=lambda: datetime.now().isoformat())
    uptime_seconds: float = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    memory_ok: bool = True
    models_ok: bool = True
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)


class GoalManager:
    """Manages persistent goals."""

    def __init__(self, goals_file: Path = GOALS_FILE):
        self.goals_file = goals_file
        self.goals: Dict[str, Goal] = {}
        self._load()

    def _load(self):
        """Load goals from persistent storage."""
        if self.goals_file.exists():
            try:
                data = json.loads(self.goals_file.read_text())
                self.goals = {
                    g['id']: Goal.from_dict(g)
                    for g in data.get('goals', [])
                }
                logger.info(f"Loaded {len(self.goals)} goals from storage")
            except Exception as e:
                logger.error(f"Failed to load goals: {e}")
                self.goals = {}

    def _save(self):
        """Persist goals to storage."""
        self.goals_file.parent.mkdir(parents=True, exist_ok=True)
        data = {'goals': [g.to_dict() for g in self.goals.values()]}
        self.goals_file.write_text(json.dumps(data, indent=2))

    def add_goal(self, description: str, priority: GoalPriority = GoalPriority.NORMAL,
                 schedule: Optional[str] = None) -> Goal:
        """Add a new goal."""
        goal_id = hashlib.md5(description.encode()).hexdigest()[:8]
        goal = Goal(
            id=goal_id,
            description=description,
            priority=priority.value,
            schedule=schedule
        )
        self.goals[goal_id] = goal
        self._save()
        logger.info(f"Added goal: {goal_id} - {description[:50]}")
        return goal

    def get_due_goals(self) -> List[Goal]:
        """Get goals that are due to run."""
        due = []
        now = datetime.now()

        for goal in self.goals.values():
            if not goal.enabled:
                continue

            if goal.schedule is None:
                # One-time goal, check if never run
                if goal.last_run is None:
                    due.append(goal)
            elif goal.schedule.endswith('m'):
                # Interval in minutes
                minutes = int(goal.schedule[:-1])
                if goal.last_run is None:
                    due.append(goal)
                else:
                    last = datetime.fromisoformat(goal.last_run)
                    if now - last > timedelta(minutes=minutes):
                        due.append(goal)
            elif goal.schedule.endswith('h'):
                # Interval in hours
                hours = int(goal.schedule[:-1])
                if goal.last_run is None:
                    due.append(goal)
                else:
                    last = datetime.fromisoformat(goal.last_run)
                    if now - last > timedelta(hours=hours):
                        due.append(goal)

        # Sort by priority
        due.sort(key=lambda g: g.priority)
        return due

    def mark_completed(self, goal_id: str, success: bool):
        """Mark a goal as completed."""
        if goal_id in self.goals:
            goal = self.goals[goal_id]
            goal.last_run = datetime.now().isoformat()
            if success:
                goal.success_count += 1
            else:
                goal.failure_count += 1
            self._save()


class TaskQueue:
    """Persistent task queue."""

    def __init__(self, tasks_file: Path = TASKS_FILE):
        self.tasks_file = tasks_file
        self.tasks: List[Task] = []
        self._load()

    def _load(self):
        """Load tasks from storage."""
        if self.tasks_file.exists():
            try:
                data = json.loads(self.tasks_file.read_text())
                self.tasks = [Task.from_dict(t) for t in data.get('tasks', [])]
                logger.info(f"Loaded {len(self.tasks)} tasks from queue")
            except Exception as e:
                logger.error(f"Failed to load tasks: {e}")

    def _save(self):
        """Persist tasks."""
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
        data = {'tasks': [t.to_dict() for t in self.tasks]}
        self.tasks_file.write_text(json.dumps(data, indent=2))

    def enqueue(self, description: str, goal_id: Optional[str] = None) -> Task:
        """Add task to queue."""
        task_id = hashlib.md5(f"{description}{time.time()}".encode()).hexdigest()[:8]
        task = Task(id=task_id, goal_id=goal_id, description=description)
        self.tasks.append(task)
        self._save()
        return task

    def get_next(self) -> Optional[Task]:
        """Get next pending task."""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING.value:
                return task
        return None

    def update_task(self, task_id: str, status: TaskStatus,
                    result: str = None, error: str = None):
        """Update task status."""
        for task in self.tasks:
            if task.id == task_id:
                task.status = status.value
                if status == TaskStatus.RUNNING:
                    task.started_at = datetime.now().isoformat()
                elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    task.completed_at = datetime.now().isoformat()
                    task.result = result
                    task.error = error
                self._save()
                break

    def cleanup_old(self, max_age_hours: int = 24):
        """Remove old completed tasks."""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        self.tasks = [
            t for t in self.tasks
            if t.status == TaskStatus.PENDING.value or
               (t.completed_at and datetime.fromisoformat(t.completed_at) > cutoff)
        ]
        self._save()


class HealthMonitor:
    """Self-monitoring system."""

    def __init__(self, health_file: Path = HEALTH_FILE):
        self.health_file = health_file
        self.start_time = datetime.now()
        self.status = HealthStatus()

    def check_models(self) -> bool:
        """Check if LLM models are available."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def check_memory(self) -> bool:
        """Check memory system."""
        try:
            from skills.conscience.memory.skill import MemorySkill
            mem = MemorySkill()
            return True
        except:
            return False

    def update(self, tasks_completed: int = 0, tasks_failed: int = 0,
               error: str = None):
        """Update health status."""
        self.status.last_heartbeat = datetime.now().isoformat()
        self.status.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        self.status.tasks_completed += tasks_completed
        self.status.tasks_failed += tasks_failed
        self.status.models_ok = self.check_models()
        self.status.memory_ok = self.check_memory()

        if error:
            self.status.errors.append(f"{datetime.now().isoformat()}: {error}")
            # Keep last 10 errors
            self.status.errors = self.status.errors[-10:]

        self._save()

    def _save(self):
        """Persist health status."""
        self.health_file.parent.mkdir(parents=True, exist_ok=True)
        self.health_file.write_text(json.dumps(self.status.to_dict(), indent=2))

    def is_healthy(self) -> bool:
        """Overall health check."""
        return self.status.alive and self.status.models_ok


class AutonomousGPIA:
    """
    Self-sustaining GPIA that runs without human intervention.

    Capabilities:
    - Persists goals and state across restarts
    - Generates tasks from goals
    - Self-monitors and heals
    - Reacts to external triggers
    - Escalates when needed
    """

    def __init__(self):
        # Ensure data directory exists
        DATA_DIR.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.goals = GoalManager()
        self.queue = TaskQueue()
        self.health = HealthMonitor()

        # Import GPIA core
        from gpia import GPIA
        self.agent = GPIA(verbose=False)

        # Control flags
        self.running = False
        self.shutdown_event = threading.Event()

        # Register signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

        logger.info("Autonomous GPIA initialized")

    def _handle_shutdown(self, signum, frame):
        """Graceful shutdown handler."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.shutdown_event.set()

    def add_goal(self, description: str, schedule: str = None,
                 priority: GoalPriority = GoalPriority.NORMAL) -> Goal:
        """Add a persistent goal."""
        return self.goals.add_goal(description, priority, schedule)

    def _generate_tasks_from_goals(self):
        """Generate tasks from due goals."""
        due_goals = self.goals.get_due_goals()

        for goal in due_goals:
            # Check if task already queued
            existing = [t for t in self.queue.tasks
                       if t.goal_id == goal.id and t.status == TaskStatus.PENDING.value]

            if not existing:
                self.queue.enqueue(goal.description, goal.id)
                logger.info(f"Generated task from goal: {goal.id}")

    def _execute_task(self, task: Task) -> bool:
        """Execute a single task."""
        logger.info(f"Executing task: {task.id} - {task.description[:50]}...")

        self.queue.update_task(task.id, TaskStatus.RUNNING)

        try:
            result = self.agent.run(task.description)

            if result.success and result.response:
                self.queue.update_task(
                    task.id,
                    TaskStatus.COMPLETED,
                    result=result.response[:1000]
                )

                # Mark goal completed if associated
                if task.goal_id:
                    self.goals.mark_completed(task.goal_id, True)

                self.health.update(tasks_completed=1)
                logger.info(f"Task completed: {task.id}")
                return True
            else:
                raise Exception("Empty or failed response")

        except Exception as e:
            error_msg = str(e)[:200]

            # Retry logic
            if task.retries < task.max_retries:
                task.retries += 1
                task.status = TaskStatus.PENDING.value
                self.queue._save()
                logger.warning(f"Task {task.id} failed, retry {task.retries}/{task.max_retries}")
            else:
                self.queue.update_task(task.id, TaskStatus.FAILED, error=error_msg)
                if task.goal_id:
                    self.goals.mark_completed(task.goal_id, False)
                self.health.update(tasks_failed=1, error=error_msg)
                logger.error(f"Task failed permanently: {task.id} - {error_msg}")

            return False

    def _self_heal(self):
        """Attempt to recover from failures."""
        if not self.health.status.models_ok:
            logger.warning("Models unavailable, waiting...")
            time.sleep(30)  # Wait for models to come back

        # Cleanup old tasks
        self.queue.cleanup_old()

    def run_once(self):
        """Run a single iteration of the autonomous loop."""
        # Update health
        self.health.update()

        # Self-heal if needed
        if not self.health.is_healthy():
            self._self_heal()
            return

        # Generate tasks from goals
        self._generate_tasks_from_goals()

        # Execute next task
        task = self.queue.get_next()
        if task:
            self._execute_task(task)
        else:
            logger.debug("No pending tasks")

    def run_daemon(self, interval_seconds: int = 60):
        """
        Run as a daemon process.

        This is the main loop for containerized deployment.
        """
        logger.info(f"Starting autonomous daemon (interval: {interval_seconds}s)")
        self.running = True

        while self.running:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"Loop error: {e}")
                self.health.update(error=str(e))

            # Wait for interval or shutdown
            self.shutdown_event.wait(timeout=interval_seconds)

            if self.shutdown_event.is_set():
                break

        logger.info("Daemon stopped")
        self.health.status.alive = False
        self.health._save()

    def status(self) -> Dict:
        """Get full status."""
        return {
            "health": self.health.status.to_dict(),
            "goals": len(self.goals.goals),
            "pending_tasks": len([t for t in self.queue.tasks
                                 if t.status == TaskStatus.PENDING.value]),
            "completed_tasks": self.health.status.tasks_completed,
            "failed_tasks": self.health.status.tasks_failed,
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Autonomous GPIA")
    parser.add_argument("--mode", choices=["daemon", "once", "status", "add-goal"],
                       default="once", help="Run mode")
    parser.add_argument("--interval", type=int, default=60,
                       help="Daemon loop interval in seconds")
    parser.add_argument("--goal", type=str, help="Goal description (for add-goal)")
    parser.add_argument("--schedule", type=str, help="Schedule (e.g., '1h', '30m')")
    args = parser.parse_args()

    agent = AutonomousGPIA()

    if args.mode == "status":
        status = agent.status()
        print(json.dumps(status, indent=2))

    elif args.mode == "add-goal":
        if not args.goal:
            print("Error: --goal required")
            sys.exit(1)
        goal = agent.add_goal(args.goal, schedule=args.schedule)
        print(f"Added goal: {goal.id}")

    elif args.mode == "once":
        agent.run_once()

    elif args.mode == "daemon":
        agent.run_daemon(interval_seconds=args.interval)


if __name__ == "__main__":
    main()
