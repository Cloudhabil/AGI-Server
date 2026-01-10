Design note: The MCP orchestration pipeline is invoked from the CLI flow in
`src/core/modes/sovereign_loop.py` when a command starts with `mcp ` or `mcp:`.
If no MCP servers are available, planning is not configured, or a policy blocks
the call, the pipeline returns `DEGRADED` or `BLOCKED` and emits an audit trace
without invoking any tools.

# MCP Skill

## Contract

The MCP Skill provides a single entrypoint for tool usage, and the MCP
orchestrator wraps the full pipeline:

- Input: `goal`, `constraints`, `available_servers`
- Output: `McpResult` with tool outputs, provenance, audit trace, and errors

The orchestrator entrypoint:

- Input: `goal`, `constraints`, `env_context`, `available_servers`
- Output: `OrchestratorResult` with status, plan, tool outputs, and audit trail

All tool calls are evaluated by the policy enforcer and can be blocked
by manual gate requirements (network, filesystem writes, credentials, or exfil patterns).

## State Machine

States:

- INIT -> DISCOVER -> AUTH -> DESCRIBE -> PLAN -> EXECUTE -> OBSERVE -> VERIFY -> COMMIT
- Terminal: DONE, FAILED, BLOCKED, DEGRADED

Transitions are driven by events such as `servers_listed`, `auth_ok`,
`tool_schema_loaded`, `plan_ready`, `call_ok`, `call_error`, and `policy_block`.
Retry budgets and timeouts are configured in `src/core/mcp_skill/state_machine.py`.

The LLM planner response is validated against a strict key set; extra keys
cause the plan to be rejected.

## Failure Modes

- No MCP servers available: returns `DEGRADED` with `no_mcp_servers_available`
- Policy blocked call: returns `BLOCKED` with an audit entry
- Schema validation failure: returns `DEGRADED` with schema error details
- Invocation failures beyond retry budget: returns `DEGRADED`

## Registering MCP Servers

Implement `McpRegistry` and inject it into `McpSkill`. The registry must
expose servers, tools, and schemas:

- `list_servers()`
- `list_tools(server)`
- `get_tool_schema(server, tool)`

Supply the registry when creating the skill instance, or replace the default
registry in `get_default_mcp_skill()` in `src/core/mcp_skill/mcp_skill.py`.

## Planner and Verifier Configuration

The orchestrator requires a planner. Provide model config in constraints:

- `planner_kind`, `planner_endpoint`, `planner_model`
- `verifier_kind`, `verifier_endpoint`, `verifier_model` (optional)

If a verifier is not configured, the deterministic verifier is used and requires
explicit success criteria in the plan.
