from typing import Any, Optional

from allure import step


class CustomAsserts:
    @classmethod
    def assert_equal(
        cls,
        value: Any,
        expected_value: Any,
        description: Optional[str] = None
    ) -> None:
        """Проверка, что значение равно ожидаемому."""
        step_name = description or f"Проверка, что '{value}' равно '{expected_value}'"

        @step(step_name)
        def _assert_equal(val, expected_val):
            if isinstance(val, str) or isinstance(expected_val, str):
                val = str(val)
                expected_val = str(expected_val)
            assert val == expected_val, f"Значение {val} не равно ожидаемому {expected_val}"

        _assert_equal(value, expected_value)

    @classmethod
    def check_item_in_list(
        cls,
        item: Any,
        item_list: list,
        description: Optional[str] = None
    ) -> None:
        """Проверка, что элемент присутствует в списке."""
        step_name = description or f"Проверка, что '{item}' присутствует в списке"

        @step(step_name)
        def _check_item_in_list(itm, lst):
            assert itm in lst, f"Элемент {itm} не найден в списке"

        _check_item_in_list(item, item_list)

    @staticmethod
    def check_status_code(response: Any, expected_status_code: int) -> None:
        """Проверка, что статус код ответа соответствует ожидаемому."""
        @step(f"Статус код = {expected_status_code}")
        def _check_status_code(resp, expected_code):
            assert hasattr(resp, "status_code"), "Объект ответа не содержит status_code"
            assert resp.status_code == expected_code, (
                f"Статус код {getattr(resp, 'status_code', None)} не равен ожидаемому {expected_code}"
            )
        _check_status_code(response, expected_status_code)
