import allure
import pytest

from src.func.user.models import User
from src.tech.custom_asserts import CustomAsserts
from src.tech.data_generator import DataGenerator


@pytest.fixture(scope="function")
def user_data():
	"""Фикстура для данных пользователя"""
	return User(**DataGenerator().generate_user_body())


@allure.epic("Petstore API")
@allure.feature("User")
@pytest.mark.user
class TestUser:

	@allure.title("Создание пользователя")
	def test_create_user(self, user_helper, user_data):
		response = user_helper.create_user(user_data)
		CustomAsserts.assert_equal(response.message, user_data.id)

	@allure.title("Получение информации о пользователе")
	def test_get_user(self, user_helper, user_data):
		with allure.step("Создание пользователя"):
			response = user_helper.create_user(user_data)

		with allure.step("Получение информации о пользователе"):
			response = user_helper.get_user(user_data.username)
			CustomAsserts.assert_equal(response.username, user_data.username)
