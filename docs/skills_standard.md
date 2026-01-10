# Skill Module Standard (Repo + Codex)

This standard defines the expected layout for skills in this repository. Code-first skills use `manifest.yaml` and `skill.py`, while instruction-first skills include a `SKILL.md` with optional scripts.

## Canonical Structure (Code Skills)

- `manifest.yaml`: Required metadata (id, name, description, category, inputs/outputs).
- `schema.json`: Optional input/output schema for validation.
- `skill.py`: Python implementation entry point.
- `README.md`: Optional usage notes.
- `assets/`: Optional static files.

Example tree:

```
src/skills/<category>/<skill_name>/
  manifest.yaml
  schema.json
  skill.py
  README.md
  assets/
```

## Instruction-First Skills (Codex style)

Some skills are instruction-led and ship as a `SKILL.md` with supporting scripts:

```
src/skills/<category>/<skill_name>/
  SKILL.md
  scripts/
  templates/
```

## Discovery, Load, Invoke

- Discover: scan for `manifest.yaml` and `SKILL.md` entries.
- Load: cache metadata from manifests and SKILL.md front-matter.
- Invoke: import `skill.py` for code skills or execute scripts for instruction skills.

## Minimal Example

See `src/skills/examples/hello_counter` for a working code skill template.
