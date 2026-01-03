param(
    [int]$Runs = 0,
    [int]$Interval = 120,
    [string]$Output = "",
    [string]$Latest = "",
    [switch]$Fix,
    [switch]$Watch,
    [int]$WatchInterval = 5,
    [int]$LifetimeSeconds = 30
)

$root = Split-Path -Parent $PSScriptRoot
$script = Join-Path $root "scripts\step1_registry_agent.py"

$pythonArgs = "`"$script`""
if ($Runs -ge 0) { $pythonArgs += " --runs $Runs" }
if ($Interval -ge 0) { $pythonArgs += " --interval $Interval" }
if ($Output) { $pythonArgs += " --output `"$Output`"" }
if ($Latest) { $pythonArgs += " --latest `"$Latest`"" }
if ($Fix) { $pythonArgs += " --fix" }
if (-not $PSBoundParameters.ContainsKey("Watch")) { $Watch = $true }
if ($Watch) { $pythonArgs += " --watch --watch-interval $WatchInterval" }

Start-Process -FilePath "python" -ArgumentList $pythonArgs -WorkingDirectory $root -WindowStyle Hidden
Start-Sleep -Seconds $LifetimeSeconds
