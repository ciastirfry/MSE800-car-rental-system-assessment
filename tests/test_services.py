"""Basic in-memory tests for services."""  # doc
from __future__ import annotations  # future hints
from carrental.storage.db import Database  # db
from carrental.storage.seed import seed_if_empty  # seed
from carrental.services.auth_service import AuthService  # auth
from carrental.services.inventory_service import InventoryService  # inv
from carrental.services.rental_service import RentalService  # rent

def setup_module(module):  # pytest setup
    db = Database.instance()  # db
    db.path = ":memory:"  # in memory
    db._conn = None  # reset
    db.ensure_schema()  # schema
    seed_if_empty(db)  # seed

def test_quote_book_approve():  # flow
    db = Database.instance()  # db
    auth, inv, rent = AuthService(db), InventoryService(db), RentalService(db)  # services
    assert auth.register("u@example.com", "pw", "U")  # register
    cars = inv.list_cars(only_available=True)  # list
    assert cars  # some
    car_id = cars[0]["id"]  # first
    total, info = rent.quote(car_id, "2025-01-10", "2025-01-12")  # quote
    assert total > 0  # positive
    assert rent.book(1, car_id, "2025-01-10", "2025-01-12", total)  # book
    pend = rent.list_bookings(status="PENDING")  # pending
    assert pend  # exists
    bid = pend[0]["id"]  # id
    rent.set_booking_status(bid, "APPROVED")  # approve
    avail_ids = [c["id"] for c in inv.list_cars(only_available=True)]  # available
    assert car_id not in avail_ids  # removed
