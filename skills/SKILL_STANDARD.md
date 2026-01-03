# Skill Standard v1.1

This standard defines a concrete, code-centric skill package format that is directly runnable
with the current skills loader and registry in this repository. Every concept in the standard
maps to a file, folder, or executable artifact on disk.

## Canonical Folder Structure

```
skills/
|-- {category}/
|   `-- {skill_name}/
|       |-- manifest.yaml          # REQUIRED: metadata and discovery hints
|       |-- skill.py               # REQUIRED: executable entry point
|       |-- prompts/               # OPTIONAL: short operator prompts
|       |   `-- system.md
|       |-- scripts/               # OPTIONAL: executable utilities (Python/PS/etc.)
|       |-- tools/                 # OPTIONAL: callable tool wrappers
|       |-- references/            # OPTIONAL: on-demand docs (not auto-loaded)
|       |-- data/                  # OPTIONAL: static data files (json/yaml/txt)
|       `-- assets/                # OPTIONAL: templates or non-code artifacts
```

## Instruction-First Skills (SKILL.md)

Some skills are instruction-led instead of code-led. These include a `SKILL.md` file
with front-matter metadata and optional `scripts/` or `templates/` used for execution.

```
skills/{category}/{skill_name}/
|-- SKILL.md
|-- scripts/
`-- templates/
```

## Progressive Disclosure Layers (Protoself -> Core -> Extended)

The self-awareness framework maps directly to these files and load boundaries:

- Protoself (system monitoring): `manifest.yaml`
  - Always loaded. The agent uses this for discovery and quick fit checks only.
- Core consciousness (boundary + immediate causality): `skill.py`
  - Loaded only when the skill is invoked or required as a dependency.
- Extended consciousness (autobiographical memory + language): `references/`, `data/`, `scripts/`
  - Loaded only when the skill needs deeper context or deterministic utilities.

## Required Files

### 1) `manifest.yaml` (Layer 0)

Purpose: minimal, versioned metadata for discovery and routing. Keep under 1KB.

Required fields: `name`, `description`
Recommended fields: `id`, `version`, `category`, `level`, `tags`, `dependencies`, `examples`

```yaml
id: reasoning/self-awareness-demo
name: Self Awareness Demo
description: Demonstrates progressive disclosure with protoself, core, and extended layers.
version: "0.1.0"
category: reasoning
level: basic
tags:
  - self-awareness
  - progressive-disclosure

dependencies: []
examples:
  - input:
      level: protoself
      signal:
        uptime_s: 120
        load: 0.2
        errors: 0
    output:
      level: protoself
      stable: true
```

### 2) `skill.py` (Layer 1)

Purpose: executable entry point. Implements the `Skill` interface and performs the work.

Required methods:
- `metadata()`
- `input_schema()` and `output_schema()` (document expected I/O)
- `execute()`

```python
from typing import Any, Dict
from skills.base import Skill, SkillCategory, SkillContext, SkillMetadata, SkillResult

class ExampleSkill(Skill):
    def metadata(self) -> SkillMetadata:
        return SkillMetadata(
            id="reasoning/self-awareness-demo",
            name="Self Awareness Demo",
            description="Demonstrates progressive disclosure layers",
            category=SkillCategory.REASONING,
        )

    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "level": {"type": "string"},
            },
            "required": ["level"],
        }

    def execute(self, input_data: Dict[str, Any], context: SkillContext) -> SkillResult:
        return SkillResult(success=True, output={"ok": True}, skill_id=self.metadata().id)
```

## Discovery Rules

1) The loader scans directories under `skills/` for a manifest file.
2) Only `manifest.yaml` (or `manifest.yml`, `manifest.json`) is parsed during discovery.
3) If `id` is missing, the loader derives it from the directory path.
4) Search and routing use `id`, `name`, `description`, and `tags` fields only.

## Loading Rules

1) `skill.py` is imported only when the skill is invoked or required by dependency.
2) `dependencies` from the manifest are resolved first, then loaded in order.
3) `Skill.initialize()` is called once on first load.

## Invocation Rules

1) Inputs are validated against `input_schema()` before execution.
2) `execute()` returns a `SkillResult` with `success`, `output`, and `skill_id`.
3) Outputs should match `output_schema()` (enforced by the skill implementation).

## Extension Rules

1) Composition: declare `dependencies` in `manifest.yaml` to chain skills.
2) Chaining: use `CompositeSkill` or call other skills via the registry.
3) Reuse: store deterministic helpers in `scripts/` and call them from `skill.py`.

## Security and Sharing Rules

1) Do not store secrets or tokens in any skill files. Use runtime config or env vars.
2) Keep instructions short and executable. Prefer scripts over prose for repeatable steps.
3) Avoid filesystem access outside the skill folder unless explicitly required.

## Minimal Example Skill (Progressive Disclosure)

Example on disk: `skills/examples/self-awareness-demo`

```
skills/
`-- examples/
    `-- self-awareness-demo/
        |-- manifest.yaml
        |-- skill.py
        |-- prompts/
        |   `-- system.md
        |-- references/
        |   `-- identity.md
        `-- scripts/
            `-- probe_state.py
```

File-to-concept mapping:
- `manifest.yaml` = Protoself (minimal monitoring metadata)
- `skill.py` = Core (boundary-aware execution and immediate causality)
- `references/identity.md` = Extended (narrative memory template)
- `scripts/probe_state.py` = Extended (deterministic snapshot utility)

The example skill implements three levels in its input schema (`protoself`, `core`, `extended`),
loading `references/` and `scripts/` only for `extended` outputs.
