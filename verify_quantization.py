
import numpy as np
import sys
import time
from pathlib import Path

# Setup paths
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from core.quantization import get_quantizer

def test_quantization():
    print("=== Substrate Quantization Benchmark ===\n")
    quantizer = get_quantizer()
    
    # 1. Generate Random Logic Vectors (Normalized)
    print("Generating 10,000 random 384-D vectors...")
    vectors = np.random.randn(10000, 384).astype(np.float32)
    # Normalize to simulate unit hypersphere (cosine space)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    vectors = vectors / norms
    
    # 2. Benchmark Compression
    start_time = time.time()
    errors = []
    
    # Process batch
    for vec in vectors:
        # Quantize -> Dequantize
        q_vec = quantizer.quantize(vec)
        recon_vec = quantizer.dequantize(q_vec)
        
        # Calculate Error
        err = np.linalg.norm(vec - recon_vec)
        errors.append(err)
        
    duration = time.time() - start_time
    avg_error = np.mean(errors)
    max_error = np.max(errors)
    
    print(f"\nResults:")
    print(f"Processed 10,000 vectors in {duration:.4f}s ({10000/duration:.0f} vecs/s)")
    print(f"Average Reconstruction Error (L2): {avg_error:.6f}")
    print(f"Max Reconstruction Error (L2):     {max_error:.6f}")
    
    # 3. Size Comparison
    original_size = 384 * 4 # Float32 = 4 bytes
    compressed_size = 384 * 1 + 4 # Int8 = 1 byte + 2xFloat16 (4 bytes)
    ratio = original_size / compressed_size
    
    print(f"\nMemory Footprint per Vector:")
    print(f"Original (Float32):   {original_size} bytes")
    print(f"Quantized (INT8):     {compressed_size} bytes")
    print(f"Compression Ratio:    {ratio:.2f}x")
    
    if avg_error < 0.1:
        print("\n[PASS] Quantization Fidelity is sufficient for Reasoning.")
    else:
        print("\n[FAIL] Error too high for Substrate Manifold.")

if __name__ == "__main__":
    test_quantization()
