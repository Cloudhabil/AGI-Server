param(
  [switch]$WithBus = $true,
  [switch]$WithRedis = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Start-InNewWindow($Title, $Command) {
  $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($Command))
  Start-Process -FilePath pwsh -ArgumentList @('-NoExit','-EncodedCommand', $encoded) -WindowStyle Normal
  Write-Host "Launched: $Title" -ForegroundColor Green
}

Push-Location $PSScriptRoot/..

Write-Host '== Dev Up (backend, frontend, optional bus) ==' -ForegroundColor Cyan

# Frontend
$frontend = Join-Path $PSScriptRoot 'dev_frontend.ps1'
if (-not (Test-Path $frontend)) { throw "Missing $frontend" }
Start-InNewWindow 'frontend' "& '$frontend'"

# Backend
$backend = Join-Path $PSScriptRoot 'dev_backend.ps1'
if (-not (Test-Path $backend)) { throw "Missing $backend" }
Start-InNewWindow 'backend' "& '$backend'"

if ($WithBus) {
  # Ensure Redis
  if ($WithRedis) {
    if (Get-Command docker -ErrorAction SilentlyContinue) {
      $running = docker ps --format '{{.Names}}' | Select-String -SimpleMatch 'redis'
      if (-not $running) {
        Write-Host 'Starting Redis docker container...' -ForegroundColor Yellow
        docker run -d --name redis -p 6379:6379 redis:7 | Out-Null
      }
    } else {
      Write-Warning 'Docker not found; expecting a Redis instance on localhost:6379'
    }
  }

  $envCmd = "`$env:BUS_TOKEN = if(`$env:BUS_TOKEN){`$env:BUS_TOKEN}else{'devbus'}; uvicorn bus_server:app --reload --host 127.0.0.1 --port 7088"
  Start-InNewWindow 'bus' $envCmd
}

Write-Host 'Dev environment launching. Use Ctrl+C in each window to stop.' -ForegroundColor Cyan

Pop-Location

