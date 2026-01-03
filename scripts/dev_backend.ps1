Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Push-Location $PSScriptRoot/..

Write-Host '== Backend Dev Helper ==' -ForegroundColor Cyan

if (-not (Test-Path venv)) {
  Write-Host 'Creating virtual environment (venv)...' -ForegroundColor Yellow
  python -m venv venv
}
$venvPy = Join-Path $PWD 'venv\Scripts\python.exe'

Write-Host 'Upgrading pip and installing requirements...' -ForegroundColor Yellow
& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install -r requirements.txt

if (-not $env:AGENT_SHARED_SECRET) {
  $env:AGENT_SHARED_SECRET = 'devsecret'
  Write-Host 'AGENT_SHARED_SECRET not set; using default for dev (devsecret).' -ForegroundColor DarkYellow
}

Write-Host 'Starting backend: venv\\Scripts\\python.exe -m uvicorn agent_server:app --reload --host 127.0.0.1 --port 8000' -ForegroundColor Green
& $venvPy -m uvicorn agent_server:app --reload --host 127.0.0.1 --port 8000

Pop-Location
