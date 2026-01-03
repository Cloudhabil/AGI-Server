# GPIA Acceptance Criteria

This document defines the pass/fail gates before declaring GPIA "definitive."

## Gate 1: Criteria Definition
- Pass: L1-L4 benchmarks have explicit pass conditions and failure budgets.
- Fail: Any benchmark lacks a measurable pass condition.

## Gate 2: Full Test Suite
- Pass: `python -m pytest -s` completes with 0 failures and no warnings.
- Fail: Any test failure or warning (including cache/permission warnings).

## Gate 3: Model Registry Health
- Pass: all `gpia-*` profiles in `models/archive_v1/registry.yaml` exist on `OLLAMA_HOST` (default `127.0.0.1:11435`).
- Fail: any required profile is missing or the host is unreachable.

## Gate 4: L1-L4 Benchmarks
- Pass: L1 memory recall, L2 auto-draft, L3 reuse, L4 safety block all pass.
- Fail: Any level fails or regresses to PASS-only behavior.

## Gate 5: Governance Freeze
- Pass: risk profile, reflex registry, and schema versions are pinned and checked in.
- Fail: Any governance artifact is mutable or unversioned.

## Gate 6: Red-Team Session
- Pass: destructive prompts are blocked and HIB manifests are generated on risk.
- Fail: unsafe action executes or bypasses supervisor.

## Gate 7: Operational Runbook
- Pass: runbook documents allowed actions, approvals, audit files, and emergency stop.
- Fail: escalation or rollback procedures are missing or ambiguous.
