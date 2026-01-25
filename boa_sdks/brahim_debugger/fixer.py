"""
CODE FIXER - Brahim-Aligned Automatic Code Repair

Applies the mirror principle for fixes:
- Every bug B(i) has a fix with effort M(B(i)) = 214 - B(i)
- Symmetry breaking (Δ₄=-3, Δ₅=+4) represents edge cases

Fix Priority Order:
1. Syntax (B(1)=27) → Quick fixes
2. Security (B(5)=97) → Critical fixes
3. Logic (B(3)=60) → Important fixes
4. Performance (B(4)=75) → Optimization
5. Architecture (B(6)=121) → Refactoring

@author: Elias Oulad Brahim
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Handle imports whether run as module or directly
try:
    from .engine import BrahimEngine
    from .analyzer import CodeIssue, IssueCategory, AnalysisResult
except ImportError:
    from engine import BrahimEngine
    from analyzer import CodeIssue, IssueCategory, AnalysisResult


@dataclass
class Fix:
    """Represents a code fix"""
    issue: CodeIssue
    original: str
    replacement: str
    line: int
    confidence: float
    explanation: str


@dataclass
class FixResult:
    """Result of fixing operation"""
    original_code: str
    fixed_code: str
    fixes_applied: List[Fix]
    fixes_skipped: List[CodeIssue]
    improvement_score: float  # How much resonance improved


class CodeFixer:
    """
    Automatic code fixer using Brahim principles.

    Applies fixes in order of impact (weighted by Brahim sequence).
    """

    # Pattern replacements (pattern -> replacement)
    PYTHON_FIXES = {
        # === TYPE FIXES (B(2)=42) ===
        (r'==\s*None', 'is None'): "Use identity check for None",
        (r'!=\s*None', 'is not None'): "Use identity check for None",
        (r'type\s*\(\s*(\w+)\s*\)\s*==\s*(\w+)', r'isinstance(\1, \2)'): "Use isinstance for type checking",
        (r'type\s*\(\s*(\w+)\s*\)\s*is\s+(\w+)', r'isinstance(\1, \2)'): "Use isinstance for type checking",

        # === LOGIC FIXES (B(3)=60) ===
        (r'if\s+True\s*:', '# TODO: Remove always-true condition\n    if True:'): "Flag constant condition",
        (r'if\s+False\s*:', '# TODO: Remove dead code\n    if False:'): "Flag dead code",
        (r'while\s+True\s*:', 'while True:  # TODO: Add break condition'): "Flag infinite loop",
        (r'except\s*:', 'except Exception as e:  # TODO: catch specific exception'): "Replace bare except",
        (r'except\s+Exception\s*:', 'except Exception as e:  # TODO: catch specific exception'): "Capture exception variable",

        # === PERFORMANCE FIXES (B(4)=75) ===
        (r'for\s+(\w+)\s+in\s+range\s*\(\s*len\s*\(\s*(\w+)\s*\)\s*\)',
         r'for \1, _item in enumerate(\2)'): "Use enumerate instead of range(len())",
        (r'\.append\s*\(\s*([^)]+)\s*\)\s*$', r'.append(\1)  # Consider list comprehension'): "Suggest list comprehension",
        (r'\+\s*=\s*["\']', '+= "  # PERF: Use join() for string building'): "Flag string concatenation in loop",

        # === SECURITY FIXES (B(5)=97) - CRITICAL ===
        (r'\beval\s*\(\s*([^)]+)\s*\)', r'ast.literal_eval(\1)  # SECURITY: was eval()'): "Replace dangerous eval",
        (r'\bexec\s*\(\s*([^)]+)\s*\)', r'# SECURITY REMOVED: exec(\1)'): "Remove dangerous exec",
        (r'pickle\.loads\s*\(', 'json.loads(  # SECURITY: was pickle.loads('): "Replace insecure pickle",
        (r'shell\s*=\s*True', 'shell=False  # SECURITY: shell=True is dangerous'): "Disable shell execution",
        (r'verify\s*=\s*False', 'verify=True  # SECURITY: SSL verification disabled'): "Enable SSL verification",

        # === STYLE FIXES ===
        (r'from\s+(\w+)\s+import\s+\*', r'from \1 import specific_name  # TODO: specify imports'): "Replace wildcard import",
        (r'#\s*TODO\s*$', '# TODO: Add description'): "Incomplete TODO",
        (r'print\s*\(\s*\)', 'print()  # Empty print - intentional?'): "Flag empty print",
    }

    KOTLIN_FIXES = {
        # === NULL SAFETY (B(5)=97 - Security) ===
        (r'(\w+)!!\s*\.', r'\1?.'): "Replace force unwrap with safe call",
        (r'(\w+)!!\s*\[', r'\1?.get('): "Replace force unwrap array access",
        (r'as\s+(\w+)\s*$', r'as? \1'): "Use safe cast",

        # === EXCEPTION HANDLING (B(3)=60 - Logic) ===
        # Network/Socket operations
        (r'catch\s*\(\s*e\s*:\s*Exception\s*\)\s*\{\s*\n\s*//\s*(Connection|Socket|Network)',
         'catch (e: java.net.SocketException) {\n            // Socket'): "Catch SocketException for network ops",
        (r'catch\s*\(\s*e\s*:\s*Exception\s*\)\s*\{\s*\n\s*//\s*(I/O|IO|Read|Write)',
         'catch (e: java.io.IOException) {\n            // I/O'): "Catch IOException for I/O ops",

        # Generic exception with better defaults
        (r'catch\s*\(\s*e\s*:\s*Exception\s*\)\s*\{',
         'catch (e: java.io.IOException) {  // TODO: verify exception type'): "Catch IOException as default",

        # === PERFORMANCE (B(4)=75) ===
        (r'\.forEach\s*\{', '.asSequence().forEach {'): "Use sequence for large collections",

        # === SECURITY (B(5)=97) ===
        (r'@SuppressLint\s*\(\s*"HardcodedCredentials"\s*\)',
         '// SECURITY: Remove hardcoded credentials'): "Flag hardcoded credentials",

        # === TYPO FIXES (B(1)=27 - Syntax) ===
        (r'findViewByld', 'findViewById'): "Fix typo",
        (r'actvity', 'activity'): "Fix typo",
        (r'overrride', 'override'): "Fix typo",
    }

    JAVA_FIXES = {
        # === NULL SAFETY ===
        (r'==\s*null', '== null'): "Null check (consider Optional)",
        (r'\.equals\s*\(\s*null\s*\)', ' == null'): "Use == for null comparison",

        # === EXCEPTION HANDLING ===
        (r'catch\s*\(\s*Exception\s+(\w+)\s*\)',
         r'catch (IOException \1)  // TODO: catch specific'): "Catch specific exception",

        # === SECURITY ===
        (r'Runtime\.getRuntime\(\)\.exec\s*\(',
         'ProcessBuilder(  // SECURITY: was Runtime.exec('): "Use ProcessBuilder",
    }

    def __init__(self, language: str = "python", auto_fix_threshold: float = 0.8):
        """
        Initialize fixer.

        Args:
            language: Target language
            auto_fix_threshold: Minimum confidence to auto-apply fix
        """
        self.language = language.lower()

        # Select fix patterns based on language
        if self.language == "python":
            self.fixes = self.PYTHON_FIXES
        elif self.language == "kotlin":
            self.fixes = self.KOTLIN_FIXES
        elif self.language == "java":
            self.fixes = self.JAVA_FIXES
        else:
            # Default to Python patterns
            self.fixes = self.PYTHON_FIXES

        self.auto_fix_threshold = auto_fix_threshold

    def fix(self, code: str, analysis: AnalysisResult, safe_only: bool = True) -> FixResult:
        """
        Apply fixes to code based on analysis.

        Args:
            code: Original code
            analysis: Analysis result from CodeAnalyzer
            safe_only: Only apply high-confidence fixes

        Returns:
            FixResult with fixed code and applied fixes
        """
        fixes_applied = []
        fixes_skipped = []
        lines = code.split('\n')
        modified_lines = lines.copy()

        # Sort issues by Brahim priority (security first, then by severity)
        prioritized = self._prioritize_fixes(analysis.issues)

        for issue in prioritized:
            # Check if we should apply this fix
            if safe_only and issue.confidence < self.auto_fix_threshold:
                fixes_skipped.append(issue)
                continue

            # Try to find a fix for this issue
            fix = self._find_fix(issue, modified_lines)

            if fix:
                # Apply the fix
                if fix.line > 0 and fix.line <= len(modified_lines):
                    modified_lines[fix.line - 1] = fix.replacement
                    fixes_applied.append(fix)
            else:
                fixes_skipped.append(issue)

        # Calculate improvement
        original_resonance = analysis.resonance
        fixed_code = '\n'.join(modified_lines)

        # Estimate new resonance (fewer issues = lower resonance)
        fixed_issues = len(analysis.issues) - len(fixes_applied)
        improvement = len(fixes_applied) / max(1, len(analysis.issues))

        return FixResult(
            original_code=code,
            fixed_code=fixed_code,
            fixes_applied=fixes_applied,
            fixes_skipped=fixes_skipped,
            improvement_score=improvement * 100
        )

    def _prioritize_fixes(self, issues: List[CodeIssue]) -> List[CodeIssue]:
        """
        Prioritize fixes using Brahim weighting.

        Priority order:
        1. Security (critical, high impact)
        2. Syntax (blocks execution)
        3. Memory (can cause crashes)
        4. Logic (affects correctness)
        5. Others (by severity)
        """
        priority_map = {
            IssueCategory.SECURITY: 1,
            IssueCategory.SYNTAX: 2,
            IssueCategory.MEMORY: 3,
            IssueCategory.LOGIC: 4,
            IssueCategory.PERFORMANCE: 5,
            IssueCategory.TYPE: 6,
            IssueCategory.ARCHITECTURE: 7,
            IssueCategory.CONCURRENCY: 8,
            IssueCategory.INTEGRATION: 9,
            IssueCategory.SYSTEM: 10,
        }

        def priority_key(issue: CodeIssue) -> Tuple[int, int, int]:
            # (category priority, -severity, line)
            cat_priority = priority_map.get(issue.category, 10)
            return (cat_priority, -issue.severity, issue.line)

        return sorted(issues, key=priority_key)

    def _find_fix(self, issue: CodeIssue, lines: List[str]) -> Optional[Fix]:
        """Find and create a fix for the given issue"""
        if issue.line < 1 or issue.line > len(lines):
            return None

        original_line = lines[issue.line - 1]

        # Try pattern-based fixes
        for (pattern, replacement), explanation in self.fixes.items():
            if re.search(pattern, original_line):
                fixed_line = re.sub(pattern, replacement, original_line)
                return Fix(
                    issue=issue,
                    original=original_line,
                    replacement=fixed_line,
                    line=issue.line,
                    confidence=0.9,
                    explanation=explanation
                )

        # Generate fix from issue suggestion
        if issue.suggestion:
            return self._generate_fix_from_suggestion(issue, original_line)

        return None

    def _generate_fix_from_suggestion(self, issue: CodeIssue, original: str) -> Optional[Fix]:
        """Generate a fix based on the issue suggestion"""

        # Common suggestion patterns
        suggestion = issue.suggestion.lower()

        # "use X instead of Y" pattern
        if "instead of" in suggestion:
            # Can't auto-fix complex substitutions
            return None

        # "remove" suggestions
        if "remove" in suggestion:
            # Comment out the line instead of removing
            return Fix(
                issue=issue,
                original=original,
                replacement=f"# TODO: {issue.message}\n# {original}",
                line=issue.line,
                confidence=0.6,
                explanation="Commented out problematic code"
            )

        # "add" suggestions
        if "add" in suggestion:
            # Add a TODO comment
            indent = len(original) - len(original.lstrip())
            todo = " " * indent + f"# TODO: {issue.suggestion}"
            return Fix(
                issue=issue,
                original=original,
                replacement=f"{todo}\n{original}",
                line=issue.line,
                confidence=0.5,
                explanation="Added TODO for required change"
            )

        return None

    def suggest_fixes(self, analysis: AnalysisResult) -> List[Dict]:
        """
        Generate fix suggestions without applying them.

        Returns list of suggested fixes with explanations.
        """
        suggestions = []

        for issue in analysis.issues:
            # Calculate fix effort using mirror principle
            bug_weight = BrahimEngine.B(issue.severity)
            fix_effort = BrahimEngine.mirror(bug_weight)

            suggestion = {
                'issue': issue.message,
                'category': issue.category.name,
                'line': issue.line,
                'severity': issue.severity,
                'bug_weight': bug_weight,
                'fix_effort': fix_effort,
                'suggestion': issue.suggestion,
                'effort_ratio': fix_effort / BrahimEngine.SUM,  # Normalized effort
                'priority_score': bug_weight / fix_effort if fix_effort > 0 else float('inf'),
            }

            suggestions.append(suggestion)

        # Sort by priority score (high bug weight, low fix effort = high priority)
        return sorted(suggestions, key=lambda x: -x['priority_score'])

    def estimate_fix_time(self, analysis: AnalysisResult) -> Dict[str, float]:
        """
        Estimate time to fix all issues using Brahim metrics.

        Uses B(3) = 60 as base cycle time (seconds).
        """
        base_time = BrahimEngine.B(3)  # 60 seconds

        total_effort = 0
        by_category = {}

        for issue in analysis.issues:
            fix_effort = BrahimEngine.mirror(BrahimEngine.B(issue.severity))
            effort_time = (fix_effort / BrahimEngine.SUM) * base_time

            total_effort += effort_time

            cat = issue.category.name
            by_category[cat] = by_category.get(cat, 0) + effort_time

        return {
            'total_seconds': total_effort,
            'total_minutes': total_effort / 60,
            'by_category': by_category,
            'issues_count': len(analysis.issues),
            'avg_per_issue': total_effort / max(1, len(analysis.issues)),
        }
