from __future__ import annotations

from enum import Enum

from pydantic import Field, StrictBool, StrictInt, StrictStr

from src.models.base_model import BaseRequestModel


class ApiResponse(BaseRequestModel):
    code: StrictInt | None = None
    type: StrictStr | None = None
    message: StrictStr | None = None


class Category(BaseRequestModel):
    id: StrictInt | None = None
    name: StrictStr | None = None


class PetStatus(Enum):
    """
    pet status in the store
    """

    AVAILABLE = "available"
    PENDING = "pending"
    SOLD = "sold"


class Tag(Category):
    pass


class OrderStatus(Enum):
    """
    Order Status
    """

    PLACED = "placed"
    APPROVED = "approved"
    DELIVERED = "delivered"


class Order(BaseRequestModel):
    id: StrictInt | None = None
    pet_id: StrictInt | None = Field(None, alias="petId")
    quantity: StrictInt | None = None
    ship_date: str | None = Field(None, alias="shipDate")
    status: OrderStatus | None = Field(None, description="Order Status")
    complete: StrictBool | None = Field(None, description="Status of the order, default: false")


class User(BaseRequestModel):
    id: StrictInt | None = None
    username: StrictStr | None = None
    first_name: StrictStr | None = Field(None, alias="firstName")
    last_name: StrictStr | None = Field(None, alias="lastName")
    email: StrictStr | None = None
    password: StrictStr | None = None
    phone: StrictStr | None = None
    user_status: StrictInt | None = Field(None, alias="userStatus", description="User Status")


class Pet(BaseRequestModel):
    id: StrictInt | None = None
    category: Category | None = None
    name: StrictStr = Field(..., examples=["doggie"])
    photo_urls: list[StrictStr] = Field(..., alias="photoUrls")
    tags: list[Tag] | None = None
    status: PetStatus | None = Field(None, description="pet status in the store")
