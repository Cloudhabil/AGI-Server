param(
  [switch]$WithBus = $false,
  [switch]$WithRedis = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Wait-Health($Url, [int]$TimeoutSec = 60) {
  $start = Get-Date
  while ((Get-Date) - $start -lt [TimeSpan]::FromSeconds($TimeoutSec)) {
    try {
      $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 -Uri $Url
      if ($r.StatusCode -ge 200 -and $r.StatusCode -lt 300) { return $true }
    } catch { Start-Sleep -Milliseconds 500 }
  }
  return $false
}

Push-Location $PSScriptRoot/..

Write-Host '== Dev Up (serial, one after the other) ==' -ForegroundColor Cyan

if (-not (Test-Path venv)) {
  Write-Host 'Creating virtual environment (venv)...' -ForegroundColor Yellow
  python -m venv venv
}
$venvPy = Join-Path $PWD 'venv\Scripts\python.exe'

Write-Host 'Installing backend dependencies...' -ForegroundColor Yellow
& $venvPy -m pip install --upgrade pip
& $venvPy -m pip install -r requirements.txt

if (-not $env:AGENT_SHARED_SECRET) { $env:AGENT_SHARED_SECRET = 'devsecret' }

# Optional bus and Redis
if ($WithBus) {
  if ($WithRedis -and (Get-Command docker -ErrorAction SilentlyContinue)) {
    if (-not (docker ps --format '{{.Names}}' | Select-String -SimpleMatch 'redis')) {
      Write-Host 'Starting Redis container...' -ForegroundColor Yellow
      docker run -d --name redis -p 6379:6379 redis:7 | Out-Null
    }
  }
  if (-not $env:BUS_TOKEN) { $env:BUS_TOKEN = 'devbus' }
  Write-Host 'Starting bus server (background)...' -ForegroundColor Yellow
  $busJob = Start-Job -Name bus -InitializationScript { Set-Location $using:PWD } -ScriptBlock {
    $env:BUS_TOKEN = $env:BUS_TOKEN
    & $using:venvPy -m uvicorn bus_server:app --host 127.0.0.1 --port 7088 --reload
  }
  if (-not (Wait-Health 'http://127.0.0.1:7088/health' 45)) { Write-Warning 'bus_server health check failed' }
}

Write-Host 'Starting backend (background)...' -ForegroundColor Yellow
$backendJob = Start-Job -Name backend -InitializationScript { Set-Location $using:PWD } -ScriptBlock {
  $env:AGENT_SHARED_SECRET = $env:AGENT_SHARED_SECRET
  & $using:venvPy -m uvicorn agent_server:app --host 127.0.0.1 --port 8000 --reload
}

if (-not (Wait-Health 'http://127.0.0.1:8000/health' 60)) {
  Write-Warning 'backend health check failed; continuing to frontend'
}

Write-Host 'Installing frontend dependencies...' -ForegroundColor Yellow
Push-Location ./frontend
npm install

Write-Host 'Starting frontend (foreground) ...' -ForegroundColor Green
Write-Host 'Open http://localhost:5173  |  Stop with Ctrl+C' -ForegroundColor DarkGreen
npm run dev -- --host 0.0.0.0

# On exit
Pop-Location
Write-Host 'Stopping background jobs (backend/bus)...' -ForegroundColor Yellow
Get-Job -Name backend,bus -ErrorAction SilentlyContinue | Stop-Job -Force | Out-Null
Get-Job -Name backend,bus -ErrorAction SilentlyContinue | Remove-Job | Out-Null

Pop-Location
