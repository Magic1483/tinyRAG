param(
  [string]$BackendHost = "0.0.0.0",
  [int]$BackendPort = 8000,
  [string]$FrontendHost = "0.0.0.0",
  [int]$FrontendPort = 3000
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting tinyRAG..."

# Backend
$backendCmd = "cd /d `"$root\src`" && uv run uvicorn api:app --host $BackendHost --port $BackendPort"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k $backendCmd" -WindowStyle Normal

# Frontend
$frontendCmd = "cd /d `"$root\frontend`" && pnpm dev --hostname $FrontendHost --port $FrontendPort"
Start-Process -FilePath "cmd.exe" -ArgumentList "/k $frontendCmd" -WindowStyle Normal

Start-Sleep -Seconds 2
Start-Process "http://localhost:$FrontendPort"

Write-Host "Backend:  http://localhost:$BackendPort"
Write-Host "Frontend: http://localhost:$FrontendPort"
