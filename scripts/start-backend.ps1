param([switch]$IngestCorpus)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root 'backend'
$Python = Join-Path $Backend '.venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { py -3.10 -m venv (Join-Path $Backend '.venv'); $Python = Join-Path $Backend '.venv\Scripts\python.exe' }
Push-Location $Backend
try {
    $env:PYTHONPATH = $Backend
    & $Python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Backend dependency installation failed.' }
    & $Python -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) { throw 'Database migrations failed; check Docker Compose and DATABASE_URL.' }
    & $Python scripts\seed_dev_user.py
    if ($LASTEXITCODE -ne 0) { throw 'Development user initialization failed.' }
    if ($IngestCorpus) { & $Python scripts\ingest_corpus.py; if ($LASTEXITCODE -ne 0) { throw 'Corpus ingestion failed.' } }
    & $Python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
} finally { Pop-Location }
