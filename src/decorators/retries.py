import time
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
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                    time.sleep(delay)
            return None

        return wrapper

    return decorator
