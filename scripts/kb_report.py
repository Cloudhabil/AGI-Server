# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from datetime import datetime
from pathlib import Path
from core.kb import search
from integrations.drive_client import upload_file
from core.kb import add_entry
import os

SECTIONS = {
    "Finance": "CFO",
    "Ops/HR": "COO CHRO",
    "Technology": "CTO CIO CPO",
    "Marketing/Product": "CMO CPO",
    "Policy/Admin": "policy memo",
}


def build_report():
    week = datetime.utcnow().strftime("%Y-%W")
    content = [f"# Weekly Report {week}\n"]
    for title, keys in SECTIONS.items():
        content.append(f"## {title}\n")
        for key in keys.split():
            results = search(key)
            for r in results:
                content.append(f"- {r['data']}")
        content.append("")
    path = Path("reports") / f"{week}.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(content), encoding="utf-8")
    if os.environ.get("GDRIVE_PARENT_FOLDER_ID"):
        file_id = upload_file(str(path), os.environ["GDRIVE_PARENT_FOLDER_ID"], path.name)
        add_entry(kind="report", file_id=file_id, path=str(path))
    return path


if __name__ == "__main__":
    build_report()