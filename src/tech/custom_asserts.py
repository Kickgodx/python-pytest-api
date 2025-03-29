from allure import step


class CustomAsserts:

	@classmethod
	@step("Проверка, что значение равно ожидаемому")
	def assert_equal(cls, value, expected_value):
		# Если одно из значений - str, то приводим оба к строке и сравниваем
		if isinstance(value, str) or isinstance(expected_value, str):
			value = str(value)
			expected_value = str(expected_value)
		assert value == expected_value, f"Значение {value} не равно ожидаемому {expected_value}"
