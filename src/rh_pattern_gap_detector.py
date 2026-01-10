"""
PatternGapDetector - Analyzes research progress and identifies gaps

This module monitors the RH research effort and detects:
1. Convergence plateaus (current students not improving)
2. Unexplored parameter spaces
3. Blind spots in the research approach
4. Opportunities for specialized agent creation

Philosophy: Research is most productive when targeting high-ROI gaps.
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

from agents.agent_utils import query_deepseek


class PatternGapDetector:
    """
    Analyzes research results to find gaps and opportunities.

    Monitors:
    - Eigenvalue convergence per student
    - Parameter space coverage
    - Statistical patterns in results
    - Reasoning diversity
    """

    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.gap_history = []

    def analyze_eigenvalue_convergence(self, results_dir: Path) -> Dict[str, Any]:
        """
        Analyze how well each student's eigenvalues converge to zeta zeros.

        Returns metrics on convergence rate, error trends, saturation.
        """
        convergence_by_student = defaultdict(list)

        # Collect results from all students
        if results_dir.exists():
            for result_file in results_dir.glob("*.json"):
                try:
                    result = json.loads(result_file.read_text())
                    student_name = result.get("student_name", "unknown")
                    error = result.get("eigenvalue_error", float('inf'))
                    timestamp = result.get("timestamp")

                    if error < float('inf'):
                        convergence_by_student[student_name].append({
                            "error": error,
                            "timestamp": timestamp
                        })
                except:
                    pass

        # Analyze convergence trends
        analysis = {}
        for student, errors in convergence_by_student.items():
            if len(errors) >= 2:
                error_vals = [e["error"] for e in errors]
                recent_5 = error_vals[-5:] if len(error_vals) >= 5 else error_vals

                # Check for improvement
                improvement = (error_vals[0] - error_vals[-1]) / max(abs(error_vals[0]), 1)
                recent_trend = (recent_5[0] - recent_5[-1]) / max(abs(recent_5[0]), 1)

                analysis[student] = {
                    "total_attempts": len(errors),
                    "current_error": error_vals[-1],
                    "best_error": min(error_vals),
                    "worst_error": max(error_vals),
                    "total_improvement": improvement,
                    "recent_trend": recent_trend,
                    "is_plateauing": abs(recent_trend) < 0.05,  # < 5% improvement
                    "is_improving": recent_trend > 0.1
                }

        return analysis

    def detect_convergence_plateau(self, convergence_analysis: Dict) -> List[str]:
        """
        Detect which students have hit convergence plateaus.

        These are candidates for specialization or new student approaches.
        """
        plateauing_students = []

        for student, metrics in convergence_analysis.items():
            if metrics.get("is_plateauing") and metrics.get("total_attempts") > 5:
                plateauing_students.append(student)

        return plateauing_students

    def analyze_parameter_space_coverage(self, results_dir: Path) -> Dict[str, Any]:
        """
        Analyze which parameter regions have been explored.

        Identifies unexplored parameter spaces that might be high-ROI.
        """
        explored_params = defaultdict(set)
        param_performance = defaultdict(list)

        if results_dir.exists():
            for result_file in results_dir.glob("*.json"):
                try:
                    result = json.loads(result_file.read_text())
                    params = result.get("parameters", {})
                    error = result.get("eigenvalue_error", None)

                    for param_name, param_val in params.items():
                        # Discretize continuous params
                        if isinstance(param_val, (int, float)):
                            discretized = round(param_val, 2)
                            explored_params[param_name].add(discretized)

                            if error is not None:
                                param_performance[param_name].append({
                                    "value": discretized,
                                    "error": error
                                })
                except:
                    pass

        # Identify unexplored regions
        analysis = {}
        for param, values in explored_params.items():
            if len(values) >= 2:
                min_val = min(values)
                max_val = max(values)
                range_val = max_val - min_val

                # Estimate coverage density
                coverage = len(values) / max(range_val * 10, 1)  # Rough heuristic

                analysis[param] = {
                    "explored_values": sorted(values),
                    "min": min_val,
                    "max": max_val,
                    "coverage_density": min(coverage, 1.0),
                    "needs_exploration": coverage < 0.3
                }

        return analysis

    def find_reasoning_blind_spots(self, proposals_dir: Path) -> List[Dict]:
        """
        Analyze proposals to find blind spots in reasoning.

        Looks for:
        - Repeated approaches (lack of diversity)
        - Ignored mathematical domains
        - Missing perspectives
        """
        proposals = []
        keywords_by_domain = defaultdict(int)

        if proposals_dir.exists():
            for proposal_file in proposals_dir.glob("*.json"):
                try:
                    proposal = json.loads(proposal_file.read_text())
                    content = proposal.get("content", "").lower()
                    proposals.append(content)

                    # Count domain keyword mentions
                    domains = {
                        "quantum": ["quantum", "hamiltonian", "eigenvalue", "wavefunction"],
                        "topology": ["topological", "manifold", "homology", "homotopy"],
                        "algebra": ["group", "ring", "field", "algebra", "invariant"],
                        "analysis": ["analytic", "convergence", "continuity", "limit"],
                        "number_theory": ["prime", "divisor", "modular", "diophantine"],
                        "operator": ["operator", "spectrum", "pseudospectra", "adjoint"],
                        "probability": ["random", "distribution", "stochastic", "measure"]
                    }

                    for domain, keywords in domains.items():
                        for keyword in keywords:
                            if keyword in content:
                                keywords_by_domain[domain] += 1
                                break

                except:
                    pass

        # Identify underexplored domains
        blind_spots = []
        total_proposals = len(proposals)

        for domain, count in keywords_by_domain.items():
            frequency = count / max(total_proposals, 1)
            if frequency < 0.2:  # Mentioned in < 20% of proposals
                blind_spots.append({
                    "domain": domain,
                    "mention_frequency": frequency,
                    "opportunity": f"Mathematical domain '{domain}' is underexplored"
                })

        return sorted(blind_spots, key=lambda x: x["mention_frequency"])

    def detect_emerging_patterns(self, results_dir: Path) -> List[Dict]:
        """
        Detect patterns that are emerging but not yet dominant.

        These can be early signals of breakthrough directions.
        """
        patterns = defaultdict(float)

        if results_dir.exists():
            for result_file in results_dir.glob("*.json"):
                try:
                    result = json.loads(result_file.read_text())
                    error = result.get("eigenvalue_error", float('inf'))

                    # Look for promising error ranges
                    if error < 50:
                        patterns["low_error_convergence"] += 1
                    if error < 10:
                        patterns["very_high_accuracy"] += 1

                    # Track parameter combinations that work
                    params = result.get("parameters", {})
                    if "a" in params and "b" in params:
                        param_sig = f"a={params['a']:.2f},b={params['b']:.2f}"
                        if error < 100:
                            patterns[param_sig] += 0.5

                except:
                    pass

        # Filter for patterns with multiple instances
        emerging = [
            {"pattern": p, "strength": s}
            for p, s in patterns.items()
            if s >= 1.5
        ]

        return sorted(emerging, key=lambda x: x["strength"], reverse=True)

    def synthesize_gap_report(self, convergence: Dict, param_coverage: Dict,
                             blind_spots: List, patterns: List) -> Dict[str, Any]:
        """
        Synthesize all analysis into actionable gap report.

        Returns recommendations for new students to create.
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "convergence_status": convergence,
            "parameter_coverage": param_coverage,
            "blind_spots": blind_spots[:3],  # Top 3
            "emerging_patterns": patterns[:3],  # Top 3
            "recommendations": []
        }

        # Generate recommendations
        recommendations = []

        # Check for plateauing students
        for student, metrics in convergence.items():
            if metrics.get("is_plateauing"):
                recommendations.append({
                    "type": "specialized_extension",
                    "for_student": student,
                    "description": f"{student} has plateaued. Create a specialized variant.",
                    "priority": "high"
                })

        # Check for unexplored parameter spaces
        for param, coverage in param_coverage.items():
            if coverage.get("needs_exploration"):
                recommendations.append({
                    "type": "parameter_space_specialist",
                    "parameter": param,
                    "description": f"Parameter '{param}' needs exploration. Create specialist.",
                    "priority": "medium"
                })

        # Check for blind spots
        for blind_spot in blind_spots[:1]:
            recommendations.append({
                "type": "domain_specialist",
                "domain": blind_spot["domain"],
                "description": f"Domain '{blind_spot['domain']}' is underexplored. Create domain specialist.",
                "priority": "high"
            })

        report["recommendations"] = recommendations
        return report

    def run_gap_detection_cycle(self, session_dir: Path) -> Dict[str, Any]:
        """
        Run a complete gap detection analysis.

        Monitors the entire research effort and produces a gap report.
        """
        results_dir = session_dir / "rh_results"
        proposals_dir = session_dir / "rh_proposals"

        print("\n[PatternGapDetector] === Running Gap Detection Cycle ===")

        # Analyze convergence
        print("  [Phase 1] Analyzing eigenvalue convergence...")
        convergence = self.analyze_eigenvalue_convergence(results_dir)

        # Find plateau students
        plateauing = self.detect_convergence_plateau(convergence)
        if plateauing:
            print(f"  ⚠ Plateauing students: {plateauing}")

        # Analyze parameter coverage
        print("  [Phase 2] Analyzing parameter space coverage...")
        param_coverage = self.analyze_parameter_space_coverage(results_dir)

        # Detect blind spots
        print("  [Phase 3] Detecting reasoning blind spots...")
        blind_spots = self.find_reasoning_blind_spots(proposals_dir)
        if blind_spots:
            print(f"  ⚠ Blind spots: {[b['domain'] for b in blind_spots[:2]]}")

        # Detect emerging patterns
        print("  [Phase 4] Detecting emerging patterns...")
        patterns = self.detect_emerging_patterns(results_dir)
        if patterns:
            print(f"  ✓ Emerging patterns: {[p['pattern'] for p in patterns[:2]]}")

        # Synthesize report
        print("  [Phase 5] Synthesizing gap report...")
        report = self.synthesize_gap_report(convergence, param_coverage, blind_spots, patterns)

        # Store report
        report_file = session_dir / "gap_detection_report.json"
        report_file.write_text(json.dumps(report, indent=2))

        self.gap_history.append(report)

        print(f"  ✓ Found {len(report['recommendations'])} opportunities for new students")

        return report

    def get_top_priority_gaps(self, report: Dict, limit: int = 3) -> List[Dict]:
        """Extract top priority gaps from report."""
        high_priority = [r for r in report.get("recommendations", [])
                        if r.get("priority") == "high"]
        return high_priority[:limit]
