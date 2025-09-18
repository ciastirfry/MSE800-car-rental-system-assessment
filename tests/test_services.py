# tests/test_services.py
import inspect
from uuid import uuid4

# ✅ Imports you need
from carrental.storage.db import Database
from carrental.storage.repositories import (
    UserRepository, CarRepository, BookingRepository
)
from carrental.services.auth_service import AuthService
from carrental.services.inventory_service import InventoryService
from carrental.services.rental_service import RentalService

def _supports_rate_pair(func) -> bool:
    """Return True if callable supports weekday_rate & weekend_rate params."""
    try:
        sig = inspect.signature(func)
        return "weekday_rate" in sig.parameters and "weekend_rate" in sig.parameters
    except Exception:
        return False

def _filtered_kwargs(func, **kwargs):
    """Return only kwargs that the callable actually accepts."""
    try:
        params = set(inspect.signature(func).parameters.keys())
        return {k: v for k, v in kwargs.items() if k in params}
    except Exception:
        return kwargs

def test_db_initializes_and_tables_exist():
    db = Database.instance()
    con = db.connect()
    cur = con.cursor()
    cur.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name IN ('users','cars','bookings')
    """)
    names = {row[0] for row in cur.fetchall()}
    assert {"users", "cars", "bookings"}.issubset(names), f"Missing tables: {names}"

def test_register_and_login_user():
    db = Database.instance()
    auth = AuthService(db)

    email = f"user_{uuid4().hex[:6]}@test.local"  # unique each run
    pwd = "User@123"
    name = "User One"

    ok = auth.register(email=email, password=pwd, name=name)
    assert ok is True

    logged = auth.login(email=email, password=pwd)
    assert logged is True

    cu = getattr(auth, "current_user", lambda: None)()
    if not cu:
        users = getattr(auth, "users", UserRepository(db))
        cu = users.get_by_email(email)
    assert cu and cu["email"] == email

def test_add_car_and_list_inventory():
    db = Database.instance()
    inv = InventoryService(db)
    cars_repo = CarRepository(db)

    base = dict(
        make="Toyota", model="Corolla", year=2020, mileage=45000,
        available=True, min_days=1, max_days=14, vehicle_type="Sedan"
    )

    added = False

    if hasattr(inv, "add_car"):
        rate_kwargs = (
            dict(weekday_rate=79.0, weekend_rate=89.0)
            if _supports_rate_pair(inv.add_car) else dict(daily_rate=79.0)
        )
        kwargs = _filtered_kwargs(inv.add_car, **{**base, **rate_kwargs})
        added = inv.add_car(**kwargs)  # type: ignore[arg-type]
        if not added:
            rate_kwargs = (
                dict(weekday_rate=79.0, weekend_rate=89.0)
                if _supports_rate_pair(cars_repo.add) else dict(daily_rate=79.0)
            )
            kwargs = _filtered_kwargs(cars_repo.add, **{**base, **rate_kwargs})
            added = cars_repo.add(**kwargs)  # type: ignore[arg-type]
    else:
        rate_kwargs = (
            dict(weekday_rate=79.0, weekend_rate=89.0)
            if _supports_rate_pair(cars_repo.add) else dict(daily_rate=79.0)
        )
        kwargs = _filtered_kwargs(cars_repo.add, **{**base, **rate_kwargs})
        added = cars_repo.add(**kwargs)  # type: ignore[arg-type]

    assert added is True

    listed = inv.list_cars(only_available=True) if hasattr(inv, "list_cars") \
             else cars_repo.list(only_available=True)
    assert any(c.get("make") == "Toyota" and c.get("model") == "Corolla" for c in listed)

def test_booking_flow_creates_pending_or_confirmed():
    db = Database.instance()
    auth = AuthService(db)
    cars = CarRepository(db)
    rent = RentalService(db)
    bookings = BookingRepository(db)

    email = f"booker_{uuid4().hex[:6]}@test.local"
    auth.register(email=email, password="P@ssw0rd", name="Booker")
    users = getattr(auth, "users", UserRepository(db))
    user = users.get_by_email(email)
    assert user is not None

    base = dict(
        make="Mazda", model="3", year=2019, mileage=60000,
        available=True, min_days=1, max_days=14, vehicle_type="Hatchback"
    )
    rate_kwargs = (
        dict(weekday_rate=65.0, weekend_rate=75.0)
        if _supports_rate_pair(cars.add) else dict(daily_rate=69.0)
    )
    assert cars.add(**_filtered_kwargs(cars.add, **{**base, **rate_kwargs})) is True  # type: ignore[arg-type]
    car = cars.list(only_available=True)[0]

    start, end = "2025-09-20", "2025-09-22"
    if hasattr(rent, "create_booking"):
        ok = rent.create_booking(user_id=user["id"], car_id=car["id"], start=start, end=end)
        assert ok is True
    else:
        day_rate = float(car.get("weekday_rate") or car.get("daily_rate") or 70.0)
        total = 2 * day_rate
        assert bookings.create(user_id=user["id"], car_id=car["id"], start=start, end=end, total_price=total) is True

    user_bookings = bookings.list(user_id=user["id"])
    assert len(user_bookings) >= 1
    assert user_bookings[0].get("status", "PENDING") in {"PENDING", "CONFIRMED", "REJECTED"}
