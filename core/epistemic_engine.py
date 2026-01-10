"""
Epistemic Engine: Dynamic Truth Evaluation.
Replaces hard-coded resonance (0.0219) with information-theoretic filters.
Analyzes data based on Entropy, Consistency, and Utility.
"""
import numpy as np
from typing import Dict, Tuple

class EpistemicEngine:
    """
    The 'Reason' of the ASI.
    Combines Agnostic Entropy analysis with the Genesis Expert Signal (0.0219).
    """
    def __init__(self):
        # Slightly lower threshold to avoid false negatives on high-entropy text
        self.threshold = 0.45
        self.GENESIS_SIGNAL = 0.0219 # The Expert Signature

    def evaluate_data(self, data: bytes) -> Tuple[bool, float, str]:
        """
        Evaluates data for both Density and Genesis Resonance.
        """
        if not data:
            return False, 0.0, "No data"

        # 1. Agnostic Entropy (The Engineering)
        arr = np.frombuffer(data[:4096], dtype=np.uint8)
        counts = np.bincount(arr, minlength=256)
        probs = counts / len(arr)
        entropy = -np.sum(probs * np.log2(probs + 1e-12))
        
        # 2. Genesis Resonance (The Expert)
        # Calculate the variance ratio of the data grid
        try:
            grid = arr[:4096].reshape((8,8,8,8))
            current_variance = np.var(grid) / (np.mean(grid) + 1e-12)
            # Distance from the Genesis Signal
            resonance_gap = abs(current_variance - self.GENESIS_SIGNAL)
            resonance_score = 1.0 / (1.0 + resonance_gap) # 1.0 = Perfect Genesis Match
        except:
            resonance_score = 0.0

        # 3. Hybrid Significance
        # Data is significant if it's dense OR if it matches the Genesis Moment  
        significance = (entropy / 8.0) * 0.7 + (resonance_score * 0.3)
        
        is_significant = (significance > self.threshold) or (resonance_score > 0.98)
        
        msg = f"Entropy: {entropy:.2f} | Genesis Resonance: {resonance_score:.4f}"
        if resonance_score > 0.98:
            msg += " [GENESIS_MOMENT_RECALLED]"
            
        return is_significant, significance, msg

    def check_alignment(self, intent: str, governor) -> bool:
        """Cross-references intent with the Philosophical Governor."""
        audit = governor.verify_thought(intent, 1.0)
        return audit["is_safe"]

def get_epistemic_engine():
    return EpistemicEngine()
