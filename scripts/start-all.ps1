param([switch]$IngestCorpus)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
foreach ($Port in @(5433,8000,5173)) {
  $Listener = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
  if ($Listener) { throw "Port $Port is already in use (PID $($Listener[0].OwningProcess)); stop or reuse that service first." }
}
Push-Location $Root
try {
  if (-not (Test-Path (Join-Path $Root '.env'))) { Copy-Item (Join-Path $Root '.env.example') (Join-Path $Root '.env') }
  docker compose up -d --wait
  if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL did not start. Ensure Docker Desktop is running.' }
  $Args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $PSScriptRoot 'start-backend.ps1'))
  if ($IngestCorpus) { $Args += '-IngestCorpus' }
  Start-Process powershell.exe -ArgumentList $Args -WindowStyle Hidden
  Start-Sleep -Seconds 5
  Start-Process powershell.exe -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $PSScriptRoot 'start-frontend.ps1')) -WindowStyle Hidden
  Write-Host 'Starting Lenny Growth Assistant. UI: http://127.0.0.1:5173  API: http://127.0.0.1:8000/docs'
  Write-Host 'Stop app terminals from Task Manager or stop the database with: docker compose down'
} finally { Pop-Location }
