# fake_store: A free fake API for testing and prototyping e-commerce applications.
# generated by datamodel-codegen:
#   filename:  fake_storeOpenAPI.yml
#   timestamp: 2025-03-31T00:10:24+00:00
#   version:   0.28.2

from __future__ import annotations

from pydantic import AnyUrl, Field, StrictFloat, StrictInt, StrictStr
from src.models.petstore import BaseRequestModel


class Product(BaseRequestModel):
    id: StrictInt | None = None
    title: StrictStr | None = None
    price: StrictFloat | None = None
    description: StrictStr | None = None
    category: StrictStr | None = None
    image: AnyUrl | None = None


class Cart(BaseRequestModel):
    id: StrictInt | None = None
    user_id: StrictInt | None = Field(None, alias="userId")
    products: list[Product] | None = None


class User(BaseRequestModel):
    id: StrictInt | None = None
    username: StrictStr | None = None
    email: StrictStr | None = None
    password: StrictStr | None = None


class Login(BaseRequestModel):
    username: StrictStr | None = None
    password: StrictStr | None = None


class LoginResponse(BaseRequestModel):
    token: StrictStr | None = None
