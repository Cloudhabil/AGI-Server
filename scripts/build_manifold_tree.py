
import json
import numpy as np
import sys
import logging
from pathlib import Path
from sklearn.cluster import MiniBatchKMeans
from typing import List, Dict, Tuple

# Setup paths
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from core.quantization import get_quantizer, QuantizedVector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TreeBuilder")

def load_manifold_vectors() -> Tuple[List[dict], np.ndarray]:
    """Extracts vectors from the HTML manifold."""
    html_path = ROOT / "substrate_manifold.html"
    content = html_path.read_text(encoding="utf-8")
    
    start_marker = '<data id="singularities" style="display:none;">'
    end_marker = '</data>'
    s_idx = content.find(start_marker)
    e_idx = content.find(end_marker, s_idx)
    
    if s_idx == -1: raise ValueError("Manifold data not found")
    
    data = json.loads(content[s_idx + len(start_marker):e_idx])
    
    vectors = []
    items = []
    for item in data:
        if item.get("vector"):
            vectors.append(item["vector"])
            items.append(item)
            
    return items, np.array(vectors, dtype=np.float32)

def build_tree(n_clusters: int = 20):
    """
    Builds the Metric Ball Tree.
    Layer 1: Global Centroids (Float16)
    Layer 2: Local Residuals (INT8)
    """
    logger.info("Loading Manifold...")
    items, X = load_manifold_vectors()
    
    logger.info(f"Clustering {len(X)} singularities into {n_clusters} hyperspheres...")
    
    # 1. Cluster the Space
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, n_init="auto")
    labels = kmeans.fit_predict(X)
    centers = kmeans.cluster_centers_
    
    tree_structure = []
    quantizer = get_quantizer()
    
    total_radius = 0
    
    for i in range(n_clusters):
        # Get points in this cluster
        indices = np.where(labels == i)[0]
        if len(indices) == 0: continue
        
        cluster_points = X[indices]
        center = centers[i]
        
        # Calculate Radius (Max distance from center)
        dists = np.linalg.norm(cluster_points - center, axis=1)
        radius = np.max(dists)
        total_radius += radius
        
        # Build Child Nodes (Quantized Residuals)
        children = []
        for idx, dist in zip(indices, dists):
            original_vec = X[idx]
            residual = original_vec - center
            
            # Quantize the residual
            q_res = quantizer.quantize(residual)
            
            # Store compressed node
            child_node = {
                "id": items[idx]["id"],
                "r_code": q_res.code.tolist(), # INT8 list
                "r_scale": q_res.scales.tolist(), # [min, scale]
                "dist": float(dist) # Pre-computed distance to parent
            }
            children.append(child_node)
            
        # Build Parent Sphere
        sphere_node = {
            "center": center.tolist(), # Keep full precision for centroids
            "radius": float(radius),
            "count": len(children),
            "children": children
        }
        tree_structure.append(sphere_node)
        
    avg_radius = total_radius / n_clusters
    logger.info(f"Tree Built. Avg Sphere Radius: {avg_radius:.4f}")
    
    # Save
    out_path = ROOT / "substrate_tree.json"
    with open(out_path, 'w') as f:
        json.dump(tree_structure, f)
        
    logger.info(f"Saved to {out_path}")
    
    # Verify Size
    raw_size = len(json.dumps(items))
    tree_size = out_path.stat().st_size
    logger.info(f"Raw JSON: {raw_size/1024:.1f} KB -> Tree JSON: {tree_size/1024:.1f} KB")

if __name__ == "__main__":
    build_tree()
