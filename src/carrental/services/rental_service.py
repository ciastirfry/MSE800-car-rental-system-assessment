# ==============================================================================
# Business rules for bookings and price calculation.
# Every step tells you plainly what it does.
#   - DESIGN PATTERN: Observer (place where we would notify listeners when a booking is approved)
# ==============================================================================

"""Rental service: quotes, bookings, and approvals."""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
from carrental.storage.db import Database
from carrental.storage.repositories import BookingRepository, CarRepository
from carrental.core.strategies import WeekendMultiplierStrategy, PaymentStrategy, CashPayment

class RentalService:
    def __init__(self, db: Database, pricing: Optional[WeekendMultiplierStrategy] = None) -> None:
        self.bookings = BookingRepository(db)  # bookings repo
        self.cars = CarRepository(db)          # cars repo
        self.pricing = pricing or WeekendMultiplierStrategy()
        self._current_user_id: Optional[int] = None  # set by UI after login

    # Allow UI to set/clear the current user id (used by commands)
    def set_current_user_id(self, user_id: Optional[int]) -> None:
        self._current_user_id = user_id

    def quote(self, car_id: int, start: str, end: str) -> Tuple[float, Dict[str, float]]:  # Calculate cost for a date range.
        car = self.cars.get(car_id)  # Read the car from DB.
        if not car or not car.get("available", 0):  # If no car or not available...
            raise ValueError("Car is not available")  # Tell the caller.
        total, details = self.pricing.quote(car["daily_rate"], start, end)  # Use the pricing strategy.
        # Enforce car-specific min/max rental days.
        days_total = int(details.get("weekday_days", 0) + details.get("weekend_days", 0))
        min_days = int(car.get("min_days", 1))
        max_days = int(car.get("max_days", 30))
        if days_total < min_days:
            raise ValueError(f"Minimum rental is {min_days} day(s).")
        if days_total > max_days:
            raise ValueError(f"Maximum rental is {max_days} day(s).")
        details["days_total"] = float(days_total)  # add for summaries
        return total, details

    def make_booking(self, *, user_id: Optional[int] = None, car_id: int, start_date: str, end_date: str, payment: Optional[PaymentStrategy] = None) -> tuple[bool, str]:
        uid = user_id if user_id is not None else self._current_user_id
        if uid is None:
            return False, "No logged-in user."
        try:
            price, _ = self.quote(car_id, start_date, end_date)
        except Exception as ex:
            return False, f"Cannot book: {ex}"
        strategy = payment or CashPayment()
        if not strategy.pay(price):
            return False, "Payment failed."
        ok = self.bookings.create(uid, car_id, start_date, end_date, price)
        return (True, "Booking placed. Awaiting approval.") if ok else (False, "Could not save booking.")

    def my_bookings_table(self, user_id: Optional[int] = None) -> tuple[List[List[str]], List[str]]:
        uid = user_id if user_id is not None else self._current_user_id
        items = self.bookings.list(user_id=uid)
        headers = ["ID","Car","Start","End","Total","Status"]
        rows = [[b["id"], b["car_id"], b["start_date"], b["end_date"], f'{b["total_price"]:.2f}', b["status"]] for b in items]
        return rows, headers

    def pending_bookings(self) -> List[Dict]:
        return self.bookings.list(status="PENDING")

    def pending_bookings_table(self) -> tuple[List[List[str]], List[str]]:
        items = self.pending_bookings()
        headers = ["ID","User","Car","Start","End","Total"]
        rows = [[b["id"], b["user_id"], b["car_id"], b["start_date"], b["end_date"], f'{b["total_price"]:.2f}'] for b in items]
        return rows, headers

    def set_booking_status(self, booking_id: int, status: str) -> None:
        self.bookings.set_status(booking_id, status)
        if status == "APPROVED":
            bk = self.bookings.get(booking_id)
            if bk:
                self.cars.set_availability(bk["car_id"], False)

    def available_cars_table(self) -> tuple[list[list[str]], list[str]]:
        """Return rows+headers for currently available cars."""
        items = self.cars.list(only_available=True)
        headers = ["ID","Make","Model","Year","Mileage","Daily Rate"]
        rows = [[c["id"], c["make"], c["model"], c["year"], c["mileage"], f'{c["daily_rate"]:.2f}'] for c in items]
        return rows, headers
