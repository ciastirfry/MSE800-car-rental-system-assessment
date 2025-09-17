#!/usr/bin/env bash
# Fred's Car Rental - portable shell launcher (macOS / Linux / WSL)
# Creates a venv (if missing), installs deps, and runs the app from src.

set -Eeuo pipefail

# --- locate project root (folder containing this script) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

usage() {
  cat <<'USAGE'
Usage: ./run_carrental.sh [--no-install] [--python PYTHON_BIN]

Options:
  --no-install     Skip 'pip install -r requirements.txt'
  --python BIN     Use a specific Python (e.g. python3.11)

Examples:
  ./run_carrental.sh
  ./run_carrental.sh --no-install
  ./run_carrental.sh --python python3.11
USAGE
}

NO_INSTALL=0
PY_BIN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-install) NO_INSTALL=1; shift ;;
    --python) PY_BIN="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

# --- find python ---
if [[ -z "${PY_BIN}" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PY_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PY_BIN="python"
  else
    echo "ERROR: Python not found. Install from https://www.python.org/ or your package manager." >&2
    exit 1
  fi
fi

# --- create venv if missing ---
if [[ ! -f ".venv/bin/python" ]]; then
  echo "[setup] Creating virtual environment with ${PY_BIN} ..."
  "${PY_BIN}" -m venv .venv
fi

# --- activate venv ---
# shellcheck disable=SC1091
source ".venv/bin/activate"

# --- install requirements (optional) ---
if [[ ${NO_INSTALL} -eq 0 && -f "requirements.txt" ]]; then
  echo "[setup] Installing requirements..."
  pip install -r requirements.txt
fi

# --- run the app from src so the 'carrental' package is importable ---
pushd "src" >/dev/null
python -m carrental
CODE=$?
popd >/dev/null

exit ${CODE}
