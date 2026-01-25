#!/usr/bin/env python3
"""
Test script for the Brahim Debugger Agent

Demonstrates analysis and fixing capabilities.

Run from boa_sdks directory: python -m brahim_debugger.test_agent
Or from brahim_debugger directory: python test_agent.py
"""

import sys
from pathlib import Path

# Handle imports whether run as module or directly
try:
    from .agent import BrahimDebuggerAgent
    from .engine import BrahimEngine
except ImportError:
    # Add parent to path for direct execution
    sys.path.insert(0, str(Path(__file__).parent))
    from agent import BrahimDebuggerAgent
    from engine import BrahimEngine


def test_basic_analysis():
    """Test basic code analysis"""
    print("=" * 60)
    print("TEST 1: Basic Analysis")
    print("=" * 60)

    agent = BrahimDebuggerAgent(verbose=True)

    code = '''
def process_data(data):
    if data == None:
        return None

    result = []
    for i in range(len(data)):
        result.append(data[i] * 2)

    return result
'''

    result = agent.debug(code, "test_basic.py")
    print(f"\nTest 1 Result: {result.verdict}")
    assert result.data['issues_count'] > 0, "Should find issues"


def test_security_detection():
    """Test security issue detection"""
    print("\n" + "=" * 60)
    print("TEST 2: Security Detection")
    print("=" * 60)

    agent = BrahimDebuggerAgent(verbose=True)

    code = '''
import pickle

def dangerous_function(user_input):
    # Security issues galore!
    data = eval(user_input)
    obj = pickle.loads(user_input.encode())
    exec(f"print({user_input})")
    return data
'''

    result = agent.debug(code, "test_security.py")
    print(f"\nTest 2 Result: {result.verdict}")

    security_issues = [
        i for i in result.data['issues']
        if i['category'] == 'SECURITY'
    ]
    print(f"Security issues found: {len(security_issues)}")
    assert len(security_issues) >= 2, "Should find multiple security issues"


def test_auto_fix():
    """Test automatic fixing"""
    print("\n" + "=" * 60)
    print("TEST 3: Auto-Fix")
    print("=" * 60)

    agent = BrahimDebuggerAgent(verbose=True)

    code = '''
def check_value(x):
    if x == None:
        return False
    if x != None:
        return True
'''

    # First, analyze
    result = agent.debug(code, "test_fix.py")

    # Then fix
    fix_result = agent.fix(code)

    print(f"\nFixes applied: {len(fix_result.fixes_applied)}")
    print(f"Improvement: {fix_result.improvement_score:.1f}%")

    if fix_result.fixes_applied:
        print("\nFixed code:")
        print("-" * 40)
        print(fix_result.fixed_code)


def test_suggestions():
    """Test fix suggestions"""
    print("\n" + "=" * 60)
    print("TEST 4: Suggestions")
    print("=" * 60)

    agent = BrahimDebuggerAgent(verbose=False)

    code = '''
def inefficient(items):
    result = ""
    for i in range(len(items)):
        result += str(items[i])
    return result
'''

    suggestions = agent.suggest(code)

    print(f"Suggestions generated: {len(suggestions)}")
    for i, s in enumerate(suggestions[:3], 1):
        print(f"\n{i}. {s['issue']}")
        print(f"   Category: {s['category']}")
        print(f"   Bug Weight: B({s['severity']}) = {s['bug_weight']}")
        print(f"   Fix Effort: M({s['bug_weight']}) = {s['fix_effort']}")
        print(f"   Suggestion: {s['suggestion']}")


def test_verification():
    """Test fix verification"""
    print("\n" + "=" * 60)
    print("TEST 5: Verification")
    print("=" * 60)

    agent = BrahimDebuggerAgent(verbose=False)

    original = '''
def check(x):
    if x == None:
        return eval(x)
'''

    fixed = '''
def check(x):
    if x is None:
        return None
'''

    verification = agent.verify(original, fixed)

    print(f"Original issues: {verification['original_issues']}")
    print(f"Fixed issues: {verification['fixed_issues']}")
    print(f"Issues resolved: {verification['issues_resolved']}")
    print(f"Resonance improvement: {verification['resonance_improvement']:.1f}%")
    print(f"Verification: {'PASS' if verification['success'] else 'FAIL'}")


def test_category_explanation():
    """Test category explanations"""
    print("\n" + "=" * 60)
    print("TEST 6: Category Explanation")
    print("=" * 60)

    agent = BrahimDebuggerAgent(verbose=False)

    print(agent.explain("SECURITY"))


def test_brahim_engine():
    """Test the Brahim Engine directly"""
    print("\n" + "=" * 60)
    print("TEST 7: Brahim Engine Verification")
    print("=" * 60)

    # Test sequence
    print(f"Sequence: {list(BrahimEngine.SEQUENCE)}")
    print(f"Sum: {sum(BrahimEngine.SEQUENCE)} (expected: 1070)")

    # Test mirror pairs
    print("\nMirror Pairs (B(i) + B(11-i) = 214):")
    for i in range(1, 6):
        j = 11 - i
        bi = BrahimEngine.B(i)
        bj = BrahimEngine.B(j)
        print(f"  B({i}) + B({j}) = {bi} + {bj} = {bi + bj}")

    # Test golden ratio identities
    print(f"\nGolden Ratio Identities:")
    print(f"  phi = {BrahimEngine.PHI:.10f}")
    print(f"  beta = {BrahimEngine.BETA:.10f}")
    print(f"  beta = sqrt(5) - 2 = {(5**0.5) - 2:.10f}")
    print(f"  beta^2 + 4*beta - 1 = {BrahimEngine.BETA**2 + 4*BrahimEngine.BETA - 1:.2e}")

    # Test resonance
    errors = [0.1, 0.2, 0.3]
    resonance = BrahimEngine.resonance(errors)
    print(f"\nResonance test: R({errors}) = {resonance:.6f}")
    print(f"Genesis target: {BrahimEngine.GENESIS}")
    print(f"Alignment: {BrahimEngine.axiological_alignment(resonance):.6f}")


def test_kotlin_analysis():
    """Test Kotlin code analysis"""
    print("\n" + "=" * 60)
    print("TEST 8: Kotlin Analysis")
    print("=" * 60)

    agent = BrahimDebuggerAgent(language="kotlin", verbose=True)

    code = '''
fun processData(input: String?): String {
    val result = input!!.trim()  // Force unwrap - NPE risk

    try {
        return result.uppercase()
    } catch (e: Exception) {  // Catching generic exception
        return ""
    }
}
'''

    result = agent.debug(code, "test.kt")
    print(f"\nKotlin Test Result: {result.verdict}")


def main():
    """Run all tests"""
    print("\n" + "+" + "=" * 58 + "+")
    print("|" + " BRAHIM DEBUGGER AGENT - TEST SUITE ".center(58) + "|")
    print("+" + "=" * 58 + "+")

    test_basic_analysis()
    test_security_detection()
    test_auto_fix()
    test_suggestions()
    test_verification()
    test_category_explanation()
    test_brahim_engine()
    test_kotlin_analysis()

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
