Param(
    [string]$PreferredPy = "py",
    [switch]$Clean
)
$PROJ_ROOT = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $PROJ_ROOT
Write-Host "[build] Project root: $PROJ_ROOT" -ForegroundColor Cyan

if (!(Test-Path "src\carrental\main.py")) { throw "Missing src\carrental\main.py" }
if (!(Test-Path "tools\app_runner.py")) { throw "Missing tools\app_runner.py" }
if (!(Test-Path "tools\seed_runner.py")) { throw "Missing tools\seed_runner.py" }

$PyCmd = $null
if (Get-Command py -ErrorAction SilentlyContinue) {
    foreach ($ver in @("3.12","3.11","3.10","3")) {
        try { py -$ver -c "import sys;print(sys.version)" *> $null; if ($LASTEXITCODE -eq 0) { $PyCmd = "py -$ver"; break } } catch {}
    }
}
if (-not $PyCmd) {
    if (Get-Command python -ErrorAction SilentlyContinue) { $PyCmd = "python" }
    else { throw "No Windows Python found. Install Python 3.10+ and ensure 'py' or 'python' is in PATH." }
}
Write-Host "[build] Using Python: $PyCmd" -ForegroundColor Cyan

if (!(Test-Path ".venv")) { & $PyCmd -m venv .venv }

$VENV_PY = ".\.venv\Scripts\python.exe"
& $VENV_PY -m pip install --upgrade pip
if (Test-Path "requirements.txt") { & $VENV_PY -m pip install -r requirements.txt }
& $VENV_PY -m pip install pyinstaller

if ($Clean) {
    Write-Host "[build] Cleaning dist/build..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force dist, build, **\__pycache__ -ErrorAction SilentlyContinue
}

$env:PYTHONPATH = (Join-Path $PROJ_ROOT "src")

Write-Host "[build] Building app executable (auto-seeds on startup)..." -ForegroundColor Cyan
& $VENV_PY -m PyInstaller --noconfirm --onefile --name FredsCarRental --paths src tools\app_runner.py

Write-Host "[build] Building seeder executable (optional manual seed)..." -ForegroundColor Cyan
& $VENV_PY -m PyInstaller --noconfirm --onefile --name FredsCarRentalSeeder --paths src tools\seed_runner.py

Write-Host "`n[build] Done. Find binaries in .\dist\" -ForegroundColor Green
