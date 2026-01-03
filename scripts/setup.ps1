# setup.ps1 — one-shot bootstrap, lint, test
param(
  [switch]$SkipTests,
  [switch]$SkipLint
)

$ErrorActionPreference = 'Stop'

function Get-PathOr([string]$Name){
  $c = Get-Command $Name -ErrorAction SilentlyContinue
  if($c){ $c.Source } else { 'not found' }
}

Write-Host "== Repo sanity ==" -ForegroundColor Cyan
if(!(Test-Path .git)){ throw "Run this from the repo root (missing .git)" }

Write-Host "== Virtualenv ==" -ForegroundColor Cyan
if(!(Test-Path .\.venv)){
  Write-Host "Creating .venv..." -ForegroundColor Yellow
  py -3 -m venv .venv 2>$null; if($LASTEXITCODE -ne 0){ python -m venv .venv }
}
if(-not $env:VIRTUAL_ENV){
  Write-Host "Activating .venv..." -ForegroundColor Yellow
  .\.venv\Scripts\Activate.ps1
}

Write-Host "== Venv proof ==" -ForegroundColor Cyan
Write-Host ("VENV:   {0}" -f ($env:VIRTUAL_ENV ?? 'not active'))
Write-Host ("python: {0}" -f (Get-PathOr 'python'))
Write-Host ("pip:    {0}" -f (Get-PathOr 'pip'))
Write-Host ("pytest: {0}" -f (Get-PathOr 'pytest'))
Write-Host ("ruff:   {0}" -f (Get-PathOr 'ruff'))

python -c "import sys, platform; print('exe        :', sys.executable); print('venv_active:', sys.base_prefix != sys.prefix); print('python     :', platform.python_version())"

Write-Host "== Install dependencies ==" -ForegroundColor Cyan
python -m pip install -q --upgrade pip
if(Test-Path .\requirements.txt){         python -m pip install -q -r .\requirements.txt }
if(Test-Path .\CLI\CLI\requirements.txt){ python -m pip install -q -r .\CLI\CLI\requirements.txt }
python -m pip install -q ruff flake8 pytest

Write-Host "== Ensure prompt files ==" -ForegroundColor Cyan
$dst = "CLI\CLI\prompts"
$src = "CLI\CLI_AI\CLI\prompts"
if(!(Test-Path $dst)){ New-Item -ItemType Directory -Force $dst | Out-Null }
if(Test-Path $src){
  Get-ChildItem "$src\system_*.md" -ErrorAction SilentlyContinue |
    ForEach-Object { Copy-Item $_.FullName $dst -Force }
}

Write-Host "== Ensure .flake8 ==" -ForegroundColor Cyan
$flake = ".\.flake8"
if(!(Test-Path $flake)){
@'
[flake8]
exclude = .venv,venv,.tox,dist,build,__pycache__,.git
# allow long help strings / REPL prompts without E501 noise
max-line-length = 400
extend-ignore = E203,W503
per-file-ignores =
    **/__init__.py:F401
    tests/*:F401
'@ | Set-Content -Encoding UTF8 $flake
}

if(-not $SkipLint){
  Write-Host "== Ruff format & fixes ==" -ForegroundColor Cyan
  ruff format .
  ruff check --fix .

  Write-Host "== Flake8 ==" -ForegroundColor Cyan
  python -m flake8
}

if(-not $SkipTests){
  Write-Host "== Pytest -q ==" -ForegroundColor Cyan
  python -m pytest -q
}

Write-Host "`nREADY ✅  (env ok, deps installed, $(if($SkipLint){'lint skipped'}else{'lint ok'}), $(if($SkipTests){'tests skipped'}else{'tests ok'}))" -ForegroundColor Green
