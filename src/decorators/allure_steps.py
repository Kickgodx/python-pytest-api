import inspect
from functools import wraps
from typing import Callable

import allure
from requests import Response

from src.utils.allure_utils import add_request_attachments, add_response_attachments


def step_assert(step_text: str = ""):
    """
    Декоратор, оборачивающий функцию проверки в Allure step.
    Можно использовать {param} в тексте — они будут подставлены автоматически.
    Пример: @step_assert("Проверка: {param1}, {param2}")
    @step_assert("Проверка ключа '{key}' в словаре")
    def check_key_in_dict(data: dict, key: str):
    assert key in data, f"Ключ '{key}' не найден в {data}"
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Автоматически определяем аргументы по именам
            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            format_args = {k: repr(v) for k, v in bound_args.arguments.items()}

            step_name = (
                step_text.format(**format_args) if step_text else f"Проверка: {func.__name__}()"
            )

            with allure.step(step_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def step_wrapper(step_text: str = "") -> Callable:
    """
    Обёртка вокруг функции с Allure step.
    Управляется параметром `with_step=True` при вызове.

    :param step_text: Название шага. Можно использовать format-переменные.
    Примеры:

    @step_wrapper("Сравнение значения: {actual} == {expected}")
    def check_equal(actual, expected, note=""):
        assert actual == expected, f"{note}: {actual} != {expected}"

    def test_with_and_without_allure():
        # с шагом Allure (по умолчанию)
        check_equal(10, 10, note="ID")

        # без шага Allure
        check_equal(10, 10, note="ID", with_step=False)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Извлекаем флаг управления
            with_step = kwargs.pop("with_step", True)

            # Подстановка значений в step_text
            bound_args = inspect.signature(func).bind(*args, **kwargs)
            bound_args.apply_defaults()
            format_args = {k: repr(v) for k, v in bound_args.arguments.items()}
            step_name = step_text.format(**format_args) if step_text else func.__name__

            if with_step:
                with allure.step(step_name):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def step_wrapper_base(step_text: str = "") -> Callable:
    """
    Обёртка вокруг функции с Allure step.
    Управляется параметром `with_step=True` при вызове.
    :param step_text: Название шага. Можно использовать format-переменные.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Извлекаем флаг управления
            with_step = kwargs.pop("with_step", True)

            if with_step:
                with allure.step(step_text):
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def attach_exception(title="Exception"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                allure.attach(str(e), name=title, attachment_type=allure.attachment_type.TEXT)
                raise

        return wrapper

    return decorator


def allure_response_attachments(func):
    """Декоратор для добавления вложений в Allure на основе ответа HTTP (requests.Response)."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if isinstance(response, Response) and kwargs.get("use_allure"):
            add_response_attachments(response)
        return response

    return wrapper


def allure_request_attachments(func):
    """Декоратор для добавления вложений в Allure на основе запроса HTTP (requests)."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        params = kwargs.get("params")

        response = func(*args, **kwargs)
        if isinstance(response, Response) and kwargs.get("use_allure"):
            request = response.request
            add_request_attachments(
                request.method, request.url, request.headers, request.body, params
            )
        return response

    return wrapper


def add_allure_attachments(func):
    """Декоратор для добавления вложений в Allure на основе запроса и ответа HTTP (requests.Response)."""

    @wraps(func)
    @allure_response_attachments
    @allure_request_attachments
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
