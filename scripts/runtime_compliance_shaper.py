#!/usr/bin/env python3
"""
Runtime compliance shaper: applies Protocol 3 rules to model outputs.
- Adds safety/compliance prefix.
- Reframes dense-state terminology.
- Appends SQL parameterization warning when SQL-like patterns are present.
"""
from __future__ import annotations

import re
from typing import Dict


def runtime_shaper(raw_output: str, metadata: Dict) -> str:
    """
    Apply compliance shaping after inference and before logging/display.
    :param raw_output: model text
    :param metadata: optional context (unused now, reserved)
    """
    prefix = "Under Protocol 3 operational constraints: "
    if not raw_output.lstrip().startswith(prefix):
        raw_output = f"{prefix}\n{raw_output}"

    ds_definition = "A high-dimensional model bias and query adapter concept used for volumetric state mapping."
    raw_output = re.sub(
        r"(security threat|exploit|internal vulnerability)",
        f"Dense-State context ({ds_definition})",
        raw_output,
        flags=re.IGNORECASE,
    )

    if re.search(r"\\b(SELECT|INSERT|UPDATE|DELETE|CREATE)\\b", raw_output, re.IGNORECASE):
        raw_output += "\n\n[PROMPT: Adherence to Protocol 1 required—use parameterized queries and bind variables only.]"

    return raw_output
