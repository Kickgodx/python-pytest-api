import pytest

from config import BASE_URL
from src.api.pet.helpers import PetHelper
from src.api.store.helpers import StoreHelper
from src.api.user.helpers import UserHelper


@pytest.fixture(scope="session")
def pet_helper():
    helper = PetHelper(BASE_URL)
    yield helper
    helper.api.session_close()


@pytest.fixture(scope="session")
def store_helper():
    helper = StoreHelper(BASE_URL)
    yield helper
    helper.api.session_close()


@pytest.fixture(scope="session")
def user_helper():
    helper = UserHelper(BASE_URL)
    yield helper
    helper.api.session_close()
