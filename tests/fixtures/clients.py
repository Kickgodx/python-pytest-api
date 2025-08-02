import os

import pytest

from src.models.client import Client


@pytest.fixture(scope="session")
def admin():
    return Client()


@pytest.fixture(autouse=True, scope="session")
def schema_name(worker_id) -> str:
    """Возвращает уникальное имя схемы для каждого процесса pytest."""
    schema_name = "public" if worker_id == "master" else f"test_schema_{worker_id}"
    os.environ["SCHEMA_NAME"] = schema_name
    return schema_name
