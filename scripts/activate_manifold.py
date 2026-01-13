import os
import sys
import json
import time
from pathlib import Path

# Setup paths
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from core.npu_utils import get_substrate_embeddings_batch, has_npu

def extract_semantic_core(file_path: Path) -> str:
    """Extracts filename and docstring/summary for embedding."""
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        # Get first 1000 chars for semantic context
        # (NPUEmbedder has a 128-token limit, so 1000 chars is plenty)
        summary = content[:1000].strip()
        return f"File: {file_path.name}\nPath: {file_path}\n{summary}"
    except Exception:
        return f"File: {file_path.name}\n(Unreadable)"

def main():
    print("=== Substrate Manifold Activation (NPU Mode) ===")
    
    manifold_path = ROOT / "substrate_manifold.html"
    if not manifold_path.exists():
        print(f"Error: {manifold_path} not found.")
        return

    # 1. Identify all 841 singularities
    print("Mapping logic singularities...")
    # List of search dirs
    dirs = [SRC / "skills", ROOT / "skills"]
    files = []
    for d in dirs:
        if d.exists():
            files.extend(list(d.rglob("*.py")))
    
    print(f"Found {len(files)} potential singularities.")
    
    # 2. Extract semantic cores
    print("Extracting semantic signatures...")
    payloads = []
    ids = []
    for f in files:
        # Convert to relative path for ID
        rel_id = f.relative_to(ROOT).as_posix()
        ids.append(rel_id)
        payloads.append(extract_semantic_core(f))

    # 3. Generate Vectors on NPU
    print(f"Activating Intel NPU for {len(payloads)} embeddings...")
    os.environ["USE_NPU_EMBEDDINGS"] = "1"
    os.environ["EMBEDDING_DEVICE"] = "NPU"
    
    start_time = time.perf_counter()
    # Batch process to respect NPU throughput
    batch_size = 50
    all_vectors = []
    
    for i in range(0, len(payloads), batch_size):
        batch = payloads[i:i+batch_size]
        print(f" Processing batch {i//batch_size + 1}/{(len(payloads)//batch_size)+1}...", end="\r")
        vectors = get_substrate_embeddings_batch(batch)
        all_vectors.extend(vectors)
    
    elapsed = time.perf_counter() - start_time
    print(f"\nNPU Task Complete in {elapsed:.2f}s (~{len(payloads)/elapsed:.1f} texts/sec).")

    # 4. Construct JSON Manifold
    manifold_data = []
    for rel_id, vector in zip(ids, all_vectors):
        manifold_data.append({
            "id": rel_id,
            "vector": vector
        })

    # 5. Inject into HTML
    print("Injecting vectors into substrate_manifold.html...")
    html_content = manifold_path.read_text(encoding="utf-8")
    
    # Find the <data id="singularities"> node
    marker_start = '<data id="singularities" style="display:none;">'
    marker_end = '</data>'
    
    start_idx = html_content.find(marker_start)
    end_idx = html_content.find(marker_end, start_idx)
    
    if start_idx == -1 or end_idx == -1:
        print("Error: Could not find <data> injection point in HTML.")
        return

    new_data_json = json.dumps(manifold_data, indent=4)
    new_html = html_content[:start_idx + len(marker_start)] + "\n" + new_data_json + "\n" + html_content[end_idx:]
    
    manifold_path.write_text(new_html, encoding="utf-8")
    print(f"SUCCESS: Manifold activated with {len(manifold_data)} vectorized singularities.")

if __name__ == "__main__":
    main()
