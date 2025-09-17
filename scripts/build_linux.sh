#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJ_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJ_ROOT"
echo "[build] Project root: $PROJ_ROOT"

[[ -f src/carrental/main.py ]] || { echo "ERROR: Missing src/carrental/main.py"; exit 1; }
[[ -f tools/app_runner.py ]] || { echo "ERROR: Missing tools/app_runner.py"; exit 1; }
[[ -f tools/seed_runner.py ]] || { echo "ERROR: Missing tools/seed_runner.py"; exit 1; }

PYTHON_EXE="${PYTHON_EXE:-python3}"

echo "[build] Creating venv..."
if [[ ! -d .venv ]]; then
  "$PYTHON_EXE" -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
if [[ -f requirements.txt ]]; then
  pip install -r requirements.txt
fi
pip install pyinstaller

export PYTHONPATH="$PROJ_ROOT/src"

echo "[build] Building app executable (auto-seeds on startup)..."
python -m PyInstaller --noconfirm --onefile --name FredsCarRental --paths src tools/app_runner.py

echo "[build] Building seeder executable (optional manual seed)..."
python -m PyInstaller --noconfirm --onefile --name FredsCarRentalSeeder --paths src tools/seed_runner.py

echo
echo "[build] Done. Binaries in ./dist/"
