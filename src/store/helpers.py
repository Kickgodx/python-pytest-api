from src.store.api import StoreAPI
from allure import step

class StoreHelper:
	def __init__(self, base_url: str):
		self.base_url = base_url
		self.api = StoreAPI(base_url)

	@step("Получение информации о складе")
	def get_inventory(self, expected_status_code=200):
		response = self.api.get_inventory()
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		return response.json()

	@step("Получение информации о заказе по ID")
	def get_order_by_id(self, order_id, expected_status_code=200):
		response = self.api.get_order_by_id(order_id)
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		return response.json()

	@step("Создание заказа")
	def place_order(self, data, expected_status_code=200):
		response = self.api.place_order(data)
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		return response.json()

	@step("Удаление заказа по ID")
	def delete_order_by_id(self, order_id, expected_status_code=200):
		response = self.api.delete_order_by_id(order_id)
		assert response.status_code == expected_status_code, f"Unexpected status code {response.status_code}"
		return response.json()
