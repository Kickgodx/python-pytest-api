import pytest

import config as cfg


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
	allure_dir = getattr(config.option, "allure_report_dir", None)
	if not allure_dir: setattr(config.option, "allure_report_dir", cfg.ALLURE_RESULTS_PATH)
	# rootpath = config.rootpath
	setattr(config.option, "attach_capture", False)
