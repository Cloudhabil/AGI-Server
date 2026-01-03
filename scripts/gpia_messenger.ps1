param(
    [ValidateSet("Start", "Stop", "Status", "Tail", "Sync")]
    [string]$Action = "Status",
    [string]$AgentId,
    [string]$AgentName,
    [int]$PollInterval = 2,
    [int]$HeartbeatInterval = 60
)

$root = Split-Path -Parent $PSScriptRoot
$registryPath = Join-Path $root "data\gpia\agents\agent_registry.json"
$pidDir = Join-Path $root "runs\messenger_pids"
$heartbeatLog = Join-Path $root "logs\messenger_heartbeat.jsonl"
$sharedContext = Join-Path $root "memory\shared_context.json"

if (-not (Test-Path $registryPath)) {
    Write-Error "Registry not found: $registryPath"
    exit 1
}

$registry = Get-Content $registryPath | ConvertFrom-Json
$agents = $registry.agents

if (-not $AgentId -and -not $AgentName) {
    Write-Error "Provide -AgentId or -AgentName"
    exit 1
}

$agent = $null
if ($AgentId) {
    $agent = $agents | Where-Object { $_.agent_id -eq $AgentId } | Select-Object -First 1
}
if (-not $agent -and $AgentName) {
    $agent = $agents | Where-Object { $_.agent_name -eq $AgentName } | Select-Object -First 1
}

if (-not $agent) {
    Write-Error "Agent not found in registry."
    exit 1
}

$workspace = $agent.workspace
$agentId = $agent.agent_id
$runner = Join-Path $workspace "agent_runner.py"
$stopSignal = Join-Path $workspace "stop.signal"
$pidPath = Join-Path $pidDir "$agentId.pid"

if (-not (Test-Path $workspace)) {
    Write-Error "Workspace not found: $workspace"
    exit 1
}

if (-not (Test-Path $runner)) {
    Write-Error "Runner not found: $runner"
    exit 1
}

New-Item -ItemType Directory -Path $pidDir -Force | Out-Null

switch ($Action) {
    "Start" {
        if (Test-Path $pidPath) {
            $procId = Get-Content $pidPath
            if ($procId -and (Get-Process -Id $procId -ErrorAction SilentlyContinue)) {
                Write-Output "Messenger already running (PID $procId)."
                exit 0
            }
        }
        if (Test-Path $stopSignal) { Remove-Item $stopSignal -Force }
        $python = (Get-Command python).Source
        $args = @($runner, "--agent-dir", $workspace)
        $proc = Start-Process -FilePath $python -ArgumentList $args -WindowStyle Hidden -PassThru
        $proc.Id | Set-Content -Path $pidPath
        Write-Output "Messenger started (PID $($proc.Id))."
    }
    "Stop" {
        Set-Content -Path $stopSignal -Value "stop"
        if (Test-Path $pidPath) {
            $procId = Get-Content $pidPath
            if ($procId) {
                Stop-Process -Id $procId -ErrorAction SilentlyContinue
                Write-Output "Messenger stopped (PID $procId)."
            }
            Remove-Item $pidPath -Force -ErrorAction SilentlyContinue
        } else {
            Write-Output "No PID file found; stop signal created."
        }
    }
    "Status" {
        if (Test-Path $pidPath) {
            $procId = Get-Content $pidPath
            $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Output "Messenger running (PID $procId)."
            } else {
                Write-Output "Messenger not running (stale PID $procId)."
            }
        } else {
            Write-Output "Messenger not running."
        }
    }
    "Tail" {
        if (-not (Test-Path $heartbeatLog)) {
            Write-Error "Heartbeat log not found: $heartbeatLog"
            exit 1
        }
        Get-Content -Path $heartbeatLog -Wait
    }
    "Sync" {
        if (-not (Test-Path $sharedContext)) {
            Write-Error "Shared context not found: $sharedContext"
            exit 1
        }
        $ctx = Get-Content $sharedContext | ConvertFrom-Json
        $ctx.last_sync_timestamp = (Get-Date).ToUniversalTime().ToString("o")
        $ctx | ConvertTo-Json -Depth 6 | Set-Content -Path $sharedContext
        Write-Output "Shared context sync updated."
    }
}
