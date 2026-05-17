from src.db import save_task


def create_task(payload):
    title = payload.get("title")
    if not title:
        raise ValueError("title is required")
    return save_task({"title": title, "done": False})
