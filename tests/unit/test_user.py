import pytest
from api.models.users import User

class TestUser:
    def test_new_user(self):
        """
        GIVEN a User model
        WHEN a new User is created
        THEN check the email, hashed_password, and role fields are defined correctly
        """
        user = User(
            username="pedro", password="1234", user_type_id=2
        )
        assert user.username == "pedro"
        assert user.password != "1234"
        assert user.user_type_id == 2
        assert User.verify_hash("1234", user.password)

