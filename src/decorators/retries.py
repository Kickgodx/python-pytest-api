import time
from contextlib import suppress
from functools import wraps


def retry_on_exception(max_attempts=3, delay=1, exceptions=(Exception,)):
    """
    Декоратор для повторной попытки выполнения функции при возникновении исключений.
    @param max_attempts: Количество попыток выполнения функции
    @param delay: задержка между попытками в секундах
    @param exceptions: кортеж исключений, при которых будет выполняться повторная попытка
    @return: декорированная функция, которая будет повторно вызываться при возникновении исключений
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(max_attempts - 1):
                with suppress(*exceptions):
                    return func(*args, **kwargs)
                time.sleep(delay)
            return func(*args, **kwargs)

        return wrapper

    return decorator
