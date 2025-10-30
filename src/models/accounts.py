# defining User class for the user account
class User:
    # initialize new User instance with username and password (all strings)
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
    
    # defines string representation of User object
    # returns string with user's username and password
    # can call if needing to print User objects
    def __str__(self) -> str:
        return f"User(username='{self.username}', password='{self.password}')"
    
    # method to verify if the given password matches the user's password
    # argument: password to verify
    # returns boolean value depending on given password matching the user's password
    def verify_password(self, password: str) -> bool:
        return self.password == password