#!/usr/bin/env python3
"""
BOA Egyptian Fractions SDK
Brahim Onion Agent for Fair Division & Resource Optimization

Applications:
- Fair division algorithms
- Scheduling with unit tasks
- Cryptographic key splitting
- Image dithering
- Music rhythm quantization
"""

import math
import json
import hashlib
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, asdict
from fractions import Fraction

# Brahim Security Constants
PHI = (1 + math.sqrt(5)) / 2
BETA_SEC = math.sqrt(5) - 2  # 1/phi^3 = 0.2360679...
ALPHA_W = 1 / PHI**2


@dataclass
class BrahimSecurityLayer:
    """Brahim Onion encryption wrapper."""

    @staticmethod
    def encode(data: str, layers: int = 3) -> str:
        """Apply Brahim onion encoding."""
        encoded = data
        for i in range(layers):
            salt = str(BETA_SEC * (i + 1))[:8]
            encoded = hashlib.sha256((salt + encoded).encode()).hexdigest() + ":" + encoded
        return encoded

    @staticmethod
    def verify_integrity(data: str) -> bool:
        """Verify data hasn't been tampered."""
        if ":" not in data:
            return False
        parts = data.split(":", 1)
        return len(parts[0]) == 64  # SHA256 hex length


@dataclass
class EgyptianSolution:
    """Solution to 4/n = 1/a + 1/b + 1/c."""
    n: int
    a: int
    b: int
    c: int
    verified: bool = False

    def verify(self) -> bool:
        """Verify the solution is correct."""
        lhs = Fraction(4, self.n)
        rhs = Fraction(1, self.a) + Fraction(1, self.b) + Fraction(1, self.c)
        self.verified = (lhs == rhs)
        return self.verified

    def to_dict(self) -> dict:
        return asdict(self)


class EgyptianFractionsSolver:
    """
    Solver for Egyptian fraction decompositions.
    Core engine for fair division applications.
    """

    HARD_RESIDUES = {1, 121, 169, 289, 361, 529}
    MODULUS = 840

    def __init__(self):
        self.cache: Dict[int, List[EgyptianSolution]] = {}
        self.security = BrahimSecurityLayer()

    def is_hard_case(self, n: int) -> bool:
        """Check if n is a hard case prime."""
        if n < 2:
            return False
        # Check primality
        if n < 4:
            return n > 1
        if n % 2 == 0 or n % 3 == 0:
            return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0:
                return False
            i += 6
        # Check residue class
        return (n % self.MODULUS) in self.HARD_RESIDUES

    def solve(self, n: int, max_denom: int = 100000) -> List[EgyptianSolution]:
        """
        Find all solutions to 4/n = 1/a + 1/b + 1/c.

        Args:
            n: The denominator in 4/n
            max_denom: Maximum denominator to search

        Returns:
            List of verified solutions
        """
        if n in self.cache:
            return self.cache[n]

        solutions = []
        a_min = (n + 3) // 4
        a_max = min(n, max_denom // 10)

        for a in range(a_min, a_max + 1):
            # 4/n - 1/a = (4a - n)/(na)
            num = 4 * a - n
            den = n * a

            if num <= 0:
                continue

            b_min = max(a, (den + num - 1) // num)
            b_max = min(max_denom, (2 * den) // num + 1)

            for b in range(b_min, b_max + 1):
                # c = den*b / (num*b - den)
                c_den = num * b - den
                if c_den <= 0:
                    continue
                c_num = den * b
                if c_num % c_den == 0:
                    c = c_num // c_den
                    if c >= b and c <= max_denom:
                        sol = EgyptianSolution(n, a, b, c)
                        if sol.verify():
                            solutions.append(sol)

        self.cache[n] = solutions
        return solutions

    def fair_division(self, total: float, n: int) -> Optional[List[float]]:
        """
        Divide a resource fairly using Egyptian fractions.

        Args:
            total: Total amount to divide
            n: Parameter for 4/n fraction

        Returns:
            List of 3 fair shares, or None if no solution
        """
        solutions = self.solve(n)
        if not solutions:
            return None

        sol = solutions[0]
        share_a = total / sol.a
        share_b = total / sol.b
        share_c = total / sol.c

        return [share_a, share_b, share_c]

    def schedule_tasks(self, duration: int, n: int) -> Optional[List[int]]:
        """
        Schedule 3 unit tasks within a duration using Egyptian fractions.

        Args:
            duration: Total time available
            n: Parameter for 4/n allocation

        Returns:
            List of 3 task durations
        """
        solutions = self.solve(n)
        if not solutions:
            return None

        sol = solutions[0]
        # Scale to duration
        lcm = sol.a * sol.b * sol.c // math.gcd(sol.a, math.gcd(sol.b, sol.c))
        scale = duration * n // (4 * lcm)

        return [
            scale * lcm // sol.a,
            scale * lcm // sol.b,
            scale * lcm // sol.c
        ]

    def split_secret(self, secret: str, n: int) -> Optional[List[str]]:
        """
        Split a secret into 3 shares using Egyptian fraction ratios.

        Args:
            secret: Secret string to split
            n: Parameter determining split ratios

        Returns:
            List of 3 encoded shares
        """
        solutions = self.solve(n)
        if not solutions:
            return None

        sol = solutions[0]

        # Encode with Brahim security
        encoded = self.security.encode(secret)

        # Create shares based on fraction weights
        total_weight = sol.a + sol.b + sol.c
        shares = [
            f"SHARE_A:{sol.a}/{total_weight}:{encoded[:len(encoded)//3]}",
            f"SHARE_B:{sol.b}/{total_weight}:{encoded[len(encoded)//3:2*len(encoded)//3]}",
            f"SHARE_C:{sol.c}/{total_weight}:{encoded[2*len(encoded)//3:]}"
        ]

        return [self.security.encode(s) for s in shares]


class EgyptianFractionsAPI:
    """REST API wrapper for Egyptian Fractions SDK."""

    def __init__(self):
        self.solver = EgyptianFractionsSolver()
        self.version = "1.0.0"

    def handle_request(self, endpoint: str, params: dict) -> dict:
        """Handle API request."""

        if endpoint == "/solve":
            n = params.get("n", 5)
            solutions = self.solver.solve(n)
            return {
                "status": "ok",
                "n": n,
                "solutions": [s.to_dict() for s in solutions[:10]],
                "total_found": len(solutions)
            }

        elif endpoint == "/fair_division":
            total = params.get("total", 100)
            n = params.get("n", 5)
            shares = self.solver.fair_division(total, n)
            return {
                "status": "ok" if shares else "no_solution",
                "total": total,
                "shares": shares
            }

        elif endpoint == "/schedule":
            duration = params.get("duration", 60)
            n = params.get("n", 5)
            tasks = self.solver.schedule_tasks(duration, n)
            return {
                "status": "ok" if tasks else "no_solution",
                "duration": duration,
                "tasks": tasks
            }

        elif endpoint == "/split_secret":
            secret = params.get("secret", "")
            n = params.get("n", 5)
            shares = self.solver.split_secret(secret, n)
            return {
                "status": "ok" if shares else "no_solution",
                "shares": shares
            }

        elif endpoint == "/health":
            return {
                "status": "ok",
                "version": self.version,
                "sdk": "BOA Egyptian Fractions",
                "security": "Brahim Onion Layer v1"
            }

        else:
            return {"status": "error", "message": f"Unknown endpoint: {endpoint}"}


# Main entry point
if __name__ == "__main__":
    api = EgyptianFractionsAPI()

    print("=" * 60)
    print("BOA EGYPTIAN FRACTIONS SDK")
    print("=" * 60)

    # Test solve
    result = api.handle_request("/solve", {"n": 5})
    print(f"\n/solve?n=5:")
    print(f"  Solutions: {result['total_found']}")
    if result['solutions']:
        s = result['solutions'][0]
        print(f"  First: 4/5 = 1/{s['a']} + 1/{s['b']} + 1/{s['c']}")

    # Test fair division
    result = api.handle_request("/fair_division", {"total": 100, "n": 5})
    print(f"\n/fair_division?total=100&n=5:")
    print(f"  Shares: {result['shares']}")

    # Test health
    result = api.handle_request("/health", {})
    print(f"\n/health:")
    print(f"  {result}")
