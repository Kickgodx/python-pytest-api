from src.func.base_model import BaseRequestModel


class User(BaseRequestModel):
	id: int
	username: str
	firstName: str
	lastName: str
	email: str
	password: str
	phone: str
	userStatus: int


class ApiResponse(BaseRequestModel):
	code: int
	type: str
	message: str
