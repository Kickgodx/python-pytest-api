import os

import allure
import pytest


@pytest.fixture(autouse=True, scope="session")
def worker_check(worker_id):
    """
    Устанавливает имя воркера в окружение для использования в логах и тестах.
    """
    with allure.step(f"Worker ID: {worker_id}"):
        allure.dynamic.title(f"Worker ID: {worker_id}")
    os.environ["WORKER_NAME"] = worker_id
    return worker_id
