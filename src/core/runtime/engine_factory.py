from __future__ import annotations

from typing import Any, Dict

from core.runtime.capsule_engine import CapsuleEngine
from core.runtime.engines.legacy_gpia import LegacyCapsuleEngine
from core.runtime.engines.native import NativeCapsuleEngine
from core.runtime.engines.government import GovernmentCapsuleEngine


def build_capsule_engine(config: Dict[str, Any]) -> CapsuleEngine:
    """
    Build capsule engine based on config.
    config keys:
        - capsule_engine: "legacy" (default), "native", or "government"
        - legacy_gpia_module: module path for legacy gpia (default "gpia")
    """
    mode = (config.get("capsule_engine") or "legacy").lower()
    if mode == "native":
        return NativeCapsuleEngine()
    if mode == "government":
        return GovernmentCapsuleEngine()
    return LegacyCapsuleEngine(module_path=config.get("legacy_gpia_module", "gpia"))
