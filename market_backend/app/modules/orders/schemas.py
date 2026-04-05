from decimal import Decimal
from uuid import UUID
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class OrderItemOut(BaseModel):
    id: UUID
    product_id: UUID
    quantity: int
    price_at_order: Decimal

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    total_price: Decimal | None
    created_at: datetime
    items: list[OrderItemOut]

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    items: list[OrderOut]
    total: int
    offset: int
    limit: int


class OrderStatusIn(BaseModel):
    status: Literal["pending", "confirmed", "cancelled"]
