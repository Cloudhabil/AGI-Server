"""
CODE ANALYZER - Brahim-Aligned Static Analysis

Applies the mirror symmetry principle:
- For every bug pattern, there exists a fix pattern
- B(i) + B(11-i) = 214 → Bug + Fix = Resolution

Analysis Categories (mapped to Brahim sequence):
- B(1)=27: Syntax errors (most basic)
- B(2)=42: Type mismatches
- B(3)=60: Logic errors
- B(4)=75: Performance issues
- B(5)=97: Security vulnerabilities
- B(6)=121: Architecture problems
- B(7)=136: Memory issues
- B(8)=154: Concurrency bugs
- B(9)=172: Integration errors
- B(10)=187: System-level failures

@author: Elias Oulad Brahim
"""

import re
import ast
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# Handle imports whether run as module or directly
try:
    from .engine import BrahimEngine, SafetyVerdict, DebugResult
except ImportError:
    from engine import BrahimEngine, SafetyVerdict, DebugResult


class IssueCategory(Enum):
    """Issue categories mapped to Brahim sequence"""
    SYNTAX = 1          # B(1) = 27
    TYPE = 2            # B(2) = 42
    LOGIC = 3           # B(3) = 60
    PERFORMANCE = 4     # B(4) = 75
    SECURITY = 5        # B(5) = 97
    ARCHITECTURE = 6    # B(6) = 121
    MEMORY = 7          # B(7) = 136
    CONCURRENCY = 8     # B(8) = 154
    INTEGRATION = 9     # B(9) = 172
    SYSTEM = 10         # B(10) = 187


@dataclass
class CodeIssue:
    """Represents a detected code issue"""
    category: IssueCategory
    severity: int  # 1-10 (maps to Brahim sequence)
    line: int
    column: int
    message: str
    suggestion: str
    code_snippet: str = ""
    confidence: float = 1.0

    @property
    def weight(self) -> int:
        """Issue weight based on Brahim sequence"""
        return BrahimEngine.B(self.severity)

    @property
    def mirror_weight(self) -> int:
        """Mirror weight (fix effort)"""
        return BrahimEngine.mirror(self.weight)


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    file_path: str
    issues: List[CodeIssue] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    verdict: SafetyVerdict = SafetyVerdict.NOMINAL
    resonance: float = 0.0
    suggestions: List[str] = field(default_factory=list)


class CodeAnalyzer:
    """
    Brahim-Aligned Code Analyzer

    Uses resonance detection to find code anomalies and
    golden ratio optimization to prioritize fixes.
    """

    # Pattern definitions with Brahim-aligned severities
    PATTERNS = {
        # Syntax patterns (severity 1-2)
        r'print\s*\(\s*\)': (IssueCategory.SYNTAX, 1, "Empty print statement", "Remove or add content"),
        r'pass\s*$': (IssueCategory.SYNTAX, 1, "Empty pass statement", "Add implementation or remove"),

        # Type patterns (severity 2-3)
        r'==\s*None': (IssueCategory.TYPE, 2, "Use 'is None' instead of '== None'", "Replace with 'is None'"),
        r'!=\s*None': (IssueCategory.TYPE, 2, "Use 'is not None' instead of '!= None'", "Replace with 'is not None'"),
        r'type\s*\(\s*\w+\s*\)\s*==': (IssueCategory.TYPE, 3, "Use isinstance() instead of type()", "Use isinstance(obj, Type)"),

        # Logic patterns (severity 3-4)
        r'if\s+True\s*:': (IssueCategory.LOGIC, 3, "Constant condition 'if True'", "Remove unnecessary condition"),
        r'if\s+False\s*:': (IssueCategory.LOGIC, 3, "Dead code 'if False'", "Remove unreachable code"),
        r'while\s+True\s*:(?!.*break)': (IssueCategory.LOGIC, 4, "Infinite loop without break", "Add break condition"),

        # Performance patterns (severity 4-5)
        r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(': (IssueCategory.PERFORMANCE, 4, "Use enumerate() instead of range(len())", "Use 'for i, item in enumerate()'"),
        r'\+\s*=\s*["\']': (IssueCategory.PERFORMANCE, 4, "String concatenation in loop", "Use join() or list"),
        r'\.append\s*\([^)]+\)\s*$': (IssueCategory.PERFORMANCE, 4, "Consider list comprehension", "Use [x for x in ...]"),

        # Security patterns (severity 5-6)
        r'eval\s*\(': (IssueCategory.SECURITY, 6, "Dangerous eval() usage", "Use ast.literal_eval() or safer alternative"),
        r'exec\s*\(': (IssueCategory.SECURITY, 6, "Dangerous exec() usage", "Avoid dynamic code execution"),
        r'pickle\.loads?\s*\(': (IssueCategory.SECURITY, 5, "Insecure pickle usage", "Use json or safer serialization"),
        r'input\s*\(\s*\)': (IssueCategory.SECURITY, 5, "Unvalidated input", "Validate and sanitize user input"),

        # Memory patterns (severity 7)
        r'global\s+\w+': (IssueCategory.MEMORY, 7, "Global variable usage", "Consider passing as parameter"),
        r'\[\s*\]\s*\*\s*\d+': (IssueCategory.MEMORY, 7, "Mutable default in list multiplication", "Use list comprehension"),

        # Architecture patterns (severity 6)
        r'from\s+\w+\s+import\s+\*': (IssueCategory.ARCHITECTURE, 6, "Wildcard import", "Import specific names"),
        r'class\s+\w+\s*:\s*\n\s*def\s+\w+\s*\(\s*self': (IssueCategory.ARCHITECTURE, 6, "Missing docstring", "Add class docstring"),

        # Concurrency patterns (severity 8)
        r'threading\.Thread\s*\(': (IssueCategory.CONCURRENCY, 8, "Direct thread usage", "Consider ThreadPoolExecutor"),
        r'time\.sleep\s*\(\s*\d+\s*\)': (IssueCategory.CONCURRENCY, 8, "Blocking sleep", "Consider async/await"),
    }

    # Kotlin/Java patterns
    KOTLIN_PATTERNS = {
        r'!!\s*\.': (IssueCategory.SECURITY, 5, "Force unwrap (!!) can cause NPE", "Use safe call (?.) or check null"),
        r'var\s+\w+\s*:\s*\w+\s*\?\s*=\s*null': (IssueCategory.TYPE, 3, "Nullable var initialized to null", "Consider lateinit or lazy"),
        r'catch\s*\(\s*e\s*:\s*Exception\s*\)': (IssueCategory.LOGIC, 4, "Catching generic Exception", "Catch specific exception types"),
        r'\.let\s*\{\s*it': (IssueCategory.PERFORMANCE, 4, "Implicit 'it' in let block", "Consider named parameter"),
        r'findViewByld': (IssueCategory.SYNTAX, 1, "Typo: findViewByld", "Should be findViewById"),
    }

    def __init__(self, language: str = "python"):
        self.language = language.lower()
        self.patterns = self.PATTERNS if language == "python" else self.KOTLIN_PATTERNS

    def analyze(self, code: str, file_path: str = "<string>") -> AnalysisResult:
        """
        Analyze code and return Brahim-aligned results.

        Uses resonance detection to find anomalies.
        """
        result = AnalysisResult(file_path=file_path)
        lines = code.split('\n')

        # Pattern-based analysis
        for line_num, line in enumerate(lines, 1):
            for pattern, (category, severity, message, suggestion) in self.patterns.items():
                if re.search(pattern, line):
                    issue = CodeIssue(
                        category=category,
                        severity=severity,
                        line=line_num,
                        column=0,
                        message=message,
                        suggestion=suggestion,
                        code_snippet=line.strip(),
                        confidence=0.9
                    )
                    result.issues.append(issue)

        # Language-specific deep analysis
        if self.language == "python":
            result.issues.extend(self._analyze_python_ast(code))

        # Calculate metrics
        result.metrics = self._calculate_metrics(code, lines)

        # Calculate resonance (error density)
        if result.issues:
            error_weights = [issue.weight / BrahimEngine.B(10) for issue in result.issues]
            result.resonance = BrahimEngine.resonance(error_weights)
        else:
            result.resonance = BrahimEngine.GENESIS  # Perfect alignment

        # Determine verdict
        result.verdict = BrahimEngine.assess_safety(result.resonance)

        # Generate suggestions
        result.suggestions = self._generate_suggestions(result)

        # Prioritize issues using Brahim weighting
        result.issues = BrahimEngine.prioritize_issues(
            [{'issue': i, 'severity': i.severity, 'frequency': 1} for i in result.issues]
        )
        result.issues = [item['issue'] for item in result.issues]

        return result

    def _analyze_python_ast(self, code: str) -> List[CodeIssue]:
        """Deep AST analysis for Python"""
        issues = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                # Check for bare except
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    issues.append(CodeIssue(
                        category=IssueCategory.LOGIC,
                        severity=4,
                        line=node.lineno,
                        column=node.col_offset,
                        message="Bare except clause",
                        suggestion="Specify exception type: except Exception as e:",
                        confidence=1.0
                    ))

                # Check for mutable default arguments
                if isinstance(node, ast.FunctionDef):
                    for default in node.args.defaults:
                        if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                            issues.append(CodeIssue(
                                category=IssueCategory.MEMORY,
                                severity=7,
                                line=node.lineno,
                                column=node.col_offset,
                                message=f"Mutable default argument in {node.name}()",
                                suggestion="Use None and initialize inside function",
                                confidence=1.0
                            ))

                # Check for too many arguments (B(4) = 75% threshold = ~7 args)
                if isinstance(node, ast.FunctionDef) and len(node.args.args) > 7:
                    issues.append(CodeIssue(
                        category=IssueCategory.ARCHITECTURE,
                        severity=6,
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"Too many parameters ({len(node.args.args)}) in {node.name}()",
                        suggestion="Consider using a config object or dataclass",
                        confidence=0.8
                    ))

                # Check for deeply nested code (using B(4)/10 = 7.5 levels)
                if isinstance(node, (ast.If, ast.For, ast.While)):
                    depth = self._get_nesting_depth(node)
                    if depth > 7:
                        issues.append(CodeIssue(
                            category=IssueCategory.LOGIC,
                            severity=4,
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Deeply nested code (depth={depth})",
                            suggestion="Extract to separate function",
                            confidence=0.9
                        ))

        except SyntaxError as e:
            issues.append(CodeIssue(
                category=IssueCategory.SYNTAX,
                severity=1,
                line=e.lineno or 1,
                column=e.offset or 0,
                message=f"Syntax error: {e.msg}",
                suggestion="Fix syntax error",
                confidence=1.0
            ))

        return issues

    def _get_nesting_depth(self, node: ast.AST, current_depth: int = 0) -> int:
        """Calculate nesting depth of a node"""
        max_depth = current_depth

        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
                child_depth = self._get_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, child_depth)

        return max_depth

    def _calculate_metrics(self, code: str, lines: List[str]) -> Dict[str, float]:
        """Calculate code metrics using Brahim principles"""
        metrics = {}

        # Lines of code (normalized by B(3) = 60)
        non_empty = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        metrics['lines'] = min(100, non_empty / BrahimEngine.B(3) * 50)

        # Comment ratio
        comments = sum(1 for line in lines if line.strip().startswith('#'))
        metrics['comment_ratio'] = comments / max(1, len(lines)) * 100

        # Cyclomatic complexity estimate (count decision points)
        decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'with', 'and', 'or']
        decisions = sum(code.count(f' {kw} ') + code.count(f' {kw}:') for kw in decision_keywords)
        metrics['cyclomatic'] = min(100, decisions / BrahimEngine.B(1) * 30)

        # Nesting estimate
        max_indent = max((len(line) - len(line.lstrip())) // 4 for line in lines if line.strip())
        metrics['nesting'] = min(100, max_indent * 10)

        # Function count
        metrics['functions'] = code.count('def ') + code.count('fun ')
        metrics['classes'] = code.count('class ')

        return metrics

    def _generate_suggestions(self, result: AnalysisResult) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []

        # Group issues by category
        categories = {}
        for issue in result.issues:
            cat = issue.category.name
            categories[cat] = categories.get(cat, 0) + 1

        # Generate category-specific suggestions
        if categories.get('SYNTAX', 0) > 0:
            suggestions.append(f"Fix {categories['SYNTAX']} syntax issue(s) first - they block execution")

        if categories.get('SECURITY', 0) > 0:
            suggestions.append(f"CRITICAL: Address {categories['SECURITY']} security issue(s) immediately")

        if categories.get('PERFORMANCE', 0) > BrahimEngine.B(1) // 10:
            suggestions.append("Consider profiling - multiple performance issues detected")

        if result.metrics.get('cyclomatic', 0) > BrahimEngine.B(4):
            suggestions.append("High complexity detected - consider refactoring into smaller functions")

        if result.metrics.get('nesting', 0) > BrahimEngine.B(3):
            suggestions.append("Deep nesting detected - extract nested logic into separate functions")

        # Brahim-aligned suggestion
        if result.resonance > BrahimEngine.GENESIS * 10:
            suggestions.append(
                f"Code resonance ({result.resonance:.4f}) is far from Genesis ({BrahimEngine.GENESIS}). "
                "Major refactoring recommended."
            )

        return suggestions

    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analyze a file from disk"""
        path = Path(file_path)

        if not path.exists():
            result = AnalysisResult(file_path=file_path)
            result.issues.append(CodeIssue(
                category=IssueCategory.SYSTEM,
                severity=10,
                line=0,
                column=0,
                message=f"File not found: {file_path}",
                suggestion="Check file path",
                confidence=1.0
            ))
            result.verdict = SafetyVerdict.BLOCKED
            return result

        # Detect language
        if path.suffix in ['.py']:
            self.language = 'python'
            self.patterns = self.PATTERNS
        elif path.suffix in ['.kt', '.java']:
            self.language = 'kotlin'
            self.patterns = self.KOTLIN_PATTERNS

        code = path.read_text(encoding='utf-8')
        return self.analyze(code, file_path)
