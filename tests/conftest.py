
import allure
import pytest

import config as cfg

pytest_plugins = [
    "tests.fixtures.clients",
    "tests.fixtures.helpers",
    "tests.fixtures.envs"
]


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    allure_dir = getattr(config.option, "allure_report_dir", None)
    if not allure_dir:
        config.option.allure_report_dir = cfg.ALLURE_RESULTS_PATH
    # rootpath = config.rootpath
    config.option.attach_capture = False


def pytest_runtest_call(item):
    """
    Добавляет описание теста в Allure на основе его документации или имени.
    """
    doc = item.function.__doc__
    test_name = item.name.replace("_", " ").title()
    description = f"{doc.strip()}" if doc else test_name
    allure.dynamic.description(description)
