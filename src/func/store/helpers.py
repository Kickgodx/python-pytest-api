from typing import Type, TypeVar, Union, Optional, Dict, Any
from allure import step
from requests import HTTPError
from pydantic import BaseModel

from src.func.base_model import BaseRequestModel
from src.func.store.api import StoreAPI
from src.func.models import Order, ApiResponse

T = TypeVar('T', bound=BaseModel)


class StoreHelper:
	def __init__(self, base_url: str):
		self.base_url = base_url
		self.api = StoreAPI(base_url)

	def _process_request(
			self,
			request_callable: callable,
			expected_status: int = 200,
			response_model: Optional[Type[T]] = None,
			*args,
			**kwargs
	) -> Union[T, ApiResponse, Dict[str, Any]]:
		"""
		Универсальный обработчик запросов с обработкой ошибок и десериализацией
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

		return response_model(**response.json()) if response_model else response.json()

	@step("Получение информации о складе")
	def get_inventory(self, expected_status_code: int = 200) -> dict:
		return self._process_request(
			self.api.get_inventory,
			expected_status_code
		)

	@step("Получение информации о заказе по ID")
	def get_order_by_id(self, order_id: int, expected_status_code: int = 200) -> Union[Order, ApiResponse]:
		return self._process_request(
			self.api.get_order_by_id,
			expected_status_code,
			Order,
			order_id
		)

	@step("Создание заказа")
	def place_order(self, data: BaseRequestModel, expected_status_code: int = 200) -> Order:
		return self._process_request(
			self.api.place_order,
			expected_status_code,
			Order,
			data.serialize_payload_by_alias()
		)

	@step("Удаление заказа по ID")
	def delete_order_by_id(self, order_id: int, expected_status_code: int = 200) -> ApiResponse:
		return self._process_request(
			self.api.delete_order_by_id,
			expected_status_code,
			ApiResponse,
			order_id
		)