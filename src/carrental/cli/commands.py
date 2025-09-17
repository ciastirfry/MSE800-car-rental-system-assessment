# ==============================================================================
# Menu command classes that do the actions (show cars, add car, etc.).
# This file is the 'explained like I am 10' version with simple comments.
# Every step tells you plainly what it does.

# ==============================================================================

"""Command objects for each menu action (Command pattern)."""  # These classes perform actions when the user selects a menu item.

from __future__ import annotations  # Use modern type hints on Python 3.10.
from typing import Protocol  # A Protocol describes the shape of an object (like an interface).
from tabulate import tabulate  # Pretty table printing for lists of cars and bookings.
from carrental.utils.ui import box_text, boxed, prompt_center, prompt_center_hidden  # Helpers to draw message boxes and content boxes.

def _prompt_int(label: str, min_value: int = None, max_value: int = None) -> int:
    while True:
        s = prompt_center(label).strip()
        try:
            val = int(s)
            if min_value is not None and val < min_value:
                print(box_text(f"Value must be >= {min_value}")); continue
            if max_value is not None and val > max_value:
                print(box_text(f"Value must be <= {max_value}")); continue
            return val
        except ValueError:
            print(box_text("Please enter a whole number."))

def _prompt_float(label: str, min_value: float = None, max_value: float = None) -> float:
    while True:
        s = prompt_center(label).strip()
        try:
            val = float(s)
            if min_value is not None and val < min_value:
                print(box_text(f"Value must be >= {min_value}")); continue
            if max_value is not None and val > max_value:
                print(box_text(f"Value must be <= {max_value}")); continue
            return val
        except ValueError:
            print(box_text("Please enter a number (you can use decimals)."))
from carrental.utils.validators import prompt_date  # Helper to safely read dates from the keyboard.
from carrental.services.inventory_service import InventoryService  # Car store service.
from carrental.services.rental_service import RentalService  # Booking service.

# --- Helper: render large tables with simple paging ---
def _render_paged_table(rows, headers, title, page_size: int = 10):
    """Render rows in pages. Controls: [N]ext, [P]rev, [Q]uit/Enter."""
    total = len(rows)
    if total == 0:
        print(boxed(["(no data)"], title=title))
        return
    pages = (total + page_size - 1) // page_size  # ceil
    page = 0
    while True:
        start = page * page_size
        end = min(start + page_size, total)
        view = rows[start:end]
        page_title = f"{title} (page {page+1}/{pages})" if pages > 1 else title
        print(boxed([tabulate(view, headers=headers, tablefmt="github")], title=page_title))
        if pages == 1:
            break
        cmd = prompt_center("Press N-next, P-prev, or Enter to continue: ").strip().lower()
        if cmd in ("n", "next"):
            if page + 1 < pages:
                page += 1
            else:
                break
        elif cmd in ("p", "prev"):
            if page > 0:
                page -= 1
        else:
            break

class Command(Protocol):  # Every command must have a label and an execute() method.
    label: str  # Human-readable menu name like "Show cars".
    def execute(self) -> bool: ...  # Returns True to keep menu open, False to leave menu.

class LogoutCommand:  # Leaves the current menu and returns to the previous screen.
    label = "Logout"  # What will show in the menu.
    def execute(self) -> bool:  # When chosen...
        return False  # ...return False to tell the menu loop to stop (logout).

class ExitAppCommand:  # Closes the whole application.
    label = "Exit"  # Menu label.
    def execute(self) -> bool:  # When chosen...
        print(box_text("Thanks for using Fred's Car Rental!"))  # Say thank you.
        raise SystemExit(0)  # Stop the Python program with a success code.


class ShowCarsCommand:  # Shows a table of cars.
    label = "View Cars"  # Menu label.
    def __init__(self, inv: InventoryService, only_available: bool = True):  # Flag decides which list to show.
        self.inv = inv  # Store service.
        self.only_available = only_available  # Remember preference.
    def execute(self) -> bool:  # When chosen...
        cars = self.inv.list_cars(only_available=self.only_available)  # Ask the service for cars.
        if not cars:
            print(box_text("No cars in the system yet."))
            prompt_center("Press Enter…")
            return True
        rows = [[c["id"], c["make"], c["model"], c["year"], c["mileage"], "Yes" if c.get("available") else "No", c.get("min_days", 1), c.get("max_days", 30), f'{c.get("daily_rate", 0.0):.2f}'] for c in cars]
        _render_paged_table(rows, headers=["ID","Make","Model","Year","Mileage","Available","Min Days","Max Days","Daily Rate"], title="Cars")
        prompt_center("Press Enter…")
        return True
        rows = [[c["id"], c["make"], c["model"], c["year"], c["mileage"], "Yes" if c.get("available") else "No", c.get("min_days", 1), c.get("max_days", 30), f'{c.get("daily_rate", 0.0):.2f}'] for c in cars]
        print(boxed([tabulate(rows, headers=["ID","Make","Model","Year","Mileage","Available","Min Days","Max Days","Daily Rate"], tablefmt="github")], title="Cars"))
        prompt_center("Press Enter…")
        return True


class AdminAddCarCommand:
    label = "Add Car"
    def __init__(self, inv: InventoryService):
        self.inv = inv
    def execute(self) -> bool:
        print(box_text("ADD NEW CAR (Admin)"))
        make = prompt_center("Make: ").strip()
        model = prompt_center("Model: ").strip()
        year = _prompt_int("Year: ", 1980, 2100)
        mileage = _prompt_int("Mileage: ", 0)
        daily_rate = _prompt_float("Daily Rate: ", 0)
        min_days = _prompt_int("Min Days: ", 1)
        max_days = _prompt_int("Max Days: ", min_days)
        ok = self.inv.add_car(make, model, year, mileage, daily_rate, min_days, max_days)
        print(box_text("Car added successfully." if ok else "Could not add car."))
        prompt_center("Press Enter…")
        return True


class AddCarCommand:
    label = "Add Car"
    def __init__(self, inv: InventoryService):
        self.inv = inv

    def _next_id(self) -> int:
        try:
            cars = self.inv.list_cars(only_available=False)
            if not cars:
                return 1
            return max(int(c.get("id", 0)) for c in cars) + 1
        except Exception:
            return 1

    def execute(self) -> bool:
        nxt = self._next_id()
        lines = [f"New Car ID (auto): {nxt}", "Fill in the details below:"]
        print(boxed(lines, title="Add New Car"))
        make = prompt_center("Make: ").strip()
        model = prompt_center("Model: ").strip()
        year = _prompt_int("Year: ", 1980, 2100)
        mileage = _prompt_int("Mileage: ", 0)
        daily_rate = _prompt_float("Daily Rate: ", 0)
        min_days = _prompt_int("Min Days: ", 1)
        max_days = _prompt_int("Max Days: ", min_days)
        ok = self.inv.add_car(make, model, year, mileage, daily_rate, min_days, max_days)
        print(box_text(f"Car added with ID ~{nxt}." if ok else "Could not add car."))
        prompt_center("Press Enter…")
        return True

  # Edits a car that already exists.
    label = "Update Car"  # Menu label.
    def __init__(self, inv: InventoryService):  # Needs inventory to modify cars.
        self.inv = inv  # Save the service.
    def execute(self) -> bool:  # When chosen...
        cars = self.inv.list_cars(only_available=False)
        if cars:
            rows = [[c["id"], c["make"], c["model"], c["year"], c["mileage"], "Yes" if c.get("available") else "No", c.get("min_days", 1), c.get("max_days", 30), f'{c.get("daily_rate", 0.0):.2f}'] for c in cars]
            _render_paged_table(rows, headers=["ID","Make","Model","Year","Mileage","Available","Min Days","Max Days","Daily Rate"], title="All Cars")
        else:
            print(box_text("No cars found."))
        try:
            cid = int(prompt_center("Car ID: ").strip())  # Ask which car by its ID number.
        except ValueError:
            print(box_text("Please enter a number for Car ID."))
            prompt_center("Press Enter…")
            return True
        # Ask new values; if left blank, keep the old value.
        make = prompt_center("New make (blank = keep): ").strip() or None
        model = prompt_center("New model (blank = keep): ").strip() or None
        year_str = prompt_center("New year (blank = keep): ").strip()
        year = int(year_str) if year_str else None
        mileage_str = prompt_center("New mileage (blank = keep): ").strip()
        mileage = int(mileage_str) if mileage_str else None
        daily_rate_str = prompt_center("New daily rate (blank = keep): ").strip()
        daily_rate = float(daily_rate_str) if daily_rate_str else None
        min_str = prompt_center("New min days (blank = keep): ").strip()
        max_str = prompt_center("New max days (blank = keep): ").strip()
        min_days = int(min_str) if min_str else None
        max_days = int(max_str) if max_str else None
        avail_str = prompt_center("Available (y/n, blank = keep): ").strip().lower()
        if avail_str in ("y", "yes"):
            available = True
        elif avail_str in ("n", "no"):
            available = False
        else:
            available = None
        ok = self.inv.update_car(cid, make=make, model=model, year=year, mileage=mileage, daily_rate=daily_rate, min_days=min_days, max_days=max_days, available=available)
        print(box_text("Car updated." if ok else "Car not found or nothing to change."))
        prompt_center("Press Enter…")
        return True
        # Ask new values; if left blank, keep the old value.
        make = prompt_center("New make (blank = keep): ").strip() or None
        model = prompt_center("New model (blank = keep): ").strip() or None
        year_str = prompt_center("New year (blank = keep): ").strip()
        year = int(year_str) if year_str else None
        mileage_str = prompt_center("New mileage (blank = keep): ").strip()
        mileage = int(mileage_str) if mileage_str else None
        daily_rate_str = prompt_center("New daily rate (blank = keep): ").strip()
        daily_rate = float(daily_rate_str) if daily_rate_str else None
        min_str = prompt_center("New min days (blank = keep): ").strip()
        max_str = prompt_center("New max days (blank = keep): ").strip()
        min_days = int(min_str) if min_str else None
        max_days = int(max_str) if max_str else None
        avail_str = prompt_center("Available (y/n, blank = keep): ").strip().lower()
        if avail_str in ("y", "yes"):
            available = True
        elif avail_str in ("n", "no"):
            available = False
        else:
            available = None
        ok = self.inv.update_car(cid, make=make, model=model, year=year, mileage=mileage, daily_rate=daily_rate, min_days=min_days, max_days=max_days, available=available)
        print(box_text("Car updated." if ok else "Car not found or nothing to change."))
        prompt_center("Press Enter…")
        return True




class CreateCarCommand:
    label = "Add Car"
    def __init__(self, inv: InventoryService):
        self.inv = inv

    def _next_id(self) -> int:
        try:
            cars = self.inv.list_cars(only_available=False)
            if not cars:
                return 1
            return max(int(c.get("id", 0)) for c in cars) + 1
        except Exception:
            return 1

    def execute(self) -> bool:
        nxt = self._next_id()
        header = [f"New Car ID (auto): {nxt}", "Fill in the details below:"]
        print(boxed(header, title="Add New Car"))
        make = prompt_center("Make: ").strip()  # Ask the brand name like Toyota
        model = prompt_center("Model: ").strip()  # Ask the model like Corolla
        year = _prompt_int("Year: ", 1980, 2100)  # Only years in a sensible range
        mileage = _prompt_int("Mileage: ", 0)  # Car must have 0 or more kilometers
        daily_rate = _prompt_float("Daily Rate: ", 0)  # Price per day cannot be negative
        min_days = _prompt_int("Min Days: ", 1)  # You must rent at least this many days
        max_days = _prompt_int("Max Days: ", min_days)  # Must be >= Min Days
        ok = self.inv.add_car(make, model, year, mileage, daily_rate, min_days, max_days)  # Save the new car in the database
        if ok:
            try:
                cars_now = self.inv.list_cars(only_available=False)
                actual_id = max(int(c.get("id", 0)) for c in cars_now) if cars_now else nxt
            except Exception:
                actual_id = nxt
            print(box_text(f"Car added successfully with ID {actual_id}."))
        else:
            print(box_text("Could not add car."))
        prompt_center("Press Enter…")
        return True

class UpdateCarCommand:
    label = "Update Car"
    def __init__(self, inv: InventoryService):
        self.inv = inv
    def execute(self) -> bool:
        cars = self.inv.list_cars(only_available=False)
        if not cars:
            print(box_text("No cars to update.")); prompt_center("Press Enter…"); return True
        rows = [[c["id"], c.get("make",""), c.get("model",""), c.get("year",""),
                 c.get("mileage",""), "Yes" if c.get("available", True) else "No",
                 c.get("min_days",1), c.get("max_days",30), f'{c.get("daily_rate",0.0):.2f}'] for c in cars]
        _render_paged_table(rows, headers=["ID","Make","Model","Year","Mileage","Available","Min Days","Max Days","Daily Rate"], title="Cars (Admin)")
        cid_str = prompt_center("Enter car ID to update (blank = cancel): ").strip()  # Which car do you want to change?
        if not cid_str: return True
        try:
            cid = int(cid_str)
        except ValueError:
            print(box_text("Invalid ID.")); prompt_center("Press Enter…"); return True
        car = self.inv.get(cid)
        if not car:
            print(box_text("Car not found.")); prompt_center("Press Enter…"); return True
        make = prompt_center("New make (blank = keep): ").strip() or None
        model = prompt_center("New model (blank = keep): ").strip() or None
        year = None
        ys = prompt_center("New year (blank = keep): ").strip()
        if ys:
            try:
                yval = int(ys)
                if 1980 <= yval <= 2100: year = yval
                else: print(box_text("Year must be between 1980 and 2100. Keeping current."))
            except ValueError:
                print(box_text("Invalid year. Keeping current."))
        mileage = None
        ms = prompt_center("New mileage (blank = keep): ").strip()
        if ms:
            try:
                mval = int(ms)
                if mval >= 0: mileage = mval
                else: print(box_text("Mileage must be >= 0. Keeping current."))
            except ValueError:
                print(box_text("Invalid mileage. Keeping current."))
        daily_rate = None
        rs = prompt_center("New daily rate (blank = keep): ").strip()
        if rs:
            try:
                rval = float(rs)
                if rval >= 0: daily_rate = rval
                else: print(box_text("Daily rate must be >= 0. Keeping current."))
            except ValueError:
                print(box_text("Invalid rate. Keeping current."))
        min_days = None
        mins = prompt_center("New min days (blank = keep): ").strip()
        if mins:
            try:
                minval = int(mins)
                if minval >= 1: min_days = minval
                else: print(box_text("Min days must be >= 1. Keeping current."))
            except ValueError:
                print(box_text("Invalid min days. Keeping current."))
        max_days = None
        maxs = prompt_center("New max days (blank = keep): ").strip()
        if maxs:
            try:
                maxval = int(maxs)
                if maxval >= 1: max_days = maxval
                else: print(box_text("Max days must be >= 1. Keeping current."))
            except ValueError:
                print(box_text("Invalid max days. Keeping current."))
        if min_days is not None and max_days is not None and max_days < min_days:
            print(box_text("Max days cannot be less than Min days. Cancelling update.")); prompt_center("Press Enter…"); return True
        avail_str = prompt_center("Available (y/n, blank = keep): ").strip().lower()
        if avail_str in ("y","yes"): available = True
        elif avail_str in ("n","no"): available = False
        else: available = None
        ok = self.inv.update_car(cid, make=make, model=model, year=year, mileage=mileage, daily_rate=daily_rate, min_days=min_days, max_days=max_days, available=available)
        print(box_text("Car updated." if ok else "Nothing changed or car not found.")); prompt_center("Press Enter…"); return True

class DeleteCarCommand:  # Removes a car.
    label = "Delete Car"  # Menu label.
    def __init__(self, inv: InventoryService):  # Needs inventory to delete.
        self.inv = inv  # Save service.
    def execute(self) -> bool:  # When chosen...
        cars = self.inv.list_cars(only_available=False)
        if cars:
            rows = [[c["id"], c["make"], c["model"], c["year"], c["mileage"], "Yes" if c["available"] else "No", c.get("min_days",1), c.get("max_days",30), f'{c.get("daily_rate",0.0):.2f}'] for c in cars]
            _render_paged_table(rows, headers=["ID","Make","Model","Year","Mileage","Available","Min Days","Max Days","Daily Rate"], title="All Cars")
        else:
            print(box_text("No cars found."))
        try:
            cid = int(prompt_center("Car ID to delete: ").strip())
        except ValueError:
            print(box_text("Please enter a number for Car ID."))
            prompt_center("Press Enter…")
            return True
        car = self.inv.get(cid)
        if not car:
            print(box_text("Car not found."))
            prompt_center("Press Enter…")
            return True
        confirm = prompt_center(f"Delete {car['make']} {car['model']} ({car['year']})? type 'yes' to confirm: ").strip().lower()
        if confirm not in ("y", "yes"):
            print(box_text("Delete cancelled."))
            prompt_center("Press Enter…")
            return True
        ok = self.inv.delete_car(cid)
        print(box_text("Car deleted." if ok else "Car not found."))
        prompt_center("Press Enter…")
        return True

class MakeBookingCommand:  # Lets a customer book a car.
    label = "Make Booking"  # Menu label.
    def __init__(self, rent: RentalService):  # Needs rental service to create bookings.
        self.rent = rent  # Save it.
    def execute(self) -> bool:  # When chosen...
        # Show available cars first so the customer can pick.
        rows, headers = self.rent.available_cars_table()
        if rows:
            _render_paged_table(rows, headers=headers, title="Available Cars")
        else:
            print(box_text("No cars are currently available."))
            prompt_center("Press Enter…")
            return True
        try:
            car_id = int(prompt_center("Car ID: ").strip())
            start = prompt_date("Start date (YYYY-MM-DD): ")
            end = prompt_date("End date (YYYY-MM-DD): ")
        except ValueError:
            print(box_text("Invalid input."))
            prompt_center("Press Enter…")
            return True
        # Quote to show summary.
        try:
            total, details = self.rent.quote(car_id, start, end)
        except Exception as ex:
            print(box_text(f"Cannot quote: {ex}"))
            prompt_center("Press Enter…")
            return True
        # Lookup car for a nicer title
        car = self.rent.cars.get(car_id)
        car_title = f"{car['make']} {car['model']}" if car else f"Car {car_id}"
        weekdays = int(details.get("weekday_days", 0))
        weekends = int(details.get("weekend_days", 0))
        days_total = weekdays + weekends
        daily_rate = details.get("daily_rate", 0.0)
        weekend_mult = details.get("weekend_multiplier", 1.2)
        summary_lines = [
            f"Car ID: {car_id}",
            f"Dates: {start} → {end}",
            f"Total days: {days_total} (weekdays: {weekdays}, weekends: {weekends})",
            f"Daily rate: ${daily_rate:.2f} | Weekend x{weekend_mult}",
            f"Estimated total: ${total:.2f}",
            "",
            "Confirm booking? Type yes or no"
        ]
        print(boxed(summary_lines, title=f"Booking Summary – {car_title}"))
        confirm = prompt_center("yes / no: ").strip().lower()
        if confirm not in ("y", "yes"):
            print(box_text("Booking cancelled."))
            prompt_center("Press Enter…")
            return True
        ok, message = self.rent.make_booking(car_id=car_id, start_date=start, end_date=end)  # Uses current user id set in service
        print(box_text(message))
        prompt_center("Press Enter…")
        return True

class MyBookingsCommand:  # Shows bookings of the current user.
    label = "My Bookings"  # Menu label.
    def __init__(self, rent: RentalService):  # Needs rental service.
        self.rent = rent  # Save it.
    def execute(self) -> bool:  # When chosen...
        rows, headers = self.rent.my_bookings_table()  # Ask the service for rows+headers to print.
        print(boxed([tabulate(rows, headers=headers, tablefmt="github")], title="My Bookings"))  # Show the table.
        prompt_center("Press Enter…")  # Pause.
        return True  # Keep menu.

class ApproveBookingsCommand:  # Admin action to approve or reject.
    label = "Review Bookings"  # Menu label.
    def __init__(self, rent: RentalService):  # Needs rental service.
        self.rent = rent  # Save it.
    def execute(self) -> bool:  # When chosen...
        pend = self.rent.pending_bookings()  # Get all bookings waiting for a decision.
        if not pend:  # If there are none...
            print(box_text("No pending bookings."))  # Say so.
            prompt_center("Press Enter…")  # Pause.
            return True  # Keep menu.
        rows, headers = self.rent.pending_bookings_table()  # Get table data.
        print(boxed([tabulate(rows, headers=headers, tablefmt="github")], title="Pending Bookings"))  # Show table.
        try:  # Parsing numbers might fail.
            bid = int(prompt_center("Booking ID to review: ").strip())  # Which booking?
        except ValueError:  # If not a number...
            print(box_text("Invalid Booking ID."))  # Say what's wrong.
            prompt_center("Press Enter…")  # Pause.
            return True  # Keep menu.
        decision = prompt_center("Approve (a) or Reject (r)? ").strip().lower()  # Ask decision.
        status = "APPROVED" if decision.startswith("a") else "REJECTED"  # Turn letter into the full word.
        self.rent.set_booking_status(bid, status)  # Tell the service to update the booking.
        print(box_text(f"Booking {bid} set to {status}."))  # Confirm.
        prompt_center("Press Enter…")  # Pause.
        return True  # Keep menu.



class ManageAdminsCommand:
    label = "Manage Admin Users"
    def __init__(self, auth: AuthService):
        self.auth = auth

    def _list(self):
        admins = self.auth.list_admins()
        if not admins:
            print(box_text("No admin accounts found."))
            return
        rows = [[a["id"], a["email"], a["name"]] for a in admins]
        print(boxed([tabulate(rows, headers=["ID","Email","Name"], tablefmt="github")], title="Admin Users"))

    def execute(self) -> bool:
        while True:
            lines = [
                "1) List admins",
                "2) Add admin",
                "3) Delete admin",
                "4) Change admin password",
                "5) Change admin email",
                "6) Change admin name",
                "0) Back",
            ]
            print(boxed(lines, title="Manage Admin Users"))
            choice = prompt_center("Select an option: ").strip()
            if choice == "1":
                self._list(); prompt_center("Press Enter…")
            elif choice == "2":
                email = prompt_center("New admin email: ").strip()
                name = prompt_center("Name: ").strip()
                pwd = prompt_center_hidden("Password: ").strip()
                ok = self.auth.add_admin(email, pwd, name)
                print(box_text("Admin added." if ok else "Could not add admin (email may exist)."))
                prompt_center("Press Enter…")
            elif choice == "3":
                self._list()
                key = prompt_center("Delete by (1) ID or (2) Email? ").strip()
                if key == "1":
                    try:
                        uid = int(prompt_center("Admin ID: ").strip())
                        ok = self.auth.delete_admin_by_id(uid)
                    except ValueError:
                        ok = False
                else:
                    email = prompt_center("Admin email: ").strip()
                    ok = self.auth.delete_admin_by_email(email)
                print(box_text("Admin deleted." if ok else "Admin not found.")); prompt_center("Press Enter…")
            elif choice == "4":
                email = prompt_center("Admin email: ").strip()
                pwd = prompt_center_hidden("New password: ").strip()
                ok = self.auth.change_admin_password(email, pwd)
                print(box_text("Password changed." if ok else "Admin not found.")); prompt_center("Press Enter…")
            elif choice == "5":
                old = prompt_center("Current email: ").strip()
                new = prompt_center("New email: ").strip()
                ok = self.auth.change_admin_email(old, new)
                print(box_text("Email changed." if ok else "Admin not found or email taken.")); prompt_center("Press Enter…")
            elif choice == "6":
                email = prompt_center("Admin email: ").strip()
                new = prompt_center("New name: ").strip()
                ok = self.auth.change_admin_name(email, new)
                print(box_text("Name updated." if ok else "Admin not found.")); prompt_center("Press Enter…")
            elif choice == "0":
                return True
            else:
                print(box_text("Invalid option.")); prompt_center("Press Enter…")
