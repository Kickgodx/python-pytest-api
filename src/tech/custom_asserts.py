from allure import step


class CustomAsserts:

	@classmethod
	@step("Проверка, что значение равно ожидаемому")
	def assert_equal(cls, value, expected_value):
		assert value == expected_value, f"Значение {value} не равно ожидаемому {expected_value}"
