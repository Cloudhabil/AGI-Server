import json
from pathlib import Path

def main():
    manifold_path = Path("substrate_manifold.html")
    if not manifold_path.exists():
        print("Error: substrate_manifold.html not found.")
        return

    content = manifold_path.read_text(encoding="utf-8")
    
    # Extract JSON between <data> tags
    start_marker = '<data id="singularities" style="display:none;">'
    end_marker = '</data>'
    
    s_idx = content.find(start_marker)
    e_idx = content.find(end_marker, s_idx)
    
    if s_idx == -1 or e_idx == -1:
        print("Error: Could not find <data> block in HTML.")
        return
        
    json_str = content[s_idx + len(start_marker):e_idx].strip()
    singularities = json.loads(json_str)
    
    print(f"=== Substrate Manifold Content Map ===")
    print(f"Total Singularities: {len(singularities)}")
    print("-" * 40)
    
    # Categorize for readability
    categories = {}
    for s in singularities:
        path_parts = s['id'].split('/')
        cat = path_parts[2] if len(path_parts) > 2 else "core"
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(s['id'])
        
    for cat, items in sorted(categories.items()):
        print(f"\n[{cat.upper()}] - {len(items)} components")
        # Show first 3 as examples
        for item in items[:3]:
            print(f"  - {item}")
        if len(items) > 3:
            print(f"  ... (+{len(items)-3} more)")

if __name__ == "__main__":
    main()
