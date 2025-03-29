from requests import HTTPError

from src.base_model import BaseRequestModel
from src.pet.api import PetAPI
from allure import step

from src.pet.models import Pet
from src.user.models import ApiResponse


class PetHelper:
	def __init__(self, base_url: str):
		self.base_url = base_url
		self.api = PetAPI(base_url)

	@step("Создание питомца")
	def create_pet(self, data: BaseRequestModel, expected_status_code=200) 	-> Pet:
		response = self.api.post_pet(data.serialize_payload_by_alias())
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		return Pet(**response.json())

	@step("Получение информации о питомце по ID")
	def get_pet(self, pet_id, expected_status_code=200) -> Pet | ApiResponse:
		try:
			response = self.api.get_find_pet_by_id(pet_id)
			assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		except HTTPError as e:
			assert e.response.status_code == expected_status_code, f"Unexpected status code {e.response.status_code}"
			return ApiResponse(**e.response.json())
		else:
			assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
			return Pet(**response.json())

	@step("Получение информации о питомцах по статусу")
	def get_pet_by_status(self, pet_status: list[str], expected_status_code: int = 200) -> list[Pet]:
		response = self.api.get_find_pet_by_status(pet_status)
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		res = [Pet.model_construct(**pet) for pet in response.json()]
		return res

	@step("Обновление информации о питомце")
	def update_pet(self, data: BaseRequestModel, expected_status_code=200) -> Pet:
		response = self.api.put_pet(data.serialize_payload_by_alias())
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		return Pet(**response.json())

	@step("Удаление питомца")
	def delete_pet(self, pet_id, expected_status_code=200):
		try:
			response = self.api.delete_pet(pet_id)
		except HTTPError as e:
			assert e.response.status_code == expected_status_code, f"Unexpected status code {e.response.status_code}"
			return e.response
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		return response.json()

	@step("Загрузка изображения питомца")
	def upload_image(self, pet_id, additional_metadata, file, expected_status_code=200):
		response = self.api.post_upload_image(pet_id, additional_metadata, file)
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		return response.json()

	@step("Обновление статуса и имени питомца")
	def update_status_and_name(self, pet_id, name, status, expected_status_code=200):
		response = self.api.post_update_status_and_name(pet_id, name, status)
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		return response.json()