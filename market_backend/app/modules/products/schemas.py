from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CategoryOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class ProductOut(BaseModel):
    id: UUID
    name: str
    description: str | None
    price: Decimal
    stock: int
    image_url: str | None
    category: CategoryOut | None

    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    items: list[ProductOut]
    total: int
    offset: int
    limit: int


class ProductIn(BaseModel):
    name: str
    description: str | None = None
    price: Decimal
    stock: int = 0
    category_id: int | None = None
    image_url: str | None = None
