"""
Network Health Monitor: Global Telemetry Sweep.
Deploys the Substrate Diagnostic Suite to analyze connection integrity.
"""
import sys
from pathlib import Path

# Add root
# Standardized import path setup
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
)

from core.network_diagnostic_suite import get_diag_suite

def main():
    suite = get_diag_suite(str(ROOT))
    
    # Authorized Global Targets for Telemetry
    targets = [
        "https://www.google.com",
        "https://www.bbc.co.uk",
        "https://opendata.cern.ch",
        "https://www.nic.ru", # Checking the Russia DNS authority integrity
        "https://www.ut.ac.ir" # Checking the Iran University integrity
    ]
    
    # Run the full diagnostic sweep
    results = suite.run_full_diagnostics(targets)
    
    print("\n" + "="*70)
    print("      DIAGNOSTIC COMPLETE")
    print("="*70)
    print(f"Historical telemetry saved to: {ROOT}/logs/network_telemetry/")
    print("="*70)

if __name__ == "__main__":
    main()

