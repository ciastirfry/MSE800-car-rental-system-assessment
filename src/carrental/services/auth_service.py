# ==============================================================================
# Authentication/authorization helpers (login, admin tools).
# This file is the 'explained like I am 10' version with simple comments.
# Every step tells you plainly what it does.

# ==============================================================================

"""Authentication service: register, login, and session info."""  # The UI talks to this class instead of touching the database directly.

from __future__ import annotations  # Modern type hints.
from typing import Optional, Dict  # We will return dictionaries of user info.
from carrental.storage.db import Database  # The database connection (Singleton).
from carrental.storage.repositories import UserRepository  # CRUD for users.

class AuthService:  # Handles who is logged in and how to check passwords.
    def __init__(self, db: Database) -> None:  # Build the service.
        self.users = UserRepository(db)  # Keep a user repository handy.
        self._current_user: Optional[Dict] = None  # Store the logged-in user dictionary or None when no one is logged in.
    def register(self, email: str, password: str, name: str, role: str = "customer") -> bool:  # Create a new account.
        return self.users.create(email=email, password=password, name=name, role=role)  # Ask the repo to insert the user.
    def login(self, email: str, password: str) -> bool:  # Try to log in with email+password.
        user = self.users.verify(email=email, password=password)  # Repo returns user dict if the password matches.
        self._current_user = user  # Remember who is logged in (or None if failed).
        return bool(user)  # True if we have a user, False if not.
    def logout(self) -> None:  # Forget the session.
        self._current_user = None  # Nobody is logged in now.
    def current_user(self) -> Optional[Dict]:  # Let other parts see who is logged in.
        return self._current_user  # Could be None.
    def current_user_id(self) -> Optional[int]:  # Convenience: get the id quickly.
        return self._current_user.get("id") if self._current_user else None  # Pull id from the dict safely.
    def current_user_role(self) -> Optional[str]:  # Convenience: get the role quickly.
        return self._current_user.get("role") if self._current_user else None  # Pull role from the dict safely.


    # --- Admin management convenience wrappers ---
    def list_admins(self):
        return self.users.list_admins()

    def add_admin(self, email: str, password: str, name: str) -> bool:
        return self.users.create(email=email, password=password, name=name, role="admin")

    def delete_admin_by_email(self, email: str) -> bool:
        return self.users.delete_by_email(email)

    def delete_admin_by_id(self, user_id: int) -> bool:
        return self.users.delete_by_id(user_id)

    def change_admin_password(self, email: str, new_password: str) -> bool:
        return self.users.set_password(email, new_password)

    def change_admin_email(self, old_email: str, new_email: str) -> bool:
        return self.users.set_email(old_email, new_email)

    def change_admin_name(self, email: str, new_name: str) -> bool:
        return self.users.set_name(email, new_name)
