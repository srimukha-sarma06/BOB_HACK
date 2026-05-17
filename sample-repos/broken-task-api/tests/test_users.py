from src.routes.users import create_user


def test_create_user():
    user = create_user({"username": "mayuur", "email": "mayuur@example.com"})
    assert user["username"] == "mayuur"
