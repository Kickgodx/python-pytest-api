from typing import Type, TypeVar, Optional, Union
from allure import step
from requests import HTTPError
from pydantic import BaseModel

from src.func.base_model import BaseRequestModel
from src.func.user.api import UserAPI
from src.func.models import User, ApiResponse

T = TypeVar('T', bound=BaseModel)


class UserHelper:
	def __init__(self, base_url: str):
		self.base_url = base_url
		self.api = UserAPI(base_url)

	def _process_request(
			self,
			request_callable: callable,
			expected_status: int = 200,
			response_model: Optional[Type[T]] = None,
			*args,
			**kwargs
	) -> Union[T, ApiResponse, dict]:
		"""
		Универсальный метод для обработки API-запросов
		"""
		try:
			response = request_callable(*args, **kwargs)
			assert response.status_code == expected_status, f"Expected status {expected_status}, got {response.status_code}"
		except HTTPError as e:
			assert e.response.status_code == expected_status, f"Unexpected error status: {e.response.status_code}"
			return ApiResponse(**e.response.json())

		if response_model:
			return response_model(**response.json())
		return response.json()

	@step("Создание пользователя")
	def create_user(self, data: BaseRequestModel, expected_status_code: int = 200) -> ApiResponse:
		return self._process_request(
			self.api.create_user,
			expected_status_code,
			ApiResponse,
			data.serialize_payload_by_alias()
		)

	@step("Получение информации о пользователе")
	def get_user(self, username: str, expected_status_code: int = 200) -> Union[User, ApiResponse]:
		return self._process_request(
			self.api.get_user_by_username,
			expected_status_code,
			User,
			username
		)

	@step("Обновление информации о пользователе")
	def update_user(self, username: str, data: BaseRequestModel, expected_status_code: int = 200) -> ApiResponse:
		return self._process_request(
			self.api.update_user,
			expected_status_code,
			ApiResponse,
			username,
			data.serialize_payload_by_alias()
		)

	@step("Удаление пользователя")
	def delete_user(self, username: str, expected_status_code: int = 200) -> ApiResponse:
		return self._process_request(
			self.api.delete_user,
			expected_status_code,
			ApiResponse,
			username
		)

	@step("Авторизация пользователя")
	def login_user(self, username: str, password: str, expected_status_code: int = 200) -> ApiResponse:
		return self._process_request(
			self.api.login_user,
			expected_status_code,
			ApiResponse,
			username,
			password
		)

	@step("Выход из аккаунта")
	def logout_user(self, expected_status_code: int = 200) -> ApiResponse:
		return self._process_request(
			self.api.logout_user,
			expected_status_code,
			ApiResponse
		)

	@step("Создание пользователя с массивом")
	def create_user_with_array(self, data: list[User], expected_status_code: int = 200) -> ApiResponse:
		return self._process_request(
			self.api.create_user_with_array,
			expected_status_code,
			ApiResponse,
			[user.model_dump() for user in data]
		)

	@step("Создание списка пользователей")
	def create_user_list(self, data: list, expected_status_code: int = 200) -> ApiResponse:
		return self._process_request(
			self.api.create_user_list,
			expected_status_code,
			ApiResponse,
			data
		)