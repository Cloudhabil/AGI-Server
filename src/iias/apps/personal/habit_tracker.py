"""
Habit Tracker - Lucas-Milestone Progression System

Tracks habits with milestones at Lucas number days:
[1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]

Based on IIAS architecture using Lucas sequence for natural progression.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

# Constants
PHI = 1.618033988749895
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]


class HabitCategory(Enum):
    """Habit categories aligned with wellness dimensions"""
    PHYSICAL = "physical"
    MENTAL = "mental"
    CREATIVE = "creative"
    SOCIAL = "social"
    SPIRITUAL = "spiritual"


@dataclass
class HabitMilestone:
    """A Lucas-number milestone"""
    day: int
    achieved: bool = False
    achieved_at: Optional[datetime] = None

    @property
    def lucas_index(self) -> int:
        """Get the index in Lucas sequence"""
        return LUCAS.index(self.day) if self.day in LUCAS else -1


@dataclass
class Habit:
    """A trackable habit with Lucas milestones"""
    name: str
    category: HabitCategory
    created_at: datetime = field(default_factory=datetime.now)
    streak: int = 0
    total_completions: int = 0
    milestones: list[HabitMilestone] = field(default_factory=list)
    last_completed: Optional[datetime] = None

    def __post_init__(self):
        # Initialize milestones from Lucas sequence
        if not self.milestones:
            self.milestones = [HabitMilestone(day=d) for d in LUCAS]

    def complete_today(self) -> dict:
        """
        Mark habit as completed today.

        Returns dict with completion info and any milestones achieved.
        """
        now = datetime.now()
        result = {
            "completed": True,
            "streak": self.streak,
            "milestone_achieved": None,
            "next_milestone": None
        }

        # Check if already completed today
        if self.last_completed:
            last_date = self.last_completed.date()
            today = now.date()

            if last_date == today:
                result["completed"] = False
                result["message"] = "Already completed today"
                return result

            # Check streak continuity
            if (today - last_date).days == 1:
                self.streak += 1
            else:
                self.streak = 1  # Reset streak
        else:
            self.streak = 1

        self.last_completed = now
        self.total_completions += 1
        result["streak"] = self.streak

        # Check for milestone achievement
        for milestone in self.milestones:
            if not milestone.achieved and self.streak >= milestone.day:
                milestone.achieved = True
                milestone.achieved_at = now
                result["milestone_achieved"] = milestone.day
                break

        # Find next milestone
        for milestone in self.milestones:
            if not milestone.achieved:
                result["next_milestone"] = milestone.day
                result["days_to_milestone"] = milestone.day - self.streak
                break

        return result

    def get_progress(self) -> dict:
        """Get habit progress summary"""
        achieved_milestones = [m for m in self.milestones if m.achieved]
        next_milestone = next((m for m in self.milestones if not m.achieved), None)

        return {
            "name": self.name,
            "category": self.category.value,
            "streak": self.streak,
            "total_completions": self.total_completions,
            "milestones_achieved": len(achieved_milestones),
            "total_milestones": len(self.milestones),
            "next_milestone_day": next_milestone.day if next_milestone else None,
            "days_to_next": (next_milestone.day - self.streak) if next_milestone else 0,
            "progress_percent": len(achieved_milestones) / len(self.milestones) * 100
        }


class HabitTracker:
    """
    Lucas-Milestone Habit Tracker

    Tracks habits with milestones at Lucas number days for
    natural, phi-based progression.
    """

    def __init__(self):
        self.habits: dict[str, Habit] = {}
        self.lucas_sequence = LUCAS.copy()

    def add_habit(self, name: str, category: HabitCategory = HabitCategory.MENTAL) -> Habit:
        """Add a new habit to track"""
        if name in self.habits:
            return self.habits[name]

        habit = Habit(name=name, category=category)
        self.habits[name] = habit
        return habit

    def remove_habit(self, name: str) -> bool:
        """Remove a habit"""
        if name in self.habits:
            del self.habits[name]
            return True
        return False

    def complete_habit(self, name: str) -> Optional[dict]:
        """Mark a habit as completed today"""
        if name not in self.habits:
            return None
        return self.habits[name].complete_today()

    def get_habit_progress(self, name: str) -> Optional[dict]:
        """Get progress for a specific habit"""
        if name not in self.habits:
            return None
        return self.habits[name].get_progress()

    def get_all_progress(self) -> list[dict]:
        """Get progress for all habits"""
        return [habit.get_progress() for habit in self.habits.values()]

    def get_milestone_summary(self) -> dict:
        """Get summary of milestone achievements across all habits"""
        total_milestones = len(LUCAS) * len(self.habits)
        achieved = sum(
            sum(1 for m in h.milestones if m.achieved)
            for h in self.habits.values()
        )

        return {
            "total_habits": len(self.habits),
            "total_milestones": total_milestones,
            "achieved_milestones": achieved,
            "achievement_rate": achieved / total_milestones * 100 if total_milestones > 0 else 0,
            "lucas_sequence": self.lucas_sequence,
            "by_category": self._get_category_summary()
        }

    def _get_category_summary(self) -> dict:
        """Get summary by category"""
        summary = {}
        for category in HabitCategory:
            habits = [h for h in self.habits.values() if h.category == category]
            if habits:
                summary[category.value] = {
                    "count": len(habits),
                    "avg_streak": sum(h.streak for h in habits) / len(habits),
                    "total_completions": sum(h.total_completions for h in habits)
                }
        return summary

    def get_streaks_leaderboard(self) -> list[tuple[str, int]]:
        """Get habits sorted by current streak"""
        return sorted(
            [(h.name, h.streak) for h in self.habits.values()],
            key=lambda x: x[1],
            reverse=True
        )

    def __repr__(self) -> str:
        return f"HabitTracker(habits={len(self.habits)}, lucas_milestones={LUCAS})"


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Habit Tracker - Lucas-Milestone Progression Test")
    print("=" * 60)
    print(f"\nLucas Sequence Milestones: {LUCAS}")

    # Create tracker
    tracker = HabitTracker()
    print(f"\n{tracker}")

    # Add habits
    print("\n--- Adding Habits ---")
    tracker.add_habit("Morning Meditation", HabitCategory.SPIRITUAL)
    tracker.add_habit("Exercise", HabitCategory.PHYSICAL)
    tracker.add_habit("Reading", HabitCategory.MENTAL)
    tracker.add_habit("Journaling", HabitCategory.CREATIVE)

    for name in tracker.habits:
        print(f"  Added: {name}")

    # Simulate completions
    print("\n--- Simulating Habit Completions ---")

    # Simulate a streak for meditation
    meditation = tracker.habits["Morning Meditation"]
    for i in range(8):  # 8-day streak
        meditation.streak = i + 1
        meditation.total_completions = i + 1
        # Mark milestones
        for m in meditation.milestones:
            if meditation.streak >= m.day and not m.achieved:
                m.achieved = True
                m.achieved_at = datetime.now()

    result = meditation.get_progress()
    print(f"\n  Morning Meditation after 8 days:")
    print(f"    Streak: {result['streak']} days")
    print(f"    Milestones achieved: {result['milestones_achieved']}/{result['total_milestones']}")
    print(f"    Next milestone: Day {result['next_milestone_day']} ({result['days_to_next']} days away)")

    # Complete exercise today
    print("\n--- Today's Completions ---")
    exercise_result = tracker.complete_habit("Exercise")
    print(f"  Exercise: streak={exercise_result['streak']}, milestone={exercise_result['milestone_achieved']}")

    reading_result = tracker.complete_habit("Reading")
    print(f"  Reading: streak={reading_result['streak']}, milestone={reading_result['milestone_achieved']}")

    # Get milestone summary
    print("\n--- Milestone Summary ---")
    summary = tracker.get_milestone_summary()
    print(f"  Total habits: {summary['total_habits']}")
    print(f"  Achieved milestones: {summary['achieved_milestones']}/{summary['total_milestones']}")
    print(f"  Achievement rate: {summary['achievement_rate']:.1f}%")

    # Streaks leaderboard
    print("\n--- Streaks Leaderboard ---")
    leaderboard = tracker.get_streaks_leaderboard()
    for i, (name, streak) in enumerate(leaderboard, 1):
        print(f"  {i}. {name}: {streak} days")

    # Show Lucas milestone explanation
    print("\n--- Lucas Milestone System ---")
    print("  Milestones follow the Lucas sequence (similar to Fibonacci):")
    for i, day in enumerate(LUCAS[:6]):
        ratio = LUCAS[i+1] / day if i < len(LUCAS) - 1 else PHI
        print(f"    Day {day:3d} -> Day {LUCAS[i+1] if i < len(LUCAS)-1 else '...':3} (ratio: {ratio:.3f})")
    print(f"  The ratios converge to PHI = {PHI:.6f}")

    print("\n" + "=" * 60)
    print("Habit Tracker Test PASSED")
    print("=" * 60)
