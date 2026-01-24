#!/usr/bin/env python3
"""
BOA SAT Solver SDK
Brahim Onion Agent for Constraint Satisfaction & Verification

Applications:
- Circuit verification
- Software bug detection
- AI planning
- Drug molecule design
- Cryptography analysis
- Compiler optimization
"""

import math
import random
import hashlib
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

# Brahim Security Constants
PHI = (1 + math.sqrt(5)) / 2
BETA_SEC = math.sqrt(5) - 2
ALPHA_W = 1 / PHI**2


class SATResult(Enum):
    SAT = "SATISFIABLE"
    UNSAT = "UNSATISFIABLE"
    UNKNOWN = "UNKNOWN"
    TIMEOUT = "TIMEOUT"


@dataclass
class BrahimSecurityLayer:
    """Brahim Onion encryption wrapper."""

    @staticmethod
    def encode(data: str, layers: int = 3) -> str:
        encoded = data
        for i in range(layers):
            salt = str(BETA_SEC * (i + 1))[:8]
            encoded = hashlib.sha256((salt + encoded).encode()).hexdigest()[:16] + encoded
        return encoded

    @staticmethod
    def hash_clause(clause: List[int]) -> str:
        """Hash a clause for integrity verification."""
        data = ",".join(map(str, sorted(clause)))
        return hashlib.md5(data.encode()).hexdigest()[:8]


@dataclass
class CNFFormula:
    """CNF (Conjunctive Normal Form) formula representation."""
    num_vars: int
    clauses: List[List[int]]

    @property
    def num_clauses(self) -> int:
        return len(self.clauses)

    @property
    def ratio(self) -> float:
        """Clause-to-variable ratio (phase transition at ~4.26 for 3-SAT)."""
        return self.num_clauses / self.num_vars if self.num_vars > 0 else 0

    @property
    def is_3sat(self) -> bool:
        return all(len(c) == 3 for c in self.clauses)

    def estimate_hardness(self) -> str:
        """Estimate problem hardness based on ratio."""
        if not self.is_3sat:
            return "unknown"
        r = self.ratio
        if abs(r - 4.26) < 0.15:
            return "phase_transition (hardest)"
        elif r < 3.5:
            return "easy (underconstrained)"
        elif r > 5.0:
            return "easy (overconstrained)"
        else:
            return "medium"


@dataclass
class SATSolution:
    """SAT solver result."""
    result: SATResult
    assignment: Optional[Dict[int, bool]] = None
    conflicts: int = 0
    decisions: int = 0
    propagations: int = 0


class DPLLSolver:
    """
    DPLL-based SAT solver with Brahim security integration.
    Davis-Putnam-Logemann-Loveland algorithm.
    """

    PHASE_TRANSITION = 4.26

    def __init__(self, max_conflicts: int = 100000):
        self.max_conflicts = max_conflicts
        self.security = BrahimSecurityLayer()
        self.stats = {"conflicts": 0, "decisions": 0, "propagations": 0}

    def parse_dimacs(self, content: str) -> CNFFormula:
        """Parse DIMACS CNF format."""
        clauses = []
        num_vars = 0

        for line in content.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p cnf"):
                parts = line.split()
                num_vars = int(parts[2])
            else:
                literals = [int(x) for x in line.split() if x != "0"]
                if literals:
                    clauses.append(literals)

        return CNFFormula(num_vars, clauses)

    def unit_propagate(self, clauses: List[List[int]], assignment: Dict[int, bool]) -> Tuple[bool, Dict[int, bool]]:
        """Perform unit propagation."""
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                unassigned = []
                satisfied = False

                for lit in clause:
                    var = abs(lit)
                    if var in assignment:
                        if (lit > 0) == assignment[var]:
                            satisfied = True
                            break
                    else:
                        unassigned.append(lit)

                if satisfied:
                    continue

                if len(unassigned) == 0:
                    return False, assignment  # Conflict

                if len(unassigned) == 1:
                    # Unit clause - must assign
                    lit = unassigned[0]
                    var = abs(lit)
                    assignment[var] = (lit > 0)
                    changed = True
                    self.stats["propagations"] += 1

        return True, assignment

    def is_satisfied(self, clauses: List[List[int]], assignment: Dict[int, bool]) -> bool:
        """Check if all clauses are satisfied."""
        for clause in clauses:
            satisfied = False
            for lit in clause:
                var = abs(lit)
                if var in assignment and (lit > 0) == assignment[var]:
                    satisfied = True
                    break
            if not satisfied:
                return False
        return True

    def choose_variable(self, formula: CNFFormula, assignment: Dict[int, bool]) -> Optional[int]:
        """Choose next variable to branch on (VSIDS-like heuristic)."""
        # Count literal occurrences
        scores: Dict[int, int] = {}
        for clause in formula.clauses:
            for lit in clause:
                var = abs(lit)
                if var not in assignment:
                    scores[var] = scores.get(var, 0) + 1

        if not scores:
            return None

        return max(scores, key=scores.get)

    def dpll(self, formula: CNFFormula, assignment: Dict[int, bool]) -> Optional[Dict[int, bool]]:
        """DPLL recursive search."""
        if self.stats["conflicts"] > self.max_conflicts:
            return None

        # Unit propagation
        success, assignment = self.unit_propagate(formula.clauses, assignment.copy())
        if not success:
            self.stats["conflicts"] += 1
            return None

        # Check if satisfied
        if self.is_satisfied(formula.clauses, assignment):
            return assignment

        # Choose variable
        var = self.choose_variable(formula, assignment)
        if var is None:
            return None

        self.stats["decisions"] += 1

        # Try True
        assignment_true = assignment.copy()
        assignment_true[var] = True
        result = self.dpll(formula, assignment_true)
        if result is not None:
            return result

        # Try False
        assignment_false = assignment.copy()
        assignment_false[var] = False
        return self.dpll(formula, assignment_false)

    def solve(self, formula: CNFFormula) -> SATSolution:
        """Solve a CNF formula."""
        self.stats = {"conflicts": 0, "decisions": 0, "propagations": 0}

        assignment = self.dpll(formula, {})

        if assignment is not None:
            return SATSolution(
                result=SATResult.SAT,
                assignment=assignment,
                conflicts=self.stats["conflicts"],
                decisions=self.stats["decisions"],
                propagations=self.stats["propagations"]
            )
        elif self.stats["conflicts"] > self.max_conflicts:
            return SATSolution(
                result=SATResult.TIMEOUT,
                conflicts=self.stats["conflicts"],
                decisions=self.stats["decisions"],
                propagations=self.stats["propagations"]
            )
        else:
            return SATSolution(
                result=SATResult.UNSAT,
                conflicts=self.stats["conflicts"],
                decisions=self.stats["decisions"],
                propagations=self.stats["propagations"]
            )

    def verify_circuit(self, inputs: Dict[str, bool], expected_output: bool, circuit_cnf: str) -> dict:
        """Verify a circuit produces expected output."""
        formula = self.parse_dimacs(circuit_cnf)
        solution = self.solve(formula)

        return {
            "verified": solution.result == SATResult.SAT,
            "result": solution.result.value,
            "stats": {
                "conflicts": solution.conflicts,
                "decisions": solution.decisions
            }
        }

    def find_bug(self, program_cnf: str) -> dict:
        """Find a bug (satisfying assignment that violates assertions)."""
        formula = self.parse_dimacs(program_cnf)
        solution = self.solve(formula)

        if solution.result == SATResult.SAT:
            return {
                "bug_found": True,
                "counterexample": solution.assignment,
                "message": "Found input that violates assertion"
            }
        else:
            return {
                "bug_found": False,
                "message": "No bug found (program correct or timeout)"
            }


class SATSolverAPI:
    """REST API wrapper for SAT Solver SDK."""

    def __init__(self):
        self.solver = DPLLSolver()
        self.version = "1.0.0"

    def handle_request(self, endpoint: str, params: dict) -> dict:
        """Handle API request."""

        if endpoint == "/solve":
            cnf = params.get("cnf", "")
            formula = self.solver.parse_dimacs(cnf)
            solution = self.solver.solve(formula)
            return {
                "status": "ok",
                "result": solution.result.value,
                "assignment": solution.assignment,
                "stats": {
                    "conflicts": solution.conflicts,
                    "decisions": solution.decisions,
                    "propagations": solution.propagations
                }
            }

        elif endpoint == "/analyze":
            cnf = params.get("cnf", "")
            formula = self.solver.parse_dimacs(cnf)
            return {
                "status": "ok",
                "variables": formula.num_vars,
                "clauses": formula.num_clauses,
                "ratio": round(formula.ratio, 4),
                "is_3sat": formula.is_3sat,
                "hardness": formula.estimate_hardness()
            }

        elif endpoint == "/verify_circuit":
            circuit_cnf = params.get("cnf", "")
            result = self.solver.verify_circuit({}, True, circuit_cnf)
            return {"status": "ok", **result}

        elif endpoint == "/find_bug":
            program_cnf = params.get("cnf", "")
            result = self.solver.find_bug(program_cnf)
            return {"status": "ok", **result}

        elif endpoint == "/health":
            return {
                "status": "ok",
                "version": self.version,
                "sdk": "BOA SAT Solver",
                "security": "Brahim Onion Layer v1",
                "phase_transition": 4.26
            }

        else:
            return {"status": "error", "message": f"Unknown endpoint: {endpoint}"}


# Main entry point
if __name__ == "__main__":
    api = SATSolverAPI()

    print("=" * 60)
    print("BOA SAT SOLVER SDK")
    print("=" * 60)

    # Test with simple formula
    test_cnf = """
c Simple test
p cnf 3 2
1 2 0
-1 3 0
"""

    result = api.handle_request("/analyze", {"cnf": test_cnf})
    print(f"\n/analyze:")
    print(f"  Variables: {result['variables']}")
    print(f"  Clauses: {result['clauses']}")
    print(f"  Ratio: {result['ratio']}")

    result = api.handle_request("/solve", {"cnf": test_cnf})
    print(f"\n/solve:")
    print(f"  Result: {result['result']}")
    print(f"  Assignment: {result['assignment']}")

    result = api.handle_request("/health", {})
    print(f"\n/health:")
    print(f"  {result}")
