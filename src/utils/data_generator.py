from faker import Faker

from src.models.petstore import OrderStatus, PetStatus


class DataGenerator:
    """Фейкер для генерации рандомных данных"""

    faker = Faker()

    @classmethod
    def fake_name(cls) -> str:
        return cls.faker.word()

    @classmethod
    def fake_email(cls) -> str:
        return cls.faker.email()

    @classmethod
    def generate_pet_body(cls) -> dict:
        """Генерация тела запроса для создания питомца"""
        return {
            "id": cls.faker.random_int(1, 1000),
            "name": cls.faker.name(),
            "category": {
                "id": cls.faker.random_int(1, 1000),
                "name": cls.faker.name_nonbinary(),
            },
            "photoUrls": [cls.faker.image_url()],
            "tags": [
                {
                    "id": cls.faker.random_int(1, 1000),
                    "name": cls.faker.color_name(),
                }
            ],
            "status": cls.faker.random_element(
                [PetStatus.AVAILABLE.value, PetStatus.PENDING.value, PetStatus.SOLD.value]
            ),
        }

    @classmethod
    def generate_order_body(cls) -> dict:
        """Генерация тела запроса для создания заказа"""
        return {
            "id": cls.faker.random_int(1, 1000),
            "petId": cls.faker.random_int(1, 1000),
            "quantity": cls.faker.random_int(1, 10),
            "shipDate": cls.faker.date_time().isoformat(),
            "status": cls.faker.random_element(
                [OrderStatus.PLACED.value, OrderStatus.APPROVED.value, OrderStatus.DELIVERED.value],
            ),
            "complete": cls.faker.boolean(),
        }

    @classmethod
    def generate_user_body(cls) -> dict:
        """Генерация тела запроса для создания пользователя"""
        return {
            "id": cls.faker.random_int(1, 10000),
            "username": cls.faker.user_name(),
            "firstName": cls.faker.first_name(),
            "lastName": cls.faker.last_name(),
            "email": cls.faker.email(),
            "password": cls.faker.password(),
            "phone": cls.faker.phone_number(),
            "userStatus": cls.faker.random_int(0, 2),
        }
