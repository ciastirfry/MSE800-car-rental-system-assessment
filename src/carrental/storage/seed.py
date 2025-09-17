# ==============================================================================
# Tiny seeding helpers that insert default data.
# Every step tells you plainly what it does.
#   - DESIGN PATTERN: Factory Method used via CarFactory
# ==============================================================================

"""Seed example admin user and cars if the database is empty."""  # Helpful for demos and testing.

from __future__ import annotations  # Modern hints.
from carrental.storage.db import Database  # DB singleton.
from carrental.storage.repositories import UserRepository, CarRepository  # Repos.
from carrental.core.factories import CarFactory  # Factory to build Car objects.

def seed_if_empty(db: Database) -> None:  # Add starting data only if nothing exists.
    urepo = UserRepository(db)  # User repo.
    crepo = CarRepository(db)  # Car repo.
    # -- admin user --
    if not urepo.get_by_email("admin@admin.com"):  # Only create if missing.
        urepo.create("admin@admin.com", "admin123", "Admin", "admin")  # Email: admin@example.com, password: admin.
    # -- cars --
    if not crepo.list(only_available=False):  # Only create cars if none exist.
        f = CarFactory()  # Build cars.
        samples = [  # Sample data: (make, model, year, mileage, daily_rate).
            ("Toyota", "Corolla", 2020, 25000, 55.0),
            ("Honda", "Civic", 2021, 18000, 60.0),
            ("Tesla", "Model 3", 2022, 12000, 120.0),
        ]  # You can add more later.
        for make, model, year, mileage, rate in samples:  # For each sample...
            car = f.create(make, model, year, mileage, rate, 1, 30)  # Build a Car object.
            crepo.add(car.make, car.model, car.year, car.mileage, car.daily_rate, car.available, car.min_days, car.max_days, car.vehicle_type)  # Save it.

        # Add 10 random cars
        import random
        makes = {
            "Toyota": ["Yaris","Corolla","RAV4"],
            "Honda": ["Jazz","Civic","CR-V"],
            "Ford": ["Fiesta","Focus","Escape"],
            "Hyundai": ["i20","i30","Tucson"],
            "Kia": ["Rio","Cerato","Sportage"],
            "Nissan": ["Tiida","Sylphy","X-Trail"],
            "Subaru": ["Impreza","XV","Forester"],
            "Mazda": ["2","3","CX-5"],
            "Volkswagen": ["Polo","Golf","Tiguan"],
            "Mitsubishi": ["ASX","Outlander","Eclipse Cross"],
        }
        for _ in range(10):
            mk = random.choice(list(makes.keys()))
            md = random.choice(makes[mk])
            yr = random.randint(2017, 2023)
            km = random.randint(10000, 120000)
            rate = round(random.uniform(45, 120), 2)
            car = CarFactory().create(mk, md, yr, km, rate, 1, 30)
            crepo.add(car.make, car.model, car.year, car.mileage, car.daily_rate,
                      car.available, car.min_days, car.max_days, car.vehicle_type)

