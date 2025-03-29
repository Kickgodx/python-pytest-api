from faker import Faker

from src.func.models import PetStatus, OrderStatus


class DataGenerator:
	"""
	Фейкер для генерации рандомных данных
	"""
	def __init__(self):
		self.faker_instance = Faker()

	faker_instance = Faker()

	@classmethod
	def fake_name(cls) -> str:
		return cls.faker_instance.word()

	@classmethod
	def fake_email(cls) -> str:
		return cls.faker_instance.email()

	@classmethod
	def generate_pet_body(cls) -> dict:
		"""Генерация тела запроса для создания питомца"""
		return {
			"id": cls.faker_instance.random_int(1, 1000),
			"name": cls.faker_instance.name(),
			"category": {
				"id": cls.faker_instance.random_int(1, 1000),
				"name": cls.faker_instance.name_nonbinary()
			},
			"photoUrls": [cls.faker_instance.image_url()],
			"tags": [{"id": cls.faker_instance.random_int(1, 1000), "name": cls.faker_instance.color_name()}],
			"status": cls.faker_instance.random_element([PetStatus.AVAILABLE.value, PetStatus.PENDING.value, PetStatus.SOLD.value])
		}

	@classmethod
	def generate_order_body(cls) -> dict:
		"""Генерация тела запроса для создания заказа"""
		return {
			"id": cls.faker_instance.random_int(1, 1000),
			"petId": cls.faker_instance.random_int(1, 1000),
			"quantity": cls.faker_instance.random_int(1, 10),
			"shipDate": cls.faker_instance.date_time().isoformat(),
			"status": cls.faker_instance.random_element([OrderStatus.PLACED.value, OrderStatus.APPROVED.value, OrderStatus.DELIVERED.value]),
			"complete": cls.faker_instance.boolean()
		}

	@classmethod
	def generate_user_body(cls) -> dict:
		"""Генерация тела запроса для создания пользователя"""
		return {
			"id": cls.faker_instance.random_int(1, 10000),
			"username": cls.faker_instance.user_name(),
			"firstName": cls.faker_instance.first_name(),
			"lastName": cls.faker_instance.last_name(),
			"email": cls.faker_instance.email(),
			"password": cls.faker_instance.password(),
			"phone": cls.faker_instance.phone_number(),
			"userStatus": cls.faker_instance.random_int(0, 2)
		}