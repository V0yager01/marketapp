from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.models import Product
from app.modules.cart.repos import CartItemRepo, CartRepo


class GetCart:
    def __init__(self, cart_repo: CartRepo):
        self.cart_repo = cart_repo

    async def execute(self, user_id: UUID):
        return await self.cart_repo.get_or_create(user_id)


class AddToCart:
    def __init__(self, cart_repo: CartRepo, item_repo: CartItemRepo, db: AsyncSession):
        self.cart_repo = cart_repo
        self.item_repo = item_repo
        self.db = db

    async def execute(self, user_id: UUID, product_id: UUID, quantity: int):
        product = await self._get_product(product_id)
        self._check_stock(product, quantity)
        cart = await self.cart_repo.get_or_create(user_id)
        return await self.item_repo.add_or_update(cart.id, product_id, quantity)

    async def _get_product(self, product_id: UUID) -> Product:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    def _check_stock(self, product: Product, quantity: int):
        if product.stock < quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock")


class UpdateCartItem:
    def __init__(self, cart_repo: CartRepo, item_repo: CartItemRepo, db: AsyncSession):
        self.cart_repo = cart_repo
        self.item_repo = item_repo
        self.db = db

    async def execute(self, user_id: UUID, product_id: UUID, quantity: int):
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if product.stock < quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stock")
        cart = await self.cart_repo.get_or_create(user_id)
        return await self.item_repo.update(cart.id, product_id, quantity)


class RemoveFromCart:
    def __init__(self, cart_repo: CartRepo, item_repo: CartItemRepo):
        self.cart_repo = cart_repo
        self.item_repo = item_repo

    async def execute(self, user_id: UUID, product_id: UUID):
        cart = await self.cart_repo.get_or_create(user_id)
        await self.item_repo.delete(cart.id, product_id)


class ClearCart:
    def __init__(self, cart_repo: CartRepo):
        self.cart_repo = cart_repo

    async def execute(self, user_id: UUID):
        cart = await self.cart_repo.get_or_create(user_id)
        await self.cart_repo.clear(cart.id)
