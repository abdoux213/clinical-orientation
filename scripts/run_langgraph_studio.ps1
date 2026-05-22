# LangGraph Studio — visualisation et test du graphe clinical_orientation
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $Root "backend")
$env:PYTHONPATH = $Root

$venvLg = Join-Path $Root ".venv\Scripts\langgraph.exe"
if (-not (Test-Path $venvLg)) {
    Write-Host "Installation de langgraph-cli..." -ForegroundColor Yellow
    & (Join-Path $Root ".venv\Scripts\pip.exe") install "langgraph-cli[inmem]>=0.4.0"
}

Write-Host ""
Write-Host "Graphe : clinical_orientation" -ForegroundColor Cyan
Write-Host "API locale : http://127.0.0.1:8123" -ForegroundColor Green
Write-Host "Studio UI  : https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:8123" -ForegroundColor Green
Write-Host ""

if (Test-Path $venvLg) {
    & $venvLg dev --host 127.0.0.1 --port 8123
} else {
    langgraph dev --host 127.0.0.1 --port 8123
}
