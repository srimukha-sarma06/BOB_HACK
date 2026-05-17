import pytest
from src.routes.users import create_user


def test_create_user():
    user = create_user({"username": "mayuur", "email": "mayuur@example.com"})
    assert user["username"] == "mayuur"
    assert user["email"] == "mayuur@example.com"


def test_create_user_rejects_invalid_email():
    with pytest.raises(ValueError, match="Invalid email address"):
        create_user({"username": "mayuur", "email": "not-an-email"})


def test_create_user_rejects_missing_email():
    with pytest.raises(ValueError, match="Invalid email address"):
        create_user({"username": "mayuur"})


def test_create_user_rejects_empty_email():
    with pytest.raises(ValueError, match="Invalid email address"):
        create_user({"username": "mayuur", "email": ""})


def test_create_user_rejects_empty_username():
    with pytest.raises(ValueError, match="Username is required"):
        create_user({"username": "", "email": "mayuur@example.com"})


def test_create_user_rejects_missing_username():
    with pytest.raises(ValueError, match="Username is required"):
        create_user({"email": "mayuur@example.com"})
