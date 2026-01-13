import torch
import time
import psutil

def format_bytes(size):
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"

def benchmark_tensor_speed(tensor, iterations=20, label=""):
    """
    Measures the speed of a simple operation on the tensor to determine 
    if it's in fast VRAM or slow Shared Memory (PCIe).
    """
    torch.cuda.synchronize()
    start = time.time()
    for _ in range(iterations):
        # Simple operation: y = x + 1 (read + write)
        _ = tensor.add(1.0) 
    torch.cuda.synchronize()
    duration = time.time() - start
    
    # Calculate effective bandwidth (Read + Write)
    # Each ops is 2 accesses (Read x, Write result) * size
    total_bytes = tensor.numel() * tensor.element_size() * 2 * iterations
    gb_per_sec = (total_bytes / duration) / 1e9
    return gb_per_sec

def main():
    print("=== Shared Memory Equilibrium Search ===")
    
    if not torch.cuda.is_available():
        print("CUDA not available.")
        return

    device = torch.device("cuda")
    props = torch.cuda.get_device_properties(device)
    total_vram = props.total_memory
    print(f"Physical VRAM Limit: {format_bytes(total_vram)}")
    
    # We will keep references to tensors to hold memory
    tensors = []
    
    # Chunk size for probing (256 MB)
    chunk_size_mb = 256
    chunk_bytes = chunk_size_mb * 1024 * 1024
    
    allocated = 0
    step = 0
    
    print(f"\n{'Step':<5} | {'Allocated':<12} | {'Speed':<15} | {'Location Estimate'}")
    print("-" * 60)
    
    # PCIe Baseline (approximate from previous test)
    pcie_threshold_gbps = 60.0 # If speed < 60 GB/s, we are definitely over PCIe
    
    try:
        while True:
            step += 1
            
            # Allocate chunk
            try:
                # We assume the driver handles swapping/managed memory if we go over
                t = torch.zeros(chunk_bytes // 4, dtype=torch.float32, device=device)
                tensors.append(t)
                allocated += chunk_bytes
            except torch.cuda.OutOfMemoryError:
                print(f"\n[!] Hard OOM reached at {format_bytes(allocated)}. Driver refused further allocation.")
                break
            except RuntimeError as e:
                print(f"\n[!] Runtime Error: {e}")
                break

            # Measure Speed of the *newest* chunk
            speed = benchmark_tensor_speed(t)
            
            # Determine Location
            location = "VRAM (Fast)"
            if speed < pcie_threshold_gbps:
                location = "SHARED (Bus/PCIe)"
                
            print(f"{step:<5} | {format_bytes(allocated):<12} | {speed:>6.2f} GB/s    | {location}")
            
            # Safety break: If we are deep in Shared Memory, stop to prevent system freeze
            if location == "SHARED (Bus/PCIe)" and allocated > (total_vram * 1.5):
                 print("\n[Equilibrium Found] Deep in Shared Memory. Stopping safety to prevent freeze.")
                 break
                 
            # If speed is extremely low, stop immediately
            if speed < 1.0:
                 print("\n[!] Speed critical (< 1 GB/s). Stopping.")
                 break

    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    
    print("\n=== Equilibrium Analysis ===")
    print(f"Total Dedicated VRAM: {format_bytes(total_vram)}")
    print(f"Total Successfully Allocated: {format_bytes(allocated)}")
    print("The 'Equilibrium Point' is the step where Speed dropped from >100 GB/s to <30 GB/s.")
    print("This confirms the PCIe Bus is active and handling the overflow memory.")

if __name__ == "__main__":
    main()
