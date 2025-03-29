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
		# Сначала создаём заказ
		with allure.step("Создание заказа"):
			response = store_helper.place_order(order_data)
			CustomAsserts.assert_equal(response.status, order_data.status)
			CustomAsserts.assert_equal(response.id, order_data.id)

		time.sleep(5)

		with allure.step("Получение информации о заказе"):
			response = store_helper.get_order_by_id(order_data.id)
			CustomAsserts.assert_equal(response.status, order_data.status)
