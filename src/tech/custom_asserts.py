from allure import step


class CustomAsserts:

	@classmethod
	def assert_equal(cls, value, expected_value, description=None):
		"""
		Проверка, что значение равно ожидаемому
		:param value: фактическое значение
		:param expected_value: ожидаемое значение
		:param description: описание проверки (необязательно)
		"""
		step_name = description if description else f"Проверка, что '{value}' равно '{expected_value}'"

		@step(step_name)
		def _assert_equal(val, expected_val):
			if isinstance(val, str) or isinstance(expected_val, str):
				val = str(val)
				expected_val = str(expected_val)
			assert val == expected_val, f"Значение {value} не равно ожидаемому {expected_value}"

		_assert_equal(value, expected_value)

	@classmethod
	def check_item_in_list(cls, item, item_list, description=None):
		"""
		Проверка, что элемент присутствует в списке
		:param item: элемент для проверки
		:param item_list: список, в котором проверяется наличие элемента
		:param description: описание проверки (необязательно)
		"""
		step_name = description if description else f"Проверка, что '{item}' присутствует в списке"

		@step(step_name)
		def _check_item_in_list(itm, lst):
			assert itm in lst, f"Элемент {item} не найден в списке"

		_check_item_in_list(item, item_list)
