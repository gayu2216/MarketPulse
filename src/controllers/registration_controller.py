from dataclasses import dataclass

@dataclass
class RegistrationData:
    first_name: str
    last_name: str
    phone: str | None
    username: str
    email: str
    password: str
    confirm_password: str

class RegistrationController:
    def __init__(self, account_ctrl):
        self.account_ctrl = account_ctrl

    def register(self, data: RegistrationData):
        if data.password != data.confirm_password:
            raise ValueError("Passwords do not match")

        user = self.account_ctrl.register(
            username=data.username,
            password=data.password,
            confirm_password=data.confirm_password,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
        )
        return user