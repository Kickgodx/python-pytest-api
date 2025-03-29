from typing import Type, TypeVar, Union, List, Optional
from allure import step
from requests import HTTPError
from pydantic import BaseModel

from src.func.base_model import BaseRequestModel
from src.func.pet.api import PetAPI
from src.func.models import Pet, ApiResponse

T = TypeVar('T', bound=BaseModel)


class PetHelper:
	def __init__(self, base_url: str):
		self.base_url = base_url
		self.api = PetAPI(base_url)

	def _process_request(
			self,
			request_callable: callable,
			expected_status: int = 200,
			response_model: Optional[Type[T]] = None,
			is_list: bool = False,
			use_model_construct: bool = False,
			*args,
			**kwargs
	) -> Union[T, List[T], ApiResponse, dict]:
		"""
		Универсальный метод обработки запросов с поддержкой:
		- Обработки списков объектов
		- Использования model_construct
		- Кастомных моделей ответов
		"""
		try:
			response = request_callable(*args, **kwargs)
			assert response.status_code == expected_status, (
				f"Expected status {expected_status}, got {response.status_code}"
			)
		except HTTPError as e:
			assert e.response.status_code == expected_status, (
				f"Unexpected error status: {e.response.status_code}"
			)
			return ApiResponse(**e.response.json())

		if response_model:
			if is_list:
				if use_model_construct:
					return [response_model.model_construct(**item) for item in response.json()]
				return [response_model(**item) for item in response.json()]

			if use_model_construct:
				return response_model.model_construct(**response.json())
			return response_model(**response.json())

		return response.json()

	@step("Создание питомца")
	def create_pet(self, data: BaseRequestModel, expected_status_code: int = 200) -> Pet:
		return self._process_request(
			self.api.post_pet,
			expected_status_code,
			Pet,
			data=data.serialize_payload_by_alias()
		)

	@step("Получение информации о питомце по ID")
	def get_pet(self, pet_id: int, expected_status_code: int = 200) -> Union[Pet, ApiResponse]:
		return self._process_request(
			self.api.get_find_pet_by_id,
			expected_status_code,
			Pet,
			pet_id=pet_id
		)

	@step("Получение информации о питомцах по статусу")
	def get_pet_by_status(self, pet_status: list[str], expected_status_code: int = 200) -> List[Pet]:
		return self._process_request(
			self.api.get_find_pet_by_status,
			expected_status_code,
			Pet,
			is_list=True,
			use_model_construct=True,
			pet_status=pet_status
		)

	@step("Обновление информации о питомце")
	def update_pet(self, data: BaseRequestModel, expected_status_code: int = 200) -> Pet:
		return self._process_request(
			self.api.put_pet,
			expected_status_code,
			Pet,
			data=data.serialize_payload_by_alias()
		)

	@step("Удаление питомца")
	def delete_pet(self, pet_id: int, expected_status_code: int = 200) -> ApiResponse:
		return self._process_request(
			self.api.delete_pet,
			expected_status_code,
			ApiResponse,
			pet_id=pet_id
		)

	@step("Загрузка изображения питомца")
	def upload_image(
			self,
			pet_id: int,
			additional_metadata: str,
			file: bytes,
			expected_status_code: int = 200
	) -> ApiResponse:
		return self._process_request(
			self.api.post_upload_image,
			expected_status_code,
			ApiResponse,
			pet_id=pet_id,
			additional_metadata=additional_metadata,
			file=file
		)

	@step("Обновление статуса и имени питомца")
	def update_status_and_name(
			self,
			pet_id: int,
			name: str,
			status: str,
			expected_status_code: int = 200
	) -> ApiResponse:
		return self._process_request(
			self.api.post_update_status_and_name,
			expected_status_code,
			ApiResponse,
			pet_id=pet_id,
			name=name,
			status=status
		)