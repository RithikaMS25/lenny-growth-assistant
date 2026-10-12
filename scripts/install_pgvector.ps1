# scripts/install_pgvector.ps1
# ─────────────────────────────────────────────────────────────────
# Run this ONCE as Administrator to install pgvector for PostgreSQL 17.
# Right-click PowerShell → "Run as administrator", then:
#   cd "D:\Oggways project"
#   .\scripts\install_pgvector.ps1
# ─────────────────────────────────────────────────────────────────

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$PGDIR  = "C:\Program Files\PostgreSQL\17"
$PGVER  = "17"
$VEC_VER = "0.8.1"
$ZIP_URL = "https://github.com/andreiramani/pgvector_pgsql_windows/releases/download/${VEC_VER}_${PGVER}.6/vector.v${VEC_VER}-pg${PGVER}.zip"
$TMP     = "$env:TEMP\pgvector_install"

Write-Host "=== pgvector installer for PostgreSQL $PGVER ===" -ForegroundColor Cyan

# Verify admin
$currentPrincipal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "This script must be run as Administrator. Right-click PowerShell and choose 'Run as administrator'."
    exit 1
}

# Check PG17 exists
if (-not (Test-Path "$PGDIR\bin\postgres.exe")) {
    Write-Error "PostgreSQL 17 not found at $PGDIR"
    exit 1
}

# Use pre-extracted files if already downloaded, otherwise download
$extractedSrc = "C:\Users\Public\pg_extensions_src"
if (Test-Path "$extractedSrc\share\extension\vector.control") {
    Write-Host "Using pre-extracted files from $extractedSrc" -ForegroundColor Green
} else {
    Write-Host "Downloading pgvector $VEC_VER for PG$PGVER..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $TMP -Force | Out-Null
    $zipPath = "$TMP\pgvector.zip"
    Invoke-WebRequest -Uri $ZIP_URL -OutFile $zipPath -UseBasicParsing
    Expand-Archive -Path $zipPath -DestinationPath $TMP -Force
    $extractedSrc = $TMP
}

# Also check temp location from previous session
if (-not (Test-Path "$extractedSrc\share\extension\vector.control")) {
    $tempSrc = "$env:TEMP\pgvector_pg17"
    if (Test-Path "$tempSrc\share\extension\vector.control") {
        $extractedSrc = $tempSrc
        Write-Host "Using pre-extracted files from $tempSrc" -ForegroundColor Green
    }
}

Write-Host "Installing pgvector files into $PGDIR..."

# Copy DLL
$srcDll = "$extractedSrc\lib\vector.dll"
if (Test-Path $srcDll) {
    Copy-Item $srcDll "$PGDIR\lib\vector.dll" -Force
    Write-Host "  ✓ vector.dll installed" -ForegroundColor Green
} else {
    Write-Error "  ✗ Source DLL not found: $srcDll"
    exit 1
}

# Copy extension files (control + SQL migration files)
$srcExt = "$extractedSrc\share\extension"
if (Test-Path $srcExt) {
    Copy-Item "$srcExt\*" "$PGDIR\share\extension\" -Force
    Write-Host "  ✓ Extension SQL and control files installed" -ForegroundColor Green
} else {
    Write-Error "  ✗ Extension files not found: $srcExt"
    exit 1
}

# Verify
if (Test-Path "$PGDIR\share\extension\vector.control") {
    Write-Host "" 
    Write-Host "=== pgvector installation complete ===" -ForegroundColor Green
    Write-Host "Now run alembic upgrade head from the backend directory:"
    Write-Host '  cd "D:\Oggways project\backend"'
    Write-Host "  .\.venv\Scripts\python.exe -m alembic upgrade head"
} else {
    Write-Error 'Installation verification failed: vector.control not found.'
    exit 1
}
