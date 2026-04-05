from uuid import UUID

from fastapi import APIRouter, Depends, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.modules.auth.depends import require_admin
from app.modules.products.repos import CategoryRepo, ProductRepo
from app.modules.products.schemas import CategoryOut, ProductIn, ProductListResponse, ProductOut
from app.modules.products.use_cases import (
    AdminCreateCategory,
    AdminCreateProduct,
    AdminDeleteCategory,
    AdminDeleteProduct,
    AdminUpdateProduct,
    GetProduct,
    ListCategories,
    ListProducts,
    UploadImage,
)

router = APIRouter()


# --- Public ---

@router.get("/products", response_model=ProductListResponse)
async def list_products(
    category_id: int | None = Query(None),
    search: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = ProductRepo(db)
    items, total = await ListProducts(repo).execute(category_id, search, offset, limit)
    return ProductListResponse(items=items, total=total, offset=offset, limit=limit)


@router.get("/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = ProductRepo(db)
    return await GetProduct(repo).execute(product_id)


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    repo = CategoryRepo(db)
    return await ListCategories(repo).execute()


# --- Admin ---

@router.post("/admin/products", response_model=ProductOut, dependencies=[Depends(require_admin)])
async def admin_create_product(body: ProductIn, db: AsyncSession = Depends(get_db)):
    repo = ProductRepo(db)
    return await AdminCreateProduct(repo).execute(body.model_dump())


@router.put("/admin/products/{product_id}", response_model=ProductOut, dependencies=[Depends(require_admin)])
async def admin_update_product(product_id: UUID, body: ProductIn, db: AsyncSession = Depends(get_db)):
    repo = ProductRepo(db)
    return await AdminUpdateProduct(repo).execute(product_id, body.model_dump(exclude_none=True))


@router.delete("/admin/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def admin_delete_product(product_id: UUID, db: AsyncSession = Depends(get_db)):
    repo = ProductRepo(db)
    await AdminDeleteProduct(repo).execute(product_id)


@router.post("/admin/products/{product_id}/upload-image", dependencies=[Depends(require_admin)])
async def admin_upload_image(
    product_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    repo = ProductRepo(db)
    image_url = await UploadImage(repo).execute(product_id, file)
    return {"image_url": image_url}


@router.post("/admin/categories", response_model=CategoryOut, dependencies=[Depends(require_admin)])
async def admin_create_category(name: str, db: AsyncSession = Depends(get_db)):
    repo = CategoryRepo(db)
    return await AdminCreateCategory(repo).execute(name)


@router.delete("/admin/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(require_admin)])
async def admin_delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    repo = CategoryRepo(db)
    await AdminDeleteCategory(repo).execute(category_id)
