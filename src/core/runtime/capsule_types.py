from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

CapsulePriority = Literal["low", "normal", "high"]
CapsuleKind = Literal["task", "skill", "debug", "teaching"]


@dataclass(frozen=True)
class Capsule:
    """Lightweight capsule contract for engine execution."""

    id: str
    kind: CapsuleKind
    goal: str
    payload: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    priority: CapsulePriority = "normal"
    trace: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CapsuleResult:
    """Normalized result for capsule execution."""

    ok: bool
    capsule_id: str
    output: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    blocked: bool = False
    pass_request: Optional[Dict[str, Any]] = None  # For PASS protocol handoff
    metrics: Dict[str, Any] = field(default_factory=dict)
