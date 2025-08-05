from http import HTTPStatus
from typing import Any, Union

from allure import step

from src.api.pet.api import PetAPI
from src.models.base_model import BaseRequestModel
from src.models.client import Client
from src.models.petstore import ApiResponse, Pet
from src.utils.custom_asserts import CustomAsserts


class PetHelper:
    def __init__(self, base_url: str) -> None:
        self.api = PetAPI(base_url)

    @step("Создание питомца")
    def create_pet(
        self,
        client: Client,
        data: BaseRequestModel,
        expected_status_code: int = 200
    ) -> Pet:
        """Создать питомца и вернуть объект Pet."""
        response = self.api.post_pet(client, data.serialize_payload_by_alias())
        CustomAsserts.check_status_code(response, expected_status_code)
        return Pet(**response.json())

    @step("Получение информации о питомце по ID")
    def get_pet(
        self,
        client: Client,
        pet_id: str,
        expected_status_code: int = 200
    ) -> Union[Pet, ApiResponse]:
        """Получить питомца по ID. Возвращает Pet или ApiResponse при ошибке."""
        response = self.api.get_find_pet_by_id(client, pet_id)
        CustomAsserts.check_status_code(response, expected_status_code)
        if response.status_code == HTTPStatus.OK.value:
            return Pet(**response.json())
        return ApiResponse(**response.json())

    @step("Получение информации о питомцах по статусу")
    def get_pet_by_status(
        self,
        client: Client,
        pet_status: list[str],
        expected_status_code: int = 200
    ) -> list[Pet]:
        """Получить список питомцев по статусу."""
        response = self.api.get_find_pet_by_status(client, pet_status)
        CustomAsserts.check_status_code(response, expected_status_code)
        pets = response.json()
        if not isinstance(pets, list):
            raise ValueError(f"Ожидался список питомцев, получено: {type(pets)}")
        return [Pet.model_construct(**pet) for pet in pets]

    @step("Обновление информации о питомце")
    def update_pet(
        self,
        client: Client,
        data: BaseRequestModel,
        expected_status_code: int = 200
    ) -> Pet:
        """Обновить данные питомца."""
        response = self.api.put_pet(client, data.serialize_payload_by_alias())
        CustomAsserts.check_status_code(response, expected_status_code)
        return Pet(**response.json())

    @step("Удаление питомца")
    def delete_pet(
        self,
        client: Client,
        pet_id: str,
        expected_status_code: int = 200
    ) -> dict:
        """Удалить питомца по ID."""
        response = self.api.delete_pet(client, pet_id)
        CustomAsserts.check_status_code(response, expected_status_code)
        try:
            return response.json()
        except Exception:
            return {"raw_response": response.text}

    @step("Загрузка изображения питомца")
    def upload_image(
        self,
        client: Client,
        pet_id: str,
        additional_metadata: str,
        file: Any,
        expected_status_code: int = 200
    ) -> dict:
        """Загрузить изображение для питомца."""
        response = self.api.post_upload_image(client, pet_id, additional_metadata, file)
        CustomAsserts.check_status_code(response, expected_status_code)
        try:
            return response.json()
        except Exception:
            return {"raw_response": response.text}

    @step("Обновление статуса и имени питомца")
    def update_status_and_name(
        self,
        client: Client,
        pet_id: str,
        name: str,
        status: str,
        expected_status_code: int = 200
    ) -> dict:
        """Обновить статус и имя питомца."""
        response = self.api.post_update_status_and_name(client, pet_id, name, status)
        CustomAsserts.check_status_code(response, expected_status_code)
        try:
            return response.json()
        except Exception:
            return {"raw_response": response.text}
