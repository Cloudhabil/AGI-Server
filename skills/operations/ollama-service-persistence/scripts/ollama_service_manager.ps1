param(
  [ValidateSet('Install','Update','Start','Stop','Status','Remove')]
  [string]$Action = 'Install',
  [ValidateSet('Service','Task','Startup')]
  [string]$Mode = 'Task',
  [ValidateSet('System','User','Auto')]
  [string]$TaskScope = 'Auto',
  [switch]$AllowTaskFallback,
  [string]$ServiceName = 'Ollama',
  [string]$ModelsDir = 'C:\Users\usuario\Business\CLI_A1_GHR\CLI-main\models',
  [string]$OllamaHost = '127.0.0.1:11435',
  [string]$OllamaExe = 'C:\Users\usuario\AppData\Local\Programs\Ollama\ollama.exe',
  [string]$RepoRoot = '',
  [string]$StartupDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
  [string]$StartupName = 'OllamaServe.cmd'
)

$ErrorActionPreference = 'Stop'

function Get-RepoRoot {
  if ($RepoRoot) {
    return (Resolve-Path $RepoRoot).Path
  }
  $root = $PSScriptRoot
  for ($i = 0; $i -lt 4; $i++) {
    $root = Split-Path -Parent $root
  }
  if (-not (Test-Path (Join-Path $root 'skills'))) {
    throw "Repo root not found. Pass -RepoRoot explicitly."
  }
  return $root
}

function Ensure-RunnerScript {
  param(
    [string]$Path,
    [string]$ModelsDirValue,
    [string]$OllamaExeValue,
    [string]$HostValue
  )
  $content = @(
    '$ErrorActionPreference = ''Stop'''
    ''
    "`$env:OLLAMA_MODELS = '$ModelsDirValue'"
    "`$env:OLLAMA_HOST = '$HostValue'"
    ''
    "& '$OllamaExeValue' serve"
  ) -join "`r`n"
  Set-Content -Path $Path -Value $content -Encoding UTF8
}

function Service-Exists {
  param([string]$Name)
  sc.exe query $Name | Out-Null
  return $LASTEXITCODE -eq 0
}

function Set-SystemModelsEnv {
  param([string]$ModelsDirValue)
  & setx /M OLLAMA_MODELS $ModelsDirValue | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "Failed to set system OLLAMA_MODELS. The service runner sets it explicitly."
  }
}

function Ensure-Startup {
  param(
    [string]$Dir,
    [string]$Name,
    [string]$ModelsDirValue,
    [string]$OllamaExeValue,
    [string]$HostValue
  )
  New-Item -ItemType Directory -Force -Path $Dir | Out-Null
  $cmdPath = Join-Path $Dir $Name
  $lines = @(
    '@echo off'
    "set OLLAMA_MODELS=$ModelsDirValue"
    "set OLLAMA_HOST=$HostValue"
    ('start "" "{0}" serve' -f $OllamaExeValue)
  )
  Set-Content -Path $cmdPath -Value ($lines -join "`r`n") -Encoding ASCII
  return $cmdPath
}

function Start-Ollama {
  param(
    [string]$ModelsDirValue,
    [string]$OllamaExeValue,
    [string]$HostValue
  )
  $env:OLLAMA_MODELS = $ModelsDirValue
  $env:OLLAMA_HOST = $HostValue
  Start-Process -FilePath $OllamaExeValue -ArgumentList 'serve' -WindowStyle Hidden | Out-Null
}

function Task-Exists {
  param([string]$Name)
  schtasks.exe /Query /TN $Name | Out-Null
  return $LASTEXITCODE -eq 0
}

function Ensure-Task {
  param(
    [string]$Name,
    [string]$RunnerPath,
    [ValidateSet('System','User')]
    [string]$Scope
  )
  $taskCmd = "`"$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe`" -NoProfile -ExecutionPolicy Bypass -File `"$RunnerPath`""
  if ($Scope -eq 'System') {
    schtasks.exe /Create /TN $Name /TR $taskCmd /SC ONSTART /RU SYSTEM /RL HIGHEST /F | Out-Null
  } else {
    schtasks.exe /Create /TN $Name /TR $taskCmd /SC ONLOGON /RU $env:USERNAME /NP /RL LIMITED /F | Out-Null
  }
  return $LASTEXITCODE -eq 0
}

$repoRootPath = Get-RepoRoot
$runnerPath = Join-Path $repoRootPath 'scripts\ollama_service.ps1'

switch ($Action) {
  'Install' {
    New-Item -ItemType Directory -Force -Path $ModelsDir | Out-Null
    icacls $ModelsDir /grant 'SYSTEM:(OI)(CI)F' | Out-Null
    Set-SystemModelsEnv -ModelsDirValue $ModelsDir
    Ensure-RunnerScript -Path $runnerPath -ModelsDirValue $ModelsDir -OllamaExeValue $OllamaExe -HostValue $OllamaHost
    if ($Mode -eq 'Startup') {
      $startupPath = Ensure-Startup -Dir $StartupDir -Name $StartupName -ModelsDirValue $ModelsDir -OllamaExeValue $OllamaExe -HostValue $OllamaHost
      Start-Ollama -ModelsDirValue $ModelsDir -OllamaExeValue $OllamaExe -HostValue $OllamaHost
      Write-Host "Startup entry created: $startupPath"
      break
    }
    if ($Mode -eq 'Task') {
      $scope = if ($TaskScope -eq 'Auto') { 'System' } else { $TaskScope }
      $created = Ensure-Task -Name $ServiceName -RunnerPath $runnerPath -Scope $scope
      if (-not $created -and $TaskScope -eq 'Auto') {
        $created = Ensure-Task -Name $ServiceName -RunnerPath $runnerPath -Scope 'User'
      }
      if ($created) {
        schtasks.exe /Run /TN $ServiceName | Out-Null
      }
      break
    }

    $bin = "`"$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe`" -NoProfile -ExecutionPolicy Bypass -File `"$runnerPath`""
    if (Service-Exists -Name $ServiceName) {
      sc.exe config $ServiceName binPath= $bin start= auto | Out-Null
    } else {
      sc.exe create $ServiceName binPath= $bin start= auto | Out-Null
    }
    sc.exe start $ServiceName | Out-Null
    if ($LASTEXITCODE -ne 0 -and $AllowTaskFallback) {
      Ensure-Task -Name $ServiceName -RunnerPath $runnerPath
      schtasks.exe /Run /TN $ServiceName | Out-Null
    }
  }
  'Update' {
    New-Item -ItemType Directory -Force -Path $ModelsDir | Out-Null
    icacls $ModelsDir /grant 'SYSTEM:(OI)(CI)F' | Out-Null
    Set-SystemModelsEnv -ModelsDirValue $ModelsDir
    Ensure-RunnerScript -Path $runnerPath -ModelsDirValue $ModelsDir -OllamaExeValue $OllamaExe -HostValue $OllamaHost
    if ($Mode -eq 'Startup') {
      $startupPath = Ensure-Startup -Dir $StartupDir -Name $StartupName -ModelsDirValue $ModelsDir -OllamaExeValue $OllamaExe -HostValue $OllamaHost
      Write-Host "Startup entry updated: $startupPath"
      break
    }
    if ($Mode -eq 'Task') {
      $scope = if ($TaskScope -eq 'Auto') { 'System' } else { $TaskScope }
      $updated = Ensure-Task -Name $ServiceName -RunnerPath $runnerPath -Scope $scope
      if (-not $updated -and $TaskScope -eq 'Auto') {
        Ensure-Task -Name $ServiceName -RunnerPath $runnerPath -Scope 'User' | Out-Null
      }
      break
    }
    $bin = "`"$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe`" -NoProfile -ExecutionPolicy Bypass -File `"$runnerPath`""
    if (-not (Service-Exists -Name $ServiceName)) {
      throw "Service '$ServiceName' not found. Use -Action Install."
    }
    sc.exe config $ServiceName binPath= $bin start= auto | Out-Null
  }
  'Start' {
    if ($Mode -eq 'Startup') { Start-Ollama -ModelsDirValue $ModelsDir -OllamaExeValue $OllamaExe -HostValue $OllamaHost }
    elseif ($Mode -eq 'Task') { schtasks.exe /Run /TN $ServiceName | Out-Null }
    else { sc.exe start $ServiceName | Out-Null }
  }
  'Stop' {
    if ($Mode -eq 'Startup') { Get-Process -Name ollama -ErrorAction SilentlyContinue | Stop-Process -Force }
    elseif ($Mode -eq 'Task') { schtasks.exe /End /TN $ServiceName | Out-Null }
    else { sc.exe stop $ServiceName | Out-Null }
  }
  'Status' {
    if ($Mode -eq 'Startup') {
      $startupPath = Join-Path $StartupDir $StartupName
      $exists = Test-Path $startupPath
      $proc = Get-Process -Name ollama -ErrorAction SilentlyContinue
      Write-Host ("Startup entry: " + $(if ($exists) { $startupPath } else { 'missing' }))
      Write-Host ("Ollama process: " + $(if ($proc) { 'running' } else { 'stopped' }))
    } elseif ($Mode -eq 'Task') { schtasks.exe /Query /TN $ServiceName /V /FO LIST }
    else { sc.exe query $ServiceName }
  }
  'Remove' {
    if ($Mode -eq 'Startup') {
      $startupPath = Join-Path $StartupDir $StartupName
      if (Test-Path $startupPath) { Remove-Item -Force $startupPath }
    } elseif ($Mode -eq 'Task') {
      if (Task-Exists -Name $ServiceName) { schtasks.exe /Delete /TN $ServiceName /F | Out-Null }
    } else { sc.exe delete $ServiceName }
  }
}
