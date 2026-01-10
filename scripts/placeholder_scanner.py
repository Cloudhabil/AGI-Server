#!/usr/bin/env python3
"""
Placeholder Scanner Agent
=========================

Scans the repository for placeholders and uses GPIA to populate them.

Usage:
    # Scan entire repo for placeholders
    python placeholder_scanner.py scan

    # Scan specific paths
    python placeholder_scanner.py scan --paths skills/ configs/

    # Analyze and suggest fixes
    python placeholder_scanner.py populate

    # Generate report
    python placeholder_scanner.py report

    # Apply fixes (with confirmation)
    python placeholder_scanner.py fix

    # Interactive mode with GPIA
    python placeholder_scanner.py interactive
"""
# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))


import argparse
import json
import sys
from pathlib import Path

# Ensure UTF-8 output
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from skills.system.placeholder_scanner.skill import PlaceholderScannerSkill
from skills.base import SkillContext


def print_header():
    """Print agent header."""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              Placeholder Scanner Agent                         ║
║         Powered by GPIA with PASS Protocol                     ║
╚═══════════════════════════════════════════════════════════════╝
""")


def cmd_scan(args):
    """Scan for placeholders."""
    print("[Scanner] Scanning repository for placeholders...")

    skill = PlaceholderScannerSkill()
    result = skill.execute({
        "capability": "scan",
        "paths": args.paths or ["."],
        "exclude_patterns": args.exclude or [],
    }, SkillContext())

    if result.success:
        output = result.output
        summary = output.get("summary", {})

        print(f"\n[Results] Found {summary.get('total_found', 0)} placeholders in {summary.get('files_scanned', 0)} files")

        print("\n[By Pattern]")
        for pattern, count in sorted(output.get("summary", {}).get("by_pattern", {}).items(), key=lambda x: -x[1]):
            print(f"  {pattern}: {count}")

        if args.verbose:
            print("\n[Details]")
            for p in output.get("placeholders", [])[:20]:
                print(f"  {p['file']}:{p['line']} ({p['pattern']})")
                print(f"    {p['line_content'][:80]}")

        if summary.get('total_found', 0) > 20:
            print(f"\n  ... and {summary.get('total_found', 0) - 20} more (use --verbose for full list)")
    else:
        print(f"[Error] {result.error}")

    return result


def cmd_populate(args):
    """Find and populate placeholders with GPIA."""
    print("[Scanner] Analyzing placeholders and generating fixes with GPIA...")

    skill = PlaceholderScannerSkill()
    result = skill.execute({
        "capability": "populate",
        "paths": args.paths or ["."],
        "dry_run": not args.apply,
    }, SkillContext())

    if result.success:
        output = result.output
        populated = output.get("populated", [])

        print(f"\n[Results] Analyzed {len(populated)} placeholders")

        for item in populated:
            status = item.get("status", "unknown")
            icon = "✓" if status == "generated" else "⊘" if status == "skipped" else "?"

            print(f"\n{icon} {item['file']}:{item['line']}")

            if status == "skipped":
                print(f"   Skipped: {item.get('reason', 'Unknown reason')}")
            elif status == "generated":
                print(f"   Original: {item.get('original', '')[:60]}")
                print(f"   Suggested: {item.get('suggested_fix', '')[:100]}")
                print(f"   Confidence: {item.get('confidence', 0):.1%}")

        if output.get("dry_run"):
            print("\n[Dry Run] No changes applied. Use --apply to apply fixes.")
    else:
        print(f"[Error] {result.error}")

    return result


def cmd_report(args):
    """Generate a report of all placeholders."""
    print("[Scanner] Generating placeholder report...")

    skill = PlaceholderScannerSkill()
    result = skill.execute({
        "capability": "report",
        "paths": args.paths or ["."],
    }, SkillContext())

    if result.success:
        output = result.output

        print(f"\n[Report] Saved to: {output.get('report_path')}")
        print(f"[Total] {output.get('total_placeholders', 0)} placeholders found")

        if args.verbose:
            print("\n" + "=" * 60)
            print(output.get("report", ""))
    else:
        print(f"[Error] {result.error}")

    return result


def cmd_fix(args):
    """Apply fixes to placeholders."""
    if not args.force:
        print("[Warning] This will modify files in your repository.")
        confirm = input("Are you sure you want to proceed? [y/N] ")
        if confirm.lower() != 'y':
            print("[Cancelled] No changes made.")
            return

    print("[Scanner] Applying fixes...")

    skill = PlaceholderScannerSkill()

    # First populate
    skill.execute({
        "capability": "populate",
        "paths": args.paths or ["."],
        "dry_run": False,
    }, SkillContext())

    # Then fix
    result = skill.execute({
        "capability": "fix",
        "dry_run": False,
    }, SkillContext())

    if result.success:
        output = result.output
        print(f"\n[Results] {output.get('message', '')}")

        if output.get("errors"):
            print("\n[Errors]")
            for err in output.get("errors", []):
                print(f"  - {err}")
    else:
        print(f"[Error] {result.error}")

    return result


def cmd_interactive(args):
    """Interactive mode with GPIA."""
    print_header()

    try:
        from gpia import GPIA
        agent = GPIA(verbose=True)
    except ImportError:
        print("[Error] GPIA not available. Please check your installation.")
        return

    skill = PlaceholderScannerSkill()

    print("""
Commands:
  /scan [paths]     - Scan for placeholders
  /populate         - Generate fixes with GPIA
  /report           - Generate report
  /fix              - Apply fixes
  /status           - Show GPIA status
  /quit             - Exit

Or ask GPIA anything about placeholders in natural language.
""")

    while True:
        try:
            user_input = input("\n[You] > ").strip()

            if not user_input:
                continue

            if user_input == "/quit":
                print("Goodbye!")
                break

            if user_input.startswith("/scan"):
                paths = user_input.split()[1:] or ["."]
                result = skill.execute({
                    "capability": "scan",
                    "paths": paths,
                }, SkillContext())

                if result.success:
                    summary = result.output.get("summary", {})
                    print(f"\n[Found] {summary.get('total_found', 0)} placeholders")
                    for p, c in summary.get("by_pattern", {}).items():
                        print(f"  {p}: {c}")
                continue

            if user_input == "/populate":
                result = skill.execute({
                    "capability": "populate",
                    "dry_run": True,
                }, SkillContext())

                if result.success:
                    for item in result.output.get("populated", [])[:5]:
                        print(f"\n{item['file']}:{item['line']}")
                        print(f"  {item.get('suggested_fix', '')[:100]}")
                continue

            if user_input == "/report":
                result = skill.execute({
                    "capability": "report",
                }, SkillContext())

                if result.success:
                    print(f"\n[Report] Saved to: {result.output.get('report_path')}")
                continue

            if user_input == "/fix":
                confirm = input("Apply fixes? [y/N] ")
                if confirm.lower() == 'y':
                    result = skill.execute({
                        "capability": "fix",
                        "dry_run": False,
                    }, SkillContext())
                    print(result.output.get("message", ""))
                continue

            if user_input == "/status":
                status = agent.status()
                print(f"\n[GPIA Status]")
                print(f"  Skills: {status.get('skills_loaded', 0)}")
                print(f"  Tasks: {status.get('task_count', 0)}")
                print(f"  Passes: {status.get('total_passes', 0)}")
                continue

            # Natural language query to GPIA
            task = f"""Analyze placeholders in this repository and help with: {user_input}

Context: I'm using the Placeholder Scanner skill which can:
- scan: Find placeholders (TODO, FIXME, stubs, empty configs)
- populate: Generate fixes using LLMs
- fix: Apply the fixes

Please help with the user's request about placeholders."""

            result = agent.run(task)
            print(f"\n[GPIA] {result.response}")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[Error] {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Placeholder Scanner Agent - Find and populate placeholders with GPIA"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Scan command
    scan_parser = subparsers.add_parser("scan", help="Scan for placeholders")
    scan_parser.add_argument("--paths", nargs="+", help="Paths to scan")
    scan_parser.add_argument("--exclude", nargs="+", help="Patterns to exclude")
    scan_parser.add_argument("-v", "--verbose", action="store_true", help="Show details")

    # Populate command
    populate_parser = subparsers.add_parser("populate", help="Generate fixes with GPIA")
    populate_parser.add_argument("--paths", nargs="+", help="Paths to scan")
    populate_parser.add_argument("--apply", action="store_true", help="Apply fixes")

    # Report command
    report_parser = subparsers.add_parser("report", help="Generate report")
    report_parser.add_argument("--paths", nargs="+", help="Paths to scan")
    report_parser.add_argument("-v", "--verbose", action="store_true", help="Print report")

    # Fix command
    fix_parser = subparsers.add_parser("fix", help="Apply fixes")
    fix_parser.add_argument("--paths", nargs="+", help="Paths to scan")
    fix_parser.add_argument("--force", action="store_true", help="Skip confirmation")

    # Interactive command
    interactive_parser = subparsers.add_parser("interactive", help="Interactive mode")

    args = parser.parse_args()

    if args.command is None:
        # Default to interactive mode
        print_header()
        cmd_interactive(args)
    elif args.command == "scan":
        cmd_scan(args)
    elif args.command == "populate":
        cmd_populate(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "fix":
        cmd_fix(args)
    elif args.command == "interactive":
        print_header()
        cmd_interactive(args)


if __name__ == "__main__":
    main()