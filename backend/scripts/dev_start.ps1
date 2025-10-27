<#
Dev helper: starts the backend with safe defaults to avoid heavy ML loads.
Usage: Open PowerShell, then:
  cd backend\scripts
  .\dev_start.ps1
#>

Write-Host "Starting backend with safe dev env vars..."
$env:USE_GENAI = '0'
$env:PREFETCH_MODELS = '0'

# Activate venv if available
$venv = Join-Path -Path (Resolve-Path ..) -ChildPath '.venv\Scripts\python.exe'
if (Test-Path $venv) {
  Write-Host "Using virtualenv python: $venv"
  & $venv "..\app.py"
} else {
  Write-Host "Virtualenv python not found at $venv; falling back to system python"
  python ..\app.py
}
