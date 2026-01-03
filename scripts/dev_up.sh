#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
root="$here/.."

echo "== Dev Up (backend, frontend, optional bus) =="

# Frontend
bash "$here/dev_frontend.sh" &
pid_front=$!
echo "frontend pid: $pid_front"

# Backend
bash "$here/dev_backend.sh" &
pid_back=$!
echo "backend pid: $pid_back"

# Bus (optional if redis available)
if command -v docker >/dev/null 2>&1; then
  if ! docker ps --format '{{.Names}}' | grep -q '^redis$'; then
    echo "Starting Redis docker container..."
    docker run -d --name redis -p 6379:6379 redis:7 >/dev/null
  fi
  (
    cd "$root"
    export BUS_TOKEN="${BUS_TOKEN:-devbus}"
    uvicorn bus_server:app --reload --host 127.0.0.1 --port 7088
  ) &
  pid_bus=$!
  echo "bus pid: $pid_bus"
else
  echo "Docker not found; skipping Redis and bus_server."
fi

echo "Press Ctrl+C to stop. Child processes will receive SIGINT."
wait

