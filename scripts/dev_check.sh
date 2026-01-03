#!/usr/bin/env bash
set -euo pipefail

echo '== Dev Diagnostics =='

# Flags: --lint, --tests (or env: LINT=1 TESTS=1)
LINT_FLAG=${LINT:-0}
TESTS_FLAG=${TESTS:-0}
for arg in "$@"; do
  case "$arg" in
    --lint) LINT_FLAG=1 ;;
    --tests) TESTS_FLAG=1 ;;
  esac
done

# Versions
PY_V=$(python3 --version 2>/dev/null || true)
NODE_V=$(node -v 2>/dev/null || true)
NPM_V=$(npm -v 2>/dev/null || true)
echo "python3: ${PY_V:-not found}"
echo "node:   ${NODE_V:-not found}"
echo "npm:    ${NPM_V:-not found}"
PY_OK=0; [ -n "${PY_V}" ] && PY_OK=1
NODE_OK=0; [ -n "${NODE_V}" ] && NODE_OK=1
NPM_OK=0; [ -n "${NPM_V}" ] && NPM_OK=1

# Venv
VENV_OK=0
PYDEPS_OK=0
if [ -d .venv ]; then
  echo '.venv: present'
  VENV_OK=1
  if [ -x .venv/bin/python ]; then
    if .venv/bin/python - <<'PY'
import sys
try:
    import fastapi, uvicorn  # noqa
    print('deps (fastapi, uvicorn): ok')
except Exception as e:
    print('deps check failed in venv:', e)
PY
    then PYDEPS_OK=1; else PYDEPS_OK=0; fi
  fi
else
  echo '.venv missing (run scripts/dev_backend.sh)'
fi

# Ports (best-effort)
check_port(){ port="$1"; if command -v lsof >/dev/null 2>&1; then lsof -i ":$port" -sTCP:LISTEN -P -n >/dev/null 2>&1; elif command -v ss >/dev/null 2>&1; then ss -ltnp | grep -q ":$port\>"; else netstat -ltnp 2>/dev/null | grep -q ":$port\>"; fi }
echo 'ports:'
if check_port 8000; then echo '  8000 (backend): LISTEN'; else echo '  8000 (backend): free'; fi
if check_port 7088; then echo '  7088 (bus):     LISTEN'; else echo '  7088 (bus):     free'; fi
if check_port 5173; then echo '  5173 (frontend): LISTEN'; else echo '  5173 (frontend): free'; fi
PORT_BACK_OK=0; check_port 8000 && PORT_BACK_OK=1 || true
PORT_BUS_OK=0; check_port 7088 && PORT_BUS_OK=1 || true
PORT_FE_OK=0; check_port 5173 && PORT_FE_OK=1 || true

# Env
[ -n "${AGENT_SHARED_SECRET:-}" ] && echo 'AGENT_SHARED_SECRET: set' || echo 'AGENT_SHARED_SECRET: missing'
[ -n "${BUS_TOKEN:-}" ] && echo 'BUS_TOKEN: set' || echo 'BUS_TOKEN: missing'
echo "BUS_URL: ${BUS_URL:-unset}"
ENV_AGENT_OK=0; [ -n "${AGENT_SHARED_SECRET:-}" ] && ENV_AGENT_OK=1
ENV_BUS_OK=0; [ -n "${BUS_TOKEN:-}" ] && ENV_BUS_OK=1

# HTTP health
"$(dirname "$0")/dev_health.sh" || true
BACKEND_URL=${BACKEND_URL:-http://127.0.0.1:8000/health}
FRONTEND_URL=${FRONTEND_URL:-http://localhost:5173}
BUS_HEALTH_URL=${BUS_URL_HEALTH:-http://127.0.0.1:7088/health}
HEALTH_BACK_OK=0; curl -sf "$BACKEND_URL" >/dev/null && HEALTH_BACK_OK=1 || true
HEALTH_FE_OK=0; curl -sf "$FRONTEND_URL" >/dev/null && HEALTH_FE_OK=1 || true
HEALTH_BUS_OK=0; curl -sf "$BUS_HEALTH_URL" >/dev/null && HEALTH_BUS_OK=1 || true

# Optional lint/tests
if [ "$LINT_FLAG" = "1" ] || [ "$TESTS_FLAG" = "1" ]; then
  echo '== Optional Checks =='
fi

if [ "$LINT_FLAG" = "1" ]; then
  if [ -x .venv/bin/python ]; then
    echo 'python lint: ruff .'
    if .venv/bin/python -m ruff .; then RUFF_OK=1; else RUFF_OK=0; echo 'ruff not available or failed'; fi
    echo 'python lint: flake8'
    if .venv/bin/python -m flake8; then FLAKE8_OK=1; else FLAKE8_OK=0; echo 'flake8 not available or failed'; fi
  fi
  if [ -f frontend/package.json ] && command -v npm >/dev/null 2>&1; then
    ( cd frontend
      if node -e "process.exit(require('./package.json').scripts?.lint?0:1)" 2>/dev/null; then
        echo 'frontend lint: npm run lint -s'
        if npm run lint -s; then FRONT_LINT_OK=1; else FRONT_LINT_OK=0; fi
      else
        echo 'frontend lint: no lint script found'
        FRONT_LINT_OK=
      fi
    )
  fi
fi

if [ "$TESTS_FLAG" = "1" ]; then
  if [ -x .venv/bin/python ]; then
    echo 'python tests: pytest -q'
    if .venv/bin/python -m pytest -q; then PYTEST_OK=1; else PYTEST_OK=0; echo 'pytest not available or failed'; fi
  fi
  if [ -f frontend/package.json ] && command -v npm >/dev/null 2>&1; then
    ( cd frontend
      if node -e "process.exit(require('./package.json').scripts?.test?0:1)" 2>/dev/null; then
        echo 'frontend tests: npm test -s'
        if npm test -s; then FRONT_TEST_OK=1; else FRONT_TEST_OK=0; fi
      else
        echo 'frontend tests: no test script found'
        FRONT_TEST_OK=
      fi
    )
  fi
fi

JSON_FLAG=0; for arg in "$@"; do [ "$arg" = "--json" ] && JSON_FLAG=1; done

if [ "$JSON_FLAG" = "1" ]; then
  # Print condensed JSON summary (no external deps)
  printf '{'
  printf '"meta":{"platform":"%s","shell":"bash"},' "$(uname -a | sed 's/"/\"/g')"
  printf '"versions":{"python":"%s","node":"%s","npm":"%s"},' "${PY_V}" "${NODE_V}" "${NPM_V}"
  printf '"venv":%s,' "$([ "$VENV_OK" = 1 ] && echo true || echo false)"
  printf '"pydeps":%s,' "$([ "$PYDEPS_OK" = 1 ] && echo true || echo false)"
  printf '"ports":{"backend":%s,"bus":%s,"frontend":%s},' "$([ "$PORT_BACK_OK" = 1 ] && echo true || echo false)" "$([ "$PORT_BUS_OK" = 1 ] && echo true || echo false)" "$([ "$PORT_FE_OK" = 1 ] && echo true || echo false)"
  printf '"env":{"AGENT_SHARED_SECRET":%s,"BUS_TOKEN":%s,"BUS_URL":"%s"},' "$([ "$ENV_AGENT_OK" = 1 ] && echo true || echo false)" "$([ "$ENV_BUS_OK" = 1 ] && echo true || echo false)" "${BUS_URL:-}"
  printf '"health":{"backend":%s,"bus":%s,"frontend":%s}' "$([ "$HEALTH_BACK_OK" = 1 ] && echo true || echo false)" "$([ "$HEALTH_BUS_OK" = 1 ] && echo true || echo false)" "$([ "$HEALTH_FE_OK" = 1 ] && echo true || echo false)"
  if [ "$LINT_FLAG" = "1" ]; then
    printf ',"lint":{"ruff":%s,"flake8":%s,"frontend":%s}' "${RUFF_OK:-null}" "${FLAKE8_OK:-null}" "${FRONT_LINT_OK:-null}"
  fi
  if [ "$TESTS_FLAG" = "1" ]; then
    printf ',"tests":{"pytest":%s,"frontend":%s}' "${PYTEST_OK:-null}" "${FRONT_TEST_OK:-null}"
  fi
  printf '}'
  echo
else
  echo '== Summary =='
  row(){ name="$1" ok="$2" note="${3:-}"; if [ -z "$ok" ]; then echo "[SKIP] $name $note"; elif [ "$ok" = 1 ]; then echo "[PASS] $name $note"; else echo "[FAIL] $name $note"; fi }
  row 'python' "$PY_OK" "$PY_V"
  row 'node' "$NODE_OK" "$NODE_V"
  row 'npm' "$NPM_OK" "$NPM_V"
  row '.venv' "$VENV_OK"
  row 'py deps (fastapi,uvicorn)' "$PYDEPS_OK"
  row 'port 8000 (backend)' "$PORT_BACK_OK"
  row 'port 7088 (bus)' "$PORT_BUS_OK"
  row 'port 5173 (frontend)' "$PORT_FE_OK"
  row 'env AGENT_SHARED_SECRET' "$ENV_AGENT_OK"
  row 'env BUS_TOKEN' "$ENV_BUS_OK"
  row 'health backend' "$HEALTH_BACK_OK"
  row 'health bus' "$HEALTH_BUS_OK"
  row 'health frontend' "$HEALTH_FE_OK"
  if [ "$LINT_FLAG" = "1" ]; then
    row 'ruff' "${RUFF_OK:-}"
    row 'flake8' "${FLAKE8_OK:-}"
    row 'frontend lint' "${FRONT_LINT_OK:-}"
  fi
  if [ "$TESTS_FLAG" = "1" ]; then
    row 'pytest' "${PYTEST_OK:-}"
    row 'frontend test' "${FRONT_TEST_OK:-}"
  fi
fi
