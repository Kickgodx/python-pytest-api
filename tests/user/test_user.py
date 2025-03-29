import random

import allure
import pytest

from src.user.models import User


@pytest.fixture(scope="function")
def user_data():
    """Фикстура для данных пользователя"""
    # Рандомный id
    user_id = random.randint(1, 100000)

    return User(**{
        "id": user_id,
        "username": "test_user",
        "firstName": "Test",
        "lastName": "User",
        "email": "test@example.com",
        "password": "123456",
        "phone": "1234567890",
        "userStatus": 1
    })


@allure.epic("Petstore API")
@allure.feature("User")
@pytest.mark.user
class TestUser:

    @allure.title("Создание пользователя")
    def test_create_user(self, user_helper, user_data):
        response = user_helper.create_user(user_data)
        assert response.message == str(user_data.id)

    @allure.title("Получение информации о пользователе")
    def test_get_user(self, user_helper, user_data):
        response = user_helper.create_user(user_data)

        response = user_helper.get_user(user_data.username)
        assert response.username == user_data.username
