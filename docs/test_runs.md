# Test Runs

This file is a historical log. Append new runs with timestamp, command, result, and notes.

## Run 2025-12-31T23:15:17
- Command: `python -m pytest -s`
- Result: timed out after ~307s (not all tests completed).
- Notes:
  - Pytest cache warning about permission denied.
  - Skill registration warnings emitted during run.

## Run 2026-01-01T15:36:28
- Command: `pytest tests/resonance_fidelity.py -q`
- Result: passed (3 tests).
- Notes:
  - Validates Temporal Formalism resonance gate stability checks.
