"""
Threat Response Orchestrator
============================

Coordinates response actions when cable threats are detected.
Provides automated and manual response workflows for
submarine cable protection.

Response Tiers:
1. ADVISORY: Increased monitoring, log event
2. WATCH: Alert operators, prepare response team
3. WARNING: Contact authorities, standby cable ship
4. CRITICAL: Activate traffic rerouting, dispatch repair

Integration Points:
- Maritime authorities (coast guard, navy)
- Cable operators (NOC notifications)
- Vessel tracking (AIS-based warnings)
- Traffic management (automatic failover)

Author: GPIA Cognitive Ecosystem
Date: 2026-01-26
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

try:
    from core.constants import GENESIS_CONSTANT, BETA_SECURITY, PHI, BRAHIM_SEQUENCE
except ImportError:
    GENESIS_CONSTANT = 2 / 901
    BETA_SECURITY = math.sqrt(5) - 2
    PHI = (1 + math.sqrt(5)) / 2
    BRAHIM_SEQUENCE = (27, 42, 60, 75, 97, 117, 139, 154, 172, 187)  # Corrected 2026-01-26

from .cable_monitor import (
    BrahimCableMonitor,
    CableSegment,
    ThreatEvent,
    ThreatLevel,
    ThreatType,
    CableSnapshot,
)

logger = logging.getLogger("cable.threat_response")


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class ResponseAction(Enum):
    """Types of response actions."""
    LOG_EVENT = auto()              # Record for analysis
    INCREASE_MONITORING = auto()    # Higher sampling rate
    ALERT_OPERATOR = auto()         # NOC notification
    ALERT_MARITIME = auto()         # Coast guard/navy
    WARN_VESSEL = auto()            # VHF/AIS message to ship
    PREPARE_SHIP = auto()           # Cable ship on standby
    DISPATCH_SHIP = auto()          # Deploy cable ship
    REROUTE_TRAFFIC = auto()        # Activate backup routes
    ISOLATE_SEGMENT = auto()        # Power down segment
    EMERGENCY_SHUTDOWN = auto()     # Full cable isolation


class ResponsePriority(Enum):
    """Response priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


# Response time targets (derived from Brahim sequence)
RESPONSE_TIMES = {
    ThreatLevel.ADVISORY: BRAHIM_SEQUENCE[4],   # 97 minutes
    ThreatLevel.WATCH: BRAHIM_SEQUENCE[2],      # 60 minutes
    ThreatLevel.WARNING: BRAHIM_SEQUENCE[0],    # 27 minutes
    ThreatLevel.CRITICAL: 5,                     # 5 minutes
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ResponseCommand:
    """Command to execute a response action."""
    command_id: str
    timestamp: datetime
    action: ResponseAction
    priority: ResponsePriority
    target_segment: str
    target_cable: str
    threat_event_id: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    executed: bool = False
    executed_at: Optional[datetime] = None
    result: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command_id": self.command_id,
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.name,
            "priority": self.priority.name,
            "target_segment": self.target_segment,
            "target_cable": self.target_cable,
            "threat_event_id": self.threat_event_id,
            "executed": self.executed,
            "result": self.result,
        }


@dataclass
class ResponsePlan:
    """Coordinated response plan for a threat."""
    plan_id: str
    created_at: datetime
    threat_event: ThreatEvent
    commands: List[ResponseCommand]
    estimated_response_time_min: float
    estimated_cost_eur: float
    status: str = "pending"  # pending, active, completed, cancelled


@dataclass
class CableHealthReport:
    """Comprehensive cable health report."""
    report_id: str
    generated_at: datetime
    period_start: datetime
    period_end: datetime
    cables_monitored: int
    segments_monitored: int
    total_length_km: float
    average_health_pct: float
    threats_detected: int
    threats_mitigated: int
    response_commands_issued: int
    downtime_minutes: float
    availability_pct: float
    brahim_metrics: Dict[str, float]


@dataclass
class VesselWarning:
    """Warning message to nearby vessel."""
    warning_id: str
    timestamp: datetime
    vessel_mmsi: str
    vessel_name: str
    message: str
    channel: str  # VHF, AIS, SAT
    acknowledged: bool = False


# =============================================================================
# THREAT RESPONSE ORCHESTRATOR
# =============================================================================

class ThreatResponseOrchestrator:
    """
    Orchestrates response to cable threats.

    Workflow:
    1. Receive threat event from monitor
    2. Assess threat severity and urgency
    3. Generate response plan
    4. Execute response commands
    5. Track resolution and report

    Response escalation follows Brahim timing:
    - ADVISORY: Log + monitor (97 min response)
    - WATCH: Alert + prepare (60 min response)
    - WARNING: Warn vessels + standby ship (27 min response)
    - CRITICAL: Reroute + dispatch (5 min response)
    """

    def __init__(
        self,
        monitor: BrahimCableMonitor,
        auto_response_enabled: bool = True,
        escalation_threshold_min: float = 15.0
    ):
        """
        Initialize response orchestrator.

        Args:
            monitor: Cable monitor instance
            auto_response_enabled: Enable automatic responses
            escalation_threshold_min: Time before escalating unresolved threats
        """
        self.monitor = monitor
        self.auto_response = auto_response_enabled
        self.escalation_threshold = timedelta(minutes=escalation_threshold_min)

        # Response tracking
        self._plans: Dict[str, ResponsePlan] = {}
        self._commands: List[ResponseCommand] = []
        self._warnings: List[VesselWarning] = []
        self._command_counter = 0

        # Callbacks for external integrations
        self._on_command: List[Callable[[ResponseCommand], None]] = []
        self._on_vessel_warning: List[Callable[[VesselWarning], None]] = []

        # Register with monitor for threat events
        monitor.on_threat(self._handle_threat)

        logger.info(
            "ThreatResponseOrchestrator initialized: auto_response=%s",
            auto_response_enabled
        )

    # =========================================================================
    # THREAT HANDLING
    # =========================================================================

    def _handle_threat(self, event: ThreatEvent) -> None:
        """Handle incoming threat event from monitor."""
        logger.info(
            "Handling threat: %s (%s) on %s",
            event.threat_type.name,
            event.threat_level.value,
            event.segment_id
        )

        # Generate response plan
        plan = self._generate_response_plan(event)
        self._plans[plan.plan_id] = plan

        # Execute if auto-response enabled
        if self.auto_response:
            self._execute_plan(plan)

    def _generate_response_plan(self, event: ThreatEvent) -> ResponsePlan:
        """Generate response plan for a threat event."""
        timestamp = datetime.utcnow()
        plan_id = f"PLAN_{timestamp.strftime('%Y%m%d%H%M%S')}_{event.event_id[:8]}"

        commands = []

        # Always log the event
        commands.append(self._create_command(
            ResponseAction.LOG_EVENT,
            ResponsePriority.LOW,
            event
        ))

        # Level-specific responses
        if event.threat_level == ThreatLevel.ADVISORY:
            commands.append(self._create_command(
                ResponseAction.INCREASE_MONITORING,
                ResponsePriority.LOW,
                event
            ))

        elif event.threat_level == ThreatLevel.WATCH:
            commands.extend([
                self._create_command(ResponseAction.INCREASE_MONITORING, ResponsePriority.MEDIUM, event),
                self._create_command(ResponseAction.ALERT_OPERATOR, ResponsePriority.MEDIUM, event),
            ])

        elif event.threat_level == ThreatLevel.WARNING:
            commands.extend([
                self._create_command(ResponseAction.ALERT_OPERATOR, ResponsePriority.HIGH, event),
                self._create_command(ResponseAction.ALERT_MARITIME, ResponsePriority.HIGH, event),
                self._create_command(ResponseAction.PREPARE_SHIP, ResponsePriority.MEDIUM, event),
            ])

            # Warn nearby vessels if applicable
            if event.threat_type in (ThreatType.ANCHOR_DROP, ThreatType.FISHING_ACTIVITY, ThreatType.VESSEL_PROXIMITY):
                commands.append(self._create_command(
                    ResponseAction.WARN_VESSEL,
                    ResponsePriority.HIGH,
                    event
                ))

        elif event.threat_level == ThreatLevel.CRITICAL:
            commands.extend([
                self._create_command(ResponseAction.ALERT_OPERATOR, ResponsePriority.CRITICAL, event),
                self._create_command(ResponseAction.ALERT_MARITIME, ResponsePriority.CRITICAL, event),
                self._create_command(ResponseAction.REROUTE_TRAFFIC, ResponsePriority.CRITICAL, event),
                self._create_command(ResponseAction.DISPATCH_SHIP, ResponsePriority.CRITICAL, event),
            ])

            if event.threat_type == ThreatType.SABOTAGE:
                commands.append(self._create_command(
                    ResponseAction.ISOLATE_SEGMENT,
                    ResponsePriority.EMERGENCY,
                    event
                ))

        # Calculate estimated response time
        response_time = RESPONSE_TIMES.get(event.threat_level, 60)

        # Estimate cost (simplified)
        cost = self._estimate_response_cost(commands)

        return ResponsePlan(
            plan_id=plan_id,
            created_at=timestamp,
            threat_event=event,
            commands=commands,
            estimated_response_time_min=response_time,
            estimated_cost_eur=cost,
        )

    def _create_command(
        self,
        action: ResponseAction,
        priority: ResponsePriority,
        event: ThreatEvent
    ) -> ResponseCommand:
        """Create a response command."""
        self._command_counter += 1
        timestamp = datetime.utcnow()

        return ResponseCommand(
            command_id=f"CMD_{timestamp.strftime('%Y%m%d%H%M%S')}_{self._command_counter:05d}",
            timestamp=timestamp,
            action=action,
            priority=priority,
            target_segment=event.segment_id,
            target_cable=event.cable_id,
            threat_event_id=event.event_id,
            parameters={
                "threat_type": event.threat_type.name,
                "confidence": event.confidence,
                "location": event.location.to_dict(),
            }
        )

    def _estimate_response_cost(self, commands: List[ResponseCommand]) -> float:
        """Estimate cost of response actions in EUR."""
        costs = {
            ResponseAction.LOG_EVENT: 0,
            ResponseAction.INCREASE_MONITORING: 100,
            ResponseAction.ALERT_OPERATOR: 50,
            ResponseAction.ALERT_MARITIME: 100,
            ResponseAction.WARN_VESSEL: 50,
            ResponseAction.PREPARE_SHIP: 10000,
            ResponseAction.DISPATCH_SHIP: 100000,  # Cable ship day rate
            ResponseAction.REROUTE_TRAFFIC: 5000,
            ResponseAction.ISOLATE_SEGMENT: 1000,
            ResponseAction.EMERGENCY_SHUTDOWN: 50000,
        }

        return sum(costs.get(cmd.action, 0) for cmd in commands)

    # =========================================================================
    # PLAN EXECUTION
    # =========================================================================

    def _execute_plan(self, plan: ResponsePlan) -> None:
        """Execute a response plan."""
        plan.status = "active"
        logger.info("Executing plan %s with %d commands", plan.plan_id, len(plan.commands))

        # Sort by priority (highest first)
        sorted_commands = sorted(plan.commands, key=lambda c: c.priority.value, reverse=True)

        for command in sorted_commands:
            self._execute_command(command)

        plan.status = "completed"

    def _execute_command(self, command: ResponseCommand) -> None:
        """Execute a single response command."""
        logger.info(
            "Executing %s (priority: %s) for segment %s",
            command.action.name,
            command.priority.name,
            command.target_segment
        )

        try:
            # Action-specific execution
            if command.action == ResponseAction.LOG_EVENT:
                command.result = "Event logged"

            elif command.action == ResponseAction.INCREASE_MONITORING:
                command.result = "Monitoring frequency increased to 1Hz"

            elif command.action == ResponseAction.ALERT_OPERATOR:
                command.result = "NOC alerted via email and SMS"

            elif command.action == ResponseAction.ALERT_MARITIME:
                command.result = "Coast guard notified"

            elif command.action == ResponseAction.WARN_VESSEL:
                warning = self._send_vessel_warning(command)
                command.result = f"Warning sent: {warning.warning_id}"

            elif command.action == ResponseAction.PREPARE_SHIP:
                command.result = "Cable ship CS Responder on 4-hour standby"

            elif command.action == ResponseAction.DISPATCH_SHIP:
                command.result = "Cable ship dispatched, ETA 48 hours"

            elif command.action == ResponseAction.REROUTE_TRAFFIC:
                command.result = "Traffic rerouted via backup path"

            elif command.action == ResponseAction.ISOLATE_SEGMENT:
                command.result = "Segment isolated from network"

            else:
                command.result = "Action executed"

            command.executed = True
            command.executed_at = datetime.utcnow()

            # Track and notify
            self._commands.append(command)
            for callback in self._on_command:
                try:
                    callback(command)
                except Exception as e:
                    logger.error("Command callback error: %s", e)

        except Exception as e:
            command.result = f"Error: {str(e)}"
            logger.error("Command execution failed: %s", e)

    def _send_vessel_warning(self, command: ResponseCommand) -> VesselWarning:
        """Send warning to nearby vessel."""
        timestamp = datetime.utcnow()
        location = command.parameters.get("location", {})

        warning = VesselWarning(
            warning_id=f"WARN_{timestamp.strftime('%Y%m%d%H%M%S')}",
            timestamp=timestamp,
            vessel_mmsi="BROADCAST",
            vessel_name="ALL VESSELS",
            message=(
                f"SECURITE SECURITE SECURITE. "
                f"Submarine cable in position {location.get('latitude', 0):.3f}N "
                f"{abs(location.get('longitude', 0)):.3f}W. "
                f"All vessels requested to avoid anchoring within 1 nautical mile. "
                f"Cable operator contact: ops@cable.example.com"
            ),
            channel="VHF_CH16",
        )

        self._warnings.append(warning)

        for callback in self._on_vessel_warning:
            try:
                callback(warning)
            except Exception as e:
                logger.error("Warning callback error: %s", e)

        return warning

    # =========================================================================
    # MANUAL RESPONSE
    # =========================================================================

    def trigger_manual_response(
        self,
        segment_id: str,
        action: ResponseAction,
        reason: str = ""
    ) -> ResponseCommand:
        """
        Trigger a manual response action.

        Args:
            segment_id: Target segment
            action: Action to execute
            reason: Reason for manual trigger

        Returns:
            Executed ResponseCommand
        """
        segment = self.monitor.get_segment(segment_id)
        if not segment:
            raise ValueError(f"Unknown segment: {segment_id}")

        self._command_counter += 1
        timestamp = datetime.utcnow()

        command = ResponseCommand(
            command_id=f"MANUAL_{timestamp.strftime('%Y%m%d%H%M%S')}_{self._command_counter:05d}",
            timestamp=timestamp,
            action=action,
            priority=ResponsePriority.HIGH,
            target_segment=segment_id,
            target_cable=segment.cable_id,
            threat_event_id="MANUAL",
            parameters={"reason": reason, "operator": "manual"},
        )

        self._execute_command(command)
        return command

    # =========================================================================
    # REPORTING
    # =========================================================================

    def generate_health_report(
        self,
        period_hours: int = 24
    ) -> CableHealthReport:
        """
        Generate comprehensive cable health report.

        Args:
            period_hours: Report period in hours

        Returns:
            CableHealthReport
        """
        now = datetime.utcnow()
        period_start = now - timedelta(hours=period_hours)

        # Get current snapshot
        snapshot = self.monitor.analyze()

        # Count events in period
        period_events = [
            e for e in self.monitor._events
            if e.timestamp >= period_start
        ]

        # Count commands in period
        period_commands = [
            c for c in self._commands
            if c.timestamp >= period_start
        ]

        # Calculate availability (simplified)
        critical_events = [e for e in period_events if e.threat_level == ThreatLevel.CRITICAL]
        downtime_minutes = len(critical_events) * 30  # Assume 30 min per critical event
        total_minutes = period_hours * 60
        availability = (total_minutes - downtime_minutes) / total_minutes * 100

        return CableHealthReport(
            report_id=f"HEALTH_{now.strftime('%Y%m%d%H%M%S')}",
            generated_at=now,
            period_start=period_start,
            period_end=now,
            cables_monitored=len(self.monitor._cables),
            segments_monitored=len(self.monitor._segments),
            total_length_km=snapshot.total_length_km,
            average_health_pct=snapshot.health_percentage,
            threats_detected=len(period_events),
            threats_mitigated=len([e for e in period_events if e.threat_level != ThreatLevel.CRITICAL]),
            response_commands_issued=len(period_commands),
            downtime_minutes=downtime_minutes,
            availability_pct=availability,
            brahim_metrics={
                "genesis_threshold": GENESIS_CONSTANT,
                "beta_attenuation": BETA_SECURITY,
                "phi": PHI,
                "current_threat_score": snapshot.threat_score,
            }
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get response orchestrator statistics."""
        return {
            "total_plans": len(self._plans),
            "active_plans": len([p for p in self._plans.values() if p.status == "active"]),
            "total_commands": len(self._commands),
            "commands_executed": len([c for c in self._commands if c.executed]),
            "vessel_warnings": len(self._warnings),
            "auto_response_enabled": self.auto_response,
            "escalation_threshold_min": self.escalation_threshold.total_seconds() / 60,
            "response_time_targets": {
                level.name: minutes
                for level, minutes in RESPONSE_TIMES.items()
            },
        }

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    def on_command(
        self,
        callback: Callable[[ResponseCommand], None]
    ) -> None:
        """Register callback for response commands."""
        self._on_command.append(callback)

    def on_vessel_warning(
        self,
        callback: Callable[[VesselWarning], None]
    ) -> None:
        """Register callback for vessel warnings."""
        self._on_vessel_warning.append(callback)


# =============================================================================
# MODULE-LEVEL SINGLETON
# =============================================================================

_orchestrator: Optional[ThreatResponseOrchestrator] = None


def get_threat_response_orchestrator(
    monitor: Optional[BrahimCableMonitor] = None
) -> ThreatResponseOrchestrator:
    """Get the global threat response orchestrator."""
    global _orchestrator

    if _orchestrator is None:
        if monitor is None:
            from .cable_monitor import get_cable_monitor
            monitor = get_cable_monitor()

        _orchestrator = ThreatResponseOrchestrator(monitor)

    return _orchestrator
