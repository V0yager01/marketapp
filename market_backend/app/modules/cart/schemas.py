from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CartItemOut(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int

    model_config = {"from_attributes": True}


class CartOut(BaseModel):
    id: UUID
    user_id: UUID
    items: list[CartItemOut]

    model_config = {"from_attributes": True}


class CartItemIn(BaseModel):
    product_id: UUID
    quantity: int = 1
