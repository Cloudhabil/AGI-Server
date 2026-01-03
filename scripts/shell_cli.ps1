param(
    [Parameter(Position = 0)]
    [ValidateSet('start', 'stop', 'status', 'list', 'guardrails', 'tail', 'send', 'dense', 'telemetry', 'server-start', 'server-stop', 'server-status', 'help')]
    [string]$Action = 'help',
    [string]$Message
)

function Start-ShellMessenger {
    & "./scripts/gpia_messenger.ps1" -Action Start -AgentName 'Messenger-01'
}

function Stop-ShellMessenger {
    & "./scripts/gpia_messenger.ps1" -Action Stop -AgentName 'Messenger-01'
}

function List-Skills {
    $path = 'skills/INDEX.json'
    if (-not (Test-Path $path)) {
        Write-Error "Missing skill registry at $path"
        return
    }

    $manifest = Get-Content $path -Raw | ConvertFrom-Json
    $manifest.skills | Select-Object -First 10 | ForEach-Object {
        Write-Output "$($_.id): $($_.description)"
    }
}

function Show-Guardrails {
    $path = 'config/agent_creator_guardrails.json'
    if (-not (Test-Path $path)) {
        Write-Error "Guardrail file not found ($path)"
        return
    }
    Get-Content $path
}

function Tail-MessengerHeartbeat {
    $path = 'logs/messenger_heartbeat.jsonl'
    if (-not (Test-Path $path)) {
        Write-Error "Heartbeat log missing ($path)"
        return
    }
    Get-Content $path -Wait
}

function Show-TelemetrySummary {
    $path = 'logs/messenger_heartbeat.jsonl'
    if (-not (Test-Path $path)) {
        Write-Error "Heartbeat log missing ($path)"
        return
    }
    $line = Get-Content $path -Tail 1
    if (-not $line) {
        Write-Error 'No heartbeat entries found'
        return
    }
    try {
        $entry = $line | ConvertFrom-Json
    } catch {
        Write-Error 'Unable to parse heartbeat JSON'
        return
    }
    $details = $entry.details
    $telemetry = $details.telemetry
    $queue = $details.queue_depth
    $outbox = $details.outbox_depth

    Write-Output "Telemetry snapshot ($($entry.timestamp))"
    Write-Output "CPU: $($telemetry.cpu_percent)%  RAM: $([math]::Round($telemetry.ram_used_mb / $telemetry.ram_total_mb * 100,2))%  VRAM: $([math]::Round($telemetry.vram_used_mb / $telemetry.vram_total_mb * 100,2))%"
    Write-Output "Queue depth: $queue  Outbox depth: $outbox"
    Write-Output "Net send: $([math]::Round($telemetry.net_bytes_sent / 1MB,2)) MB  Net recv: $([math]::Round($telemetry.net_bytes_recv / 1MB,2)) MB"
}

function Send-Message {
    if (-not $Message) {
        Write-Error 'Provide -Message text'
        return
    }

    $path = 'memory/shared_context.json'
    if (-not (Test-Path $path)) {
        Write-Error "Shared context not found ($path)"
        return
    }

    $ctx = Get-Content $path -Raw | ConvertFrom-Json
    $entry = [pscustomobject]@{
        sender    = 'USER'
        text      = $Message
        processed = $false
        timestamp = (Get-Date).ToUniversalTime().ToString('o')
    }

    $newQueue = @()
    if ($ctx.message_queue) {
        $newQueue += @($ctx.message_queue)
    }
    $newQueue += $entry
    $ctx.message_queue = $newQueue
    $ctx | ConvertTo-Json -Depth 8 | Set-Content -Path $path -Encoding utf8
    Write-Output 'queued'
}

function Generate-DenseState {
    & "./scripts/generate_mock_dense_state.ps1"
}

function Start-GPIAServer {
    & "./scripts/gpia_server_manager.ps1" -Action Start
}

function Stop-GPIAServer {
    & "./scripts/gpia_server_manager.ps1" -Action Stop
}

function Status-GPIAServer {
    & "./scripts/gpia_server_manager.ps1" -Action Status
}

switch ($Action.ToLower()) {
    'start'     { Start-ShellMessenger }
    'status'    { Status-GPIAServer }
    'stop'      { Stop-ShellMessenger }
    'server-start'  { Start-GPIAServer }
    'server-stop'   { Stop-GPIAServer }
    'server-status' { Status-GPIAServer }
    'list'      { List-Skills }
    'guardrails'{ Show-Guardrails }
    'telemetry' { Show-TelemetrySummary }
    'tail'      { Tail-MessengerHeartbeat }
    'send'      { Send-Message }
    'dense'     { Generate-DenseState }
    default     {
        Write-Output 'Actions: start, stop, list, guardrails, telemetry, tail, send, dense'
    }
}
