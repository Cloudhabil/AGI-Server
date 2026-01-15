
import numpy as np
import logging
from typing import Tuple, List, Optional
import pickle
from pathlib import Path

logger = logging.getLogger(__name__)

class QuantizedVector:
    """
    Represents a 384-D vector compressed into INT8 residuals.
    Uses a simplified Product Quantization (PQ) scheme.
    """
    def __init__(self, code: np.ndarray, scales: np.ndarray):
        self.code = code.astype(np.int8) # The quantized residuals
        self.scales = scales.astype(np.float16) # Scale factors (Half Precision)

class Quantizer:
    """
    Handles the compression of High-Dimensional Logic Vectors.
    Target: 384-D Float32 -> 384-D INT8 + Scale Factors.
    """
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.codebook = None # Reserved for future clustering optimization

    def quantize(self, vector: np.ndarray) -> QuantizedVector:
        """
        Compress a single 384-D float32 vector.
        Strategy: Min-Max Quantization per chunk.
        """
        # Ensure input is standard
        vec = vector.astype(np.float32)
        
        # 1. Find dynamic range
        v_min = np.min(vec)
        v_max = np.max(vec)
        scale = (v_max - v_min) / 255.0
        
        if scale == 0: scale = 1.0 # Avoid div/0 for zero vectors
        
        # 2. Compress to INT8 [-128, 127]
        # Shift to positive range [0, 255] then cast
        quantized = np.round((vec - v_min) / scale).astype(np.uint8)
        
        # Store as INT8 (byte) for storage efficiency
        # We store min_val and scale to reconstruct
        scales = np.array([v_min, scale], dtype=np.float16)
        
        return QuantizedVector(quantized.view(np.int8), scales)

    def dequantize(self, qv: QuantizedVector) -> np.ndarray:
        """
        Reconstruct the approximate float32 vector.
        """
        # Retrieve params
        v_min = qv.scales[0]
        scale = qv.scales[1]
        
        # Cast back to uint8 view then to float
        data = qv.code.view(np.uint8).astype(np.float32)
        
        # Reconstruct: val * scale + min
        reconstructed = data * scale + v_min
        return reconstructed

    @staticmethod
    def distance(v1: np.ndarray, v2: np.ndarray) -> float:
        """Standard Euclidean distance."""
        return np.linalg.norm(v1 - v2)

    def verify_integrity(self, original: np.ndarray) -> float:
        """
        Returns the reconstruction error (L2 distance).
        Target: < 0.1 for normalized vectors.
        """
        q = self.quantize(original)
        recon = self.dequantize(q)
        err = self.distance(original, recon)
        return err

# Singleton
_quantizer = Quantizer()

def get_quantizer() -> Quantizer:
    return _quantizer
