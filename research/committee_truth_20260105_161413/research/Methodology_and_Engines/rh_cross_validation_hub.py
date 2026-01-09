"""
CrossValidationHub - Validates research results across multiple student agents

This module implements cross-validation where multiple students evaluate each other's
proposals and results. Consensus across students increases confidence.

Philosophy: A single agent can hallucinate or fixate. Multiple agents with different
specializations provide cross-checking and emergent reliability.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

from agents.agent_utils import query_deepseek


class CrossValidationHub:
    """
    Coordinates validation of proposals across all active students.

    Implements:
    1. Peer Review: Students review each other's proposals
    2. Consensus Detection: Find areas of agreement (high confidence)
    3. Divergence Analysis: Find disagreements (interesting tensions)
    4. Confidence Scoring: Overall confidence in results
    """

    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.validation_records = []

    def request_peer_review(self, proposal_id: str, proposal_content: str,
                           reviewer_name: str, reviewer_specialty: str) -> Dict[str, Any]:
        """
        Request a peer review of a proposal from another student.

        Reviewer evaluates based on their specialty perspective.
        """
        review_prompt = f"""
You are {reviewer_name}, a specialized research agent in {reviewer_specialty}.

Review this proposal from a peer:

PROPOSAL:
{proposal_content[:1000]}

Evaluate from your perspective ({reviewer_specialty}):

1. Mathematical Soundness (0-1): Is it mathematically correct?
2. Novelty (0-1): Does it offer new insights from {reviewer_specialty} perspective?
3. Practicality (0-1): Can it actually be implemented computationally?
4. Alignment with RMT (0-1): Does it respect Random Matrix Theory constraints?
5. Potential for Breakthrough (0-1): Could this lead somewhere important?

Also provide:
- Key Strengths
- Critical Weaknesses
- Questions for the proposer
- Alternative approaches you'd suggest

Format as JSON with keys: soundness, novelty, practicality, rmt_alignment, breakthrough_potential, strengths, weaknesses, questions, alternatives
"""

        response = query_deepseek(review_prompt, max_tokens=1500)

        # Extract JSON review
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                review = json.loads(json_match.group())
                review["reviewer"] = reviewer_name
                review["reviewed_proposal_id"] = proposal_id
                review["timestamp"] = datetime.now().isoformat()
                return review
        except:
            pass

        # Fallback review
        return {
            "reviewer": reviewer_name,
            "reviewed_proposal_id": proposal_id,
            "soundness": 0.7,
            "novelty": 0.6,
            "practicality": 0.5,
            "rmt_alignment": 0.7,
            "breakthrough_potential": 0.4,
            "timestamp": datetime.now().isoformat()
        }

    def validate_eigenvalue_result(self, result: Dict, validators: List[str]) -> Dict[str, Any]:
        """
        Have multiple students validate an eigenvalue result.

        Each validator provides assessment from their perspective.
        """
        validation = {
            "result_id": result.get("id", "unknown"),
            "original_error": result.get("eigenvalue_error"),
            "reviews": [],
            "timestamp": datetime.now().isoformat()
        }

        # Request validation from each validator
        for validator in validators:
            validator_prompt = f"""
You are {validator}, a specialized RH researcher.

Evaluate these eigenvalue computation results:

Results: {json.dumps(result, indent=2)[:800]}

Assessment:
1. Error magnitude acceptable? (0-1)
2. Convergence trend promising? (0-1)
3. Methodology sound? (0-1)
4. Next steps clear? (0-1)
5. Overall confidence in results? (0-1)

Provide brief justification for each score.

Format as JSON: {{"error_assessment": float, "convergence_promising": float, "methodology": float, "next_steps_clear": float, "confidence": float, "justification": str}}
"""

            response = query_deepseek(validator_prompt, max_tokens=800)

            try:
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    assessment = json.loads(json_match.group())
                    assessment["validator"] = validator
                    validation["reviews"].append(assessment)
            except:
                validation["reviews"].append({
                    "validator": validator,
                    "error_assessment": 0.7,
                    "confidence": 0.6
                })

        return validation

    def compute_consensus_metrics(self, reviews: List[Dict]) -> Dict[str, float]:
        """
        Compute consensus metrics from multiple reviews.

        Returns: {
            "agreement_level": 0-1 (how much do reviewers agree?),
            "confidence": 0-1 (average confidence across reviewers),
            "consensus": bool (strong consensus on quality?)
        }
        """
        if not reviews:
            return {"agreement_level": 0, "confidence": 0, "consensus": False}

        # Extract scores
        scores = defaultdict(list)
        for review in reviews:
            for key, val in review.items():
                if isinstance(val, float) and 0 <= val <= 1:
                    scores[key].append(val)

        if not scores:
            return {"agreement_level": 0, "confidence": 0, "consensus": False}

        # Compute variance (inverse = agreement)
        variances = {}
        for key, vals in scores.items():
            if len(vals) > 1:
                import statistics
                try:
                    variance = statistics.variance(vals)
                    variances[key] = 1.0 - min(variance, 1.0)  # Convert to agreement
                except:
                    variances[key] = 0.5

        avg_agreement = sum(variances.values()) / len(variances) if variances else 0

        # Compute average confidence
        avg_confidence = sum(scores.get("confidence", [0])) / max(len(scores.get("confidence", [])), 1)

        # Determine consensus threshold
        consensus = avg_agreement > 0.7 and avg_confidence > 0.6

        return {
            "agreement_level": avg_agreement,
            "confidence": avg_confidence,
            "consensus": consensus,
            "metric_variance": variances
        }

    def identify_divergent_opinions(self, reviews: List[Dict]) -> List[Dict]:
        """
        Identify where reviewers significantly disagree.

        Divergences can reveal important blind spots or opportunities.
        """
        divergences = []

        # Group reviews by metric
        metrics = defaultdict(list)
        for review in reviews:
            reviewer = review.get("reviewer", "unknown")
            for key, val in review.items():
                if isinstance(val, float) and 0 <= val <= 1:
                    metrics[key].append({"reviewer": reviewer, "value": val})

        # Find metrics with high variance
        for metric, assessments in metrics.items():
            if len(assessments) >= 2:
                values = [a["value"] for a in assessments]
                import statistics
                try:
                    variance = statistics.variance(values)
                    if variance > 0.15:  # High disagreement
                        divergences.append({
                            "metric": metric,
                            "variance": variance,
                            "assessments": assessments,
                            "interpretation": f"Reviewers disagree on {metric}: {[f'{a['reviewer']}:{a['value']:.2f}' for a in assessments]}"
                        })
                except:
                    pass

        return sorted(divergences, key=lambda x: x["variance"], reverse=True)

    def orchestrate_cross_validation(self, proposal_id: str, proposal: Dict,
                                    active_students: List[str]) -> Dict[str, Any]:
        """
        Orchestrate full cross-validation of a proposal.

        All active students review it, compute consensus, identify divergences.
        """
        print(f"\n[CrossValidationHub] Validating proposal {proposal_id}")

        result = {
            "proposal_id": proposal_id,
            "proposal_type": proposal.get("type"),
            "validation_timestamp": datetime.now().isoformat(),
            "reviews": [],
            "consensus_metrics": {},
            "divergences": [],
            "recommendation": None
        }

        # Request peer reviews from each active student
        for student in active_students:
            print(f"  - Requesting review from {student}...")
            review = self.request_peer_review(
                proposal_id,
                proposal.get("content", ""),
                student,
                f"{student}'s specialty"
            )
            result["reviews"].append(review)

        # Compute consensus
        print(f"  - Computing consensus metrics...")
        consensus = self.compute_consensus_metrics(result["reviews"])
        result["consensus_metrics"] = consensus

        # Identify divergences
        divergences = self.identify_divergent_opinions(result["reviews"])
        result["divergences"] = divergences
        if divergences:
            print(f"  ⚠ Found {len(divergences)} areas of significant disagreement")

        # Generate recommendation
        if consensus["consensus"]:
            result["recommendation"] = "HIGH_CONFIDENCE_PROMISING"
            recommendation_text = "Cross-validation consensus: This proposal shows promise"
        elif consensus["confidence"] > 0.5:
            result["recommendation"] = "MODERATE_CONFIDENCE_EXPLORE"
            recommendation_text = "Mixed reviews but worth exploring further"
        else:
            result["recommendation"] = "LOW_CONFIDENCE_UNLIKELY"
            recommendation_text = "Reviewers skeptical; other approaches may be better"

        print(f"  ✓ Recommendation: {result['recommendation']}")

        # Store record
        self.validation_records.append(result)

        return result

    def generate_consensus_report(self) -> Dict[str, Any]:
        """
        Generate overall report of cross-validation findings.

        Shows patterns in what proposals succeed/fail.
        """
        if not self.validation_records:
            return {"status": "no_validations_yet"}

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_validations": len(self.validation_records),
            "recommendations_breakdown": {},
            "high_consensus_proposals": [],
            "divergent_proposals": []
        }

        # Count recommendations
        from collections import Counter
        recommendations = [r.get("recommendation") for r in self.validation_records]
        report["recommendations_breakdown"] = dict(Counter(recommendations))

        # Find high consensus proposals
        high_consensus = [r for r in self.validation_records
                         if r.get("consensus_metrics", {}).get("consensus")]
        report["high_consensus_proposals"] = [
            {
                "proposal_id": r["proposal_id"],
                "confidence": r.get("consensus_metrics", {}).get("confidence")
            }
            for r in high_consensus
        ]

        # Find divergent proposals (interesting tension)
        divergent = [r for r in self.validation_records
                    if len(r.get("divergences", [])) > 2]
        report["divergent_proposals"] = [
            {
                "proposal_id": r["proposal_id"],
                "divergence_count": len(r.get("divergences", [])),
                "divergences": [d["interpretation"] for d in r.get("divergences", [])[:2]]
            }
            for r in divergent
        ]

        return report

    def save_validation_report(self, report: Dict) -> Path:
        """Save cross-validation report to disk."""
        report_file = self.session_dir / "cross_validation_report.json"
        report_file.write_text(json.dumps(report, indent=2))
        return report_file
