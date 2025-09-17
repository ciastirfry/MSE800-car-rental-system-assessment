@echo off
setlocal enabledelayedexpansion

REM Always run relative to this script's parent (project root)
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%\.."
set "PROJ_ROOT=%CD%"
echo [build] Project root: %PROJ_ROOT%

REM Sanity checks
if not exist "src\carrental\main.py" (
  echo ERROR: Missing src\carrental\main.py in %PROJ_ROOT%
  exit /b 1
)
if not exist "tools\app_runner.py" (
  echo ERROR: Missing tools\app_runner.py in %PROJ_ROOT%
  exit /b 1
)
if not exist "tools\seed_runner.py" (
  echo ERROR: Missing tools\seed_runner.py in %PROJ_ROOT%
  exit /b 1
)

REM Prefer Windows Python via the py launcher
set "PY_CMD="
where py >nul 2>nul && (
  for %%V in (3.12 3.11 3.10 3) do (
    py -%%V -c "import sys; print(sys.version)" >nul 2>nul && (
      set "PY_CMD=py -%%V"
      goto :foundpy
    )
  )
)
where python >nul 2>nul && set "PY_CMD=python"
:foundpy
if not defined PY_CMD (
  echo ERROR: No Windows Python found. Install Python 3.10+ and ensure 'py' or 'python' is in PATH.
  popd & exit /b 1
)
echo [build] Using Python: %PY_CMD%

if not exist ".venv" (
  %PY_CMD% -m venv .venv || (echo ERROR: venv creation failed.& popd & exit /b 1)
)

set "VENV_PY=.venv\Scripts\python.exe"
"%VENV_PY%" -m pip install --upgrade pip
if exist requirements.txt ("%VENV_PY%" -m pip install -r requirements.txt)
"%VENV_PY%" -m pip install pyinstaller

set "PYTHONPATH=%PROJ_ROOT%\src"

echo [build] Building app executable (auto-seeds on startup)...
"%VENV_PY%" -m PyInstaller --noconfirm --onefile --name FredsCarRental --paths src tools\app_runner.py

echo [build] Building seeder executable (optional manual seed)...
"%VENV_PY%" -m PyInstaller --noconfirm --onefile --name FredsCarRentalSeeder --paths src tools\seed_runner.py

echo.
echo [build] Done. Binaries in .\dist\
popd
endlocal
