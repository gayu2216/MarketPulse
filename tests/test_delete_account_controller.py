import pytest
from src.controllers.account_controller import AccountController
from src.models.accounts import User

# test-case area; run register/login/logout tests

class TestAccountController:
    
    @pytest.fixture
    def controller(self):
        return AccountController()

    # example test (delete later)
    @pytest.fixture
    def test_account(self):
        return User(
            username="testuser",
            password="testPass123"
        )   

    def test_register_and_login_user(self, controller, test_account):
        user = controller.register(username=test_account.username, password=test_account.password)
        
        assert user is not None
        
        validation_success = controller.login(username=test_account.username, password=test_account.password)
        
        assert validation_success is True

        authenticated_user = controller.is_authenticated(username=test_account.username)
        assert authenticated_user is True