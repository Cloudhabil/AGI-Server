import sys
from pathlib import Path
import os

# Add src to sys.path
root = Path(os.getcwd())
src_path = root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

from skills.loader import SkillLoader
from skills.registry import get_registry

def main():
    loader = SkillLoader()
    # Add root skills dir if it exists
    skills_dir = root / "skills"
    if skills_dir.exists():
        loader.add_base_dir(skills_dir)
    
    count = loader.scan_all(lazy=True)
    print(f"Total skills discovered by loader: {count}")
    
    registry = get_registry()
    stats = registry.get_stats()
    print(f"Registry stats: {stats}")

if __name__ == "__main__":
    main()
