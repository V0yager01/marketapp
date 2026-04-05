import os
import uuid
from uuid import UUID

from fastapi import HTTPException, UploadFile, status

from app.modules.products.repos import CategoryRepo, ProductRepo

UPLOAD_DIR = "app/static/uploads/products"


class ListProducts:
    def __init__(self, repo: ProductRepo):
        self.repo = repo

    async def execute(self, category_id, search, offset, limit):
        items, total = await self.repo.list(category_id, search, offset, limit)
        return items, total


class GetProduct:
    def __init__(self, repo: ProductRepo):
        self.repo = repo

    async def execute(self, product_id: UUID):
        product = await self.repo.get(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product


class ListCategories:
    def __init__(self, repo: CategoryRepo):
        self.repo = repo

    async def execute(self):
        return await self.repo.list()


class AdminCreateProduct:
    def __init__(self, repo: ProductRepo):
        self.repo = repo

    async def execute(self, data: dict):
        return await self.repo.create(**data)


class AdminUpdateProduct:
    def __init__(self, repo: ProductRepo):
        self.repo = repo

    async def execute(self, product_id: UUID, data: dict):
        product = await self.repo.get(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return await self.repo.update(product, **data)


class AdminDeleteProduct:
    def __init__(self, repo: ProductRepo):
        self.repo = repo

    async def execute(self, product_id: UUID):
        product = await self.repo.get(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        await self.repo.delete(product)


class AdminCreateCategory:
    def __init__(self, repo: CategoryRepo):
        self.repo = repo

    async def execute(self, name: str):
        return await self.repo.create(name)


class AdminDeleteCategory:
    def __init__(self, repo: CategoryRepo):
        self.repo = repo

    async def execute(self, category_id: int):
        category = await self.repo.get(category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        await self.repo.delete(category)


class UploadImage:
    def __init__(self, product_repo: ProductRepo):
        self.product_repo = product_repo

    async def execute(self, product_id: UUID, file: UploadFile) -> str:
        product = await self.product_repo.get(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        path = os.path.join(UPLOAD_DIR, filename)

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        content = await file.read()
        with open(path, "wb") as f:
            f.write(content)

        image_url = f"/static/uploads/products/{filename}"
        await self.product_repo.update(product, image_url=image_url)
        return image_url
