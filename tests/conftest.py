import pytest
from prometheus_client import Counter, start_http_server

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


# Метрики
TEST_COUNTER = Counter('pytest_test_calls_total', 'Number of test calls', ['outcome', 'name'])

# Запуск HTTP-сервера с метриками
@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    print("🚀 Starting Prometheus metrics server on port 0.0.0.0:8000")
    start_http_server(8000, addr="0.0.0.0")

# Хук на каждый тест — считаем успешные, упавшие и т.п.
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()
    if result.when == "call":
        TEST_COUNTER.labels(outcome=result.outcome, name=item.name).inc()


def pytest_sessionfinish(session, exitstatus):
    import time
    time.sleep(20)  # Ждём 10 секунд перед выходом