from http import HTTPStatus
from typing import Union

from allure import step

from src.api.store.api import StoreAPI
from src.models.base_model import BaseRequestModel
from src.models.client import Client
from src.models.petstore import ApiResponse, Order
from src.utils.custom_asserts import CustomAsserts


class StoreHelper:
    def __init__(self, base_url: str) -> None:
        self.api = StoreAPI(base_url)

    @step("Получение информации о складе")
    def get_inventory(
        self,
        client: Client,
        expected_status_code: int = 200,
    ) -> dict:
        """Получить информацию о складе."""
        response = self.api.get_inventory(client)
        CustomAsserts.check_status_code(response, expected_status_code)
        try:
            return response.json()
        except Exception:
            return {"raw_response": response.text}

    @step("Получение информации о заказе по ID")
    def get_order_by_id(
        self,
        client: Client,
        order_id: int,
        expected_status_code: int = 200,
    ) -> Union[Order, ApiResponse]:
        """Получить заказ по ID. Возвращает Order или ApiResponse при ошибке."""
        response = self.api.get_order_by_id(client, order_id)
        CustomAsserts.check_status_code(response, expected_status_code)
        if response.status_code == HTTPStatus.OK.value:
            return Order(**response.json())
        return ApiResponse(**response.json())

    @step("Создание заказа")
    def place_order(
        self,
        client: Client,
        data: BaseRequestModel,
        expected_status_code: int = 200,
    ) -> Order:
        """Создать заказ и вернуть объект Order."""
        response = self.api.place_order(client, data.serialize_payload_by_alias())
        CustomAsserts.check_status_code(response, expected_status_code)
        return Order(**response.json())

    @step("Удаление заказа по ID")
    def delete_order_by_id(
        self,
        client: Client,
        order_id: int,
        expected_status_code: int = 200,
    ) -> Union[dict, ApiResponse]:
        """Удалить заказ по ID."""
        response = self.api.delete_order_by_id(client, order_id)
        CustomAsserts.check_status_code(response, expected_status_code)
        if response.status_code == HTTPStatus.OK.value:
            try:
                return response.json()
            except Exception:
                return {"raw_response": response.text}
        return ApiResponse(**response.json())
