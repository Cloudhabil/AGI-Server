import torch
import time
import psutil
import os

def format_bytes(size):
    power = 2**10
    n = 0
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}B"

def benchmark_bandwidth(size_bytes, device, iterations=100):
    # Host buffer (pinned memory for faster transfer)
    host_tensor = torch.randn(size_bytes // 4, dtype=torch.float32).pin_memory()
    # Pre-allocate Device buffer
    try:
        device_tensor = torch.empty(size_bytes // 4, dtype=torch.float32, device=device)
    except torch.cuda.OutOfMemoryError:
        raise RuntimeError("OOM during pre-allocation")

    # Measure Host to Device (H2D)
    torch.cuda.synchronize()
    start = time.time()
    for _ in range(iterations):
        device_tensor.copy_(host_tensor, non_blocking=True)
    torch.cuda.synchronize()
    h2d_time = time.time() - start
    h2d_bw = (size_bytes * iterations) / h2d_time / 1e9  # GB/s

    # Measure Device to Host (D2H)
    torch.cuda.synchronize()
    start = time.time()
    for _ in range(iterations):
        host_tensor.copy_(device_tensor, non_blocking=True)
    torch.cuda.synchronize()
    d2h_time = time.time() - start
    d2h_bw = (size_bytes * iterations) / d2h_time / 1e9  # GB/s

    # Measure Device to Device (D2D) - Internal VRAM Bandwidth
    # We need a second device buffer for a true copy
    try:
        device_tensor_2 = torch.empty(size_bytes // 4, dtype=torch.float32, device=device)
        torch.cuda.synchronize()
        start = time.time()
        for _ in range(iterations):
            device_tensor_2.copy_(device_tensor, non_blocking=True)
        torch.cuda.synchronize()
        d2d_time = time.time() - start
        d2d_bw = (size_bytes * iterations) / d2d_time / 1e9  # GB/s
        del device_tensor_2
    except torch.cuda.OutOfMemoryError:
        d2d_bw = 0.0 # Skip D2D if OOM for 2nd buffer

    del device_tensor
    return h2d_bw, d2h_bw, d2d_bw

def main():
    print("=== GPU Memory Benchmark ===")
    
    if not torch.cuda.is_available():
        print("CUDA is not available. Aborting.")
        return

    device = torch.device("cuda")
    props = torch.cuda.get_device_properties(device)
    print(f"Device: {props.name}")
    print(f"Total VRAM: {format_bytes(props.total_memory)}")
    
    # Check System Memory (RAM)
    vm = psutil.virtual_memory()
    print(f"System RAM: {format_bytes(vm.total)} (Available: {format_bytes(vm.available)})")

    # Benchmark Sizes
    sizes = [
        (1024 * 1024 * 10, "10 MB"),
        (1024 * 1024 * 100, "100 MB"),
        (1024 * 1024 * 500, "500 MB"),
        (1024 * 1024 * 1024, "1 GB"), 
    ]

    print("\nStarting Bandwidth Tests...")
    print(f"{ 'Size':<10} | {'H2D (PCIe)':<15} | {'D2H (PCIe)':<15} | {'D2D (VRAM)':<15}")
    print("-" * 65)

    for size_bytes, label in sizes:
        try:
            h2d, d2h, d2d = benchmark_bandwidth(size_bytes, device)
            print(f"{label:<10} | {h2d:>10.2f} GB/s | {d2h:>10.2f} GB/s | {d2d:>10.2f} GB/s")
        except RuntimeError as e:
            print(f"{label:<10} | Error: {e}")
            break
            
    print("\nNote: 'H2D/D2H' represents PCIe transfer speeds between CPU and GPU.")
    print("Note: 'D2D' represents internal VRAM copy speeds (Global Memory).")
    print("Note: 'Shared Memory' (L1/SRAM) is not directly measurable via PyTorch high-level API,")
    print("      but is significantly faster (TB/s range) and handled automatically by CUDA kernels.")

    # Shared GPU Memory (Windows Concept) Check
    print("\n=== Shared GPU Memory (System RAM backing) ===")
    print("This tests the OS's ability to use System RAM as VRAM overflow.")
    print("WARNING: This involves allocating > VRAM and may cause swapping/freezes.")
    
    try:
        # Try to allocate 110% of VRAM to force some swapping if possible, 
        # but be careful not to crash.
        # Actually, let's just allocate a safe chunk and see if it fits in VRAM first.
        allocated = torch.cuda.memory_allocated()
        free = props.total_memory - allocated
        print(f"Current Free VRAM: {format_bytes(free)}")
        
        # We won't force overflow automatically to avoid crashing the user's session without consent.
        print("Skipping forced overflow test for safety. If you want to test 'Shared GPU Memory' (RAM overflow),")
        print("you would need to allocate tensors exceeding physical VRAM.")
        
    except Exception as e:
        print(f"Error checking memory: {e}")

if __name__ == "__main__":
    main()
