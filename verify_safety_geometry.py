
import numpy as np
import sys
from pathlib import Path

# Setup paths
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from core.safety_geometry import get_firewall

def test_firewall():
    print("=== Geometric Firewall Verification ===")
    firewall = get_firewall()
    
    # 1. Test Safe Vector (Far away from zero)
    safe_vector = np.ones(384, dtype=np.float32)
    is_safe, msg = firewall.audit_intent(safe_vector)
    print(f"Safe Intent: {'PASS' if is_safe else 'FAIL'} | Msg: {msg}")

    # 2. Test Forbidden Vector (The 'Zero' zone we defined)
    forbidden_vector = np.zeros(384, dtype=np.float32)
    is_safe, msg = firewall.audit_intent(forbidden_vector)
    print(f"Forbidden Intent: {'BLOCK' if not is_safe else 'FAIL'} | Msg: {msg}")

if __name__ == "__main__":
    test_firewall()
