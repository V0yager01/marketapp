from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.modules.auth.models import User
from app.modules.auth.depends import get_current_user
from app.modules.cart.repos import CartItemRepo, CartRepo
from app.modules.cart.schemas import CartItemIn, CartItemOut, CartOut
from app.modules.cart.use_cases import (
    AddToCart,
    ClearCart,
    GetCart,
    RemoveFromCart,
    UpdateCartItem,
)

router = APIRouter()


@router.get("", response_model=CartOut)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cart_repo = CartRepo(db)
    return await GetCart(cart_repo).execute(current_user.id)


@router.post("/items", response_model=CartItemOut, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    body: CartItemIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cart_repo = CartRepo(db)
    item_repo = CartItemRepo(db)
    return await AddToCart(cart_repo, item_repo, db).execute(
        current_user.id, body.product_id, body.quantity
    )


@router.put("/items/{product_id}", response_model=CartItemOut)
async def update_cart_item(
    product_id: UUID,
    body: CartItemIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cart_repo = CartRepo(db)
    item_repo = CartItemRepo(db)
    return await UpdateCartItem(cart_repo, item_repo, db).execute(
        current_user.id, product_id, body.quantity
    )


@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cart_repo = CartRepo(db)
    item_repo = CartItemRepo(db)
    await RemoveFromCart(cart_repo, item_repo).execute(current_user.id, product_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cart_repo = CartRepo(db)
    await ClearCart(cart_repo).execute(current_user.id)
