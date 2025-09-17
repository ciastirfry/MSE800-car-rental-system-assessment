# ==============================================================================
# Inventory logic for cars (add, update, list).
# Every step tells you plainly what it does.

# ==============================================================================

"""Inventory service for cars."""  # Keeps car logic tidy and away from SQL details.

from __future__ import annotations  # Modern hints.
from typing import List, Dict, Optional  # Type names.
from carrental.storage.db import Database  # DB singleton.
from carrental.storage.repositories import CarRepository  # Where SQL lives.
from carrental.core.factories import CarFactory  # Builds clean Car objects.

class InventoryService:  # High-level API for car operations.
    def __init__(self, db: Database) -> None:  # Build the service.
        self.car_repo = CarRepository(db)  # Keep a repo for DB operations.
        self.factory = CarFactory()  # Build car objects consistently.
    def list_cars(self, only_available: bool = True) -> List[Dict]:  # Read all cars.
        return self.car_repo.list(only_available=only_available)  # Ask the repo.
    def add_car(self, make: str, model: str, year: int, mileage: int, daily_rate: float, min_days: int, max_days: int) -> bool:  # Create a car.
        car = self.factory.create(make, model, year, mileage, daily_rate, min_days, max_days)  # Build a Car object.
        return self.car_repo.add(car.make, car.model, car.year, car.mileage, car.daily_rate, car.available, car.min_days, car.max_days, car.vehicle_type)  # Save it.
    def update_car(self, car_id: int, *, available: Optional[bool] = None,  make: Optional[str] = None, model: Optional[str] = None, year: Optional[int] = None, mileage: Optional[int] = None, daily_rate: Optional[float] = None, min_days: Optional[int] = None, max_days: Optional[int] = None) -> bool:  # Edit a car.
        return self.car_repo.update(car_id, available=available,  make=make, model=model, year=year, mileage=mileage, daily_rate=daily_rate, min_days=min_days, max_days=max_days)  # Ask repo to update changed fields.
    def delete_car(self, car_id: int) -> bool:  # Remove a car.
        return self.car_repo.delete(car_id)  # Ask repo.
    def toggle_availability(self, car_id: int) -> None:  # Flip availability.
        self.car_repo.toggle_availability(car_id)  # Ask repo.
    def set_availability(self, car_id: int, available: bool) -> None:  # Force availability.
        self.car_repo.set_availability(car_id, available)  # Ask repo.
    def get(self, car_id: int) -> Optional[Dict]:  # Read a single car.
        return self.car_repo.get(car_id)  # Ask repo.
