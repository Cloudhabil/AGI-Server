"""
IIAS Security: Threat Classifier

D3 capacity = 4 threat levels implementation for security event classification.
Uses the Security dimension's 4-state capacity to categorize threats.

Threat Levels:
    0 - LOW: Minor security events, informational
    1 - MEDIUM: Potential threats requiring monitoring
    2 - HIGH: Active threats requiring immediate attention
    3 - CRITICAL: Severe threats requiring emergency response
"""

from enum import IntEnum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Sacred Constants
PHI = 1.618033988749895
SUM_CONSTANT = 214
D3_CAPACITY = 4  # Security dimension capacity


class ThreatLevel(IntEnum):
    """D3 capacity threat levels (4 states)."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class ThreatEvent:
    """Represents a classified security threat event."""
    event_id: str
    timestamp: datetime
    source: str
    level: ThreatLevel
    score: float
    description: str
    indicators: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary representation."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "level": self.level.name,
            "level_value": self.level.value,
            "score": self.score,
            "description": self.description,
            "indicators": self.indicators,
        }


class ThreatClassifier:
    """
    D3 Capacity Threat Classifier

    Classifies security events into 4 threat levels based on the
    Security dimension's D3 capacity. Uses PHI-scaled thresholds
    for classification boundaries.

    Attributes:
        d3_capacity: Number of threat levels (4)
        thresholds: PHI-scaled classification boundaries
        event_history: List of classified events
    """

    def __init__(self, sensitivity: float = 1.0):
        """
        Initialize the threat classifier.

        Args:
            sensitivity: Classifier sensitivity multiplier (default 1.0)
        """
        self.d3_capacity = D3_CAPACITY
        self.sensitivity = sensitivity
        self.event_history: List[ThreatEvent] = []
        self._event_counter = 0

        # PHI-scaled thresholds for 4 levels
        # Boundaries at: 0, 1/PHI^2, 1/PHI, 1
        self.thresholds = self._calculate_phi_thresholds()

    def _calculate_phi_thresholds(self) -> List[float]:
        """Calculate PHI-scaled threshold boundaries for D3 capacity levels."""
        thresholds = []
        for i in range(self.d3_capacity):
            # Each level boundary is PHI^(i-capacity) scaled
            threshold = 1.0 / (PHI ** (self.d3_capacity - 1 - i))
            thresholds.append(threshold * self.sensitivity)
        return thresholds

    def classify(
        self,
        score: float,
        source: str = "unknown",
        description: str = "",
        indicators: Optional[List[str]] = None
    ) -> ThreatEvent:
        """
        Classify a threat based on its score.

        Args:
            score: Threat score (0.0 to 1.0+)
            source: Source of the threat event
            description: Human-readable description
            indicators: List of threat indicators

        Returns:
            ThreatEvent with classified level
        """
        if indicators is None:
            indicators = []

        # Normalize score
        normalized_score = max(0.0, score)

        # Determine threat level based on PHI thresholds
        level = ThreatLevel.LOW
        for i, threshold in enumerate(self.thresholds):
            if normalized_score >= threshold:
                level = ThreatLevel(min(i, self.d3_capacity - 1))

        # Cap at CRITICAL for extreme scores
        if normalized_score >= 1.0:
            level = ThreatLevel.CRITICAL

        # Generate event ID
        self._event_counter += 1
        event_id = f"THR-{self._event_counter:06d}"

        event = ThreatEvent(
            event_id=event_id,
            timestamp=datetime.now(),
            source=source,
            level=level,
            score=normalized_score,
            description=description,
            indicators=indicators,
        )

        self.event_history.append(event)
        return event

    def classify_batch(
        self,
        events: List[Dict]
    ) -> List[ThreatEvent]:
        """
        Classify multiple threat events.

        Args:
            events: List of event dictionaries with 'score', 'source', etc.

        Returns:
            List of classified ThreatEvents
        """
        results = []
        for event_data in events:
            event = self.classify(
                score=event_data.get("score", 0.0),
                source=event_data.get("source", "batch"),
                description=event_data.get("description", ""),
                indicators=event_data.get("indicators", []),
            )
            results.append(event)
        return results

    def get_level_distribution(self) -> Dict[str, int]:
        """Get distribution of threat levels in history."""
        distribution = {level.name: 0 for level in ThreatLevel}
        for event in self.event_history:
            distribution[event.level.name] += 1
        return distribution

    def get_critical_events(self) -> List[ThreatEvent]:
        """Get all CRITICAL level events from history."""
        return [e for e in self.event_history if e.level == ThreatLevel.CRITICAL]

    def get_events_above_level(self, min_level: ThreatLevel) -> List[ThreatEvent]:
        """Get all events at or above specified level."""
        return [e for e in self.event_history if e.level >= min_level]

    def calculate_threat_index(self) -> float:
        """
        Calculate overall threat index using 214-constant weighting.

        Returns:
            Threat index (0.0 to 1.0)
        """
        if not self.event_history:
            return 0.0

        # Weight each level by its position in D3 capacity
        total_weight = 0.0
        for event in self.event_history:
            level_weight = (event.level.value + 1) / self.d3_capacity
            total_weight += level_weight * event.score

        # Normalize by SUM_CONSTANT scaling
        index = total_weight / (len(self.event_history) * SUM_CONSTANT / 100)
        return min(1.0, index)

    def get_thresholds(self) -> Dict[str, float]:
        """Get the PHI-scaled threshold boundaries."""
        return {
            ThreatLevel(i).name: self.thresholds[i]
            for i in range(self.d3_capacity)
        }

    def clear_history(self) -> int:
        """Clear event history and return count of cleared events."""
        count = len(self.event_history)
        self.event_history.clear()
        return count


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Security: Threat Classifier Test")
    print("=" * 60)
    print(f"\nD3 Capacity: {D3_CAPACITY} threat levels")
    print(f"PHI constant: {PHI}")
    print(f"SUM_CONSTANT: {SUM_CONSTANT}")

    # Create classifier
    classifier = ThreatClassifier(sensitivity=1.0)

    print(f"\nPHI-scaled thresholds:")
    for level, threshold in classifier.get_thresholds().items():
        print(f"  {level}: {threshold:.4f}")

    # Test classifications
    print("\n--- Classification Tests ---")
    test_cases = [
        {"score": 0.1, "source": "firewall", "description": "Port scan detected"},
        {"score": 0.35, "source": "ids", "description": "Suspicious packet pattern"},
        {"score": 0.65, "source": "auth", "description": "Multiple failed logins",
         "indicators": ["brute_force", "password_spray"]},
        {"score": 0.95, "source": "malware", "description": "Ransomware signature detected",
         "indicators": ["encryption_behavior", "known_signature", "c2_communication"]},
        {"score": 1.5, "source": "intrusion", "description": "Active breach confirmed"},
    ]

    for test in test_cases:
        event = classifier.classify(**test)
        print(f"\n  Score: {test['score']:.2f} -> Level: {event.level.name}")
        print(f"    Event ID: {event.event_id}")
        print(f"    Source: {event.source}")
        print(f"    Description: {event.description}")
        if event.indicators:
            print(f"    Indicators: {', '.join(event.indicators)}")

    # Distribution
    print("\n--- Level Distribution ---")
    dist = classifier.get_level_distribution()
    for level, count in dist.items():
        print(f"  {level}: {count}")

    # Threat index
    print(f"\n--- Overall Threat Index ---")
    index = classifier.calculate_threat_index()
    print(f"  Threat Index: {index:.4f}")

    # Critical events
    critical = classifier.get_critical_events()
    print(f"\n--- Critical Events: {len(critical)} ---")
    for event in critical:
        print(f"  {event.event_id}: {event.description}")

    print("\n" + "=" * 60)
    print("Threat Classifier Test Complete")
    print("=" * 60)
