"""IIAS Badges - Track application completion status"""

import json
from pathlib import Path
from datetime import datetime

BADGES = {
    "core": "🔷",      # Foundation
    "cloud": "☁️",     # Infrastructure
    "edge": "📱",      # Edge/Local
    "ai": "🧠",        # AI/ML
    "security": "🔒",  # Security
    "comm": "📡",      # Communication
    "data": "💾",      # Data/Storage
    "business": "💼",  # Business
    "dev": "🛠️",       # Developer
    "science": "🔬",   # Scientific
    "iot": "📟",       # IoT
    "personal": "👤",  # Personal
    "finance": "💰",   # Finance
}

STATUS_ICONS = {
    "done": "✅",
    "pending": "⏳",
    "building": "🔨",
    "error": "❌",
}


class BadgeTracker:
    def __init__(self, apps_file: str = None):
        if apps_file is None:
            apps_file = Path(__file__).parent / "applications.json"
        self.apps_file = Path(apps_file)
        self.load()

    def load(self):
        if self.apps_file.exists():
            with open(self.apps_file) as f:
                self.data = json.load(f)
        else:
            self.data = {"categories": {}}

    def save(self):
        with open(self.apps_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def mark_done(self, app_name: str):
        for cat, info in self.data["categories"].items():
            for app in info["apps"]:
                if app["name"] == app_name:
                    app["status"] = "done"
                    app["completed_at"] = datetime.now().isoformat()
                    self.save()
                    return True
        return False

    def mark_building(self, app_name: str):
        for cat, info in self.data["categories"].items():
            for app in info["apps"]:
                if app["name"] == app_name:
                    app["status"] = "building"
                    self.save()
                    return True
        return False

    def get_status(self) -> dict:
        result = {"total": 0, "done": 0, "pending": 0, "building": 0}
        for cat, info in self.data["categories"].items():
            for app in info["apps"]:
                result["total"] += 1
                result[app["status"]] = result.get(app["status"], 0) + 1
        return result

    def generate_readme_badges(self) -> str:
        lines = ["# IIAS Applications Status\n"]
        status = self.get_status()
        pct = (status["done"] / status["total"] * 100) if status["total"] > 0 else 0

        lines.append(f"**Progress: {status['done']}/{status['total']} ({pct:.1f}%)**\n")
        lines.append(f"- ✅ Done: {status['done']}")
        lines.append(f"- 🔨 Building: {status.get('building', 0)}")
        lines.append(f"- ⏳ Pending: {status['pending']}\n")

        for cat, info in self.data["categories"].items():
            badge = BADGES.get(info["apps"][0]["badge"], "⚪")
            done = sum(1 for a in info["apps"] if a["status"] == "done")
            lines.append(f"\n## {badge} {cat.upper()} ({done}/{info['count']})")
            for app in info["apps"]:
                icon = STATUS_ICONS.get(app["status"], "⏳")
                lines.append(f"- {icon} {app['name']}")

        return "\n".join(lines)


if __name__ == "__main__":
    tracker = BadgeTracker()
    print(tracker.generate_readme_badges())
