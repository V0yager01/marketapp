from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.cart.models import Cart, CartItem


class CartRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(self, user_id: UUID) -> Cart:
        result = await self.db.execute(
            select(Cart).options(selectinload(Cart.items)).where(Cart.user_id == user_id)
        )
        cart = result.scalar_one_or_none()
        if cart is None:
            cart = Cart(user_id=user_id)
            self.db.add(cart)
            await self.db.commit()
            await self.db.refresh(cart)
            cart = await self.get_or_create(user_id)
        return cart

    async def clear(self, cart_id: UUID) -> None:
        await self.db.execute(delete(CartItem).where(CartItem.cart_id == cart_id))
        await self.db.commit()


class CartItemRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, cart_id: UUID, product_id: UUID) -> CartItem | None:
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.product_id == product_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_or_update(self, cart_id: UUID, product_id: UUID, quantity: int) -> CartItem:
        item = await self.get(cart_id, product_id)
        if item:
            item.quantity += quantity
        else:
            item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
            self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def update(self, cart_id: UUID, product_id: UUID, quantity: int) -> CartItem:
        item = await self.get(cart_id, product_id)
        if not item:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not in cart")
        item.quantity = quantity
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete(self, cart_id: UUID, product_id: UUID) -> None:
        item = await self.get(cart_id, product_id)
        if item:
            await self.db.delete(item)
            await self.db.commit()
