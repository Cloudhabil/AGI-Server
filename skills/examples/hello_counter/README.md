# Hello Counter Skill

Minimal example skill implementing progressive disclosure. Only `skill.yaml` and `VERSION` are read at discovery. Code is imported on invocation.

Usage:
- Input schema: `{ "base": number, "increment": number }`
- Output schema: `{ "result": number }`
- Entry point: `handlers.run:main`
