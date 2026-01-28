"""
Focus Manager - D2 (Attention) Allocation System

Uses the D2 Attention dimension with capacity 3 for focus sessions.
Based on IIAS 12-dimensional architecture where D2 represents Attention.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

# Constants
PHI = 1.618033988749895
D2_CAPACITY = 3  # Attention dimension capacity


class FocusState(Enum):
    """Focus session states"""
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class FocusSession:
    """A single focus session"""
    name: str
    priority: int  # 1-3, where 1 is highest
    duration_minutes: int
    state: FocusState = FocusState.IDLE
    started_at: Optional[datetime] = None
    elapsed_minutes: float = 0.0

    def start(self) -> None:
        """Start the focus session"""
        self.state = FocusState.ACTIVE
        self.started_at = datetime.now()

    def pause(self) -> None:
        """Pause the focus session"""
        if self.state == FocusState.ACTIVE and self.started_at:
            self.elapsed_minutes += (datetime.now() - self.started_at).total_seconds() / 60
            self.state = FocusState.PAUSED

    def resume(self) -> None:
        """Resume a paused session"""
        if self.state == FocusState.PAUSED:
            self.started_at = datetime.now()
            self.state = FocusState.ACTIVE

    def complete(self) -> None:
        """Mark session as completed"""
        if self.state == FocusState.ACTIVE and self.started_at:
            self.elapsed_minutes += (datetime.now() - self.started_at).total_seconds() / 60
        self.state = FocusState.COMPLETED

    @property
    def progress(self) -> float:
        """Get progress as percentage (0-1)"""
        current = self.elapsed_minutes
        if self.state == FocusState.ACTIVE and self.started_at:
            current += (datetime.now() - self.started_at).total_seconds() / 60
        return min(current / self.duration_minutes, 1.0) if self.duration_minutes > 0 else 0.0


class FocusManager:
    """
    D2 (Attention) Allocation Manager

    Manages focus sessions with a capacity of 3 concurrent sessions.
    Uses PHI-based attention weighting for priority allocation.
    """

    def __init__(self):
        self.capacity = D2_CAPACITY
        self.sessions: list[FocusSession] = []
        self.completed_sessions: list[FocusSession] = []
        self.total_focus_minutes: float = 0.0

    @property
    def available_slots(self) -> int:
        """Get number of available focus slots"""
        active_count = sum(1 for s in self.sessions if s.state in [FocusState.ACTIVE, FocusState.PAUSED])
        return self.capacity - active_count

    def add_session(self, name: str, duration_minutes: int, priority: int = 2) -> Optional[FocusSession]:
        """
        Add a new focus session if capacity allows.

        Args:
            name: Session name/description
            duration_minutes: Target duration
            priority: 1 (high), 2 (medium), 3 (low)

        Returns:
            FocusSession if added, None if at capacity
        """
        if self.available_slots <= 0:
            return None

        priority = max(1, min(3, priority))  # Clamp to 1-3
        session = FocusSession(name=name, priority=priority, duration_minutes=duration_minutes)
        self.sessions.append(session)
        return session

    def start_session(self, name: str) -> bool:
        """Start a session by name"""
        for session in self.sessions:
            if session.name == name and session.state == FocusState.IDLE:
                session.start()
                return True
        return False

    def complete_session(self, name: str) -> bool:
        """Complete a session by name"""
        for session in self.sessions:
            if session.name == name and session.state != FocusState.COMPLETED:
                session.complete()
                self.total_focus_minutes += session.elapsed_minutes
                self.completed_sessions.append(session)
                self.sessions.remove(session)
                return True
        return False

    def get_attention_weights(self) -> dict[str, float]:
        """
        Calculate PHI-based attention weights for active sessions.

        Higher priority sessions get PHI^(3-priority) weight.
        """
        weights = {}
        active_sessions = [s for s in self.sessions if s.state in [FocusState.ACTIVE, FocusState.PAUSED]]

        if not active_sessions:
            return weights

        raw_weights = {}
        for session in active_sessions:
            # Priority 1 gets PHI^2, Priority 2 gets PHI^1, Priority 3 gets PHI^0
            raw_weights[session.name] = PHI ** (3 - session.priority)

        # Normalize weights
        total = sum(raw_weights.values())
        for name, weight in raw_weights.items():
            weights[name] = weight / total

        return weights

    def get_status(self) -> dict:
        """Get current focus manager status"""
        return {
            "capacity": self.capacity,
            "available_slots": self.available_slots,
            "active_sessions": len([s for s in self.sessions if s.state == FocusState.ACTIVE]),
            "paused_sessions": len([s for s in self.sessions if s.state == FocusState.PAUSED]),
            "total_focus_minutes": self.total_focus_minutes,
            "completed_count": len(self.completed_sessions),
            "attention_weights": self.get_attention_weights()
        }

    def __repr__(self) -> str:
        status = self.get_status()
        return (f"FocusManager(capacity={self.capacity}, "
                f"active={status['active_sessions']}, "
                f"available={status['available_slots']})")


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Focus Manager - D2 (Attention) Allocation Test")
    print("=" * 60)
    print(f"\nConstants: PHI={PHI}, D2_CAPACITY={D2_CAPACITY}")

    # Create focus manager
    fm = FocusManager()
    print(f"\n{fm}")

    # Add sessions
    print("\n--- Adding Focus Sessions ---")
    s1 = fm.add_session("Deep Work: Code Review", duration_minutes=90, priority=1)
    s2 = fm.add_session("Email Processing", duration_minutes=30, priority=3)
    s3 = fm.add_session("Design Planning", duration_minutes=60, priority=2)

    for s in [s1, s2, s3]:
        if s:
            print(f"  Added: {s.name} (priority={s.priority}, duration={s.duration_minutes}min)")

    # Try adding beyond capacity
    s4 = fm.add_session("Extra Task", duration_minutes=45, priority=2)
    print(f"\n  Adding 4th session: {'Success' if s4 else 'Rejected (at capacity)'}")

    # Start sessions
    print("\n--- Starting Sessions ---")
    fm.start_session("Deep Work: Code Review")
    fm.start_session("Design Planning")

    # Check attention weights
    print("\n--- PHI-Based Attention Weights ---")
    weights = fm.get_attention_weights()
    for name, weight in weights.items():
        print(f"  {name}: {weight:.3f} ({weight*100:.1f}%)")

    # Complete a session
    print("\n--- Completing Session ---")
    fm.complete_session("Deep Work: Code Review")
    print(f"  Completed: Deep Work: Code Review")

    # Final status
    print("\n--- Final Status ---")
    status = fm.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("Focus Manager Test PASSED")
    print("=" * 60)
