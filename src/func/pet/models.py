from enum import Enum

from src.models.base_model import BaseRequestModel


class Category(BaseRequestModel):
	id: int
	name: str


class Tag(BaseRequestModel):
	id: int
	name: str


class PetStatus(Enum):
	AVAILABLE = "available"
	PENDING = "pending"
	SOLD = "sold"


class Pet(BaseRequestModel):
	id: int = None
	category: Category = None
	name: str
	photoUrls: list
	tags: list[Tag] = None
	status: PetStatus = None
