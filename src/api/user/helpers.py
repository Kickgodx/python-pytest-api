from http import HTTPStatus
from typing import Union

from allure import step

from src.api.user.api import UserAPI
from src.models.base_model import BaseRequestModel
from src.models.client import Client
from src.models.petstore import ApiResponse, User
from src.utils.custom_asserts import CustomAsserts


class UserHelper:
    def __init__(self, base_url: str) -> None:
        self.api = UserAPI(base_url)

    @step("Создание пользователя")
    def create_user(
        self,
        client: Client,
        data: BaseRequestModel,
        expected_status_code: int = 200,
    ) -> ApiResponse:
        """Создать пользователя и вернуть ApiResponse."""
        response = self.api.create_user(client, data.serialize_payload_by_alias())
        CustomAsserts.check_status_code(response, expected_status_code)
        return ApiResponse(**response.json())

    @step("Получение информации о пользователе")
    def get_user(
        self,
        client: Client,
        username: str,
        expected_status_code: int = 200,
    ) -> Union[ApiResponse, User]:
        """Получить пользователя по username. Возвращает User или ApiResponse при ошибке."""
        response = self.api.get_user_by_username(client, username)
        CustomAsserts.check_status_code(response, expected_status_code)
        if response.status_code == HTTPStatus.OK.value:
            return User(**response.json())
        return ApiResponse(**response.json())

    @step("Обновление информации о пользователе")
    def update_user(
        self,
        client: Client,
        username: str,
        data: BaseRequestModel,
        expected_status_code: int = 200,
    ) -> ApiResponse:
        """Обновить пользователя и вернуть ApiResponse."""
        response = self.api.update_user(client, username, data.serialize_payload_by_alias())
        CustomAsserts.check_status_code(response, expected_status_code)
        return ApiResponse(**response.json())

    @step("Удаление пользователя")
    def delete_user(
        self,
        client: Client,
        username: str,
        expected_status_code: int = 200,
    ) -> Union[ApiResponse, dict]:
        """Удалить пользователя по username."""
        response = self.api.delete_user(client, username)
        CustomAsserts.check_status_code(response, expected_status_code)
        if response.status_code == HTTPStatus.OK.value:
            try:
                return ApiResponse(**response.json())
            except Exception:
                return {"raw_response": response.text}
        return response.json()

    @step("Авторизация пользователя")
    def login_user(
        self,
        client: Client,
        username: str,
        password: str,
        expected_status_code: int = 200,
    ) -> ApiResponse:
        """Авторизация пользователя."""
        response = self.api.login_user(client, username, password)
        CustomAsserts.check_status_code(response, expected_status_code)
        return ApiResponse(**response.json())

    @step("Выход из аккаунта")
    def logout_user(
        self,
        client: Client,
        expected_status_code: int = 200,
    ) -> ApiResponse:
        """Выход пользователя из аккаунта."""
        response = self.api.logout_user(client)
        CustomAsserts.check_status_code(response, expected_status_code)
        return ApiResponse(**response.json())

    @step("Создание пользователя с массивом")
    def create_user_with_array(
        self,
        client: Client,
        data: list[User],
        expected_status_code: int = 200,
    ) -> ApiResponse:
        """Создать пользователей из массива."""
        response = self.api.create_user_with_array(
            client, BaseRequestModel.serialize_array_by_alias(data)
        )
        CustomAsserts.check_status_code(response, expected_status_code)
        return ApiResponse(**response.json())

    @step("Создание списка пользователей")
    def create_user_list(
        self,
        client: Client,
        data: list,
        expected_status_code: int = 200,
    ) -> dict:
        """Создать список пользователей."""
        response = self.api.create_user_list(client, data)
        CustomAsserts.check_status_code(response, expected_status_code)
        try:
            return response.json()
        except Exception:
            return {"raw_response": response.text}
