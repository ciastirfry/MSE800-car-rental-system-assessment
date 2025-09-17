# ==============================================================================
# Lightweight models used by the program (Car structure).
# This file is the 'explained like I am 10' version with simple comments.
# Every step tells you plainly what it does.

# ==============================================================================

"""Data models for User, Car, and Booking."""  # This file describes the shapes of our main things.

from __future__ import annotations  # Allow modern type hints on Python 3.10.
from dataclasses import dataclass  # This decorator builds handy classes for us.
from typing import Optional  # "Optional" means a value can also be None (empty).

@dataclass  # This marks a simple class that only stores data.
class Entity:  # A tiny base class so every table can share an "id".
    id: Optional[int] = None  # The primary-key number from the database if one exists.

@dataclass  # A user of the system (admin or customer).
class User(Entity):  # Inherits from Entity, so it also has "id".
    email: str = ""  # The person's login email.
    password_hash: str = ""  # The scrambled password (never store real passwords!).
    name: str = ""  # Their display name.
    role: str = "customer"  # Either "customer" or "admin".

@dataclass  # A car that can be rented.
class Car(Entity):  # Inherits id too.
    make: str = ""  # The brand, like "Toyota".
    model: str = ""  # The model, like "Corolla".
    year: int = 0  # The year the car was made.
    mileage: int = 0  # How many kilometers the car has driven.
    daily_rate: float = 0.0  # How much it costs per day in dollars.
    available: bool = True  # Is the car ready to rent right now?
    min_days: int = 1  # The least number of days you may rent it.
    max_days: int = 30  # The most number of days you may rent it.
    vehicle_type: str = "CAR"  # A simple type name.

@dataclass  # One booking made by a user for a car.
class Booking(Entity):  # Inherits id too.
    user_id: int = 0  # The id of the user who booked (links to users table).
    car_id: int = 0  # The id of the car (links to cars table).
    start_date: str = ""  # The first day of the booking (YYYY-MM-DD).
    end_date: str = ""  # The last day of the booking (YYYY-MM-DD).
    total_price: float = 0.0  # How much the whole booking costs.
    status: str = "PENDING"  # Can be PENDING, APPROVED, or REJECTED.
