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

REM --- Install pytest + coverage + HTML reporter ---
echo [setup] Installing pytest-cov and pytest-html ...
".venv\Scripts\python.exe" -m pip install -U pytest pytest-cov pytest-html || goto :fail

REM --- Make sure src is importable ---
set "PYTHONPATH=%CD%\src"

REM --- Run tests with coverage + HTML report ---
set "REPORT=pytest_report.html"
echo [tests] Running pytest with coverage and HTML report...
".venv\Scripts\python.exe" -m pytest -vv ^
  --cov=src/carrental --cov-report=term-missing:skip-covered ^
  --html=%REPORT% --self-contained-html

set "EXITCODE=%ERRORLEVEL%"

REM --- Open report if it exists ---
if exist "%REPORT%" (
  echo [report] Opening %REPORT% ...
  start "" "%REPORT%"
)

:done
popd
if not defined CI pause
exit /b %EXITCODE%

:fail
echo [error] Setup or test run failed.
set "EXITCODE=1"
goto :done
