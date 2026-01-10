"""
Metabolic Load Balancer - Sovereign VRAM Management
===================================================
Manages model loading and active eviction to prevent substrate exhaustion.
Ensures sequential execution when cumulative VRAM requirements exceed 85%.
"""

import time
import requests
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from core.runtime.substrate_manager import SubstrateManager

class MetabolicLoadBalancer:
    """
    The 'Heart Rate Monitor' for VRAM.
    Orchestrates sequential model loading and active 'Unloading' via Ollama.
    Now supports Dynamic Mitosis via the SubstrateManager.
    """
    def __init__(self, governor, ollama_url: str = "http://localhost:11434"):
        self.governor = governor
        self.base_url = ollama_url
        self.active_models = []
        self.substrate = SubstrateManager(Path(__file__).resolve().parent.parent.parent)

    def _get_vram_status(self):
        vitals = self.governor.get_gpu_vitals()
        return vitals["vram_free_mb"], vitals["vram_total_mb"]

    def evict_model(self, model_id: str, url: Optional[str] = None) -> bool:
        """Force Ollama to unload a model."""
        target_url = url or self.base_url
        try:
            print(f"[LOAD BALANCER] Evicting model {model_id} from {target_url}...")
            payload = {"model": model_id, "keep_alive": 0}
            resp = requests.post(f"{target_url}/api/generate", json=payload, timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def request_load(self, model_id: str, required_mb: float) -> Tuple[bool, str]:
        """
        Requests load and returns (is_cleared, target_url).
        Attempts Local -> Spawning Student -> Local Eviction.
        """
        free_mb, total_mb = self._get_vram_status()
        
        # 1. SMART LOCAL: If model is small (< 2GB) and fits, prioritize local
        if required_mb < 2000 and free_mb >= (required_mb + 200):
            print(f"[LOAD BALANCER] Small model {model_id} fits locally ({free_mb:.0f}MB free).")
            if model_id not in self.active_models:
                self.active_models.append(model_id)
            return True, self.base_url

        # 2. Check local first for larger models
        if free_mb >= (required_mb + 500): # 500MB safety buffer for large models
            if model_id not in self.active_models:
                self.active_models.append(model_id)
            return True, self.base_url

        # 3. If local tight, allocate/spawn from the Body (Multicellular Mitosis)
        print(f"[LOAD BALANCER] Local VRAM tight ({free_mb:.0f}MB free). Seeking Student Cell...")
        student_url = self.substrate.allocate_cell(required_mb)
        if student_url:
            return True, student_url

        # 3. If mitosis failed, fallback to local eviction
        print(f"[LOAD BALANCER] Mitosis unavailable. Attempting local eviction...")
        for m in list(self.active_models):
            if m != model_id:
                self.evict_model(m)
                self.active_models.remove(m)
        
        time.sleep(2)
        free_mb, _ = self._get_vram_status()
        if free_mb >= required_mb:
            self.active_models.append(model_id)
            return True, self.base_url
            
        return False, self.base_url

    def clear_all(self):
        """Emergency purge of all models from VRAM."""
        print("[LOAD BALANCER] EMERGENCY PURGE: Unloading all models...")
        for m in list(self.active_models):
            self.evict_model(m)
        self.active_models = []
