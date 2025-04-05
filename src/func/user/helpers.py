from allure import step

from src.func.models import User, ApiResponse
from src.func.user.api import UserAPI
from src.models.base_model import BaseRequestModel
from src.models.client import Client


class UserHelper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.api = UserAPI(base_url)

    @step("Создание пользователя")
    def create_user(self, client: Client, data: BaseRequestModel, expected_status_code=200) -> ApiResponse:
        response = self.api.create_user(client, data.serialize_payload_by_alias())
        assert response.status_code == expected_status_code
        return ApiResponse(**response.json())

    @step("Получение информации о пользователе")
    def get_user(self, client: Client, username: str, expected_status_code=200) -> ApiResponse | User:
        response = self.api.get_user_by_username(client, username)
        assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
        if response.status_code == 200:
            return User(**response.json())
        else:
            return ApiResponse(**response.json())

    @step("Обновление информации о пользователе")
    def update_user(self, client: Client, username: str, data: BaseRequestModel) -> ApiResponse:
        response = self.api.update_user(client, username, data.serialize_payload_by_alias())
        assert response.status_code == 200
        return ApiResponse(**response.json())

    @step("Удаление пользователя")
    def delete_user(self, client: Client, username: str) -> ApiResponse:
        response = self.api.delete_user(client, username)
        assert response.status_code == 200, f"Unexpected status code {response.status_code}"

        if response.status_code == 200:
            return ApiResponse(**response.json())
        else:
            return response.json()

    @step("Авторизация пользователя")
    def login_user(self, client: Client, username: str, password: str) -> ApiResponse:
        response = self.api.login_user(client, username, password)
        assert response.status_code == 200
        return ApiResponse(**response.json())

    @step("Выход из аккаунта")
    def logout_user(self, client: Client) -> ApiResponse:
        response = self.api.logout_user(client)
        assert response.status_code == 200
        return ApiResponse(**response.json())

    @step("Создание пользователя с массивом")
    def create_user_with_array(self, client: Client, data: list[User]) -> ApiResponse:
        # list_users = [user.model_dump(exclude_none=True) for user in data]
        response = self.api.create_user_with_array(client, BaseRequestModel.serialize_array_by_alias(data))
        assert response.status_code == 200
        return ApiResponse(**response.json())

    @step("Создание списка пользователей")
    def create_user_list(self, client: Client, data: list) -> dict:
        response = self.api.create_user_list(client, data)
        assert response.status_code == 200
        return response.json()
