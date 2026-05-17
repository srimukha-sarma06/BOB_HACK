import pytest
from src.routes.tasks import create_task


def test_create_task():
    task = create_task({"title": "ship demo"})
    assert task["done"] is False


def test_create_task_rejects_empty_title():
    with pytest.raises(ValueError):
        create_task({})
