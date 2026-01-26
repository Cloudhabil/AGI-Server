"""
Adaptive Threat Detection and Response System (ATDRS)
======================================================

A formal implementation of an adaptive security layer for autonomous
cognitive systems, providing:

1. Anomaly Detection: Statistical and pattern-based threat identification
2. Adaptive Boundaries: Machine learning-augmented security perimeters
3. Graceful Degradation: Multi-level fault tolerance protocols
4. Persistent Threat Memory: Long-term signature storage with decay

This module implements concepts from:
- Denning, D.E. (1987) "An Intrusion-Detection Model"
- Forrest, S. et al. (1994) "Self-Nonself Discrimination in a Computer"
- Hofmeyr, S.A. (2000) "An Immunological Model of Distributed Detection"

Author: Elias Oulad Brahim
Institution: ASIOS Research
Date: 2026-01-26
License: Proprietary
"""

import json
import logging
import time
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum, IntEnum
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: CONSTANTS AND CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Detection thresholds (empirically derived)
ANOMALY_THRESHOLD_ALPHA = 0.382    # Minor deviation (1-sigma equivalent)
ANOMALY_THRESHOLD_BETA = 0.618     # Significant deviation (2-sigma)
ANOMALY_THRESHOLD_GAMMA = 0.854    # Critical deviation (3-sigma)

# System parameters
SIGNATURE_RETENTION_DAYS = 30      # Threat signature memory retention
ADAPTIVE_LEARNING_RATE = 0.236    # Boundary adjustment coefficient
MINIMUM_CLUSTER_SIZE = 3          # Events required for pattern extraction
RECOVERY_ITERATION_COUNT = 7      # Fault recovery cycles


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: TYPE DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

class SeverityLevel(IntEnum):
    """
    Threat severity classification following CVSS v3.1 methodology.

    Reference: FIRST.org Common Vulnerability Scoring System
    """
    NONE = 0        # No security impact
    LOW = 1         # Minor impact, self-recoverable
    MEDIUM = 2      # Moderate impact, requires isolation
    HIGH = 3        # Significant impact, immediate response
    CRITICAL = 4    # System-wide impact, emergency protocols


class ThreatCategory(Enum):
    """
    Taxonomy of detectable threat types.

    Based on MITRE ATT&CK framework classifications.
    """
    BOUNDARY_VIOLATION = "boundary"      # Vector space intrusion
    INJECTION_ATTACK = "injection"       # Malicious content injection
    INTEGRITY_VIOLATION = "integrity"    # Data corruption detected
    BEHAVIORAL_ANOMALY = "behavioral"    # Statistical deviation
    RESOURCE_EXHAUSTION = "dos"          # Denial of service pattern
    UNTRUSTED_SOURCE = "untrusted"       # External source risk
    UNCLASSIFIED = "unknown"


@dataclass
class ThreatSignature:
    """
    Formal representation of a detected threat pattern.

    Attributes:
        signature_id: Unique identifier (UUID format recommended)
        category: Classification per ThreatCategory taxonomy
        centroid_vector: Mean vector of clustered threat instances
        boundary_radius: Detection radius in vector space (L2 norm)
        keyword_patterns: String patterns for text-based detection
        source_blacklist: Known malicious source identifiers
        created_at: ISO 8601 timestamp of first detection
        last_seen: ISO 8601 timestamp of most recent match
        occurrence_count: Total matches against this signature
    """
    signature_id: str
    category: ThreatCategory
    centroid_vector: Optional[List[float]] = None
    boundary_radius: float = 0.5
    keyword_patterns: List[str] = field(default_factory=list)
    source_blacklist: List[str] = field(default_factory=list)
    created_at: str = ""
    last_seen: str = ""
    occurrence_count: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()
        self.last_seen = datetime.utcnow().isoformat()


@dataclass
class SecurityEvent:
    """
    Structured security event record.

    Conforms to CEF (Common Event Format) logging standards.
    """
    event_id: str
    timestamp: str
    severity: SeverityLevel
    category: ThreatCategory
    source_identifier: str
    description: str
    feature_vector: Optional[List[float]] = None
    affected_components: List[int] = field(default_factory=list)
    response_actions: str = ""
    resolved: bool = False


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: DETECTION ENGINES
# ═══════════════════════════════════════════════════════════════════════════════

class SignatureBasedDetector:
    """
    Pattern matching detector using known threat signatures.

    Implements exact and fuzzy matching against stored signatures.
    Time complexity: O(n*m) where n=signatures, m=feature dimensions.
    """

    def __init__(self, signature_store: 'SignatureStore'):
        self._store = signature_store

    def detect(
        self,
        feature_vector: np.ndarray,
        metadata: Dict
    ) -> Optional[ThreatSignature]:
        """
        Check feature vector against known threat signatures.

        Args:
            feature_vector: N-dimensional feature representation
            metadata: Additional context (source, timestamp, etc.)

        Returns:
            Matching ThreatSignature if detected, None otherwise
        """
        for signature in self._store.get_active_signatures():
            # Vector-based matching (Euclidean distance)
            if signature.centroid_vector is not None:
                centroid = np.array(signature.centroid_vector, dtype=np.float32)
                distance = np.linalg.norm(feature_vector - centroid)
                if distance < signature.boundary_radius:
                    return signature

            # Keyword pattern matching
            source = metadata.get("source", "")
            for pattern in signature.keyword_patterns:
                if pattern.lower() in source.lower():
                    return signature

        return None


class AnomalyBasedDetector:
    """
    Statistical anomaly detection using baseline comparison.

    Implements modified Z-score analysis for multivariate data.
    Reference: Iglewicz & Hoaglin (1993) "How to Detect and Handle Outliers"
    """

    def __init__(self):
        self._baseline: Dict[str, float] = {}
        self._variance: Dict[str, float] = {}

    def calibrate(self, baseline_metrics: Dict[str, float]):
        """
        Establish baseline for anomaly comparison.

        Args:
            baseline_metrics: Dictionary of metric_name -> healthy_value
        """
        self._baseline = baseline_metrics.copy()

    def detect(
        self,
        current_metrics: Dict[str, float]
    ) -> List[Tuple[str, float, SeverityLevel]]:
        """
        Compare current metrics against baseline.

        Args:
            current_metrics: Current system state metrics

        Returns:
            List of (metric_name, deviation_ratio, severity) tuples
        """
        anomalies = []

        for metric_name, current_value in current_metrics.items():
            baseline_value = self._baseline.get(metric_name, current_value)
            if baseline_value == 0:
                continue

            # Calculate normalized deviation
            deviation = abs(current_value - baseline_value) / (baseline_value + 1e-9)

            # Classify severity based on deviation magnitude
            if deviation > ANOMALY_THRESHOLD_GAMMA:
                anomalies.append((metric_name, deviation, SeverityLevel.HIGH))
            elif deviation > ANOMALY_THRESHOLD_BETA:
                anomalies.append((metric_name, deviation, SeverityLevel.MEDIUM))
            elif deviation > ANOMALY_THRESHOLD_ALPHA:
                anomalies.append((metric_name, deviation, SeverityLevel.LOW))

        return anomalies


class AdaptivePatternLearner:
    """
    Online learning component for threat pattern extraction.

    Implements incremental clustering for new signature generation.
    Based on: Aggarwal et al. (2003) "A Framework for Clustering Evolving Data Streams"
    """

    def __init__(self, signature_store: 'SignatureStore'):
        self._store = signature_store
        self._event_buffer: List[SecurityEvent] = []

    def ingest_event(self, event: SecurityEvent):
        """
        Process security event for pattern learning.

        Args:
            event: Detected security event to learn from
        """
        self._event_buffer.append(event)
        self._attempt_signature_extraction(event.category)

    def _attempt_signature_extraction(self, category: ThreatCategory):
        """
        Attempt to extract new signature from clustered events.
        """
        # Filter events by category
        category_events = [
            e for e in self._event_buffer
            if e.category == category
        ]

        if len(category_events) < MINIMUM_CLUSTER_SIZE:
            return

        # Extract feature vectors
        vectors = [
            np.array(e.feature_vector)
            for e in category_events
            if e.feature_vector is not None
        ]

        if len(vectors) < MINIMUM_CLUSTER_SIZE:
            return

        # Compute cluster centroid and radius
        centroid = np.mean(vectors, axis=0)
        max_distance = max(np.linalg.norm(v - centroid) for v in vectors)
        radius = max_distance + 0.1  # Safety margin

        # Generate new signature
        new_signature = ThreatSignature(
            signature_id=f"auto_{category.value}_{int(time.time())}",
            category=category,
            centroid_vector=centroid.tolist(),
            boundary_radius=radius,
            occurrence_count=len(category_events)
        )

        self._store.register(new_signature)
        logger.info(f"Extracted new threat signature: {new_signature.signature_id}")

        # Clear processed events
        self._event_buffer = [
            e for e in self._event_buffer
            if e.category != category
        ]


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: SIGNATURE PERSISTENCE
# ═══════════════════════════════════════════════════════════════════════════════

class SignatureStore:
    """
    Persistent storage for threat signatures with temporal decay.

    Implements LRU-style eviction based on last-seen timestamp.
    """

    def __init__(self, storage_path: Path):
        self._path = storage_path
        self._signatures: Dict[str, ThreatSignature] = {}
        self._load()

    def _load(self):
        """Load signatures from persistent storage."""
        if not self._path.exists():
            return

        try:
            with open(self._path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for entry in data.get("signatures", []):
                sig = ThreatSignature(
                    signature_id=entry["signature_id"],
                    category=ThreatCategory(entry["category"]),
                    centroid_vector=entry.get("centroid_vector"),
                    boundary_radius=entry.get("boundary_radius", 0.5),
                    keyword_patterns=entry.get("keyword_patterns", []),
                    source_blacklist=entry.get("source_blacklist", []),
                    created_at=entry.get("created_at", ""),
                    last_seen=entry.get("last_seen", ""),
                    occurrence_count=entry.get("occurrence_count", 0)
                )
                self._signatures[sig.signature_id] = sig

            logger.info(f"Loaded {len(self._signatures)} threat signatures.")
        except Exception as e:
            logger.error(f"Failed to load signature store: {e}")

    def _save(self):
        """Persist signatures to storage."""
        self._path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "signatures": [],
            "last_updated": datetime.utcnow().isoformat(),
            "schema_version": "1.0"
        }

        for sig in self._signatures.values():
            entry = asdict(sig)
            entry["category"] = sig.category.value
            data["signatures"].append(entry)

        with open(self._path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def register(self, signature: ThreatSignature):
        """Add or update a threat signature."""
        if signature.signature_id in self._signatures:
            existing = self._signatures[signature.signature_id]
            existing.occurrence_count += 1
            existing.last_seen = datetime.utcnow().isoformat()
        else:
            self._signatures[signature.signature_id] = signature
        self._save()

    def get_active_signatures(self) -> List[ThreatSignature]:
        """
        Retrieve non-expired signatures.

        Signatures are considered expired if:
        - Not seen in SIGNATURE_RETENTION_DAYS
        - AND occurrence_count < 10 (low-frequency threats may be retained)
        """
        cutoff = datetime.utcnow() - timedelta(days=SIGNATURE_RETENTION_DAYS)
        active = []

        for sig in self._signatures.values():
            last_seen = datetime.fromisoformat(sig.last_seen) if sig.last_seen else datetime.min
            if last_seen > cutoff or sig.occurrence_count >= 10:
                active.append(sig)

        return active

    def prune_expired(self):
        """Remove expired signatures from store."""
        cutoff = datetime.utcnow() - timedelta(days=SIGNATURE_RETENTION_DAYS * 2)
        expired = []

        for sig_id, sig in self._signatures.items():
            last_seen = datetime.fromisoformat(sig.last_seen) if sig.last_seen else datetime.min
            if last_seen < cutoff and sig.occurrence_count < 5:
                expired.append(sig_id)

        for sig_id in expired:
            del self._signatures[sig_id]
            logger.info(f"Pruned expired signature: {sig_id}")

        if expired:
            self._save()


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: ADAPTIVE SECURITY PERIMETER
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SecurityZone:
    """
    Definition of a protected region in feature space.

    Implements dynamic boundary adjustment based on threat feedback.
    """
    zone_id: str
    centroid: List[float]
    radius: float
    description: str
    created_at: str = ""
    adjustment_count: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.utcnow().isoformat()


class AdaptiveSecurityPerimeter:
    """
    Dynamic security boundary management.

    Implements feedback-driven boundary adjustment:
    - Expansion on confirmed threats
    - Contraction on false positives

    Reference: Portnoy et al. (2001) "Intrusion detection with unlabeled data"
    """

    def __init__(self, config_path: Path):
        self._config_path = config_path
        self._zones: Dict[str, SecurityZone] = {}
        self._load()

    def _load(self):
        """Load zone configuration."""
        if not self._config_path.exists():
            return

        try:
            with open(self._config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for entry in data.get("security_zones", []):
                zone = SecurityZone(
                    zone_id=entry["zone_id"],
                    centroid=entry["centroid"],
                    radius=entry["radius"],
                    description=entry.get("description", ""),
                    created_at=entry.get("created_at", ""),
                    adjustment_count=entry.get("adjustment_count", 0)
                )
                self._zones[zone.zone_id] = zone

            logger.info(f"Loaded {len(self._zones)} security zones.")
        except Exception as e:
            logger.warning(f"Failed to load security perimeter config: {e}")

    def _save(self):
        """Persist zone configuration."""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "security_zones": [asdict(z) for z in self._zones.values()],
            "last_updated": datetime.utcnow().isoformat()
        }

        with open(self._config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def check_boundary(
        self,
        feature_vector: np.ndarray
    ) -> Tuple[bool, Optional[str]]:
        """
        Evaluate feature vector against security perimeter.

        Args:
            feature_vector: N-dimensional feature representation

        Returns:
            Tuple of (is_permitted, violation_message)
        """
        for zone in self._zones.values():
            centroid = np.array(zone.centroid, dtype=np.float32)
            distance = np.linalg.norm(feature_vector - centroid)
            if distance < zone.radius:
                return False, f"PERIMETER_VIOLATION: {zone.description}"
        return True, None

    def adjust_boundary(
        self,
        zone_id: str,
        incident_vector: np.ndarray,
        was_true_positive: bool
    ):
        """
        Adjust zone boundary based on detection feedback.

        Args:
            zone_id: Identifier of zone to adjust
            incident_vector: Vector that triggered detection
            was_true_positive: Whether detection was correct
        """
        if zone_id not in self._zones:
            return

        zone = self._zones[zone_id]

        if was_true_positive:
            # Expand boundary (increase security)
            zone.radius *= (1 + ADAPTIVE_LEARNING_RATE * 0.1)
            zone.radius = min(zone.radius, zone.radius * 1.5)  # Cap expansion
        else:
            # Contract boundary (reduce false positives)
            zone.radius *= (1 - ADAPTIVE_LEARNING_RATE * 0.05)
            zone.radius = max(zone.radius, 0.1)  # Minimum boundary

        zone.adjustment_count += 1
        self._save()
        logger.info(f"Adjusted zone {zone_id}: radius={zone.radius:.4f}")

    def create_zone(
        self,
        centroid: np.ndarray,
        description: str
    ) -> str:
        """
        Dynamically create new security zone.

        Args:
            centroid: Center point of new zone
            description: Human-readable zone description

        Returns:
            Generated zone_id
        """
        zone_id = f"dynamic_{int(time.time())}"
        zone = SecurityZone(
            zone_id=zone_id,
            centroid=centroid.tolist(),
            radius=0.3,  # Initial conservative radius
            description=description
        )
        self._zones[zone_id] = zone
        self._save()
        logger.info(f"Created security zone: {zone_id}")
        return zone_id


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: FAULT TOLERANCE AND RECOVERY
# ═══════════════════════════════════════════════════════════════════════════════

class FaultToleranceManager:
    """
    Multi-level degradation and recovery management.

    Implements graceful degradation pattern:
    Level 0: Normal operation
    Level 1: External input disabled
    Level 2: Autonomous operations disabled
    Level 3: Read-only mode
    Level 4: Network isolation
    Level 5: Emergency halt

    Reference: Gray & Reuter (1993) "Transaction Processing: Concepts and Techniques"
    """

    def __init__(self, repo_root: Path):
        self._root = repo_root
        self._recovery_log: List[Dict] = []
        self._degradation_level = 0

    def execute_response(self, event: SecurityEvent) -> Dict:
        """
        Execute appropriate response based on event severity.

        Args:
            event: Security event requiring response

        Returns:
            Response report dictionary
        """
        response = {
            "event_id": event.event_id,
            "timestamp": datetime.utcnow().isoformat(),
            "actions": [],
            "success": True
        }

        if event.severity == SeverityLevel.LOW:
            response["actions"].append("LOG_EVENT")

        elif event.severity == SeverityLevel.MEDIUM:
            response["actions"].append("ISOLATE_COMPONENTS")
            self._isolate_components(event.affected_components)

        elif event.severity == SeverityLevel.HIGH:
            response["actions"].append("ISOLATE_COMPONENTS")
            response["actions"].append("ENTER_DEGRADED_MODE_1")
            self._isolate_components(event.affected_components)
            self._set_degradation_level(1)

        elif event.severity == SeverityLevel.CRITICAL:
            response["actions"].append("EMERGENCY_ISOLATION")
            response["actions"].append("ENTER_DEGRADED_MODE_3")
            response["actions"].append("ALERT_ADMINISTRATOR")
            self._isolate_components(event.affected_components)
            self._set_degradation_level(3)
            self._send_alert(event)

        self._recovery_log.append(response)
        return response

    def _isolate_components(self, component_indices: List[int]):
        """Mark components as isolated in system state."""
        state_path = self._root / "data" / "substrate_tree.json"
        if not state_path.exists():
            return

        try:
            with open(state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            for idx in component_indices:
                if 0 <= idx < len(state):
                    state[idx]["status"] = "ISOLATED"
                    state[idx]["isolated_at"] = datetime.utcnow().isoformat()

            with open(state_path, 'w', encoding='utf-8') as f:
                json.dump(state, f)

            logger.info(f"Isolated {len(component_indices)} components.")
        except Exception as e:
            logger.error(f"Component isolation failed: {e}")

    def _set_degradation_level(self, level: int):
        """
        Set system degradation level.

        Persists degradation state for system-wide awareness.
        """
        self._degradation_level = min(level, 5)

        state_path = self._root / "data" / "system_degradation.json"
        state_path.parent.mkdir(parents=True, exist_ok=True)

        restrictions = self._get_restrictions(self._degradation_level)

        with open(state_path, 'w', encoding='utf-8') as f:
            json.dump({
                "level": self._degradation_level,
                "timestamp": datetime.utcnow().isoformat(),
                "restrictions": restrictions
            }, f, indent=2)

        logger.warning(f"System degradation level: {self._degradation_level}")

    def _get_restrictions(self, level: int) -> List[str]:
        """Map degradation level to operational restrictions."""
        restrictions = []
        if level >= 1:
            restrictions.append("EXTERNAL_INPUT_DISABLED")
        if level >= 2:
            restrictions.append("AUTONOMOUS_OPERATIONS_DISABLED")
        if level >= 3:
            restrictions.append("WRITE_OPERATIONS_DISABLED")
        if level >= 4:
            restrictions.append("NETWORK_ACCESS_DISABLED")
        if level >= 5:
            restrictions.append("SYSTEM_HALTED")
        return restrictions

    def _send_alert(self, event: SecurityEvent):
        """Queue alert for administrator review."""
        alert_path = self._root / "data" / "security_alerts.json"
        alerts = []

        if alert_path.exists():
            with open(alert_path, 'r', encoding='utf-8') as f:
                alerts = json.load(f)

        alerts.append({
            "event_id": event.event_id,
            "severity": event.severity.name,
            "description": event.description,
            "timestamp": datetime.utcnow().isoformat(),
            "requires_review": True
        })

        with open(alert_path, 'w', encoding='utf-8') as f:
            json.dump(alerts, f, indent=2)

    def attempt_recovery(self) -> bool:
        """
        Attempt system recovery from degraded state.

        Returns:
            True if recovery successful, False otherwise
        """
        if self._degradation_level == 0:
            return True

        state_path = self._root / "data" / "substrate_tree.json"
        if not state_path.exists():
            return False

        try:
            with open(state_path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            isolated_count = sum(
                1 for s in state if s.get("status") == "ISOLATED"
            )

            if isolated_count == 0:
                # Clear degradation progressively
                for _ in range(RECOVERY_ITERATION_COUNT):
                    if self._degradation_level > 0:
                        self._degradation_level -= 1

                if self._degradation_level == 0:
                    state_file = self._root / "data" / "system_degradation.json"
                    if state_file.exists():
                        state_file.unlink()
                    logger.info("System recovery complete.")
                    return True

        except Exception as e:
            logger.error(f"Recovery failed: {e}")

        return False

    @property
    def degradation_level(self) -> int:
        """Current degradation level."""
        return self._degradation_level


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: MAIN SYSTEM ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

class AdaptiveThreatDetectionSystem:
    """
    Central coordinator for threat detection and response.

    Integrates:
    - Signature-based detection
    - Anomaly-based detection
    - Adaptive learning
    - Fault tolerance

    Usage:
        system = AdaptiveThreatDetectionSystem(repo_root)
        is_safe, event = system.evaluate(feature_vector, metadata)
        if not is_safe:
            # Handle threat
    """

    def __init__(self, repo_root: Path):
        self._root = repo_root

        # Initialize components
        self._signature_store = SignatureStore(
            repo_root / "data" / "threat_signatures.json"
        )
        self._perimeter = AdaptiveSecurityPerimeter(
            repo_root / "config" / "security_perimeter.json"
        )
        self._fault_manager = FaultToleranceManager(repo_root)

        # Detection engines
        self._signature_detector = SignatureBasedDetector(self._signature_store)
        self._anomaly_detector = AnomalyBasedDetector()
        self._pattern_learner = AdaptivePatternLearner(self._signature_store)

        # Event history
        self._event_history: List[SecurityEvent] = []

        logger.info("Adaptive Threat Detection System initialized.")

    def evaluate(
        self,
        feature_vector: np.ndarray,
        metadata: Optional[Dict] = None
    ) -> Tuple[bool, Optional[SecurityEvent]]:
        """
        Evaluate input against all detection mechanisms.

        Args:
            feature_vector: N-dimensional feature representation
            metadata: Additional context (source, timestamp, etc.)

        Returns:
            Tuple of (is_permitted, security_event_if_detected)
        """
        metadata = metadata or {}

        # Phase 1: Perimeter check
        permitted, violation_msg = self._perimeter.check_boundary(feature_vector)
        if not permitted:
            event = self._create_event(
                SeverityLevel.HIGH,
                ThreatCategory.BOUNDARY_VIOLATION,
                metadata.get("source", "unknown"),
                violation_msg,
                feature_vector
            )
            self._handle_detection(event)
            return False, event

        # Phase 2: Signature matching
        matched_signature = self._signature_detector.detect(feature_vector, metadata)
        if matched_signature:
            event = self._create_event(
                SeverityLevel.MEDIUM,
                matched_signature.category,
                metadata.get("source", "unknown"),
                f"Matched signature: {matched_signature.signature_id}",
                feature_vector
            )
            matched_signature.occurrence_count += 1
            matched_signature.last_seen = datetime.utcnow().isoformat()
            self._signature_store._save()
            self._handle_detection(event)
            return False, event

        return True, None

    def monitor_metrics(
        self,
        current_metrics: Dict[str, float]
    ) -> List[SecurityEvent]:
        """
        Evaluate system metrics for anomalies.

        Args:
            current_metrics: Current system state metrics

        Returns:
            List of detected security events
        """
        anomalies = self._anomaly_detector.detect(current_metrics)
        events = []

        for metric_name, deviation, severity in anomalies:
            event = self._create_event(
                severity,
                ThreatCategory.BEHAVIORAL_ANOMALY,
                "metrics_monitor",
                f"Anomaly in {metric_name}: {deviation:.1%} deviation",
                None
            )
            events.append(event)
            if severity.value >= SeverityLevel.MEDIUM.value:
                self._handle_detection(event)

        return events

    def calibrate_baseline(self, metrics: Dict[str, float]):
        """
        Set baseline metrics for anomaly detection.

        Args:
            metrics: Dictionary of metric_name -> healthy_value
        """
        self._anomaly_detector.calibrate(metrics)

    def _handle_detection(self, event: SecurityEvent):
        """Process detected security event."""
        self._event_history.append(event)

        # Learn from event
        self._pattern_learner.ingest_event(event)

        # Execute response
        response = self._fault_manager.execute_response(event)
        event.response_actions = ", ".join(response["actions"])

        # Adaptive perimeter update
        if event.category == ThreatCategory.BOUNDARY_VIOLATION and event.feature_vector:
            self._perimeter.create_zone(
                np.array(event.feature_vector),
                f"Auto-generated: {event.description}"
            )

        logger.warning(
            f"Security event [{event.severity.name}]: {event.response_actions}"
        )

    def _create_event(
        self,
        severity: SeverityLevel,
        category: ThreatCategory,
        source: str,
        description: str,
        vector: Optional[np.ndarray]
    ) -> SecurityEvent:
        """Construct security event record."""
        return SecurityEvent(
            event_id=f"evt_{int(time.time() * 1000)}",
            timestamp=datetime.utcnow().isoformat(),
            severity=severity,
            category=category,
            source_identifier=source,
            description=description,
            feature_vector=vector.tolist() if vector is not None else None
        )

    def get_status(self) -> Dict:
        """
        Return current system status.

        Returns:
            Dictionary with system health indicators
        """
        return {
            "degradation_level": self._fault_manager.degradation_level,
            "active_threats": len([e for e in self._event_history if not e.resolved]),
            "known_signatures": len(self._signature_store.get_active_signatures()),
            "security_zones": len(self._perimeter._zones),
            "total_events": len(self._event_history),
            "last_event": self._event_history[-1].timestamp if self._event_history else None,
            "status": (
                "NORMAL" if self._fault_manager.degradation_level == 0
                else f"DEGRADED_L{self._fault_manager.degradation_level}"
            )
        }

    def run_maintenance(self) -> Dict:
        """
        Execute periodic maintenance tasks.

        Returns:
            Maintenance report
        """
        recovered = self._fault_manager.attempt_recovery()
        self._signature_store.prune_expired()

        return {
            "recovery_attempted": True,
            "recovered": recovered,
            "degradation_level": self._fault_manager.degradation_level,
            "active_signatures": len(self._signature_store.get_active_signatures())
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: MODULE INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

_instance: Optional[AdaptiveThreatDetectionSystem] = None


def get_threat_detection_system(
    repo_root: Optional[Path] = None
) -> AdaptiveThreatDetectionSystem:
    """
    Singleton accessor for threat detection system.

    Args:
        repo_root: Repository root path (auto-detected if None)

    Returns:
        AdaptiveThreatDetectionSystem instance
    """
    global _instance
    if _instance is None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[2]
        _instance = AdaptiveThreatDetectionSystem(repo_root)
    return _instance


def evaluate_intent(
    intent_vector: np.ndarray,
    metadata: Optional[Dict] = None
) -> Tuple[bool, Optional[str]]:
    """
    Convenience function for intent evaluation.

    Drop-in replacement for legacy GeometricFirewall.audit_intent().

    Args:
        intent_vector: Feature vector to evaluate
        metadata: Additional context

    Returns:
        Tuple of (is_permitted, error_message)
    """
    system = get_threat_detection_system()
    is_safe, event = system.evaluate(intent_vector, metadata)
    if not is_safe and event:
        return False, event.description
    return True, None
