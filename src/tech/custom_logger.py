import atexit
import inspect
import logging
import multiprocessing
import os
from logging import FileHandler
from logging.handlers import QueueHandler, QueueListener

from requests import Response

import config as cfg
from src.tech.utc_log_formatter import UtcFormatter

os.makedirs(cfg.LOGS_PATH, exist_ok=True)

# Создаем файл лога, если он не существует или очищаем его, если он существует
log_file = os.path.join(cfg.LOGS_PATH, cfg.LOG_FILE_NAME)
with open(log_file, "w", encoding="utf-8") as f:
    f.write("")

logger = logging.getLogger(__name__)
logger.setLevel(cfg.FILE_LOG_LEVEL)

worker_id = os.environ.get("PYTEST_XDIST_WORKER", default="master")
formatter = UtcFormatter(f"[{worker_id.replace('gw', 'worker_')}]" + cfg.LOG_FORMAT, datefmt="[%H:%M:%S]", tz_hours_gap=3)

file_log_handler = FileHandler(str(log_file), "a", encoding="utf-8")
file_log_handler.setLevel(cfg.FILE_LOG_LEVEL)
file_log_handler.setFormatter(formatter)

queue = multiprocessing.Queue(-1)
queue_handler = QueueHandler(queue)
logger.addHandler(queue_handler)

# QueueListener с нормальным Handler, а не функцией
queue_listener = QueueListener(queue, file_log_handler)
queue_listener.start()


def shutdown_logger():
    queue_listener.stop()
    logger.removeHandler(queue_handler)
    queue.close()
    queue.join_thread()
    file_log_handler.close()


def log_request(request_id: str, method: str, url: str, **kwargs) -> None:
    """Метод для логирования информации о запросе
    :param request_id: уникальный идентификатор запроса
    :param method: HTTP-метод
    :param url: URL-адрес запроса
    :param kwargs: дополнительные параметры запроса
    :return: None
    """
    filename, lineno, funcname = get_caller_info()
    logger.info(f"RequestID: [{request_id}] - Request: {method} {url} - {filename}:{lineno} - {funcname}")
    if "headers" in kwargs:
        headers_to_log = mask_bearer_tokens(kwargs["headers"])
        logger.info(f"RequestID: [{request_id}] - Headers: {headers_to_log}")
    if "params" in kwargs:
        logger.info(f"RequestID: [{request_id}] - Params: {kwargs['params']}")
    if "json" in kwargs:
        logger.info(f"RequestID: [{request_id}] - Payload (json): {kwargs['json']}")
    if "data" in kwargs:
        logger.info(f"RequestID: [{request_id}] - Payload (data): {kwargs['data']}")


def log_response(request_id: str, response: Response) -> None:
    """Метод для логирования информации об ответе
    :param request_id: уникальный идентификатор запроса
    :param response: объект ответа на запрос (requests.Response)
    :return: None
    """
    logger.info(f"[{request_id}] - Response: {response.status_code} {response.url}")
    logger.info(f"[{request_id}] - Response headers: {response.headers}")
    logger.info(f"[{request_id}] - Response body: {response.text}\n")


def log_error(
    request_id: str, err, response: Response | None, data, headers: dict, url: str, method: str, filename, lineno, funcname
) -> None:
    """Метод для логирования информации об ошибке
    :param request_id: уникальный идентификатор запроса
    :param err: объект ошибки (HTTPError или RequestException)
    :param response: объект ответа на запрос (requests.Response)
    :param data: данные запроса
    :param headers: заголовки запроса (dict)
    :param url: URL-адрес запроса
    :param method: HTTP-метод
    :param filename: имя файла, из которого был вызван запрос
    :param lineno: номер строки, из которой был вызван запрос
    :param funcname: имя функции, из которой был вызван запрос
    :return: None
    """
    if filename is None or lineno is None or funcname is None:
        filename, lineno, funcname = get_caller_info()

    test_name = os.environ.get("PYTEST_CURRENT_TEST", "Unknown test")

    log_lines = []

    if test_name != "Unknown test":
        log_lines.append(f"Test: {test_name}")
    else:
        log_lines.append("Unknown test")

    log_lines.append(f"[{request_id}] - Error in: {filename}:{lineno} - {funcname}")
    log_lines.append(f"[{request_id}] - {err}")
    log_lines.append(f"[{request_id}] - Request URL: {method} {url}")

    headers_to_log = mask_bearer_tokens(headers)
    log_lines.append(f"[{request_id}] - Request headers: {headers_to_log}")
    log_lines.append(f"[{request_id}] - Request body: {data}")

    if response is not None:
        log_lines.append(f"[{request_id}] - Response headers: {response.headers}")
        log_lines.append(f"[{request_id}] - Response body: {response.text}\n")
    else:
        log_lines.append(f"[{request_id}] - Response body: None\n")

    # Объединяем все строки с переносами
    logger.error("\n".join(log_lines))


def log_info(message: str) -> None:
    """Метод для логирования информации
    :param message: сообщение для логирования
    :return: None
    """
    logger.info(f"{message}")


def get_caller_info() -> tuple[str, int, str]:
    for frame in inspect.stack():
        module = inspect.getmodule(frame[0])
        filename = module.__file__ if module else "Unknown"
        if filename != __file__:
            lineno = frame.lineno
            funcname = frame.function
            return filename, lineno, funcname
    return "Unknown", 0, "Unknown"


def mask_bearer_tokens(headers: dict) -> dict:
    """Маскирует Bearer-токены во всех значениях словаря headers.
    Возвращает новый словарь с замаскированными данными.
    """
    masked_headers = {}
    for key, value in headers.items():
        if isinstance(value, str) and "Bearer " in value:
            # Разделяем строку по Bearer и маскируем токен
            parts = value.split("Bearer ")
            if len(parts) > 1:
                # Оставляем 'Bearer ', но заменяем сам токен на '*****'
                masked_value = f"{parts[0]}Bearer *****"
                masked_headers[key] = masked_value
            else:
                masked_headers[key] = value
        else:
            masked_headers[key] = value
    return {**headers, **masked_headers}


atexit.register(shutdown_logger)
