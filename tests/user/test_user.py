import time

import allure
import pytest

from src.func.user.models import User
from src.tech.custom_asserts import CustomAsserts
from src.tech.data_generator import DataGenerator


@pytest.fixture(scope="function")
def user_data():
	"""Фикстура для данных пользователя"""
	return User(**DataGenerator().generate_user_body())

@pytest.fixture(scope="function")
def users_data():
	"""Фикстура для массива данных пользователей"""
	us_data = [User(**DataGenerator().generate_user_body()) for _ in range(10)]
	return us_data

users_datas = [User(**DataGenerator().generate_user_body()) for _ in range(10)]


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
		user_helper.create_user(user_data)

		time.sleep(5)

		with allure.step("Получение информации о пользователе"):
			response = user_helper.get_user(user_data.username)
			CustomAsserts.assert_equal(response.username, user_data.username)

	@allure.title("Обновление информации о пользователе")
	def test_update_user(self, user_helper, user_data):
		user_helper.create_user(user_data)

		time.sleep(5)

		with allure.step("Обновление информации о пользователе"):
			response = user_helper.update_user(user_data.username, user_data)
			CustomAsserts.assert_equal(response.message, user_data.id)

	@allure.title("Удаление пользователя")
	def test_delete_user(self, user_helper, user_data):
		user_helper.create_user(user_data)

		time.sleep(5)

		with allure.step("Удаление пользователя"):
			response = user_helper.delete_user(user_data.username)
			CustomAsserts.assert_equal(response.message, user_data.username)

	@allure.title("Авторизация пользователя")
	def test_login_user(self, user_helper, user_data):
		user_helper.create_user(user_data)

		time.sleep(5)

		with allure.step("Авторизация пользователя"):
			response = user_helper.login_user(user_data.username, user_data.password)
			CustomAsserts.assert_equal(response.code, 200)

	@allure.title("Выход из аккаунта")
	def test_logout_user(self, user_helper, user_data):
		user_helper.create_user(user_data)

		time.sleep(5)

		user_helper.login_user(user_data.username, user_data.password)

		time.sleep(5)

		with allure.step("Выход из аккаунта"):
			response = user_helper.logout_user()
			CustomAsserts.assert_equal(response.message, "ok")

	@allure.title("Создание пользователя из массива")
	def test_create_user_with_array(self, user_helper, users_data):
		response = user_helper.create_user_with_array(users_data)
		CustomAsserts.assert_equal(response.code, 200)
		CustomAsserts.assert_equal(response.message, "ok")