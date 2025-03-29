import pytest

from config import BASE_URL
from src.func.store.helpers import StoreHelper


@pytest.fixture(scope="session")
def store_helper():
	return StoreHelper(BASE_URL)
