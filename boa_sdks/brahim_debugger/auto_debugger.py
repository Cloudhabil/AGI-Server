#!/usr/bin/env python3
"""
BRAHIM AUTO-DEBUGGER - Intelligent Code Analysis & Auto-Fix System

This enhanced agent:
1. DISCOVERS - Finds all code files in a project
2. ANALYZES - Runs Brahim-aligned analysis on each file
3. THINKS - Prioritizes issues using Brahim mathematics
4. FIXES - Automatically applies safe fixes
5. VERIFIES - Confirms improvements

Usage:
    python auto_debugger.py /path/to/project --fix --language python

Author: Elias Oulad Brahim
"""

import os
import sys
import json
import argparse
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from engine import BrahimEngine, SafetyVerdict
from analyzer import CodeAnalyzer, IssueCategory
from fixer import CodeFixer


@dataclass
class FileReport:
    """Report for a single file"""
    path: str
    language: str
    issues_found: int
    issues_fixed: int
    original_resonance: float
    final_resonance: float
    verdict: str
    issues: List[Dict]
    fixes_applied: List[str]
    thinking: List[str]  # Agent's reasoning


@dataclass
class ProjectReport:
    """Report for entire project"""
    project_path: str
    timestamp: str
    files_scanned: int
    files_with_issues: int
    total_issues: int
    total_fixed: int
    overall_resonance: float
    genesis_alignment: float
    file_reports: List[FileReport]
    summary: Dict


class BrahimAutoDebugger:
    """
    Intelligent Auto-Debugging Agent using Brahim Principles

    The agent thinks through problems using the Brahim sequence
    to prioritize and fix issues automatically.
    """

    VERSION = "2.0.0"

    # File patterns by language
    FILE_PATTERNS = {
        'python': ['*.py'],
        'kotlin': ['*.kt', '*.kts'],
        'java': ['*.java'],
        'javascript': ['*.js', '*.jsx', '*.ts', '*.tsx'],
        'go': ['*.go'],
        'rust': ['*.rs'],
        'c': ['*.c', '*.h'],
        'cpp': ['*.cpp', '*.hpp', '*.cc', '*.hh'],
    }

    # Directories to skip
    SKIP_DIRS = {
        '__pycache__', 'node_modules', '.git', '.svn', 'venv', 'env',
        'build', 'dist', 'target', '.idea', '.vscode', 'vendor',
        'test', 'tests', '__tests__', 'spec', 'specs'
    }

    def __init__(
        self,
        language: str = 'python',
        auto_fix: bool = False,
        safe_only: bool = True,
        verbose: bool = True,
        max_workers: int = 4
    ):
        self.language = language.lower()
        self.auto_fix = auto_fix
        self.safe_only = safe_only
        self.verbose = verbose
        self.max_workers = max_workers

        self.analyzer = CodeAnalyzer(language=language)
        self.fixer = CodeFixer(language=language)

        self._thinking_log = []

    def think(self, thought: str):
        """Log agent's reasoning process"""
        self._thinking_log.append(thought)
        if self.verbose:
            print(f"  [THINK] {thought}")

    def discover_files(self, project_path: str) -> List[Path]:
        """
        Discover all code files in the project.
        Uses Brahim B(9)=172 principle: Integration requires thorough discovery.
        """
        self.think(f"Scanning project: {project_path}")

        patterns = self.FILE_PATTERNS.get(self.language, ['*.*'])
        files = []

        project = Path(project_path)
        if not project.exists():
            self.think(f"ERROR: Path does not exist: {project_path}")
            return []

        if project.is_file():
            self.think(f"Single file mode: {project.name}")
            return [project]

        for pattern in patterns:
            for file_path in project.rglob(pattern):
                # Skip excluded directories
                if any(skip in file_path.parts for skip in self.SKIP_DIRS):
                    continue
                files.append(file_path)

        self.think(f"Found {len(files)} {self.language} files")

        # Sort by modification time (most recent first) - B(1)=27 principle
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        return files

    def analyze_file(self, file_path: Path) -> FileReport:
        """
        Analyze a single file with full thinking process.
        """
        thinking = []
        thinking.append(f"Analyzing: {file_path.name}")

        try:
            code = file_path.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            thinking.append(f"ERROR reading file: {e}")
            return FileReport(
                path=str(file_path),
                language=self.language,
                issues_found=0,
                issues_fixed=0,
                original_resonance=1.0,
                final_resonance=1.0,
                verdict="ERROR",
                issues=[],
                fixes_applied=[],
                thinking=thinking
            )

        # Line count check - B(3)=60 principle (review cycle)
        lines = code.count('\n') + 1
        thinking.append(f"File has {lines} lines")

        if lines > 1000:
            thinking.append(f"Large file (>{1000} lines) - will take longer")

        # Run analysis
        analysis = self.analyzer.analyze(code, str(file_path))

        thinking.append(f"Found {len(analysis.issues)} issues")
        thinking.append(f"Resonance: {analysis.resonance:.4f} (Genesis: {BrahimEngine.GENESIS})")

        # Categorize issues using Brahim weights
        by_category = {}
        for issue in analysis.issues:
            cat = issue.category.name
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(issue)

        for cat, issues in sorted(by_category.items(), key=lambda x: -len(x[1])):
            weight = BrahimEngine.B(IssueCategory[cat].value)
            thinking.append(f"  {cat}: {len(issues)} issues (B={weight})")

        # Prepare issues for report
        issues_data = [
            {
                'category': i.category.name,
                'severity': i.severity,
                'line': i.line,
                'message': i.message,
                'suggestion': i.suggestion,
                'brahim_weight': BrahimEngine.B(i.severity)
            }
            for i in analysis.issues
        ]

        fixes_applied = []
        final_resonance = analysis.resonance

        # Auto-fix if enabled
        if self.auto_fix and analysis.issues:
            thinking.append("Attempting auto-fix...")

            fix_result = self.fixer.fix(code, analysis, self.safe_only)

            if fix_result.fixes_applied:
                thinking.append(f"Applied {len(fix_result.fixes_applied)} fixes")

                # Write fixed code back
                try:
                    file_path.write_text(fix_result.fixed_code, encoding='utf-8')
                    thinking.append("Saved fixed code to file")

                    fixes_applied = [f.explanation for f in fix_result.fixes_applied]

                    # Re-analyze to get new resonance
                    new_analysis = self.analyzer.analyze(fix_result.fixed_code, str(file_path))
                    final_resonance = new_analysis.resonance

                    improvement = ((analysis.resonance - final_resonance) /
                                   max(0.001, analysis.resonance) * 100)
                    thinking.append(f"Resonance improved by {improvement:.1f}%")

                except Exception as e:
                    thinking.append(f"ERROR saving fixes: {e}")
            else:
                thinking.append("No safe fixes available")

        return FileReport(
            path=str(file_path),
            language=self.language,
            issues_found=len(analysis.issues),
            issues_fixed=len(fixes_applied),
            original_resonance=analysis.resonance,
            final_resonance=final_resonance,
            verdict=analysis.verdict.value.upper(),
            issues=issues_data,
            fixes_applied=fixes_applied,
            thinking=thinking
        )

    def debug_project(self, project_path: str) -> ProjectReport:
        """
        Debug entire project with parallel analysis.

        Uses B(8)=154 principle: Concurrency for efficiency.
        """
        start_time = datetime.now()

        print("=" * 70)
        print("  BRAHIM AUTO-DEBUGGER v" + self.VERSION)
        print("  Intelligent Code Analysis & Auto-Fix System")
        print("=" * 70)
        print()

        # Discover files
        files = self.discover_files(project_path)

        if not files:
            print("[!] No files found to analyze")
            return ProjectReport(
                project_path=project_path,
                timestamp=start_time.isoformat(),
                files_scanned=0,
                files_with_issues=0,
                total_issues=0,
                total_fixed=0,
                overall_resonance=0.0,
                genesis_alignment=0.0,
                file_reports=[],
                summary={}
            )

        print(f"\n[*] Analyzing {len(files)} files...")
        print("-" * 70)

        # Analyze files (parallel or sequential based on count)
        file_reports = []

        if len(files) > 10 and self.max_workers > 1:
            # Parallel analysis for large projects
            self.think(f"Using {self.max_workers} parallel workers")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self.analyze_file, f): f for f in files}

                for i, future in enumerate(as_completed(futures), 1):
                    report = future.result()
                    file_reports.append(report)

                    # Progress indicator
                    status = self._verdict_icon(report.verdict)
                    rel_path = Path(report.path).name
                    print(f"  [{i:3d}/{len(files)}] {status} {rel_path}: "
                          f"{report.issues_found} issues, {report.issues_fixed} fixed")
        else:
            # Sequential for small projects (better output)
            for i, file_path in enumerate(files, 1):
                report = self.analyze_file(file_path)
                file_reports.append(report)

                status = self._verdict_icon(report.verdict)
                rel_path = file_path.name
                print(f"  [{i:3d}/{len(files)}] {status} {rel_path}: "
                      f"{report.issues_found} issues, {report.issues_fixed} fixed")

        # Calculate totals
        total_issues = sum(r.issues_found for r in file_reports)
        total_fixed = sum(r.issues_fixed for r in file_reports)
        files_with_issues = sum(1 for r in file_reports if r.issues_found > 0)

        # Calculate overall resonance (weighted average)
        if file_reports:
            total_lines = sum(1 for r in file_reports)  # Simplified
            overall_resonance = sum(r.final_resonance for r in file_reports) / len(file_reports)
        else:
            overall_resonance = 0.0

        genesis_alignment = BrahimEngine.axiological_alignment(overall_resonance)

        # Build summary
        summary = self._build_summary(file_reports, total_issues, total_fixed)

        # Print summary
        self._print_summary(
            files=len(files),
            with_issues=files_with_issues,
            total_issues=total_issues,
            total_fixed=total_fixed,
            resonance=overall_resonance,
            alignment=genesis_alignment,
            summary=summary,
            duration=(datetime.now() - start_time).total_seconds()
        )

        return ProjectReport(
            project_path=project_path,
            timestamp=start_time.isoformat(),
            files_scanned=len(files),
            files_with_issues=files_with_issues,
            total_issues=total_issues,
            total_fixed=total_fixed,
            overall_resonance=overall_resonance,
            genesis_alignment=genesis_alignment,
            file_reports=file_reports,
            summary=summary
        )

    def _build_summary(
        self,
        reports: List[FileReport],
        total_issues: int,
        total_fixed: int
    ) -> Dict:
        """Build analysis summary using Brahim categories"""

        # Issues by category
        by_category = {}
        for report in reports:
            for issue in report.issues:
                cat = issue['category']
                if cat not in by_category:
                    by_category[cat] = {'count': 0, 'fixed': 0, 'files': set()}
                by_category[cat]['count'] += 1
                by_category[cat]['files'].add(report.path)

        # Convert sets to counts
        for cat in by_category:
            by_category[cat]['files'] = len(by_category[cat]['files'])

        # Verdicts
        verdicts = {}
        for report in reports:
            v = report.verdict
            verdicts[v] = verdicts.get(v, 0) + 1

        # Top issues to fix (priority order)
        all_issues = []
        for report in reports:
            for issue in report.issues:
                all_issues.append({
                    **issue,
                    'file': Path(report.path).name
                })

        # Sort by Brahim weight (highest first)
        all_issues.sort(key=lambda x: -x.get('brahim_weight', 0))

        return {
            'by_category': by_category,
            'verdicts': verdicts,
            'top_issues': all_issues[:20],
            'fix_rate': (total_fixed / max(1, total_issues)) * 100
        }

    def _verdict_icon(self, verdict: str) -> str:
        """Get icon for verdict"""
        icons = {
            'SAFE': '[OK]',
            'NOMINAL': '[--]',
            'CAUTION': '[!!]',
            'UNSAFE': '[**]',
            'BLOCKED': '[XX]',
            'ERROR': '[??]'
        }
        return icons.get(verdict, '[??]')

    def _print_summary(
        self,
        files: int,
        with_issues: int,
        total_issues: int,
        total_fixed: int,
        resonance: float,
        alignment: float,
        summary: Dict,
        duration: float
    ):
        """Print analysis summary"""
        print()
        print("=" * 70)
        print("  ANALYSIS SUMMARY")
        print("=" * 70)
        print()

        print(f"  FILES:")
        print(f"    Scanned:      {files}")
        print(f"    With issues:  {with_issues} ({with_issues/max(1,files)*100:.1f}%)")
        print(f"    Clean:        {files - with_issues}")
        print()

        print(f"  ISSUES:")
        print(f"    Total found:  {total_issues}")
        print(f"    Auto-fixed:   {total_fixed}")
        print(f"    Remaining:    {total_issues - total_fixed}")
        print(f"    Fix rate:     {summary['fix_rate']:.1f}%")
        print()

        print(f"  RESONANCE:")
        print(f"    Current:      {resonance:.6f}")
        print(f"    Genesis:      {BrahimEngine.GENESIS}")
        print(f"    Alignment:    {alignment:.6f}")
        print()

        if summary['by_category']:
            print(f"  ISSUES BY CATEGORY (Brahim-Weighted):")

            # Sort by Brahim weight
            cats = list(summary['by_category'].items())
            cat_order = ['SECURITY', 'SYNTAX', 'MEMORY', 'LOGIC', 'PERFORMANCE',
                        'TYPE', 'ARCHITECTURE', 'CONCURRENCY', 'INTEGRATION', 'SYSTEM']
            cats.sort(key=lambda x: cat_order.index(x[0]) if x[0] in cat_order else 99)

            for cat, data in cats:
                try:
                    weight = BrahimEngine.B(IssueCategory[cat].value)
                except:
                    weight = 0
                print(f"    [{cat}] B={weight}: {data['count']} in {data['files']} files")
            print()

        if summary['top_issues']:
            print(f"  TOP ISSUES TO FIX:")
            print("-" * 70)
            for i, issue in enumerate(summary['top_issues'][:10], 1):
                print(f"  {i:2d}. [{issue['category']}] {issue['file']}:{issue['line']}")
                print(f"      {issue['message']}")
                if issue.get('suggestion'):
                    print(f"      -> {issue['suggestion']}")
            print()

        print(f"  Completed in {duration:.2f}s")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Brahim Auto-Debugger - Intelligent Code Analysis & Auto-Fix",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto_debugger.py ./my_project                    # Analyze Python project
  python auto_debugger.py ./my_project --fix              # Analyze and auto-fix
  python auto_debugger.py ./my_project -l kotlin --fix    # Kotlin with auto-fix
  python auto_debugger.py ./src/app.py                    # Single file

Brahim Principles Applied:
  B(1)=27  - Syntax fundamentals first
  B(5)=97  - Security is critical
  B(3)=60  - Review cycle time
  B(8)=154 - Concurrent processing
  Genesis  - 0.0219 target resonance
        """
    )

    parser.add_argument('path', help='Project directory or file to analyze')
    parser.add_argument('--fix', '-f', action='store_true',
                       help='Automatically apply safe fixes')
    parser.add_argument('--language', '-l', default='python',
                       choices=['python', 'kotlin', 'java', 'javascript', 'go', 'rust'],
                       help='Programming language (default: python)')
    parser.add_argument('--unsafe', action='store_true',
                       help='Apply all fixes, not just safe ones')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Minimal output')
    parser.add_argument('--workers', '-w', type=int, default=4,
                       help='Parallel workers (default: 4)')
    parser.add_argument('--json', '-j', help='Output JSON report to file')

    args = parser.parse_args()

    debugger = BrahimAutoDebugger(
        language=args.language,
        auto_fix=args.fix,
        safe_only=not args.unsafe,
        verbose=not args.quiet,
        max_workers=args.workers
    )

    report = debugger.debug_project(args.path)

    # Save JSON report if requested
    if args.json:
        with open(args.json, 'w') as f:
            # Convert dataclasses to dicts
            report_dict = asdict(report)
            json.dump(report_dict, f, indent=2, default=str)
        print(f"\n[*] Report saved to: {args.json}")

    # Exit code based on issues
    if report.total_issues == 0:
        sys.exit(0)
    elif report.total_issues == report.total_fixed:
        sys.exit(0)  # All fixed
    else:
        sys.exit(1)  # Issues remain


if __name__ == "__main__":
    main()
