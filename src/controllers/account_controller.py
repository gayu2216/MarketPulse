from typing import Dict
from src.models.accounts import User

# define AccountController class for user authentication and management
class AccountController:

    # initialize new AccountController instance with empty sessions and users dictionaries
    # user dictionaries store user accounts (filled when register() is called with user details)
    # session dictionaries stores usernames that are currently logged in users
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._sessions: Dict[str, User] = {}

    # method to validate username (length must be between 2 and 15 characters, can only contain letters and digits)
    # argument: username to validate
    # returns boolean value depending on given username matching requirements
    def is_username_valid(self, username: str) -> bool:
        if len(username) <= 2 or len(username) >= 15:
            return False
            
        if any(char.isspace() for char in username) or not username.isalnum():
            return False
            
        return True
    
    # method to validate password (length must be between 8 and 25 characters, must contain at least one capital letter and digit, can only contain letters and digits)
    # argument: password to validate
    # returns boolean value depending on given password matching requirements
    def is_password_valid(self, password: str) -> bool:
        if len(password) <= 8 or len(password) >= 25 or not any(ch.isupper() for ch in password) \
            or not any(ch.isdigit() for ch in password) or not password.isalnum():
            return False
        
        return True
    
    # method to register a new user (validate username and password, create new user); will be used in test cases
    # arguments: username and password
    # returns newly created user
    def register(self, username: str, password: str) -> User:
        if not self.is_username_valid(username):
            raise ValueError(
                "Username must be 2-15 characters long and contain only letters and digits"
            )
            
        if not self.is_password_valid(password):
            raise ValueError(
                "Password must be 8-25 characters long, contain at least one capital letter and one digit, and only contain letters and digits"
            )
            
        # create new user and add to users dictionary before returning it
        user = User(username=username, password=password)
        self._users[username] = user
        return user
    
    # method to login a user (validate existence, create session); will be used in test cases
    # arguments: username, password
    # returns session token if login is successful
    def login(self, username: str, password: str) -> bool:
        if username not in self._users:
            raise ValueError("Invalid username or password")
            
        user = self._users[username]
        
        if not user.verify_password(password):
            raise ValueError("Invalid username or password")
            
        # store logged in username into session dictionary and return if login was successful
        self._sessions[username] = user
        return True
            
    # method to logout a user (remove session) through deleting username from session dictionary; will be used in test cases
    # arguments: username
    def logout(self, username: str) -> None:
        if username in self._sessions:
            del self._sessions[username]


    # Optional:         
    # method to check if a user is authenticated (validate session/is username already existing in session dictionary); can be used in test cases
    # returns boolean value if existing
    def is_authenticated(self, username: str) -> bool:
        return username in self._sessions
