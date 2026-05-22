# Lance le frontend React (Vite) sur http://127.0.0.1:5173
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Front = Join-Path $Root "frontend-react"
Set-Location $Front

if (-not (Test-Path "node_modules")) {
  Write-Host "Installation npm…"
  npm install
}

if (-not $env:VITE_API_URL) { $env:VITE_API_URL = "http://127.0.0.1:8000" }
Write-Host "VITE_API_URL=$($env:VITE_API_URL)"
Write-Host "Frontend React: http://127.0.0.1:5173" -ForegroundColor Green

npm run dev -- --host 127.0.0.1 --port 5173
