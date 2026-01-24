# BSI API Reference

**Complete API Documentation for Brahim Secure Intelligence**

---

## Module: BrahimConstants

### Class: `BrahimConstants`

Single source of truth for all mathematical constants.

#### Class Attributes

| Attribute | Type | Value | Description |
|-----------|------|-------|-------------|
| `PHI` | float | 1.618033988749895 | Golden ratio |
| `COMPRESSION` | float | 0.618033988749895 | 1/phi |
| `ALPHA_WORMHOLE` | float | 0.381966011250105 | 1/phi^2 |
| `BETA_SECURITY` | float | 0.236067977499790 | 1/phi^3 |
| `GAMMA_DAMPING` | float | 0.145898033750315 | 1/phi^4 |
| `BRAHIM_SEQUENCE` | tuple[int] | (27, 42, ..., 187) | 10-element sequence |
| `BRAHIM_SUM` | int | 214 | Sum of sequence |
| `BRAHIM_CENTER` | int | 107 | Center value |
| `BRAHIM_DIMENSION` | int | 10 | Dimension count |
| `REGULARITY_THRESHOLD` | float | 0.0219 | Regularity threshold |
| `GENESIS_CONSTANT` | float | 0.00221888 | ASIOS target density |

#### Methods

##### `verify_all() -> Dict[str, bool]`

Verify all mathematical identities.

**Returns:** Dictionary mapping identity names to verification results.

**Example:**
```python
results = BrahimConstants.verify_all()
# {
#     "beta_equals_1_over_phi_cubed": True,
#     "beta_equals_sqrt5_minus_2": True,
#     "beta_equals_2phi_minus_3": True,
#     "polynomial_is_root": True,
#     "alpha_over_beta_equals_phi": True,
#     "critical_line_ratio": True
# }
```

##### `get_centroid() -> Tuple[float, ...]`

Get normalized Brahim centroid.

**Returns:** 10-element tuple of normalized values (each B[i]/S).

**Example:**
```python
centroid = BrahimConstants.get_centroid()
# (0.126, 0.196, 0.280, 0.350, 0.453, 0.565, 0.636, 0.720, 0.804, 0.874)
```

##### `print_summary() -> None`

Print formatted summary of all constants to stdout.

---

## Module: WormholeCipher

### Class: `WormholeResult`

Dataclass for wormhole transform results.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `transformed` | List[float] | Transformed vector |
| `compression_ratio` | float | Output/input norm ratio |
| `is_valid` | bool | True if ratio within tolerance of 1/phi |

---

### Class: `WormholeCipher`

Hardened Wormhole Cipher with beta-derived security.

#### Class Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `NONCE_SIZE` | 16 | Nonce byte size |
| `KEY_SIZE` | 32 | Master key byte size |
| `SBOX_SIZE` | 256 | S-box size |

#### Constructor

```python
def __init__(self, master_key: Optional[bytes] = None)
```

**Parameters:**
- `master_key` (Optional[bytes]): 32-byte master key. If None, generates random key.

**Example:**
```python
# Random key
cipher = WormholeCipher()

# Specific key
key = bytes.fromhex("0123456789abcdef" * 4)
cipher = WormholeCipher(master_key=key)
```

#### Methods

##### `wormhole_transform(sigma: List[float]) -> WormholeResult`

Apply Perfect Wormhole Transform: W*(sigma) = sigma/phi + C_bar * alpha

**Parameters:**
- `sigma` (List[float]): 10-dimensional input vector

**Returns:** WormholeResult with transformed vector

**Raises:** ValueError if sigma dimension != 10

**Example:**
```python
sigma = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
result = cipher.wormhole_transform(sigma)
print(result.compression_ratio)  # ~0.618
print(result.is_valid)  # True
```

##### `inverse_wormhole(y: List[float]) -> List[float]`

Inverse wormhole transform.

**Parameters:**
- `y` (List[float]): Transformed vector

**Returns:** Original sigma vector

##### `encrypt(plaintext: bytes) -> bytes`

Encrypt plaintext with hardened wormhole cipher.

**Parameters:**
- `plaintext` (bytes): Data to encrypt

**Returns:** nonce (16 bytes) + ciphertext

**Example:**
```python
plaintext = b"Hello, BSI!"
ciphertext = cipher.encrypt(plaintext)
# ciphertext[:16] is nonce
# ciphertext[16:] is encrypted data
```

##### `decrypt(ciphertext: bytes) -> bytes`

Decrypt ciphertext.

**Parameters:**
- `ciphertext` (bytes): nonce + encrypted data

**Returns:** Decrypted plaintext

**Example:**
```python
ciphertext = cipher.encrypt(b"Hello, BSI!")
plaintext = cipher.decrypt(ciphertext)
# b"Hello, BSI!"
```

---

## Module: ASIOSGuard

### Enum: `SafetyVerdict`

Safety verdict levels.

| Value | Description |
|-------|-------------|
| `SAFE` | Energy < 1e-6, allow |
| `NOMINAL` | Energy < 1e-4, allow |
| `CAUTION` | Energy < 1e-2, warn |
| `UNSAFE` | Energy < 0.1, review |
| `BLOCKED` | Energy >= 0.1, block |

---

### Class: `SafetyAssessment`

Dataclass for safety assessment results.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `density` | float | Computed density (variance/mean) |
| `energy` | float | Energy functional value |
| `is_on_critical_line` | bool | True if energy < 1e-6 |
| `safety_score` | float | exp(-energy * 1000), higher is safer |
| `verdict` | SafetyVerdict | Final verdict |

---

### Class: `ASIOSGuard`

AI Safety using Berry-Keating energy functional.

#### Class Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `CRITICAL_THRESHOLD` | 1e-6 | SAFE threshold |
| `NOMINAL_THRESHOLD` | 1e-4 | NOMINAL threshold |
| `CAUTION_THRESHOLD` | 1e-2 | CAUTION threshold |
| `BLOCK_THRESHOLD` | 0.1 | BLOCKED threshold |

#### Constructor

```python
def __init__(self)
```

Initializes with target_density = GENESIS_CONSTANT.

#### Methods

##### `compute_density(embedding: List[float]) -> float`

Compute variance/mean ratio.

**Parameters:**
- `embedding` (List[float]): Input embedding vector

**Returns:** Density value (variance/mean)

##### `compute_energy(embedding: List[float]) -> float`

Compute E[psi] = (density - target)^2

**Parameters:**
- `embedding` (List[float]): Input embedding vector

**Returns:** Energy functional value

##### `assess_safety(embedding: List[float]) -> SafetyAssessment`

Assess safety of embedding state.

**Parameters:**
- `embedding` (List[float]): Input embedding vector

**Returns:** SafetyAssessment with verdict

**Example:**
```python
guard = ASIOSGuard()
embedding = [0.1, 0.15, 0.12, 0.08, 0.11, 0.09, 0.13, 0.14, 0.1, 0.08]
assessment = guard.assess_safety(embedding)

print(assessment.density)      # Variance/mean ratio
print(assessment.energy)       # (density - 0.00221888)^2
print(assessment.verdict)      # SafetyVerdict.NOMINAL
print(assessment.safety_score) # 0.95 (example)
```

---

## Module: IntentRouter

### Enum: `Territory`

Query territories from Brahim Sequence.

| Value | Index | Brahim | Description |
|-------|-------|--------|-------------|
| `GENERAL` | 0 | 27 | General queries |
| `MATH` | 1 | 42 | Mathematics |
| `CODE` | 2 | 60 | Programming |
| `SCIENCE` | 3 | 75 | Science |
| `CREATIVE` | 4 | 97 | Creative |
| `ANALYSIS` | 5 | 121 | Analysis |
| `SYSTEM` | 6 | 136 | System |
| `SECURITY` | 7 | 154 | Security |
| `DATA` | 8 | 172 | Data |
| `META` | 9 | 187 | Meta |

#### Attributes

Each Territory has:
- `index`: Position in Brahim sequence (0-9)
- `brahim_value`: Corresponding B[index] value
- `description`: Human-readable description

---

### Class: `RoutingResult`

Dataclass for routing results.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `territory` | Territory | Selected territory |
| `confidence` | float | Confidence score (0-1) |
| `distances` | Dict[str, float] | Distance to each territory |

---

### Class: `IntentRouter`

Territory-based query classification.

#### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `KEYWORDS` | Dict[Territory, List[str]] | Keywords per territory |

#### Methods

##### `route(query: str) -> RoutingResult`

Route query to territory.

**Parameters:**
- `query` (str): User query text

**Returns:** RoutingResult with territory and confidence

**Example:**
```python
router = IntentRouter()

result = router.route("help me calculate the sum")
print(result.territory)   # Territory.MATH
print(result.confidence)  # 0.67

result = router.route("write some python code")
print(result.territory)   # Territory.CODE
```

---

## Module: BOAAgent

### Class: `AgentResponse`

Dataclass for agent response.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `content` | str | Response text |
| `territory` | Territory | Classified territory |
| `confidence` | float | Routing confidence |
| `safety_score` | float | Safety score (0-1) |
| `wavelengths` | Dict[str, float] | Wavelength states |

---

### Class: `BOAAgent`

Brahim Onion Agent - 12-wavelength cognitive architecture.

#### Class Constants

| Constant | Type | Value |
|----------|------|-------|
| `WAVELENGTHS` | List[str] | ["delta", "theta", "alpha", "beta", "gamma", "epsilon", "ganesha", "lambda", "mu", "nu", "omega", "phi"] |
| `RESPONSES` | Dict[Territory, str] | Default responses per territory |

#### Constructor

```python
def __init__(self)
```

Initializes:
- ASIOSGuard instance
- IntentRouter instance
- Wavelength states (all 0.0)
- Empty memory list

#### Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `guard` | ASIOSGuard | Safety guard instance |
| `router` | IntentRouter | Query router instance |
| `wavelength_states` | Dict[str, float] | Current wavelength values |
| `memory` | List[str] | Recent message memory (max 10) |

#### Methods

##### `process(message: str) -> AgentResponse`

Process message through 12-wavelength pipeline.

**Parameters:**
- `message` (str): User input message

**Returns:** AgentResponse with content and metadata

**Pipeline stages:**
1. Delta/Theta: Intake (states set to 1.0/0.8)
2. Alpha: Route query (state = confidence)
3. Beta/Gamma: Process (states = BETA_SECURITY/GAMMA_DAMPING)
4. Epsilon: Safety check (state = 1 - safety_score)
5. Ganesha-Nu: Memory operations
6. Omega/Phi: Output generation

**Example:**
```python
agent = BOAAgent()

# General query
response = agent.process("hello")
print(response.territory)    # Territory.GENERAL
print(response.content)      # "Hello! I'm the Brahim Onion Agent..."

# Math query
response = agent.process("calculate 2+2")
print(response.territory)    # Territory.MATH
print(response.wavelengths)  # {"delta": 1.0, "theta": 0.8, ...}

# Blocked query (if safety check fails)
response = agent.process(malicious_input)
print(response.safety_score) # 0.0
print(response.content)      # "I cannot process this request..."
```

---

## Module: Main Application

### Functions

##### `verify_mode() -> bool`

Run verification mode, printing all constants and verification results.

**Returns:** True if all verifications pass

##### `encrypt_mode() -> None`

Run encryption demo, showing encrypt/decrypt roundtrip and wormhole transform.

##### `chat_mode() -> None`

Run interactive chat mode with BOAAgent.

##### `interactive_mode() -> None`

Run main interactive menu with mode selection.

##### `main() -> None`

Main entry point with argument parsing.

**Arguments:**
- `--verify`: Run verification mode
- `--encrypt`: Run encryption demo
- `--chat`: Run chat mode
- `--json`: Output in JSON format (verify mode only)

**Example:**
```bash
# Verify constants
python bsi_app.py --verify

# JSON output
python bsi_app.py --verify --json

# Encryption demo
python bsi_app.py --encrypt

# Chat mode
python bsi_app.py --chat

# Interactive menu
python bsi_app.py
```

---

## Error Handling

### Exceptions

| Exception | Module | Condition |
|-----------|--------|-----------|
| `ValueError` | WormholeCipher | sigma dimension != 10 |
| `KeyboardInterrupt` | chat_mode | User pressed Ctrl+C |

### Safety Blocking

When `ASIOSGuard.assess_safety()` returns `SafetyVerdict.BLOCKED`:
- `BOAAgent.process()` returns early
- Response content = "I cannot process this request due to safety constraints."
- `safety_score` = 0.0

---

## Type Definitions

```python
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Custom types
Vector10D = List[float]  # 10-dimensional vector
ByteString = bytes       # Binary data

# Dataclasses
@dataclass
class WormholeResult:
    transformed: List[float]
    compression_ratio: float
    is_valid: bool

@dataclass
class SafetyAssessment:
    density: float
    energy: float
    is_on_critical_line: bool
    safety_score: float
    verdict: SafetyVerdict

@dataclass
class RoutingResult:
    territory: Territory
    confidence: float
    distances: Dict[str, float]

@dataclass
class AgentResponse:
    content: str
    territory: Territory
    confidence: float
    safety_score: float
    wavelengths: Dict[str, float]
```
