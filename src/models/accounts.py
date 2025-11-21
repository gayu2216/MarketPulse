from typing import Optional, Dict

class User:
    def __init__(
        self,
        username: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone

    @classmethod
    def create(cls, username: str, raw_password: str, **profile) -> "User":
        return cls(username=username, password=raw_password, **profile)

    def verify_password(self, raw_password: str) -> bool:
        return self.password == raw_password

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "username": self.username,
            "password": self.password,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Optional[str]]) -> "User":
        return cls(
            username=data.get("username"),
            password=data.get("password"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            phone=data.get("phone"),
        )

    def __str__(self) -> str:
        return f"User(username='{self.username}')"