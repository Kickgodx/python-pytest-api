from src.user.api import UserAPI
from allure import step

class UserHelper:
	def __init__(self, base_url: str):
		self.base_url = base_url
		self.api = UserAPI(base_url)

	@step("Создание пользователя")
	def create_user(self, data: dict):
		response = self.api.create_user(data)
		assert response.status_code == 200
		return response.json()

	@step("Получение информации о пользователе")
	def get_user(self, username: str):
		response = self.api.get_user_by_username(username)
		assert response.status_code == 200
		return response.json()

	@step("Обновление информации о пользователе")
	def update_user(self, username: str, data: dict):
		response = self.api.update_user(username, data)
		assert response.status_code == 200
		return response.json()

	@step("Удаление пользователя")
	def delete_user(self, username: str):
		response = self.api.delete_user(username)
		assert response.status_code == 200
		return response.json()

	@step("Авторизация пользователя")
	def login_user(self, username: str, password: str):
		response = self.api.login_user(username, password)
		assert response.status_code == 200
		return response.json()

	@step("Выход из аккаунта")
	def logout_user(self):
		response = self.api.logout_user()
		assert response.status_code == 200
		return response.json()

	@step("Создание пользователя с массивом")
	def create_user_with_array(self, data: list):
		response = self.api.create_user_with_array(data)
		assert response.status_code == 200
		return response.json()

	@step("Создание списка пользователей")
	def create_user_list(self, data: list):
		response = self.api.create_user_list(data)
		assert response.status_code == 200
		return response.json()

