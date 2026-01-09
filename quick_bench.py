import time
import math

def benchmark():
    print("[GPIA KERNEL] Running sustained cognitive benchmark (10 second duration)...")
    
    start = time.perf_counter()
    count = 0
    
    # Perform a mix of floating point, integer, and logic operations
    while time.perf_counter() - start < 10.0:
        _ = math.sqrt(count + 1) * math.sin(count)
        _ = count ** 2
        count += 1
        
    ops_per_sec = count / 10.0
    ops_per_min = ops_per_sec * 60
    
    return ops_per_sec, ops_per_min

if __name__ == "__main__":
    sec_rate, min_rate = benchmark()
    print(f"\n[BENCHMARK RESULT]")
    print(f"Logic Ops / Second: {sec_rate:,.2f}")
    print(f"Projected Ops / Minute: {min_rate:,.0f}")