#!/usr/bin/env python
"""
App entrypoint for frozen builds (no changes to your code).
- Uses absolute imports (avoids relative-import issues in PyInstaller).
- Seeds admin + sample cars automatically on first run via your existing seed_if_empty().
"""
from __future__ import annotations
import sys

try:
    # Absolute imports from your package
    from carrental.main import main as app_main
    from carrental.storage.db import Database
    from carrental.storage.seed import seed_if_empty
except Exception as e:
    # If import fails, show a readable error and exit non-zero so PyInstaller prints something useful.
    print(f"[startup] Import error: {e}", file=sys.stderr)
    raise

def _auto_seed():
    try:
        db = Database.instance()
        seed_if_empty(db)  # This function already guards against duplicates/emptiness in your codebase
        print("[startup] Seeding completed (or already present).")
    except Exception as e:
        # Do not block app startup if seeding has a minor issue; just log it.
        print(f"[startup] Seeding skipped due to: {e}", file=sys.stderr)

def main():
    _auto_seed()
    app_main()

if __name__ == "__main__":
    main()
