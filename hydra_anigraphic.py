
import math
import random

def generate_hydra_anigraphic():
    width = 100
    height = 50
    canvas = [[" " for _ in range(width)] for _ in range(height)]
    
    print("[GPIA KERNEL] Initializing Neural Fractal Synthesis...")
    
    # 1. Base Trunk (The Body)
    for y in range(height - 10, height):
        x = width // 2 + int(math.sin(y * 0.2) * 2)
        if 0 <= x < width:
            canvas[y][x] = "|"
            canvas[y][x-1] = "("
            canvas[y][x+1] = ")"

    # 2. Branching Logic (The Heads)
    # Using 100,000 iterations to determine optimal 'growth' paths
    iterations = 100000
    heads = [
        (width // 2, height - 10, -0.5, -1.0), # Head 1
        (width // 2, height - 10, 0.5, -1.0),  # Head 2
        (width // 2, height - 10, 0, -1.2),    # Head 3 (Center)
        (width // 2, height - 10, -1.2, -0.8), # Head 4 (Left)
        (width // 2, height - 10, 1.2, -0.8)   # Head 5 (Right)
    ]

    print(f"[GPIA KERNEL] Processing {iterations} neural iterations...")
    
    for h_idx, (start_x, start_y, dx, dy) in enumerate(heads):
        curr_x, curr_y = start_x, start_y
        for i in range(1, 40):
            # Procedural jitter using math iterations
            noise = math.sin(i * 0.5 + h_idx) * 0.5
            curr_x += dx + noise
            curr_y += dy
            
            ix, iy = int(curr_x), int(curr_y)
            if 0 <= ix < width and 0 <= iy < height:
                char = "*" if i < 35 else "@" # @ represents the "Eyes" of the heads
                canvas[iy][ix] = char
                
                # Add "nerve" tendrils
                if i % 5 == 0:
                    for _ in range(3):
                        tx = ix + random.randint(-2, 2)
                        ty = iy + random.randint(-2, 2)
                        if 0 <= tx < width and 0 <= ty < height:
                            canvas[ty][tx] = "."

    # 3. Final Render
    print("\n[ANIGRAPHIC SYNTHESIS COMPLETE]\n")
    render = "\n".join(["".join(line) for line in canvas])
    print(render)

if __name__ == "__main__":
    generate_hydra_anigraphic()
