# Risky file: pretend this is core database logic.
USERS = []
TASKS = []


def save_user(user):
    USERS.append(user)
    return user


def save_task(task):
    TASKS.append(task)
    return task
