# Security Guide

## Authentication
- **Message bus**: protect `/publish` and `/get` with a bearer token set in the `BUS_TOKEN` env var.
  - Example: `curl "$BUS_URL/health" -H "Authorization: Bearer $BUS_TOKEN"`
- **Agent server**: require `AGENT_SHARED_SECRET` for all requests.
  - Example: `curl ip/health -H "Authorization: Bearer $AGENT_SHARED_SECRET"`
  - If `AGENT_SHARED_SECRET` is unset, the server logs a warning and responds with `401 Unauthorized`.
  - Tokens are compared using `hmac.compare_digest` to avoid timing attacks.
- Store secrets in environment variables and rotate them regularly.
- Unauthorized bearer tokens are masked before being logged to the knowledge base.
- Topics published to the bus must be alphanumeric or underscore; invalid names are rejected.

## Authorization
- The CEO policy engine (`admin_policy.py`) enforces high-level rules over agent actions.
- PowerShell allow/deny lists restrict which commands can be executed by scripts.

## Hardening
- Run services behind TLS and limit network exposure.
- Keep the GPIA Ollama host bound to loopback unless explicitly proxied.
- Use long, random tokens and change them periodically.
- Log and monitor `auth_failure` events from the knowledge base.
- Keep dependencies patched and apply the principle of least privilege for file and process permissions.

## Token Rotation
- Generate a new random token.
- Update the `BUS_TOKEN` environment variable on the bus server and all clients.
- The server checks the environment on every request, so rotation does not require a restart.
- Immediately verify access with the new token and revoke any copies of the old one.
