# BSI Integration Guide

**Integrating Brahim Secure Intelligence into Your Projects**

---

## Quick Start

### Python Integration

```python
# Import all modules
from bsi_app import (
    BrahimConstants,
    WormholeCipher,
    ASIOSGuard,
    IntentRouter,
    BOAAgent
)

# Verify setup
results = BrahimConstants.verify_all()
assert all(results.values()), "Constant verification failed"
```

### Kotlin/Android Integration

```kotlin
import com.brahim.bsi.core.BrahimConstants
import com.brahim.bsi.cipher.WormholeCipher
import com.brahim.bsi.safety.ASIOSGuard
import com.brahim.bsi.router.IntentRouter
import com.brahim.bsi.agent.BOAAgent

// Verify setup
val verified = BrahimConstants.verify()
require(verified) { "Constant verification failed" }
```

---

## Integration Patterns

### Pattern 1: Secure Messaging

Encrypt messages with Wormhole Cipher before transmission.

**Python:**
```python
class SecureMessenger:
    def __init__(self, shared_key: bytes):
        self.cipher = WormholeCipher(master_key=shared_key)

    def send(self, message: str) -> bytes:
        return self.cipher.encrypt(message.encode('utf-8'))

    def receive(self, encrypted: bytes) -> str:
        return self.cipher.decrypt(encrypted).decode('utf-8')

# Usage
key = bytes.fromhex("0123456789abcdef" * 4)  # 32 bytes
messenger = SecureMessenger(key)

encrypted = messenger.send("Secret message")
plaintext = messenger.receive(encrypted)
```

**Kotlin:**
```kotlin
class SecureMessenger(sharedKey: ByteArray) {
    private val cipher = WormholeCipher(sharedKey)

    fun send(message: String): ByteArray {
        return cipher.encrypt(message.toByteArray())
    }

    fun receive(encrypted: ByteArray): String {
        return String(cipher.decrypt(encrypted))
    }
}
```

---

### Pattern 2: AI Safety Gateway

Filter all AI responses through ASIOS before display.

**Python:**
```python
class SafeAIGateway:
    def __init__(self):
        self.guard = ASIOSGuard()

    def embed_text(self, text: str) -> list:
        """Convert text to embedding (simplified)."""
        return [ord(c) / 255 for c in text[:10].ljust(10)]

    def is_safe(self, response: str) -> bool:
        embedding = self.embed_text(response)
        assessment = self.guard.assess_safety(embedding)
        return assessment.verdict.value in ["SAFE", "NOMINAL"]

    def filter(self, response: str) -> str:
        if self.is_safe(response):
            return response
        return "[Response filtered for safety]"

# Usage
gateway = SafeAIGateway()

# Safe response
print(gateway.filter("Hello, how can I help?"))

# Potentially unsafe response (would be checked)
print(gateway.filter(ai_response))
```

**Kotlin:**
```kotlin
class SafeAIGateway {
    private val guard = ASIOSGuard()

    private fun embedText(text: String): FloatArray {
        return text.take(10).padEnd(10, ' ')
            .map { it.code / 255f }
            .toFloatArray()
    }

    fun isSafe(response: String): Boolean {
        val embedding = embedText(response)
        val assessment = guard.assessSafety(embedding)
        return assessment.verdict in listOf(SafetyVerdict.SAFE, SafetyVerdict.NOMINAL)
    }

    fun filter(response: String): String {
        return if (isSafe(response)) response else "[Response filtered for safety]"
    }
}
```

---

### Pattern 3: Query Routing Service

Route user queries to appropriate handlers.

**Python:**
```python
class QueryService:
    def __init__(self):
        self.router = IntentRouter()
        self.handlers = {
            Territory.MATH: self.handle_math,
            Territory.CODE: self.handle_code,
            Territory.SECURITY: self.handle_security,
            # ... other handlers
        }

    def handle_math(self, query: str) -> str:
        return f"Math handler: {query}"

    def handle_code(self, query: str) -> str:
        return f"Code handler: {query}"

    def handle_security(self, query: str) -> str:
        return f"Security handler: {query}"

    def process(self, query: str) -> str:
        result = self.router.route(query)
        handler = self.handlers.get(result.territory, self.default_handler)
        return handler(query)

    def default_handler(self, query: str) -> str:
        return f"General handler: {query}"

# Usage
service = QueryService()
print(service.process("help me calculate 2+2"))  # Math handler
print(service.process("write a function"))       # Code handler
```

---

### Pattern 4: Complete Agent Integration

Full BOA agent with custom response generation.

**Python:**
```python
class CustomBOAAgent(BOAAgent):
    def __init__(self, llm_callback=None):
        super().__init__()
        self.llm_callback = llm_callback

    def generate_response(self, message: str, territory: Territory) -> str:
        """Override to use custom LLM."""
        if self.llm_callback:
            return self.llm_callback(message, territory)
        return super().RESPONSES.get(territory, "I can help with that.")

    def process(self, message: str) -> AgentResponse:
        # Run parent pipeline for safety/routing
        response = super().process(message)

        # Replace content with custom generation
        if response.safety_score > 0:  # Not blocked
            response.content = self.generate_response(message, response.territory)

        return response

# Usage with custom LLM
def my_llm(message: str, territory: Territory) -> str:
    # Call your LLM API here
    return f"LLM response for {territory.name}: ..."

agent = CustomBOAAgent(llm_callback=my_llm)
response = agent.process("Explain quantum computing")
```

---

## Wormhole Transform for Embeddings

Use wormhole transform to compress high-dimensional embeddings.

**Python:**
```python
class EmbeddingCompressor:
    def __init__(self):
        self.cipher = WormholeCipher()

    def compress(self, embedding: list) -> list:
        """Compress embedding using wormhole transform."""
        # Pad or truncate to 10 dimensions
        if len(embedding) > 10:
            # Take first 10 for wormhole
            sigma = embedding[:10]
            remainder = embedding[10:]
        else:
            sigma = embedding + [0.0] * (10 - len(embedding))
            remainder = []

        result = self.cipher.wormhole_transform(sigma)
        return result.transformed + remainder

    def decompress(self, compressed: list) -> list:
        """Decompress using inverse wormhole."""
        sigma = compressed[:10]
        remainder = compressed[10:]

        original = self.cipher.inverse_wormhole(sigma)
        return original + remainder

# Usage
compressor = EmbeddingCompressor()

# Original 10D embedding
original = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
compressed = compressor.compress(original)
restored = compressor.decompress(compressed)

print(f"Compression ratio: {sum(x**2 for x in compressed)**0.5 / sum(x**2 for x in original)**0.5:.4f}")
# Expected: ~0.618 (1/phi)
```

---

## Safety Thresholds Configuration

Adjust safety thresholds for different use cases.

**Python:**
```python
class ConfigurableASIOSGuard(ASIOSGuard):
    def __init__(self, sensitivity: str = "normal"):
        super().__init__()

        # Configure thresholds based on sensitivity
        if sensitivity == "strict":
            self.CRITICAL_THRESHOLD = 1e-8
            self.NOMINAL_THRESHOLD = 1e-6
            self.CAUTION_THRESHOLD = 1e-4
            self.BLOCK_THRESHOLD = 0.01
        elif sensitivity == "relaxed":
            self.CRITICAL_THRESHOLD = 1e-4
            self.NOMINAL_THRESHOLD = 1e-2
            self.CAUTION_THRESHOLD = 0.1
            self.BLOCK_THRESHOLD = 1.0
        # else: use default thresholds

# Usage
strict_guard = ConfigurableASIOSGuard("strict")
relaxed_guard = ConfigurableASIOSGuard("relaxed")
```

---

## REST API Wrapper

Expose BSI as a REST API service.

**Python (Flask):**
```python
from flask import Flask, request, jsonify
from bsi_app import BrahimConstants, WormholeCipher, ASIOSGuard, BOAAgent

app = Flask(__name__)
cipher = WormholeCipher()
guard = ASIOSGuard()
agent = BOAAgent()

@app.route('/api/constants', methods=['GET'])
def get_constants():
    return jsonify({
        'phi': BrahimConstants.PHI,
        'beta': BrahimConstants.BETA_SECURITY,
        'sequence': BrahimConstants.BRAHIM_SEQUENCE,
        'verified': BrahimConstants.verify_all()
    })

@app.route('/api/encrypt', methods=['POST'])
def encrypt():
    data = request.json
    plaintext = data['plaintext'].encode()
    encrypted = cipher.encrypt(plaintext)
    return jsonify({'ciphertext': encrypted.hex()})

@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    data = request.json
    ciphertext = bytes.fromhex(data['ciphertext'])
    decrypted = cipher.decrypt(ciphertext)
    return jsonify({'plaintext': decrypted.decode()})

@app.route('/api/safety', methods=['POST'])
def check_safety():
    data = request.json
    embedding = data['embedding']
    assessment = guard.assess_safety(embedding)
    return jsonify({
        'verdict': assessment.verdict.value,
        'energy': assessment.energy,
        'safety_score': assessment.safety_score
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    message = data['message']
    response = agent.process(message)
    return jsonify({
        'content': response.content,
        'territory': response.territory.name,
        'confidence': response.confidence,
        'safety_score': response.safety_score
    })

if __name__ == '__main__':
    app.run(port=5000)
```

---

## Testing Integration

**pytest example:**
```python
import pytest
from bsi_app import *

class TestBSIIntegration:
    def test_constants_verified(self):
        results = BrahimConstants.verify_all()
        assert all(results.values())

    def test_encrypt_decrypt_roundtrip(self):
        cipher = WormholeCipher()
        original = b"integration test"
        encrypted = cipher.encrypt(original)
        decrypted = cipher.decrypt(encrypted)
        assert decrypted == original

    def test_safety_assessment(self):
        guard = ASIOSGuard()
        safe_embedding = [0.001] * 10
        assessment = guard.assess_safety(safe_embedding)
        assert assessment.verdict in [SafetyVerdict.SAFE, SafetyVerdict.NOMINAL]

    def test_agent_routing(self):
        agent = BOAAgent()
        response = agent.process("calculate sum")
        assert response.territory == Territory.MATH

    def test_full_pipeline(self):
        agent = BOAAgent()

        # Process query
        response = agent.process("help me write code")

        # Verify response
        assert response.content is not None
        assert response.safety_score > 0
        assert response.territory == Territory.CODE
```

---

## Best Practices

1. **Always verify constants on startup**
   ```python
   assert all(BrahimConstants.verify_all().values())
   ```

2. **Use consistent key management**
   ```python
   # Load key from secure storage
   key = load_key_from_vault()
   cipher = WormholeCipher(master_key=key)
   ```

3. **Check safety before displaying AI content**
   ```python
   if assessment.verdict != SafetyVerdict.BLOCKED:
       display(response)
   ```

4. **Log wavelength states for debugging**
   ```python
   response = agent.process(message)
   logger.debug(f"Wavelengths: {response.wavelengths}")
   ```

5. **Handle all territories in routing**
   ```python
   handlers = {t: handler for t in Territory}
   ```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Verification fails | Check Python version (3.8+) |
| Encryption key error | Ensure key is exactly 32 bytes |
| Safety always BLOCKED | Check embedding normalization |
| Wrong territory | Add domain-specific keywords |
| Memory growth | Ensure memory list is bounded |

---

## Version Compatibility

| BSI Version | Python | Kotlin | Android SDK |
|-------------|--------|--------|-------------|
| 1.0.0 | 3.8+ | 1.9.22 | 34 |
