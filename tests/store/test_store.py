import time

import allure
import pytest

from src.store.models import Order
import random

@pytest.fixture(scope="function")
def order_data():
    """Фикстура для данных заказа"""
    rand = random.randint(1, 10)
    rand2 = random.randint(1, 100)
    return Order(**{
        "id": rand,
        "petId": rand2,
        "quantity": 1,
        "shipDate": "2025-04-01T12:00:00.000Z",
        "status": "placed",
        "complete": True
    })

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
        response = store_helper.place_order(order_data)
        assert response.status == order_data.status

        # Пауза 5 сек
        time.sleep(5)

        # Теперь получаем информацию о заказе
        response = store_helper.get_order_by_id(order_data.id)
        assert response.status == order_data.status
