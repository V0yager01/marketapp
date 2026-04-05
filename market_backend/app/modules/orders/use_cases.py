from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.cart.models import Cart, CartItem
from app.modules.products.models import Product
from app.modules.cart.repos import CartRepo
from app.modules.orders.repos import OrderRepo


class CreateOrder:
    def __init__(self, order_repo: OrderRepo, cart_repo: CartRepo, db: AsyncSession):
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.db = db

    async def execute(self, user_id: UUID):
        cart = await self.cart_repo.get_or_create(user_id)
        if not cart.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

        items_data = []
        total = 0

        for cart_item in cart.items:
            result = await self.db.execute(
                select(Product).where(Product.id == cart_item.product_id).with_for_update()
            )
            product = result.scalar_one_or_none()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {cart_item.product_id} not found")
            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Not enough stock for {product.name}",
                )
            product.stock -= cart_item.quantity
            total += float(product.price) * cart_item.quantity
            items_data.append({
                "product_id": cart_item.product_id,
                "quantity": cart_item.quantity,
                "price_at_order": product.price,
            })

        order = await self.order_repo.create(user_id, round(total, 2), items_data)
        await self.cart_repo.clear(cart.id)
        return order


class CancelOrder:
    def __init__(self, order_repo: OrderRepo, db: AsyncSession):
        self.order_repo = order_repo
        self.db = db

    async def execute(self, user_id: UUID, order_id: UUID):
        order = await self.order_repo.get(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your order")
        if order.status != "pending":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only pending orders can be cancelled")

        for item in order.items:
            result = await self.db.execute(select(Product).where(Product.id == item.product_id))
            product = result.scalar_one_or_none()
            if product:
                product.stock += item.quantity

        await self.db.commit()
        return await self.order_repo.set_status(order, "cancelled")


class ListOrders:
    def __init__(self, order_repo: OrderRepo):
        self.order_repo = order_repo

    async def execute(self, user_id: UUID, offset: int, limit: int):
        return await self.order_repo.list_by_user(user_id, offset, limit)


class GetOrder:
    def __init__(self, order_repo: OrderRepo):
        self.order_repo = order_repo

    async def execute(self, user_id: UUID, order_id: UUID):
        order = await self.order_repo.get(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        if order.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your order")
        return order


class AdminListOrders:
    def __init__(self, order_repo: OrderRepo):
        self.order_repo = order_repo

    async def execute(self, offset: int, limit: int):
        return await self.order_repo.list_all(offset, limit)


class AdminSetOrderStatus:
    def __init__(self, order_repo: OrderRepo, db: AsyncSession):
        self.order_repo = order_repo
        self.db = db

    async def execute(self, order_id: UUID, new_status: str):
        order = await self.order_repo.get(order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if new_status == "cancelled" and order.status == "pending":
            for item in order.items:
                result = await self.db.execute(select(Product).where(Product.id == item.product_id))
                product = result.scalar_one_or_none()
                if product:
                    product.stock += item.quantity
            await self.db.commit()

        return await self.order_repo.set_status(order, new_status)
