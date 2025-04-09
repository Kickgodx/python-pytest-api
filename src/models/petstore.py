from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import Field, StrictBool, StrictInt, StrictStr

from src.models.base_model import BaseRequestModel


class ApiResponse(BaseRequestModel):
    code: Optional[StrictInt] = None
    type: Optional[StrictStr] = None
    message: Optional[StrictStr] = None


class Category(BaseRequestModel):
    id: Optional[StrictInt] = None
    name: Optional[StrictStr] = None


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
    id: Optional[StrictInt] = None
    pet_id: Optional[StrictInt] = Field(None, alias="petId")
    quantity: Optional[StrictInt] = None
    ship_date: Optional[str] = Field(None, alias="shipDate")
    status: Optional[OrderStatus] = Field(None, description="Order Status")
    complete: Optional[StrictBool] = None


class User(BaseRequestModel):
    id: Optional[StrictInt] = None
    username: Optional[StrictStr] = None
    first_name: Optional[StrictStr] = Field(None, alias="firstName")
    last_name: Optional[StrictStr] = Field(None, alias="lastName")
    email: Optional[StrictStr] = None
    password: Optional[StrictStr] = None
    phone: Optional[StrictStr] = None
    user_status: Optional[StrictInt] = Field(None, alias="userStatus", description="User Status")


class Pet(BaseRequestModel):
    id: Optional[StrictInt] = None
    category: Optional[Category] = None
    name: StrictStr = Field(..., examples=["doggie"])
    photo_urls: list[StrictStr] = Field(..., alias="photoUrls")
    tags: Optional[list[Tag]] = None
    status: Optional[PetStatus] = Field(None, description="pet status in the store")
