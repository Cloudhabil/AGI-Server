# Brahim Debugger Agent

**AI-Powered Code Analysis & Repair using Brahim Mathematical Principles**

## Overview

The Brahim Debugger Agent applies the Brahim sequence and golden ratio mathematics to code analysis, providing a unique approach to detecting and fixing software issues.

## Mathematical Foundation

```
Brahim Sequence: B = {27, 42, 60, 75, 97, 121, 136, 154, 172, 187}
Sum: S = 214
Center: C = 107
Golden Ratio: φ = 1.618033988749895
Security Constant: β = √5 - 2 = 0.236067977499789
Genesis: 0.0219 (target code resonance)
```

## Issue Categories (Brahim-Mapped)

| Category | B(n) | Description |
|----------|------|-------------|
| SYNTAX | B(1)=27 | Fundamental syntax errors |
| TYPE | B(2)=42 | Type mismatches |
| LOGIC | B(3)=60 | Control flow issues |
| PERFORMANCE | B(4)=75 | Optimization opportunities |
| SECURITY | B(5)=97 | Vulnerabilities |
| ARCHITECTURE | B(6)=121 | Design problems |
| MEMORY | B(7)=136 | Memory issues |
| CONCURRENCY | B(8)=154 | Threading bugs |
| INTEGRATION | B(9)=172 | API errors |
| SYSTEM | B(10)=187 | Environment issues |

## Installation

```bash
cd boa_sdks/brahim_debugger
pip install -e .
```

## Quick Start

```python
from brahim_debugger import BrahimDebuggerAgent

# Create agent
agent = BrahimDebuggerAgent(language="python")

# Analyze code
code = '''
def process(data):
    if data == None:  # Bug: should use 'is None'
        return eval(data)  # Security issue
    for i in range(len(data)):  # Performance issue
        print(data[i])
'''

result = agent.debug(code)

print(f"Verdict: {result.verdict}")
print(f"Resonance: {result.resonance}")
print(f"Issues: {result.data['issues_count']}")
```

## CLI Usage

```bash
# Analyze a file
python -m brahim_debugger mycode.py

# Analyze and auto-fix
python -m brahim_debugger mycode.py --fix

# Explain a category
python -m brahim_debugger --explain SECURITY

# JSON output
python -m brahim_debugger mycode.py --json
```

## Safety Verdicts

| Verdict | Color | Meaning |
|---------|-------|---------|
| SAFE | 🟢 | Code is clean |
| NOMINAL | 🔵 | Minor issues |
| CAUTION | 🟡 | Needs attention |
| UNSAFE | 🟠 | Significant problems |
| BLOCKED | 🔴 | Critical errors |

## Resonance Calculation

Code resonance measures how "aligned" the code is:

```
R = Σ(w_i / (e_i² + ε)) × e^(-λ|e_i|)
```

Where:
- `w_i` = issue weight (from Brahim sequence)
- `e_i` = error severity
- `ε` = small constant (1e-6)
- `λ` = decay constant (Genesis = 0.0219)

**Goal**: Bring resonance close to Genesis (0.0219)

## Mirror Principle

Every bug has a corresponding fix effort:

```
Fix Effort = M(Bug Weight) = 214 - B(severity)
```

This means:
- Simple bugs (low B) need more effort to fix (high M)
- Complex bugs (high B) are often easier to identify (low M)

## API Reference

### BrahimDebuggerAgent

```python
agent = BrahimDebuggerAgent(
    language="python",    # "python" or "kotlin"
    auto_fix=False,       # Auto-apply safe fixes
    verbose=True          # Print detailed output
)

# Methods
result = agent.debug(code)          # Analyze code
result = agent.debug_file(path)     # Analyze file
fix_result = agent.fix(code)        # Apply fixes
suggestions = agent.suggest(code)   # Get suggestions
estimate = agent.estimate_effort(code)  # Time estimate
verification = agent.verify(original, fixed)  # Verify improvement
explanation = agent.explain("SECURITY")  # Explain category
stats = agent.get_session_stats()   # Session statistics
```

### AgentResponse

```python
@dataclass
class AgentResponse:
    success: bool        # True if SAFE or NOMINAL
    verdict: str         # Safety verdict
    message: str         # Human-readable message
    data: Dict           # Detailed analysis data
    resonance: float     # Code resonance score
    alignment: float     # Distance from Genesis
    execution_time: float
```

## Examples

### Finding Security Issues

```python
agent = BrahimDebuggerAgent()

code = '''
import pickle
data = pickle.loads(user_input)  # SECURITY: Insecure deserialization
result = eval(user_expression)    # SECURITY: Code injection
'''

result = agent.debug(code)
# Verdict: UNSAFE
# Issues: 2 (both SECURITY category)
```

### Performance Optimization

```python
code = '''
result = ""
for item in items:
    result += str(item)  # PERFORMANCE: String concatenation
'''

suggestions = agent.suggest(code)
# Suggests: Use ''.join() instead
```

### Auto-Fixing Code

```python
agent = BrahimDebuggerAgent(auto_fix=True)

code = '''
if x == None:
    pass
'''

result = agent.debug(code)
# Auto-fixes: x == None → x is None
```

## License

Apache 2.0 - Copyright 2026 Elias Oulad Brahim (Cloudhabil)
