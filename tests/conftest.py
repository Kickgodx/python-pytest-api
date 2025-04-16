import allure
import pytest

import config as cfg
from src.models.client import Client


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    allure_dir = getattr(config.option, "allure_report_dir", None)
    if not allure_dir: setattr(config.option, "allure_report_dir", cfg.ALLURE_RESULTS_PATH)
    # rootpath = config.rootpath
    setattr(config.option, "attach_capture", False)


@pytest.fixture(scope="session")
def client():
    return Client()


def pytest_runtest_call(item):
    doc = item.function.__doc__
    test_name = item.name.replace("_", " ").title()
    description = f"{doc.strip()}" if doc else test_name
    allure.dynamic.description(description)
