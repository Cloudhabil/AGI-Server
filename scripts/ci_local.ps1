$ErrorActionPreference = 'Stop'
Write-Host "==> Lint"
python -m pip install --upgrade pip | Out-Null
pip install -r requirements.txt | Out-Null
pip install flake8 mypy pytest | Out-Null
flake8 .
Write-Host "==> Type check"
mypy
Write-Host "==> Tests"
$env:SKIP_OPENVINO = "true"
 $env:SKIP_DB = "true"
pytest -q
Write-Host "==> Done"
