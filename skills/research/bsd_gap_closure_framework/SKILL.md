---
name: BSD Gap Closure Framework
description: Solutions-provider framework to generate computational evidence + explicit needs for Effective Descent, Q→Fp compatibility, and Sha estimation.
---

# BSD Gap Closure Framework (GPIA)

This skill is a **solutions-provider framework** for the three “missing links” you listed:

1. **Effective Descent / Search Engine Gap**: tries to find rational points (bounded search) and simple torsion structure signals (e.g., rational 2‑torsion).
2. **Local↔Global / Q→Fp Bridge Gap**: computes small‑prime reductions \(E(\mathbb{F}_p)\), \(a_p\), and reduces found \(\mathbb{Q}\)-points mod \(p\) when possible.
3. **“Ghost” Gap / \(|\Sha|\)**: given the missing BSD inputs, computes the *BSD‑predicted* \(|\Sha|\) and lists what’s missing when it can’t.

## What it is (and is not)

- It is **a workflow + evidence generator**, not a proof engine.
- It uses **pure Python** (plus optional SymPy helpers) so it runs in this repo without Sage/Pari/mwrank.
- For large cryptographic primes it intentionally **does not** try to count points (SEA/Schoof not implemented); it emits a “need”.

## Capability: `run`

Input (example):

```json
{
  "capability": "run",
  "curve": {"a": -1, "b": 0},
  "search": {"x_bound": 200, "u_bound": 200, "v_bound": 30, "torsion_order_max": 24},
  "primes": [101, 103, 10007],
  "sha_inputs": {
    "rank": 1,
    "l_star": "0.1234",
    "period": "3.14159",
    "regulator": "1.0",
    "tamagawa_product": "1",
    "torsion_order": 1
  },
  "write_report": true
}
```

## CLI helper

Run `python run_bsd_gap_closure_framework.py --help` for a simple command-line wrapper.
