param(
  [switch]$Backend = $true,
  [switch]$Frontend = $true,
  [switch]$Bus = $true,
  [string]$BackendUrl = 'http://127.0.0.1:8000/health',
  [string]$FrontendUrl = 'http://localhost:5173',
  [string]$BusUrl = 'http://127.0.0.1:7088/health'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Test-Http($Url) {
  try {
    $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 -Uri $Url
    [pscustomobject]@{ Url=$Url; Ok=$true; StatusCode=$r.StatusCode }
  } catch {
    [pscustomobject]@{ Url=$Url; Ok=$false; StatusCode=0; Error=$_.Exception.Message }
  }
}

function Test-Tcp($Host, $Port) {
  try {
    $client = [System.Net.Sockets.TcpClient]::new()
    $async = $client.BeginConnect($Host, [int]$Port, $null, $null)
    $ok = $async.AsyncWaitHandle.WaitOne(2000)
    if ($ok -and $client.Connected) { $client.EndConnect($async); $client.Dispose(); return $true }
    $client.Dispose(); return $false
  } catch { return $false }
}

Write-Host '== Health Check ==' -ForegroundColor Cyan
if ($Backend) {
  $h = Test-Http $BackendUrl
  $color = if ($h.Ok) { 'Green' } else { 'Red' }
  Write-Host ("backend: {0} {1}" -f $h.Url, (if ($h.Ok) { $h.StatusCode } else { $h.Error })) -ForegroundColor $color
}
if ($Frontend) {
  $h = Test-Http $FrontendUrl
  $color = if ($h.Ok) { 'Green' } else { 'Red' }
  Write-Host ("frontend: {0} {1}" -f $h.Url, (if ($h.Ok) { $h.StatusCode } else { $h.Error })) -ForegroundColor $color
}
if ($Bus) {
  $h = Test-Http $BusUrl
  $color = if ($h.Ok) { 'Green' } else { 'Red' }
  Write-Host ("bus: {0} {1}" -f $h.Url, (if ($h.Ok) { $h.StatusCode } else { $h.Error })) -ForegroundColor $color
  $redisOk = Test-Tcp '127.0.0.1' 6379
  Write-Host ("redis: 127.0.0.1:6379 {0}" -f (if ($redisOk) { 'open' } else { 'closed' })) -ForegroundColor (if ($redisOk) { 'Green' } else { 'Red' })
}

