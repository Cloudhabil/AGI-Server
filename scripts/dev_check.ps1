param(
  [switch]$Lint = $false,
  [switch]$Tests = $false,
  [switch]$Json = $false
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$summary = @{}
$summary.meta = @{ platform = $PSVersionTable.OS; powershell = $PSVersionTable.PSVersion.ToString() }

function Test-Http($Url) {
  try {
    $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 -Uri $Url
    return $true
  } catch { return $false }
}

function Print-Row([string]$Name, $Ok, [string]$Note='') {
  if ($null -eq $Ok) {
    Write-Host ("[SKIP] {0} {1}" -f $Name, $Note)
  } elseif ($Ok) {
    Write-Host ("[PASS] {0} {1}" -f $Name, $Note) -ForegroundColor Green
  } else {
    Write-Host ("[FAIL] {0} {1}" -f $Name, $Note) -ForegroundColor Red
  }
}

Write-Host '== Dev Diagnostics ==' -ForegroundColor Cyan

# Versions
function Get-CmdVersion($cmd, $args='--version') {
  try { & $cmd $args 2>$null } catch { return $null }
}

$pyv = Get-CmdVersion python --version
$nodev = Get-CmdVersion node -v
$npmv = Get-CmdVersion npm -v

Write-Host ("python: {0}" -f ($pyv ?? 'not found'))
Write-Host ("node:   {0}" -f ($nodev ?? 'not found'))
Write-Host ("npm:    {0}" -f ($npmv ?? 'not found'))
$summary.python = [bool]$pyv
$summary.node = [bool]$nodev
$summary.npm = [bool]$npmv
$summary.versions = @{ python = $pyv; node = $nodev; npm = $npmv }

# Venv
if (Test-Path .venv) {
  Write-Host '.venv: present' -ForegroundColor Green
  $summary.venv = $true
  $venvPy = Join-Path .venv 'Scripts/python.exe'
  if (Test-Path $venvPy) {
    try {
      & $venvPy -c "import fastapi,uvicorn; print('deps: ok')" | Out-Null
      Write-Host 'deps (fastapi, uvicorn): ok' -ForegroundColor Green
      $summary.pydeps = $true
    } catch {
      Write-Warning 'deps check failed in venv (fastapi/uvicorn)'
      $summary.pydeps = $false
    }
  }
} else {
  Write-Warning '.venv missing (run dev_backend.ps1)'
  $summary.venv = $false
}

# Ports
function Test-Port($port){
  try {
    $c = Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction Stop
    return $true
  } catch { return $false }
}

Write-Host ("port 8000 (backend): {0}" -f (if (Test-Port 8000) { 'LISTEN' } else { 'free' }))
Write-Host ("port 7088 (bus):     {0}" -f (if (Test-Port 7088) { 'LISTEN' } else { 'free' }))
Write-Host ("port 5173 (frontend):{0}" -f (if (Test-Port 5173) { 'LISTEN' } else { 'free' }))
$summary.port_backend = Test-Port 8000
$summary.port_bus = Test-Port 7088
$summary.port_frontend = Test-Port 5173

# Env
Write-Host ("AGENT_SHARED_SECRET: {0}" -f (if ($env:AGENT_SHARED_SECRET) { 'set' } else { 'missing' }))
Write-Host ("BUS_TOKEN:           {0}" -f (if ($env:BUS_TOKEN) { 'set' } else { 'missing' }))
Write-Host ("BUS_URL:             {0}" -f (if ($env:BUS_URL) { $env:BUS_URL } else { 'unset' }))
$summary.env_agent_secret = [bool]$env:AGENT_SHARED_SECRET
$summary.env_bus_token = [bool]$env:BUS_TOKEN
$summary.env = @{ AGENT_SHARED_SECRET = [bool]$env:AGENT_SHARED_SECRET; BUS_TOKEN = [bool]$env:BUS_TOKEN; BUS_URL = $env:BUS_URL }

# HTTP health (best-effort)
$backendUrl = 'http://127.0.0.1:8000/health'
$frontendUrl = 'http://localhost:5173'
$busUrl = 'http://127.0.0.1:7088/health'
$summary.health_backend = Test-Http $backendUrl
$summary.health_frontend = Test-Http $frontendUrl
$summary.health_bus = Test-Http $busUrl
try { & $PSScriptRoot/dev_health.ps1 | Out-Null; & $PSScriptRoot/dev_health.ps1 } catch { Write-Warning 'health check script failed' }

# Optional lint/tests
if ($Lint -or $Tests) {
  Write-Host '== Optional Checks ==' -ForegroundColor Cyan
}

if ($Lint) {
  if (Test-Path .venv/Scripts/python.exe) {
    Write-Host 'python lint: ruff .' -ForegroundColor Yellow
    try { & .\.venv\Scripts\python.exe -m ruff .; $summary.ruff = $true } catch { Write-Warning "ruff not available or failed ($($_.Exception.Message))"; $summary.ruff = $false }
    Write-Host 'python lint: flake8' -ForegroundColor Yellow
    try { & .\.venv\Scripts\python.exe -m flake8; $summary.flake8 = $true } catch { Write-Warning "flake8 not available or failed ($($_.Exception.Message))"; $summary.flake8 = $false }
  }
  if (Test-Path ./frontend/package.json -and (Get-Command npm -ErrorAction SilentlyContinue)) {
    Push-Location ./frontend
    try {
      $pkg = Get-Content package.json -Raw | ConvertFrom-Json
      if ($pkg.scripts.PSObject.Properties.Name -contains 'lint') {
        Write-Host 'frontend lint: npm run lint -s' -ForegroundColor Yellow
        npm run lint -s; if ($LASTEXITCODE -eq 0) { $summary.frontend_lint = $true } else { $summary.frontend_lint = $false }
      } else {
        Write-Host 'frontend lint: no lint script found' -ForegroundColor DarkYellow
        $summary.frontend_lint = $null
      }
    } catch { Write-Warning "frontend lint failed ($($_.Exception.Message))" }
    Pop-Location
  }
}

if ($Tests) {
  if (Test-Path .venv/Scripts/python.exe) {
    Write-Host 'python tests: pytest -q' -ForegroundColor Yellow
    try { & .\.venv\Scripts\python.exe -m pytest -q; if ($LASTEXITCODE -eq 0) { $summary.pytest = $true } else { $summary.pytest = $false } } catch { Write-Warning "pytest not available or failed ($($_.Exception.Message))"; $summary.pytest = $false }
  }
  if (Test-Path ./frontend/package.json -and (Get-Command npm -ErrorAction SilentlyContinue)) {
    Push-Location ./frontend
    try {
      $pkg = Get-Content package.json -Raw | ConvertFrom-Json
      if ($pkg.scripts.PSObject.Properties.Name -contains 'test') {
        Write-Host 'frontend tests: npm test -s' -ForegroundColor Yellow
        npm test -s; if ($LASTEXITCODE -eq 0) { $summary.frontend_test = $true } else { $summary.frontend_test = $false }
      } else {
        Write-Host 'frontend tests: no test script found' -ForegroundColor DarkYellow
        $summary.frontend_test = $null
      }
    } catch { Write-Warning "frontend tests failed ($($_.Exception.Message))" }
    Pop-Location
  }
}

Write-Host '== Summary ==' -ForegroundColor Cyan
Print-Row 'python' $summary.python $pyv
Print-Row 'node' $summary.node $nodev
Print-Row 'npm' $summary.npm $npmv
Print-Row '.venv' $summary.venv
Print-Row 'py deps (fastapi,uvicorn)' $summary.pydeps
Print-Row 'port 8000 (backend)' $summary.port_backend
Print-Row 'port 7088 (bus)' $summary.port_bus
Print-Row 'port 5173 (frontend)' $summary.port_frontend
Print-Row 'env AGENT_SHARED_SECRET' $summary.env_agent_secret
Print-Row 'env BUS_TOKEN' $summary.env_bus_token
Print-Row 'health backend' $summary.health_backend
Print-Row 'health bus' $summary.health_bus
Print-Row 'health frontend' $summary.health_frontend
if ($Lint) {
  Print-Row 'ruff' $summary.ruff
  Print-Row 'flake8' $summary.flake8
  Print-Row 'frontend lint' $summary.frontend_lint
}
if ($Tests) {
  Print-Row 'pytest' $summary.pytest
  Print-Row 'frontend test' $summary.frontend_test
}

if ($Json) {
  $json = $summary | ConvertTo-Json -Depth 6
  Write-Output $json
}
