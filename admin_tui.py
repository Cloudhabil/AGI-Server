from typing import Callable
from rich.console import Console
from core.kb import last, search, add_entry, summarize_entry
from ui.ui_texts import load_texts


def main(
    route: Callable[[str, str, str], None],
    check_ceo: Callable[[str], str],
    lang: str = "en",
):
    texts = load_texts(lang)
    console = Console()
    while True:
        try:
            line = console.input(texts.get("prompt", "admin> "))
        except (EOFError, KeyboardInterrupt):
            break
        if not line.strip():
            continue
        if line.startswith("chat "):
            _, rest = line.split(" ", 1)
            agent, msg = rest.split("::", 1)
            route("admin", agent.strip(), msg.strip())
        elif line.startswith("check "):
            _, rest = line.split(" ", 1)
            agent, msg = rest.split("::", 1)
            if agent.strip().upper() == "CEO":
                verdict = check_ceo(msg.strip())
                console.print(f"{texts.get('policy', 'policy')}: {verdict}")
        elif line.startswith("kb last"):
            parts = line.split("::")
            n = int(parts[1]) if len(parts) > 1 else 5
            for entry in last(n):
                summary = summarize_entry(entry, lambda t: " ".join(t.split()[:40]))
                console.print({**entry, "summary": summary})
        elif line.startswith("kb search"):
            _, query = line.split("::", 1)
            for entry in search(query.strip()):
                summary = summarize_entry(entry, lambda t: " ".join(t.split()[:40]))
                console.print({**entry, "summary": summary})
        elif line.startswith("kb memo"):
            _, rest = line.split("::", 1)
            topic, text = rest.split("||", 1)
            add_entry(kind="memo", topic=topic.strip(), text=text.strip())
        else:
            console.print(texts.get("unknown_command", "unknown command"))
