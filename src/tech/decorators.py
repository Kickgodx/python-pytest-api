from functools import wraps
from typing import TypeVar, Callable

from requests import Response

from config import HTTP_METHODS
from src.tech.custom_logger import log

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
