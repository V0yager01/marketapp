from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class UserOut(BaseModel):
    id: UUID
    email: str
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: list[UserOut]
    total: int
    offset: int
    limit: int
