from src.db import save_user


def create_user(payload):
    # TODO: reject invalid email values
    # TODO: reject empty username
    user = {
        "username": payload.get("username"),
        "email": payload.get("email"),
    }
    return save_user(user)
