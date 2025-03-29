import random
import time

import allure
import pytest

from src.pet.models import Pet, PetStatus, Category, Tag
from utils.custom_asserts import CustomAsserts


@pytest.fixture(scope="function")
def pet_data():
	"""Фикстура для данных питомца"""
	rand = random.randint(1, 1000)
	generate_name = f"TsumTsum{rand}"
	return Pet(
		id=rand,
		name=generate_name,
		category=Category(id=1, name="Dog"),
		photoUrls=["https://example.com/dog.jpg"],
		tags=[Tag(id=1, name="cute")],
		status=PetStatus.AVAILABLE.value
	)


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
		CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		# Теперь получаем информацию о питомце
		response = pet_helper.get_pet(pet_data.id)
		CustomAsserts.assert_equal(response.name, pet_data.name)
		assert response.name == pet_data.name

	@allure.title("Создание и обновление информации о питомце")
	def test_update_pet(self, pet_helper, pet_data):
		"""Обновление информации о питомце"""
		# Сначала создаём питомца
		response = pet_helper.create_pet(pet_data)
		CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		# Обновляем информацию о питомце
		new_name = "Bobby Jr."
		pet_data.name = new_name
		response = pet_helper.update_pet(pet_data)
		CustomAsserts.assert_equal(response.name, new_name)

		time.sleep(10)

		# Проверяем, что информация обновилась
		response = pet_helper.get_pet(pet_data.id)
		CustomAsserts.assert_equal(response.name, new_name)

	@allure.title("Создание и удаление питомца")
	def test_delete_pet(self, pet_helper, pet_data):
		"""Удаление питомца"""
		# Сначала создаём питомца
		response = pet_helper.create_pet(pet_data)
		CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		# Удаляем питомца
		pet_helper.delete_pet(pet_data.id)

		time.sleep(10)

		# Проверяем, что питомец удалён
		response = pet_helper.get_pet(pet_data.id, 404)
		CustomAsserts.assert_equal(response.message, "Pet not found")

	@allure.title("Создание и обновление статуса питомца")
	def test_update_pet_status(self, pet_helper, pet_data):
		"""Обновление статуса питомца"""
		# Сначала создаём питомца
		response = pet_helper.create_pet(pet_data)
		CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		# Обновляем статус питомца
		pet_data.status = PetStatus.SOLD.value
		response = pet_helper.update_pet(pet_data)
		CustomAsserts.assert_equal(response.status, PetStatus.SOLD.value)

		# Проверяем, что статус обновился
		response = pet_helper.get_pet(pet_data.id)
		CustomAsserts.assert_equal(response.status, PetStatus.SOLD.value)

	@allure.title("Создание и поиск питомца по статусу")
	def test_find_pet_by_status(self, pet_helper, pet_data):
		"""Поиск питомца по статусу"""
		# Сначала создаём питомца
		response = pet_helper.create_pet(pet_data)
		CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		# Ищем питомца по статусу
		response = pet_helper.get_pet_by_status([PetStatus.AVAILABLE.value])
		CustomAsserts.assert_equal(response[0].name, pet_data.name)

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

	@allure.title("Создание и добавление тега питомцу")
	def test_add_pet_tag(self, pet_helper, pet_data):
		"""Добавление тега питомцу"""
		# Сначала создаём питомца
		response = pet_helper.create_pet(pet_data)
		CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		# Добавляем тег питомцу
		tag = Tag(id=2, name="fluffy")
		pet_data.tags = [tag]
		response = pet_helper.update_pet(pet_data)
		CustomAsserts.assert_equal(response.tags[0].id, tag.id)

		# Проверяем, что тег добавлен
		response = pet_helper.get_pet(pet_data.id)
		assert tag in response.tags

	@allure.title("Создание и удаление тега у питомца")
	def test_delete_pet_tag(self, pet_helper, pet_data):
		"""Удаление тега у питомца"""
		# Сначала создаём питомца
		response = pet_helper.create_pet(pet_data)
		CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		# Добавляем тег питомцу
		tag = Tag(id=2, name="fluffy")
		pet_data.tags = [tag]
		response = pet_helper.update_pet(pet_data)
		CustomAsserts.assert_equal(response.tags[0].id, tag.id)

		# Удаляем тег у питомца
		pet_data.tags = None
		response = pet_helper.update_pet(pet_data)
		CustomAsserts.assert_equal(response.tags, [])

		# Проверяем, что тег удалён
		response = pet_helper.get_pet(pet_data.id)
		assert tag not in response.tags

	@allure.title("Создание и обновление категории питомца")
	def test_update_pet_category(self, pet_helper, pet_data):
		"""Обновление категории питомца"""
		# Сначала создаём питомца
		response = pet_helper.create_pet(pet_data)
		CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		# Обновляем категорию питомца
		new_category = Category(id=2, name="Cat")
		pet_data.category = new_category
		response = pet_helper.update_pet(pet_data)
		CustomAsserts.assert_equal(response.category.id, new_category.id)

		# Проверяем, что категория обновилась
		response = pet_helper.get_pet(pet_data.id)
		CustomAsserts.assert_equal(response.category.id, new_category.id)
		CustomAsserts.assert_equal(response.category.name, new_category.name)

	@allure.title("Создание и удаление категории у питомца")
	def test_delete_pet_category(self, pet_helper, pet_data):
		"""Удаление категории у питомца"""
		# Сначала создаём питомца
		response = pet_helper.create_pet(pet_data)
		CustomAsserts.assert_equal(response.name, pet_data.name)

		time.sleep(10)

		# Обновляем категорию питомца
		new_category = Category(id=3, name="Dog")
		pet_data.category = new_category
		response = pet_helper.update_pet(pet_data)
		CustomAsserts.assert_equal(response.category.id, new_category.id)

		# Удаляем категорию у питомца
		pet_data.category = None
		response = pet_helper.update_pet(pet_data)
		CustomAsserts.assert_equal(response.category, None)

		# Проверяем, что категория удалена
		response = pet_helper.get_pet(pet_data.id)
		CustomAsserts.assert_equal(response.category, None)

	@allure.title("Создание питомца без обязательного поля name")
	def test_create_pet_without_name(self, pet_helper, pet_data):
		"""Добавление питомца без обязательного поля name"""
		pet_data.name = None
		response = pet_helper.create_pet(pet_data, 400)
		CustomAsserts.assert_equal(response.message, "Bad input")

	@allure.title("Создание питомца без обязательного поля photoUrls")
	def test_create_pet_without_photo_urls(self, pet_helper, pet_data):
		"""Добавление питомца без обязательного поля photoUrls"""
		pet_data.photoUrls = None
		response = pet_helper.create_pet(pet_data, 400)
		CustomAsserts.assert_equal(response.message, "Bad input")
		assert response.message == "Bad input"
