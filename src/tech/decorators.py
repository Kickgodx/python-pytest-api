import uuid
from functools import wraps
from typing import TypeVar, Callable

from requests import Response

from config import HTTP_METHODS
from src.tech.custom_logger import log, CustomLogger

T = TypeVar("T", bound="CustomRequester")


def validate_http_method(func: Callable) -> Callable:
    """Декоратор для валидации HTTP-методов."""

    @wraps(func)
    def wrapper(self: T, http_method: str, *args, **kwargs) -> Response:
        if http_method.upper() not in HTTP_METHODS:
            err_msg = f"Недопустимый HTTP-метод: {http_method}. Допустимые значения: {HTTP_METHODS}"
            log.error(err_msg)
            raise ValueError(err_msg)
        return func(self, http_method, *args, **kwargs)

    return wrapper


def add_allure_attachments(method: Callable) -> Callable:
    """Декоратор для добавления вложений в Allure отчет."""

    @wraps(method)
    def wrapper(self: T, *args, **kwargs) -> Response:
        if kwargs.get('use_allure', True):
            self._add_request_attachments(
                kwargs.get('method', ''),
                f"{self.base_url}{kwargs.get('endpoint', '')}",
                kwargs.get('headers', {}),
                kwargs.get('data', None),
                kwargs.get('params', None)
            )

        response = method(self, *args, **kwargs)

        if kwargs.get('use_allure', True):
            self._add_response_attachments(response)
        return response

    return wrapper


def handle_request_exceptions(logger: CustomLogger):
    """Декоратор для обработки исключений при выполнении запросов."""

    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapper(self: T, *args, **kwargs) -> Response:
            # Получаем параметры запроса из kwargs или args
            method_name = kwargs.get('method', '')
            endpoint = kwargs.get('endpoint', '')
            url = f"{self.base_url}{endpoint}"
            headers = kwargs.get('headers', {})
            data = kwargs.get('data')
            params = kwargs.get('params')
            request_id = headers.get("requestId", str(uuid.uuid4()))

            try:
                return method(self, *args, **kwargs)
            except Exception as e:
                self._add_request_attachments(method_name, url, headers, data, params)

                # Логируем ошибку
                exception_name = e.__class__.__name__
                err_msg = f"исключение при {method_name.upper()} запросе {endpoint}: {e}"
                logger.log_error(
                    request_id,
                    f"{exception_name} {err_msg}",
                    None,
                    data,
                    headers,
                    url,
                    method_name
                )
                raise e.__class__(err_msg) from e

        return wrapper

    return decorator
