from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.products.models import Category, Product


class ProductRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        category_id: int | None,
        search: str | None,
        offset: int,
        limit: int,
    ) -> tuple[list[Product], int]:
        q = select(Product).options(selectinload(Product.category))
        if category_id is not None:
            q = q.where(Product.category_id == category_id)
        if search:
            q = q.where(Product.name.ilike(f"%{search}%"))

        total_q = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(total_q)).scalar_one()

        q = q.offset(offset).limit(limit)
        result = await self.db.execute(q)
        return result.scalars().all(), total

    async def get(self, product_id: UUID) -> Product | None:
        result = await self.db.execute(
            select(Product).options(selectinload(Product.category)).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Product:
        product = Product(**kwargs)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return await self.get(product.id)

    async def update(self, product: Product, **kwargs) -> Product:
        for key, value in kwargs.items():
            setattr(product, key, value)
        await self.db.commit()
        await self.db.refresh(product)
        return await self.get(product.id)

    async def delete(self, product: Product) -> None:
        await self.db.delete(product)
        await self.db.commit()


class CategoryRepo:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self) -> list[Category]:
        result = await self.db.execute(select(Category))
        return result.scalars().all()

    async def get(self, category_id: int) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def create(self, name: str) -> Category:
        category = Category(name=name)
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete(self, category: Category) -> None:
        await self.db.delete(category)
        await self.db.commit()
