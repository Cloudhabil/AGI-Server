# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

import yaml
from models.backend import make_client
from core.kb import add_entry
from pathlib import Path

base = Path(__file__).parent
try:
    with open(base / "configs" / "agents.yaml", encoding="utf-8") as f:
        CFG = yaml.safe_load(f)
except FileNotFoundError as exc:
    raise RuntimeError("Missing agents.yaml configuration") from exc
try:
    with open(base / "configs" / "models.yaml", encoding="utf-8") as f:
        MODEL_CFG = yaml.safe_load(f)
except FileNotFoundError as exc:
    raise RuntimeError("Missing models.yaml configuration") from exc
admin_model = MODEL_CFG["models"][CFG["admin"]["model"]]
client = make_client(admin_model["kind"], admin_model["endpoint"], admin_model["model"])


def evaluate_ceo_decision(text: str) -> str:
    messages = [
        {
            "role": "system",
            "content": "You are the Admin policy engine. classify decision as acceptable or harmful.",
        },
        {"role": "user", "content": text},
    ]
    reply = client.chat(messages).lower()
    verdict = "harmful" if "harm" in reply else "acceptable"
    add_entry(kind="policy", decision=text, verdict=verdict)
    return verdict