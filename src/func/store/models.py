from enum import Enum

from src.func.base_model import BaseRequestModel


class OrderStatus(Enum):
	"""Статус заказа"""
	PLACED = "placed"
	APPROVED = "approved"
	DELIVERED = "delivered"

	@classmethod
	def get_values(cls) -> list:
		"""Возвращает список всех значений"""
		return [cls.PLACED, cls.APPROVED, cls.DELIVERED]


class Order(BaseRequestModel):
	"""Модель заказа"""
	id: int
	petId: int
	quantity: int
	shipDate: str
	status: OrderStatus
	complete: bool
