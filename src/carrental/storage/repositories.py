# ==============================================================================
# Small data layer helpers for figures like users and cars.
# Every step tells you plainly what it does.

# ==============================================================================

"""Repository layer: all SQL is kept here so the rest of the app stays clean."""  # Repositories hide the database details.

from __future__ import annotations  # Modern hints.
import hashlib  # To hash passwords safely.
from typing import List, Optional, Dict, Any  # Type names.
from carrental.storage.db import Database  # DB helper.

def _hash(pw: str) -> str:  # Turn a plain password into a safe, scrambled string.
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()  # SHA-256 produces a long hex string.

class UserRepository:  # All user-related SQL goes here.
    def __init__(self, db: Database) -> None:  # Build the repo.
        self.db = db  # Save the DB so we can use it later.
    def get_by_email(self, email: str) -> Optional[Dict]:  # Find a user by email.
        with self.db.unit_of_work() as con:  # Open a transaction.
            cur = con.cursor()  # Get a cursor.
            cur.execute("SELECT * FROM users WHERE email=?", (email,))  # Run SQL to fetch the row.
            row = cur.fetchone()  # Get one row or None.
            return dict(row) if row else None  # Turn it into a dict if it exists.
    def create(self, email: str, password: str, name: str, role: str) -> bool:  # Add a new user.
        try:  # It might fail (e.g., duplicate email), so we protect it.
            with self.db.unit_of_work() as con:  # Transaction.
                cur = con.cursor()  # Cursor.
                cur.execute("INSERT INTO users (email, password_hash, name, role) VALUES (?, ?, ?, ?)", (email, _hash(password), name, role))  # Insert.
            return True  # If we got here, it worked.
        except Exception:  # Any error means False.
            return False  # Insert failed.
    def verify(self, email: str, password: str) -> Optional[Dict]:  # Check if email+password match.
        user = self.get_by_email(email)  # Find user first.
        if not user:  # If we didn't find one...
            return None  # Login fails.
        if user["password_hash"] != _hash(password):  # Compare hashed password.
            return None  # Wrong password.
        return user  
    def list_by_role(self, role: str) -> List[Dict]:
        with self.db.unit_of_work() as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE role=? ORDER BY id", (role,))
            return [dict(r) for r in cur.fetchall()]

    def list_admins(self) -> List[Dict]:
        return self.list_by_role("admin")

    def delete_by_id(self, user_id: int) -> bool:
        with self.db.unit_of_work() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM users WHERE id=?", (user_id,))
            return cur.rowcount > 0

    def delete_by_email(self, email: str) -> bool:
        with self.db.unit_of_work() as con:
            cur = con.cursor()
            cur.execute("DELETE FROM users WHERE email=?", (email,))
            return cur.rowcount > 0

    def set_password(self, email: str, new_password: str) -> bool:
        with self.db.unit_of_work() as con:
            cur = con.cursor()
            cur.execute("UPDATE users SET password_hash=? WHERE email=?", (_hash(new_password), email))
            return cur.rowcount > 0

    def set_email(self, old_email: str, new_email: str) -> bool:
        with self.db.unit_of_work() as con:
            cur = con.cursor()
            cur.execute("UPDATE users SET email=? WHERE email=?", (new_email, old_email))
            return cur.rowcount > 0

    def set_name(self, email: str, new_name: str) -> bool:
        with self.db.unit_of_work() as con:
            cur = con.cursor()
            cur.execute("UPDATE users SET name=? WHERE email=?", (new_name, email))
            return cur.rowcount > 0
# Success: return the whole user dict.

class CarRepository:  # SQL for cars.
    def __init__(self, db: Database) -> None:  # Build repo.
        self.db = db  # Save DB.
    def list(self, *, only_available: bool = True) -> List[Dict]:  # List all cars, maybe only available ones.
        with self.db.unit_of_work() as con:  # Transaction.
            cur = con.cursor()  # Cursor.
            sql = "SELECT * FROM cars"  # Base query.
            if only_available:  # If caller only wants available...
                sql += " WHERE available=1"  # Only rows with available=1.
            cur.execute(sql)  # Run query.
            return [dict(r) for r in cur.fetchall()]  # Convert all rows to dictionaries.
    def add(self, make: str, model: str, year: int, mileage: int, daily_rate: float, available: bool, min_days: int, max_days: int, vehicle_type: str) -> bool:  # Insert car.
        with self.db.unit_of_work() as con:  # Transaction.
            cur = con.cursor()  # Cursor.
            cur.execute("INSERT INTO cars (make, model, year, mileage, daily_rate, available, min_days, max_days, vehicle_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (make, model, year, mileage, daily_rate, 1 if available else 0, min_days, max_days, vehicle_type))  # Insert row.
            return True  # Insert ok.
    def update(self, car_id: int, *, make: Optional[str] = None, model: Optional[str] = None, year: Optional[int] = None, mileage: Optional[int] = None, daily_rate: Optional[float] = None, min_days: Optional[int] = None, max_days: Optional[int] = None, available: Optional[bool] = None) -> bool:  # Update only provided fields.
        fields: List[str] = []
        values: List[Any] = []
        if make is not None: fields.append("make=?"); values.append(make)
        if model is not None: fields.append("model=?"); values.append(model)
        if year is not None: fields.append("year=?"); values.append(year)
        if mileage is not None: fields.append("mileage=?"); values.append(mileage)
        if daily_rate is not None: fields.append("daily_rate=?"); values.append(daily_rate)
        if min_days is not None: fields.append("min_days=?"); values.append(min_days)
        if max_days is not None: fields.append("max_days=?"); values.append(max_days)
        if available is not None: fields.append("available=?"); values.append(1 if available else 0)
        if not fields:
            return False
        values.append(car_id)
        with self.db.unit_of_work() as con:
            cur = con.cursor()
            cur.execute("UPDATE cars SET " + ", ".join(fields) + " WHERE id=?", tuple(values))
            return cur.rowcount > 0  # True if a row was changed.
    def delete(self, car_id: int) -> bool:  # Remove a car.
        with self.db.unit_of_work() as con:  # Transaction.
            cur = con.cursor()  # Cursor.
            cur.execute("DELETE FROM cars WHERE id=?", (car_id,))  # Delete row.
            return cur.rowcount > 0  # True if a row was deleted.
    def get(self, car_id: int) -> Optional[Dict]:  # Read one car.
        with self.db.unit_of_work() as con:  # Transaction.
            cur = con.cursor()  # Cursor.
            cur.execute("SELECT * FROM cars WHERE id=?", (car_id,))  # Select row.
            row = cur.fetchone()  # One or None.
            return dict(row) if row else None  # Dict or None.
    def set_availability(self, car_id: int, available: bool) -> None:  # Force availability flag.
        with self.db.unit_of_work() as con:  # Transaction.
            cur = con.cursor()  # Cursor.
            cur.execute("UPDATE cars SET available=? WHERE id=?", (1 if available else 0, car_id))  # Update.
    def toggle_availability(self, car_id: int) -> None:  # Flip available to the opposite value.
        with self.db.unit_of_work() as con:  # Transaction.
            cur = con.cursor()  # Cursor.
            cur.execute("UPDATE cars SET available = 1 - available WHERE id=?", (car_id,))  # Clever trick: 1-0=1, 1-1=0.

class BookingRepository:  # All booking-related SQL.
    def __init__(self, db: Database) -> None:  # Build repo.
        self.db = db  # Save DB.
    def create(self, user_id: int, car_id: int, start: str, end: str, total_price: float) -> bool:  # Insert booking.
        with self.db.unit_of_work() as con:  # Transaction.
            cur = con.cursor()  # Cursor.
            cur.execute("INSERT INTO bookings (user_id, car_id, start_date, end_date, total_price, status) VALUES (?, ?, ?, ?, ?, ?)", (user_id, car_id, start, end, total_price, "PENDING"))  # Insert row.
            return True  # Insert ok.
    def list(self, *, user_id: Optional[int] = None, status: Optional[str] = None) -> List[Dict]:  # Read many bookings.
        with self.db.unit_of_work() as con:  # Transaction.
            cur = con.cursor()  # Cursor.
            sql = "SELECT * FROM bookings"  # Base query.
            params: List[Any] = []  # Values for placeholders.
            where: List[str] = []  # Conditions.
            if user_id is not None:  # Add condition if asked.
                where.append("user_id=?"); params.append(user_id)  # Filter by user.
            if status is not None:  # Add condition if asked.
                where.append("status=?"); params.append(status)  # Filter by status.
            if where:  # If any conditions were added...
                sql += " WHERE " + " AND ".join(where)  # Attach them to SQL.
            sql += " ORDER BY id DESC"  # Newest first looks nicer.
            cur.execute(sql, tuple(params))  # Run query.
            return [dict(r) for r in cur.fetchall()]  # Turn rows into dicts.
    def set_status(self, booking_id: int, status: str) -> None:  # Update status for one booking.
        with self.db.unit_of_work() as con:  # Transaction.
            cur = con.cursor()  # Cursor.
            cur.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))  # Update.
    def get(self, booking_id: int) -> Optional[Dict]:  # Read a single booking.
        with self.db.unit_of_work() as con:  # Transaction.
            cur = con.cursor()  # Cursor.
            cur.execute("SELECT * FROM bookings WHERE id=?", (booking_id,))  # Run query.
            row = cur.fetchone()  # One or None.
            return dict(row) if row else None  # Dict or None.
