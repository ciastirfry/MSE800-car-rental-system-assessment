@echo off
setlocal EnableExtensions

REM --- Always run from the folder this script lives in ---
pushd "%~dp0"

REM --- Pick a Python launcher ---
where py >NUL 2>&1 && set "PYLAUNCHER=1"
if defined PYLAUNCHER (
  py -3 -c "import sys; print('ok')" >NUL 2>&1 || set "PYLAUNCHER="
)
if defined PYLAUNCHER (
  set "PYCMD=py -3"
) else (
  set "PYCMD=python"
)

REM --- Create venv if missing ---
if not exist ".venv\Scripts\python.exe" (
  echo [setup] Creating virtual environment...
  %PYCMD% -m venv .venv || goto :fail
)

REM --- Upgrade pip and install project deps (if present) ---
echo [setup] Upgrading pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip >NUL

if exist requirements.txt (
  echo [setup] Installing requirements.txt ...
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :fail
)

REM --- Ensure pytest is installed ---
echo [setup] Installing pytest ...
".venv\Scripts\python.exe" -m pip install -U pytest || goto :fail

REM --- Make sure src is importable (tests also handle this, but belt & suspenders) ---
set "PYTHONPATH=%CD%\src"

REM --- Run tests (verbose, reasons, short TB, show locals, show slow tests) ---
echo [tests] Running pytest...
".venv\Scripts\python.exe" -m pytest -vv -ra --tb=short -l --durations=5
set "EXITCODE=%ERRORLEVEL%"

:done
popd
if not defined CI pause
exit /b %EXITCODE%

:fail
echo [error] Setup or test run failed.
set "EXITCODE=1"
goto :done
