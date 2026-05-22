# Lance le frontend Streamlit sur http://127.0.0.1:8501
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
if (-not $env:PYTHONPATH) { $env:PYTHONPATH = $Root }
if (-not $env:API_URL) { $env:API_URL = "http://127.0.0.1:8000" }

Write-Host "PYTHONPATH=$($env:PYTHONPATH)"
Write-Host "API_URL=$($env:API_URL)"
Write-Host "Frontend: http://127.0.0.1:8501" -ForegroundColor Green

$venvSt = Join-Path $Root ".venv\Scripts\streamlit.exe"
if (Test-Path $venvSt) {
  & $venvSt run frontend/app.py --server.port 8501 --server.address 127.0.0.1
} else {
  & streamlit run frontend/app.py --server.port 8501 --server.address 127.0.0.1
}
