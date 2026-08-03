# Build Windows desktop EXE (PyInstaller onedir)
# Usage from data_access_app/:
#   powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

# Prefer monorepo .venv (Python 3.12+/3.14) — system Python 3.10.0 breaks PyInstaller bytecode scan.
$repoRoot = Split-Path (Get-Location) -Parent
$venvPy = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
  $venvPy = (Get-Command python).Source
}
Write-Host "==> Python: $venvPy"
& $venvPy -c "import sys; print(sys.version)"

Write-Host "==> Ensuring deps + pyinstaller…"
uv pip install --python $venvPy --native-tls -q -r requirements.txt "pyinstaller>=6.0"

Write-Host "==> Building DataAccessApp (onedir)…"
& $venvPy -m PyInstaller DataAccessApp.spec --noconfirm --clean

$appDir = Join-Path (Get-Location) "dist\DataAccessApp"
$exePath = Join-Path $appDir "DataAccessApp.exe"
if (-not (Test-Path $exePath)) {
  throw "Build finished but exe missing: $exePath"
}

# Merge .env for packaged app: local + monorepo DSN keys
$envDst = Join-Path $appDir ".env"
$lines = @{}
function Merge-EnvFile([string]$path) {
  if (-not (Test-Path $path)) { return }
  Get-Content $path | ForEach-Object {
    if ($_ -match '^\s*#') { return }
    if ($_ -match '^\s*$') { return }
    $i = $_.IndexOf('=')
    if ($i -lt 1) { return }
    $k = $_.Substring(0, $i).Trim()
    $v = $_.Substring($i + 1)
    $script:lines[$k] = $v
  }
}
Merge-EnvFile (Join-Path (Get-Location) ".env")
Merge-EnvFile (Join-Path $repoRoot ".env")
# Prefer explicit DSN keys if present
$out = ($lines.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "`n"
Set-Content -Path $envDst -Value ($out + "`n") -Encoding UTF8
Write-Host "==> Wrote packaged .env ($($lines.Count) keys)"

New-Item -ItemType Directory -Force -Path (Join-Path $appDir "output") | Out-Null

Write-Host ""
Write-Host "OK"
Write-Host "  Folder: $appDir"
Write-Host "  EXE:    $exePath"
Write-Host "Edit .env next to the exe for DSN, then run DataAccessApp.exe"
