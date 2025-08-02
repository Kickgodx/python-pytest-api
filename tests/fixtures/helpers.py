import pytest

from config import BASE_URL
from src.api.pet.helpers import PetHelper
from src.api.store.helpers import StoreHelper
from src.api.user.helpers import UserHelper


@pytest.fixture(scope="session")
def pet_helper():
    return PetHelper(BASE_URL)


@pytest.fixture(scope="session")
def store_helper():
    return StoreHelper(BASE_URL)


@pytest.fixture(scope="session")
def user_helper():
    return UserHelper(BASE_URL)
