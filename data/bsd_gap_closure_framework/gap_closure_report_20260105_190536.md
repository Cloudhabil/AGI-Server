# BSD Gap Closure Framework Report

- Generated: 2026-01-05T19:05:36.954115Z
- Curve: {'a': -1, 'b': 0}

## Gap 1 — Effective Descent (bounded search)
```json
{
  "status": "ok",
  "discriminant": 64,
  "rational_2_torsion_points": [
    {
      "x": "0",
      "y": "0"
    }
  ],
  "points_found": [
    {
      "x": "-1",
      "y": "0",
      "small_order": 2
    },
    {
      "x": "0",
      "y": "0",
      "small_order": 2
    },
    {
      "x": "1",
      "y": "0",
      "small_order": 2
    }
  ],
  "search_params": {
    "x_bound": 20,
    "u_bound": 20,
    "v_bound": 10,
    "torsion_order_max": 12
  },
  "notes": [
    "Point search is bounded/heuristic; absence of points is not evidence of rank 0.",
    "Small-order detection is a quick filter; it does not prove torsion structure."
  ]
}
```

## Gap 2 — Q → F_p bridge (small primes)
```json
{
  "status": "ok",
  "max_naive_prime": 20000,
  "primes": [
    {
      "p": 101,
      "status": "good_reduction",
      "#E(F_p)": 104,
      "a_p": -2,
      "factorization": {
        "2": 3,
        "13": 1
      }
    },
    {
      "p": 103,
      "status": "good_reduction",
      "#E(F_p)": 104,
      "a_p": 0,
      "factorization": {
        "2": 3,
        "13": 1
      }
    },
    {
      "p": 101,
      "reduced_Q_points": [
        {
          "x": 0,
          "y": 0
        },
        {
          "x": 100,
          "y": 0
        },
        {
          "x": 1,
          "y": 0
        }
      ]
    },
    {
      "p": 103,
      "reduced_Q_points": [
        {
          "x": 0,
          "y": 0
        },
        {
          "x": 102,
          "y": 0
        },
        {
          "x": 1,
          "y": 0
        }
      ]
    }
  ],
  "notes": [
    "Naive point counting is O(p); suitable only for small primes.",
    "For cryptographic primes, integrate SEA/Schoof backends (not shipped here)."
  ]
}
```

## Gap 3 — |Sha| (BSD-predicted estimate)
```json
{
  "status": "no_inputs",
  "reason": "Provide sha_inputs={...} to estimate |Sha|"
}
```

## Needs / Next Steps
```json
[]
```

## Notes
- This report is computational/operational scaffolding; it does not constitute a mathematical proof.
