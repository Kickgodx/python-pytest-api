import allure
import pytest

@pytest.fixture(scope="function")
def pet_data():
    """Фикстура для данных питомца"""
    return {
        "id": 456,
        "name": "Bobby",
        "category": {"id": 1, "name": "Dog"},
        "photoUrls": ["https://example.com/dog.jpg"],
        "tags": [{"id": 1, "name": "cute"}],
        "status": "available"
    }

@allure.epic("Petstore API")
@allure.feature("Pet")
class TestPet:

    @allure.title("Создание питомца")
    def test_create_pet(self, pet_helper, pet_data):
        """Добавление нового питомца"""
        response = pet_helper.create_pet(pet_data)

    @allure.title("Создание и получение информации о питомце")
    def test_get_pet(self, pet_helper, pet_data):
        """Получение информации о питомце"""
        # Сначала создаём питомца
        response = pet_helper.create_pet(pet_data)
        assert response["name"] == pet_data["name"]

        # Теперь получаем информацию о питомце
        response = pet_helper.get_pet(pet_data["id"])
        assert response["name"] == pet_data["name"]

