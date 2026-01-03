#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== Backend Dev Helper (bash) =="

if [ ! -d venv ]; then
  echo "Creating virtual environment (venv)..."
  python3 -m venv venv
fi

venv_py="venv/bin/python"

echo "Upgrading pip and installing requirements..."
"$venv_py" -m pip install --upgrade pip
"$venv_py" -m pip install -r requirements.txt

export AGENT_SHARED_SECRET="${AGENT_SHARED_SECRET:-devsecret}"
echo "Using AGENT_SHARED_SECRET=$AGENT_SHARED_SECRET"

echo "Starting backend: venv/bin/python -m uvicorn agent_server:app --reload --host 127.0.0.1 --port 8000"
exec "$venv_py" -m uvicorn agent_server:app --reload --host 127.0.0.1 --port 8000
