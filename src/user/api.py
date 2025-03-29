from utils.custom_requester import CustomRequester
import src.user.endpoints as url

class UserAPI(CustomRequester):
	def __init__(self, base_url: str):
		super().__init__(base_url)
		self.headers = {"Content-Type": "application/json"}

	def create_user(self, data):
		"""Create user"""
		return self.post(url.POST_CREATE_USER, data=data, headers=self.headers)

	def create_user_list(self, data: list):
		"""Create user list"""
		return self.post(url.POST_CREATE_USER_LIST, json=data)

	def create_user_with_array(self, data: list):
		"""Create user with array"""
		return self.post(url.POST_CREATE_USER_WITH_ARRAY, json=data)

	def get_user_by_username(self, username: str):
		"""Get user by username"""
		return self.get(url.GET_USER_BY_USERNAME.format(username=username))

	def login_user(self, username: str, password: str):
		"""Login user"""
		query = {"username": username, "password": password}
		return self.get(url.GET_LOGIN_USER, params=query)

	def logout_user(self):
		"""Logout user"""
		return self.get(url.GET_LOGOUT_USER)

	def update_user(self, username: str, data):
		"""Update user"""
		return self.put(url.PUT_UPDATE_USER.format(username=username), data=data, headers=self.headers)

	def delete_user(self, username: str):
		"""Delete user"""
		return self.delete(url.DELETE_USER.format(username=username))
