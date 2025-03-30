from allure import step
from requests import HTTPError

from src.func.base_model import BaseRequestModel
from src.func.user.api import UserAPI
from src.func.models import User, ApiResponse


class UserHelper:
	def __init__(self, base_url: str):
		self.base_url = base_url
		self.api = UserAPI(base_url)

	@step("Создание пользователя")
	def create_user(self, data: BaseRequestModel, expected_status_code=200) -> ApiResponse:
		response = self.api.create_user(data.serialize_payload_by_alias())
		assert response.status_code == expected_status_code
		return ApiResponse(**response.json())

	@step("Получение информации о пользователе")
	def get_user(self, username: str, expected_status_code=200) -> ApiResponse | User:
		try:
			response = self.api.get_user_by_username(username)
			assert response.status_code == expected_status_code
		except HTTPError as e:
			assert e.response.status_code == expected_status_code, f"Unexpected status code {e.response.status_code}"
			return ApiResponse(**e.response.json())
		else:
			assert response.status_code == expected_status_code
			return User(**response.json())

	@step("Обновление информации о пользователе")
	def update_user(self, username: str, data: BaseRequestModel) -> ApiResponse:
		response = self.api.update_user(username, data.serialize_payload_by_alias())
		assert response.status_code == 200
		return ApiResponse(**response.json())

	@step("Удаление пользователя")
	def delete_user(self, username: str) -> ApiResponse:
		try:
			response = self.api.delete_user(username)
			assert response.status_code == 200
		except HTTPError as e:
			assert e.response.status_code == 200, f"Unexpected status code {e.response.status_code}"
			return ApiResponse(**e.response.json())
		else:
			assert response.status_code == 200
			return ApiResponse(**response.json())

	@step("Авторизация пользователя")
	def login_user(self, username: str, password: str) -> ApiResponse:
		response = self.api.login_user(username, password)
		assert response.status_code == 200
		return ApiResponse(**response.json())

	@step("Выход из аккаунта")
	def logout_user(self) -> ApiResponse:
		response = self.api.logout_user()
		assert response.status_code == 200
		return ApiResponse(**response.json())

	@step("Создание пользователя с массивом")
	def create_user_with_array(self, data: list[User]) -> ApiResponse:
		# list_users = [user.model_dump(exclude_none=True) for user in data]
		response = self.api.create_user_with_array(BaseRequestModel.serialize_array_by_alias(data))
		assert response.status_code == 200
		return ApiResponse(**response.json())

	@step("Создание списка пользователей")
	def create_user_list(self, data: list) -> dict:
		response = self.api.create_user_list(data)
		assert response.status_code == 200
		return response.json()
