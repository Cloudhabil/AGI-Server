import torch
import time
import psutil
import numpy as np

def format_bytes(size):
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"

def benchmark_cpu_ram_bandwidth(size_mb=512):
    """Benchmarks System RAM Bandwidth using standard Copy operations."""
    print(f"Benchmarking System RAM ({size_mb} MB chunk)...", end="", flush=True)
    size_bytes = size_mb * 1024 * 1024
    # Allocate in pinned memory (page-locked) to get closer to raw hardware speed
    # or just standard tensor to measure "app usage" speed.
    t_cpu = torch.zeros(size_bytes // 4, dtype=torch.float32)
    t_cpu_2 = torch.zeros(size_bytes // 4, dtype=torch.float32)
    
    start = time.time()
    t_cpu_2.copy_(t_cpu)
    duration = time.time() - start
    
    gb_per_sec = (size_bytes / duration) / 1e9
    print(f" {gb_per_sec:.2f} GB/s")
    return gb_per_sec

def benchmark_tensor_speed(tensor, iterations=10):
    torch.cuda.synchronize()
    start = time.time()
    for _ in range(iterations):
        _ = tensor.add(1.0)
    torch.cuda.synchronize()
    duration = time.time() - start
    
    # Read + Write = 2 ops per element
    total_bytes = tensor.numel() * tensor.element_size() * 2 * iterations
    gb_per_sec = (total_bytes / duration) / 1e9
    return gb_per_sec

def main():
    print("=== Precision Memory Map & RAM Baseline ===")
    
    # 1. System RAM Baseline
    ram_speed = benchmark_cpu_ram_bandwidth()
    print(f"-> Your System RAM Limit is approx. {ram_speed:.2f} GB/s.")
    print(f"-> This means 'Shared Memory' (GPU overflow) can NEVER exceed this speed.\n")

    if not torch.cuda.is_available():
        print("CUDA not available.")
        return

    device = torch.device("cuda")
    props = torch.cuda.get_device_properties(device)
    total_vram = props.total_memory
    print(f"Physical VRAM Total: {format_bytes(total_vram)}")
    
    # 2. Fast Approach to Safe Zone
    tensors = []
    allocated = 0
    
    # Fill to 8.5 GB quickly (safe zone)
    safe_zone_mb = 8500
    print(f"Fast-filling first {format_bytes(safe_zone_mb * 1024**2)}...")
    
    try:
        t_big = torch.zeros((safe_zone_mb * 1024 * 1024) // 4, dtype=torch.float32, device=device)
        tensors.append(t_big)
        allocated += (safe_zone_mb * 1024 * 1024)
    except Exception as e:
        print(f"Error during fast fill: {e}")
        return

    print("Approaching the Cliff... Switching to 25 MB steps.")
    print(f"\n{'Allocated':<12} | {'Gap to Max':<12} | {'Speed':<15} | {'State'}")
    print("-" * 65)
    
    chunk_mb = 25
    chunk_bytes = chunk_mb * 1024 * 1024
    
    cliff_found = False
    
    try:
        while True:
            # Allocate small chunk
            try:
                t = torch.zeros(chunk_bytes // 4, dtype=torch.float32, device=device)
                tensors.append(t)
                allocated += chunk_bytes
            except torch.cuda.OutOfMemoryError:
                print(f"\n[!] Hard OOM reached at {format_bytes(allocated)}.")
                break

            # Measure Speed
            speed = benchmark_tensor_speed(t)
            
            remaining = total_vram - allocated
            gap_str = format_bytes(remaining) if remaining > 0 else f"-{format_bytes(abs(remaining))}"
            
            state = "OK"
            if speed < 100.0:
                state = "SLOW (Shared?)"
            if speed < 40.0:
                state = "CLIFF HIT!"
                cliff_found = True
            
            print(f"{format_bytes(allocated):<12} | {gap_str:<12} | {speed:>6.2f} GB/s    | {state}")
            
            if cliff_found and speed < 30.0:
                print(f"\n[Result] The Precision Cliff is at {format_bytes(allocated)}.")
                print(f"At this point, you hit the 'Invisible Wall' of Windows/Display overhead.")
                break
                
            # Safety stop well past physical
            if allocated > (total_vram + 1024*1024*1024): # Stop 1GB past physical
                print("Passed physical limit significantly. Stopping.")
                break

    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
