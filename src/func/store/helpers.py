from allure import step

from src.models.base_model import BaseRequestModel
from src.func.store.api import StoreAPI
from src.func.models import Order, ApiResponse


class StoreHelper:
	def __init__(self, base_url: str):
		self.base_url = base_url
		self.api = StoreAPI(base_url)

	@step("Получение информации о складе")
	def get_inventory(self, expected_status_code=200) -> dict:
		response = self.api.get_inventory()
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		return response.json()

	@step("Получение информации о заказе по ID")
	def get_order_by_id(self, order_id, expected_status_code=200) -> Order | ApiResponse:
		response = self.api.get_order_by_id(order_id)
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"

		if response.status_code == 200:
			return Order(**response.json())
		else:
			return ApiResponse(**response.json())

	@step("Создание заказа")
	def place_order(self, data: BaseRequestModel, expected_status_code=200) -> Order:
		response = self.api.place_order(data.serialize_payload_by_alias())
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		return Order(**response.json())

	@step("Удаление заказа по ID")
	def delete_order_by_id(self, order_id, expected_status_code=200) -> ApiResponse | dict:
		response = self.api.delete_order_by_id(order_id)
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		if response.status_code == 200:
			return response.json()
		else:
			return ApiResponse(**response.json())
