import logging
from http import HTTPMethod
from pathlib import Path

# region logging
FILE_LOG_LEVEL = logging.ERROR
LOG_FORMAT = "%(asctime)s[%(levelname)s] - %(message)s"
LOG_FILE_NAME = "log.log"
# endregion

# region http
DEFAULT_TIMEOUT = 30.0
MIN_CLIENT_ERROR_CODE = 400  # 4xx errors start at 400
MAX_SERVER_ERROR_CODE = 799  # 5xx errors end at 799
HTTP_METHODS = list(HTTPMethod)  # ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD']
# endregion

# region paths
ROOT_DIR = Path(__file__).resolve().parent

LOGS_PATH = ROOT_DIR / "logs"
ALLURE_RESULTS_PATH = ROOT_DIR / "allure-results"
# endregion

# region hosts
BASE_URL = "https://petstore.swagger.io/v2"
# endregion
