from allure import step
from requests import Response

from src.models.base_model import BaseRequestModel
from src.func.pet.api import PetAPI
from src.models.petstore import Pet, ApiResponse
from src.models.client import Client
from src.tech.custom_asserts import CustomAsserts


class PetHelper:
	def __init__(self, base_url: str):
		self.base_url = base_url
		self.api = PetAPI(base_url)

	@step("Создание питомца")
	def create_pet(self, client: Client, data: BaseRequestModel, expected_status_code=200) -> Pet:
		response = self.api.post_pet(client, data.serialize_payload_by_alias())
		CustomAsserts.check_status_code(response, expected_status_code)
		return Pet(**response.json())

	@step("Получение информации о питомце по ID")
	def get_pet(self, client: Client, pet_id, expected_status_code=200) -> Pet | ApiResponse:
			response = self.api.get_find_pet_by_id(client, pet_id)
			CustomAsserts.check_status_code(response, expected_status_code)
			if response.status_code == 200:
				return Pet(**response.json())
			else:
				return ApiResponse(**response.json())

	@step("Получение информации о питомцах по статусу")
	def get_pet_by_status(self, client: Client, pet_status: list[str], expected_status_code: int = 200) -> list[Pet]:
		response = self.api.get_find_pet_by_status(client, pet_status)
		CustomAsserts.check_status_code(response, expected_status_code)
		res = [Pet.model_construct(**pet) for pet in response.json()]
		return res

	@step("Обновление информации о питомце")
	def update_pet(self, client: Client, data: BaseRequestModel, expected_status_code=200) -> Pet:
		response = self.api.put_pet(client, data.serialize_payload_by_alias())
		CustomAsserts.check_status_code(response, expected_status_code)
		return Pet(**response.json())

	@step("Удаление питомца")
	def delete_pet(self, client: Client, pet_id, expected_status_code=200) -> dict | Response:
		response = self.api.delete_pet(client, pet_id)
		CustomAsserts.check_status_code(response, expected_status_code)
		return response.json()

	@step("Загрузка изображения питомца")
	def upload_image(self, client: Client, pet_id, additional_metadata, file, expected_status_code=200) -> dict:
		response = self.api.post_upload_image(client, pet_id, additional_metadata, file)
		CustomAsserts.check_status_code(response, expected_status_code)
		return response.json()

	@step("Обновление статуса и имени питомца")
	def update_status_and_name(self, client: Client, pet_id, name, status, expected_status_code=200) -> dict:
		response = self.api.post_update_status_and_name(client, pet_id, name, status)
		CustomAsserts.check_status_code(response, expected_status_code)
		return response.json()
