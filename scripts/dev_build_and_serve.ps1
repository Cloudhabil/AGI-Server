Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Push-Location $PSScriptRoot/..

Write-Host '== Build frontend ==' -ForegroundColor Cyan
Push-Location ./frontend
npm install
npm run build
$dist = (Resolve-Path ./dist).Path
Pop-Location

Write-Host "Serving SPA from: $dist" -ForegroundColor Green

if (-not (Test-Path venv)) { python -m venv venv }
$venvPy = Join-Path $PWD 'venv\Scripts\python.exe'
& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install -r requirements.txt

if (-not $env:AGENT_SHARED_SECRET) { $env:AGENT_SHARED_SECRET = 'devsecret' }
$env:SERVE_SPA_DIST = $dist

Write-Host 'Starting backend (serving SPA at / )' -ForegroundColor Green
& $venvPy -m uvicorn agent_server:app --host 127.0.0.1 --port 8000

Pop-Location
