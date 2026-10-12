$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$OutputDirectory = Join-Path $Root 'dist'
$ArchivePath = Join-Path $OutputDirectory 'lenny-growth-assistant-final.zip'
if (Test-Path $ArchivePath) { throw "Refusing to overwrite existing package: $ArchivePath" }
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression
$ExcludedDirectories = @('.git','.venv','venv','node_modules','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache','dist','build','logs')
$Files = Get-ChildItem -LiteralPath $Root -Recurse -File | Where-Object {
  $Relative = $_.FullName.Substring($Root.Length + 1).Replace('\','/')
  $Segments = $Relative.Split('/')
  $IsExcludedDirectory = $false
  foreach ($Segment in $Segments) { if ($ExcludedDirectories -contains $Segment) { $IsExcludedDirectory = $true; break } }
  -not $IsExcludedDirectory -and
  $Relative -notmatch '(^|/).env($|/)' -and
  ($Relative -eq '.env.example' -or $Relative -notmatch '(^|/).env\.') -and
  $Relative -notmatch '^data/' -and
  $Relative -ne 'Pi_is_working.txt' -and
  $_.Extension -notin @('.pyc','.pyo','.zip')
}
$Archive = [System.IO.Compression.ZipFile]::Open($ArchivePath, [System.IO.Compression.ZipArchiveMode]::Create)
try {
  foreach ($File in $Files) {
    $Relative = $File.FullName.Substring($Root.Length + 1).Replace('\','/')
    [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($Archive, $File.FullName, $Relative, [System.IO.Compression.CompressionLevel]::Optimal) | Out-Null
  }
} finally { $Archive.Dispose() }
$Check = [System.IO.Compression.ZipFile]::OpenRead($ArchivePath)
try {
  $Names = @($Check.Entries | ForEach-Object FullName)
  foreach ($Required in @('README.md','.env.example','backend/app/main.py','backend/migrations/versions/b6e9a4d17310_allow_local_sources_without_urls.py','frontend/src/App.jsx','docs/PRD.md','docs/design.md','docs/architecture.md','docs/completion-report.md')) {
    if ($Names -notcontains $Required) { throw "Package is missing required file: $Required" }
  }
  if ($Names -contains '.env' -or $Names -match '(^|/)data/' -or $Names -match '(^|/)node_modules/') { throw 'Package contains a private or generated path.' }
  if ((Get-Item $ArchivePath).Length -le 0) { throw 'Package archive is empty.' }
} finally { $Check.Dispose() }
Write-Host "Verified package: $ArchivePath ($((Get-Item $ArchivePath).Length) bytes)"
