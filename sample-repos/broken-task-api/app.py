from src.routes.users import create_user
from src.routes.tasks import create_task


def health():
    return {"status": "ok"}
