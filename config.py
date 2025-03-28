import logging
import os

BASE_URL = "https://petstore.swagger.io/v2"

# region logging
FILE_LOG_LEVEL = logging.ERROR
LOG_FORMAT = "%(asctime)s.%(msecs)03d [%(levelname)s] - %(message)s"
LOG_FILE_NAME = "log.log"
# endregion

# region paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

LOGS_PATH = os.path.join(ROOT_DIR, 'logs')
ALLURE_RESULTS_PATH = os.path.join(ROOT_DIR, 'allure-results')
