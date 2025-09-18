# tests/conftest.py
import sys
import pathlib
import pytest

# Make "src" importable (no need to set PYTHONPATH)
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

@pytest.fixture(autouse=True)
def _isolate_cwd(tmp_path, monkeypatch):
    """
    Each test runs in its own temporary directory.
    Ensures a brand-new carrental.db per test session.
    """
    monkeypatch.chdir(tmp_path)

@pytest.fixture(autouse=True)
def _reset_db_singleton():
    """
    Reset the Database singleton before/after each test so connections
    and schema init are clean and independent.
    """
    try:
        from carrental.storage.db import Database
        if hasattr(Database, "_instance"):
            Database._instance = None  # type: ignore[attr-defined]
    except Exception:
        pass
    yield
    try:
        from carrental.storage.db import Database
        if hasattr(Database, "_instance"):
            Database._instance = None  # type: ignore[attr-defined]
    except Exception:
        pass
