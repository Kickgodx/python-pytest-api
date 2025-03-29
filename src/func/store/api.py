import src.func.store.endpoints as url
from src.tech.custom_requester import CustomRequester


class StoreAPI(CustomRequester):
	def __init__(self, base_url: str):
		super().__init__(base_url)
		self.headers = {"Content-Type": "application/json"}

	def get_inventory(self):
		"""Get inventory"""
		return self.get(url.GET_STORE_INVENTORY)

	def get_order_by_id(self, order_id: int):
		"""Get purchase order by ID"""
		return self.get(url.GET_FIND_PURCHASE_ORDER_BY_ID.format(order_id=order_id))

	def place_order(self, data):
		"""Place an order"""
		return self.post(url.POST_PLACE_AN_ORDER, data=data, headers=self.headers)

	def delete_order_by_id(self, order_id: int):
		"""Delete purchase order by ID"""
		return self.delete(url.DELETE_DELETE_PURCHASE_ORDER_BY_ID.format(order_id=order_id))
