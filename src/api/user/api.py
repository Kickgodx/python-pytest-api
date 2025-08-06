from src.api.user.router import UserRouter as Router
from src.models.client import Client
from src.utils.custom_requester import CustomRequester


class UserAPI(CustomRequester):
    def create_user(self, client: Client, data):
        """Create user"""
        return self.post(Router.POST_CREATE_USER, data=data, headers=client.get_base_headers())

    def create_user_list(self, client: Client, data: list):
        """Create user list"""
        return self.post(Router.POST_CREATE_USER_LIST, json=data, headers=client.get_base_headers())

    def create_user_with_array(self, client: Client, data: list):
        """Create user with array"""
        return self.post(
            Router.POST_CREATE_USER_WITH_ARRAY, data=data, headers=client.get_base_headers()
        )

    def get_user_by_username(self, client: Client, username: str):
        """Get user by username"""
        return self.get(
            Router.GET_USER_BY_USERNAME.format(username=username), headers=client.get_base_headers()
        )

    def login_user(self, client: Client, username: str, password: str):
        """Login user"""
        query = {"username": username, "password": password}
        return self.get(Router.GET_LOGIN_USER, params=query, headers=client.get_base_headers())

    def logout_user(self, client: Client):
        """Logout user"""
        return self.get(Router.GET_LOGOUT_USER, headers=client.get_base_headers())

    def update_user(self, client: Client, username: str, data):
        """Update user"""
        return self.put(
            Router.PUT_UPDATE_USER.format(username=username),
            data=data,
            headers=client.get_base_headers(),
        )

    def delete_user(self, client: Client, username: str):
        """Delete user"""
        return self.delete(
            Router.DELETE_USER.format(username=username), headers=client.get_base_headers()
        )
