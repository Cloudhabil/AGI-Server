import json
from pathlib import Path

def main():
    manifold_path = Path("substrate_manifold.html")
    content = manifold_path.read_text(encoding="utf-8")
    
    start_marker = '<data id="singularities" style="display:none;">'
    end_marker = '</data>'
    
    s_idx = content.find(start_marker)
    e_idx = content.find(end_marker, s_idx)
    
    json_str = content[s_idx + len(start_marker):e_idx].strip()
    singularities = json.loads(json_str)
    
    # Extract IDs only
    ids = [s['id'] for s in singularities]
    
    with open("skills.md", "w", encoding="utf-8") as f:
        f.write("# GPIA Logic Substrate Skills\n\n")
        for skill_id in sorted(ids):
            f.write(f"- {skill_id}\n")

if __name__ == "__main__":
    main()

