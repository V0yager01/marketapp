from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.modules.auth.models import User
from app.modules.auth.depends import get_current_user, require_admin
from app.modules.cart.repos import CartRepo
from app.modules.orders.repos import OrderRepo
from app.modules.orders.schemas import OrderListResponse, OrderOut, OrderStatusIn
from app.modules.orders.use_cases import (
    AdminListOrders,
    AdminSetOrderStatus,
    CancelOrder,
    CreateOrder,
    GetOrder,
    ListOrders,
)

router = APIRouter()


@router.post("/orders", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order_repo = OrderRepo(db)
    cart_repo = CartRepo(db)
    return await CreateOrder(order_repo, cart_repo, db).execute(current_user.id)


@router.get("/orders", response_model=OrderListResponse)
async def list_orders(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order_repo = OrderRepo(db)
    items, total = await ListOrders(order_repo).execute(current_user.id, offset, limit)
    return OrderListResponse(items=items, total=total, offset=offset, limit=limit)


@router.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order_repo = OrderRepo(db)
    return await GetOrder(order_repo).execute(current_user.id, order_id)


@router.patch("/orders/{order_id}/cancel", response_model=OrderOut)
async def cancel_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    order_repo = OrderRepo(db)
    return await CancelOrder(order_repo, db).execute(current_user.id, order_id)


# --- Admin ---

@router.get("/admin/orders", response_model=OrderListResponse, dependencies=[Depends(require_admin)])
async def admin_list_orders(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    order_repo = OrderRepo(db)
    items, total = await AdminListOrders(order_repo).execute(offset, limit)
    return OrderListResponse(items=items, total=total, offset=offset, limit=limit)


@router.patch("/admin/orders/{order_id}/status", response_model=OrderOut, dependencies=[Depends(require_admin)])
async def admin_set_order_status(
    order_id: UUID,
    body: OrderStatusIn,
    db: AsyncSession = Depends(get_db),
):
    order_repo = OrderRepo(db)
    return await AdminSetOrderStatus(order_repo, db).execute(order_id, body.status)
