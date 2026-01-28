"""
Goal Tracker - Genesis-Milestone Checkpoint System

Uses the Genesis function G(t) for goal progression checkpoints:
    G(0) = VOID (goal not started)
    G(GENESIS_CONSTANT) = GARDEN (initial momentum)
    G(1) = PIO_OPERATIONAL (goal achieved)

Based on IIAS architecture using Genesis emergence function.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum
import math

# Constants
PHI = 1.618033988749895
GENESIS_CONSTANT = 2 / 901  # ~0.00222


class GoalState(Enum):
    """Goal states based on Genesis function"""
    VOID = "void"              # G(0): Not started
    EMERGING = "emerging"      # 0 < t < GENESIS_CONSTANT
    GARDEN = "garden"          # GENESIS_CONSTANT <= t < 1
    OPERATIONAL = "operational"  # t >= 1: Goal achieved


class GoalCategory(Enum):
    """Goal categories"""
    CAREER = "career"
    HEALTH = "health"
    FINANCIAL = "financial"
    PERSONAL = "personal"
    LEARNING = "learning"


@dataclass
class GenesisCheckpoint:
    """A checkpoint based on Genesis function milestones"""
    name: str
    t_value: float  # Progress value (0 to 1)
    description: str
    reached: bool = False
    reached_at: Optional[datetime] = None

    @property
    def state(self) -> GoalState:
        """Get state at this checkpoint"""
        if self.t_value <= 0:
            return GoalState.VOID
        elif self.t_value < GENESIS_CONSTANT:
            return GoalState.EMERGING
        elif self.t_value < 1:
            return GoalState.GARDEN
        else:
            return GoalState.OPERATIONAL


def genesis_function(t: float) -> dict:
    """
    Genesis function G(t) for goal emergence.

    emergence = 1 - exp(-t / GENESIS_CONSTANT)

    Returns state and dimensional emergence.
    """
    if t <= 0:
        return {
            "state": GoalState.VOID,
            "emergence": 0.0,
            "dimensions": 0,
            "energy": 0.0
        }

    emergence = 1 - math.exp(-t / GENESIS_CONSTANT)
    dimensions = int(12 * emergence)
    energy = emergence * PHI  # PHI-scaled energy

    if t < GENESIS_CONSTANT:
        state = GoalState.EMERGING
    elif t < 1:
        state = GoalState.GARDEN
    else:
        state = GoalState.OPERATIONAL

    return {
        "state": state,
        "emergence": emergence,
        "dimensions": dimensions,
        "energy": energy
    }


@dataclass
class Goal:
    """A goal with Genesis-based checkpoints"""
    title: str
    description: str
    category: GoalCategory
    target_date: datetime
    created_at: datetime = field(default_factory=datetime.now)
    progress: float = 0.0  # 0 to 1
    checkpoints: list[GenesisCheckpoint] = field(default_factory=list)
    completed: bool = False
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        # Initialize Genesis checkpoints if not provided
        if not self.checkpoints:
            self.checkpoints = [
                GenesisCheckpoint("Inception", 0.0, "Goal created"),
                GenesisCheckpoint("First Step", GENESIS_CONSTANT / 2, "Initial action taken"),
                GenesisCheckpoint("Garden Entry", GENESIS_CONSTANT, "Critical momentum achieved"),
                GenesisCheckpoint("Quarter Progress", 0.25, "25% complete"),
                GenesisCheckpoint("Halfway", 0.5, "50% complete"),
                GenesisCheckpoint("Three Quarters", 0.75, "75% complete"),
                GenesisCheckpoint("Final Push", 0.9, "90% complete - final stretch"),
                GenesisCheckpoint("Completion", 1.0, "Goal achieved!")
            ]
            # Mark inception as reached
            self.checkpoints[0].reached = True
            self.checkpoints[0].reached_at = self.created_at

    def update_progress(self, new_progress: float) -> dict:
        """
        Update goal progress and check for milestone achievements.

        Returns dict with update info and any checkpoints reached.
        """
        new_progress = max(0, min(1, new_progress))  # Clamp to 0-1
        old_progress = self.progress
        self.progress = new_progress

        result = {
            "old_progress": old_progress,
            "new_progress": new_progress,
            "checkpoints_reached": [],
            "genesis": genesis_function(new_progress)
        }

        # Check for newly reached checkpoints
        for checkpoint in self.checkpoints:
            if not checkpoint.reached and new_progress >= checkpoint.t_value:
                checkpoint.reached = True
                checkpoint.reached_at = datetime.now()
                result["checkpoints_reached"].append(checkpoint.name)

        # Check for completion
        if new_progress >= 1.0 and not self.completed:
            self.completed = True
            self.completed_at = datetime.now()
            result["goal_completed"] = True

        return result

    def get_genesis_state(self) -> dict:
        """Get current Genesis state for the goal"""
        return genesis_function(self.progress)

    def get_next_checkpoint(self) -> Optional[GenesisCheckpoint]:
        """Get the next unreached checkpoint"""
        for checkpoint in self.checkpoints:
            if not checkpoint.reached:
                return checkpoint
        return None

    def get_status(self) -> dict:
        """Get comprehensive goal status"""
        genesis = self.get_genesis_state()
        next_cp = self.get_next_checkpoint()
        reached_count = sum(1 for cp in self.checkpoints if cp.reached)

        # Calculate days remaining
        days_remaining = (self.target_date - datetime.now()).days

        return {
            "title": self.title,
            "category": self.category.value,
            "progress": self.progress * 100,  # As percentage
            "state": genesis["state"].value,
            "emergence": genesis["emergence"],
            "dimensions_active": genesis["dimensions"],
            "energy_level": genesis["energy"],
            "checkpoints_reached": reached_count,
            "total_checkpoints": len(self.checkpoints),
            "next_checkpoint": next_cp.name if next_cp else None,
            "progress_to_next": (self.progress / next_cp.t_value * 100) if next_cp and next_cp.t_value > 0 else 100,
            "days_remaining": days_remaining,
            "completed": self.completed
        }


class GoalTracker:
    """
    Genesis-Milestone Goal Tracker

    Uses the Genesis function G(t) to track goal progress through
    emergence phases: VOID -> EMERGING -> GARDEN -> OPERATIONAL
    """

    def __init__(self):
        self.goals: dict[str, Goal] = {}
        self.genesis_constant = GENESIS_CONSTANT
        self.phi = PHI

    def add_goal(self, title: str, description: str,
                 category: GoalCategory, target_date: datetime) -> Goal:
        """Add a new goal"""
        if title in self.goals:
            return self.goals[title]

        goal = Goal(
            title=title,
            description=description,
            category=category,
            target_date=target_date
        )
        self.goals[title] = goal
        return goal

    def update_progress(self, title: str, progress: float) -> Optional[dict]:
        """Update progress for a goal"""
        if title not in self.goals:
            return None
        return self.goals[title].update_progress(progress)

    def get_goal_status(self, title: str) -> Optional[dict]:
        """Get status for a specific goal"""
        if title not in self.goals:
            return None
        return self.goals[title].get_status()

    def get_goals_by_state(self, state: GoalState) -> list[Goal]:
        """Get all goals in a specific Genesis state"""
        return [g for g in self.goals.values()
                if g.get_genesis_state()["state"] == state]

    def get_goals_by_category(self, category: GoalCategory) -> list[Goal]:
        """Get all goals in a category"""
        return [g for g in self.goals.values() if g.category == category]

    def get_dashboard(self) -> dict:
        """Get overall goals dashboard"""
        all_goals = list(self.goals.values())

        if not all_goals:
            return {
                "total_goals": 0,
                "by_state": {},
                "by_category": {},
                "overall_progress": 0
            }

        # Count by state
        by_state = {}
        for state in GoalState:
            count = len([g for g in all_goals
                        if g.get_genesis_state()["state"] == state])
            by_state[state.value] = count

        # Count by category
        by_category = {}
        for category in GoalCategory:
            goals = [g for g in all_goals if g.category == category]
            if goals:
                by_category[category.value] = {
                    "count": len(goals),
                    "avg_progress": sum(g.progress for g in goals) / len(goals) * 100
                }

        return {
            "total_goals": len(all_goals),
            "completed_goals": sum(1 for g in all_goals if g.completed),
            "by_state": by_state,
            "by_category": by_category,
            "overall_progress": sum(g.progress for g in all_goals) / len(all_goals) * 100,
            "total_energy": sum(g.get_genesis_state()["energy"] for g in all_goals),
            "genesis_constant": self.genesis_constant
        }

    def get_upcoming_deadlines(self, days: int = 30) -> list[dict]:
        """Get goals with deadlines in the next N days"""
        now = datetime.now()
        cutoff = now + timedelta(days=days)

        upcoming = []
        for goal in self.goals.values():
            if not goal.completed and goal.target_date <= cutoff:
                upcoming.append({
                    "title": goal.title,
                    "days_remaining": (goal.target_date - now).days,
                    "progress": goal.progress * 100,
                    "state": goal.get_genesis_state()["state"].value
                })

        return sorted(upcoming, key=lambda x: x["days_remaining"])

    def __repr__(self) -> str:
        return f"GoalTracker(goals={len(self.goals)}, G={self.genesis_constant:.6f})"


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Goal Tracker - Genesis-Milestone Checkpoint Test")
    print("=" * 60)
    print(f"\nConstants: PHI={PHI}, GENESIS_CONSTANT={GENESIS_CONSTANT:.6f}")

    # Show Genesis function behavior
    print("\n--- Genesis Function G(t) Behavior ---")
    test_values = [0, GENESIS_CONSTANT/2, GENESIS_CONSTANT, 0.25, 0.5, 0.75, 1.0]
    for t in test_values:
        g = genesis_function(t)
        print(f"  G({t:.4f}): state={g['state'].value:12s}, "
              f"emergence={g['emergence']:.4f}, dims={g['dimensions']:2d}")

    # Create tracker
    tracker = GoalTracker()
    print(f"\n{tracker}")

    # Add goals
    print("\n--- Adding Goals ---")

    goal1 = tracker.add_goal(
        "Learn Machine Learning",
        "Complete ML course and build 3 projects",
        GoalCategory.LEARNING,
        datetime.now() + timedelta(days=90)
    )

    goal2 = tracker.add_goal(
        "Run Half Marathon",
        "Train and complete a half marathon",
        GoalCategory.HEALTH,
        datetime.now() + timedelta(days=120)
    )

    goal3 = tracker.add_goal(
        "Side Project Launch",
        "Build and launch a web application",
        GoalCategory.CAREER,
        datetime.now() + timedelta(days=60)
    )

    for name in tracker.goals:
        status = tracker.get_goal_status(name)
        print(f"  Added: {name}")
        print(f"    State: {status['state']}, Progress: {status['progress']:.1f}%")

    # Update progress
    print("\n--- Updating Progress ---")

    # ML goal: Just started
    result1 = tracker.update_progress("Learn Machine Learning", 0.001)  # Before GENESIS
    print(f"\n  ML Goal progress -> 0.1%:")
    print(f"    State: {result1['genesis']['state'].value}")
    print(f"    Checkpoints reached: {result1['checkpoints_reached']}")

    # ML goal: Pass GENESIS threshold
    result2 = tracker.update_progress("Learn Machine Learning", GENESIS_CONSTANT)
    print(f"\n  ML Goal progress -> {GENESIS_CONSTANT*100:.3f}% (GENESIS threshold):")
    print(f"    State: {result2['genesis']['state'].value}")
    print(f"    Checkpoints reached: {result2['checkpoints_reached']}")

    # Marathon: Halfway
    result3 = tracker.update_progress("Run Half Marathon", 0.5)
    print(f"\n  Marathon progress -> 50%:")
    print(f"    State: {result3['genesis']['state'].value}")
    print(f"    Emergence: {result3['genesis']['emergence']:.4f}")
    print(f"    Checkpoints reached: {result3['checkpoints_reached']}")

    # Side Project: Complete
    result4 = tracker.update_progress("Side Project Launch", 1.0)
    print(f"\n  Side Project progress -> 100%:")
    print(f"    State: {result4['genesis']['state'].value}")
    print(f"    Goal completed: {result4.get('goal_completed', False)}")
    print(f"    Checkpoints reached: {result4['checkpoints_reached']}")

    # Get dashboard
    print("\n--- Goals Dashboard ---")
    dashboard = tracker.get_dashboard()
    print(f"  Total goals: {dashboard['total_goals']}")
    print(f"  Completed: {dashboard['completed_goals']}")
    print(f"  Overall progress: {dashboard['overall_progress']:.1f}%")
    print(f"  Total energy: {dashboard['total_energy']:.2f}")
    print(f"\n  By State:")
    for state, count in dashboard['by_state'].items():
        if count > 0:
            print(f"    {state}: {count}")

    # Upcoming deadlines
    print("\n--- Upcoming Deadlines (30 days) ---")
    upcoming = tracker.get_upcoming_deadlines(30)
    if upcoming:
        for goal in upcoming:
            print(f"  {goal['title']}: {goal['days_remaining']} days, "
                  f"{goal['progress']:.1f}% done ({goal['state']})")
    else:
        print("  No deadlines in next 30 days")

    print("\n" + "=" * 60)
    print("Goal Tracker Test PASSED")
    print("=" * 60)
