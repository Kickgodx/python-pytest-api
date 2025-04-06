import src.func.pet.endpoints as url
from src.models.client import Client
from src.tech.custom_requester import CustomRequester


class PetAPI(CustomRequester):
	def __init__(self, base_url: str):
		super().__init__(base_url)

	def get_find_pet_by_id(self, client: Client, pet_id: str):
		return self.get(url.GET_FIND_BY_ID.format(pet_id=pet_id), headers=client.get_base_headers())

	def get_find_pet_by_status(self, client: Client, pet_status: list[str]):
		params = [("status", status) for status in pet_status]
		return self.get(url.GET_FIND_BY_STATUS, params=params, headers=client.get_base_headers())

	def post_pet(self, client: Client, data):
		return self.post(url.POST_PET, data=data, headers=client.get_base_headers())

	def put_pet(self, client: Client, data):
		return self.put(url.PUT_PET, data=data, headers=client.get_base_headers())

	def delete_pet(self, client: Client, pet_id):
		return self.delete(url.DELETE_PET.format(pet_id=pet_id), headers=client.get_base_headers())

	def post_upload_image(self, client: Client, pet_id, additional_metadata: str, file):
		params = {"additionalMetadata": additional_metadata}
		return self.post(url.POST_UPLOAD_IMAGE.format(pet_id=pet_id), files=file, params=params, headers=client.get_base_headers())

	def post_update_status_and_name(self, client: Client, pet_id, name, status):
		"""
		:param client: Клиент, который делает запрос
		:param pet_id: ID питомца
		:param name: Имя питомца (передается как formData)
		:param status: Статус питомца (передается как formData)
		"""
		params = {"name": name, "status": status}
		return self.post(url.POST_UPDATE_STATUS_AND_NAME.format(pet_id=pet_id), params=params, headers=client.get_base_headers())
