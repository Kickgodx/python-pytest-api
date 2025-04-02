import time

import allure
import pytest

from src.func.pet.models import Pet, PetStatus, Category, Tag
from src.tech.custom_asserts import CustomAsserts
from src.tech.data_generator import DataGenerator


@pytest.fixture(scope="function")
def pet_data():
	"""Фикстура для данных питомца"""
	return Pet(**DataGenerator().generate_pet_body())

# список питомцев для параметризации 5 штук
pets_data = [Pet(**DataGenerator().generate_pet_body()) for _ in range(10)]


@allure.epic("Petstore API")
@allure.feature("Pet")
class TestPet:

	@allure.story("Создание питомцев")
	@allure.title("Создание питомца")
	@pytest.mark.parametrize("pet_data_m", pets_data)
	def test_create_pet(self, pet_helper, pet_data_m):
		response = pet_helper.create_pet(pet_data_m)
		CustomAsserts.assert_equal(response.name, pet_data_m.name)

	@allure.story("Поиск питомцев")
	@allure.title("Создание и получение информации о питомце")
	def test_get_pet(self, pet_helper, pet_data):
		with allure.step("Создание питомца"):
			response = pet_helper.create_pet(pet_data)
			CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		with allure.step("Получение информации о питомце"):
			response = pet_helper.get_pet(pet_data.id)
			CustomAsserts.assert_equal(response.name, pet_data.name)

	@allure.story("Обновление информации о питомцах")
	@allure.title("Создание и обновление информации о питомце")
	def test_update_pet(self, pet_helper, pet_data):
		with allure.step("Создание питомца"):
			response = pet_helper.create_pet(pet_data)
			CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		with allure.step("Обновление информации о питомце"):
			new_name = "Bobby Jr."
			pet_data.name = new_name
			response = pet_helper.update_pet(pet_data)
			CustomAsserts.assert_equal(response.name, new_name)

		time.sleep(10)

		with allure.step("Проверка обновления информации о питомце"):
			response = pet_helper.get_pet(pet_data.id)
			CustomAsserts.assert_equal(response.name, new_name)

	@allure.story("Удаление питомцев")
	@allure.title("Создание и удаление питомца")
	def test_delete_pet(self, pet_helper, pet_data):
		with allure.step("Создание питомца"):
			response = pet_helper.create_pet(pet_data)
			CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		with allure.step("Удаление питомца"):
			pet_helper.delete_pet(pet_data.id)

		time.sleep(10)

		with allure.step("Проверка удаления питомца"):
			response = pet_helper.get_pet(pet_data.id, 404)
			CustomAsserts.assert_equal(response.message, "Pet not found")

	@allure.story("Обновление информации о питомцах")
	@allure.title("Создание и обновление статуса питомца")
	def test_update_pet_status(self, pet_helper, pet_data):
		with allure.step("Создание питомца"):
			response = pet_helper.create_pet(pet_data)
			CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		with allure.step("Обновление статуса питомца"):
			pet_data.status = PetStatus.SOLD.value
			response = pet_helper.update_pet(pet_data)
			CustomAsserts.assert_equal(response.status, PetStatus.SOLD.value)

		with allure.step("Проверка обновления статуса питомца"):
			response = pet_helper.get_pet(pet_data.id)
			CustomAsserts.assert_equal(response.status, PetStatus.SOLD.value)

	@allure.story("Поиск питомцев")
	@allure.title("Создание и поиск питомца по статусу")
	def test_find_pet_by_status(self, pet_helper, pet_data):
		with allure.step("Создание питомца"):
			response = pet_helper.create_pet(pet_data)
			CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		with allure.step("Поиск питомца по статусу"):
			response = pet_helper.get_pet_by_status([PetStatus.AVAILABLE.value])
			CustomAsserts.assert_equal(response[0].name, pet_data.name)

	@allure.story("Обновление информации о питомцах")
	@allure.title("Создание и загрузка фото питомца")
	def test_upload_pet_photo(self, pet_helper, pet_data):
		"""Загрузка фото питомца"""
		pytest.skip("Доделать загрузку файла (доразместить фото и проверить, что фото загружено)")
		# TODO: доделать загрузку файла (доразместить фото)
		# Сначала создаём питомца
		response = pet_helper.create_pet(pet_data)
		CustomAsserts.assert_equal(response.name, pet_data.name)

		# Загружаем фото питомца
		photo_url = "https://example.com/dog2.jpg"
		response = pet_helper.upload_image(pet_data.id, "dog2", photo_url)

		# Проверяем, что фото загружено
		response = pet_helper.get_pet(pet_data.id)
		assert photo_url in response.photoUrls

	@allure.story("Обновление информации о питомцах")
	@allure.title("Создание и добавление тега питомцу")
	def test_add_pet_tag(self, pet_helper, pet_data):
		with allure.step("Создание питомца"):
			response = pet_helper.create_pet(pet_data)
			CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		with allure.step("Добавление тега питомцу"):
			tag = Tag(id=2, name="fluffy")
			pet_data.tags = [tag]
			response = pet_helper.update_pet(pet_data)
			CustomAsserts.assert_equal(response.tags[0].id, tag.id)

		with allure.step("Проверка добавления тега питомцу"):
			response = pet_helper.get_pet(pet_data.id)
			CustomAsserts.check_item_in_list(tag, response.tags, "Тег не добавлен к питомцу или не найден")

	@allure.story("Обновление информации о питомцах")
	@allure.title("Создание и удаление тега у питомца")
	def test_delete_pet_tag(self, pet_helper, pet_data):
		with allure.step("Создание питомца"):
			response = pet_helper.create_pet(pet_data)
			CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		with allure.step("Добавление тега питомцу"):
			tag = Tag(id=2, name="fluffy")
			pet_data.tags = [tag]
			response = pet_helper.update_pet(pet_data)
			CustomAsserts.assert_equal(response.tags[0].id, tag.id)

		with allure.step("Удаление тега у питомца"):
			pet_data.tags = None
			response = pet_helper.update_pet(pet_data)
			CustomAsserts.assert_equal(response.tags, [])

		with allure.step("Проверка удаления тега у питомца"):
			response = pet_helper.get_pet(pet_data.id)
			assert tag not in response.tags

	@allure.story("Обновление информации о питомцах")
	@allure.title("Создание и обновление категории питомца")
	def test_update_pet_category(self, pet_helper, pet_data):
		with allure.step("Создание питомца"):
			response = pet_helper.create_pet(pet_data)
			CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		with allure.step("Обновление категории питомца"):
			new_category = Category(id=2, name="Cat")
			pet_data.category = new_category
			response = pet_helper.update_pet(pet_data)
			CustomAsserts.assert_equal(response.category.id, new_category.id)

		with allure.step("Проверка обновления категории питомца"):
			response = pet_helper.get_pet(pet_data.id)
			CustomAsserts.assert_equal(response.category.id, new_category.id)
			CustomAsserts.assert_equal(response.category.name, new_category.name)

	@allure.story("Обновление информации о питомцах")
	@allure.title("Создание и удаление категории у питомца")
	def test_delete_pet_category(self, pet_helper, pet_data):
		with allure.step("Создание питомца"):
			response = pet_helper.create_pet(pet_data)
			CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		with allure.step("Обновление категории питомца"):
			new_category = Category(id=2, name="Cat")
			pet_data.category = new_category
			response = pet_helper.update_pet(pet_data)
			CustomAsserts.assert_equal(response.category.id, new_category.id)

		with allure.step("Удаление категории у питомца"):
			pet_data.category = None
			response = pet_helper.update_pet(pet_data)
			CustomAsserts.assert_equal(response.category, None)

		with allure.step("Проверка удаления категории у питомца"):
			response = pet_helper.get_pet(pet_data.id)
			CustomAsserts.assert_equal(response.category, None)

	@allure.story("Создание питомцев")
	@allure.title("Создание питомца без обязательного поля name")
	def test_create_pet_without_name(self, pet_helper, pet_data):
		"""Добавление питомца без обязательного поля name"""
		pet_data.name = None
		response = pet_helper.create_pet(pet_data, 400)
		CustomAsserts.assert_equal(response.message, "Bad input")

	@allure.story("Создание питомцев")
	@allure.title("Создание питомца без обязательного поля photoUrls")
	def test_create_pet_without_photo_urls(self, pet_helper, pet_data):
		"""Добавление питомца без обязательного поля photoUrls"""
		pet_data.photoUrls = None
		response = pet_helper.create_pet(pet_data, 400)
		CustomAsserts.assert_equal(response.message, "Bad input")
		assert response.message == "Bad input"
