import pytest

from config import BASE_URL
from src.func.pet.helpers import PetHelper


@pytest.fixture(scope="session")
def pet_helper():
	return PetHelper(BASE_URL)
