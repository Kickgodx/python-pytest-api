import uuid
from functools import wraps
from typing import Callable, TypeVar

from requests import Response
from requests.exceptions import HTTPError

from config import HTTP_METHODS
from src.utils.allure_utils import add_request_attachments
from src.utils.custom_logger import CustomLogger

T = TypeVar("T", bound="CustomRequester")


def log_response(logger: CustomLogger):
    """Декоратор для логирования ответа HTTP (requests.Response)."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if isinstance(response, Response):
                request_id = kwargs.get("request_id", str(uuid.uuid4()))
                logger.log_response(request_id, response)
            return response

        return wrapper

    return decorator


def log_request(logger: CustomLogger):
    """Декоратор для логирования запроса HTTP (requests)."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self: T, *args, **kwargs):
            request_id = kwargs.get("request_id", str(uuid.uuid4()))
            method = kwargs.get("method", "No HTTP method provided decorated")
            endpoint = kwargs.get("endpoint", "No endpoint provided decorated")
            url = f"{self.base_url}{endpoint}"
            params = kwargs.get("params")

            response = func(self, *args, **kwargs)
            if isinstance(response, Response):
                request = response.request
                logger.log_request(request_id, method, url, headers=request.headers, params=params, data=request.body)
            return response

        return wrapper

    return decorator


def request_exception_handler(logger: CustomLogger):
    """Декоратор для обработки исключений при выполнении HTTP-запросов."""

    def decorator(func: Callable) -> Callable:
        # Если был метод с неименованными аргументами + именованными + навалено в **kwargs, например:
        # return self._send_request("GET", endpoint, use_allure=use_allure, headers=headers, params=params, **kwargs), то
        # в декораторе неименованные вытаскивать по позиции из *args или напрямую указывая в методе распаковывая по позиции
        @wraps(func)
        def wrapper(*args, **kwargs):
            """Обработчик исключений для логирования ошибок при выполнении HTTP-запросов."""

            self = args[0]
            method = args[1] if len(args) > 1 else kwargs.get("method")
            endpoint = args[2] if len(args) > 2 else kwargs.get("endpoint")
            request_id = kwargs.get("request_id", str(uuid.uuid4()))
            url = f"{self.base_url}{endpoint}"
            data = kwargs.get("data")
            headers = kwargs.get("headers", {})
            params = kwargs.get("params")

            try:
                return func(*args, **kwargs)
            except Exception as e:
                if kwargs.get("use_allure", False):
                    add_request_attachments(method, url, headers, data, params)

                exception_name = e.__class__.__name__
                err_msg = f"исключение при {method.upper()} запросе: {e}"
                logger.log_error(request_id, f"{exception_name} {err_msg}", None, data, headers, url, method)
                # Собираем Response.request из существующей информации (метод, URL, заголовки и т.д.)
                res = Response()
                res.request = type("Request", (), {"method": method, "url": url, "headers": headers, "body": data})()
                raise e.__class__(err_msg) from e

        return wrapper

    return decorator


def check_status_code_400_799(logger: CustomLogger):
    """Декоратор для проверки кода состояния ответа HTTP (requests.Response) в диапазоне 400-799."""

    def decorator(func: Callable) -> Callable:

        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            request = response.request

            request_id = kwargs.get("request_id", str(uuid.uuid4()) + "-custom_requester")

            if isinstance(response, Response) and 400 <= response.status_code <= 799:
                try:
                    response.raise_for_status()
                except HTTPError as e:
                    exception_name = e.__class__.__name__
                    response_request_id = request.headers.get("requestId", request_id)
                    logger.log_error(response_request_id, f"{exception_name}: {e}", response, request.body,
                                     request.headers, request.url,
                                     request.method)
            return response

        return wrapper

    return decorator


def validate_http_methods(logger: CustomLogger):
    """Декоратор для валидации HTTP-методов."""

    def decorator(func: Callable) -> Callable:
        """Проверяет, что переданный HTTP-метод является допустимым."""

        @wraps(func)
        def wrapper(self, http_method: str, *args, **kwargs) -> Response:
            if http_method.upper() not in HTTP_METHODS:
                err_msg = f"Недопустимый HTTP-метод: {http_method}. Допустимые значения: {HTTP_METHODS}"
                logger.logger.error(err_msg)
                raise ValueError(err_msg)
            return func(self, http_method, *args, **kwargs)

        return wrapper

    return decorator


def check_status_code(expected=200):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if not isinstance(response, Response):
                raise TypeError(f"Expected a Response object, got {type(response).__name__}")
            assert response.status_code == expected, f"Expected {expected}, got {response.status_code}"
            return response

        return wrapper

    return decorator


def send_request_wrapper(logger: CustomLogger):
    """Декоратор для обёртки метода отправки запросов класса CustomRequester с логированием и обработкой исключений."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        @validate_http_methods(logger)
        @request_exception_handler(logger)
        @log_response(logger)
        @log_request(logger)
        @check_status_code_400_799(logger)
        def wrapper(self: T, *args, **kwargs):
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
