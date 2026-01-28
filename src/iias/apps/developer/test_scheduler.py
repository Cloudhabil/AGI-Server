"""
Test Scheduler - Lucas-priority test ordering.

Assigns test priorities based on Lucas numbers for optimal execution order.
Lucas sequence: 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322
"""

import time
from dataclasses import dataclass, field
from typing import List, Callable, Optional, Any
from enum import Enum
import heapq

# Constants
LUCAS = [1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199, 322]


class TestStatus(Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestCase:
    """Represents a single test case."""
    name: str
    test_fn: Optional[Callable] = None
    lucas_tier: int = 0  # Index into LUCAS sequence
    status: TestStatus = TestStatus.PENDING
    duration: float = 0.0
    error: Optional[str] = None

    @property
    def weight(self) -> int:
        """Get Lucas weight for this test."""
        if 0 <= self.lucas_tier < len(LUCAS):
            return LUCAS[self.lucas_tier]
        return LUCAS[-1]  # Max weight for out-of-range

    def __lt__(self, other: "TestCase") -> bool:
        """Compare by weight for priority queue (lower weight = higher priority)."""
        return self.weight < other.weight


@dataclass
class TestSuite:
    """Collection of test cases."""
    name: str
    tests: List[TestCase] = field(default_factory=list)

    def add_test(self, test: TestCase) -> None:
        """Add a test to the suite."""
        self.tests.append(test)


@dataclass
class TestResults:
    """Results from a test run."""
    total: int
    passed: int
    failed: int
    skipped: int
    total_time: float
    execution_order: List[str]


class TestScheduler:
    """
    Lucas-priority test scheduler.

    Orders test execution by Lucas number weights:
    - Tier 0: weight 1 (highest priority - critical tests)
    - Tier 1: weight 3 (high priority - core tests)
    - Tier 2: weight 4 (medium-high priority)
    - ...
    - Tier 11: weight 322 (lowest priority - optional tests)

    Lower weight = earlier execution.
    """

    def __init__(self):
        """Initialize the test scheduler."""
        self.suites: List[TestSuite] = []
        self.results: Optional[TestResults] = None
        self._execution_order: List[str] = []

    @staticmethod
    def get_lucas_sequence() -> List[int]:
        """Return the Lucas sequence used for weighting."""
        return LUCAS.copy()

    @staticmethod
    def get_weight_for_tier(tier: int) -> int:
        """Get the Lucas weight for a given tier."""
        if 0 <= tier < len(LUCAS):
            return LUCAS[tier]
        return LUCAS[-1]

    def add_suite(self, suite: TestSuite) -> None:
        """Add a test suite to the scheduler."""
        self.suites.append(suite)

    def create_test(
        self,
        name: str,
        test_fn: Optional[Callable] = None,
        tier: int = 5
    ) -> TestCase:
        """
        Create a test case with Lucas-based priority.

        Args:
            name: Test name.
            test_fn: Test function to execute.
            tier: Lucas tier (0-11). Lower = higher priority.

        Returns:
            Configured TestCase.
        """
        return TestCase(name=name, test_fn=test_fn, lucas_tier=tier)

    def _collect_all_tests(self) -> List[TestCase]:
        """Collect all tests from all suites."""
        all_tests = []
        for suite in self.suites:
            all_tests.extend(suite.tests)
        return all_tests

    def get_execution_order(self) -> List[TestCase]:
        """
        Get tests in Lucas-weighted execution order.

        Returns:
            Tests sorted by Lucas weight (ascending).
        """
        all_tests = self._collect_all_tests()
        # Use heapq for efficient priority-based sorting
        return sorted(all_tests, key=lambda t: t.weight)

    def _run_test(self, test: TestCase) -> TestCase:
        """Execute a single test."""
        test.status = TestStatus.RUNNING
        start = time.time()

        try:
            if test.test_fn:
                test.test_fn()
            test.status = TestStatus.PASSED
        except AssertionError as e:
            test.status = TestStatus.FAILED
            test.error = str(e)
        except Exception as e:
            test.status = TestStatus.FAILED
            test.error = f"Unexpected error: {e}"

        test.duration = time.time() - start
        return test

    def run_all(self, stop_on_failure: bool = False) -> TestResults:
        """
        Run all tests in Lucas-priority order.

        Args:
            stop_on_failure: Stop execution on first failure.

        Returns:
            TestResults with execution summary.
        """
        ordered_tests = self.get_execution_order()
        start_time = time.time()

        passed = 0
        failed = 0
        skipped = 0
        self._execution_order = []

        for test in ordered_tests:
            if stop_on_failure and failed > 0:
                test.status = TestStatus.SKIPPED
                skipped += 1
                continue

            self._run_test(test)
            self._execution_order.append(test.name)

            if test.status == TestStatus.PASSED:
                passed += 1
            elif test.status == TestStatus.FAILED:
                failed += 1
            else:
                skipped += 1

        self.results = TestResults(
            total=len(ordered_tests),
            passed=passed,
            failed=failed,
            skipped=skipped,
            total_time=time.time() - start_time,
            execution_order=self._execution_order.copy()
        )

        return self.results

    def get_schedule_report(self) -> str:
        """Generate a report on test scheduling."""
        lines = [
            "=" * 50,
            "LUCAS-PRIORITY TEST SCHEDULE",
            "=" * 50,
            "Lucas Sequence: " + ", ".join(map(str, LUCAS)),
            "",
            "TIER WEIGHTS:",
        ]

        for i, weight in enumerate(LUCAS):
            lines.append(f"  Tier {i}: weight {weight}")

        lines.append("")
        lines.append("SCHEDULED TESTS (by priority):")

        ordered = self.get_execution_order()
        for i, test in enumerate(ordered, 1):
            status_icon = {
                TestStatus.PENDING: "[ ]",
                TestStatus.PASSED: "[+]",
                TestStatus.FAILED: "[X]",
                TestStatus.SKIPPED: "[-]",
                TestStatus.RUNNING: "[~]",
            }.get(test.status, "[?]")

            lines.append(
                f"  {i}. {status_icon} {test.name} "
                f"(tier={test.lucas_tier}, weight={test.weight})"
            )

        if self.results:
            lines.extend([
                "",
                "RESULTS:",
                f"  Total: {self.results.total}",
                f"  Passed: {self.results.passed}",
                f"  Failed: {self.results.failed}",
                f"  Skipped: {self.results.skipped}",
                f"  Time: {self.results.total_time:.4f}s",
            ])

        lines.append("=" * 50)
        return "\n".join(lines)


if __name__ == "__main__":
    print("Testing TestScheduler - Lucas-priority test ordering")
    print()

    # Display Lucas sequence
    print("Lucas Sequence for test weights:")
    for i, weight in enumerate(LUCAS):
        print(f"  Tier {i}: weight {weight}")
    print()

    # Create scheduler
    scheduler = TestScheduler()

    # Create test suite with various tiers
    suite = TestSuite("Core Tests")

    # Add tests with different Lucas tiers
    def passing_test():
        assert True

    def failing_test():
        assert False, "Intentional failure"

    # Critical tests (tier 0, weight 1)
    suite.add_test(scheduler.create_test("test_critical_init", passing_test, tier=0))

    # High priority (tier 1, weight 3)
    suite.add_test(scheduler.create_test("test_core_function", passing_test, tier=1))

    # Medium priority (tier 3, weight 7)
    suite.add_test(scheduler.create_test("test_validation", passing_test, tier=3))

    # Lower priority (tier 5, weight 18)
    suite.add_test(scheduler.create_test("test_edge_cases", passing_test, tier=5))

    # Low priority (tier 8, weight 76)
    suite.add_test(scheduler.create_test("test_integration", passing_test, tier=8))

    # Lowest priority (tier 11, weight 322)
    suite.add_test(scheduler.create_test("test_optional_feature", passing_test, tier=11))

    scheduler.add_suite(suite)

    # Show execution order before running
    print("Execution Order (before run):")
    for i, test in enumerate(scheduler.get_execution_order(), 1):
        print(f"  {i}. {test.name} (weight={test.weight})")
    print()

    # Run all tests
    results = scheduler.run_all()

    # Print full report
    print(scheduler.get_schedule_report())

    # Verify execution order follows Lucas weights
    weights = [t.weight for t in scheduler.get_execution_order()]
    assert weights == sorted(weights), "Tests should be ordered by weight!"

    print("\nTest PASSED: TestScheduler working correctly!")
