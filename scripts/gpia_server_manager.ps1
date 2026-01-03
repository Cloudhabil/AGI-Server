param(
    [ValidateSet("Start", "Stop", "Status")]
    [string]$Action = "Status",
    [string]$PidDir = "runs\gpia_server_pids"
)

$root = Split-Path -Parent $PSScriptRoot
$pidPath = Join-Path $root "$PidDir\gpia_server.pid"
$script = Join-Path $root "scripts\run_gpia_server.py"

function Start-Server {
    if (Test-Path $pidPath) {
        $existing = Get-Content $pidPath
        if ($existing -and (Get-Process -Id $existing -ErrorAction SilentlyContinue)) {
            Write-Output "Server already running (PID $existing)."
            return
        }
    }
    $python = (Get-Command python).Source
    $proc = Start-Process -FilePath $python -ArgumentList $script -WindowStyle Hidden -PassThru
    New-Item -ItemType Directory -Path (Split-Path $pidPath) -Force | Out-Null
    $proc.Id | Set-Content -Path $pidPath
    Write-Output "GPIA server started (PID $($proc.Id))."
}

function Stop-Server {
    if (-not (Test-Path $pidPath)) {
        Write-Output "No server PID file; nothing to stop."
        return
    }
    $serverPid = Get-Content $pidPath
    if ($serverPid) {
        Stop-Process -Id $serverPid -ErrorAction SilentlyContinue
        Write-Output "GPIA server stopped (PID $serverPid)."
    }
    Remove-Item $pidPath -Force -ErrorAction SilentlyContinue
}

function Status-Server {
    if (-not (Test-Path $pidPath)) {
        Write-Output "GPIA server not running."
        return
    }
    $serverPid = Get-Content $pidPath
    if ($serverPid -and (Get-Process -Id $serverPid -ErrorAction SilentlyContinue)) {
        Write-Output "GPIA server running (PID $serverPid)."
    } else {
        Write-Output "Stale PID file found."
        Remove-Item $pidPath -Force -ErrorAction SilentlyContinue
    }
}

switch ($Action) {
    "Start" { Start-Server }
    "Stop"  { Stop-Server }
    "Status" { Status-Server }
}
