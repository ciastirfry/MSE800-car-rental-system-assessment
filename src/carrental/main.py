# ==============================================================================
# Top‑level menus and wiring for the console app.
# This file is the 'explained like I am 10' version with simple comments.
# Every step tells you plainly what it does.

# ==============================================================================

"""Command-Line Interface (CLI) for the Car Rental System."""  # This file wires together menus and services so a user can use the app.

from __future__ import annotations  # Allows modern type hint syntax on Python 3.10.
import getpass  # Lets us type passwords without showing them on screen.
from typing import Dict  # "Dict" is a type so we can describe menu shapes like Dict[str, Command].

# We import helpful functions to draw and prompt in the terminal.
from carrental.utils.ui import clear, boxed, box_text, prompt_center, title_box, prompt_center_hidden  # Pretty printing helpers.
# We import the "Command" interface and several concrete commands that do things.
from carrental.cli.commands import (  # Menu command objects live here.
    Command,  # The common shape that all commands follow.
    LogoutCommand,  # Lets a user leave a menu.
    ExitAppCommand,  # Lets a user close the whole program.
    ShowCarsCommand,  # Shows a list of cars.
    AddCarCommand, UpdateCarCommand, DeleteCarCommand,  # Admin actions for car records.
    MakeBookingCommand, MyBookingsCommand, ApproveBookingsCommand  # Booking things.
, CreateCarCommand)
# Import services that hold the brains/data of the app.
from carrental.services.auth_service import AuthService
from carrental.storage.db import Database  # Handles login and who you are.
from carrental.services.inventory_service import InventoryService  # Handles the cars we can rent.
from carrental.services.rental_service import RentalService  # Handles bookings and prices.

def run_menu(title: str, menu: Dict[str, Command], prompt_text: str = "Select an option") -> bool:  # Shows a menu and runs the chosen action.
    clear()  # Clean the screen so the menu looks fresh.
    print(title_box("Fred's Car Rental"))  # Always show the big app title at the very top.
    lines = [f"{k}) {menu[k].label}" for k in sorted(menu.keys(), key=int)]  # Build one text line for each menu item like '1) Show cars'.
    print(boxed(lines, title=title))  # Draw a neat box around the menu with the menu title on top.
    choice = prompt_center(prompt_text).strip()  # Ask the user what they want to do and trim extra spaces.
    action = menu.get(choice)  # Try to find a command object that matches the number/letter they typed.
    if not action:  # If the choice wasn't in the menu...
        print(box_text("That is not on the menu. Try again."))  # Tell them nicely in a box.
        input("Press Enter...")  # Wait so they can read the message.
        return True  # Return True to keep the menu loop going.
    return action.execute()  # If we have a valid command, do it and return its True/False (keep/leave).

def main() -> None:  # This starts the whole application.
    # Create the services that hold our data and logic.
    db = Database.instance()  # Get (or create) database
    auth = AuthService(db)
    inventory = InventoryService(db)
    rent = RentalService(db)
  # Booking logic that also talks to cars.

    # Build the top-level (home) menu that appears first.
    menu: Dict[str, Command] = {  # A dictionary maps input keys (like "1") to command objects.
        "1": ExitAppCommand(),  # Option 1 closes the entire app (a safety exit).
    }  # You can add more home actions here later if needed.

    # Build the login screen menu options (not using the command pattern for simplicity here).
    while True:  # This loop keeps showing the Home/Login screen until the user exits.
        clear()  # Clean the screen.
        print(title_box("Fred's Car Rental"))  # Always show the app title on top.
        # Show a simple login/register menu.
        lines = ["1) Login", "2) Register", "0) Exit"]  # The three choices we offer at the start.
        print(boxed(lines, title="Home"))  # Draw the home menu in a box.
        sel = prompt_center("Select an option").strip()  # Ask the user what to do.
        if sel == "1":  # If they picked Login...
            email = prompt_center("Email: ").strip()
            while not email:
                email = prompt_center("Email (cannot be blank): ").strip()
            pwd = prompt_center_hidden("Password: ").strip()
            while not pwd:
                pwd = prompt_center_hidden("Password (cannot be blank): ").strip()
            if not auth.login(email=email, password=pwd):  # Try to log in; if it fails...
                print(box_text("Login failed. Please try again."))  # Say it didn't work.
                input("Press Enter...")  # Pause so they can read the message.
                continue  # Go back to the start of the loop to try again.
            # If login worked, choose which role menu to show.
            role = auth.current_user_role()
            rent.set_current_user_id(auth.current_user_id())  # tell rental who is logged in  # Find out if user is 'admin' or 'customer'.
            # Build role-specific menus.
            if role == "admin":  # For admins we give car management and approvals.
                from carrental.cli.commands import AddCarCommand as _ACC, UpdateCarCommand as _UCC
                _ACC.label = "Add Car"
                _UCC.label = "Update Car"
                menu: Dict[str, Command] = {
                    "1": ShowCarsCommand(inventory, only_available=False),  # Let admin view all cars.
                    "2": CreateCarCommand(inventory),  # Add a new car to stock.
                    "3": UpdateCarCommand(inventory),  # Edit a car's details.
                    "4": DeleteCarCommand(inventory),  # Remove a car from stock.
                    "5": ApproveBookingsCommand(rent),  # Approve or reject booking requests.
                    "0": LogoutCommand(),  # Leave admin area and go back to login screen.
                }  # End of admin menu.
                # Keep showing the admin menu until the user logs out.
                keep = True  # Start by staying in the admin menu.
                while keep:  # While the admin still wants to be here...
                    keep = run_menu("Admin Menu", menu)  # Show the menu and run selected command.
            else:  # Otherwise the user is a customer.
                menu = {
                    "1": ShowCarsCommand(inventory, only_available=False),  # Let customer browse cars they can rent.
                    "2": MakeBookingCommand(rent),  # Create a booking for selected dates.
                    "3": MyBookingsCommand(rent),  # See their own bookings.
                    "0": LogoutCommand(),  # Leave customer area and go back to login screen.
                }  # End of customer menu.
                keep = True  # Start by staying in customer menu.
                while keep:  # Keep looping until they choose Logout.
                    keep = run_menu("Customer Menu", menu)  # Show the menu and handle the choice.
            # When we get here the user chose Logout; end the session.
            auth.logout()  # Forget who is logged in.
            rent.set_current_user_id(None)  # clear
            print(box_text("You have been logged out."))  # Tell them what happened.
            input("Press Enter...")  # Pause so they can read the message.
        elif sel == "2":  # If they picked Register...
            name = prompt_center("Name: ").strip()
            while not name:
                name = prompt_center("Name (cannot be blank): ").strip()
            email = prompt_center("Email: ").strip()
            while not email:
                email = prompt_center("Email (cannot be blank): ").strip()
            pwd = prompt_center_hidden("Password: ").strip()
            while not pwd:
                pwd = prompt_center_hidden("Password (cannot be blank): ").strip()  # Ask for a password (not shown).
            ok = auth.register(email=email, password=pwd, name=name, role="customer")  # Try to create the account.
            msg = "Registration successful." if ok else "Registration failed (email already exists)."  # Pick a friendly message.
            print(box_text(msg))  # Show the message in a box.
            input("Press Enter...")  # Pause so they can read.
        elif sel == "0":  # If they picked Exit...
            print(box_text("Goodbye!"))  # Say goodbye in a nice box.
            break  # Leave the while loop to end the program.
        else:  # If they typed something we don't understand...
            print(box_text("Invalid choice. Please pick 1, 2, or 0."))  # Tell them the valid options.
            input("Press Enter...")  # Pause so they can try again.
