from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.orders.models import Order, OrderItem


class OrderRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, total_price, items_data: list[dict]) -> Order:
        order = Order(user_id=user_id, total_price=total_price)
        self.db.add(order)
        await self.db.flush()
        for item in items_data:
            self.db.add(OrderItem(order_id=order.id, **item))
        await self.db.commit()
        return await self.get(order.id)

    async def get(self, order_id: UUID) -> Order | None:
        result = await self.db.execute(
            select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID, offset: int, limit: int) -> tuple[list[Order], int]:
        q = select(Order).options(selectinload(Order.items)).where(Order.user_id == user_id)
        total = (await self.db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        result = await self.db.execute(q.order_by(Order.created_at.desc()).offset(offset).limit(limit))
        return result.scalars().all(), total

    async def list_all(self, offset: int, limit: int) -> tuple[list[Order], int]:
        q = select(Order).options(selectinload(Order.items))
        total = (await self.db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        result = await self.db.execute(q.order_by(Order.created_at.desc()).offset(offset).limit(limit))
        return result.scalars().all(), total

    async def set_status(self, order: Order, new_status: str) -> Order:
        order.status = new_status
        await self.db.commit()
        await self.db.refresh(order)
        return await self.get(order.id)
