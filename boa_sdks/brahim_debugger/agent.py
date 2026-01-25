"""
BRAHIM DEBUGGER AGENT - AI-Powered Code Analysis & Repair

The agent operates on the principle:
"Every line of code has a resonance with the universal sequence."

Workflow:
1. ANALYZE: Detect issues using pattern matching + AST analysis
2. ASSESS: Calculate resonance and safety verdict
3. PRIORITIZE: Order fixes by Brahim weighting
4. FIX: Apply automatic repairs (optional)
5. VERIFY: Confirm improvement in code resonance

The agent aims to bring code resonance to Genesis (0.0219),
representing perfect axiological alignment.

@author: Elias Oulad Brahim
"""

import json
import time
import sys
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict

# Handle imports whether run as module or directly
try:
    from .engine import BrahimEngine, SafetyVerdict, DebugResult
    from .analyzer import CodeAnalyzer, AnalysisResult, CodeIssue
    from .fixer import CodeFixer, FixResult
except ImportError:
    from engine import BrahimEngine, SafetyVerdict, DebugResult
    from analyzer import CodeAnalyzer, AnalysisResult, CodeIssue
    from fixer import CodeFixer, FixResult


@dataclass
class AgentResponse:
    """Standard response from the agent"""
    success: bool
    verdict: str
    message: str
    data: Dict[str, Any]
    resonance: float
    alignment: float
    execution_time: float


class BrahimDebuggerAgent:
    """
    Brahim-Aligned Debugger Agent

    An AI agent that analyzes and fixes code using mathematical
    principles derived from the Brahim sequence.

    Example:
        agent = BrahimDebuggerAgent()
        result = agent.debug(code)
        if result.verdict == "UNSAFE":
            fixed = agent.fix(code)
    """

    VERSION = "1.0.0"
    NAME = "BrahimDebugger"

    def __init__(
        self,
        language: str = "python",
        auto_fix: bool = False,
        verbose: bool = True
    ):
        """
        Initialize the Brahim Debugger Agent.

        Args:
            language: Target language ("python" or "kotlin")
            auto_fix: Automatically apply safe fixes
            verbose: Print detailed output
        """
        self.language = language.lower()
        self.auto_fix = auto_fix
        self.verbose = verbose

        self.analyzer = CodeAnalyzer(language=language)
        self.fixer = CodeFixer(language=language)

        self._session_start = time.time()
        self._analysis_count = 0
        self._fixes_applied = 0

    def debug(self, code: str, file_path: str = "<input>") -> AgentResponse:
        """
        Analyze code and return debugging results.

        This is the main entry point for code analysis.

        Args:
            code: Source code to analyze
            file_path: Optional file path for context

        Returns:
            AgentResponse with analysis results
        """
        start_time = time.time()
        self._analysis_count += 1

        if self.verbose:
            self._print_header(f"Analyzing {file_path}")

        # Perform analysis
        analysis = self.analyzer.analyze(code, file_path)

        # Build response
        response = self._build_response(analysis, time.time() - start_time)

        if self.verbose:
            self._print_analysis(analysis, response)

        # Auto-fix if enabled
        if self.auto_fix and analysis.verdict in [SafetyVerdict.CAUTION, SafetyVerdict.UNSAFE]:
            self._print_info("Auto-fix enabled, applying safe fixes...")
            fix_result = self.fix(code, analysis)
            response.data['auto_fix'] = {
                'applied': len(fix_result.fixes_applied),
                'skipped': len(fix_result.fixes_skipped),
                'improvement': fix_result.improvement_score
            }

        return response

    def debug_file(self, file_path: str) -> AgentResponse:
        """Analyze a file from disk"""
        path = Path(file_path)

        if not path.exists():
            return AgentResponse(
                success=False,
                verdict="BLOCKED",
                message=f"File not found: {file_path}",
                data={'error': 'FILE_NOT_FOUND'},
                resonance=1.0,
                alignment=1.0,
                execution_time=0.0
            )

        code = path.read_text(encoding='utf-8')
        return self.debug(code, file_path)

    def fix(
        self,
        code: str,
        analysis: Optional[AnalysisResult] = None,
        safe_only: bool = True
    ) -> FixResult:
        """
        Apply fixes to code.

        Args:
            code: Source code to fix
            analysis: Pre-computed analysis (optional)
            safe_only: Only apply high-confidence fixes

        Returns:
            FixResult with fixed code
        """
        if analysis is None:
            analysis = self.analyzer.analyze(code)

        fix_result = self.fixer.fix(code, analysis, safe_only)
        self._fixes_applied += len(fix_result.fixes_applied)

        if self.verbose:
            self._print_fixes(fix_result)

        return fix_result

    def suggest(self, code: str) -> List[Dict]:
        """
        Get fix suggestions without applying them.

        Returns list of suggested fixes with priorities.
        """
        analysis = self.analyzer.analyze(code)
        return self.fixer.suggest_fixes(analysis)

    def estimate_effort(self, code: str) -> Dict[str, float]:
        """
        Estimate time to fix all issues.

        Uses Brahim metrics for estimation.
        """
        analysis = self.analyzer.analyze(code)
        return self.fixer.estimate_fix_time(analysis)

    def verify(self, original: str, fixed: str) -> Dict[str, Any]:
        """
        Verify that fixes improved the code.

        Compares resonance before and after fixes.
        """
        original_analysis = self.analyzer.analyze(original, "<original>")
        fixed_analysis = self.analyzer.analyze(fixed, "<fixed>")

        original_resonance = original_analysis.resonance
        fixed_resonance = fixed_analysis.resonance

        improvement = (original_resonance - fixed_resonance) / max(0.001, original_resonance) * 100

        return {
            'original_issues': len(original_analysis.issues),
            'fixed_issues': len(fixed_analysis.issues),
            'issues_resolved': len(original_analysis.issues) - len(fixed_analysis.issues),
            'original_resonance': original_resonance,
            'fixed_resonance': fixed_resonance,
            'resonance_improvement': improvement,
            'original_verdict': original_analysis.verdict.value,
            'fixed_verdict': fixed_analysis.verdict.value,
            'success': fixed_resonance < original_resonance,
            'genesis_alignment': BrahimEngine.axiological_alignment(fixed_resonance)
        }

    def get_metrics(self, code: str) -> Dict[str, float]:
        """Get code metrics without full analysis"""
        analysis = self.analyzer.analyze(code)
        return analysis.metrics

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics for the current session"""
        return {
            'session_duration': time.time() - self._session_start,
            'analyses_performed': self._analysis_count,
            'fixes_applied': self._fixes_applied,
            'agent_version': self.VERSION,
            'language': self.language,
            'brahim_constants': {
                'phi': BrahimEngine.PHI,
                'beta': BrahimEngine.BETA,
                'genesis': BrahimEngine.GENESIS,
                'sequence': list(BrahimEngine.SEQUENCE)
            }
        }

    def explain(self, issue_category: str) -> str:
        """
        Explain an issue category using Brahim principles.

        Args:
            issue_category: Category name (e.g., "SECURITY", "LOGIC")

        Returns:
            Explanation string
        """
        explanations = {
            'SYNTAX': f"""
SYNTAX Issues (B(1) = {BrahimEngine.B(1)})
-----------------------------------------
The most fundamental errors. Like B(1)=27, they are the foundation.
Fix these first as they block all other analysis.
Mirror effort: M(27) = {BrahimEngine.mirror(27)} (relatively easy to fix)
""",
            'TYPE': f"""
TYPE Issues (B(2) = {BrahimEngine.B(2)})
-----------------------------------------
Type mismatches and incorrect comparisons.
B(2)=42 - "The answer" to getting types right.
Mirror effort: M(42) = {BrahimEngine.mirror(42)}
""",
            'LOGIC': f"""
LOGIC Issues (B(3) = {BrahimEngine.B(3)})
-----------------------------------------
Flaws in program logic and control flow.
B(3)=60 represents the review cycle time.
Mirror effort: M(60) = {BrahimEngine.mirror(60)}
""",
            'PERFORMANCE': f"""
PERFORMANCE Issues (B(4) = {BrahimEngine.B(4)})
-----------------------------------------
Inefficiencies and optimization opportunities.
B(4)=75 is the target code coverage - aim high.
Mirror effort: M(75) = {BrahimEngine.mirror(75)}
Note: D4 = {BrahimEngine.delta(4, 7)} (symmetry breaking)
""",
            'SECURITY': f"""
SECURITY Issues (B(5) = {BrahimEngine.B(5)})
-----------------------------------------
CRITICAL: Vulnerabilities and unsafe patterns.
B(5)=97 - near-complete validation required.
Mirror effort: M(97) = {BrahimEngine.mirror(97)} (harder to fix properly)
Note: D5 = {BrahimEngine.delta(5, 6)} (symmetry breaking - edge cases!)
""",
            'ARCHITECTURE': f"""
ARCHITECTURE Issues (B(6) = {BrahimEngine.B(6)})
-----------------------------------------
Structural and design problems.
B(6)=121=11^2 - prime power, fundamental structure.
Mirror effort: M(121) = {BrahimEngine.mirror(121)}
""",
            'MEMORY': f"""
MEMORY Issues (B(7) = {BrahimEngine.B(7)})
-----------------------------------------
Memory leaks, unsafe allocations.
B(7)=136 ~ 1/alpha (fine structure constant)
Mirror effort: M(136) = {BrahimEngine.mirror(136)}
""",
            'CONCURRENCY': f"""
CONCURRENCY Issues (B(8) = {BrahimEngine.B(8)})
-----------------------------------------
Race conditions, deadlocks, threading issues.
B(8)=154 = Mirror of B(3)=60 (balance)
Mirror effort: M(154) = {BrahimEngine.mirror(154)}
""",
            'INTEGRATION': f"""
INTEGRATION Issues (B(9) = {BrahimEngine.B(9)})
-----------------------------------------
API mismatches, protocol errors.
B(9)=172 = Mirror of B(2)=42
Mirror effort: M(172) = {BrahimEngine.mirror(172)}
""",
            'SYSTEM': f"""
SYSTEM Issues (B(10) = {BrahimEngine.B(10)})
-----------------------------------------
System-level failures, environment issues.
B(10)=187 - Maximum complexity score.
Mirror effort: M(187) = {BrahimEngine.mirror(187)} (simplest to identify)
Note: B(10) = 7*B(1) - 2 (Alpha-Omega identity)
"""
        }

        return explanations.get(
            issue_category.upper(),
            f"Unknown category: {issue_category}"
        )

    # ==================================================================
    # PRIVATE METHODS
    # ==================================================================

    def _build_response(self, analysis: AnalysisResult, exec_time: float) -> AgentResponse:
        """Build agent response from analysis"""
        return AgentResponse(
            success=analysis.verdict in [SafetyVerdict.SAFE, SafetyVerdict.NOMINAL],
            verdict=analysis.verdict.value.upper(),
            message=self._verdict_message(analysis.verdict, len(analysis.issues)),
            data={
                'file': analysis.file_path,
                'issues_count': len(analysis.issues),
                'issues': [
                    {
                        'category': i.category.name,
                        'severity': i.severity,
                        'line': i.line,
                        'message': i.message,
                        'suggestion': i.suggestion
                    }
                    for i in analysis.issues[:10]  # Top 10 issues
                ],
                'metrics': analysis.metrics,
                'suggestions': analysis.suggestions
            },
            resonance=analysis.resonance,
            alignment=BrahimEngine.axiological_alignment(analysis.resonance),
            execution_time=exec_time
        )

    def _verdict_message(self, verdict: SafetyVerdict, issue_count: int) -> str:
        """Generate human-readable verdict message"""
        messages = {
            SafetyVerdict.SAFE: f"Code is clean. No issues detected.",
            SafetyVerdict.NOMINAL: f"Code is acceptable. {issue_count} minor issue(s).",
            SafetyVerdict.CAUTION: f"Potential problems. {issue_count} issue(s) need attention.",
            SafetyVerdict.UNSAFE: f"Significant issues. {issue_count} problem(s) require fixing.",
            SafetyVerdict.BLOCKED: f"Critical errors. {issue_count} blocking issue(s)."
        }
        return messages.get(verdict, f"{issue_count} issue(s) found.")

    def _print_header(self, title: str):
        """Print formatted header"""
        print(f"\n{'=' * 60}")
        print(f"  BRAHIM DEBUGGER v{self.VERSION}")
        print(f"  {title}")
        print(f"{'=' * 60}\n")

    def _print_analysis(self, analysis: AnalysisResult, response: AgentResponse):
        """Print analysis results"""
        # Verdict banner
        verdict_colors = {
            'SAFE': '[OK]',
            'NOMINAL': '[--]',
            'CAUTION': '[!!]',
            'UNSAFE': '[**]',
            'BLOCKED': '[XX]'
        }
        icon = verdict_colors.get(response.verdict, '[??]')
        print(f"{icon} Verdict: {response.verdict}")
        print(f"   {response.message}\n")

        # Resonance
        print(f"[R] Resonance Analysis:")
        print(f"   Code Resonance: {response.resonance:.6f}")
        print(f"   Genesis Target: {BrahimEngine.GENESIS}")
        print(f"   Alignment Gap:  {response.alignment:.6f}")
        print()

        # Issues summary
        if analysis.issues:
            print(f"[!] Issues Found: {len(analysis.issues)}")
            print(f"{'-' * 40}")
            for i, issue in enumerate(analysis.issues[:5], 1):
                print(f"   {i}. [{issue.category.name}] Line {issue.line}: {issue.message}")
            if len(analysis.issues) > 5:
                print(f"   ... and {len(analysis.issues) - 5} more")
            print()

        # Suggestions
        if analysis.suggestions:
            print(f"[*] Suggestions:")
            for suggestion in analysis.suggestions[:3]:
                print(f"   - {suggestion}")
            print()

        # Execution time
        print(f"[T] Analysis completed in {response.execution_time:.3f}s")

    def _print_fixes(self, fix_result: FixResult):
        """Print fix results"""
        print(f"\n[F] Fixes Applied: {len(fix_result.fixes_applied)}")
        for fix in fix_result.fixes_applied[:5]:
            print(f"   Line {fix.line}: {fix.explanation}")

        if fix_result.fixes_skipped:
            print(f"\n[>] Fixes Skipped: {len(fix_result.fixes_skipped)}")
            print(f"   (Low confidence or requires manual review)")

        print(f"\n[+] Improvement Score: {fix_result.improvement_score:.1f}%")

    def _print_info(self, message: str):
        """Print info message"""
        print(f"[i] {message}")


# ==================================================================
# CLI INTERFACE
# ==================================================================

def main():
    """Command-line interface for the Brahim Debugger"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Brahim-Aligned Code Debugger Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m brahim_debugger code.py           # Analyze a file
  python -m brahim_debugger code.py --fix     # Analyze and fix
  python -m brahim_debugger --explain SECURITY # Explain category

Brahim Sequence: B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187}
Genesis Constant: 0.0219
        """
    )

    parser.add_argument('file', nargs='?', help='File to analyze')
    parser.add_argument('--fix', action='store_true', help='Apply automatic fixes')
    parser.add_argument('--language', '-l', default='python', help='Language (python/kotlin)')
    parser.add_argument('--explain', '-e', help='Explain issue category')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')
    parser.add_argument('--json', action='store_true', help='Output as JSON')

    args = parser.parse_args()

    agent = BrahimDebuggerAgent(
        language=args.language,
        auto_fix=args.fix,
        verbose=not args.quiet
    )

    if args.explain:
        print(agent.explain(args.explain))
        return

    if not args.file:
        parser.print_help()
        return

    result = agent.debug_file(args.file)

    if args.json:
        print(json.dumps(asdict(result), indent=2, default=str))
    elif args.fix and result.data.get('auto_fix'):
        print(f"\n✅ Auto-fix completed: {result.data['auto_fix']['applied']} fixes applied")


if __name__ == '__main__':
    main()
