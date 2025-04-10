import logging
import os

# region logging
FILE_LOG_LEVEL = logging.ERROR
LOG_FORMAT = "%(asctime)s[%(levelname)s] - %(message)s"
LOG_FILE_NAME = "log.log"
# endregion

# region paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

LOGS_PATH = os.path.join(ROOT_DIR, 'logs')
ALLURE_RESULTS_PATH = os.path.join(ROOT_DIR, 'allure-results')
# endregion

# region hosts
BASE_URL = "https://petstore.swagger.io/v2"
# endregion
