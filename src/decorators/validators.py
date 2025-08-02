from functools import wraps

import allure
from jsonschema import ValidationError, validate


def validate_json(schema):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            try:
                validate(instance=response.json(), schema=schema)
            except ValidationError as e:
                allure.attach(str(e), name="Validation Error", attachment_type=allure.attachment_type.TEXT)
                raise
            return response

        return wrapper

    return decorator
