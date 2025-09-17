# ==============================================================================
# SQLite helper that opens/creates our database file.
# This file is the 'explained like I am 10' version with simple comments.
# Every step tells you plainly what it does.
#   - DESIGN PATTERN: Singleton (single Database used app‑wide)
# ==============================================================================

"""SQLite database helper (Singleton + Unit of Work)."""  # One connection for the whole app to share safely.

from __future__ import annotations  # Modern hints.
import sqlite3, threading, os  # Database driver, a lock, and file paths.
from contextlib import contextmanager  # Lets us build a "with ...:" helper.
from typing import Iterator  # Type of the generator we return.

class Database:  # Our database manager.
    _instance: "Database | None" = None  # A single copy for the whole program (Singleton).
    _lock = threading.Lock()  # A lock so two threads do not create two instances at the same time.

    def __init__(self, path: str | None = None) -> None:  # Create the object with a file path.
        # Place the database file next to the code unless a path is given.
        default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "carrental.db"))  # Build a default path.
        self.path = os.path.abspath(path or default_path)  # Use given path or default.
        self._conn: sqlite3.Connection | None = None  # The actual SQLite connection starts as None (not opened yet).

    @classmethod  # This method belongs to the class, not an instance.
    def instance(cls) -> "Database":  # Get the one-and-only Database instance.
        with cls._lock:  # Make this block thread-safe.
            if cls._instance is None:  # If we have not made one yet...
                cls._instance = Database()  # Create it.
            return cls._instance  # Give back the same object every time.

    def connect(self) -> sqlite3.Connection:  # Open the SQLite connection if needed and return it.
        if self._conn is None:  # If we have not connected yet...
            self._conn = sqlite3.connect(self.path, check_same_thread=False)  # Open the file as a database.
            self._conn.row_factory = sqlite3.Row  # Make rows act like dictionaries (name-based access).
            self._ensure_schema()  # Make sure tables exist.
        return self._conn  # Give back the connection.

    @contextmanager  # This makes a "with db.unit_of_work() as con:" helper.
    def unit_of_work(self) -> Iterator[sqlite3.Connection]:  # A tiny transaction manager.
        con = self.connect()  # Get the connection (opens if needed).
        try:  # Try to do changes.
            yield con  # Give the connection to the caller's code.
            con.commit()  # If no error happened, save the changes.
        except Exception:  # If something went wrong...
            con.rollback()  # Undo any half-done work.
            raise  # Re-raise so the caller sees the error.

    # --- schema ---
    def _ensure_schema(self) -> None:  # Create tables the first time the app runs.
        con = self._conn  # Short name.
        cur = con.cursor()  # A cursor lets us run SQL.
        # Create users table.
        cur.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL
        )""")  # Users table schema.
        # Create cars table.
        cur.execute("""CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            mileage INTEGER NOT NULL,
            daily_rate REAL NOT NULL,
            available INTEGER NOT NULL,
            min_days INTEGER NOT NULL DEFAULT 1,
            max_days INTEGER NOT NULL DEFAULT 30,
            vehicle_type TEXT NOT NULL
        )""")  # Cars table schema.
        # Create bookings table.
        cur.execute("""CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            total_price REAL NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(car_id) REFERENCES cars(id)
        )""")  # Bookings table schema.
