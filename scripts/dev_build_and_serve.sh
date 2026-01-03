#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo '== Build frontend =='
(
  cd frontend
  npm install
  npm run build
)
dist="$(cd frontend/dist && pwd)"
echo "Serving SPA from: $dist"

if [ ! -d venv ]; then python3 -m venv venv; fi
venv_py="venv/bin/python"
"$venv_py" -m pip install --upgrade pip
"$venv_py" -m pip install -r requirements.txt

export AGENT_SHARED_SECRET="${AGENT_SHARED_SECRET:-devsecret}"
export SERVE_SPA_DIST="$dist"
"$venv_py" -m uvicorn agent_server:app --host 127.0.0.1 --port 8000
