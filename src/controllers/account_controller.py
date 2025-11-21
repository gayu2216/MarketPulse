import json
import os
from typing import Dict, Optional
from pathlib import Path

from src.models.accounts import User

class AccountController:

    def __init__(self, storage_path: Optional[str] = None):
        self._sessions: Dict[str, User] = {}
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            self.storage_path = Path(os.getcwd()) / "src" / "data" / "users.json"

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._users: Dict[str, User] = {}
        self._load_users()

    def _load_users(self) -> None:
        if not self.storage_path.exists():
            admin = User.create("admin", "Admin123")
            self._users = {"admin": admin}
            self._save_users()
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            for username, data in raw.items():
                self._users[username] = User.from_dict(data)
        except Exception:
            self._users = {}

    def _save_users(self) -> None:
        serial = {u: self._users[u].to_dict() for u in self._users}
        with open(self.storage_path, "w", encoding="utf-8") as fh:
            json.dump(serial, fh, indent=2)

    def is_username_valid(self, username: str) -> bool:
        if not username:
            return False
        if len(username) <= 2 or len(username) >= 15:
            return False
        if any(char.isspace() for char in username) or not username.isalnum():
            return False
        return True

    def is_password_valid(self, password: str) -> bool:
        if not password:
            return False
        if len(password) <= 8 or len(password) >= 25:
            return False
        if not any(ch.isupper() for ch in password):
            return False
        if not any(ch.isdigit() for ch in password):
            return False
        if not password.isalnum():
            return False
        return True

    def register(
        self,
        username: str,
        password: str,
        confirm_password: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> User:
        # validate username and password
        if not self.is_username_valid(username):
            raise ValueError(
                "Username must be 2-15 characters long and contain only letters and digits"
            )

        if username in self._users:
            raise ValueError("Username already exists")

        if not self.is_password_valid(password):
            raise ValueError(
                "Password must be 8-25 characters long, contain at least one capital letter and one digit, and only contain letters and digits"
            )

        if confirm_password is not None and password != confirm_password:
            raise ValueError("Password and confirm password do not match")

        user = User.create(
            username,
            password,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
        )

        self._users[username] = user
        self._save_users()
        return user
    
    def delete_user(self, username: str) -> None:
        if username not in self._users:
            raise ValueError("User not found")

        del self._users[username]
        if username in self._sessions:
            del self._sessions[username]
        self._save_users()


    def login(self, username: str, password: str) -> bool:
        if username not in self._users:
            raise ValueError("Invalid username or password")
        user = self._users[username]
        if not user.verify_password(password):
            raise ValueError("Invalid username or password")
        self._sessions[username] = user
        return True

    def logout(self, username: str) -> None:
        if username in self._sessions:
            del self._sessions[username]

    def is_authenticated(self, username: str) -> bool:
        return username in self._sessions

    def get_user(self, username: str) -> Optional[User]:
        return self._users.get(username)

    def update_user(
        self,
        username: str,
        *,
        new_username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        password: Optional[str] = None,
    ) -> User:
        if username not in self._users:
            raise ValueError("User not found")

        user = self._users[username]

        target_username = (new_username or username).strip() or username
        if target_username != username:
            if not self.is_username_valid(target_username):
                raise ValueError(
                    "Username must be 2-15 characters long and contain only letters and digits"
                )
            if target_username in self._users:
                raise ValueError("Username already exists")

        if password:
            if not self.is_password_valid(password):
                raise ValueError(
                    "Password must be 8-25 characters long, contain at least one capital letter and one digit, and only contain letters and digits"
                )
            user.password = password

        user.first_name = first_name or None
        user.last_name = last_name or None
        user.email = email or None
        user.phone = phone or None

        if target_username != username:
            user.username = target_username
            self._users[target_username] = user
            del self._users[username]
            if username in self._sessions:
                self._sessions[target_username] = self._sessions.pop(username)

        self._save_users()
        return user
