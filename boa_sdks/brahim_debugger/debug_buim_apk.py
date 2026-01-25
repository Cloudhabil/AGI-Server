#!/usr/bin/env python3
"""
BUIM APK Debugger - Analyzes all Kotlin files in the APK using Brahim principles

Generates a consolidated report of all issues found.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import BrahimDebuggerAgent
from engine import BrahimEngine


def find_kotlin_files(root_dir: str) -> list:
    """Find all .kt files in directory"""
    kotlin_files = []
    for root, dirs, files in os.walk(root_dir):
        # Skip test files for now
        if 'test' in root.lower():
            continue
        for file in files:
            if file.endswith('.kt'):
                kotlin_files.append(os.path.join(root, file))
    return sorted(kotlin_files)


def analyze_file(agent: BrahimDebuggerAgent, file_path: str) -> dict:
    """Analyze a single file and return results"""
    try:
        result = agent.debug_file(file_path)
        return {
            'file': file_path,
            'verdict': result.verdict,
            'issues_count': result.data.get('issues_count', 0),
            'issues': result.data.get('issues', []),
            'resonance': result.resonance,
            'alignment': result.alignment,
            'success': result.success
        }
    except Exception as e:
        return {
            'file': file_path,
            'verdict': 'ERROR',
            'issues_count': 0,
            'issues': [],
            'resonance': 0,
            'alignment': 0,
            'success': False,
            'error': str(e)
        }


def main():
    print("=" * 70)
    print("  BRAHIM DEBUGGER - BUIM APK ANALYSIS")
    print("  Analyzing all Kotlin files using Brahim mathematical principles")
    print("=" * 70)
    print()

    # Find APK directory
    script_dir = Path(__file__).parent
    apk_dir = script_dir.parent.parent / "buim_apk"

    if not apk_dir.exists():
        print(f"[ERROR] APK directory not found: {apk_dir}")
        return

    # Find all Kotlin files
    kotlin_files = find_kotlin_files(str(apk_dir))
    print(f"[*] Found {len(kotlin_files)} Kotlin files to analyze")
    print()

    # Create agent (verbose=False for batch processing)
    agent = BrahimDebuggerAgent(language="kotlin", verbose=False)

    # Analyze all files
    results = []
    issues_by_category = {}
    total_issues = 0

    verdicts = {
        'SAFE': 0,
        'NOMINAL': 0,
        'CAUTION': 0,
        'UNSAFE': 0,
        'BLOCKED': 0,
        'ERROR': 0
    }

    for i, file_path in enumerate(kotlin_files, 1):
        rel_path = os.path.relpath(file_path, apk_dir)
        print(f"  [{i:3d}/{len(kotlin_files)}] {rel_path}...", end=" ")

        result = analyze_file(agent, file_path)
        results.append(result)

        # Track statistics
        verdicts[result['verdict']] = verdicts.get(result['verdict'], 0) + 1
        total_issues += result['issues_count']

        # Track issues by category
        for issue in result['issues']:
            cat = issue.get('category', 'UNKNOWN')
            if cat not in issues_by_category:
                issues_by_category[cat] = []
            issues_by_category[cat].append({
                'file': rel_path,
                'line': issue.get('line', 0),
                'message': issue.get('message', ''),
                'suggestion': issue.get('suggestion', '')
            })

        # Print result
        if result['verdict'] == 'SAFE':
            print("[OK]")
        elif result['verdict'] == 'NOMINAL':
            print(f"[--] {result['issues_count']} minor")
        elif result['verdict'] == 'CAUTION':
            print(f"[!!] {result['issues_count']} issues")
        elif result['verdict'] == 'UNSAFE':
            print(f"[**] {result['issues_count']} problems")
        elif result['verdict'] == 'BLOCKED':
            print(f"[XX] {result['issues_count']} critical")
        else:
            print(f"[??] {result.get('error', 'Unknown error')}")

    # Print summary
    print()
    print("=" * 70)
    print("  ANALYSIS SUMMARY")
    print("=" * 70)
    print()

    print("  VERDICTS:")
    print(f"    [OK] SAFE:     {verdicts['SAFE']:3d} files")
    print(f"    [--] NOMINAL:  {verdicts['NOMINAL']:3d} files")
    print(f"    [!!] CAUTION:  {verdicts['CAUTION']:3d} files")
    print(f"    [**] UNSAFE:   {verdicts['UNSAFE']:3d} files")
    print(f"    [XX] BLOCKED:  {verdicts['BLOCKED']:3d} files")
    if verdicts['ERROR'] > 0:
        print(f"    [??] ERROR:    {verdicts['ERROR']:3d} files")
    print()

    print(f"  TOTAL ISSUES: {total_issues}")
    print()

    if issues_by_category:
        print("  ISSUES BY CATEGORY (Brahim-Weighted):")
        # Sort by Brahim weight (most critical first)
        category_order = ['SECURITY', 'SYNTAX', 'MEMORY', 'LOGIC', 'PERFORMANCE',
                         'TYPE', 'ARCHITECTURE', 'CONCURRENCY', 'INTEGRATION', 'SYSTEM']

        for cat in category_order:
            if cat in issues_by_category:
                issues = issues_by_category[cat]
                weight = BrahimEngine.B(category_order.index(cat) + 1) if cat in category_order[:10] else 0
                print(f"    [{cat}] B({category_order.index(cat)+1})={weight}: {len(issues)} issues")

        # Any remaining categories
        for cat, issues in issues_by_category.items():
            if cat not in category_order:
                print(f"    [{cat}]: {len(issues)} issues")

    print()

    # Calculate overall resonance
    if results:
        avg_resonance = sum(r['resonance'] for r in results) / len(results)
        avg_alignment = sum(r['alignment'] for r in results) / len(results)
        print(f"  CODEBASE RESONANCE:")
        print(f"    Average Resonance: {avg_resonance:.6f}")
        print(f"    Genesis Target:    {BrahimEngine.GENESIS}")
        print(f"    Average Alignment: {avg_alignment:.6f}")

    print()
    print("=" * 70)

    # Show top issues to fix
    if total_issues > 0:
        print()
        print("  TOP ISSUES TO FIX (Priority Order):")
        print("-" * 70)

        # Flatten and prioritize issues
        all_issues = []
        for cat, issues in issues_by_category.items():
            for issue in issues:
                all_issues.append({**issue, 'category': cat})

        # Sort by category priority (SECURITY first)
        priority_map = {cat: i for i, cat in enumerate(category_order)}
        all_issues.sort(key=lambda x: priority_map.get(x['category'], 99))

        for i, issue in enumerate(all_issues[:15], 1):
            print(f"  {i:2d}. [{issue['category']}] {issue['file']}:{issue['line']}")
            print(f"      {issue['message']}")
            if issue['suggestion']:
                print(f"      -> {issue['suggestion']}")
            print()

    # Save report
    report = {
        'timestamp': datetime.now().isoformat(),
        'files_analyzed': len(kotlin_files),
        'total_issues': total_issues,
        'verdicts': verdicts,
        'issues_by_category': {k: len(v) for k, v in issues_by_category.items()},
        'avg_resonance': avg_resonance if results else 0,
        'genesis_target': BrahimEngine.GENESIS,
        'results': results
    }

    report_path = script_dir / 'buim_apk_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print(f"  Full report saved to: {report_path}")
    print()


if __name__ == "__main__":
    main()
