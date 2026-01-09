
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.getcwd())

from skills.synthesized.creative_ascii.skill import CreativeAsciiSkill
from skills.base import SkillContext

def test_skill():
    skill = CreativeAsciiSkill()
    context = SkillContext()
    
    print("--- Testing Text to ASCII ---")
    res = skill.execute({"action": "text_to_ascii", "text": "GPIA", "font": "slant"}, context)
    if res.success:
        print(res.output)
    else:
        print(f"Error: {res.error}")

    print("\n--- Testing Divider ---")
    res = skill.execute({"action": "create_divider", "style": "double", "width": 30}, context)
    if res.success:
        print(res.output)
    else:
        print(f"Error: {res.error}")

    print("\n--- Testing Fonts List ---")
    res = skill.execute({"action": "list_fonts"}, context)
    if res.success:
        fonts = res.output.get("fonts", [])
        print(f"Found {len(fonts)} fonts. First 5: {fonts[:5]}")
    else:
        print(f"Error: {res.error}")

if __name__ == "__main__":
    test_skill()
