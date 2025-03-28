from utils.custom_requester import CustomRequester
import src.pet.endpoints as url


class PetAPI(CustomRequester):
	def __init__(self, base_url: str):
		super().__init__(base_url)

	def get_find_pet_by_id(self, pet_id: str):
		return self.get(url.GET_FIND_BY_ID.format(pet_id=pet_id))

	def get_find_pet_by_status(self, pet_status):
		params = pet_status
		return self.get(url.GET_FIND_BY_STATUS, params=params)

	def post_pet(self, data):
		return self.post(url.POST_PET, json=data)

	def put_pet(self, data):
		return self.put(url.PUT_PET, json=data)

	def delete_pet(self, pet_id):
		return self.delete(url.DELETE_PET.format(pet_id=pet_id))

	def post_upload_image(self, pet_id, additional_metadata: str, file):
		params = {"additionalMetadata": additional_metadata}
		return self.post(url.POST_UPLOAD_IMAGE.format(pet_id=pet_id), files=file, params=params)

	def post_update_status_and_name(self, pet_id, name, status):
		"""
		:param pet_id: ID питомца
		:param name: Имя питомца (передается как formData)
		:param status: Статус питомца (передается как formData)
		"""
		params = {"name": name, "status": status}
		return self.post(url.POST_UPDATE_STATUS_AND_NAME.format(pet_id=pet_id), params=params)