from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.modules.auth.depends import require_admin
from app.modules.users.repos import UserRepo
from app.modules.users.schemas import UserListResponse
from app.modules.users.use_cases import AdminListUsers

router = APIRouter()


@router.get("/admin/users", response_model=UserListResponse, dependencies=[Depends(require_admin)])
async def admin_list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = UserRepo(db)
    items, total = await AdminListUsers(repo).execute(offset, limit)
    return UserListResponse(items=items, total=total, offset=offset, limit=limit)
