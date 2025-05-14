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


class CustomLogger:
    """Класс для логирования HTTP-запросов и ответов с поддержкой многопроцессорности."""

    def __init__(self):
        self._initialize_logger()
        atexit.register(self.shutdown)

    def _initialize_logger(self) -> None:
        """Инициализирует логгер с настройками из конфига."""
        os.makedirs(cfg.LOGS_PATH, exist_ok=True)

        # Очищаем или создаем файл лога
        log_file = os.path.join(cfg.LOGS_PATH, cfg.LOG_FILE_NAME)
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("")

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(cfg.FILE_LOG_LEVEL)

        worker_id = os.environ.get("PYTEST_XDIST_WORKER", "master")
        formatter = UtcFormatter(
            f"[{worker_id.replace('gw', 'worker_')}]" + cfg.LOG_FORMAT,
            datefmt="[%H:%M:%S]",
            tz_hours_gap=3
        )

        self.file_log_handler = FileHandler(str(log_file), "a", encoding="utf-8")
        self.file_log_handler.setLevel(cfg.FILE_LOG_LEVEL)
        self.file_log_handler.setFormatter(formatter)

        self.queue = multiprocessing.Queue(-1)
        self.queue_handler = QueueHandler(self.queue)
        self.logger.addHandler(self.queue_handler)

        self.queue_listener = QueueListener(self.queue, self.file_log_handler)
        self.queue_listener.start()

    def shutdown(self) -> None:
        """Корректно завершает работу логгера."""
        self.queue_listener.stop()
        self.logger.removeHandler(self.queue_handler)
        self.queue.close()
        self.queue.join_thread()
        self.file_log_handler.close()

    @staticmethod
    def get_caller_info() -> tuple[str, int, str]:
        """Возвращает информацию о вызывающем коде."""
        for frame in inspect.stack():
            module = inspect.getmodule(frame[0])
            filename = module.__file__ if module else "Unknown"
            if filename != __file__:
                return filename, frame.lineno, frame.function
        return "Unknown", 0, "Unknown"

    @staticmethod
    def _mask_bearer_tokens(headers: dict[str, object]) -> dict[str, object]:
        """Маскирует Bearer-токены в заголовках."""
        masked_headers = headers.copy()
        for key, value in headers.items():
            if isinstance(value, str) and "Bearer " in value:
                parts = value.split("Bearer ")
                if len(parts) > 1:
                    masked_headers[key] = f"{parts[0]}Bearer *****"
        return masked_headers

    def log_request(self, request_id: str, method: str, url: str, **kwargs) -> None:
        """Логирует информацию о запросе."""
        self.logger.info(f"[{request_id}] - Request URL: {method} {url}")

        if "headers" in kwargs:
            headers_to_log = self._mask_bearer_tokens(kwargs["headers"])
            self.logger.info(f"[{request_id}] - Headers: {headers_to_log}")
        if "params" in kwargs:
            self.logger.info(f"[{request_id}] - Params: {kwargs['params']}")
        if "json" in kwargs:
            self.logger.info(f"[{request_id}] - Payload (json): {kwargs['json']}")
        if "data" in kwargs:
            self.logger.info(f"[{request_id}] - Payload (data): {kwargs['data']}")

    def log_response(self, request_id: str, response: Response) -> None:
        """Логирует информацию об ответе."""
        self.logger.info(f"[{request_id}] - Response: {response.status_code} {response.url}")
        self.logger.info(f"[{request_id}] - Response headers: {response.headers}")
        if response.text:
            try:
                json_data = response.json()
                self.logger.info(f"[{request_id}] - Response body: {json_data}\n")
            except ValueError:
                self.logger.info(f"[{request_id}] - Response body: {response.text}\n")
        else:
            self.logger.info(f"[{request_id}] - Response body: None")

    def log_error(self, request_id: str, err, response: Response | None, data, headers: dict, url: str, method: str, **kwargs) -> None:
        """Метод для логирования информации об ошибке
        :param request_id: уникальный идентификатор запроса
        :param err: объект ошибки (HTTPError или RequestException)
        :param response: объект ответа на запрос (requests.Response)
        :param data: данные запроса
        :param headers: заголовки запроса (dict)
        :param url: URL-адрес запроса
        :param method: HTTP-метод
        :return: None
        """
        test_name = os.environ.get("PYTEST_CURRENT_TEST", "Unknown test")
        log_lines = [f"Test: {test_name.replace("(call)", "")}"]

        # log_lines.append(f"[{request_id}] - Error in: {filename}:{lineno} - {funcname}")
        log_lines.append(f"[{request_id}] - {err}")
        log_lines.append(f"[{request_id}] - Request URL: {method} {url}")

        headers_to_log = self._mask_bearer_tokens(headers)
        log_lines.append(f"[{request_id}] - Request headers: {headers_to_log}")
        if "params" in kwargs:
            log_lines.append(f"[{request_id}] - Request params: {kwargs['params']}")
        log_lines.append(f"[{request_id}] - Request body: {data}")

        if response is not None:
            log_lines.append(f"[{request_id}] - Response headers: {response.headers}")
            log_lines.append(f"[{request_id}] - Response body: {response.text}\n")
        else:
            log_lines.append(f"[{request_id}] - Response body: None\n")

        # Объединяем все строки с переносами
        self.logger.error("\n".join(log_lines))


# Инициализация глобального экземпляра логгера
logger = CustomLogger()
