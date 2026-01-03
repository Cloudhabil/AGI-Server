#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
root="$here/.."

echo "== Dev Up (serial, one after the other) =="

cd "$root"

if [ ! -d venv ]; then
  echo "Creating virtual environment (venv)..."
  python3 -m venv venv
fi
venv_py="venv/bin/python"

echo "Installing backend dependencies..."
"$venv_py" -m pip install --upgrade pip
"$venv_py" -m pip install -r requirements.txt

export AGENT_SHARED_SECRET="${AGENT_SHARED_SECRET:-devsecret}"

# Optional bus
if [[ "${WITH_BUS:-0}" == "1" ]]; then
  if command -v docker >/dev/null 2>&1; then
    if ! docker ps --format '{{.Names}}' | grep -q '^redis$'; then
      echo "Starting Redis container..."
      docker run -d --name redis -p 6379:6379 redis:7 >/dev/null
    fi
  else
    echo "Docker not found; expecting Redis at localhost:6379" >&2
  fi

  export BUS_TOKEN="${BUS_TOKEN:-devbus}"
  echo "Starting bus server in background..."
  "$venv_py" -m uvicorn bus_server:app --host 127.0.0.1 --port 7088 --reload &
  bus_pid=$!
  # health wait
  for i in {1..45}; do
    if curl -sf http://127.0.0.1:7088/health >/dev/null; then break; fi
    sleep 1
  done
fi

echo "Starting backend in background..."
"$venv_py" -m uvicorn agent_server:app --host 127.0.0.1 --port 8000 --reload &
back_pid=$!

for i in {1..60}; do
  if curl -sf http://127.0.0.1:8000/health >/dev/null; then break; fi
  sleep 1
done

echo "Installing frontend deps..."
cd frontend
npm install

echo "Starting frontend (foreground)... Open http://localhost:5173"
trap 'echo stopping...; kill ${back_pid:-0} ${bus_pid:-0} 2>/dev/null || true' INT TERM EXIT
npm run dev -- --host 0.0.0.0
