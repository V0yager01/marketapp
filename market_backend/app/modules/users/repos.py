from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User


class UserRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, offset: int, limit: int) -> tuple[list[User], int]:
        q = select(User)
        total = (await self.db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        result = await self.db.execute(q.offset(offset).limit(limit))
        return result.scalars().all(), total
