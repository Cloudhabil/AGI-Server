"""Deterministic MCP end-to-end demo runner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.mcp_skill.interfaces import PolicyDecision
from core.mcp_skill.mcp_skill import DefaultPolicyEnforcer, McpSkill, SchemaValidator
from core.mcp_skill.orchestrator import (
    DeterministicVerifier,
    FileAuditLogger,
    McpOrchestrator,
    Plan,
    PlanStep,
)


class DemoRegistry:
    def list_servers(self) -> Sequence[str]:
        return ["demo"]

    def list_tools(self, server: str) -> Sequence[str]:
        return ["echo"]

    def get_tool_schema(self, server: str, tool: str) -> Dict[str, Any]:
        return {
            "parameters": {
                "required": ["text"],
                "properties": {"text": {"type": "string"}},
            }
        }


class DemoAuth:
    def get_token(self, server: str) -> str:
        return "demo-token"

    def refresh(self, server: str) -> str:
        return "demo-token"


class DemoInvoker:
    def invoke_tool(self, server: str, tool: str, args: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        SchemaValidator.validate(schema, args)
        return {"result": "OK", "echo": args.get("text", "")}


class DemoPlanner:
    def plan(self, goal: str, constraints: Dict[str, Any], env_context: Dict[str, Any]) -> Plan:
        return Plan(
            steps=[PlanStep(tool="echo", args={"text": goal})],
            final_success_criteria=["OK"],
        )


class AllowPolicy(DefaultPolicyEnforcer):
    def evaluate_call(self, call, context):
        decision = super().evaluate_call(call, context)
        return PolicyDecision(
            allowed=decision.allowed,
            reason=decision.reason,
            requires_manual=decision.requires_manual,
            risk_tier=decision.risk_tier,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic MCP pipeline demo.")
    parser.add_argument("--goal", required=True, help="Goal string for MCP orchestration.")
    args = parser.parse_args()

    audit = FileAuditLogger()
    policy = AllowPolicy()
    mcp_skill = McpSkill(
        registry=DemoRegistry(),
        auth=DemoAuth(),
        invoker=DemoInvoker(),
        policy=policy,
        audit=audit,
    )
    orchestrator = McpOrchestrator(
        mcp_skill=mcp_skill,
        planner=DemoPlanner(),
        verifier=DeterministicVerifier(),
        policy=policy,
        audit=audit,
    )

    result = orchestrator.run(
        goal=args.goal,
        constraints={},
        env_context={"mode": "demo"},
        available_servers=["demo"],
    )

    payload = {
        "status": result.status,
        "trace_id": result.trace_id,
        "verified": result.verified,
        "committed": result.committed,
        "errors": result.errors,
    }
    print(json.dumps(payload, indent=2))
    return 0 if result.status == "DONE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
