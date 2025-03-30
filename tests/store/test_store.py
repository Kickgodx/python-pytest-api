import time

import allure
import pytest

from src.func.store.models import Order
from src.tech.custom_asserts import CustomAsserts
from src.tech.data_generator import DataGenerator


@pytest.fixture(scope="function")
def order_data():
	"""Фикстура для данных заказа"""
	return Order(**DataGenerator().generate_order_body())


@pytest.mark.store
@allure.epic("Petstore API")
@allure.feature("Store")
class TestStore:

	@allure.title("Создание заказа")
	def test_create_order(self, store_helper, order_data):
		response = store_helper.place_order(order_data)

	@allure.title("Создание и получение информации о заказе")
	def test_get_order(self, store_helper, order_data):
		with allure.step("Создание заказа"):
			response = store_helper.place_order(order_data)
			CustomAsserts.assert_equal(response.status, order_data.status)
			CustomAsserts.assert_equal(response.id, order_data.id)

		time.sleep(5)

		with allure.step("Получение информации о заказе"):
			response = store_helper.get_order_by_id(order_data.id)
			CustomAsserts.assert_equal(response.status, order_data.status)

	@allure.title("Создание и удаление заказа")
	def test_delete_order(self, store_helper, order_data):
		with allure.step("Создание заказа"):
			response = store_helper.place_order(order_data)
			CustomAsserts.assert_equal(response.status, order_data.status)
			CustomAsserts.assert_equal(response.id, order_data.id)

		time.sleep(5)

		response = store_helper.delete_order_by_id(order_data.id)

	@allure.title("Получение информации о складе")
	def test_get_inventory(self, store_helper):
		response = store_helper.get_inventory()
		assert response, "Inventory is empty"
		assert isinstance(response, dict), "Unexpected response type (expected dict)"

	@allure.title("Получение информации о заказе по несуществующему ID")
	def test_get_order_by_nonexistent_id(self, store_helper):
		response = store_helper.get_order_by_id(0, expected_status_code=404)
		assert response.code == 1, "Unexpected error code"
		assert response.message == "Order not found", "Unexpected error message"

	@allure.title("Удаление заказа по несуществующему ID")
	def test_delete_order_by_nonexistent_id(self, store_helper):
		response = store_helper.delete_order_by_id(0, expected_status_code=404)
		assert response.code == 404, "Unexpected error code"
		assert response.message == "Order Not Found", "Unexpected error message"

	@allure.title("Создание заказа с невалидными данными")
	def test_create_order_with_invalid_data(self, store_helper, order_data):
		order_data.id = 2025008213453549843908439809804398034593454536556445
		response = store_helper.place_order(order_data, expected_status_code=400)
		assert response.code == 400, "Unexpected error code"
		assert response.message == "Invalid Order", "Unexpected error message"
