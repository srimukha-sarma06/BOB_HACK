import re
from src.db import save_user


def create_user(payload):
    username = payload.get("username")
    email = payload.get("email")
    
    # Validate username
    if not username:
        raise ValueError("Username is required")
    
    # Validate email format
    if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        raise ValueError("Invalid email address")
    
    user = {
        "username": username,
        "email": email,
    }
    return save_user(user)
