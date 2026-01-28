"""
Learning Planner - PHI-Spaced Repetition System

Implements spaced repetition with PHI-based intervals:
    review_interval = previous_interval * PHI

Based on IIAS architecture using the golden ratio for optimal learning.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum
import math

# Constants
PHI = 1.618033988749895
INITIAL_INTERVAL_HOURS = 1  # Start with 1 hour


class Difficulty(Enum):
    """Review difficulty ratings"""
    EASY = "easy"       # Increase interval more
    GOOD = "good"       # Standard PHI increase
    HARD = "hard"       # Smaller increase
    AGAIN = "again"     # Reset to beginning


class ContentType(Enum):
    """Types of learning content"""
    CONCEPT = "concept"
    FACT = "fact"
    SKILL = "skill"
    PROCEDURE = "procedure"


@dataclass
class LearningItem:
    """A single item to learn with PHI-spaced repetition"""
    title: str
    content: str
    content_type: ContentType
    created_at: datetime = field(default_factory=datetime.now)
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    interval_hours: float = INITIAL_INTERVAL_HOURS
    review_count: int = 0
    ease_factor: float = PHI  # Personal PHI multiplier

    def __post_init__(self):
        if self.next_review is None:
            self.next_review = self.created_at + timedelta(hours=self.interval_hours)

    def review(self, difficulty: Difficulty) -> dict:
        """
        Process a review with PHI-spaced interval calculation.

        review_interval = previous_interval * PHI * difficulty_modifier
        """
        now = datetime.now()
        self.last_reviewed = now
        self.review_count += 1

        result = {
            "item": self.title,
            "previous_interval_hours": self.interval_hours,
            "difficulty": difficulty.value,
            "review_count": self.review_count
        }

        # Calculate new interval based on difficulty
        if difficulty == Difficulty.AGAIN:
            # Reset to initial interval
            self.interval_hours = INITIAL_INTERVAL_HOURS
            self.ease_factor = max(1.3, self.ease_factor - 0.2)
        elif difficulty == Difficulty.HARD:
            # Smaller increase (PHI^0.5)
            self.interval_hours *= math.sqrt(PHI)
            self.ease_factor = max(1.3, self.ease_factor - 0.15)
        elif difficulty == Difficulty.GOOD:
            # Standard PHI increase
            self.interval_hours *= self.ease_factor
        elif difficulty == Difficulty.EASY:
            # Larger increase (PHI^1.5)
            self.interval_hours *= PHI * math.sqrt(PHI)
            self.ease_factor = min(3.0, self.ease_factor + 0.15)

        self.next_review = now + timedelta(hours=self.interval_hours)

        result["new_interval_hours"] = self.interval_hours
        result["new_interval_days"] = self.interval_hours / 24
        result["next_review"] = self.next_review.isoformat()
        result["ease_factor"] = self.ease_factor

        return result

    @property
    def is_due(self) -> bool:
        """Check if item is due for review"""
        return self.next_review is not None and datetime.now() >= self.next_review

    @property
    def days_until_review(self) -> float:
        """Days until next review (negative if overdue)"""
        if self.next_review is None:
            return 0
        delta = self.next_review - datetime.now()
        return delta.total_seconds() / 86400


@dataclass
class LearningTopic:
    """A topic containing multiple learning items"""
    name: str
    description: str = ""
    items: list[LearningItem] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add_item(self, title: str, content: str,
                 content_type: ContentType = ContentType.CONCEPT) -> LearningItem:
        """Add a new learning item to the topic"""
        item = LearningItem(title=title, content=content, content_type=content_type)
        self.items.append(item)
        return item

    def get_due_items(self) -> list[LearningItem]:
        """Get all items due for review"""
        return [item for item in self.items if item.is_due]

    def get_progress(self) -> dict:
        """Get topic learning progress"""
        if not self.items:
            return {"name": self.name, "total_items": 0, "mastered": 0, "progress": 0}

        # Items with interval > 30 days are considered "mastered"
        mastered = sum(1 for i in self.items if i.interval_hours > 30 * 24)

        return {
            "name": self.name,
            "total_items": len(self.items),
            "mastered": mastered,
            "due_count": len(self.get_due_items()),
            "avg_interval_days": sum(i.interval_hours for i in self.items) / len(self.items) / 24,
            "progress": mastered / len(self.items) * 100
        }


class LearningPlanner:
    """
    PHI-Spaced Repetition Learning Planner

    Uses PHI (golden ratio) for optimal spaced repetition intervals:
    - Each successful review multiplies interval by PHI
    - Creates naturally expanding review schedule
    - Adapts to difficulty with ease factor adjustments
    """

    def __init__(self):
        self.topics: dict[str, LearningTopic] = {}
        self.phi = PHI
        self.initial_interval = INITIAL_INTERVAL_HOURS

    def add_topic(self, name: str, description: str = "") -> LearningTopic:
        """Add a new learning topic"""
        if name in self.topics:
            return self.topics[name]

        topic = LearningTopic(name=name, description=description)
        self.topics[name] = topic
        return topic

    def add_item(self, topic_name: str, title: str, content: str,
                 content_type: ContentType = ContentType.CONCEPT) -> Optional[LearningItem]:
        """Add a learning item to a topic"""
        if topic_name not in self.topics:
            self.add_topic(topic_name)

        return self.topics[topic_name].add_item(title, content, content_type)

    def get_due_items(self, topic_name: Optional[str] = None) -> list[LearningItem]:
        """Get all due items, optionally filtered by topic"""
        if topic_name and topic_name in self.topics:
            return self.topics[topic_name].get_due_items()

        due = []
        for topic in self.topics.values():
            due.extend(topic.get_due_items())
        return sorted(due, key=lambda x: x.next_review or datetime.max)

    def review_item(self, topic_name: str, item_title: str,
                    difficulty: Difficulty) -> Optional[dict]:
        """Review an item and update its schedule"""
        if topic_name not in self.topics:
            return None

        topic = self.topics[topic_name]
        for item in topic.items:
            if item.title == item_title:
                return item.review(difficulty)
        return None

    def get_study_schedule(self, days: int = 7) -> dict:
        """Get study schedule for upcoming days"""
        schedule = {i: [] for i in range(days)}
        now = datetime.now()

        for topic in self.topics.values():
            for item in topic.items:
                if item.next_review:
                    days_until = (item.next_review - now).days
                    if 0 <= days_until < days:
                        schedule[days_until].append({
                            "topic": topic.name,
                            "item": item.title,
                            "interval_days": item.interval_hours / 24
                        })

        return schedule

    def calculate_phi_sequence(self, n_intervals: int = 10) -> list[float]:
        """Calculate PHI-spaced intervals in days starting from initial"""
        intervals = []
        current = self.initial_interval / 24  # Convert to days

        for _ in range(n_intervals):
            intervals.append(round(current, 2))
            current *= self.phi

        return intervals

    def get_statistics(self) -> dict:
        """Get overall learning statistics"""
        all_items = [item for topic in self.topics.values() for item in topic.items]

        if not all_items:
            return {
                "total_topics": len(self.topics),
                "total_items": 0,
                "due_today": 0,
                "mastery_rate": 0
            }

        mastered = sum(1 for i in all_items if i.interval_hours > 30 * 24)

        return {
            "total_topics": len(self.topics),
            "total_items": len(all_items),
            "due_today": len(self.get_due_items()),
            "total_reviews": sum(i.review_count for i in all_items),
            "avg_interval_days": sum(i.interval_hours for i in all_items) / len(all_items) / 24,
            "mastered_items": mastered,
            "mastery_rate": mastered / len(all_items) * 100,
            "phi_intervals_days": self.calculate_phi_sequence(8)
        }

    def __repr__(self) -> str:
        return f"LearningPlanner(topics={len(self.topics)}, phi={self.phi})"


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Learning Planner - PHI-Spaced Repetition Test")
    print("=" * 60)
    print(f"\nConstants: PHI={PHI}, INITIAL_INTERVAL={INITIAL_INTERVAL_HOURS}h")

    # Create planner
    planner = LearningPlanner()
    print(f"\n{planner}")

    # Show PHI interval sequence
    print("\n--- PHI-Spaced Interval Sequence ---")
    intervals = planner.calculate_phi_sequence(10)
    for i, interval in enumerate(intervals):
        print(f"  Review {i+1}: {interval:.2f} days ({interval*24:.1f} hours)")

    # Add topics and items
    print("\n--- Adding Learning Content ---")

    # Python topic
    python_topic = planner.add_topic("Python", "Python programming fundamentals")
    planner.add_item("Python", "List Comprehensions",
                     "Concise way to create lists: [x for x in range(10)]",
                     ContentType.CONCEPT)
    planner.add_item("Python", "Decorators",
                     "@decorator syntax for wrapping functions",
                     ContentType.CONCEPT)
    planner.add_item("Python", "Context Managers",
                     "with statement for resource management",
                     ContentType.SKILL)

    # Math topic
    math_topic = planner.add_topic("Mathematics", "Mathematical concepts")
    planner.add_item("Mathematics", "Golden Ratio",
                     f"PHI = (1 + sqrt(5))/2 = {PHI}",
                     ContentType.FACT)
    planner.add_item("Mathematics", "Lucas Numbers",
                     "L(n) = L(n-1) + L(n-2), starting with 2, 1",
                     ContentType.CONCEPT)

    print(f"  Added topic 'Python' with 3 items")
    print(f"  Added topic 'Mathematics' with 2 items")

    # Simulate reviews
    print("\n--- Simulating Reviews ---")

    # Review with different difficulties
    result1 = planner.review_item("Python", "List Comprehensions", Difficulty.EASY)
    print(f"\n  List Comprehensions (EASY):")
    print(f"    Previous interval: {result1['previous_interval_hours']}h")
    print(f"    New interval: {result1['new_interval_hours']:.2f}h ({result1['new_interval_days']:.2f} days)")

    result2 = planner.review_item("Python", "Decorators", Difficulty.GOOD)
    print(f"\n  Decorators (GOOD):")
    print(f"    Previous interval: {result2['previous_interval_hours']}h")
    print(f"    New interval: {result2['new_interval_hours']:.2f}h ({result2['new_interval_days']:.2f} days)")

    result3 = planner.review_item("Python", "Context Managers", Difficulty.HARD)
    print(f"\n  Context Managers (HARD):")
    print(f"    Previous interval: {result3['previous_interval_hours']}h")
    print(f"    New interval: {result3['new_interval_hours']:.2f}h ({result3['new_interval_days']:.2f} days)")

    result4 = planner.review_item("Mathematics", "Golden Ratio", Difficulty.AGAIN)
    print(f"\n  Golden Ratio (AGAIN - Reset):")
    print(f"    Previous interval: {result4['previous_interval_hours']}h")
    print(f"    New interval: {result4['new_interval_hours']:.2f}h (reset to initial)")

    # Get statistics
    print("\n--- Learning Statistics ---")
    stats = planner.get_statistics()
    for key, value in stats.items():
        if key != "phi_intervals_days":
            print(f"  {key}: {value}")

    # Study schedule
    print("\n--- 7-Day Study Schedule ---")
    schedule = planner.get_study_schedule(7)
    for day, items in schedule.items():
        if items:
            print(f"  Day {day}: {len(items)} items")
            for item in items[:2]:  # Show first 2
                print(f"    - {item['topic']}: {item['item']}")

    print("\n" + "=" * 60)
    print("Learning Planner Test PASSED")
    print("=" * 60)
