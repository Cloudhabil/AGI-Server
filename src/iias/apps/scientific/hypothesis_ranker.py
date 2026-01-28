"""
Hypothesis Ranker - D10 (Wisdom) Scoring with Capacity 123
==========================================================

Ranks scientific hypotheses using the D10 (Wisdom) dimension scoring system.
The D10 dimension has a Lucas capacity of 123, representing the "Wisdom" level
in the 12-dimensional IIAS architecture.

Scoring Dimensions:
    - Novelty: How new/original is the hypothesis?
    - Testability: Can it be empirically tested?
    - Explanatory Power: How much does it explain?
    - Parsimony: Simplicity (Occam's razor)
    - Coherence: Fits with existing knowledge?
    - Predictive Power: Makes useful predictions?

The final D10 Wisdom score is PHI-weighted across all dimensions.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum

# Constants
PHI = 1.618033988749895
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]
D10_CAPACITY = 123  # Wisdom dimension
TOTAL_STATES = 840


class ScoreDimension(Enum):
    """Dimensions for hypothesis scoring."""
    NOVELTY = "novelty"
    TESTABILITY = "testability"
    EXPLANATORY_POWER = "explanatory_power"
    PARSIMONY = "parsimony"
    COHERENCE = "coherence"
    PREDICTIVE_POWER = "predictive_power"


# PHI-based weights for each scoring dimension
DIMENSION_WEIGHTS = {
    ScoreDimension.NOVELTY: 1.0,
    ScoreDimension.TESTABILITY: PHI,
    ScoreDimension.EXPLANATORY_POWER: PHI ** 2,
    ScoreDimension.PARSIMONY: PHI,
    ScoreDimension.COHERENCE: PHI ** 0.5,
    ScoreDimension.PREDICTIVE_POWER: PHI ** 2,
}


@dataclass
class HypothesisScores:
    """Individual scores for a hypothesis across all dimensions."""
    novelty: float = 0.0           # 0-1 scale
    testability: float = 0.0       # 0-1 scale
    explanatory_power: float = 0.0 # 0-1 scale
    parsimony: float = 0.0         # 0-1 scale
    coherence: float = 0.0         # 0-1 scale
    predictive_power: float = 0.0  # 0-1 scale

    def __post_init__(self):
        # Clamp all scores to [0, 1]
        self.novelty = max(0.0, min(1.0, self.novelty))
        self.testability = max(0.0, min(1.0, self.testability))
        self.explanatory_power = max(0.0, min(1.0, self.explanatory_power))
        self.parsimony = max(0.0, min(1.0, self.parsimony))
        self.coherence = max(0.0, min(1.0, self.coherence))
        self.predictive_power = max(0.0, min(1.0, self.predictive_power))

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "novelty": self.novelty,
            "testability": self.testability,
            "explanatory_power": self.explanatory_power,
            "parsimony": self.parsimony,
            "coherence": self.coherence,
            "predictive_power": self.predictive_power,
        }

    def get_score(self, dimension: ScoreDimension) -> float:
        """Get score for a specific dimension."""
        return getattr(self, dimension.value)


@dataclass
class Hypothesis:
    """A scientific hypothesis to be ranked."""
    hyp_id: str
    title: str
    description: str
    scores: HypothesisScores
    domain: str = "general"
    author: str = ""
    created_timestamp: float = field(default_factory=lambda: 0.0)

    # Computed scores (set by ranker)
    d10_wisdom_score: float = field(default=0.0)
    normalized_rank: float = field(default=0.0)
    capacity_slot: Optional[int] = field(default=None)


@dataclass
class RankingResult:
    """Result of ranking a hypothesis."""
    hypothesis: Hypothesis
    d10_wisdom_score: float
    weighted_scores: Dict[str, float]
    capacity_slot: int
    rank_position: int
    percentile: float
    accepted: bool
    message: str = ""


class HypothesisRanker:
    """
    Ranks hypotheses using D10 (Wisdom) scoring with capacity 123.

    Features:
        - PHI-weighted multi-dimensional scoring
        - D10 capacity limit of 123 ranked hypotheses
        - Automatic re-ranking on new submissions
        - Wisdom score normalization
    """

    def __init__(self):
        self.phi = PHI
        self.lucas = LUCAS
        self.d10_capacity = D10_CAPACITY
        self.total_states = TOTAL_STATES

        # Ranked hypotheses (sorted by wisdom score)
        self._ranked: List[Hypothesis] = []

        # All submitted hypotheses
        self._all_hypotheses: Dict[str, Hypothesis] = {}

        # Dimension weights
        self._weights = DIMENSION_WEIGHTS

    def calculate_wisdom_score(self, scores: HypothesisScores) -> float:
        """
        Calculate the D10 Wisdom score using PHI-weighted dimensions.

        The Wisdom score is normalized to [0, D10_CAPACITY].
        """
        weighted_sum = 0.0
        total_weight = 0.0

        for dimension, weight in self._weights.items():
            score = scores.get_score(dimension)
            weighted_sum += score * weight
            total_weight += weight

        # Normalize to [0, 1] then scale to D10 capacity
        normalized = weighted_sum / total_weight
        wisdom_score = normalized * self.d10_capacity

        return wisdom_score

    def submit(self, hypothesis: Hypothesis) -> RankingResult:
        """
        Submit a hypothesis for ranking.

        Args:
            hypothesis: The hypothesis to rank

        Returns:
            RankingResult with ranking details
        """
        # Calculate wisdom score
        wisdom_score = self.calculate_wisdom_score(hypothesis.scores)
        hypothesis.d10_wisdom_score = wisdom_score

        # Calculate weighted scores for reporting
        weighted_scores = {}
        for dimension, weight in self._weights.items():
            score = hypothesis.scores.get_score(dimension)
            weighted_scores[dimension.value] = score * weight

        # Store hypothesis
        self._all_hypotheses[hypothesis.hyp_id] = hypothesis

        # Check if it can enter top 123
        accepted = False
        capacity_slot = -1

        if len(self._ranked) < self.d10_capacity:
            # Room available
            self._ranked.append(hypothesis)
            accepted = True
        elif wisdom_score > self._ranked[-1].d10_wisdom_score:
            # Better than lowest ranked - replace
            evicted = self._ranked.pop()
            evicted.capacity_slot = None
            self._ranked.append(hypothesis)
            accepted = True

        # Re-sort and assign slots
        self._ranked.sort(key=lambda h: h.d10_wisdom_score, reverse=True)
        for i, h in enumerate(self._ranked):
            h.capacity_slot = i + 1
            h.normalized_rank = h.d10_wisdom_score / self.d10_capacity

        if accepted:
            capacity_slot = hypothesis.capacity_slot

        # Calculate rank position and percentile
        all_scores = [h.d10_wisdom_score for h in self._all_hypotheses.values()]
        all_scores.sort(reverse=True)
        rank_position = all_scores.index(wisdom_score) + 1
        percentile = (1 - rank_position / len(all_scores)) * 100 if all_scores else 0.0

        message = f"Ranked #{rank_position}" if accepted else "Below D10 capacity threshold"

        return RankingResult(
            hypothesis=hypothesis,
            d10_wisdom_score=wisdom_score,
            weighted_scores=weighted_scores,
            capacity_slot=capacity_slot,
            rank_position=rank_position,
            percentile=percentile,
            accepted=accepted,
            message=message
        )

    def get_top_n(self, n: int = 10) -> List[Hypothesis]:
        """Get top N ranked hypotheses."""
        return self._ranked[:min(n, len(self._ranked))]

    def get_wisdom_threshold(self) -> float:
        """Get the minimum wisdom score to enter top 123."""
        if len(self._ranked) < self.d10_capacity:
            return 0.0
        return self._ranked[-1].d10_wisdom_score

    def get_capacity_status(self) -> Dict[str, Any]:
        """Get D10 capacity status."""
        return {
            "dimension": "D10 (Wisdom)",
            "capacity": self.d10_capacity,
            "filled": len(self._ranked),
            "available": self.d10_capacity - len(self._ranked),
            "utilization": len(self._ranked) / self.d10_capacity,
            "threshold_score": self.get_wisdom_threshold(),
        }

    def get_score_distribution(self) -> Dict[str, Any]:
        """Get score distribution statistics."""
        if not self._ranked:
            return {"mean": 0, "min": 0, "max": 0, "std": 0}

        scores = [h.d10_wisdom_score for h in self._ranked]
        mean = sum(scores) / len(scores)
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)

        return {
            "mean": mean,
            "min": min(scores),
            "max": max(scores),
            "std": math.sqrt(variance),
            "count": len(scores),
        }

    def remove(self, hyp_id: str) -> bool:
        """Remove a hypothesis from ranking."""
        if hyp_id not in self._all_hypotheses:
            return False

        hypothesis = self._all_hypotheses.pop(hyp_id)
        if hypothesis in self._ranked:
            self._ranked.remove(hypothesis)
            # Re-assign slots
            for i, h in enumerate(self._ranked):
                h.capacity_slot = i + 1

        return True


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Hypothesis Ranker Test")
    print("=" * 60)

    ranker = HypothesisRanker()

    # Display constants
    print(f"\nPHI = {PHI}")
    print(f"LUCAS = {LUCAS}")
    print(f"D10_CAPACITY = {D10_CAPACITY}")
    print(f"TOTAL_STATES = {TOTAL_STATES}")

    # Display dimension weights
    print("\n--- PHI-Weighted Scoring Dimensions ---")
    for dim, weight in DIMENSION_WEIGHTS.items():
        print(f"  {dim.value:20s}: weight = {weight:.4f}")

    # Submit test hypotheses
    print("\n--- Submitting Hypotheses ---")
    test_hypotheses = [
        Hypothesis(
            hyp_id="hyp-001",
            title="Quantum Coherence in Biological Systems",
            description="Proposes quantum effects play role in photosynthesis",
            scores=HypothesisScores(
                novelty=0.8, testability=0.9, explanatory_power=0.7,
                parsimony=0.6, coherence=0.8, predictive_power=0.85
            ),
            domain="biophysics"
        ),
        Hypothesis(
            hyp_id="hyp-002",
            title="Dark Matter as Modified Gravity",
            description="Suggests dark matter effects are gravitational anomalies",
            scores=HypothesisScores(
                novelty=0.6, testability=0.5, explanatory_power=0.9,
                parsimony=0.8, coherence=0.4, predictive_power=0.7
            ),
            domain="cosmology"
        ),
        Hypothesis(
            hyp_id="hyp-003",
            title="Consciousness as Integrated Information",
            description="Proposes consciousness emerges from information integration",
            scores=HypothesisScores(
                novelty=0.7, testability=0.4, explanatory_power=0.8,
                parsimony=0.5, coherence=0.7, predictive_power=0.3
            ),
            domain="neuroscience"
        ),
        Hypothesis(
            hyp_id="hyp-004",
            title="RNA World Origin of Life",
            description="Self-replicating RNA preceded DNA and proteins",
            scores=HypothesisScores(
                novelty=0.5, testability=0.7, explanatory_power=0.8,
                parsimony=0.7, coherence=0.9, predictive_power=0.6
            ),
            domain="abiogenesis"
        ),
        Hypothesis(
            hyp_id="hyp-005",
            title="Multiverse from Eternal Inflation",
            description="Proposes multiple universes from inflationary cosmology",
            scores=HypothesisScores(
                novelty=0.9, testability=0.2, explanatory_power=0.95,
                parsimony=0.3, coherence=0.6, predictive_power=0.4
            ),
            domain="cosmology"
        ),
    ]

    for hyp in test_hypotheses:
        result = ranker.submit(hyp)
        print(f"\n{hyp.title}:")
        print(f"  D10 Wisdom Score: {result.d10_wisdom_score:.2f}/{D10_CAPACITY}")
        print(f"  Rank Position: #{result.rank_position}")
        print(f"  Percentile: {result.percentile:.1f}%")
        print(f"  Capacity Slot: {result.capacity_slot}")
        print(f"  Accepted: {result.accepted}")

    # Display top ranked
    print("\n--- Top Ranked Hypotheses ---")
    top = ranker.get_top_n(5)
    for i, hyp in enumerate(top, 1):
        print(f"  {i}. {hyp.title}")
        print(f"     Wisdom Score: {hyp.d10_wisdom_score:.2f}")

    # Display D10 capacity status
    print("\n--- D10 (Wisdom) Capacity Status ---")
    status = ranker.get_capacity_status()
    print(f"  Dimension: {status['dimension']}")
    print(f"  Capacity: {status['capacity']}")
    print(f"  Filled: {status['filled']}")
    print(f"  Utilization: {status['utilization']:.1%}")
    print(f"  Entry Threshold: {status['threshold_score']:.2f}")

    # Display score distribution
    print("\n--- Score Distribution ---")
    dist = ranker.get_score_distribution()
    print(f"  Mean: {dist['mean']:.2f}")
    print(f"  Min: {dist['min']:.2f}")
    print(f"  Max: {dist['max']:.2f}")
    print(f"  Std Dev: {dist['std']:.2f}")

    print("\n" + "=" * 60)
    print("Hypothesis Ranker Test Complete")
    print("=" * 60)
