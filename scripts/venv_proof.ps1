# venv_proof.ps1 (PS 5.1)
$ErrorActionPreference = 'Stop'
function Get-PathOr { param([string]$Name)
  $c = Get-Command $Name -ErrorAction SilentlyContinue
  if ($c) { $c.Source } else { 'not found' }
}

"== Quick venv proof =="
"VENV:   $env:VIRTUAL_ENV"
"python:  $(Get-PathOr 'python')"
"pip:     $(Get-PathOr 'pip')"
"pytest:  $(Get-PathOr 'pytest')"
"ruff:    $(Get-PathOr 'ruff')"
python -c "import sys; print('exe=', sys.executable); print('venv_active=', sys.base_prefix!=sys.prefix)"
