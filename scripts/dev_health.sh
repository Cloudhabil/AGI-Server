#!/usr/bin/env bash
set -euo pipefail

backend_url="${BACKEND_URL:-http://127.0.0.1:8000/health}"
frontend_url="${FRONTEND_URL:-http://localhost:5173}"
bus_url="${BUS_URL_HEALTH:-http://127.0.0.1:7088/health}"

echo '== Health Check =='

if curl -sf "$backend_url" >/dev/null; then
  echo "backend: $backend_url 200"
else
  echo "backend: $backend_url unreachable" >&2
fi

if curl -sf "$frontend_url" >/dev/null; then
  echo "frontend: $frontend_url 200"
else
  echo "frontend: $frontend_url unreachable" >&2
fi

if curl -sf "$bus_url" >/dev/null; then
  echo "bus: $bus_url 200"
else
  echo "bus: $bus_url unreachable" >&2
fi

# Redis TCP
host=127.0.0.1; port=6379
if command -v nc >/dev/null 2>&1; then
  if nc -z "$host" "$port"; then echo "redis: $host:$port open"; else echo "redis: $host:$port closed"; fi
else
  (echo > "/dev/tcp/$host/$port") >/dev/null 2>&1 && echo "redis: $host:$port open" || echo "redis: $host:$port closed"
fi

