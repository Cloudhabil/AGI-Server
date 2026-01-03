# AST Safety Skill

## ID
safety/ast-safety

## Name
AST-Based Safety Verification

## Description
Implements AST-based safety patterns for code verification, vulnerability detection, and pre-generation filtering. Uses structural fingerprinting to prevent regeneration of known-bad patterns.

## Version
1.0.0

## Level
advanced

## Category
safety

## Capabilities
- fingerprint: Hash AST structures for pattern identification
- filter: Pre-generation filter to reject code matching known-bad AST hashes
- analyze: Vulnerability analysis using AST patterns (SQL injection, buffer overflow, etc.)
- classify: Classify code as Golden Snippet (verified) or Landmine (forbidden)
- log: Write-heavy logging for confidence-triggered retrieval

## Input Schema
```yaml
capability:
  type: string
  enum: [fingerprint, filter, analyze, classify, log]
  required: true
code:
  type: string
  description: Code to analyze or fingerprint
language:
  type: string
  enum: [python, javascript, typescript, go, rust]
  default: python
confidence_threshold:
  type: number
  description: Threshold for triggering analysis (0.0-1.0)
  default: 0.7
```

## Output Schema
```yaml
fingerprint:
  type: string
  description: AST hash of the code
classification:
  type: string
  enum: [golden_snippet, landmine, unknown]
vulnerabilities:
  type: array
  description: Detected vulnerability patterns
allowed:
  type: boolean
  description: Whether code passes pre-generation filter
```

## Model Routing
- L0 (fingerprint): codegemma - Fast AST parsing
- L1 (filter/classify): qwen3 - Pattern matching
- L2 (analyze): deepseek_r1 - Deep vulnerability analysis
- L3 (orchestrate): gpt_oss_20b - Multi-perspective synthesis

## References
- Singapore Consensus AI Safety Methods (2025)
- K-ASTRO: AST-based structural security
- Hyperon Neuro-Symbolic approach
