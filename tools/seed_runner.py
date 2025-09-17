#!/usr/bin/env python
"""
Standalone seeder entrypoint (optional; no app code changes).
- Creates an admin if missing.
- Ensures at least 10 cars exist by topping up with random cars.
- Uses the SAME DB path the app uses by importing the app's Database helper.
"""
from __future__ import annotations
import argparse, random, sys
from carrental.storage.db import Database
from carrental.storage.repositories import UserRepository, CarRepository

MAKES = {
    "Toyota": ["Yaris","Corolla","Camry","RAV4"],
    "Honda": ["Fit","City","Civic","CR-V"],
    "Mazda": ["2","3","CX-5"],
    "Volkswagen": ["Polo","Golf","Tiguan"],
    "Mitsubishi": ["ASX","Outlander","Eclipse Cross"],
    "Nissan": ["Note","Sylphy","Qashqai","X-Trail"],
    "Hyundai": ["i20","i30","Elantra","Tucson"],
    "Kia": ["Rio","Cerato","Seltos","Sportage"],
    "Ford": ["Fiesta","Focus","Mondeo","Escape"],
}

def rand_car():
    make = random.choice(list(MAKES.keys()))
    model = random.choice(MAKES[make])
    year = random.randint(2016, 2024)
    km = random.randint(10_000, 180_000)
    rate = round(random.uniform(39, 129), 2)
    available = True
    min_days = 1
    max_days = random.choice([7, 14, 21, 30])
    vehicle_type = random.choice(["Sedan", "Hatchback", "SUV", "Ute", "Van"])
    return make, model, year, km, rate, available, min_days, max_days, vehicle_type

def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--admin-email", default="admin@local")
    ap.add_argument("--admin-name", default="Administrator")
    ap.add_argument("--admin-password", default="Admin@123")
    ap.add_argument("--car-count", type=int, default=10)
    args, _ = ap.parse_known_args()

    db = Database.instance()
    users = UserRepository(db)
    cars = CarRepository(db)

    # Admin
    existing = users.get_by_email(args.admin_email)
    if not existing:
        users.create(args.admin_email, args.admin_password, args.admin_name, "ADMIN")
        print(f"[seed] Created admin: {args.admin_email}")
    else:
        print(f"[seed] Admin exists: {args.admin_email}")

    # Cars: top up to N
    try:
        current = cars.list(only_available=False)
    except TypeError:
        current = cars.list()
    missing = max(0, args.car_count - len(current))
    for _ in range(missing):
        mk, md, yr, km, rate, avail, min_d, max_d, vtype = rand_car()
        cars.add(mk, md, yr, km, rate, avail, min_d, max_d, vtype)
    try:
        total = len(cars.list(only_available=False))
    except TypeError:
        total = len(cars.list())
    print(f"[seed] Done. Cars in DB: {total}")

if __name__ == "__main__":
    main()
