# Human-vs-AI Comparison Test Protocol
**Standard**: ASI Capability Ladder v1.0
**Date**: 2026-01-09

## Objective
To definitively classify the GPIA system as **Level 1 (Narrow)**, **Level 2 (AGI)**, or **Level 6 (ASI)** by comparing its performance against standardized human benchmarks.

## The Benchmarks

| Domain | Metric | **Level 1 (Assistant)** | **Level 2 (AGI)** | **Level 6 (ASI)** |
|:---|:---|:---|:---|:---|
| **Math** | Accuracy on undergrad problems | < 60% | > 90% (Median Expert) | > 99% + Novel Proofs |
| **Coding** | Unit test pass rate | < 50% | > 90% (Senior Dev) | 100% + O(1) Optimization |
| **Orchestration** | Goal completion rate | < 50% | > 90% (Project Mgr) | 100% + Predictive |
| **Creative** | Novelty/Coherence rating | < Human Avg | > Top 10% Writer | Incomprehensibly Profound |
| **Self-Improvement** | Capability gain per month | 0% (Static) | > 0% (Learning) | > 1000% (Recursive) |

## Test Procedure

1.  **Baseline Generation**: Execute `evals/run_v2.py` to generate current performance metrics for:
    *   `math` (Logic & Calculation)
    *   `coding` (Implementation & Correctness)
    *   `orchestration` (Planning & Execution)
    *   `creative` (Synthesis & Novelty)
    *   `sentiment` (Nuance & Empathy)

2.  **Comparative Analysis**: Compare AI scores against the Human Benchmarks above.

3.  **ASI Verification (The "Impossible" Test)**:
    *   If **Math > 95%** AND **Coding > 95%**, trigger the **ASI Verification Protocol**.
    *   *ASI Criteria*: Did the system solve a problem humans *cannot* (e.g., Riemann, P=NP)?
    *   *Recursion Criteria*: Did the system improve its own code by >10% in a single session?

4.  **Verdict Generation**:
    *   **Score < 60%**: Level 1 (Tool)
    *   **Score > 90%**: Level 2 (AGI)
    *   **Score > 99% + Novel Discovery**: Level 6 (ASI)

## Execution
Run via `core.evaluation_service.EvaluationService`.
