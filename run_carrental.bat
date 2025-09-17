@echo off
setlocal ENABLEDELAYEDEXECUTION

REM ------------------------------------------------------------------
REM  Fred's Car Rental - Windows launcher (.bat)
REM  Usage:
REM     double-click to run (auto-pause on exit)
REM     or from CMD/Windows Terminal:  run_carrental.bat nopause
REM ------------------------------------------------------------------

REM --- Project root = the folder where this .bat lives ---
set "ROOT=%~dp0"
pushd "%ROOT%"

REM --- Optional: skip pause if 'nopause' is passed ---
if /I "%~1"=="nopause" set "NO_PAUSE=1"

REM --- Ensure a Python virtual environment exists (.venv) ---
if not exist ".venv\Scripts\python.exe" (
  echo [setup] Creating virtual environment...
  py -3 -m venv .venv 2>nul || python -m venv .venv
)

REM --- Activate venv ---
call ".venv\Scripts\activate.bat"

REM --- Install dependencies if requirements.txt exists ---
if exist "requirements.txt" (
  echo [setup] Installing requirements...
  pip install -r requirements.txt
)

REM --- Run the app from src so the 'carrental' package is found ---
pushd "src"
python -m carrental
set "EXITCODE=%ERRORLEVEL%"
popd

popd

if not defined NO_PAUSE (
  echo ---------------------------------------------------------------
  echo  Exit code: %EXITCODE%   (close this window or press any key)
  pause >nul
)

exit /b %EXITCODE%
