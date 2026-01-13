import time
import os
import numpy as np
import torch
import psutil

def format_bytes(size):
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"

def benchmark_ram_numpy(size_mb=1024):
    """Benchmarks RAM using optimized NumPy (CPU) operations to find max theoretical throughput."""
    print(f"1. [RAM] Benchmarking DDR5 Speed ({size_mb} MB)...", end="", flush=True)
    size_bytes = size_mb * 1024 * 1024
    
    # Alloc
    a = np.ones(size_bytes // 8, dtype=np.float64)
    b = np.ones(size_bytes // 8, dtype=np.float64)
    
    start = time.time()
    # Copy a to b
    np.copyto(b, a)
    duration = time.time() - start
    
    gb_per_sec = (size_bytes / duration) / 1e9
    print(f" {gb_per_sec:.2f} GB/s")
    return gb_per_sec

def benchmark_ssd(filename="benchmark_temp.dat", size_mb=1024):
    """Benchmarks Sequential Write/Read speed of the Disk."""
    print(f"2. [SSD] Benchmarking Disk I/O ({size_mb} MB)...", end="", flush=True)
    size_bytes = size_mb * 1024 * 1024
    data = os.urandom(size_bytes)
    
    # Write
    start = time.time()
    with open(filename, "wb") as f:
        f.write(data)
        os.fsync(f.fileno()) # Force write to disk
    write_time = time.time() - start
    write_speed = (size_bytes / write_time) / 1e9
    
    # Read
    start = time.time()
    with open(filename, "rb") as f:
        _ = f.read()
    read_time = time.time() - start
    read_speed = (size_bytes / read_time) / 1e9
    
    os.remove(filename)
    print(f" Write: {write_speed:.2f} GB/s | Read: {read_speed:.2f} GB/s")
    return write_speed, read_speed

def check_npu():
    """Checks for OpenVINO / NPU availability."""
    print("3. [NPU] Checking Intel AI Boost / NPU...", end="", flush=True)
    try:
        from openvino.runtime import Core
        core = Core()
        devices = core.available_devices
        
        npu_found = any("NPU" in d for d in devices)
        if npu_found:
            print(f" FOUND! Available Devices: {devices}")
            return True, devices
        else:
            print(f" Not Found. Devices: {devices}")
            return False, devices
    except ImportError:
        print(" OpenVINO not installed/found.")
        return False, []
    except Exception as e:
        print(f" Error: {e}")
        return False, []

def main():
    print("=== Full System Substrate Benchmark ===\n")
    
    # RAM
    ram_bw = benchmark_ram_numpy()
    
    # SSD
    ssd_write, ssd_read = benchmark_ssd()
    
    # NPU
    npu_avail, devices = check_npu()
    
    print("\n=== Substrate Hierarchy Report ===")
    print(f"TIER 1 (VRAM):      ~350.00 GB/s (Measured previously)")
    print(f"TIER 2 (RAM):       ~{ram_bw:.2f} GB/s (DDR5 Capacity)")
    print(f"TIER 3 (PCIe Bus):  ~26.00 GB/s (The Bottleneck)")
    print(f"TIER 4 (SSD):       ~{ssd_read:.2f} GB/s (Swap/Virtual Mem)")
    
    print("\n--- Insight ---")
    if ram_bw > 26.0:
        print(f"(!) Your RAM ({ram_bw:.2f} GB/s) is faster than your PCIe Bus (26 GB/s).")
        print("    This confirms the Bus is the choke point for Shared Memory.")
    
    if npu_avail:
        print(f"(!) NPU is ACTIVE ({devices}).")
        print("    You can offload Embeddings/Audio here to save VRAM.")
    else:
        print("(!) NPU is inactive. Install OpenVINO to unlock this tier.")

if __name__ == "__main__":
    main()
