from src.api.store.router import StoreRouter as Router
from src.models.client import Client
from src.utils.custom_requester import CustomRequester


class StoreAPI(CustomRequester):
    def get_inventory(self, client: Client):
        """Get inventory"""
        return self.get(Router.GET_STORE_INVENTORY, headers=client.get_base_headers())

    def get_order_by_id(self, client: Client, order_id: int):
        """Get purchase order by ID"""
        return self.get(
            Router.GET_FIND_PURCHASE_ORDER_BY_ID.format(order_id=order_id),
            headers=client.get_base_headers(),
        )

    def place_order(self, client: Client, data):
        """Place an order"""
        return self.post(Router.POST_PLACE_AN_ORDER, data=data, headers=client.get_base_headers())

    def delete_order_by_id(self, client: Client, order_id: int):
        """Delete purchase order by ID"""
        return self.delete(
            Router.DELETE_DELETE_PURCHASE_ORDER_BY_ID.format(order_id=order_id),
            headers=client.get_base_headers(),
        )
