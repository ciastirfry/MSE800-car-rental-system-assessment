# ==============================================================================
# Factory that builds Car objects in one place.
# This file is the 'explained like I am 10' version with simple comments.
# Every step tells you plainly what it does.
#   - DESIGN PATTERN: Factory Method (object creation lives here)
# ==============================================================================

"""Factory that builds Car objects in one place."""  # Factory keeps object creation tidy and consistent.

from __future__ import annotations  # Modern hints on Python 3.10.
from typing import Protocol  # A Protocol describes what methods/fields a thing should have.
from carrental.core.models import Car  # We will build Car objects.

class Vehicle(Protocol):  # This is the general shape a "vehicle" must have.
    make: str  # The brand name.
    model: str  # The model name.
    year: int  # The year built.
    mileage: int  # How many kilometers driven.
    daily_rate: float  # Cost per day.
    available: bool  # Is it rentable?
    min_days: int  # Minimum rental days.
    max_days: int  # Maximum rental days.
    vehicle_type: str  # What kind of vehicle this is.

class VehicleFactory(Protocol):  # Any factory must provide "create(...)".
    def create(self, make: str, model: str, year: int, mileage: int, daily_rate: float, min_days: int, max_days: int) -> Vehicle: ...  # Method shape only.

class CarFactory:  # Our real factory that makes Car objects.
    """Creates Car objects with sensible defaults."""  # Human description.
    def create(self, make: str, model: str, year: int, mileage: int, daily_rate: float, min_days: int = 1, max_days: int = 30) -> Vehicle:  # Build a car.
        # We fill in all fields so every new car is complete and ready.
        return Car(make=make, model=model, year=year, mileage=mileage, daily_rate=daily_rate, available=True, min_days=min_days, max_days=max_days, vehicle_type="CAR")  # Return the new Car.
