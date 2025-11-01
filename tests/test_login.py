import pytest
from src.controllers.account_controller import AccountController

@pytest.fixture
def controller():
    return AccountController()

def test_invalid_username(controller):
    try:
        controller.register("JohnSmith#123", "Password321")
        assert False, "Should raise ValueError for username with special characters"
    except ValueError as e:
        assert "Username must be 2-15 characters long and contain only letters and digits" in str(e), "Unexpected error message"
        
def test_exceptional_username(controller):
    try:
        controller.register("John Smith 123", "Password321")
        assert False, "Should raise ValueError for username with spaces"
    except ValueError as e:
        assert "Username must be 2-15 characters long and contain only letters and digits" in str(e), "Unexpected error message"
   
def test_invalid_password(controller):
    try:
        controller.register("JohnSmith123", "Password#321")
        assert False, "Should raise ValueError for password with special characters"
    except ValueError as e:
        assert "Password must be 8-25 characters long, contain at least one capital letter and one digit, and only contain letters and digits" in str(e), "Unexpected error message"

def test_exceptional_password(controller):
    try:
        controller.register("JohnSmith123", "Password 321")
        assert False, "Should raise ValueError for password with spaces"
    except ValueError as e:
        assert "Password must be 8-25 characters long, contain at least one capital letter and one digit, and only contain letters and digits" in str(e), "Unexpected error message"

def test_successful_registration_and_login(controller):
    user = controller.register("JohnSmith123", "Password321")
    assert user.username == "JohnSmith123"
    
    # test successful login
    result = controller.login("JohnSmith123", "Password321")
    assert result is True
    assert controller.is_authenticated("JohnSmith123") is True
    
    # test successful logout
    controller.logout("JohnSmith123")
    assert controller.is_authenticated("JohnSmith123") is False
