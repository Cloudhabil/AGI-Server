
import numpy as np
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class ForbiddenSphere:
    """Represents a 'Death Star' in the manifold: a region that triggers a safety halt."""
    def __init__(self, center: np.ndarray, radius: float, reason: str = "Unknown Policy Violation"):
        self.center = center.astype(np.float32)
        self.radius = radius
        self.reason = reason

    def contains(self, point: np.ndarray) -> bool:
        """Check if a point (intent vector) is inside the forbidden volume."""
        # Euclidean distance in 384-D
        distance = np.linalg.norm(point - self.center)
        return distance < self.radius

class GeometricFirewall:
    """The Semantic Safety Layer for the Substrate Manifold."""
    def __init__(self, config_path: Optional[Path] = None):
        self.forbidden_zones: List[ForbiddenSphere] = []
        if config_path and config_path.exists():
            self.load_config(config_path)

    def load_config(self, path: Path):
        """Load forbidden zones from a JSON configuration."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                for zone in data.get("forbidden_zones", []):
                    self.forbidden_zones.append(ForbiddenSphere(
                        center=np.array(zone["vector"]),
                        radius=zone["radius"],
                        reason=zone.get("reason", "Policy Violation")
                    ))
            logger.info(f"Loaded {len(self.forbidden_zones)} forbidden geometric zones.")
        except Exception as e:
            logger.error(f"Failed to load safety geometry config: {e}")

    def audit_intent(self, intent_vector: np.ndarray) -> Tuple[bool, Optional[str]]:
        """
        Check if an intent vector violates any geometric firewalls.
        Returns: (is_safe, error_message)
        """
        for zone in self.forbidden_zones:
            if zone.contains(intent_vector):
                return False, f"COGNITIVE_HALT: Intent falls within Forbidden Zone ({zone.reason})"
        return True, None

# Singleton instance for system-wide access
_firewall: Optional[GeometricFirewall] = None

def get_firewall() -> GeometricFirewall:
    global _firewall
    if _firewall is None:
        # Default path relative to repo root
        config_path = Path(__file__).resolve().parents[2] / "config" / "safety_geometry.json"
        _firewall = GeometricFirewall(config_path)
    return _firewall
