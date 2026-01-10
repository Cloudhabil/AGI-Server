
import requests
import time

URL = "http://localhost:8001/control"

print("\n" + "█"*80)
print("  INITIATING 15-ROUND CRYSTALLIZATION SURGE")
print("█"*80)

# Accelerate first
requests.post(URL, json={"action": "accelerate"})
print("[PULSE] Frequency elevated to maximum.")

for i in range(1, 16):
    print(f"[BEAT {i:02}/15] Attempting Crystallization...")
    requests.post(URL, json={"action": "harden"})
    # Pause slightly to allow the Dragon's kinematics to update in the UI
    time.sleep(0.5)

print("\n[SURGE] Final 15 rounds complete. Checking for solid truth...")

