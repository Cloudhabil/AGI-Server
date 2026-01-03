from pathlib import Path
import re

p = Path("CLI/ch_repl.py")
src = p.read_text(encoding="utf-8")

# Fix 1: message when there is no code block
pat1 = re.compile(
    r"if\s+not\s+code:\s*\n\s*console\.print\(\s*\n\s*f\"\[yellow\]\{TEXTS\.get\('no_code_block',\s*'No encontr\\u00e9 bloque ```python``` en el \\u00faltimo output\.'\)\}\[/yellow\]\"\)\s*",
    flags=re.M,
)
rep1 = (
    "if not code:\n"
    "        msg = TEXTS.get('no_code_block', 'No encontré bloque ```python``` en el último output.')\n"
    '        console.print(f"[yellow]{msg}[/yellow]")\n'
)
src, n1 = pat1.subn(rep1, src)

# Fix 2: exec running label with U+25B6
pat2 = re.compile(
    r"console\.print\(\s*f\"\[bold\]\{TEXTS\.get\('exec_running',\s*'\\u25B6 Ejecutando'\)\}\[/bold\]\s*\{\s*script\s*\}\)\s*"
)
rep2 = (
    "exec_label = TEXTS.get('exec_running', '▶ Ejecutando')\n"
    '        console.print(f"[bold]{exec_label}[/bold] {script}")\n'
)
src, n2 = pat2.subn(rep2, src)

if n1 == 0 or n2 == 0:
    print(f"[warn] expected patterns not fully matched: pat1={n1}, pat2={n2}")

p.write_text(src, encoding="utf-8")
print(f"[ok] patched {p}  (pat1={n1}, pat2={n2})")
