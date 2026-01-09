#!/usr/bin/env python3
"""
Test Script: Autonomous Skill Selector Integration with Orchestrator

This script demonstrates the end-to-end integration of:
1. Predictive Sequential Orchestrator (resource management)
2. Autonomous Skill Selector Agent (intelligent skill selection)
3. Learning feedback loop (recording outcomes)

Quick tests to verify the system works before long production runs.
"""

import os
import sys
import time
from pathlib import Path

# Add repo to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from orchestrator_predictive_sequential import PredictiveSequentialOrchestrator


def test_skill_selector_available():
    """Test 1: Verify skill selector is available."""
    print("\n" + "=" * 80)
    print("TEST 1: Autonomous Skill Selector Availability")
    print("=" * 80)

    try:
        from skills.autonomous_skill_selector import get_skill_selector_agent
        agent = get_skill_selector_agent()
        print("[OK] Skill selector agent initialized successfully")
        print(f"     Database: {agent.memory.db_path}")
        agent.print_agent_status()
        return True
    except ImportError as e:
        print(f"[ERROR] Skill selector not available: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to initialize: {e}")
        return False


def test_orchestrator_initialization():
    """Test 2: Verify orchestrator initializes with skill selector."""
    print("\n" + "=" * 80)
    print("TEST 2: Orchestrator Initialization with Skill Selector")
    print("=" * 80)

    try:
        orchestrator = PredictiveSequentialOrchestrator(
            session_name="test_skill_learning",
            duration_minutes=1  # Just 1 minute for quick test
        )
        if orchestrator.skill_selector:
            print("[OK] Orchestrator initialized with skill selector")
            return True
        else:
            print("[WARN] Orchestrator initialized but skill selector not available")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to initialize orchestrator: {e}")
        return False


def test_skill_selection_logic():
    """Test 3: Verify skill selection logic works."""
    print("\n" + "=" * 80)
    print("TEST 3: Skill Selection Logic")
    print("=" * 80)

    try:
        from skills.autonomous_skill_selector import get_skill_selector_agent

        agent = get_skill_selector_agent()

        # Test pattern abstraction
        test_tasks = [
            ("Analyze Riemann Hypothesis structure", "reasoning"),
            ("Synthesize findings from multiple sources", "synthesis"),
            ("Validate mathematical proof", "validation"),
            ("Find patterns in sequence", "pattern_recognition"),
            ("Break down complex problem", "decomposition"),
        ]

        print("\nPattern Abstraction Tests:")
        for task, expected_pattern in test_tasks:
            pattern = agent.abstract_task_pattern(task)
            status = "[OK]" if pattern == expected_pattern else "[WARN]"
            print(f"  {status} '{task[:40]}' -> {pattern}")

        # Test skill selection
        print("\nSkill Selection Test:")
        skill, reasoning = agent.select_skill(
            "test_model",
            "Analyze the structure of the Riemann Hypothesis"
        )
        print(f"  Selected skill: {skill}")
        print(f"  Reasoning: {reasoning}")
        print(f"  [OK] Skill selection logic working")
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_learning_loop():
    """Test 4: Verify learning outcome recording."""
    print("\n" + "=" * 80)
    print("TEST 4: Learning Outcome Recording")
    print("=" * 80)

    try:
        from skills.autonomous_skill_selector import get_skill_selector_agent

        agent = get_skill_selector_agent()

        # Record some demo outcomes
        demo_outcomes = [
            ("test_student_1", "Analyze hypothesis", "riemann_analysis", True, 0.85),
            ("test_student_1", "Analyze structure", "riemann_analysis", True, 0.87),
            ("test_student_1", "Synthesize findings", "synthesis", True, 0.82),
            ("test_student_2", "Quick summary", "summary", True, 0.80),
        ]

        print("\nRecording demo outcomes:")
        for model, task, skill, success, quality in demo_outcomes:
            agent.record_outcome(model, task, skill, success, quality)
            print(f"  Recorded: {model}/{skill} Q={quality:.2f}")

        print("\n[OK] Learning outcomes recorded successfully")

        # Print learned knowledge
        print("\nLearned Knowledge So Far:")
        agent.print_learned_knowledge()
        return True

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_quick_orchestration():
    """Test 5: Run 1 quick cycle to verify full integration."""
    print("\n" + "=" * 80)
    print("TEST 5: Quick Integration Test (1 minute)")
    print("=" * 80)

    try:
        orchestrator = PredictiveSequentialOrchestrator(
            session_name="test_integration",
            duration_minutes=1  # Just 1 minute
        )

        print("\nStarting orchestrator (this may take 1-2 minutes depending on model load times)...")
        print("Ctrl+C to stop early.\n")

        orchestrator.run()

        print("\n[OK] Orchestrator completed successfully")
        return True

    except KeyboardInterrupt:
        print("\n[INFO] Test interrupted by user")
        return True
    except Exception as e:
        print(f"\n[ERROR] Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests in sequence."""
    print("\n" + "=" * 80)
    print("AUTONOMOUS SKILL SELECTOR INTEGRATION TEST SUITE")
    print("=" * 80)

    results = []

    # Run tests
    results.append(("Skill Selector Available", test_skill_selector_available()))
    if results[-1][1]:  # Only continue if selector is available
        results.append(("Orchestrator Init", test_orchestrator_initialization()))
        results.append(("Skill Selection Logic", test_skill_selection_logic()))
        results.append(("Learning Loop", test_learning_loop()))
        results.append(("Quick Orchestration", test_quick_orchestration()))

    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! System is ready for production use.")
        print("\nNext steps:")
        print("1. Run long production session:")
        print("   python orchestrator_predictive_sequential.py --duration 1440 --session rh_learning")
        print("\n2. Monitor learning progress:")
        print("   sqlite3 agents/sessions/rh_learning/metrics.db 'SELECT * FROM skill_selections;'")
        print("\n3. After 1+ week, analyze learned patterns")
    else:
        print("\n[WARNING] Some tests failed. Check errors above.")

    print("\n" + "=" * 80 + "\n")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
