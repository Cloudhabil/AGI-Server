"""Quick summary of Gardener organization results"""
import json
from pathlib import Path
from collections import Counter

ledger_file = Path("data/ledger/gardener.jsonl")

if not ledger_file.exists():
    print("No ledger file found")
    exit(1)

# Read all entries
entries = []
with open(ledger_file, 'r', encoding='utf-8') as f:
    for line in f:
        entries.append(json.loads(line))

# Filter out venv entries
project_entries = [e for e in entries if 'venv' not in e['artifact_path']]

# Count by classification
classifications = Counter(e['classification'] for e in project_entries)

# Count actually moved files
moved = [e for e in project_entries if e['source_path'] != e['destination_path']]

print("=" * 80)
print("FILESYSTEM GARDENER - ORGANIZATION SUMMARY")
print("=" * 80)
print(f"\nTotal entries processed: {len(project_entries)}")
print(f"Files actually organized: {len(moved)}")
print(f"Files left in place (low confidence): {len(project_entries) - len(moved)}")

print("\nClassification Breakdown:")
for classification, count in sorted(classifications.items(), key=lambda x: -x[1]):
    print(f"  {classification}: {count}")

print("\nSample Organized Files:")
for entry in moved[:15]:
    src = Path(entry['source_path']).name
    dest = entry['classification']
    conf = entry['confidence']
    print(f"  {src:<40} -> {dest:<30} ({conf:.2f})")

print("\n" + "=" * 80)
