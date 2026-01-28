"""
Resource Allocator - 214-sum Project Budgeting

Allocates resources across projects ensuring the sum of all allocations
equals 214 when normalized. This constant represents the harmonic
balance point for resource distribution in IIAS systems.

Constants:
- SUM_CONSTANT = 214 (normalized allocation sum)
- PHI = 1.618033988749895 (Golden Ratio for proportional splits)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import math

# IIAS Constants
PHI = 1.618033988749895
SUM_CONSTANT = 214


class AllocationPriority(Enum):
    """Priority levels for resource allocation."""
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class Project:
    """Represents a project requiring resource allocation."""
    name: str
    requested_budget: float
    priority: AllocationPriority = AllocationPriority.MEDIUM
    min_allocation: float = 0.0
    max_allocation: Optional[float] = None


@dataclass
class Allocation:
    """Represents the final allocation for a project."""
    project_name: str
    requested: float
    allocated: float
    normalized: float
    percentage: float


class ResourceAllocator:
    """
    214-sum normalized resource allocator.

    Distributes budgets across projects ensuring total normalized
    allocation equals SUM_CONSTANT (214). Uses PHI-weighted
    priority scaling for fair distribution.
    """

    def __init__(self, total_budget: float):
        """
        Initialize the allocator with a total budget.

        Args:
            total_budget: The total available budget to allocate
        """
        self.total_budget = total_budget
        self.projects: List[Project] = []
        self._allocations: Dict[str, Allocation] = {}

    def add_project(self, project: Project) -> None:
        """Add a project to the allocation pool."""
        self.projects.append(project)

    def add_projects(self, projects: List[Project]) -> None:
        """Add multiple projects to the allocation pool."""
        self.projects.extend(projects)

    def _calculate_priority_weight(self, priority: AllocationPriority) -> float:
        """
        Calculate PHI-based weight for priority level.

        Higher priorities get exponentially more weight using PHI.
        """
        return PHI ** (priority.value - 1)

    def _normalize_to_214(self, allocations: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize allocations so their sum equals 214.

        Args:
            allocations: Raw allocation amounts

        Returns:
            Normalized allocations summing to 214
        """
        total = sum(allocations.values())
        if total == 0:
            return {k: 0.0 for k in allocations}

        scale_factor = SUM_CONSTANT / total
        return {k: v * scale_factor for k, v in allocations.items()}

    def allocate(self) -> List[Allocation]:
        """
        Perform resource allocation across all projects.

        Returns:
            List of Allocation objects with final distributions
        """
        if not self.projects:
            return []

        # Calculate weighted requests
        weighted_requests: Dict[str, float] = {}
        for project in self.projects:
            weight = self._calculate_priority_weight(project.priority)
            weighted_requests[project.name] = project.requested_budget * weight

        # Calculate total weighted request
        total_weighted = sum(weighted_requests.values())

        # Allocate proportionally within budget
        raw_allocations: Dict[str, float] = {}
        for project in self.projects:
            if total_weighted > 0:
                proportion = weighted_requests[project.name] / total_weighted
                allocated = self.total_budget * proportion
            else:
                allocated = 0.0

            # Apply min/max constraints
            allocated = max(allocated, project.min_allocation)
            if project.max_allocation is not None:
                allocated = min(allocated, project.max_allocation)

            raw_allocations[project.name] = allocated

        # Normalize to 214
        normalized = self._normalize_to_214(raw_allocations)

        # Build allocation results
        allocations = []
        for project in self.projects:
            alloc = Allocation(
                project_name=project.name,
                requested=project.requested_budget,
                allocated=raw_allocations[project.name],
                normalized=normalized[project.name],
                percentage=(raw_allocations[project.name] / self.total_budget * 100)
                           if self.total_budget > 0 else 0.0
            )
            allocations.append(alloc)
            self._allocations[project.name] = alloc

        return allocations

    def get_allocation(self, project_name: str) -> Optional[Allocation]:
        """Get allocation for a specific project."""
        return self._allocations.get(project_name)

    def get_summary(self) -> Dict:
        """
        Get allocation summary statistics.

        Returns:
            Dictionary with summary metrics
        """
        if not self._allocations:
            self.allocate()

        allocations = list(self._allocations.values())
        total_allocated = sum(a.allocated for a in allocations)
        total_normalized = sum(a.normalized for a in allocations)

        return {
            "total_budget": self.total_budget,
            "total_allocated": total_allocated,
            "total_normalized": total_normalized,
            "sum_constant_check": abs(total_normalized - SUM_CONSTANT) < 0.001,
            "project_count": len(allocations),
            "utilization_rate": total_allocated / self.total_budget if self.total_budget > 0 else 0.0
        }

    def rebalance_with_phi(self) -> List[Allocation]:
        """
        Rebalance allocations using PHI-ratio splits.

        Creates a golden-ratio based distribution where each
        allocation relates to the next by factor PHI.
        """
        if not self.projects:
            return []

        n = len(self.projects)
        # Sort by priority (highest first)
        sorted_projects = sorted(self.projects,
                                 key=lambda p: p.priority.value,
                                 reverse=True)

        # Calculate PHI-weighted distribution
        # Sum of PHI^0 + PHI^1 + ... + PHI^(n-1)
        phi_sum = sum(PHI ** i for i in range(n))

        raw_allocations: Dict[str, float] = {}
        for i, project in enumerate(sorted_projects):
            # Higher priority gets larger PHI power
            phi_weight = PHI ** (n - 1 - i)
            raw_allocations[project.name] = (phi_weight / phi_sum) * self.total_budget

        # Normalize to 214
        normalized = self._normalize_to_214(raw_allocations)

        # Build results
        allocations = []
        for project in self.projects:
            alloc = Allocation(
                project_name=project.name,
                requested=project.requested_budget,
                allocated=raw_allocations[project.name],
                normalized=normalized[project.name],
                percentage=(raw_allocations[project.name] / self.total_budget * 100)
                           if self.total_budget > 0 else 0.0
            )
            allocations.append(alloc)
            self._allocations[project.name] = alloc

        return allocations


if __name__ == "__main__":
    print("=" * 60)
    print("IIAS Resource Allocator - 214-sum Project Budgeting")
    print("=" * 60)
    print(f"\nConstants: SUM_CONSTANT={SUM_CONSTANT}, PHI={PHI:.6f}")

    # Create allocator with $1,000,000 budget
    allocator = ResourceAllocator(total_budget=1_000_000)

    # Add test projects
    projects = [
        Project("Infrastructure", 300_000, AllocationPriority.CRITICAL),
        Project("Development", 250_000, AllocationPriority.HIGH),
        Project("Marketing", 200_000, AllocationPriority.MEDIUM),
        Project("Research", 150_000, AllocationPriority.MEDIUM),
        Project("Training", 100_000, AllocationPriority.LOW),
    ]
    allocator.add_projects(projects)

    # Perform allocation
    print("\n--- Standard Allocation ---")
    allocations = allocator.allocate()

    total_normalized = 0
    for alloc in allocations:
        print(f"  {alloc.project_name:15} | "
              f"Requested: ${alloc.requested:>10,.0f} | "
              f"Allocated: ${alloc.allocated:>10,.2f} | "
              f"Normalized: {alloc.normalized:>7.3f} | "
              f"{alloc.percentage:>5.1f}%")
        total_normalized += alloc.normalized

    print(f"\n  Total Normalized: {total_normalized:.3f} (Target: {SUM_CONSTANT})")

    # Summary
    summary = allocator.get_summary()
    print(f"\n--- Summary ---")
    print(f"  Total Budget:     ${summary['total_budget']:,.0f}")
    print(f"  Total Allocated:  ${summary['total_allocated']:,.2f}")
    print(f"  214-sum Check:    {'PASS' if summary['sum_constant_check'] else 'FAIL'}")
    print(f"  Utilization:      {summary['utilization_rate']*100:.1f}%")

    # PHI-rebalanced allocation
    print("\n--- PHI-Rebalanced Allocation ---")
    allocations = allocator.rebalance_with_phi()

    total_normalized = 0
    for alloc in allocations:
        print(f"  {alloc.project_name:15} | "
              f"Allocated: ${alloc.allocated:>10,.2f} | "
              f"Normalized: {alloc.normalized:>7.3f} | "
              f"{alloc.percentage:>5.1f}%")
        total_normalized += alloc.normalized

    print(f"\n  Total Normalized: {total_normalized:.3f} (Target: {SUM_CONSTANT})")

    # Verify 214-sum
    print("\n--- 214-Sum Verification ---")
    print(f"  Sum of normalized allocations: {total_normalized:.6f}")
    print(f"  Target constant:               {SUM_CONSTANT}")
    print(f"  Difference:                    {abs(total_normalized - SUM_CONSTANT):.10f}")
    print(f"  Status: {'VERIFIED' if abs(total_normalized - SUM_CONSTANT) < 0.001 else 'FAILED'}")
